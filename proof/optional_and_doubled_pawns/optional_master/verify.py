#!/usr/bin/env python3
"""Certificate: fourteen independent promotions AND independent deletions.
No enumeration of promotion assignments, deletion subsets, or material profiles."""
from inspect_master import *
from collections import defaultdict
import json

def knight(a,z):return abs(a%8-z%8)*abs(a//8-z//8)==2
def route(b,c,home,other,wait,target):
    ek=king(b,-c);q=deque([home]);prev={home:None}
    while q and target not in prev:
        a=q.popleft()
        for z in range(64):
            if not knight(a,z) or z in prev or z==wait or knight(z,ek) or (b[z] and z!=target):continue
            prev[z]=a;q.append(z)
    assert target in prev
    path=[target]
    while prev[path[-1]] is not None:path.append(prev[path[-1]])
    path.reverse();tour=path+path[-2::-1];seq=[]
    for i,(a,z) in enumerate(zip(tour,tour[1:])):
        m=name(a)+name(z);w=name(wait if i%2 else other)+name(other if i%2 else wait)
        seq.extend([m,w] if st.c==c else [w,m])
    return seq

def robust(b,z,c,optional):
    core=[p if i not in optional else 0 for i,p in enumerate(b)]
    if attacked(core,z,c):return True
    for i in optional:
        if b[i]*c>0:
            core[i]=b[i]
            if attacked(core,z,c):return True
            core[i]=0
    return False

def count_side(a,b,m,n,op_a,op_b):
    # P,N,B,R,Q; five-way wildcards can supply any type, four-way only nonpawns.
    # For each type count t, its excess over fixed surviving pieces requires a wildcard.
    dp={(0,0,0):1}
    for j,(ai,bi) in enumerate(zip(a,b)):
        nd=defaultdict(int)
        for (i,k,l),v in dp.items():
            for t in range(min(ai+m-i,bi+n-k)+1):
                da,db=max(0,t-ai),max(0,t-bi)
                if j==0 and (da>op_a or db>op_b):continue
                nd[i+da,k+db,l+t]+=v
        dp=nd
    out=Counter()
    for (i,k,l),v in dp.items():out[l+2]+=v
    return out

def mul(a,b):
    c=Counter()
    for i,v in a.items():
        for j,w in b.items():c[i+j]+=v*w
    return c

st,h,options=replay_prefix();b=st.b;c=st.c;hw,ww,hb,wb=h;ks={s:king(b,s) for s in (1,-1)};homes={1:hw,-1:hb};waits={1:ww,-1:wb};core={ks[1],ks[-1],hw,hb};optional={i for i,p in enumerate(b) if p and i not in core}
assert (st.plies,st.half,c)==(381,107,-1)
assert b[hw]==2 and b[hb]==-2 and len(optional)==21 and b.count(7)==5 and b.count(-7)==6 and len(options)==2
assert len(set(h))==4 and not b[ww] and not b[wb]
# Every nonking piece is incapable of checking the opposing king on an empty
# board, even in the union Q+N model. Kings are non-adjacent by the prefix.
for i,p in enumerate(b):
    if p and abs(p)!=6:
        side=sgn(p);assert not attacked([p if j==i else 0 for j in range(64)],ks[-side],side)
print('PASS: prefix 381 plies, 9 four-way and 2 five-way choices; no raw attacks')
cert=[];maxphase=0;maxlength=0;maxfirst=0
for z in sorted(optional):
    side=-sgn(b[z]);seq=route(b,side,homes[side],homes[-side],waits[-side],z)
    cb=b.copy();turn=c;opt=optional-{z};caps=0;phase=Counter();first=Counter(st.reps)
    phase[sig(cb,turn)]+=1;pre=True
    for m in seq:
        a,v,pr=parse(m);assert a not in opt and v not in opt and not pr
        captured=bool(cb[v]);nb=moved(cb,turn,m);assert nb is not None
        assert not robust(nb,king(nb,turn),-turn,opt)
        assert all(nb[i]==b[i] for i in opt)
        if captured:
            assert v==z and cb[v]*turn<0;caps+=1;maxphase=max(maxphase,max(phase.values()));phase=Counter();pre=False
        cb=nb;turn=-turn;phase[sig(cb,turn)]+=1
        if pre:
            first[sig(cb,turn)]+=1
            maxfirst=max(maxfirst,max(first.values()))
    expected=b.copy();expected[z]=0
    assert cb==expected and turn==c and caps==1
    maxphase=max(maxphase,max(phase.values()));maxlength=max(maxlength,len(seq));cert.append([name(z),seq])
assert maxfirst<=4 and maxphase<=2
# Subsequent phases: deleting a piece strictly decreases material count, so
# only tail of previous and head of next operation can share a position.
# For smaller subsets, equality of color-occupancy projections along a module
# is unaffected by removing stationary pieces (the routes avoid them).
assert st.half+maxlength<150 and 2*maxlength<150
print('PASS: 21 independent deletion routes; longest',maxlength,'plies; max within-phase repeats',maxphase,'; initial overlap',maxfirst)
# Common mating continuation after all optional pieces are deleted.
cb=[p if i in core else 0 for i,p in enumerate(b)];s=State(cb,c);mate=Path(__file__).with_name('mate.txt').read_text().split()
for m in mate:s.play(m)
assert attacked(s.b,king(s.b,s.c),-s.c)
for a,p in enumerate(s.b):
    if p*s.c<=0:continue
    for z in range(64):assert moved(s.b,s.c,name(a)+name(z)) is None
assert max(s.reps.values())<=2 and maxlength+len(mate)<150
# Only the previous final deletion phase shares the core material count.
print('PASS: common',len(mate),'ply two-knight mating suffix; no premature dead position or automatic draw')
# Count every material profile by polynomial convolution, not by profile enumeration.
a=[b.count(t)-(t==2) for t in (1,2,3,4,5)]
d=[b.count(-t)-(t==2) for t in (1,2,3,4,5)]
m,n=b.count(7),b.count(-7);oa=sum(b[i]==7 for i in options);ob=sum(b[i]==-7 for i in options)
print('Fixed optional material P,N,B,R,Q',a,d,'wildcards',m,n,'5-way',oa,ob)
W=count_side(a,a,m,m,oa,oa);B=count_side(d,d,n,n,ob,ob);I=count_side(a,d,m,n,oa,ob)
P=mul(W,B);II=mul(I,I)
for z in range(4,26):
    diag=I[z//2] if z%2==0 else 0
    assert (II[z]-diag)%2==0
    P[z]-=(II[z]-diag)//2
assert all(v>=0 for v in P.values())
print('White families',sum(W.values()),'black families',sum(B.values()),'intersection',sum(I.values()))
print('Distinct unordered profiles',sum(P.values()))
print('N\tPROFILES')
for z in range(4,26):print(z,P[z],sep='\t')
Path(__file__).with_name('deletions.json').write_text(json.dumps(cert,separators=(',',':'))+'\n')
Path(__file__).with_name('counts.tsv').write_text('N\tprofiles\n'+''.join(f'{z}\t{P[z]}\n' for z in range(4,26)))
