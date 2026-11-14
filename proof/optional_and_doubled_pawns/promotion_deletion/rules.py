#!/usr/bin/env python3
"""Independent 64-square symbolic verifier. No external packages required.
Piece 7 is an unknown one of N/B/R/Q. It attacks as Q+N, but stays frozen.
Piece 8 is an inert blocker, used ONLY for the final universal-mate test.
The legality checks overapproximate enemy attacks, so acceptance proves legality
for every assignment of the independent wildcard choices.
"""
from collections import Counter
from pathlib import Path
from math import comb
from itertools import product
import argparse
ROOT = Path(__file__).resolve().parent
TYPES = (2, 3, 4, 5)  # N B R Q
PC = '  nbrq'

def sq(s):
    assert len(s)==2 and 'a'<=s[0]<='h' and '1'<=s[1]<='8', s
    return ord(s[0])-97+8*(int(s[1])-1)

def sgn(x): return (x>0)-(x<0)
def attacked(b, target, color):
    x,y=target%8,target//8
    for a,pc in enumerate(b):
        p=pc*color
        if p<=0 or p==8: continue
        u,v=a%8,a//8; dx,dy=x-u,y-v; X,Y=abs(dx),abs(dy)
        if p==1:
            if X==1 and dy==color: return True
        elif p==6:
            if max(X,Y)==1: return True
        else:
            if p in (2,7) and X*Y==2: return True
            if p==2: continue
            diag=X==Y; line=dx==0 or dy==0
            if (dx or dy) and ((p==3 and diag) or (p==4 and line) or (p in (5,7) and (diag or line))):
                d=sgn(dx)+8*sgn(dy); i=a+d
                while i!=target and not b[i]: i+=d
                if i==target: return True
    return False

def king(b,c):
    assert b.count(6*c)==1
    return b.index(6*c)

def parse(m):
    assert len(m) in (4,5), m
    a,z=sq(m[:2]),sq(m[2:4]); pr=PC.index(m[4]) if len(m)==5 else 0
    return a,z,pr

def moved(b,c,m):
    """Return new board or None. No castling or en passant in this certificate."""
    a,z,pr=parse(m); p=b[a]*c; v=b[z]*c
    if a==z or p<=0 or p>=7 or v>0 or v==-6: return None
    dx,dy=z%8-a%8,z//8-a//8; X,Y=abs(dx),abs(dy)
    if p==1:
        if not dx:
            if v or not (dy==c or (dy==2*c and a//8==(1 if c==1 else 6) and not b[a+8*c])): return None
        elif X!=1 or dy!=c or v>=0: return None
        if (z//8 in (0,7)) != bool(pr) or (pr and pr not in TYPES): return None
    else:
        if pr: return None
        if p==2:
            if X*Y!=2: return None
        elif p==6:
            if max(X,Y)!=1: return None
        else:
            diag=X==Y; line=dx==0 or dy==0
            if not ((p==3 and diag) or (p==4 and line) or (p==5 and (diag or line))): return None
            d=sgn(dx)+8*sgn(dy); i=a+d
            while i!=z:
                if b[i]: return None
                i+=d
    q=b.copy();q[a]=0;q[z]=c*(pr or p)
    if attacked(q,king(q,c),-c): return None
    return q

def initial():
    back=[4,2,3,5,6,3,2,4]
    return back+[1]*8+[0]*32+[-1]*8+[-p for p in back]

def sig(b,c):
    # Color-only occupancy: equal actual positions always have equal projections.
    # This deliberately ignores type, castling and en passant; it overcounts repeats.
    return (bytes(sgn(p)+1 for p in b),c)

class State:
    def __init__(self,b=None,c=1,half=0,reps=None,plies=0):
        self.b=initial() if b is None else b; self.c=c; self.half=half; self.plies=plies
        self.reps=Counter({sig(self.b,self.c):1}) if reps is None else reps
    def copy(self): return State(self.b.copy(),self.c,self.half,self.reps.copy(),self.plies)
    def play(self,m):
        a,z,pr=parse(m); b,c=self.b,self.c
        q=moved(b,c,m)
        assert q is not None, (self.plies+1,m,'illegal in symbolic attack model')
        self.half=0 if abs(b[a])==1 or b[z] else self.half+1
        assert self.half<150, ('75-move limit',self.plies,m)
        self.b=q;self.c=-c;self.plies+=1
        k=sig(q,self.c);self.reps[k]+=1
        assert self.reps[k]<5, ('fivefold color-only projection',self.plies,m,self.reps[k])

