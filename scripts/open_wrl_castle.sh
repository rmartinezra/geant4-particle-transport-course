#!/usr/bin/env bash
set -euo pipefail

# Abre un WRL del checkout con Castle Model Viewer en el sistema anfitrión.
# En WSL usa por defecto la copia portátil preparada por setup_castle_viewer_windows.sh.

if [[ $# -ne 1 ]]; then
  echo "Uso: $0 RUTA_AL_ARCHIVO.wrl" >&2
  exit 2
fi

model="$1"
if [[ "$model" != /* ]]; then
  model="$PWD/$model"
fi

if [[ ! -f "$model" ]]; then
  echo "ERROR: no existe el WRL: $model" >&2
  echo "Genera uno, por ejemplo, con:" >&2
  echo "  docker compose run --rm geant4-course make visualize-ex1a" >&2
  exit 1
fi

if [[ "${model,,}" != *.wrl ]]; then
  echo "ERROR: se esperaba un archivo con extensión .wrl: $model" >&2
  exit 1
fi

if [[ -n "${CASTLE_VIEWER_EXE:-}" ]]; then
  viewer="$CASTLE_VIEWER_EXE"
elif uname -r | grep -qi microsoft; then
  for command_name in cmd.exe wslpath; do
    if ! command -v "$command_name" >/dev/null 2>&1; then
      echo "ERROR: WSL no proporciona el comando '$command_name'." >&2
      exit 1
    fi
  done
  windows_profile_win="$(cmd.exe /C 'echo %USERPROFILE%' 2>/dev/null | tr -d '\r')"
  if [[ -z "$windows_profile_win" || "$windows_profile_win" == *%USERPROFILE%* ]]; then
    echo "ERROR: no se pudo determinar el perfil del usuario de Windows." >&2
    exit 1
  fi
  windows_profile="$(wslpath -u "$windows_profile_win")"
  viewer="$windows_profile/Apps/CastleModelViewer-5.2.0/castle-model-viewer/castle-model-viewer.exe"
else
  viewer="$(command -v castle-model-viewer || true)"
fi

if [[ -z "$viewer" || ! -f "$viewer" ]]; then
  echo "ERROR: no se encontró Castle Model Viewer." >&2
  if uname -r | grep -qi microsoft; then
    echo "Prepáralo una sola vez desde WSL:" >&2
    echo "  ./scripts/setup_castle_viewer_windows.sh" >&2
  else
    echo "Instálalo desde https://castle-engine.io/castle-model-viewer" >&2
    echo "o define CASTLE_VIEWER_EXE con la ruta del ejecutable." >&2
  fi
  exit 1
fi

if uname -r | grep -qi microsoft && [[ "${viewer,,}" == *.exe ]]; then
  if ! command -v wslpath >/dev/null 2>&1; then
    echo "ERROR: WSL no proporciona el comando wslpath." >&2
    exit 1
  fi
  model_argument="$(wslpath -w "$model")"
else
  model_argument="$model"
fi

echo "[CASTLE] Abriendo $(basename "$model")"
"$viewer" "$model_argument" >/dev/null 2>&1 &
echo "[OK] Castle Model Viewer se inició en el sistema anfitrión."
