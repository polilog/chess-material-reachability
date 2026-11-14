#!/usr/bin/env python3
"""Reproduce descriptive coverage statistics from a completed cold replay."""
import argparse, csv, hashlib, json, os, subprocess, tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
LABELS=('concrete', 'promotion_variants', 'templates', 'storage')

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1<<20),b''): h.update(chunk)
    return h.hexdigest()

def read_summary(path):
    with path.open() as f:
        return {r['N']: (int(r['upper']),int(r['covered'])) for r in csv.DictReader(f,delimiter='\t')}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--replay',type=Path,default=ROOT/'replay')
    p.add_argument('--output',type=Path,default=ROOT/'results'/'coverage_breakdown.tsv')
    a=p.parse_args(); w=a.replay.resolve()
    marker=json.loads((w/'VERIFIED.json').read_text())
    manifest=ROOT/'data'/'manifest.json'
    if marker['manifest_sha256']!=sha(manifest) or marker['summary_sha256']!=sha(w/'summary.tsv'):
        raise SystemExit('Replay marker does not match manifest/summary; run verify.py first.')
    for name, info in json.loads(manifest.read_text()).items():
        if sha(w/name.removesuffix('.zst'))!=info['raw_sha256']:
            raise SystemExit(f'Raw replay input changed: {name}')
    games=sorted(w.glob('games_*.uci')); templates=sorted(w.glob('templates_*.families'))
    if len(games)!=4 or len(templates)!=4: raise SystemExit('Missing replay inputs')
    # Derived families must be from the completed verified replay. This is
    # descriptive analysis, not an independent proof of their authenticity.
    cxx=os.environ.get('CXX','g++')
    env=os.environ.copy(); env.pop('OUT_STATE',None); env.pop('BASE_STATE',None)
    with tempfile.TemporaryDirectory(prefix='coverage-stats-') as tmp:
        t=Path(tmp); direct=t/'direct'; agg=t/'aggregate'; keys=t/'concrete.keys'
        for source, exe in [('direct_material.cpp',direct),('aggregate.cpp',agg)]:
            subprocess.run([cxx,'-O3','-std=c++17',str(ROOT/'src'/source),str('-o'),str(exe)],check=True)
        small=ROOT/'examples'/'small'
        subprocess.run([str(direct),str(keys),*map(str,games),str(small/'mate_games.uci'),str(small/'dead_games.uci')],check=True)
        gf=[x.with_suffix('.families') for x in games]
        stages=[[keys],[keys,*gf],[keys,*gf,*templates]]
        summaries=[]
        for i, files in enumerate(stages):
            out=t/f'stage{i}.tsv'
            with out.open('w') as f:
                subprocess.run([str(agg),*map(str,files)],check=True,stdout=f,env=env)
            summaries.append(read_summary(out))
        summaries.append(read_summary(w/'summary.tsv'))
        expected=read_summary(ROOT/'results'/'expected.tsv')
        rows=[]
        for n in [str(i) for i in range(2,33)]+['Total']:
            counts=[s[n][1] for s in summaries]; upper=expected[n][0]
            if any(s[n][0]!=upper for s in summaries) or counts!=sorted(counts) or counts[-1]!=upper:
                raise SystemExit(f'Inconsistent cumulative coverage: {n}')
            rows.append([n,upper,*[x-y for x,y in zip(counts,[0,*counts[:-1]])]])
        if [sum(r[j] for r in rows[:-1]) for j in range(1,6)]!=rows[-1][1:]: raise SystemExit('Totals disagree')
        a.output.parent.mkdir(parents=True,exist_ok=True)
        with a.output.open('w') as f:
            writer=csv.writer(f,delimiter='\t',lineterminator='\n');writer.writerow(['pieces','total',*LABELS]);writer.writerows(rows)
        print(a.output,rows[-1])
if __name__=='__main__': main()
