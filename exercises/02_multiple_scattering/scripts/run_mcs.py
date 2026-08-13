#!/usr/bin/env python3
"""Ejecuta los barridos de MCS y reduce los ntuples de TestEm5 a CSV."""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import gzip
import json
import math
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import numpy as np


THICKNESSES_CM = (5.0, 10.0, 20.0, 40.0, 60.0, 80.0, 100.0)
ENERGIES_GEV = (5.0, 10.0, 20.0, 50.0, 100.0, 200.0, 500.0)
SUMMARY_FIELDS = (
    "thickness_cm", "energy_GeV", "momentum_GeV_c", "N_generated",
    "N_transmitted", "mean_theta_x_rad", "std_theta_x_rad", "rms_theta_x_rad",
    "mean_theta_y_rad", "std_theta_y_rad", "rms_theta_y_rad",
    "q16_theta_x_rad", "q50_theta_x_rad", "q84_theta_x_rad",
    "material", "density_g_cm3", "radiation_length_cm",
)
EVENT_FIELDS = (
    "event_id", "energy_GeV", "thickness_cm", "theta_x_rad", "theta_y_rad",
    "theta_total_rad", "transmitted", "final_energy_GeV",
)


def parse_args() -> argparse.Namespace:
    project = Path(__file__).resolve().parents[1]
    root = project.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--executable", type=Path, default=root / "build" / "experiment02_mcs" / "TestEm5")
    parser.add_argument("--events", type=int, default=100_000, help="eventos por configuracion")
    parser.add_argument("--representative-events", type=int, default=None)
    parser.add_argument("--seed", type=int, default=2026081202)
    parser.add_argument("--tag", default="final", help="final escribe los CSV principales; otro tag va a data/pilots/TAG")
    parser.add_argument("--output-dir", type=Path, default=project / "data")
    parser.add_argument("--logs-dir", type=Path, default=project / "logs")
    parser.add_argument("--jobs", type=int, default=4,
                        help="procesos Geant4 independientes en paralelo; cada uno sigue siendo monohilo")
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def macro_text(events: int, energy_gev: float, thickness_cm: float, seed1: int, seed2: int) -> str:
    world_x = thickness_cm + 0.2
    return f"""# Generada por scripts/run_mcs.py
/control/verbose 1
/run/verbose 1
/random/setSeeds {seed1} {seed2}
/testem/det/setAbsMat G4_Fe
/testem/det/setAbsThick {thickness_cm:.12g} cm
/testem/det/setAbsYZ 10 m
/testem/det/setWorldX {world_x:.12g} cm
/testem/det/setWorldYZ 10 m
/testem/phys/addPhysics emstandard_opt0
/run/setCut 1 mm
/run/initialize
/testem/gun/setDefault
/gun/particle mu+
/gun/energy {energy_gev:.12g} GeV
/testem/stack/killSecondaries
/run/printProgress {max(events // 10, 1)}
/run/beamOn {events}
"""


def native_header(path: Path) -> list[str]:
    header: list[str] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.startswith("#column "):
                header.append(line.strip().split(maxsplit=2)[2])
    return header


