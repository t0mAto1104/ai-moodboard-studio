#!/bin/bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "$0")/.." && pwd)"
PYTHON="${MOODBOARD_BUILD_PYTHON:-$ROOT/.build/venv/bin/python}"
if [[ "$(uname -m)" != arm64 ]]; then echo 'This release target requires an Apple Silicon build host.' >&2; exit 1; fi
npm --prefix "$ROOT/apps/web" run build
export PYINSTALLER_CONFIG_DIR="$ROOT/.build/pyinstaller-cache"
export MOODBOARD_DATA_DIR="$ROOT/.build/analysis-data"
export LITELLM_LOCAL_MODEL_COST_MAP=True
mkdir -p "$ROOT/.build" "$ROOT/releases"
"$PYTHON" -m PyInstaller --noconfirm --distpath "$ROOT/.build/dist" --workpath "$ROOT/.build/work" "$ROOT/desktop/MoodBoard.spec"
"$PYTHON" "$ROOT/scripts/audit-bundle.py" "$ROOT/.build/dist/AI Mood Board Studio.app" --output "$ROOT/docs/package-audit.json"
