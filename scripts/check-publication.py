"""Fail a public source snapshot check without printing matched secret values."""
import argparse
import json
from pathlib import Path
import re

PATTERNS = [r'gh[pousr]_[A-Za-z0-9]{30,}', r'github_pat_[A-Za-z0-9_]{30,}',
            r'sk-(?:proj-|ant-)[A-Za-z0-9_-]{24,}', r'AIza[A-Za-z0-9_-]{30,}',
            r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----']
FORBIDDEN = {'.local', '.venv', '.model-tools', '.build', 'node_modules', 'releases', '__pycache__'}

def check(root):
    files = [p for p in root.rglob('*') if p.is_file() and '.git' not in p.relative_to(root).parts]
    findings = []
    links = []
    for p in files:
        relative = p.relative_to(root)
        if any(v in FORBIDDEN for v in relative.parts) or p.suffix in {'.safetensors', '.gguf', '.dmg', '.sqlite', '.log', '.pyc'}:
            findings.append(str(relative))
        if p.stat().st_size > 10_000_000: findings.append('large-file:'+str(relative))
        if p.suffix in {'.png', '.icns'}: continue
        value = p.read_text(encoding='utf-8')
        if '\x00' in value or any(re.search(pattern, value) for pattern in PATTERNS):
            findings.append('sensitive-or-binary:'+str(relative))
        if p.suffix == '.md':
            for link in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)', value):
                link = link.split('#')[0]
                if link and not re.match(r'[a-z]+:', link) and not (p.parent/link).exists():
                    links.append(str(relative)+':'+link)
    report = {'passed':not findings and not links, 'files':len(files),
              'bytes':sum(p.stat().st_size for p in files),
              'findings':findings, 'broken_relative_links':links,
              'scope':'source snapshot only; pattern scan is not proof that arbitrary secrets are absent'}
    return report

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('directory', type=Path)
    args = parser.parse_args()
    report = check(args.directory)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report['passed'] else 1)
