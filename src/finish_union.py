#!/usr/bin/env python3
"""Finish a fresh replay with storage/deletion rectangles; compare sets, not totals."""
import argparse, json
from pathlib import Path
from functools import lru_cache
from collections import defaultdict
import numpy as np
from upper_bound import side_profiles, upper_bound

def main():
    p=argparse.ArgumentParser();p.add_argument('matrix',type=Path);p.add_argument('output',type=Path);p.add_argument('storage',nargs='*',type=Path);a=p.parse_args()
    sides=side_profiles();L=len(sides);A=np.array(sides);sz=A.sum(1)+1
    assert a.matrix.stat().st_size==L*L
    raw=np.memmap(a.matrix,dtype=np.uint8,mode='r',shape=(L,L));rows=[]
    for i in range(L):
        mask=np.concatenate((raw[:i,i],raw[i,i:]))==2
        rows.append(int.from_bytes(np.packbits(mask,bitorder='little').tobytes(),'little'))
    @lru_cache(None)
    def down(t,w,m):
        o=np.array(t);ok=(A[:,0]<=o[0])&(np.maximum(A[:,1:]-o[1:],0).sum(1)<=w)&(A[:,1]>=m)
        return tuple(np.flatnonzero(ok)),int.from_bytes(np.packbits(ok,bitorder='little').tobytes(),'little')
    by={n:sum(1<<i for i,s in enumerate(sz) if s==n) for n in range(1,17)}
    lim=[sum(by.get(n,0) for n in range(max(1,9-sz[i]),min(16,23-sz[i])+1)) for i in range(L)]
    for f in a.storage:
        for q in json.loads(f.read_text()):
            for s in [0]+q['sac']:
                aa=q['a'].copy();bb=q['b'].copy();aa[1]-=s==1;bb[1]-=s==-1
                ai,am=down(tuple(aa),q['w'],0 if s==1 else 1);bi,bm=down(tuple(bb),q['z'],0 if s==-1 else 1)
                for i in ai:rows[i]|=bm&lim[i]
                for j in bi:rows[j]|=am&lim[j]
    # Build exact candidate row masks from independently grouped single-side data.
    groups=defaultdict(int);keys=[]
    for i,t in enumerate(sides):
        u=sum(max(0,x-y) for x,y in zip(t[1:],(2,2,2,1)));d=8-t[0]-u;key=(15-sum(t),u,d)
        groups[key]|=1<<i;keys.append(key)
    assert len(groups)==324
    allowed={}
    for l,u,d in groups:
        mask=0
        for (r,v,e),bits in groups.items():
            if u<=l+r+e and v<=l+r+d:mask|=bits
        allowed[l,u,d]=mask
    for i,r in enumerate(rows):
        assert r&~allowed[keys[i]]==0,('noncandidate coverage',sides[i])
    missing=[allowed[k]&~r for k,r in zip(keys,rows)]
    # Symmetry follows by construction, but check it explicitly on the actual
    # upper-triangular concrete data + symmetric rectangle union if desired.
    up=upper_bound();counts=[];lines=['N\tupper\tcovered\tmissing']
    for n in range(2,33):
        bits=[r&by.get(n-sz[i],0) for i,r in enumerate(missing)]
        m=(sum(x.bit_count() for x in bits)+sum((x>>i)&1 for i,x in enumerate(bits)))//2
        counts.append(m);lines.append(f'{n}\t{up[n]}\t{up[n]-m}\t{m}')
    total=sum(counts);lines.append(f'Total\t{sum(up)}\t{sum(up)-total}\t{total}')
    a.output.write_text('\n'.join(lines)+'\n');print(a.output.read_text(),end='')
    if total:
        with a.output.with_suffix('.missing.tsv').open('w') as f:
            f.write('N\twhite_PNBRQ\tblack_PNBRQ\n')
            for i,mask in enumerate(missing):
                mask &= ~((1<<i)-1)
                while mask:
                    bit=mask&-mask;j=bit.bit_length()-1;mask^=bit
                    f.write(f'{sz[i]+sz[j]}\t{",".join(map(str,sides[i]))}\t{",".join(map(str,sides[j]))}\n')
        raise SystemExit('INCOMPLETE: exact missing profiles saved')
    assert all(r==allowed[k] for r,k in zip(rows,keys))
    print('PASS: exact set equality, rebuilt from certificate outputs.')
if __name__=='__main__':main()
