#!/usr/bin/env python3
"""Ejecuta TestEm18 para los barridos de perdida de energia de muones."""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import gzip
import json
import math
import re
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import numpy as np


MUON_MASS_MEV = 105.6583755
THICKNESSES_CM = (1.0, 2.0, 5.0, 10.0, 20.0, 40.0)
ENERGIES_GEV = (0.2, 0.3, 0.5, 1.0, 3.0, 10.0, 30.0, 100.0, 300.0, 1000.0)
EVENT_FIELDS = (
    "event_id", "initial_energy_MeV", "final_energy_MeV", "energy_loss_MeV",
    "energy_deposited_MeV", "transmitted", "ionization_loss_MeV",
    "bremsstrahlung_loss_MeV", "pair_production_loss_MeV", "other_loss_MeV",
    "primary_continuous_deposit_MeV", "secondary_deposit_MeV",
)
EVENT_OUTPUT_FIELDS = EVENT_FIELDS + ("secondary_energy_transferred_MeV",)
THICKNESS_FIELDS = (
    "thickness_cm", "areal_density_g_cm2", "energy_initial_GeV", "N_generated", "N_transmitted",
    "mean_energy_loss_MeV", "std_energy_loss_MeV", "sem_energy_loss_MeV",
    "median_energy_loss_MeV", "q16_energy_loss_MeV", "q84_energy_loss_MeV",
    "mean_final_energy_MeV", "mean_final_energy_GeV", "material", "density_g_cm3",
)
ENERGY_FIELDS = (
    "energy_GeV", "beta", "gamma", "beta_gamma", "thickness_cm",
    "N_generated", "N_transmitted", "fraction_stopped", "mean_energy_loss_MeV",
    "std_energy_loss_MeV", "sem_energy_loss_MeV", "median_energy_loss_MeV",
    "q16_energy_loss_MeV", "q84_energy_loss_MeV", "mean_dedx_MeV_cm",
    "mass_stopping_power_MeV_cm2_g", "mean_final_energy_MeV", "density_g_cm3",
    "reference_dedx_MeV_cm",
)
PROCESS_FIELDS = (
    "energy_GeV", "beta_gamma", "N_generated", "mean_ionization_loss_MeV",
    "mean_bremsstrahlung_loss_MeV", "mean_pair_production_loss_MeV",
    "mean_other_loss_MeV", "fraction_ionization", "fraction_bremsstrahlung",
    "fraction_pair_production", "fraction_other", "ionization_MeV_cm",
    "bremsstrahlung_MeV_cm", "pair_production_MeV_cm", "other_MeV_cm", "total_MeV_cm",
)


def arguments() -> argparse.Namespace:
    project = Path(__file__).resolve().parents[1]
    root = project.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--executable", type=Path, default=root / "build" / "experiment03_energy_loss" / "TestEm18")
    parser.add_argument("--events", type=int, default=100_000)
    parser.add_argument("--representative-events", type=int, default=None)
    parser.add_argument("--seed", type=int, default=2026081203)
    parser.add_argument("--tag", default="final")
    parser.add_argument("--output-dir", type=Path, default=project / "data")
    parser.add_argument("--logs-dir", type=Path, default=project / "logs")
    parser.add_argument("--jobs", type=int, default=4,
                        help="procesos Geant4 independientes; cada proceso es monohilo")
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def macro_text(events: int, energy_gev: float, thickness_cm: float,
               seed1: int, seed2: int, track_secondaries: bool) -> str:
    return f"""# Generada por scripts/run_energy_loss.py
/control/verbose 1
/run/verbose 1
/random/setSeeds {seed1} {seed2}
/testem/det/setMat G4_WATER
/testem/det/setSize {thickness_cm:.12g} cm
/testem/phys/addPhysics standard
/run/setCut 1 mm
/run/initialize
/gun/particle mu+
/gun/energy {energy_gev:.12g} GeV
/testem/trackSecondaries {'true' if track_secondaries else 'false'}
/run/printProgress {max(events // 10, 1)}
/run/beamOn {events}
"""


