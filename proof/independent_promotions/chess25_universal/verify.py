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

# For the final universal mate, underestimate attack from unknown attackers and
# overestimate the possible moves of unknown defenders (queen OR knight).
def universal_mate(st):
    b,c=st.b.copy(),st.c
    for a,p in enumerate(b):
        if p==-7*c:b[a]=-8*c
    assert attacked(b,king(b,c),-c), 'no check from a fixed piece'
    for a,pc in enumerate(b):
        if pc*c<=0: continue
        for typ in ((2,5) if pc==7*c else (pc*c,)):
            q=b.copy();q[a]=typ*c
            for z in range(64):
                m=chr(97+a%8)+str(a//8+1)+chr(97+z%8)+str(z//8+1)
                for pr in ('n','b','r','q') if typ==1 and z//8 in (0,7) else ('',):
                    assert moved(q,c,m+pr) is None, ('potential escape in relaxed mate test',m+pr)
    return True

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--choices',default=None,help='15 chars from nbrq; emit one ordinary UCI game');args=ap.parse_args()
    if args.choices is not None: assert len(args.choices)==15 and set(args.choices)<=set('nbrq')
    lines=(ROOT/'template.txt').read_text().splitlines();st=State();expanded=lines[0].split();
    for m in expanded: st.play(m)
    assert sum(p!=0 for p in st.b)==25
    assert Counter(st.b)==Counter({0:39,1:8,-1:7,2:2,3:2,4:2,5:1,-5:1,6:1,-6:1})
    # Every promoted wildcard remains stationary except during the immediately
    # following PARK macro, where the type is revealed locally and rehidden.
    nw=nb=0;prefix_counts={(0,0)};i=1;parks=0;proms=[]
    while i<len(lines):
        tok=lines[i].split();tag=tok[0]
        if tag=='END':break
        if tag=='MOVE':
            a,z,pr=parse(tok[1]);assert not pr and abs(st.b[a])!=7 and not st.b[z]
            st.play(tok[1]);expanded.append(tok[1]);i+=1;continue
        assert tag=='PROM',tok
        m=tok[1];a,z,pr=parse(m);c=st.c;assert st.b[a]==c and not st.b[z]
        old=st.copy();branches=[];has_park=i+1<len(lines) and lines[i+1].startswith('PARK ')
        park=lines[i+1].split()[1:] if has_park else []
        if has_park:
            assert len(park)==10
            parks+=1
        for t in TYPES:
            s=old.copy();s.play(m+PC[t]);end=z
            if has_park:
                w,rev=park[:2];p1,p2=park[2+2*(t-2):4+2*(t-2)]
                assert parse(p1)[0]==z and parse(p2)[0]==parse(p1)[1]
                assert parse(w)[:2]==tuple(reversed(parse(rev)[:2]))
                for u in (w,p1,rev,p2):
                    aa,zz,pp=parse(u);assert not s.b[zz] and not pp and abs(s.b[aa])!=7
                    s.play(u)
                end=parse(p2)[1]
            assert s.b[end]==c*t
            s.b[end]=7*c;branches.append(s)
        # The branch endpoints must agree exactly after replacing the active
        # promoted piece with a wildcard; prior wildcards never moved.
        st=branches[0]
        for s in branches[1:]:
            assert (s.b,s.c,s.half,s.plies)==(st.b,st.c,st.half,st.plies)
        # Conservative maxima across alternative histories, never summing them.
        for s in branches[1:]: st.reps |= s.reps
        assert max(st.reps.values())<5
        chosen=args.choices[nw+nb] if args.choices else 'q';expanded.append(m+chosen)
        if has_park:
            j=PC.index(chosen)-2;expanded.extend([park[0],park[2+2*j],park[1],park[3+2*j]])
        if c==1:nw+=1
        else:nb+=1
        prefix_counts.add((nw,nb));proms.append((st.plies,nw,nb));i+=2 if has_park else 1
    assert (nw,nb)==(8,7) and st.b.count(7)==8 and st.b.count(-7)==7
    assert sum(p!=0 for p in st.b)==25
    milestone=st.plies
    for l in (ROOT/'mate_suffix.txt').read_text().splitlines():
        tag,m=l.split();assert tag=='MOVE';assert abs(st.b[parse(m)[0]])!=7
        st.play(m);expanded.append(m)
    assert universal_mate(st)
    # Distinct choices of type multisets; different p counts imply different pawn counts.
    covered=sum(comb(w+3,3)*comb(b+3,3) for w,b in prefix_counts)
    if args.choices:
        print(' '.join(expanded));return
    print('PASS: all 4^15 promotion assignments are legal and have a common continuation to checkmate.')
    print('Final 25-piece material profiles:',comb(11,3)*comb(10,3))
    print('25-piece profiles including all promotion prefixes:',covered)
    print('Promotion order (white, black):',sorted(prefix_counts,key=sum))
    print('PARK macros:',parks,'milestone ply:',milestone,'mate ply:',st.plies)
    print('Maximum conservative repetition count:',max(st.reps.values()))
if __name__=='__main__':main()
