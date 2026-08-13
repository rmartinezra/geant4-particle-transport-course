#!/usr/bin/env python3
"""Mide la longitud libre de captura n+10B conservando escapes censurados."""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import gzip
import json
import re
import shutil
import subprocess
from pathlib import Path

import numpy as np


EVENT_FIELDS = (
    "event_id", "particle", "energy_eV", "material", "isotope",
    "density_g_cm3", "number_density_cm3", "path_length_cm", "interacted",
    "escaped", "process_name",
)
CANONICAL_FIELDS = (
    "event_id", "particle", "energy", "material", "interaction_occurred",
    "interaction_distance_cm", "process_name", "target_nucleus_if_available",
)


def arguments() -> argparse.Namespace:
    project = Path(__file__).resolve().parents[1]
    root = project.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--executable", type=Path, default=root / "build" / "experiment04_hadronic" / "Hadr03")
    parser.add_argument("--events", type=int, default=100_000)
    parser.add_argument("--length-cm", type=float, default=300.0,
                        help="volumen largo; cualquier escape se conserva como censura derecha")
    parser.add_argument("--seed", type=int, default=2026081204)
    parser.add_argument("--tag", default="final")
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def macro_text(events: int, length_cm: float, seed1: int, seed2: int) -> str:
    return f"""# Generada por scripts/run_hadronic.py
/control/verbose 1
/run/verbose 1
/random/setSeeds {seed1} {seed2}
/testhadr/det/setIsotopeMat B10 5 10 2.46 g/cm3
/testhadr/det/setSize {length_cm:.12g} cm
/run/initialize
/gun/particle neutron
/gun/energy 1 eV
/process/inactivate hadElastic
/process/inactivate neutronInelastic
/process/inactivate nFission
/testhadr/run/printStat false
/run/printProgress {max(events // 10, 1)}
/run/beamOn {events}
"""


def read_native(path: Path) -> list[dict[str, str]]:
    header: list[str] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.startswith("#column "):
                header.append(line.strip().split(maxsplit=2)[2])
    if not set(EVENT_FIELDS).issubset(header):
        raise RuntimeError(f"Cabecera inesperada en {path}: {header}")
    rows: list[dict[str, str]] = []
    with path.open(newline="", encoding="utf-8") as handle:
        for line in handle:
            if line.startswith("#") or not line.strip():
                continue
            rows.append(dict(zip(header, next(csv.reader([line])), strict=True)))
    return rows


def main() -> int:
    args = arguments()
    if args.events <= 1 or args.length_cm <= 0:
        raise SystemExit("Eventos y longitud deben ser positivos")
    executable = args.executable.resolve()
    if not executable.is_file():
        raise SystemExit(f"No existe {executable}; ejecute ../../build_all.sh")
    project = Path(__file__).resolve().parents[1]
    output_dir = project / "data" if args.tag == "final" else project / "data" / "pilots" / args.tag
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / "interaction_lengths.csv"
    rich_output = output_dir / "hadronic_events.csv"
    collisions = [path for path in (output, rich_output) if path.exists()]
    if collisions and not args.force:
        raise SystemExit(f"Ya existen {collisions}; use --force")
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = project / "logs" / f"{args.tag}_{args.events}_{stamp}"
    run_dir.mkdir(parents=True, exist_ok=False)
    macro = run_dir / "run.mac"
    log = run_dir / "run.log"
    seed1, seed2 = args.seed, args.seed + 1
    macro.write_text(macro_text(args.events, args.length_cm, seed1, seed2), encoding="utf-8")
    completed = subprocess.run([str(executable), str(macro)], cwd=run_dir, text=True,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    log.write_text(completed.stdout, encoding="utf-8")
    if completed.returncode != 0:
        raise RuntimeError(f"Geant4 fallo; vea {log}")
    matches = re.findall(
        r"COURSE_HADRONIC_REFERENCE process=(\S+) macroscopic_cm-1=([0-9.eE+\-]+) microscopic_barn=([0-9.eE+\-]+)",
        completed.stdout,
    )
    capture_matches = [item for item in matches if item[0] == "nCapture"]
    if len(capture_matches) != 1:
        raise RuntimeError(f"No se encontro referencia hadronica en {log}")
    reference_process, reference_macro, reference_micro = capture_matches[0]
    native = run_dir / "hadronic_native.csv"
    if not native.is_file():
        raise RuntimeError(f"No se genero {native}")
    rows = read_native(native)
    if len(rows) != args.events:
        raise RuntimeError(f"Se esperaban {args.events} filas y se obtuvieron {len(rows)}")
    interacted = np.asarray([int(row["interacted"]) for row in rows])
    escaped = np.asarray([int(row["escaped"]) for row in rows])
    paths = np.asarray([float(row["path_length_cm"]) for row in rows])
    processes = np.asarray([row["process_name"] for row in rows])
    if not np.all(interacted + escaped == 1):
        raise RuntimeError("Cada fila debe ser interaccion o escape, pero no ambas")
    if not np.all(processes[interacted == 1] == "nCapture"):
        raise RuntimeError(f"Canal inesperado: {np.unique(processes[interacted == 1])}")
    if np.any(paths <= 0.0) or np.any(paths > args.length_cm*(1.0 + 1.e-8)):
        raise RuntimeError("Distancia fuera del volumen configurado")
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CANONICAL_FIELDS)
        writer.writeheader()
        writer.writerows({
            "event_id": row["event_id"], "particle": row["particle"],
            "energy": row["energy_eV"] + " eV", "material": row["material"],
            "interaction_occurred": row["interacted"],
            "interaction_distance_cm": row["path_length_cm"],
            "process_name": row["process_name"],
            "target_nucleus_if_available": row["isotope"],
        } for row in rows)
    # Rich machine-oriented companion used by the censored-likelihood analysis.
    with rich_output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=EVENT_FIELDS)
        writer.writeheader()
        writer.writerows({field: row[field] for field in EVENT_FIELDS} for row in rows)
    with native.open("rb") as source, gzip.open(run_dir / "hadronic_native.csv.gz", "wb", compresslevel=6) as target:
        shutil.copyfileobj(source, target)
    native.unlink()
    metadata = {
        "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "executable": str(executable), "events": args.events, "length_cm": args.length_cm,
        "seed_1": seed1, "seed_2": seed2, "threads": 1,
        "particle": "neutron", "energy_eV": 1.0, "material": "pure B10 isotope",
        "active_process": "nCapture only; hadElastic, neutronInelastic and nFission inactivated",
        "physics_list": "Hadr03 PhysicsList with G4HadronPhysicsQGSP_BIC_HP",
        "low_energy_model": "NeutronHPCapture (0--20 MeV)",
        "cross_section_datasets_reported_by_process_dump": ["NeutronHPCaptureXS", "G4NeutronCaptureXS"],
        "reference_policy": "G4HadronicProcessStore queried in EndOfRun, after the events",
        "reference_process": reference_process,
        "reference_macroscopic_cm-1": float(reference_macro),
        "reference_microscopic_barn": float(reference_micro),
        "interacted": int(interacted.sum()), "escaped_right_censored": int(escaped.sum()),
        "macro": str(macro), "log": str(log),
        "geant4_version": subprocess.run(["geant4-config", "--version"], text=True, capture_output=True).stdout.strip(),
    }
    (output_dir / "run_metadata.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Hadr04: {len(rows)} eventos, {interacted.sum()} capturas, {escaped.sum()} escapes censurados")
    print(f"Datos: {output}")
    print(f"Macro, log y ntuple nativo comprimido: {run_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
