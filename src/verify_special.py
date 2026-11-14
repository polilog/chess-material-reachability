#!/usr/bin/env python3
import sys, importlib.util
from pathlib import Path
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
root=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('v',root/'verify_base.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)

def sig_family(b, optional=()):
    a=[]
    for c in (1,-1):
        n=Counter(x*c for x in b)
        numopt=sum(b[i]==7*c for i in optional)
        a.append(''.join(chr(97+n[t]) for t in (1,2,3,4,5))+chr(65+v.MASKS[c])*(n[7]-numopt)+'Z'*numopt)
    return ':'.join(sorted(a))

def verify_one(lines,masks=(15,15)):
    v.MASKS={1:masks[0],-1:masks[1]}
    st=v.State();fs=set();optional=set();start=lines[0].split()
    for m in start:
        a,z,pr=v.parse(m); changed=bool(st.b[z] or pr)
        st.play(m)
        if changed: fs.add(sig_family(st.b,optional))
    assert sum(x!=0 for x in st.b ) in (24,25,26,27) and not any(abs(x)==7 for x in st.b)
    fs.add(sig_family(st.b,optional));i=1;last=start[-1]
    while i<len(lines) and lines[i]!='SUFFIX':
        tok=lines[i].split();tag=tok[0]
        if tag=='CAP':
            a,z,pr=v.parse(tok[1]);assert not pr and st.b[z]*st.c<0 and abs(st.b[z])!=6 and abs(st.b[a])!=7
            st.play(tok[1]);fs.add(sig_family(st.b,optional));i+=1;continue
        if tag=='MOVE':
            a,z,pr=v.parse(tok[1]);assert not pr and not st.b[z] and abs(st.b[a])!=7
            st.play(tok[1]);last=tok[1];i+=1;continue
        if tag=='REVEAL':
            loc=v.sq(tok[1]);typ=v.PC.index(tok[2]);assert len(tok)==3 and loc not in optional and abs(st.b[loc])==7
            c=1 if st.b[loc]>0 else -1;assert typ in v.allowed(c)
            st.b[loc]=c*typ
            # Earlier snapshots included choices that this specialization no longer proves.
            fs.clear();fs.add(sig_family(st.b,optional));i+=1;continue
        if tag=='SHIFT':
            loc=v.sq(tok[1]);assert len(tok)==12 and loc not in optional and st.b[loc]==-7*st.c
            c=-st.c;old=st.copy();branches=[];park=tok[2:]
            for t in v.allowed(c):
                s=old.copy();s.b[loc]=c*t
                w,rev=park[:2];p1,p2=park[2+2*(t-2):4+2*(t-2)]
                assert v.parse(w)[:2]==tuple(reversed(v.parse(rev)[:2]))
                assert v.parse(p1)[0]==loc and v.parse(p2)[0]==v.parse(p1)[1]
                for m in (w,p1,rev,p2):
                    a,z,pr=v.parse(m);assert not s.b[z] and not pr and abs(s.b[a])!=7
                    s.play(m)
                end=v.parse(p2)[1];assert s.b[end]==c*t and not s.b[loc]
                s.b[end]=7*c;expect=old.b.copy();expect[loc]=0;expect[end]=7*c
                assert s.b==expect and s.c==old.c
                branches.append(s)
            st=branches[0]
            for s in branches[1:]:
                assert (s.b,s.c,s.plies)==(st.b,st.c,st.plies)
                st.half=max(st.half,s.half);st.reps|=s.reps
            assert max(st.reps.values())<5 and st.half<150
            i+=1;continue
        if tag=='OPTION':
            assert masks==(15,15)
            loc=v.sq(tok[1]);assert len(tok)==42 and st.b[loc]==st.c
            assert loc//8==(5 if st.c==1 else 2)
            c=st.c;old=st.copy();branches=[]
            for j,t in enumerate((1,2,3,4,5)):
                s=old.copy()
                for m in tok[2+8*j:10+8*j]:
                    a,z,pr=v.parse(m);assert not s.b[z] and abs(s.b[a])!=7
                    s.play(m)
                expect=old.b.copy();expect[loc]=c*t
                assert s.b==expect and s.c==old.c and s.plies==old.plies+8
                s.b[loc]=7*c;branches.append(s)
            st=branches[0]
            for s in branches[1:]:
                assert (s.b,s.c,s.plies)==(st.b,st.c,st.plies)
                st.half=max(st.half,s.half);st.reps|=s.reps
            assert max(st.reps.values())<5 and st.half<150
            optional.add(loc);fs.add(sig_family(st.b,optional));i+=1;continue
        assert tag=='PROM';m=tok[1];a,z,pr=v.parse(m);c=st.c;assert st.b[a]==c and not st.b[z]
        old=st.copy();branches=[];has_park=i+1<len(lines) and lines[i+1].startswith('PARK ')
        park=lines[i+1].split()[1:] if has_park else []
        for t in v.allowed(c):
            s=old.copy();s.play(m+v.PC[t]);end=z
            if has_park:
                assert len(park)==10
                w,rev=park[:2];p1,p2=park[2+2*(t-2):4+2*(t-2)]
                assert v.parse(p1)[0]==z and v.parse(p2)[0]==v.parse(p1)[1]
                assert v.parse(w)[:2]==tuple(reversed(v.parse(rev)[:2]))
                for u in (w,p1,rev,p2):
                    aa,zz,pp=v.parse(u);assert not s.b[zz] and not pp and abs(s.b[aa])!=7
                    s.play(u)
                end=v.parse(p2)[1]
            assert s.b[end]==c*t
            s.b[end]=7*c;branches.append(s)
        st=branches[0]
        for s in branches[1:]:
            assert (s.b,s.c,s.half,s.plies)==(st.b,st.c,st.half,st.plies)
            st.reps|=s.reps
        assert max(st.reps.values())<5
        fs.add(sig_family(st.b,optional));i+=2 if has_park else 1
    assert i<len(lines) and lines[i]=='SUFFIX';i+=1;assert i<len(lines)
    for l in lines[i:]:
        tag,m=l.split();assert tag=='MOVE';a,z,p=v.parse(m);assert abs(st.b[a])!=7
        last_double=abs(st.b[a])==1 and abs(a//8-z//8)==2
        a,z,pr=v.parse(m); changed=bool(st.b[z] or pr)
        st.play(m)
        if changed: fs.add(sig_family(st.b,optional))
    assert not last_double, 'possible final en passant'
    v.universal_mate(st)
    return fs

def read_templates(p):
    lines=[];num=0
    for l in p.read_text().splitlines():
        if l.startswith('BEGIN '):lines=[];num+=1;header=l.split()
        elif l=='END':yield num,header,lines;lines=[]
        else:lines.append(l)

def check_file(name):
    p=Path(name);good=bad=0;families={};errs=[]
    for n,header,lines in read_templates(p):
        try:
            for x in verify_one(lines,tuple(map(int,header[4:6])) if len(header)>=6 else (15,15)):families.setdefault(x,n)
            good+=1
        except Exception as e:
            bad+=1;errs.append(f'{n}: {e!r}')
    out=p.with_suffix('.families');out.write_text(''.join(f'{s} {n} 0\n' for s,n in families.items()))
    p.with_suffix('.validation').write_text(f'{good} valid {bad} invalid {len(families)} families\n'+'\n'.join(errs))
    return str(p),good,bad,len(families)
if __name__=='__main__':
    with ProcessPoolExecutor(max_workers=4) as ex:
        for result in ex.map(check_file,sys.argv[1:]):print(*result,flush=True)
