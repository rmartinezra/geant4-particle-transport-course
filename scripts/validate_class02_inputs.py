#!/usr/bin/env python3
"""Comprueba que la Clase 2 use la producción FULL prevista."""

from __future__ import annotations

import csv
import json
from pathlib import Path


EXPECTED_THICKNESSES_CM = {0.25, 0.5, 1.0, 2.0, 3.0, 5.0}
EXPECTED_EX1A_EVENTS_PER_THICKNESS = 100_000
EXPECTED_EX1B_EVENTS = 200_000


def fail(message: str) -> None:
    raise SystemExit(
        f"Clase 2 requiere datos FULL: {message}.\n"
        "Genérelos con: make prepare-class02 SEED=20260901"
    )


def read_json(path: Path) -> dict[str, object]:
    if not path.is_file():
        fail(f"falta el metadato {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def validate_ex1a(root: Path) -> int:
    path = root / "generated/data/ex1a/transmission_scan.csv"
    if not path.is_file():
        fail(f"falta {path}")
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != len(EXPECTED_THICKNESSES_CM):
        fail(f"1A tiene {len(rows)} espesores, no {len(EXPECTED_THICKNESSES_CM)}")
    try:
        thicknesses = {float(row["thickness_cm"]) for row in rows}
        event_counts = {int(row["N0"]) for row in rows}
    except (KeyError, ValueError) as exc:
        fail(f"el CSV de 1A no tiene la estructura esperada ({exc})")
    if thicknesses != EXPECTED_THICKNESSES_CM:
        fail(f"los espesores de 1A son {sorted(thicknesses)}")
    if event_counts != {EXPECTED_EX1A_EVENTS_PER_THICKNESS}:
        fail(
            "1A contiene "
            f"{sorted(event_counts)} eventos por espesor, no "
            f"{EXPECTED_EX1A_EVENTS_PER_THICKNESS}"
        )
    for row in rows:
        if int(row["N_transmitted"]) + int(row["N_interacted"]) != int(row["N0"]):
            fail(f"los conteos de 1A no cierran para x={row['thickness_cm']} cm")
    metadata = read_json(root / "generated/data/ex1a/transmission_scan_metadata.json")
    if int(metadata.get("events_per_thickness", 0)) != EXPECTED_EX1A_EVENTS_PER_THICKNESS:
        fail("el metadato de 1A no corresponde a la producción FULL")
    return int(metadata.get("base_seed", 0))


def validate_ex1b(root: Path) -> int:
    path = root / "generated/data/ex1b/compton_events.csv"
    if not path.is_file():
        fail(f"falta {path}")
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        count = sum(1 for _ in reader)
    if count != EXPECTED_EX1B_EVENTS:
        fail(f"1B contiene {count} eventos, no {EXPECTED_EX1B_EVENTS}")
    metadata = read_json(root / "generated/data/ex1b/compton_events_metadata.json")
    if int(metadata.get("events", 0)) != EXPECTED_EX1B_EVENTS:
        fail("el metadato de 1B no corresponde a la producción FULL")
    return int(metadata.get("seed_1", 0))


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    seed_ex1a = validate_ex1a(root)
    seed_ex1b = validate_ex1b(root)
    print(
        "PASS: Clase 2 FULL; "
        f"1A={EXPECTED_EX1A_EVENTS_PER_THICKNESS} eventos × 6 "
        f"(seed base {seed_ex1a}), "
        f"1B={EXPECTED_EX1B_EVENTS} eventos (seed {seed_ex1b})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
