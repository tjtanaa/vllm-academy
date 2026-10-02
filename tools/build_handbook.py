"""Build a Markdown handbook; --html also builds an offline HTML reader.

HTML rendering requires Mistune 3.x. Core teaching tests do not depend on it.
"""
from pathlib import Path
import argparse
import html
import json
import re

ROOT = Path(__file__).resolve().parents[1]

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--html', action='store_true', help='Also render the standalone HTML handbook')
    args = parser.parse_args()
    manifest = json.loads((ROOT / 'maintainers/chapter-manifest.json').read_text())
    sections = [('course-plan', 'Course blueprint', 'COURSE_BLUEPRINT.md'),
                ('curriculum', 'Curriculum and learning routes', 'SYLLABUS.md')]
    sections += [(f'lesson-{i:02d}', row['title'], row['path']) for i, row in enumerate(manifest)]
    sections += [('reading', 'Primary-source reading guide', 'READING_GUIDE.md'),
                 ('evidence', 'Version and evidence policy', 'VERSION_POLICY.md'),
                 ('references', 'References and provenance', 'REFERENCES.md')]
    intro = '''# vLLM Academy · Learning handbook

**Understand inference. Build a small engine. Read real vLLM. Make a useful contribution.**

Phase 1 materials from the original course seed. Independent course starter: 12 core lesson drafts and 6 advanced workshop briefs. The accompanying repository contains the reference implementation, tests, lab scripts and instructor materials.

The tiny engine is CPU-tested. It uses random weights, sequential execution and dense gathers from paged storage. It is not production vLLM. CUDA/ROCm serving recipes and advanced features are not hardware-validated by this package. Source reading uses vLLM v0.29.0 at an immutable commit, separately from runtime validation.

'''
    toc = '\n'.join(f'- [{title}](#{sid})' for sid,title,_ in sections)
    text = intro + '## Contents\n\n' + toc + '\n\n'
    for sid,title,path in sections:
        text += f'\n---\n\n<a id="{sid}"></a>\n\n' + (ROOT/path).read_text() + '\n'
    (ROOT/'HANDBOOK.md').write_text(text)
    if not args.html:
        return
    try:
        import mistune
    except ImportError:
        parser.exit(2, 'Markdown built. HTML requires Mistune 3.x; install the optional docs dependency.\n')
    md = mistune.create_markdown(plugins=['table'], escape=True)
    mapping = {path: '#'+sid for sid,_,path in sections}
    nav = ''.join(f'<a href="#{sid}">{html.escape(title)}</a>' for sid,title,_ in sections)
    body = ''
    for sid,title,path in sections:
        rendered = md((ROOT/path).read_text())
        for old,new in mapping.items():
            rendered = rendered.replace(f'href="{old}"', f'href="{new}"')
        body += f'<section id="{sid}" class="chapter">{rendered}</section>\n'
    css = '''
:root {--ink:#192d37;--muted:#566773;--accent:#086e65;--paper:#fcfcfa;--line:#dce5e5;--nav:#142c36;}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--paper);color:var(--ink);font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.75;font-size:16px}
a{color:var(--accent);text-decoration-thickness:1px;text-underline-offset:3px}aside{position:fixed;left:0;top:0;bottom:0;width:284px;background:var(--nav);color:#dce8e9;padding:28px 22px;overflow:auto}aside strong{display:block;font-size:24px;letter-spacing:-.8px;color:white}aside small{display:block;margin:5px 0 22px;color:#a8c2c4}aside a{display:block;color:#dce8e9;text-decoration:none;line-height:1.45;font-size:13px;padding:8px 10px;border-radius:5px}aside a:hover,aside a:focus{background:#244652;color:white}main{margin-left:284px;max-width:1200px;padding:60px 65px 100px}.eyebrow{text-transform:uppercase;letter-spacing:2px;font-size:12px;color:var(--accent);font-weight:750}.hero h1{font-size:48px;line-height:1.1;letter-spacing:-1.8px;margin:12px 0 22px}.subtitle{font-size:21px;line-height:1.55;max-width:730px}.stats{display:flex;gap:16px;margin:30px 0}.stat{flex:1;border:1px solid var(--line);padding:18px 20px;background:white;border-radius:10px}.stat b{display:block;font-size:29px;color:var(--accent);line-height:1.1}.stat span{font-size:12px;color:var(--muted)}.notice{border-left:4px solid #b98525;padding:16px 20px;background:#fff6e5;font-size:14px;line-height:1.65}.chapter{margin-top:64px;padding-top:28px;border-top:2px solid var(--line);scroll-margin-top:25px}.chapter>h1{font-size:30px;line-height:1.25;letter-spacing:-.6px;margin:0 0 22px}.chapter h2{font-size:22px;line-height:1.35;margin-top:32px}.chapter h3{font-size:18px;margin-top:26px}p{margin:14px 0}pre{white-space:pre;overflow:auto;background:#eef3f4;border:1px solid var(--line);border-radius:8px;padding:19px;line-height:1.6;font-size:12.5px}code{font-family:ui-monospace,SFMono-Regular,Consolas,monospace;font-size:.88em;overflow-wrap:anywhere}p code,td code,li code{background:#eaf0ef;padding:2px 4px;border-radius:3px}table{border-collapse:collapse;width:100%;display:block;overflow-x:auto;font-size:13px;margin:22px 0}th,td{text-align:left;border-bottom:1px solid var(--line);padding:10px 13px;vertical-align:top;min-width:100px}th{background:#e7efee;color:var(--ink);line-height:1.5}tr:nth-child(even)td{background:#f4f7f6}blockquote{border-left:3px solid var(--accent);margin-left:0;padding-left:20px;color:var(--muted)}li{margin:5px 0}footer{margin-top:60px;color:var(--muted);font-size:13px;border-top:1px solid var(--line);padding-top:20px}
@media(max-width:1050px){aside{width:235px;padding:22px 14px}main{margin-left:235px;padding:40px 30px}.hero h1{font-size:40px}}
@media(max-width:760px){aside{position:static;width:auto;max-height:300px}main{margin-left:0;padding:35px 22px}.hero h1{font-size:36px}.stats{gap:8px}.stat{padding:14px 10px}.stat b{font-size:23px}.subtitle{font-size:18px}}
@media print{aside{display:none}main{margin:0;max-width:none;padding:0}.chapter{break-before:page}.notice{border:1px solid #999}a{color:inherit}pre{white-space:pre-wrap;overflow-wrap:anywhere}.hero h1{font-size:36px}}
'''
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="description" content="An independent, correctness-first vLLM course starter: build, test, read source and contribute."><title>vLLM Academy · Learning handbook</title><style>{css}</style></head><body>
<aside aria-label="Handbook navigation"><strong>vLLM Academy</strong><small>PHASE 1 LEARNING HANDBOOK</small>{nav}</aside>
<main><header class="hero"><div class="eyebrow">An independent engineering course</div><h1>From first token<br>to first useful contribution.</h1><p class="subtitle">Understand inference. Build a small engine. Read real vLLM. Learn to prove that an optimization is correct.</p><div class="stats"><div class="stat"><b>12</b><span>CORE LESSON DRAFTS</span></div><div class="stat"><b>6</b><span>ADVANCED WORKSHOP BRIEFS</span></div><div class="stat"><b>30</b><span>BASELINE CPU TESTS</span></div></div><div class="notice"><strong>Read the evidence boundary.</strong> The tiny engine is CPU-tested, with random weights and serial execution. CUDA and ROCm serving recipes remain unverified on hardware. Production source reading is pinned to vLLM v0.29.0; it is not a runtime validation claim. Human instructional review is pending.</div></header>
{body}<footer>Phase 1 materials from the original course seed. Original materials inspired by the learning progression of zero-to-sglang. No official affiliation or endorsement is implied. Source code, tests, templates and instructor notes are included in the accompanying repository archive.</footer></main></body></html>'''
    (ROOT/'START_HERE.html').write_text(page)
    print(json.dumps({'handbook':'HANDBOOK.md','html':'START_HERE.html','chapters':len(manifest),'renderer':mistune.__version__}))

if __name__ == '__main__':
    main()
