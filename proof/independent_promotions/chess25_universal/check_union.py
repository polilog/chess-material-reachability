#!/usr/bin/env python3
"""Reverify the old 28-piece archive and union its 25-piece profiles with the symbolic certificate."""
from pathlib import Path
from itertools import product
from collections import defaultdict
import subprocess, tempfile, sys, os, zipfile
ROOT=Path(__file__).resolve().parent
assert len(sys.argv)==2, 'Usage: python check_union.py /path/to/chess_material_28_proof.zip'
subprocess.run([sys.executable,str(ROOT/'verify.py')],check=True)
with tempfile.TemporaryDirectory() as d:
    exe=Path(d)/'scan';subprocess.run([os.environ.get('CXX','g++'),'-O3','-std=c++17',str(ROOT/'verify_archive.cpp'),'-o',str(exe)],check=True)
    with zipfile.ZipFile(sys.argv[1]) as z, z.open('chess28_games.uci') as f:
        p=subprocess.Popen([str(exe)],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
        # avoid PIPE deadlock: stream input from a thread, consume stdout concurrently
        from threading import Thread
        def feed():
            import shutil
            with p.stdin:shutil.copyfileobj(f,p.stdin,1024*1024)
        t=Thread(target=feed);t.start();lines=p.stdout.read().decode().splitlines();t.join();assert p.wait()==0
seen=set(map(int,lines[1:]));print(lines[0], '25-piece sets',len(seen))
pairs=[(0,0),(0,1),(1,1),(2,1),(2,2),(2,3),(3,3),(3,4),(4,4),(4,5),(5,5),(6,5),(7,5),(8,5),(8,6),(8,7)]
def comps(n):return [x for x in product(range(n+1),repeat=4) if sum(x)==n]
def pack(s):return sum(x<<(4*i) for i,x in enumerate(s))
family=set()
for w,b in pairs:
    for x in comps(w):
        a=pack((8-w,x[0]+2,x[1]+2,x[2]+2,x[3]+1))
        for y in comps(b):
            z=pack((7-b,y[0],y[1],y[2],y[3]+1));i,j=sorted((a,z));family.add(i|(j<<20))
print('Symbolic family:',len(family),'overlap:',len(family&seen),'union:',len(family|seen))
assert len(seen)==369432 and len(family)==62106 and len(family|seen)==430883
