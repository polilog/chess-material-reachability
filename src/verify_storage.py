#!/usr/bin/env python3
"""Verify independent deletions and optional final sacrifice of one helper.
Proof uses only local knight routes and a common mating continuation.
No enumeration of subsets of material or promotion assignments.
"""
import sys,json
from pathlib import Path
from collections import deque,Counter
from concurrent.futures import ProcessPoolExecutor
from storage_prefix import verify_one,v
from verify_special import read_templates

def name(z):return chr(97+z%8)+str(z//8+1)
def move(a,z):return name(a)+name(z)
def kn(a,z):return abs(a%8-z%8)*abs(a//8-z//8)==2
def adj(a,z):return max(abs(a%8-z%8),abs(a//8-z//8))==1
def raw(p,a,z):
    x=[0]*64;x[a]=p
    return v.attacked(x,z,v.sgn(p))
def path(b,side,home,wait,goal):
    ek=v.king(b,-side);q=deque([home]);prev={home:None}
    while q and goal not in prev:
        a=q.popleft()
        for z in range(64):
            if not kn(a,z) or z in prev or z==wait or kn(z,ek) or (b[z] and z!=goal):continue
            prev[z]=a;q.append(z)
    if goal not in prev:return None
    p=[goal]
    while prev[p[-1]] is not None:p.append(prev[p[-1]])
    return p[::-1]
def seq_for(p,side,homeother,wait,turn):
    seq=[]
    for i,(a,z) in enumerate(zip(p,p[1:])):
        w=move(wait,homeother) if i%2 else move(homeother,wait)
        m=move(a,z);seq.extend([m,w] if turn==side else [w,m])
    return seq

def verify_one_storage(lines):
    hidx=next(i for i,l in enumerate(lines) if l.startswith('STORAGE '));assert hidx==len(lines)-2 and lines[-1].startswith('MATE ')
    st=verify_one(lines[:hidx]+['SUFFIX']);b=st.b;turn=st.c
    hw,ww,hb,wb=map(v.sq,lines[hidx].split()[1:]);homes={1:hw,-1:hb};waits={1:ww,-1:wb};kings={c:v.king(b,c) for c in (1,-1)}
    assert b[hw]==2 and b[hb]==-2 and len({hw,ww,hb,wb})==4 and not b[ww] and not b[wb]
    core={hw,hb,*kings.values()};optional={i for i,p in enumerate(b) if p and i not in core}
    for a,p in enumerate(b):
        if p:assert not raw(p,a,kings[-v.sgn(p)])
    # Check deletion modules with all optional pieces present. Since raw attacks
    # from stationary pieces are absent and knights avoid checking the kings,
    # omitting any other optional pieces cannot invalidate any move.
    modules=[];maxlen=0;maxpre=0;maxpost=0
    for target in sorted(optional):
        side=-v.sgn(b[target]);p=path(b,side,homes[side],waits[-side],target);assert p is not None
        seq=seq_for(p+p[-2::-1],side,homes[-side],waits[-side],turn)
        q=b.copy();c=turn;caps=0;pre=Counter();post=Counter();phase=pre
        ph=0
        # Core-moving geometry only; counts are independent of stationary subset.
        locs=homes.copy()
        def key():return (locs[1],locs[-1],c)
        phase[key()]+=1
        for m in seq:
            a,z,pr=v.parse(m);assert not pr and a==locs[c] and abs(q[a])==2
            assert z not in optional or z==target and q[z] or z==target and not q[z]
            victim=q[z];r=v.moved(q,c,m);assert r is not None
            assert not kn(z,kings[-c]);locs[c]=z
            q=r;c=-c
            if victim:
                assert z==target and victim*b[target]>0;caps+=1;phase=post;ph=1
            phase[key()]+=1
        out=b.copy();out[target]=0;assert q==out and c==turn and caps==1
        assert max(pre.values())<=2 and max(post.values())<=2
        # Validate overlap of the initial prefix with pre-capture phase.
        check=st.reps.copy();qq=b.copy();cc=turn;steps_pre=0
        for m in seq:
            a,z,_=v.parse(m)
            if qq[z]:break
            qq=v.moved(qq,cc,m);cc=-cc;check[v.sig(qq,cc)]+=1;steps_pre+=1
        assert max(check.values())<5
        maxlen=max(maxlen,len(seq));maxpre=max(maxpre,steps_pre);maxpost=max(maxpost,len(seq)-steps_pre-1)
        modules.append((target,seq,pre,post))
    assert st.half+maxpre<150 and maxpost+maxpre<150
    coreb=[p if i in core else 0 for i,p in enumerate(b)];mate=v.State(coreb,turn);mate_seq=lines[-1].split()[1:]
    for m in mate_seq:
        a,z,pr=v.parse(m);assert not mate.b[z] and not pr;mate.play(m)
    v.universal_mate(mate);assert max(mate.reps.values())<=2 and maxpost+len(mate_seq)<150
    # For a final sacrifice of one helper, find a reversible round trip. At
    # the last outward hop the king can capture it. The round trip, then
    # independent deletions and the core mate, proves every prefix non-dead.
    sacrifices={}
    for side in (1,-1):
        enemy=-side;ek=kings[enemy];home=homes[side]
        for z in range(64):
            if b[z] or z==waits[enemy] or not adj(ek,z):continue
            if any(p*side>0 and a!=home and raw(p,a,z) for a,p in enumerate(b)):continue
            p=path(b,side,home,waits[enemy],z)
            if p is None:continue
            seq=seq_for(p+p[-2::-1],side,homes[enemy],waits[enemy],turn)
            # Construct full round trip and collect moving-core signatures.
            q=b.copy();c=turn;loc=homes.copy();rep=Counter();full=[];cap_seq=None
            for m in seq:
                a,d,pr=v.parse(m);assert not q[d] and not pr and a==loc[c]
                q=v.moved(q,c,m);assert q is not None and not kn(d,kings[-c]);loc[c]=d;c=-c;full.append(m);rep[(loc[1],loc[-1],c)]+=1
                if d==z and c==enemy and cap_seq is None:
                    capture=move(ek,z);assert v.moved(q,c,capture) is not None;cap_seq=full+[capture]
            assert q==b and c==turn
            if cap_seq is None:continue
            # All material-preserving intervals before and after the reversible
            # loop must obey fivefold repetition and 75 moves, even under any
            # stationary subset. Ignore the shared boundary once in each count.
            if st.half+len(seq)+maxpre>=150 or maxpost+len(seq)+maxpre>=150:continue
            ok=True
            for _,_,_,post in modules:
                for _,_,pre,_ in modules:
                    if max((post+rep+pre).values())>4:ok=False;break
                if not ok:break
            if not ok:continue
            qq=b.copy();cc=turn;reps=st.reps.copy()
            for m in seq:qq=v.moved(qq,cc,m);cc=-cc;reps[v.sig(qq,cc)]+=1
            if max(reps.values())>4:continue
            for _,moves,_,_ in modules:
                qq=b.copy();cc=turn;r=reps.copy()
                for m in moves:
                    a,d,pr=v.parse(m)
                    if qq[d]:break
                    qq=v.moved(qq,cc,m);cc=-cc;r[v.sig(qq,cc)]+=1
                if max(r.values())>4:ok=False;break
            if not ok:continue
            sacrifices[side]=cap_seq;break
    a=tuple(b.count(t) for t in range(1,6));d=tuple(b.count(-t) for t in range(1,6))
    return dict(a=a,b=d,w=b.count(7),z=b.count(-7),sac=sorted(sacrifices),routes=len(modules),maxlen=maxlen,half=st.half)

def check_file(p):
    out=[];bad=[];n=0
    for i,h,ls in read_templates(Path(p)):
        n+=1
        try:
            f=verify_one_storage(ls);f['source']=Path(p).name;f['index']=i;out.append(f)
        except Exception as e:bad.append((i,repr(e)))
    Path(p).with_suffix('.storage.json').write_text(json.dumps(out,separators=(',',':'))+'\n')
    Path(p).with_suffix('.storage.validation').write_text(json.dumps(bad)+'\n')
    return str(p),n,len(out),len(bad),sum(bool(f['sac']) for f in out)
if __name__=='__main__':
    with ProcessPoolExecutor(max_workers=4) as ex:
        for r in ex.map(check_file,sys.argv[1:]):print(*r,flush=True)
