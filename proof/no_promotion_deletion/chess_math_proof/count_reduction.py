#!/usr/bin/env python3
"""Count sufficient master-certificate classes; this is NOT existence proof."""
from collections import Counter
from itertools import product

def pairs(ranges,k):
    d=Counter(map(sum,product(*(range(r) for r in ranges))))
    ordered=sum(d[i]*d[k-i] for i in range(k+1))
    fixed=d[k//2] if k%2==0 else 0
    return (ordered+fixed)//2
all8=pairs((9,3,3,3,2),8)
reserve8=pairs((9,2,3,3,2),8)
exceptions23=pairs((9,3,3,2),5)
print('24-piece loss classes:',all8)
print('24-piece loss classes retaining an original knight of each color:',reserve8)
print('24-piece boundary classes with a knightless side:',all8-reserve8)
print('23-piece boundary classes with both sides knightless:',exceptions23)
print('Sufficient master-certificate classes (if each has the stated robust property):',all8+exceptions23)
assert (all8,reserve8,exceptions23)==(3209,1985,212)
