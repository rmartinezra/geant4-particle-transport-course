#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if ! command -v geant4-config >/dev/null 2>&1; then
  echo "ERROR: geant4-config no está disponible." >&2
  exit 1
fi
if [[ "$(geant4-config --version)" != "11.2.2" ]]; then
  echo "ERROR: se requiere Geant4 11.2.2; se encontró $(geant4-config --version)." >&2
  exit 1
fi

G4_CMAKE_DIR="${Geant4_DIR:-$(geant4-config --prefix)/lib/cmake/Geant4}"
JOBS="${BUILD_JOBS:-2}"
declare -a MODULES=(
  "ex1a|exercises/01_compton/A_cross_section"
  "ex1b|exercises/01_compton/B_kinematics"
  "ex2|exercises/02_multiple_scattering"
  "ex3|exercises/03_energy_loss"
  "ex4|exercises/04_nuclear_cross_section"
)

for item in "${MODULES[@]}"; do
  name="${item%%|*}"
  source_dir="${item#*|}"
  echo "[BUILD] ${name}"
  cmake -S "$ROOT_DIR/$source_dir" -B "$ROOT_DIR/build/$name" \
    -DGeant4_DIR="$G4_CMAKE_DIR" -DWITH_GEANT4_UIVIS=ON \
    -DCMAKE_BUILD_TYPE=Release
  cmake --build "$ROOT_DIR/build/$name" -j"$JOBS"
done

echo "[BUILD] Geant4 $(geant4-config --version); cinco módulos compilados."
