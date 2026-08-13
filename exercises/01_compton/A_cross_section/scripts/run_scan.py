#!/usr/bin/env python3
"""Ejecuta TestEm13 para varios espesores y construye el CSV de transmision."""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import math
import re
import subprocess
import sys
from pathlib import Path


DEFAULT_THICKNESSES = [0.25, 0.50, 1.00, 2.00, 3.00, 5.00]
FIELDS = [
    "thickness_cm",
    "N0",
    "N_transmitted",
    "N_interacted",
    "transmission",
    "transmission_stat_error",
    "material",
    "density_g_cm3",
    "atomic_number",
    "atomic_number_density_cm3",
    "energy_keV",
    "geant4_compton_mu_cm_inv",
    "geant4_compton_sigma_cm2_atom",
    "seed_1",
    "seed_2",
    "active_outcomes",
    "geant4_version",
]


def parse_args() -> argparse.Namespace:
    project = Path(__file__).resolve().parents[1]
    default_executable = project.parent / "build" / "A" / "TestEm13"
    parser = argparse.ArgumentParser()
    parser.add_argument("--executable", type=Path, default=default_executable)
    parser.add_argument("--events", type=int, default=100_000)
    parser.add_argument("--thicknesses", type=float, nargs="+", default=DEFAULT_THICKNESSES)
    parser.add_argument("--energy-kev", type=float, default=300.0)
    parser.add_argument("--seed", type=int, default=20260812)
    parser.add_argument("--threads", type=int, default=1)
    parser.add_argument("--output", type=Path, default=project / "data" / "transmission_scan.csv")
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def macro_text(thickness: float, events: int, energy: float, seed1: int, seed2: int) -> str:
    return f"""# Generada por scripts/run_scan.py
/control/verbose 1
/run/verbose 1
/testem/det/setMat G4_Al
/testem/det/setSize {thickness:.12g} cm
/run/initialize
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


def parse_result(log_text: str) -> dict[str, str]:
    lines = [line for line in log_text.splitlines() if line.startswith("COURSE_RESULT_A,")]
    if len(lines) != 1:
        raise RuntimeError(f"Se esperaba un COURSE_RESULT_A y se encontraron {len(lines)}")
    result: dict[str, str] = {}
    for item in lines[0].split(",")[1:]:
        key, value = item.split("=", 1)
        result[key] = value.strip()
    return result


def verify_processes(log_text: str, n0: int) -> dict[str, int]:
    matches = re.findall(r"Process calls frequency --->([^\n]+)", log_text)
    if len(matches) != 1:
        raise RuntimeError("No se pudo verificar la frecuencia de procesos")
    counts = {name: int(value) for name, value in re.findall(r"([A-Za-z0-9_]+)\s*=\s*(\d+)", matches[0])}
    unexpected = set(counts) - {"Transportation", "compt"}
    if unexpected:
        raise RuntimeError(f"Procesos inesperados en el primario: {sorted(unexpected)}")
    if sum(counts.values()) != n0:
        raise RuntimeError(f"Los conteos {counts} no suman N0={n0}")
    return counts


def main() -> int:
    args = parse_args()
    if args.events <= 0 or args.threads <= 0 or any(x <= 0 for x in args.thicknesses):
        raise SystemExit("Eventos, threads y espesores deben ser positivos")
    executable = args.executable.resolve()
    output = args.output.resolve()
    if not executable.is_file():
        raise SystemExit(f"No existe el ejecutable: {executable}. Ejecute build_and_test.sh")
    if output.exists() and not args.force:
        raise SystemExit(f"Ya existe {output}; use --force para reemplazarlo conscientemente")

    project = Path(__file__).resolve().parents[1]
    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = project / "logs" / f"scan_{timestamp}"
    run_dir.mkdir(parents=True, exist_ok=False)
    output.parent.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, object]] = []
    for index, thickness in enumerate(sorted(args.thicknesses)):
        seed1 = args.seed + 2 * index
        seed2 = args.seed + 2 * index + 1
        label = f"{thickness:g}cm".replace(".", "p")
        macro = run_dir / f"run_{label}.mac"
        log = run_dir / f"run_{label}.log"
        macro.write_text(
            macro_text(thickness, args.events, args.energy_kev, seed1, seed2), encoding="utf-8"
        )
        completed = subprocess.run(
            [str(executable), str(macro), str(args.threads)],
            cwd=project,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        log.write_text(completed.stdout, encoding="utf-8")
        if completed.returncode != 0:
            raise RuntimeError(f"Geant4 fallo para {thickness} cm; vea {log}")
        raw = parse_result(completed.stdout)
        counts = verify_processes(completed.stdout, args.events)
        n_transmitted = int(raw["N_transmitted"])
        n_interacted = int(raw["N_interacted"])
        if n_transmitted != counts.get("Transportation", 0) or n_interacted != counts.get("compt", 0):
            raise RuntimeError(f"Conteos incoherentes para {thickness} cm")
        transmission = n_transmitted / args.events
        error = math.sqrt(transmission * (1.0 - transmission) / args.events)
        rows.append(
            {
                "thickness_cm": float(raw["thickness_cm"]),
                "N0": args.events,
                "N_transmitted": n_transmitted,
                "N_interacted": n_interacted,
                "transmission": transmission,
                "transmission_stat_error": error,
                "material": raw["material"],
                "density_g_cm3": float(raw["density_g_cm3"]),
                "atomic_number": float(raw["atomic_number"]),
                "atomic_number_density_cm3": float(raw["atomic_number_density_cm3"]),
                "energy_keV": float(raw["energy_keV"]),
                "geant4_compton_mu_cm_inv": float(raw["geant4_compton_mu_cm_inv"]),
                "geant4_compton_sigma_cm2_atom": float(raw["geant4_compton_sigma_cm2_atom"]),
                "seed_1": seed1,
                "seed_2": seed2,
                "active_outcomes": "Transportation|compt",
                "geant4_version": raw["geant4_version"],
            }
        )
        print(f"A: x={thickness:g} cm, T={transmission:.6f} +/- {error:.6f}")

    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    metadata = {
        "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "executable": str(executable),
        "output_csv": str(output),
        "log_directory": str(run_dir),
        "events_per_thickness": args.events,
        "thicknesses_cm": sorted(args.thicknesses),
        "energy_keV": args.energy_kev,
        "material": "G4_Al",
        "base_seed": args.seed,
        "threads": args.threads,
        "physics": "TestEm13 standard; gamma: Transportation + compt only",
    }
    output.with_name(output.stem + "_metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"CSV: {output}")
    print(f"Logs y macros exactas: {run_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
