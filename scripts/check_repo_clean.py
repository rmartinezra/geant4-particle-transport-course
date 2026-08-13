#!/usr/bin/env python3
"""Falla si el contenido publicable contiene datos, builds o rutas privadas."""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path


FORBIDDEN_SUFFIXES = {".csv", ".root", ".hdf5", ".npy", ".npz", ".wrl", ".log", ".pyc"}
FORBIDDEN_PARTS = {"build", "logs", "__pycache__", "CMakeFiles"}
GENERATED_PARTS = {".git", "build", "generated", "logs", "__pycache__", "CMakeFiles"}
DATASET_PREFIXES = ("G4NDL", "G4EMLOW", "PhotonEvaporation", "RadioactiveDecay",
                    "G4PARTICLEXS", "G4PII", "RealSurface", "G4SAIDDATA",
                    "G4ABLA", "G4INCL", "G4ENSDFSTATE", "G4CHANNELING", "G4TENDL")
PRIVATE_PATTERNS = (
    re.compile(r"C:\\" r"Users\\", re.I), re.compile(r"/mnt/c/" r"Users/", re.I),
    re.compile(r"One" r"Drive", re.I), re.compile(r"/home/[A-Za-z0-9._-]+/"),
)
MAX_BYTES = 5 * 1024 * 1024


def tracked(root: Path) -> list[Path]:
    if shutil.which("git") and (root / ".git").exists():
        completed = subprocess.run(["git", "ls-files", "-z"], cwd=root,
                                   stdout=subprocess.PIPE, check=True)
        return [root / item.decode() for item in completed.stdout.split(b"\0") if item]
    # La imagen didáctica no necesita Git. En un checkout exportado se revisa
    # todo el árbol publicable y se omiten únicamente artefactos regenerables.
    return [path for path in root.rglob("*")
            if path.is_file()
            and not any(part in GENERATED_PARTS for part in path.relative_to(root).parts)]


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    problems: list[str] = []
    files = tracked(root)
    for path in files:
        rel = path.relative_to(root)
        if not path.is_file():
            continue
        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            problems.append(f"tipo prohibido: {rel}")
        if any(part in FORBIDDEN_PARTS for part in rel.parts):
            problems.append(f"directorio prohibido: {rel}")
        if any(part.startswith(DATASET_PREFIXES) for part in rel.parts):
            problems.append(f"dataset Geant4: {rel}")
        if path.stat().st_size > MAX_BYTES:
            problems.append(f"archivo >5 MiB: {rel}")
        if path.suffix.lower() in {".png", ".jpg", ".jpeg"}:
            if not str(rel).startswith("examples/"):
                problems.append(f"imagen fuera de examples/: {rel}")
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError as exc:
            problems.append(f"no se pudo leer {rel}: {exc}")
            continue
        for pattern in PRIVATE_PATTERNS:
            if pattern.search(content):
                problems.append(f"ruta privada ({pattern.pattern}): {rel}")
    if problems:
        print("FAIL: repositorio no publicable")
        print("\n".join(f"- {item}" for item in sorted(set(problems))))
        return 1
    print(f"PASS: {len(files)} archivos publicables, sin datos Monte Carlo ni rutas privadas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
