"""Check chapter structure and local Markdown targets; no network or external packages."""
from pathlib import Path
import json
import re
import sys
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]

def main() -> None:
    errors: list[str] = []
    manifest = json.loads((ROOT / 'maintainers/chapter-manifest.json').read_text())
    if len(manifest) != 18:
        errors.append(f'Expected 18 chapters, found {len(manifest)}')
    for item in manifest:
        path = ROOT / item['path']
        if not path.is_file():
            errors.append(f'Missing chapter: {path}')
            continue
        text = path.read_text()
        if '## References' not in text or '**Material status:**' not in text:
            errors.append(f'Missing chapter metadata or references: {path.relative_to(ROOT)}')
        if len(text.split()) < 250:
            errors.append(f'Chapter is too short for the declared draft: {path.relative_to(ROOT)}')
    checked = 0
    for path in ROOT.rglob('*.md'):
        if any(part.startswith('.') for part in path.relative_to(ROOT).parts):
            continue
        text = re.sub(r'```.*?```', '', path.read_text(), flags=re.S)
        for link in re.findall(r'\[[^\]]*\]\(([^)]+)\)', text):
            link = link.strip().split(' "')[0].strip('<>')
            if not link or re.match(r'^[a-zA-Z][\w+.-]*:', link) or link.startswith('#'):
                continue
            target = unquote(link.split('#', 1)[0])
            if not target:
                continue
            checked += 1
            if not (path.parent / target).exists():
                errors.append(f'{path.relative_to(ROOT)} -> missing {target}')
    report = {'chapters': len(manifest), 'local_links_checked': checked, 'errors': errors}
    print(json.dumps(report, indent=2))
    sys.exit(bool(errors))

if __name__ == '__main__':
    main()
