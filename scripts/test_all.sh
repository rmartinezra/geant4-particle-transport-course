#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"
make build
make visualize-all VIS_EVENTS="${VIS_EVENTS:-10}" VIS_SEED="${VIS_SEED:-10101}"
for module in ex1a ex1b ex2 ex3 ex4; do
  make "run-$module" FAST=1 VIS=0 SEED="${SEED:-12345}"
  make "analyze-$module"
done
python3 scripts/validate_results.py
python3 scripts/check_repo_clean.py
echo "PASS: checkout → build → VRML → FAST → análisis → magnitudes físicas"
