#!/usr/bin/env python3
"""Smoke tests físicos y de los cinco archivos VRML generados."""

from __future__ import annotations

import re
from pathlib import Path


def value(text: str, key: str) -> float:
    match = re.search(rf"^{re.escape(key)}\s*=\s*([0-9.eE+\-]+)", text, re.M)
    if not match:
        raise RuntimeError(f"No se encontró {key}")
    return float(match.group(1))


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    fits = root / "generated" / "fits"
    ex1a = (fits / "ex1a/summary_A.txt").read_text(encoding="utf-8")
    ex1b = (fits / "ex1b/summary_B.txt").read_text(encoding="utf-8")
    ex2 = (fits / "ex2/summary_mcs.txt").read_text(encoding="utf-8")
    ex3 = (fits / "ex3/summary_energy_loss.txt").read_text(encoding="utf-8")
    ex4 = (fits / "ex4/summary_hadronic.txt").read_text(encoding="utf-8")
    checks = {
        "ex1a_sigma": 1.0 < value(ex1a, "sigma_barn_per_atom") < 10.0,
        "ex1b_mass": 480.0 < value(ex1b, "M_linear_fit_keV") < 540.0,
        "ex2_alpha_x": 0.3 < value(ex2, "alpha_thickness") < 0.7,
        "ex2_alpha_p": 0.7 < value(ex2, "alpha_momentum") < 1.3,
        "ex3_dedx": 1.0 < value(ex3, "dEdx_measured_MeV_cm") < 5.0,
        "ex4_lambda": value(ex4, "lambda_cm") > 0.0,
        "ex4_sigma": value(ex4, "microscopic_cross_section_barn") > 0.0,
    }
    for module in ("ex1a", "ex1b", "ex2", "ex3", "ex4"):
        files = list((root / "generated/visualization" / module).glob("*.wrl"))
        checks[f"{module}_wrl"] = len(files) >= 1 and all(
            path.stat().st_size > 0 and path.read_bytes().startswith(b"#VRML V2.0 utf8")
            for path in files
        )
    for name, passed in checks.items():
        print(f"{'PASS' if passed else 'FAIL'}: {name}")
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