def read_native(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    header: list[str] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.startswith("#column "):
                header.append(line.strip().split(maxsplit=2)[2])
    required = set(EVENT_FIELDS) | {"thickness_cm", "density_g_cm3"}
    if not required.issubset(header):
        raise RuntimeError(f"Cabecera inesperada en {path}: {header}")
    rows: list[dict[str, str]] = []
    with path.open(newline="", encoding="utf-8") as handle:
        for line in handle:
            if line.startswith("#") or not line.strip():
                continue
            rows.append(dict(zip(header, next(csv.reader([line])), strict=True)))
    return header, rows


def arrays(rows: list[dict[str, str]], expected: int) -> dict[str, np.ndarray]:
    if len(rows) != expected:
        raise RuntimeError(f"Se esperaban {expected} filas y se obtuvieron {len(rows)}")
    result = {key: np.asarray([float(row[key]) for row in rows]) for key in rows[0]}
    tolerance = 2.e-6
    if np.any(result["energy_loss_MeV"] < -tolerance):
        raise RuntimeError("Se encontro perdida de energia negativa")
    if np.any(result["final_energy_MeV"] > result["initial_energy_MeV"] + tolerance):
        raise RuntimeError("La energia final supera la inicial")
    classified = (result["ionization_loss_MeV"] + result["bremsstrahlung_loss_MeV"]
                  + result["pair_production_loss_MeV"] + result["other_loss_MeV"])
    # G4Tools CSV uses six significant digits.  At GeV-scale catastrophic
    # transfers, independently rounded components can differ by a few keV.
    if not np.allclose(classified, result["energy_loss_MeV"], rtol=2.e-5, atol=2.e-2):
        raise RuntimeError("Las contribuciones por proceso no cierran el balance del primario")
    return result


def compress(path: Path, destination: Path) -> None:
    with path.open("rb") as source, gzip.open(destination, "wb", compresslevel=6) as target:
        shutil.copyfileobj(source, target)
    path.unlink()


def run_one(executable: Path, session: Path, label: str, events: int, energy_gev: float,
            thickness_cm: float, seed1: int, seed2: int, track_secondaries: bool
            ) -> tuple[list[dict[str, str]], dict[str, np.ndarray], dict[str, object]]:
    run_dir = session / label
    run_dir.mkdir(parents=True, exist_ok=False)
    macro = run_dir / "run.mac"
    log = run_dir / "run.log"
    macro.write_text(macro_text(events, energy_gev, thickness_cm, seed1, seed2, track_secondaries), encoding="utf-8")
    completed = subprocess.run([str(executable), str(macro)], cwd=run_dir, text=True,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    log.write_text(completed.stdout, encoding="utf-8")
    if completed.returncode != 0:
        raise RuntimeError(f"Geant4 fallo en {label}; vea {log}")
    match = re.search(r"COURSE_EM_REFERENCE total_dedx_MeV_cm=([0-9.eE+\-]+) csda_range_cm=([0-9.eE+\-]+)", completed.stdout)
    if not match:
        raise RuntimeError(f"No se encontro la referencia G4EmCalculator en {log}")
    native = run_dir / "energy_loss_native.csv"
    if not native.is_file():
        raise RuntimeError(f"No se genero {native}")
    _, rows = read_native(native)
    data = arrays(rows, events)
    compress(native, run_dir / "energy_loss_native.csv.gz")
    record = {
        "label": label, "events": events, "energy_GeV": energy_gev,
        "thickness_cm": thickness_cm, "track_secondaries": track_secondaries,
        "seed_1": seed1, "seed_2": seed2, "macro": str(macro), "log": str(log),
        "reference_dedx_MeV_cm": float(match.group(1)), "csda_range_cm": float(match.group(2)),
    }
    return rows, data, record


def stats(data: dict[str, np.ndarray]) -> dict[str, float | int]:
    loss = data["energy_loss_MeV"]
    q16, median, q84 = np.quantile(loss, (0.16, 0.50, 0.84))
    return {
        "N_generated": len(loss),
        "N_transmitted": int(np.count_nonzero(data["transmitted"] > 0.5)),
        "mean_energy_loss_MeV": float(loss.mean()),
        "std_energy_loss_MeV": float(loss.std(ddof=1)),
        "median_energy_loss_MeV": float(median),
        "q16_energy_loss_MeV": float(q16),
        "q84_energy_loss_MeV": float(q84),
        "mean_final_energy_MeV": float(data["final_energy_MeV"].mean()),
        "density_g_cm3": float(data["density_g_cm3"][0]),
        "sem_energy_loss_MeV": float(loss.std(ddof=1)/math.sqrt(len(loss))),
    }


def write_csv(path: Path, fields: tuple[str, ...], rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    args = arguments()
    if args.events <= 1:
        raise SystemExit("--events debe ser mayor que 1")
    representative_events = args.representative_events or args.events
    executable = args.executable.resolve()
    if not executable.is_file():
        raise SystemExit(f"No existe {executable}; ejecute ../../build_all.sh")
    project = Path(__file__).resolve().parents[1]
    output_dir = args.output_dir.resolve() if args.tag == "final" else args.output_dir.resolve() / "pilots" / args.tag
    output_dir.mkdir(parents=True, exist_ok=True)
    filenames = ("thickness_scan.csv", "energy_scan.csv", "energy_loss_events.csv", "process_contributions.csv")
    outputs = [output_dir / name for name in filenames]
    collisions = [path for path in outputs + [output_dir / "dedx_energy_scan.csv"] if path.exists()]
    if collisions and not args.force:
        raise SystemExit(f"Ya existen {collisions}; use --force")
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    session = args.logs_dir.resolve() / f"{args.tag}_{args.events}_{stamp}"
    session.mkdir(parents=True, exist_ok=False)
    if args.jobs < 1:
        raise SystemExit("--jobs debe ser positivo")
    thickness_rows: list[dict[str, object] | None] = [None]*len(THICKNESSES_CM)
    energy_rows: list[dict[str, object] | None] = [None]*len(ENERGIES_GEV)
    process_rows: list[dict[str, object] | None] = [None]*len(ENERGIES_GEV)
    records: list[dict[str, object] | None] = [None]*(len(THICKNESSES_CM) + len(ENERGIES_GEV) + 1)
    tasks: list[tuple[str, int, int, str, int, float, float, int, int, bool]] = []
    index = 0
    for position, thickness in enumerate(THICKNESSES_CM):
        tasks.append(("thickness", position, index, f"thickness_{thickness:g}cm", args.events,
                      3.0, thickness, args.seed + 2*index, args.seed + 2*index + 1, False))
        index += 1
    for position, energy_gev in enumerate(ENERGIES_GEV):
        tasks.append(("energy", position, index, f"energy_{energy_gev:g}GeV", args.events,
                      energy_gev, 1.0, args.seed + 2*index, args.seed + 2*index + 1, False))
        index += 1
    tasks.append(("representative", 0, index, "representative_3GeV_10cm_secondaries",
                  representative_events, 3.0, 10.0, args.seed + 2*index, args.seed + 2*index + 1, True))
    representative: list[dict[str, str]] | None = None
    with ThreadPoolExecutor(max_workers=args.jobs) as executor:
        future_map = {
            executor.submit(run_one, executable, session, label, count, energy_gev, thick,
                            seed1, seed2, track_secondaries): (kind, position, record_index, energy_gev, thick)
            for kind, position, record_index, label, count, energy_gev, thick, seed1, seed2, track_secondaries in tasks
        }
        for future in as_completed(future_map):
            kind, position, record_index, energy_gev, thick = future_map[future]
            rows, data, record = future.result()
            records[record_index] = record
            if kind == "thickness":
                summary = stats(data)
                summary.update(thickness_cm=thick,
                               areal_density_g_cm2=thick*summary["density_g_cm3"],
                               energy_initial_GeV=3.0,
                               mean_final_energy_GeV=summary["mean_final_energy_MeV"]/1000.0,
                               material="G4_WATER")
                thickness_rows[position] = summary
            elif kind == "energy":
                summary = stats(data)
                gamma = 1.0 + energy_gev*1000.0/MUON_MASS_MEV
                beta = math.sqrt(1.0 - 1.0/(gamma*gamma))
                mean_loss = summary["mean_energy_loss_MeV"]
                energy_rows[position] = {
                    "energy_GeV": energy_gev, "beta": beta, "gamma": gamma,
                    "beta_gamma": beta*gamma, "thickness_cm": 1.0,
                    "N_generated": summary["N_generated"], "N_transmitted": summary["N_transmitted"],
                    "fraction_stopped": 1.0-summary["N_transmitted"]/summary["N_generated"],
                    "mean_energy_loss_MeV": mean_loss, "std_energy_loss_MeV": summary["std_energy_loss_MeV"],
                    "sem_energy_loss_MeV": summary["sem_energy_loss_MeV"],
                    "median_energy_loss_MeV": summary["median_energy_loss_MeV"],
                    "q16_energy_loss_MeV": summary["q16_energy_loss_MeV"],
                    "q84_energy_loss_MeV": summary["q84_energy_loss_MeV"],
                    "mean_dedx_MeV_cm": mean_loss,
                    "mass_stopping_power_MeV_cm2_g": mean_loss/summary["density_g_cm3"],
                    "mean_final_energy_MeV": summary["mean_final_energy_MeV"],
                    "density_g_cm3": summary["density_g_cm3"],
                    "reference_dedx_MeV_cm": record["reference_dedx_MeV_cm"],
                }
                process_means = {
                    "ionization": float(data["ionization_loss_MeV"].mean()),
                    "bremsstrahlung": float(data["bremsstrahlung_loss_MeV"].mean()),
                    "pair_production": float(data["pair_production_loss_MeV"].mean()),
                    "other": float(data["other_loss_MeV"].mean()),
                }
                denominator = sum(process_means.values())
                process_rows[position] = {
                    "energy_GeV": energy_gev, "beta_gamma": beta*gamma, "N_generated": args.events,
                    **{f"mean_{key}_loss_MeV": value for key, value in process_means.items()},
                    **{f"fraction_{key}": value/denominator for key, value in process_means.items()},
                    "ionization_MeV_cm": process_means["ionization"],
                    "bremsstrahlung_MeV_cm": process_means["bremsstrahlung"],
                    "pair_production_MeV_cm": process_means["pair_production"],
                    "other_MeV_cm": process_means["other"],
                    "total_MeV_cm": denominator,
                }
            else:
                representative = rows
            if kind != "representative":
                del rows
    if (representative is None or any(row is None for row in
                                      thickness_rows + energy_rows + process_rows + records)):
        raise RuntimeError("Resultado paralelo incompleto")

    write_csv(outputs[0], THICKNESS_FIELDS, thickness_rows)
    write_csv(outputs[1], ENERGY_FIELDS, energy_rows)
    representative_output = []
    for row in representative:
        converted = {field: row[field] for field in EVENT_FIELDS}
        converted["secondary_energy_transferred_MeV"] = (
            float(row["energy_loss_MeV"]) - float(row["primary_continuous_deposit_MeV"])
        )
        representative_output.append(converted)
    write_csv(outputs[2], EVENT_OUTPUT_FIELDS, representative_output)
    write_csv(outputs[3], PROCESS_FIELDS, process_rows)
    # Canonical course filename; energy_scan.csv is retained as a convenient
    # richer alias used by the analysis script.
    write_csv(output_dir / "dedx_energy_scan.csv", ENERGY_FIELDS, energy_rows)
    metadata = {
        "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "executable": str(executable), "tag": args.tag, "base_seed": args.seed,
        "events_per_scan_configuration": args.events, "representative_events": representative_events,
        "threads_per_process": 1, "parallel_independent_processes": args.jobs,
        "particle": "mu+", "material": "G4_WATER",
        "physics": "TestEm18 standard EM, intentionally without multiple scattering",
        "scan_secondary_policy": "secondaries killed after their creation energy is registered; primary energy loss remains complete",
        "representative_secondary_policy": "secondaries tracked; energy_deposited_MeV is local deposition in the finite water cube",
        "reference_policy": "G4EmCalculator ComputeTotalDEDX evaluated and printed in EndOfRunAction, after all events",
        "geant4_version": subprocess.run(["geant4-config", "--version"], text=True, capture_output=True).stdout.strip(),
        "session": str(session), "runs": records,
    }
    (output_dir / "run_metadata.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Perdida de energia: {len(thickness_rows)} espesores, {len(energy_rows)} energias, {len(representative)} eventos")
    print(f"Datos: {output_dir}")
    print(f"Logs y ntuples nativos comprimidos: {session}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
