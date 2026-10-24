#!/bin/bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "$0")/.." && pwd)"
APP="$ROOT/.build/dist/AI Mood Board Studio.app"
PYTHON="${MOODBOARD_BUILD_PYTHON:-$ROOT/.build/venv/bin/python}"
"$PYTHON" "$ROOT/scripts/audit-bundle.py" "$APP" --output "$ROOT/docs/package-audit.json"
codesign --verify --deep --strict "$APP"
STAGE="$(mktemp -d "$ROOT/.build/dmg-stage.XXXXXX")"
ditto "$APP" "$STAGE/AI Mood Board Studio.app"
ln -s /Applications "$STAGE/Applications"
cp "$ROOT/desktop/INSTALL.txt" "$STAGE/安装说明.txt"
mkdir -p "$ROOT/releases"
DMG="$ROOT/releases/AI-Mood-Board-Studio-0.1.0-macOS-arm64.dmg"
hdiutil create -volname 'AI Mood Board Studio' -srcfolder "$STAGE" -ov -format UDZO "$DMG"
hdiutil verify "$DMG"
(cd "$ROOT/releases"; shasum -a 256 "$(basename "$DMG")" > "$(basename "$DMG").sha256")
cp "$ROOT/desktop/INSTALL.txt" "$ROOT/releases/安装说明.txt"
echo "$DMG"
