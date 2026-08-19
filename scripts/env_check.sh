#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EXPECTED_GEANT4="11.2.2"
JOBS="${BUILD_JOBS:-2}"

ok() {
  printf '[OK] %s\n' "$1"
}

fail() {
  printf '[ERROR] %s\n' "$1" >&2
  exit 1
}

require_command() {
  local command_name="$1"
  local label="$2"
  command -v "$command_name" >/dev/null 2>&1 \
    || fail "No se encontró ${label} (${command_name})."
  ok "${label}: $(command -v "$command_name")"
}

printf '%s\n' 'Comprobación ligera del entorno para la Clase 1'
printf '%s\n' '------------------------------------------------'

if [[ -f /.dockerenv || "${container:-}" == "docker" ]]; then
  ok 'Contenedor Docker accesible'
else
  fail 'Este target debe ejecutarse con docker compose run --rm geant4-course make env-check.'
fi

require_command geant4-config 'Geant4'
geant4_version="$(geant4-config --version)"
[[ "$geant4_version" == "$EXPECTED_GEANT4" ]] \
  || fail "Se requiere Geant4 ${EXPECTED_GEANT4}; se encontró ${geant4_version}."
ok "Versión exacta de Geant4: ${geant4_version}"

require_command python3 'Python'
python3 - <<'PY'
import importlib

for name in ("numpy", "scipy", "matplotlib"):
    module = importlib.import_module(name)
    print(f"[OK] Python {name}: {module.__version__}")
PY

require_command cmake 'CMake'
ok "$(cmake --version | head -n 1)"
require_command c++ 'Compilador C++'
ok "$(c++ --version | head -n 1)"

declare -a DATASET_VARIABLES=(
  G4LEDATA
  G4LEVELGAMMADATA
  G4RADIOACTIVEDATA
  G4PARTICLEXSDATA
  G4NEUTRONHPDATA
  G4ENSDFSTATEDATA
)

for variable_name in "${DATASET_VARIABLES[@]}"; do
  dataset_path="${!variable_name:-}"
  [[ -n "$dataset_path" ]] || fail "La variable ${variable_name} no está definida."
  [[ -d "$dataset_path" ]] || fail "No existe el dataset ${variable_name}: ${dataset_path}"
  if ! find "$dataset_path" -type f -print -quit | grep -q .; then
    fail "El dataset ${variable_name} está vacío: ${dataset_path}"
  fi
  ok "Dataset ${variable_name} accesible"
done

mkdir -p "$ROOT_DIR/generated"
write_probe="$(mktemp "$ROOT_DIR/generated/.env-check-write.XXXXXX")"
rm -f -- "$write_probe"
ok 'generated/ puede crearse y escribirse en el volumen del host'

G4_CMAKE_DIR="${Geant4_DIR:-$(geant4-config --prefix)/lib/cmake/Geant4}"
CHECK_BUILD_ROOT="$ROOT_DIR/build/env-check"
declare -a COMPTON_MODULES=(
  'ex1a|exercises/01_compton/A_cross_section|TestEm13'
  'ex1b|exercises/01_compton/B_kinematics|TestEm14'
)

for item in "${COMPTON_MODULES[@]}"; do
  name="${item%%|*}"
  remainder="${item#*|}"
  source_dir="${remainder%%|*}"
  executable="${remainder##*|}"
  build_dir="$CHECK_BUILD_ROOT/$name"
  printf '[CHECK] Compilación mínima de %s\n' "$name"
  cmake -S "$ROOT_DIR/$source_dir" -B "$build_dir" \
    -DGeant4_DIR="$G4_CMAKE_DIR" \
    -DWITH_GEANT4_UIVIS=ON \
    -DCMAKE_BUILD_TYPE=Release >/dev/null
  cmake --build "$build_dir" -j"$JOBS" >/dev/null
  [[ -x "$build_dir/$executable" ]] \
    || fail "No se creó el ejecutable ${executable}."
  ok "Módulo ${name} compilado"
done

temp_dir="$(mktemp -d -t geant4-class01-vrml.XXXXXX)"
cleanup() {
  rm -rf -- "$temp_dir"
}
trap cleanup EXIT

sed 's#/run/beamOn 10#/run/beamOn 1#' \
  "$ROOT_DIR/exercises/01_compton/A_cross_section/macros/visualization.mac" \
  > "$temp_dir/vrml_smoke.mac"

(
  cd "$temp_dir"
  "$CHECK_BUILD_ROOT/ex1a/TestEm13" "$temp_dir/vrml_smoke.mac" 1 \
    > "$temp_dir/vrml_smoke.log" 2>&1
)

grep -q 'VRML2FILE' "$temp_dir/vrml_smoke.log" \
  || fail 'Geant4 no confirmó el driver VRML2FILE.'
wrl_file="$(find "$temp_dir" -maxdepth 1 -type f -name '*.wrl' -size +0c -print -quit)"
[[ -n "$wrl_file" ]] || fail 'VRML2FILE no produjo un archivo temporal.'
head -n 1 "$wrl_file" | grep -q '^#VRML V2.0 utf8' \
  || fail 'El archivo VRML2 temporal no tiene una cabecera válida.'
ok 'VRML2FILE generó un archivo temporal válido y se eliminará al terminar'

printf '\n%s\n' 'Entorno listo para la Clase 1.'
