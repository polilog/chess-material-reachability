"""Coefficient calculations only, no enumeration of two-sided material profiles."""
from collections import Counter
from itertools import combinations
from math import prod

def mul(a,b,limit=None):
    out=Counter()
    for i,x in a.items():
        for j,y in b.items():
            if limit is None or i+j<=limit:out[i+j]+=x*y
    return out

# F: nonpawn loss types N,B,R,Q. Capturing at most 7 original nonpawns per color.
F=Counter({0:1})
for m in (2,2,2,1):F=mul(F,Counter({i:1 for i in range(m+1)}))
G=mul(F,F)
classes=(G[8]+F[4])//2
assert classes==248
print('8 nonpawn loss classes:',classes,'oriented',G[8],'fixed under swap',F[4])
print('Special 25-piece master: 1 pawn + 6 nonpawns of the smaller side')
print('Total sufficient classes for N<=24: 249 (conditional on master construction)')
# Seven captures, one pawn lost. Use either side for the pawn loss, color symmetry.
assert G[6]==483
assert G[7]//2==267
print('N=25: 483 one-pawn-loss classes, 267 no-pawn-loss classes')

# A side family (fixed optional P,N,B,R,Q; total wildcards; 5-way wildcards).
# One king + one mandatory helper knight per side are implicit.
# t is an optional vector. Condition: sum positive excess <= m, pawn excess <= o.
FAMS=[((0,0,1,2,1),8,0),((0,1,2,1,0),6,0),((2,0,2,2,1),5,2),((0,1,2,0,0),6,0)]

def inter(ids, pawnless=False):
    fs=[FAMS[i] for i in sorted(set(ids))];dp={tuple([0]*len(fs))+ (0,):1}
    for t in range(5):
        nd=Counter()
        for key,v in dp.items():
            costs, size=key[:-1],key[-1]
            limit=min(f[0][t]+f[1]-k for f,k in zip(fs,costs))
            for c in range((0 if pawnless and t==0 else limit)+1):
                excess=[max(0,c-f[0][t]) for f in fs]
                if t==0 and any(d>f[2] for d,f in zip(excess,fs)):continue
                new=tuple(k+d for k,d in zip(costs,excess))
                if all(k<=f[1] for k,f in zip(new,fs)):nd[new+(size+c,)]+=v
        dp=nd
    out=Counter()
    for key,v in dp.items():out[key[-1]+2]+=v
    return out

def union(rects, pawnless=False):
    # Union of rectangles in ordered-color space, divided by the swap involution.
    oriented=Counter();diagonal=Counter()
    for k in range(1,len(rects)+1):
        for r in combinations(rects,k):
            left,right=zip(*r);a=inter(left,pawnless);b=inter(right,pawnless);d=inter(left+right,pawnless)
            sign=(-1)**(k+1)
            for n,v in mul(a,b).items():oriented[n]+=sign*v
            for n,v in d.items():diagonal[2*n]+=sign*v
    out=Counter()
    for n,v in oriented.items():
        assert (v+diagonal[n])%2==0 and v>=0
        out[n]=(v+diagonal[n])//2
    return out
old=union([(0,1),(1,0)]);new=union([(2,3),(3,2)]);combined=union([(0,1),(1,0),(2,3),(3,2)])
assert sum(old.values())==733950 and sum(new.values())==1143269
pawnless=union([(0,1),(1,0),(2,3),(3,2)],True)
print('Old family:',sum(old.values()),'new family:',sum(new.values()))
print('Union:',sum(combined.values()),'intersection:',sum(old.values())+sum(new.values())-sum(combined.values()))
print('Union with >=1 pawn:',sum(combined.values())-sum(pawnless.values()))
print('N\told\tnew\tunion')
for n in range(4,27):print(n,old[n],new[n],combined[n],sep='\t')
