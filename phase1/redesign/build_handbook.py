"""Build an offline handbook; no network and no bundled external fonts/assets."""
from pathlib import Path
from urllib.parse import urlparse, unquote
import base64, html, json, re
import mistune

P=Path(__file__).resolve().parent
ORDER=['README.md','CURRICULUM.md','SOURCE_REVIEW.md']
ORDER += [str(f.relative_to(P)) for f in sorted((P/'lessons').glob('*.md'))]
ORDER += ['ARCHITECTURE_ATLAS.md','MODEL_ACCEPTANCE.md','GLOSSARY.md',
          'INSTRUCTOR_GUIDE.md','INTEGRATION.md','VALIDATION.md','SOURCE_MAP.md','REFERENCES.md']
RESOURCES=sorted([str(f.relative_to(P)) for folder in ['labs','tests','results','figures']
                  for f in (P/folder).glob('*') if f.suffix in ['.py','.json','.txt','.dot']])
RESOURCES += ['references.json','source-map.json','curriculum.json','pyproject.toml']

def ident(path):return 'section-'+re.sub(r'[^a-zA-Z0-9]+','-',str(path)).strip('-').lower()

class Renderer(mistune.HTMLRenderer):
    source='README.md'
    def link(self,text,url,title=None):
        original=url
        if not urlparse(url).scheme and not url.startswith('#'):
            target=((P/self.source).parent/unquote(url.split('#',1)[0])).resolve()
            try:relative=str(target.relative_to(P))
            except ValueError:relative=''
            if relative in ORDER or relative in RESOURCES:url='#'+ident(relative)
            elif target.is_file() and target.suffix in {'.png','.svg'}:
                mime='image/svg+xml' if target.suffix=='.svg' else 'image/png'
                url='data:'+mime+';base64,'+base64.b64encode(target.read_bytes()).decode()
        return super().link(text,url,title)
    def image(self,text,url,title=None):
        target=((P/self.source).parent/unquote(url)).resolve()
        if target.is_file() and target.suffix=='.svg':
            svg=target.read_text();svg=svg[svg.index('<svg'):]
            return '<figure role="img" aria-label="'+html.escape(text,quote=True)+'">'+svg+'<figcaption>'+html.escape(text)+'</figcaption></figure>'
        return super().image(text,url,title)

CSS='''
:root{--ink:#193046;--muted:#586c7b;--accent:#147a70;--line:#d8e1e8;--paper:#fff;--back:#edf2f5;--nav:270px}
*{box-sizing:border-box}body{margin:0;font-family:system-ui,-apple-system,"Segoe UI",sans-serif;color:var(--ink);background:var(--back);line-height:1.7;font-size:16px}
a{color:#106b81;text-decoration-thickness:1px;text-underline-offset:3px}a:hover{color:#084d47}
.hero{background:#142f46;color:white;padding:54px max(5vw,30px) 38px}.hero .eyebrow{letter-spacing:.17em;font-weight:650;font-size:12px;color:#9fd5cb;text-transform:uppercase}.hero h1{font-size:clamp(30px,4vw,50px);line-height:1.12;max-width:900px;margin:.4em 0}.hero p{max-width:850px;color:#d8e6ef}.hero .meta{display:flex;gap:12px;flex-wrap:wrap;margin-top:24px}.hero .meta span{border:1px solid #547080;padding:6px 12px;border-radius:20px;font-size:13px}
.layout{display:grid;grid-template-columns:var(--nav) minmax(0,1fr);max-width:1600px;margin:auto;align-items:start}nav{position:sticky;top:0;max-height:100vh;overflow:auto;padding:24px 18px;font-size:13px}nav strong{display:block;margin:14px 8px 5px;color:var(--muted);font-size:11px;letter-spacing:.09em;text-transform:uppercase}nav a{display:block;padding:7px 9px;text-decoration:none;line-height:1.4;border-radius:6px}nav a:hover{background:#dae8e8}main{min-width:0;background:var(--paper);padding:10px clamp(20px,4vw,66px) 60px}section{scroll-margin-top:20px;padding:32px 0 42px;border-bottom:1px solid var(--line)}section>h1{font-size:30px;line-height:1.25;margin:.4em 0 .8em;color:#17364b}h2{font-size:23px;line-height:1.3;margin:1.9em 0 .7em}h3{font-size:19px;line-height:1.4;margin:1.4em 0 .5em}p{margin:.8em 0 1.1em}strong{font-weight:650}code{font-family:ui-monospace,SFMono-Regular,Consolas,monospace;font-size:.87em;background:#edf3f5;padding:.13em .25em;border-radius:3px;overflow-wrap:anywhere}pre{background:#112a3d;color:#e2f1f5;padding:18px 20px;border-radius:8px;overflow:auto;line-height:1.6;font-size:14px}pre code{background:transparent;color:inherit;padding:0;overflow-wrap:normal}table{border-collapse:collapse;width:100%;font-size:14px;line-height:1.55;margin:18px 0 28px;display:table}th,td{text-align:left;vertical-align:top;padding:12px 13px;border-bottom:1px solid var(--line);overflow-wrap:anywhere}th{background:#eaf2f5;color:#254a60}tr:nth-child(even) td{background:#f8fafb}figure{margin:30px 0;padding:12px;border:1px solid var(--line);border-radius:9px;background:white;overflow:auto}figure svg{width:100%;height:auto;max-height:1100px}figcaption{font-size:13px;color:var(--muted);padding:8px 8px 0;line-height:1.5}blockquote{border-left:4px solid var(--accent);margin:20px 0;padding:8px 18px;background:#f1f8f5}details{margin:14px 0;border:1px solid var(--line);border-radius:8px;padding:12px 16px;scroll-margin-top:14px}summary{cursor:pointer;font-weight:600;font-size:14px}.footer{font-size:12px;color:var(--muted)}
@media(max-width:1000px){:root{--nav:210px}nav{font-size:12px}main{padding:8px 24px 40px}table{font-size:13px}th,td{padding:8px}}
@media(max-width:720px){.layout{display:block}nav{position:relative;max-height:320px;border-bottom:1px solid var(--line)}.hero{padding:30px 22px}main{padding:5px 18px}table{display:block;overflow:auto}section>h1{font-size:25px}h2{font-size:21px}}
@media print{nav,.hero .meta{display:none}.layout{display:block}.hero{color:#17364b;background:white;padding:25px 0}.hero p{color:#333}main{padding:0}section{break-before:page}pre{white-space:pre-wrap;color:black;background:#f1f1f1}a{color:inherit}figure{break-inside:avoid}details:not([open]){display:none}}
'''

