#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
target="$ROOT_DIR/generated"
if [[ -d "$target" && "$target" == "$ROOT_DIR/generated" ]]; then
  find "$target" -mindepth 1 -delete
fi
echo "generated/ quedó vacío."
