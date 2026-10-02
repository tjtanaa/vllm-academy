"""Validate the course's source locations against a local vLLM checkout; no network."""
import argparse
import json
from pathlib import Path
import subprocess


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('checkout', type=Path)
    p.add_argument('--allow-different-commit', action='store_true')
    a = p.parse_args()
    manifest = json.loads((Path(__file__).resolve().parents[1] / 'maintainers/source-map.json').read_text())
    try:
        sha = subprocess.check_output(['git','-C',str(a.checkout),'rev-parse','HEAD'],text=True).strip()
    except (OSError, subprocess.SubprocessError) as exc:
        p.exit(2, f'Cannot inspect git checkout: {exc}\n')
    if sha != manifest['commit'] and not a.allow_different_commit:
        p.exit(2, f'Expected {manifest["commit"]}, found {sha}. Use the pinned checkout or explicitly allow drift.\n')
    failures = []
    for item in manifest['files']:
        f = a.checkout / item['path']
        if not f.is_file():
            failures.append(item['path'] + ': missing')
            continue
        text = f.read_text()
        for symbol in item.get('search_terms',[]):
            if symbol not in text:
                failures.append(item['path'] + ': missing term ' + symbol)
    print(json.dumps({'commit':sha,'checked_files':len(manifest['files']),'failures':failures},indent=2))
    raise SystemExit(bool(failures))


if __name__ == '__main__':
    main()