def read_native(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    header = native_header(path)
    required = set(EVENT_FIELDS) | {"momentum_GeV_c", "density_g_cm3", "radiation_length_cm"}
    if not required.issubset(header):
        raise RuntimeError(f"Cabecera inesperada en {path}: {header}")
    rows: list[dict[str, str]] = []
    with path.open(newline="", encoding="utf-8") as handle:
        for line in handle:
            if line.startswith("#") or not line.strip():
                continue
            values = next(csv.reader([line]))
            rows.append(dict(zip(header, values, strict=True)))
    return header, rows


def summarize(rows: list[dict[str, str]], expected: int) -> dict[str, float | int]:
    if len(rows) != expected:
        raise RuntimeError(f"Se esperaban {expected} filas y se obtuvieron {len(rows)}")
    transmitted = np.asarray([int(row["transmitted"]) for row in rows], dtype=bool)
    if not transmitted.any():
        raise RuntimeError("Ningun muon atraveso el blanco")
    tx = np.asarray([float(row["theta_x_rad"]) for row in rows])[transmitted]
    ty = np.asarray([float(row["theta_y_rad"]) for row in rows])[transmitted]
    if not (np.isfinite(tx).all() and np.isfinite(ty).all()):
        raise RuntimeError("Angulos no finitos")
    q16, q50, q84 = np.quantile(tx, [0.16, 0.50, 0.84])
    first = rows[0]
    return {
        "thickness_cm": float(first["thickness_cm"]),
        "energy_GeV": float(first["energy_GeV"]),
        "momentum_GeV_c": float(first["momentum_GeV_c"]),
        "N_generated": expected,
        "N_transmitted": int(transmitted.sum()),
        "mean_theta_x_rad": float(tx.mean()),
        "std_theta_x_rad": float(tx.std(ddof=1)),
        "rms_theta_x_rad": float(np.sqrt(np.mean(tx * tx))),
        "mean_theta_y_rad": float(ty.mean()),
        "std_theta_y_rad": float(ty.std(ddof=1)),
        "rms_theta_y_rad": float(np.sqrt(np.mean(ty * ty))),
        "q16_theta_x_rad": float(q16),
        "q50_theta_x_rad": float(q50),
        "q84_theta_x_rad": float(q84),
        "material": "G4_Fe",
        "density_g_cm3": float(first["density_g_cm3"]),
        "radiation_length_cm": float(first["radiation_length_cm"]),
    }


def write_csv(path: Path, fields: tuple[str, ...], rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def compress_raw(path: Path, destination: Path) -> None:
    with path.open("rb") as source, gzip.open(destination, "wb", compresslevel=6) as target:
        shutil.copyfileobj(source, target)
    path.unlink()


def run_one(
    executable: Path, session: Path, label: str, events: int, energy: float,
    thickness: float, seed1: int, seed2: int,
) -> tuple[list[dict[str, str]], dict[str, object]]:
    run_dir = session / label
    run_dir.mkdir(parents=True, exist_ok=False)
    macro = run_dir / "run.mac"
    log = run_dir / "run.log"
    macro.write_text(macro_text(events, energy, thickness, seed1, seed2), encoding="utf-8")
    completed = subprocess.run(
        [str(executable), str(macro)], cwd=run_dir, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
    )
    log.write_text(completed.stdout, encoding="utf-8")
    if completed.returncode != 0:
        raise RuntimeError(f"Geant4 fallo en {label}; vea {log}")
    generated = run_dir / "mcs_events.csv"
    if not generated.is_file():
        raise RuntimeError(f"No se genero {generated}")
    _, rows = read_native(generated)
    summary = summarize(rows, events)
    compress_raw(generated, run_dir / "mcs_events_native.csv.gz")
    return rows, {
        "label": label, "events": events, "energy_GeV": energy,
        "thickness_cm": thickness, "seed_1": seed1, "seed_2": seed2,
        "summary": summary, "macro": str(macro), "log": str(log),
    }


def main() -> int:
    args = parse_args()
    if args.events <= 1:
        raise SystemExit("--events debe ser mayor que 1")
    representative_events = args.representative_events or args.events
    executable = args.executable.resolve()
    if not executable.is_file():
        raise SystemExit(f"No existe {executable}; ejecute ../../build_all.sh")
    project = Path(__file__).resolve().parents[1]
    output_dir = args.output_dir.resolve() if args.tag == "final" else args.output_dir.resolve() / "pilots" / args.tag
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = [output_dir / "thickness_scan.csv", output_dir / "energy_scan.csv", output_dir / "angular_events.csv"]
    collisions = [path for path in outputs if path.exists()]
    if collisions and not args.force:
        raise SystemExit(f"Ya existen {collisions}; use --force para reemplazarlos")

    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    session = args.logs_dir.resolve() / f"{args.tag}_{args.events}_{stamp}"
    session.mkdir(parents=True, exist_ok=False)
    if args.jobs < 1:
        raise SystemExit("--jobs debe ser positivo")
    thickness_rows: list[dict[str, object] | None] = [None]*len(THICKNESSES_CM)
    energy_rows: list[dict[str, object] | None] = [None]*len(ENERGIES_GEV)
    records_by_index: list[dict[str, object] | None] = [None]*(len(THICKNESSES_CM) + len(ENERGIES_GEV) + 1)
    tasks: list[tuple[str, int, int, str, int, float, float, int, int]] = []
    index = 0
    for position, thickness in enumerate(THICKNESSES_CM):
        tasks.append(("thickness", position, index, f"thickness_{thickness:g}cm", args.events,
                      100.0, thickness, args.seed + 2*index, args.seed + 2*index + 1))
        index += 1
    for position, energy in enumerate(ENERGIES_GEV):
        tasks.append(("energy", position, index, f"energy_{energy:g}GeV", args.events,
                      energy, 50.0, args.seed + 2*index, args.seed + 2*index + 1))
        index += 1
    tasks.append(("representative", 0, index, "representative_100GeV_50cm", representative_events,
                  100.0, 50.0, args.seed + 2*index, args.seed + 2*index + 1))
    representative: list[dict[str, str]] | None = None
    with ThreadPoolExecutor(max_workers=args.jobs) as executor:
        future_map = {
            executor.submit(run_one, executable, session, label, count, energy, thick, seed1, seed2):
            (kind, position, record_index)
            for kind, position, record_index, label, count, energy, thick, seed1, seed2 in tasks
        }
        for future in as_completed(future_map):
            kind, position, record_index = future_map[future]
            rows, record = future.result()
            records_by_index[record_index] = record
            if kind == "thickness":
                thickness_rows[position] = record["summary"]
            elif kind == "energy":
                energy_rows[position] = record["summary"]
            else:
                representative = rows
            if kind != "representative":
                del rows
    if representative is None or any(row is None for row in thickness_rows + energy_rows + records_by_index):
        raise RuntimeError("Resultado paralelo incompleto")
    records = records_by_index

    # Write only after every Geant4 run and validation succeeded.
    write_csv(outputs[0], SUMMARY_FIELDS, thickness_rows)
    write_csv(outputs[1], SUMMARY_FIELDS, energy_rows)
    event_rows = [{field: row[field] for field in EVENT_FIELDS} for row in representative]
    write_csv(outputs[2], EVENT_FIELDS, event_rows)
    metadata = {
        "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "executable": str(executable), "tag": args.tag,
        "events_per_scan_configuration": args.events,
        "representative_events": representative_events,
        "base_seed": args.seed, "threads_per_process": 1,
        "parallel_independent_processes": args.jobs,
        "geant4_version": subprocess.run(["geant4-config", "--version"], text=True, capture_output=True).stdout.strip(),
        "particle": "mu+", "material": "G4_Fe",
        "physics": "TestEm5 emstandard_opt0; secondaries killed after creation",
        "projected_angle_convention": "theta_x=atan2(u_final dot +Y, u_final dot u_initial); theta_y analogous +Z for the +X beam",
        "session": str(session), "runs": records,
    }
    (output_dir / "run_metadata.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"MCS: {len(thickness_rows)} espesores, {len(energy_rows)} energias y {len(event_rows)} eventos representativos")
    print(f"Datos: {output_dir}")
    print(f"Macros, logs y ntuples nativos comprimidos: {session}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
