"""Read a bounded source excerpt from an exact locally available vLLM checkout."""
import argparse
import json
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser();p.add_argument('--checkout',type=Path,required=True)
    p.add_argument('--entry',default='api');p.add_argument('--lines',type=int,default=36)
    a=p.parse_args()
    if not 1<=a.lines<=80: p.error('--lines must be in 1..80')
    data=json.loads((ROOT/'source-map.json').read_text())
    found=subprocess.run(['git','-C',str(a.checkout),'rev-parse','HEAD'],check=True,
                         text=True,capture_output=True).stdout.strip()
    if found!=data['commit']:p.error('Checkout does not match source-map commit')
    rows=[r for r in data['entries'] if r['id']==a.entry]
    if not rows:p.error('Unknown entry; choose '+', '.join(r['id'] for r in data['entries']))
    r=rows[0]; lines=(a.checkout/r['path']).read_text().splitlines()
    start=max(0,(r.get('read_start') or 1)-1)
    if r.get('symbol'):
        pat=re.compile(r'^(?:async\s+)?(?:class|def)\s+'+re.escape(r['symbol'])+r'\b')
        matches=[i for i,line in enumerate(lines) if pat.search(line.lstrip())]
        if not matches:p.error('Symbol missing from pinned file')
        start=matches[0]
    print(r['path']+' @ '+found+'\nQuestion: '+r['question'])
    for i in range(start,min(start+a.lines,len(lines))): print(f'{i+1:5}: {lines[i]}')
if __name__=='__main__':main()
