#!/usr/bin/env python3
"""Counts master loss classes by coefficients; never enumerates material profiles."""
from collections import Counter

def mul(a,b):
    c=Counter()
    for (i,p),v in a.items():
        for (j,q),w in b.items():
            if i+j<=8:c[i+j,p+q]+=v*w
    return c

def side(knight_cap=2):
    f={(0,0):1}
    for cap in (knight_cap,2,2,1):f=mul(f,{(j,0):1 for j in range(cap+1)})
    return mul(f,{(2*d,d):1 for d in range(5)})
for cap in (2,1):
    f=side(cap);g=mul(f,f);tot=0
    for d in range(5):
        n=(g[8,d]+(f.get((4,d//2),0) if d%2==0 else 0))//2
        tot+=n;print('retain knight' if cap==1 else 'all','D=',d,'C=',8-d,'classes',n)
    print('TOTAL',tot)
    assert tot==(1123 if cap==2 else 657)
f=side();g=mul(f,f);assert g[7,0]%2==0
print('25-piece, no pawn loss:',g[7,0]//2)
assert g[7,0]//2==267
