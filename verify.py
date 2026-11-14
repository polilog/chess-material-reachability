#!/usr/bin/env python3
"""Cold replay: no baseline matrices, saved families, or cached coverage trusted."""
import argparse, hashlib, json, os, subprocess as sp, sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).resolve().parent
SRC=ROOT/'src'


def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()
def run(args, **kw):return sp.run([str(x) for x in args],check=True,**kw)
def main():
    if not __debug__:raise SystemExit('Do not use python -O: the checkers require assertions.')
    p=argparse.ArgumentParser();p.add_argument('--work',type=Path,default=ROOT/'replay');a=p.parse_args();w=a.work.resolve()
    if w.exists():raise SystemExit('Choose a new --work directory; refusing to reuse old outputs.')
    w.mkdir(parents=True)
    data=ROOT/'data'; expected=json.loads((data/'manifest.json').read_text())
    assert len(expected)==9
    for name,info in expected.items():
        assert (data/name).stat().st_size==info['bytes'],f'Certificate length mismatch: {name}'
        assert sha(data/name)==info['sha256'],f'Certificate checksum mismatch: {name}'
        raw=w/name.removesuffix('.zst')
        with raw.open('wb') as out:run(['zstd','-dc',data/name],stdout=out)
        assert raw.stat().st_size==info['raw_bytes'] and sha(raw)==info['raw_sha256'],f'Decompressed certificate mismatch: {name}'
    print('PASS: compact certificate checksums and decompression',flush=True)
    cxx=os.environ.get('CXX','g++');exe=w/'symbolic_all';agg=w/'aggregate';small=w/'small'
    for src,out in [(SRC/'symbolic_all.cpp',exe),(SRC/'aggregate.cpp',agg),(ROOT/'examples/small/verify.cpp',small)]:run([cxx,'-O3','-std=c++17',src,'-o',out])
    games=sorted(w.glob('games_*.uci'));templates=sorted(w.glob('templates_*.txt'));storage=sorted(w.glob('storage_*.txt'))
    assert len(games)==4 and len(templates)==4 and len(storage)==1
    def game(p):
        out=p.with_suffix('.families')
        r=run([exe,p,out],capture_output=True,text=True);p.with_suffix('.replay.log').write_text(r.stderr)
        print(p.name,r.stderr.splitlines()[-1],flush=True)
    with ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(game,games))
    # Each validator writes freshly derived families and rejects invalid blocks.
    run([sys.executable,SRC/'verify_branch.py',*templates]);run([sys.executable,SRC/'verify_storage.py',*storage])
    # Explicit terminal targets: verify the alternative mate-game prefix.
    sd=ROOT/'examples/small';mates=(sd/'mate_games.uci').read_text().splitlines()
    for line in (sd/'dead_games.uci').read_text().splitlines():
        prefix=line.split()[:-1];assert any(g.split()[:len(prefix)]==prefix for g in mates)
    r=run([small,sd/'mate_games.uci',sd/'dead_games.uci'],capture_output=True,text=True)
    lines=r.stdout.splitlines();assert lines[0]=='valid 1113 invalid 0';keys=w/'small.keys';keys.write_text('\n'.join(lines[1:])+'\n')
    fresh=[f.with_suffix('.families') for f in games+templates]
    assert len(fresh)==len(set(fresh)), 'Colliding certificate output paths'
    env=os.environ.copy();env.pop('BASE_STATE',None);env['OUT_STATE']=str(w/'fresh.state')
    with (w/'ordinary_summary.tsv').open('w') as out:run([agg,keys,*fresh],cwd=w,env=env,stdout=out)
    run([sys.executable,SRC/'finish_union.py',w/'fresh.state',w/'summary.tsv',*[f.with_suffix('.storage.json') for f in storage]])
    assert (w/'summary.tsv').read_bytes()==(ROOT/'results/expected.tsv').read_bytes()
    (w/'VERIFIED.json').write_text(json.dumps({'format':1,'manifest_sha256':sha(data/'manifest.json'),'summary_sha256':sha(w/'summary.tsv')},indent=2)+'\n')
    print('PASS: all 29,045,304 candidates reconstructed from compact certificates, no historical archives or cached coverage.',flush=True)
if __name__=='__main__':main()
