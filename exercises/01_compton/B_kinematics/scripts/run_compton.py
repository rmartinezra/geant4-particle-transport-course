#!/usr/bin/env python3
"""Ejecuta TestEm14 en modo secuencial y conserva su ntuple CSV."""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import re
import subprocess
from pathlib import Path


def arguments() -> argparse.Namespace:
    project = Path(__file__).resolve().parents[1]
    repository = project.parents[2]
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--executable", type=Path, default=repository / "build" / "ex1b" / "TestEm14"
    )
    parser.add_argument("--events", type=int, default=200_000)
    parser.add_argument("--energy-kev", type=float, default=300.0)
    parser.add_argument("--seed", type=int, default=20260812)
    parser.add_argument("--output", type=Path, default=project / "data" / "compton_events.csv")
    parser.add_argument("--logs-dir", type=Path, default=project / "logs")
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def macro_text(events: int, energy: float, seed1: int, seed2: int) -> str:
    return f"""# Generada por scripts/run_compton.py
/control/verbose 1
/run/verbose 1
/testem/det/setMat G4_Al
/testem/phys/addPhysics standard
/run/initialize
/run/setCut 1 nm
/process/inactivate phot
/process/inactivate conv
/process/inactivate GammaToMuPair
/particle/select gamma
/particle/process/dump
/gun/particle gamma
/gun/energy {energy:.12g} keV
/random/setSeeds {seed1} {seed2}
/run/beamOn {events}
"""


def main() -> int:
    args = arguments()
    if args.events <= 0:
        raise SystemExit("El numero de eventos debe ser positivo")
    executable = args.executable.resolve()
    output = args.output.resolve()
    if not executable.is_file():
        raise SystemExit(f"No existe el ejecutable: {executable}. Ejecute make build")
    if output.exists() and not args.force:
        raise SystemExit(f"Ya existe {output}; use --force para reemplazarlo conscientemente")

    project = Path(__file__).resolve().parents[1]
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = args.logs_dir.resolve() / f"kinematics_{stamp}"
    run_dir.mkdir(parents=True, exist_ok=False)
    macro = run_dir / "compton_runtime.mac"
    log = run_dir / "compton_runtime.log"
    seed1, seed2 = args.seed, args.seed + 1
    macro.write_text(macro_text(args.events, args.energy_kev, seed1, seed2), encoding="utf-8")
    completed = subprocess.run(
        [str(executable), str(macro)],
        cwd=run_dir,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    log.write_text(completed.stdout, encoding="utf-8")
    if completed.returncode != 0:
        raise RuntimeError(f"Geant4 fallo; vea {log}")
    matches = re.findall(r"Process calls frequency --->([^\n]+)", completed.stdout)
    if len(matches) != 1:
        raise RuntimeError("No se pudo verificar la frecuencia de procesos")
    counts = {name: int(value) for name, value in re.findall(r"([A-Za-z0-9_]+)\s*=\s*(\d+)", matches[0])}
    if counts != {"compt": args.events}:
        raise RuntimeError(f"Se esperaba solo compt={args.events}, se obtuvo {counts}")

    generated = run_dir / "compton_events.csv"
    if not generated.is_file():
        candidates = sorted(run_dir.glob("*compton_events*.csv"))
        raise RuntimeError(f"No se genero compton_events.csv; candidatos: {candidates}")
    # G4Tools CSV describes columns in '#column TYPE NAME' comment lines.
    # Convert that native file to a conventional CSV header while preserving
    # the untouched Geant4 file in the log directory.
    header: list[str] = []
    with generated.open(encoding="utf-8") as handle:
        for line in handle:
            if line.startswith("#column "):
                header.append(line.strip().split(maxsplit=2)[2])
    required = {
        "event_id", "E0_keV", "Egamma_scattered_keV", "cos_theta", "theta_deg",
        "electron_kinetic_energy_keV", "process_name",
    }
    if not required.issubset(set(header)):
        raise RuntimeError(f"Cabecera CSV inesperada: {header}")

    output.parent.mkdir(parents=True, exist_ok=True)
    row_count = 0
    with generated.open(newline="", encoding="utf-8") as source, output.open(
        "w", newline="", encoding="utf-8"
    ) as destination:
        writer = csv.writer(destination)
        writer.writerow(header)
        for line in source:
            if line.startswith("#") or not line.strip():
                continue
            writer.writerow(next(csv.reader([line])))
            row_count += 1
    if row_count != args.events:
        raise RuntimeError(f"El CSV contiene {row_count} filas, no {args.events}")
    metadata = {
        "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "executable": str(executable),
        "output_csv": str(output),
        "raw_csv": str(generated),
        "log": str(log),
        "macro": str(macro),
        "events": args.events,
        "energy_keV": args.energy_kev,
        "material": "G4_Al",
        "seed_1": seed1,
        "seed_2": seed2,
        "threads": 1,
        "execution": "G4RunManagerType::SerialOnly",
        "physics": "TestEm14 standard/Klein-Nishina; primary outcome compt only",
        "geometry": "100 m cube from original TestEm14; first interaction aborts event",
    }
    output.with_name(output.stem + "_metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"B: {row_count} eventos Compton escritos en {output}")
    print(f"Log, macro y CSV bruto: {run_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
