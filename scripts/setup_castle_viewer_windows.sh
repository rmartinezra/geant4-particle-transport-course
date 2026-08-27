#!/usr/bin/env bash
set -euo pipefail

# Instala de forma portátil Castle Model Viewer para Windows desde WSL.
# No debe ejecutarse dentro del contenedor Docker.

VERSION="5.2.0"
ARCHIVE_NAME="castle-model-viewer-${VERSION}-win64-x86_64.zip"
DOWNLOAD_URL="https://github.com/castle-engine/castle-model-viewer/releases/download/v${VERSION}/${ARCHIVE_NAME}"
EXPECTED_SHA256="3e0f8da90e4ed14690a8f62196ecf11e1ac31cb217a867f573ecf2768540584d"

if ! uname -r | grep -qi microsoft; then
  echo "ERROR: este instalador prepara la aplicación nativa de Windows desde WSL." >&2
  echo "En Linux nativo descarga la versión Linux desde https://castle-engine.io/castle-model-viewer" >&2
  exit 1
fi

for command_name in cmd.exe curl sha256sum unzip wslpath; do
  if ! command -v "$command_name" >/dev/null 2>&1; then
    echo "ERROR: falta '$command_name' en WSL." >&2
    exit 1
  fi
done

windows_profile_win="$(cmd.exe /C 'echo %USERPROFILE%' 2>/dev/null | tr -d '\r')"
if [[ -z "$windows_profile_win" || "$windows_profile_win" == *%USERPROFILE%* ]]; then
  echo "ERROR: no se pudo determinar el perfil del usuario de Windows." >&2
  exit 1
fi

WINDOWS_PROFILE="$(wslpath -u "$windows_profile_win")"
APPS_DIR="$WINDOWS_PROFILE/Apps"
ARCHIVE="$WINDOWS_PROFILE/Downloads/$ARCHIVE_NAME"
INSTALL_DIR="$APPS_DIR/CastleModelViewer-${VERSION}"
EXECUTABLE="$INSTALL_DIR/castle-model-viewer/castle-model-viewer.exe"

if [[ -f "$EXECUTABLE" ]]; then
  echo "[OK] Castle Model Viewer ${VERSION} ya está preparado."
  echo "$EXECUTABLE"
  exit 0
fi

if [[ -e "$INSTALL_DIR" ]]; then
  echo "ERROR: existe una instalación incompleta en $INSTALL_DIR" >&2
  echo "Muévela o elimínala manualmente y vuelve a ejecutar este script." >&2
  exit 1
fi

mkdir -p "$APPS_DIR" "$(dirname "$ARCHIVE")"
if [[ ! -f "$ARCHIVE" ]]; then
  echo "[DOWNLOAD] Castle Model Viewer ${VERSION} para Windows x86_64"
  curl --fail --location --retry 3 --output "$ARCHIVE" "$DOWNLOAD_URL"
else
  echo "[CHECK] Reutilizando el ZIP que ya existe en Descargas."
fi

actual_sha256="$(sha256sum "$ARCHIVE" | awk '{print $1}')"
if [[ "$actual_sha256" != "$EXPECTED_SHA256" ]]; then
  echo "ERROR: checksum SHA-256 inesperado; el archivo se conserva para auditoría:" >&2
  echo "$ARCHIVE" >&2
  echo "esperado: $EXPECTED_SHA256" >&2
  echo "obtenido: $actual_sha256" >&2
  exit 1
fi

temporary_dir="$(mktemp -d "$APPS_DIR/.CastleModelViewer-${VERSION}.XXXXXX")"
cleanup_temporary_dir() {
  if [[ -n "${temporary_dir:-}" && -d "$temporary_dir" ]]; then
    find "$temporary_dir" -mindepth 1 -delete
    rmdir "$temporary_dir"
  fi
}
trap cleanup_temporary_dir EXIT
unzip -q "$ARCHIVE" -d "$temporary_dir"

if [[ ! -f "$temporary_dir/castle-model-viewer/castle-model-viewer.exe" ]]; then
  echo "ERROR: el paquete no contiene castle-model-viewer.exe en la ruta esperada." >&2
  exit 1
fi

mv "$temporary_dir" "$INSTALL_DIR"
temporary_dir=""

if [[ ! -f "$EXECUTABLE" ]]; then
  echo "ERROR: no se pudo completar la instalación portátil." >&2
  exit 1
fi

echo "[OK] Castle Model Viewer ${VERSION} quedó preparado sin instalador."
echo "$EXECUTABLE"
echo "Ahora abre un WRL con:"
echo "  ./scripts/open_wrl_castle.sh generated/visualization/ex1a/compton_transmission_10events.wrl"
