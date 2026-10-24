#!/bin/bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "$0")/.." && pwd)"
PYTHON="${MOODBOARD_PYTHON:-$ROOT/.venv/bin/python}"
if [[ ! -x "$PYTHON" && -x "$ROOT/../.venv/bin/python" ]]; then PYTHON="$ROOT/../.venv/bin/python"; fi
if [[ ! -x "$PYTHON" ]]; then echo 'Create .venv and install requirements-tested.txt first.' >&2; exit 1; fi
cd "$ROOT/apps/api"
"$PYTHON" -m alembic upgrade head
exec "$PYTHON" -m uvicorn app.main:app --host 127.0.0.1 --port 8765
