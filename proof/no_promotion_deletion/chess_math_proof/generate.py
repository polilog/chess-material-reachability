#!/usr/bin/env python3
"""Emit a legal UCI sequence for any material profile within original limits.
Usage: python generate.py '8,2,2,2,1' '0,0,1,0,0'
Counts are P,N,B,R,Q; colors are interchangeable for the six bishop cases.
"""
import argparse,json
from pathlib import Path
from rules import State,sq
ROOT=Path(__file__).resolve().parent
D=json.loads((ROOT/'proof.json').read_text())

def counts(s):
    out=tuple(map(int,s.split(',')))
    assert len(out)==5 and all(0<=v<=m for v,m in zip(out,(8,2,2,2,1)))
    return out

def generate(w,b):
    target={1:w,-1:b};st=State();moves=D['prefix'].copy()
    for m in moves:st.play(m)
    hw,ww,hb,wb=map(sq,D['homes']);homes={1:hw,-1:hb};board=st.b.copy()
    if w[1]==b[1]==0 and all(w[i]==b[i]==0 for i in (0,3,4)):
        key=sorted([w[2],b[2]]);case=next(x for x in D['bishop_exceptions'] if x['profile']==key)
        extra=case['moves_after_storage']
        for m in extra:st.play(m)
        moves+=extra
    else:
        # If neither side wants a knight, retain one chosen P/R/Q until the
        # last helper sacrifice to guarantee a possible mating continuation.
        witness=None
        if w[1]==b[1]==0:
            witness=next((s,t,sq(loc)) for s,loc,t,seq in D['major_mates'] if target[s][t-1]>0)
        keep=set(homes.values())
        for c in (1,-1):
            for typ,n in enumerate(target[c],1):
                if typ==2:n=max(0,n-1)
                locs=[i for i,p in enumerate(board) if p==c*typ and i!=homes[c]]
                if witness and witness[:2]==(c,typ):
                    chosen=witness[2];locs.remove(chosen);locs.insert(0,chosen)
                keep.update(locs[:n])
        for c,loc,seq in D['two_helper']:
            if sq(loc) not in keep:
                for m in seq:st.play(m)
                moves+=seq
        absent=[c for c in (1,-1) if target[c][1]==0]
        if len(absent)==2:absent=[-witness[0],witness[0]]
        for i,c in enumerate(absent):
            cert=D['sacrifices'][str(c)]
            # Stop immediately after the last required capture, including
            # when the target is itself a dead position.
            seq=cert['moves'] if i+1<len(absent) else cert['moves'][:cert['capture_index']+1]
            for m in seq:st.play(m)
            moves+=seq
    got=tuple(sorted(tuple(st.b.count(c*t) for t in range(1,6)) for c in (1,-1)))
    assert got==tuple(sorted((w,b))) and all(len(m)==4 for m in moves)
    return moves
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('white',type=counts);p.add_argument('black',type=counts);a=p.parse_args()
    print(' '.join(generate(a.white,a.black)))
