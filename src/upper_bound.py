#!/usr/bin/env python3
from collections import Counter
from itertools import product
BASE=(8,2,2,2,1)
def side_profiles():
    return [a for a in product(range(9),range(11),range(11),range(11),range(10))
            if sum(a)<=15 and a[0]+sum(max(0,x-y) for x,y in zip(a[1:],BASE[1:]))<=8]
def upper_bound():
    sides=side_profiles(); assert len(sides)==8694
    groups=Counter()
    for a in sides:
        p=sum(max(0,x-y) for x,y in zip(a[1:],BASE[1:])); d=8-a[0]-p
        groups[(15-sum(a),p,d)]+=1
    assert len(groups)==324
    out=[0]*33;g=list(groups.items())
    for i,((l,p,d),u) in enumerate(g):
        for j,((r,q,e),v) in enumerate(g[i:],i):
            C=l+r
            if p>C+e or q>C+d: continue
            out[32-C]+=u*v if i!=j else u*(u+1)//2
    assert sum(out)==29045304
    return out
if __name__=='__main__':
    up=upper_bound()
    for n in range(2,33):print(n,up[n])
    print('Total',sum(up))
