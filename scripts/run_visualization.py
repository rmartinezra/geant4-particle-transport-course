#!/usr/bin/env python3
"""Genera y valida un WRL VRML2 headless a partir de una macro docente."""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


MODULES = {
    "ex1a": ("build/ex1a/TestEm13", "exercises/01_compton/A_cross_section/macros/visualization.mac",
             "compton_transmission"),
    "ex1b": ("build/ex1b/TestEm14", "exercises/01_compton/B_kinematics/macros/visualization.mac",
             "compton_kinematics"),
    "ex2": ("build/ex2/TestEm5", "exercises/02_multiple_scattering/macros/visualization.mac",
            "muon_mcs"),
    "ex3": ("build/ex3/TestEm18", "exercises/03_energy_loss/macros/visualization.mac",
            "muon_energy_loss"),
    "ex4": ("build/ex4/Hadr03", "exercises/04_nuclear_cross_section/macros/visualization.mac",
            "neutron_fission"),
}


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("module", choices=MODULES)
    parser.add_argument("--events", type=int, default=10)
    parser.add_argument("--seed", type=int, default=10101)
    return parser.parse_args()


def main() -> int:
    args = arguments()
    if args.events < 10:
        raise SystemExit("VIS_EVENTS nunca puede ser menor que 10")
    root = Path(__file__).resolve().parents[1]
    executable_rel, macro_rel, basename = MODULES[args.module]
    executable = root / executable_rel
    source_macro = root / macro_rel
    if not executable.is_file():
        raise SystemExit(f"No existe {executable}; ejecute make build")
    text = source_macro.read_text(encoding="utf-8")
    text, n_beam = re.subn(r"/run/beamOn\s+\d+", f"/run/beamOn {args.events}", text)
    text, n_seed = re.subn(r"/random/setSeeds\s+\d+\s+\d+",
                           f"/random/setSeeds {args.seed} {args.seed + 1}", text)
    if n_beam != 1 or n_seed != 1 or "/vis/open VRML2FILE" not in text:
        raise RuntimeError(f"Macro de visualización inválida: {source_macro}")

    output_dir = root / "generated" / "visualization" / args.module
    logs_dir = root / "generated" / "logs" / "visualization" / args.module
    output_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=f"{args.module}_", dir=logs_dir) as temp_name:
        temp = Path(temp_name)
        macro = temp / "visualization.mac"
        macro.write_text(text, encoding="utf-8")
        env = os.environ.copy()
        if args.module == "ex4":
            env["G4COURSE_KEEP_SECONDARIES"] = "1"
        command = [str(executable), str(macro)]
        # TestEm13 conserva su argumento histórico de número de threads.
        # Un único worker garantiza una sola escena acumulada reproducible.
        if args.module == "ex1a":
            command.append("1")
        completed = subprocess.run(command, cwd=temp, env=env,
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                   text=True, check=False)
        (logs_dir / f"{basename}_{args.events}events.log").write_text(
            completed.stdout, encoding="utf-8"
        )
        if completed.returncode != 0:
            raise RuntimeError(f"Geant4 terminó con código {completed.returncode}")
        if "VRML2FILE" not in completed.stdout:
            raise RuntimeError("La salida no confirma el driver VRML2FILE")
        bad = ("command not found", "ERROR: G4VisCommand", "ERROR: No graphics system")
        if any(token.lower() in completed.stdout.lower() for token in bad):
            raise RuntimeError("Geant4 informó un error de visualización")
        generated = sorted(temp.glob("*.wrl"))
        if not generated:
            raise RuntimeError("VRML2FILE no produjo ningún WRL")
        # VRML2FILE puede cerrar una escena de geometría y otra acumulada al
        # hacer flush. La escena acumulada con trayectorias es la más grande;
        # solo esa se publica bajo el nombre pedagógico determinista.
        selected = max(generated, key=lambda path: path.stat().st_size)
        header = selected.read_bytes()[:80]
        if not header.startswith(b"#VRML V2.0 utf8"):
            raise RuntimeError("Cabecera VRML2 inválida")
        destination = output_dir / f"{basename}_{args.events}events.wrl"
        shutil.move(str(selected), destination)
    if destination.stat().st_size == 0:
        raise RuntimeError("El WRL está vacío")
    metadata = output_dir / f"{basename}_{args.events}events.metadata.txt"
    metadata.write_text(
        f"module={args.module}\nevents={args.events}\nseed={args.seed}\n"
        f"driver=VRML2FILE\nfile={destination.name}\nbytes={destination.stat().st_size}\n",
        encoding="utf-8",
    )
    print(f"[VIS] {destination.relative_to(root)} ({destination.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
