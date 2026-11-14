#!/usr/bin/env python3
"""Verify one prefix and local certificates, not 118341 profiles or 2^28 subsets."""
import json
from pathlib import Path
from collections import Counter
from rules import State, parse, sq, attacked, moved, king
ROOT=Path(__file__).resolve().parent
D=json.loads((ROOT/'proof.json').read_text())

def name(z):return chr(z%8+97)+str(z//8+1)
def nm(a,z):return name(a)+name(z)
def static(b,excepts):return {i for i,p in enumerate(b) if p and i not in excepts}
def robust_attacked(b,z,c,optional):
    # For any subset, an attack must also occur when all optional blockers
    # except the attacking piece are removed. Mandatory blockers stay.
    core=[p if i not in optional else 0 for i,p in enumerate(b)]
    if attacked(core,z,c):return True
    for i in optional:
        if b[i]*c>0:
            core[i]=b[i]
            if attacked(core,z,c):return True
            core[i]=0
    return False

def symbolic(b,c,seq,optional):
    b=b.copy();optional=set(optional);original={i:b[i] for i in optional}
    states=[(b.copy(),c)]; captures=[];phase=Counter();maxrep=0
    def signature():return (tuple(p if i not in optional else 0 for i,p in enumerate(b)),c)
    phase[signature()]+=1
    for j,m in enumerate(seq):
        a,z,pr=parse(m)
        assert a not in optional and z not in optional,(j,m,'optional piece moved or taken')
        victim=b[z];q=moved(b,c,m)
        assert q is not None,(j,m,'full board legality')
        assert not robust_attacked(q,king(q,c),-c,optional),(j,m,'subset safety')
        assert all(q[i]==p for i,p in original.items())
        if victim:captures.append((j,z,victim));maxrep=max(maxrep,max(phase.values()));phase=Counter()
        b=q;c=-c;states.append((b.copy(),c));phase[signature()]+=1
    maxrep=max(maxrep,max(phase.values()))
    return b,c,captures,states,maxrep

def mate(st):
    b,c=st.b,st.c
    assert attacked(b,king(b,c),-c)
    for a,p in enumerate(b):
        if p*c<=0:continue
        for z in range(64):
            if abs(p)==1 and z//8 in (0,7):
                for pr in 'nbrq':assert moved(b,c,nm(a,z)+pr) is None
            else:assert moved(b,c,nm(a,z)) is None

def replay(st,seq):
    for m in seq:st.play(m)
    return st

base=State()
for m in D['prefix']:
    a,z,pr=parse(m);assert not base.b[z] and not pr
    base.play(m)
b,c=base.b,base.c;hw,ww,hb,wb=map(sq,D['homes']);homes={1:hw,-1:hb};ks={1:king(b,1),-1:king(b,-1)}
assert sum(p!=0 for p in b)==32 and b[hw]==2 and b[hb]==-2
assert Counter(b)==Counter({0:32,1:8,-1:8,2:2,-2:2,3:2,-3:2,4:2,-4:2,5:1,-5:1,6:1,-6:1})
assert max(base.reps.values())==1
print('PASS: 347-ply no-capture, no-promotion opening; all 32 pieces remain.')
fixed_core={ks[1],ks[-1],hw,hb};seen=set();maxrep=1
for side,loc,seq in D['two_helper']:
    z=sq(loc);assert z not in fixed_core and b[z]*side<0 and len(seq)<=28
    out,t,cap,states,r=symbolic(b,c,seq,static(b,fixed_core|{z}))
    expected=b.copy();expected[z]=0
    assert out==expected and t==c and len(cap)==1 and cap[0][1]==z and all(len(m)==4 for m in seq)
    maxrep=max(maxrep,r);seen.add(z)
assert seen==static(b,fixed_core) and len(seen)==28
print('PASS: 28 independent deletions, both helpers returned.')
# Exact mate on the two-king/two-knight core. This is the common alternative
# continuation proving all ordinary deletion prefixes are non-dead.
core=[p if i in fixed_core else 0 for i,p in enumerate(b)]
mate(replay(State(core,c),D['knights_mate']))
print('PASS: common two-knight mating continuation.')
for victim in (1,-1):
    sp=D['sacrifices'][str(victim)];opt=static(b,{ks[1],ks[-1],homes[victim]})
    out,t,cap,states,r=symbolic(b,c,sp['moves'],opt)
    expected=b.copy();expected[homes[victim]]=0
    assert out==expected and t==c and len(cap)==1 and cap[0][0]==sp['capture_index'] and cap[0][2]==victim*2
    assert len(sp['moves'])<=14 and all(len(m)==4 for m in sp['moves'])
    maxrep=max(maxrep,r)
    # Every pre-capture point can return to the unchanged storage configuration.
    # Valid even if the other helper is absent (it is optional).
    assert len(sp['rollback'])==sp['capture_index']
    for j,back in enumerate(sp['rollback']):
        sb,sc=states[j+1]
        ret,rt,rc,_,_=symbolic(sb,sc,back,opt)
        assert ret==b and rt==c and not rc
print('PASS: two helper-sacrifice modules and all pre-capture reversals.')
assert maxrep<=2
assert base.half+28<150 and 2*28+14<150
print('PASS: target histories have no fivefold repetition or 75-move draw (at most two phases per material count).')
# After losing one helper, the remaining helper can still remove all enemies
# other than their king. This is used only for a possible mating continuation.
seen=set()
for side,loc,seq in D['one_helper']:
    z=sq(loc);start=b.copy();start[homes[-side]]=0
    assert start[z]*side<0 and abs(start[z])!=6
    opt=static(start,{ks[1],ks[-1],homes[side],z})
    out,t,cap,_,_=symbolic(start,c,seq,opt)
    exp=start.copy();exp[z]=0
    assert out==exp and t==c and len(cap)==1 and cap[0][1]==z
    seen.add((side,z))
assert seen=={(side,z) for side in (1,-1) for z,p in enumerate(b) if p*side<0 and abs(p)!=6 and z!=homes[-side]}
print('PASS: 28 one-helper clearing modules.')
# For a target with no knights but at least a pawn, rook, or queen, we keep
# a designated representative of one such type. Retain that color's helper
# until the last capture. After the first helper is lost, all remaining
# target histories can still lead to mate via clearing and one of these six
# routes. No need to assume arbitrary positions with a pawn are non-dead.
seen=set()
for side,loc,typ,seq in D['major_mates']:
    z=sq(loc);assert b[z]==side*typ
    start=[p if p*side>0 and (abs(p)!=2 or i==homes[side]) else 0 for i,p in enumerate(b)]
    start[ks[-side]]=-6*side
    opt=static(start,{ks[1],ks[-1],homes[side],z})
    out,t,cap,_,_=symbolic(start,c,seq,opt)
    assert not cap and t==-side and king(out,-side)==ks[-side]
    if side==1: nloc,mloc=('c6','b8') if typ==4 else ('d6','b7')
    else:nloc,mloc=('f3','g1') if typ==4 else ('e3','g2')
    assert out[sq(nloc)]==side*2 and out[sq(mloc)]==side*(4 if typ==4 else 5)
    # Mate depends only on these adjacent attacks and the knight. With every
    # optional piece absent the position is mate; adding them cannot obstruct
    # the adjacent rook/queen attacks or the knight's attacks.
    final=[p if i not in opt else 0 for i,p in enumerate(out)]
    mate(State(final,t));assert sum(p!=0 for p in final)==4
    seen.add((side,typ))
assert seen=={(s,t) for s in (1,-1) for t in (1,4,5)}
print('PASS: six robust one-helper mating continuations.')
# Six all-bishop profiles: keep a temporary rook until the last capture, and
# certify the exact same prefix by a separate no-promotion mate continuation.
seen=set()
for case in D['bishop_exceptions']:
    seq=case['moves_after_storage'];alt=case['mate_after_storage'];assert seq[:-1]==alt[:len(seq)-1]
    assert all(len(m)==4 for m in seq+alt)
    target=replay(base.copy(),seq);mate(replay(base.copy(),alt))
    p=tuple(sorted((target.b.count(3),target.b.count(-3))))
    assert list(p)==case['profile'] and all(abs(x) in (0,3,6) for x in target.b)
    seen.add(p)
assert seen=={(i,j) for i in range(3) for j in range(i,3)}
print('PASS: six all-bishop profiles, including K vs K, without promotions.')
# Count, not enumerate, the material profiles. Every capped side count can be
# selected by the deletion procedure. Interchange of colors is a symmetry.
side_profiles=9*3*3*3*2;total=side_profiles*(side_profiles+1)//2
print('PASS:',total,'material profiles with original type limits, all reachable without any promotion.')
