#!/bin/bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "$0")/.." && pwd)"
PYTHON="${MOODBOARD_PYTHON:-$ROOT/.venv/bin/python}"
if [[ ! -x "$PYTHON" && -x "$ROOT/../.venv/bin/python" ]]; then PYTHON="$ROOT/../.venv/bin/python"; fi
cd "$ROOT"
"$PYTHON" -m pytest apps/api/tests -q
npm --prefix apps/web test -- --run
npm --prefix apps/web run build
"$PYTHON" scripts/smoke.py
