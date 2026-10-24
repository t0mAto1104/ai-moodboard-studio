"""Produce a reviewable, source-only publication snapshot; never copy private runtime data."""
import argparse
import json
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
TOP = {'README.md', 'README.en.md', 'AGENTS.md', 'CHANGELOG.md', 'CONTRIBUTING.md',
       'NOTICE.md', '.gitignore', '.env.example', 'requirements-tested.txt'}
DIRS = {'apps', 'fixtures', 'scripts', 'desktop', 'docs', '.github'}
SKIP_PARTS = {'.git', '.local', '.venv', '.model-tools', '.build', '.publish', 'releases', 'node_modules',
              'dist', '__pycache__', '.pytest_cache', '.cache'}
REPORTS = {'benchmark-metadata.json', 'benchmark-siglip2.json', 'benchmark-siglip2-mps.json',
           'desktop-release-report.json', 'desktop-model-test.json', 'desktop-mps-test.json',
           'desktop-dmg-test.json', 'package-audit.json', 'openverse-contract.json', 'stock-export-live.json', 'desktop-frozen-test.json'}

def clean(value):
    if isinstance(value, dict): return {k: clean(v) for k, v in value.items()}
    if isinstance(value, list): return [clean(v) for v in value]
    if isinstance(value, str):
        value = re.sub(r'/Users/[^/\s]+', '/Users/LOCAL_USER', value)
        value = value.replace('/Volumes/KINGSTON/', '/Volumes/YOUR_DISK/')
    return value

def export(destination):
    destination = destination.resolve()
    if destination.exists(): raise ValueError('Use a new empty publication directory')
    destination.mkdir(parents=True)
    for source in sorted(ROOT.rglob('*')):
        relative = source.relative_to(ROOT)
        if any(p in SKIP_PARTS for p in relative.parts): continue
        if source.is_symlink() or not source.is_file(): continue
        if len(relative.parts) == 1 and relative.name not in TOP: continue
        if len(relative.parts) > 1 and relative.parts[0] not in DIRS: continue
        if source.suffix in {'.log', '.pyc', '.tsbuildinfo', '.sqlite', '.safetensors', '.gguf', '.dmg'}: continue
        if relative.name == '.DS_Store': continue
        if relative.parts[0] == 'docs':
            if relative.name in {'progress.md', 'design-reference.txt'}: continue
            if source.suffix == '.json' and relative.name not in REPORTS: continue
            if source.suffix == '.png' and relative.name != 'ui-desktop-package.png': continue
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.suffix == '.json' and relative.parts[0] == 'docs':
            target.write_text(json.dumps(clean(json.loads(source.read_text())), ensure_ascii=False, indent=2)+'\n')
        else:
            shutil.copy2(source, target)
    (destination/'docs/progress.md').write_text(
        '# Public development record\n\n'
        '2026-10-24: Local MVP and Apple Silicon desktop preview completed. '
        'Backend 67 tests, frontend 11 tests, production build, isolated Mock workflow, '
        'native window lifecycle, read-only DMG relocation and external SigLIP CPU/MPS encoding passed. '
        'Private development logs and live user-data reports are intentionally excluded.\n\n'
        'See validation.md, CHANGELOG.md and known-limitations.md for scope and remaining work.\n')
    return destination

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    print(export(args.destination))