def main():
    renderer=Renderer(escape=False)
    md=mistune.create_markdown(renderer=renderer,plugins=['table'])
    nav=[];sections=[];handbook=[]
    for i,relative in enumerate(ORDER):
        source=(P/relative).read_text()
        title=source.splitlines()[0].lstrip('# ')
        if relative=='README.md': nav.append('<strong>Overview</strong>')
        if relative.startswith('lessons/00'):nav.append('<strong>18 lesson drafts</strong>')
        if relative=='ARCHITECTURE_ATLAS.md':nav.append('<strong>Atlas and reference</strong>')
        nav.append(f'<a href="#{ident(relative)}">{html.escape(title)}</a>')
        renderer.source=relative
        sections.append('<section id="'+ident(relative)+'">'+md(source)+'</section>')
        # Rebase Markdown references when collecting chapter text at the root.
        def rewrite(match):
            label,url=match.group(1),match.group(2)
            if not urlparse(url).scheme and not url.startswith('#'):
                target=((P/relative).parent/url.split('#',1)[0]).resolve()
                try:dest=str(target.relative_to(P))
                except ValueError:dest=url
                if dest in ORDER:return f'[{label}](#{ident(dest)})'
                return f'[{label}]({dest})'
            return match.group(0)
        rebased=re.sub(r'\[([^\]]*)\]\(([^)]+)\)',rewrite,source)
        handbook.append('<a id="'+ident(relative)+'"></a>\n\n'+rebased)
    resources=[]
    for relative in RESOURCES:
        text=(P/relative).read_text()
        resources.append(f'<details id="{ident(relative)}"><summary>{html.escape(relative)}</summary><pre><code>'+html.escape(text)+'</code></pre></details>')
    sections.append('<section id="resources"><h1>Executable sources and raw evidence</h1><p>Embedded here for standalone reading. Use the ZIP to run files with their original paths.</p>'+''.join(resources)+'</section>')
    nav.append('<strong>Offline appendix</strong><a href="#resources">Code and raw execution evidence</a>')
    body='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>vLLM Academy | Phase 1 redesigned</title><style>'''+CSS+'''</style></head><body>
<header class="hero"><div class="eyebrow">vLLM Academy / learning design / 02 October 2026</div><h1>From model mechanics<br>to the whole request.</h1><p>A practical route through LLM history, naive Transformers, native model demos, serving abstractions, APIs, multimodality and contribution.</p><div class="meta"><span>18 lesson drafts</span><span>44 CPU tests passed</span><span>4 original figures</span><span>31 primary/original sources</span></div></header>
<div class="layout"><nav aria-label="Table of contents">'''+''.join(nav)+'''</nav><main>'''+''.join(sections)+'''<p class="footer">Original curriculum supplement. Source reading, local CPU execution and unexecuted integration gates are distinguished throughout. No external scripts, fonts or image requests are needed to read this file.</p></main></div></body></html>'''
    (P/'START_HERE.html').write_text(body)
    (P/'HANDBOOK.md').write_text('# vLLM Academy — Phase 1 handbook\n\nOffline reading copy. Source files and runnable labs are provided separately in the package.\n\n'+'\n\n---\n\n'.join(handbook))
    # Validate local Markdown links excluding generated handbook anchors.
    errors=[]
    for f in P.rglob('*.md'):
        if f.name=='HANDBOOK.md':continue
        for _,url in re.findall(r'\[([^\]]*)\]\(([^)]+)\)',f.read_text()):
            if urlparse(url).scheme or url.startswith('#'):continue
            target=(f.parent/unquote(url.split('#',1)[0])).resolve()
            if not target.exists():errors.append(f'{f.relative_to(P)} -> {url}')
    anchors=set(re.findall(r'id="([^"]+)"',body))
    missing=sorted(set(re.findall(r'href="#([^"]+)"',body))-anchors)
    if missing:errors+=['Missing HTML anchor: '+x for x in missing]
    stats={'markdown_link_errors':errors,'html_internal_missing_anchors':missing,
           'lesson_files':len(list((P/'lessons').glob('*.md'))),'references':len(json.loads((P/'references.json').read_text())),
           'svg_figures':len(list((P/'figures').glob('*.svg'))),'html_bytes':len(body.encode()),'source_sections':len(ORDER)}
    (P/'results/document-checks.json').write_text(json.dumps(stats,indent=2))
    if errors:raise SystemExit('\n'.join(errors))
    print(json.dumps(stats,indent=2))

if __name__=='__main__':main()
