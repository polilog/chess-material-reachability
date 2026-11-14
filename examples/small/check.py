#!/usr/bin/env python3
from itertools import product
from pathlib import Path
import os, subprocess, tempfile
root=Path(__file__).resolve().parent
mate=(root/'mate_games.uci').read_text().splitlines()
dead=(root/'dead_games.uci').read_text().splitlines()
# Every dead-position witness follows a verified mate-game prefix until the final move.
for g in dead:
    prefix=' '.join(g.split()[:-1])+' '
    assert any(x.startswith(prefix) for x in mate), 'missing certified nondead prefix'
sides=[[] for _ in range(6)]
for s in product(range(6),repeat=5):
    if sum(s)<=5:sides[sum(s)].append(s)
def pack(s):return sum(v<<(4*i) for i,v in enumerate(s))
expected=set()
for n in range(2,8):
    for a in range(n-1):
        for s in sides[a]:
            for t in sides[n-2-a]:
                x,y=sorted((pack(s),pack(t)));expected.add(x|(y<<20))
with tempfile.TemporaryDirectory() as d:
    exe=Path(d)/'verify';subprocess.run([os.environ.get('CXX','g++'),'-O3','-std=c++17',str(root/'verify.cpp'),'-o',str(exe)],check=True)
    lines=subprocess.check_output([str(exe),str(root/'mate_games.uci'),str(root/'dead_games.uci')],text=True).splitlines()
seen=set(map(int,lines[1:]));print(lines[0]);assert seen==expected,(len(expected-seen),len(seen-expected))
for n in range(2,8): print(n,sum(2+sum((k>>(4*j))&15 for j in range(10))==n for k in seen))
print('PASS:',len(seen),'distinct material sets, exact coverage.')
