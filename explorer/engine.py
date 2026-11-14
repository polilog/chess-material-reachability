"""Witness lookup and concrete expansion; all paths relative to a compact release."""
from __future__ import annotations
from collections import Counter
from functools import lru_cache
from pathlib import Path
import sys, subprocess, os, json, itertools, shutil
ROOT=Path(os.environ.get('CHESS_REPO',Path(__file__).resolve().parent.parent)).resolve()
sys.path.insert(0,str(ROOT/'src'))
import verify_base as v
from verify_special import read_templates
from verify_branch import verify as check_template
from storage_details import verify_one_storage
PC=' pnbrqk'; TYPES=(1,2,3,4,5); INIT=(8,2,2,2,1)

def profile(b,c):return tuple(b.count(c*t) for t in TYPES)
def sq(n):return chr(97+n%8)+str(n//8+1)
def parse(m):return v.sq(m[:2]),v.sq(m[2:4]),PC.index(m[4]) if len(m)==5 else 0

def geom(t,a,z):
    x,y=abs(a%8-z%8),abs(a//8-z//8)
    return bool(x or y) and (x*y==2 if t==2 else x==y if t==3 else not(x and y) if t==4 else not(x and y) or x==y)
def hits(b,t,a,z):
    if not geom(t,a,z):return False
    if t==2:return True
    d=v.sgn(z%8-a%8)+8*v.sgn(z//8-a//8);i=a+d
    while i!=z:
        if b[i]:return False
        i+=d
    return True

def moved(b,c,m,ep=-1):
    a,z,pr=parse(m)
    if abs(b[a])==1 and b[a]==c and not b[z] and a%8!=z%8:
        if z!=ep or abs(a%8-z%8)!=1 or z//8-a//8!=c or b[z-8*c]!=-c or pr:return None
        q=b.copy();q[a]=q[z-8*c]=0;q[z]=c
        return None if v.attacked(q,v.king(q,c),-c) else q
    return v.moved(b,c,m)

def next_ep(b,m):
    a,z,_=parse(m);return (a+z)//2 if abs(b[a])==1 and abs(a//8-z//8)==2 else -1

def moves_legal(b,c,ep):
    for a,p in enumerate(b):
        if p*c<=0:continue
        for z in range(64):
            if b[z]*c>0 or z==a:continue
            for pr in ('n','b','r','q') if abs(p)==1 and z//8 in (0,7) else ('',):
                m=sq(a)+sq(z)+pr
                if moved(b,c,m,ep) is not None:yield m

def concrete(ms, target, *, full_mate=False, note='',source=''):
    """Verify concrete moves; emit real board positions and SAN PGN."""
    b=v.initial();c=1;ep=-1;half=0;reps=Counter();boards=[];sans=[];hit=None;swapped=False
    def record():
        nonlocal hit,swapped
        boards.append(''.join(PC[p].upper() if p>0 else PC[-p] if p<0 else '.' for p in b))
        w,bl=profile(b,1),profile(b,-1)
        if hit is None and (w,bl) in (target,target[::-1]):hit=len(boards)-1;swapped=(w,bl)!=target
        elif (w,bl)==target and swapped:hit=len(boards)-1;swapped=False
    record()
    for i,m in enumerate(ms):
        key=(tuple(b),c);reps[key]+=1
        if reps[key]>=5 or half>=150:raise ValueError('automatic draw before target')
        a,z,pr=parse(m);p=abs(b[a]);cap=bool(b[z] or p==1 and a%8!=z%8)
        q=moved(b,c,m,ep)
        if q is None:raise ValueError(f'illegal move {i+1}: {m}')
        if p==1: san=(m[0]+'x' if cap else '')+m[2:4]
        else:
            alts=[j for j,t in enumerate(b) if j!=a and t==b[a] and moved(b,c,sq(j)+sq(z),ep) is not None]
            dis='' if not alts else m[0] if all(j%8!=a%8 for j in alts) else m[1] if all(j//8!=a//8 for j in alts) else m[:2]
            san=PC[p].upper()+dis+('x' if cap else '')+m[2:4]
        if pr:san+='='+PC[pr].upper()
        e=next_ep(b,m);check=v.attacked(q,v.king(q,-c),c)
        if check:
            mate=next(moves_legal(q,-c,e),None) is None
            san+='#' if mate else '+'
            if mate and i!=len(ms)-1:raise ValueError('moves after mate')
        sans.append(san);half=0 if cap or p==1 else half+1;b=q;c=-c;ep=e;record()
    mate=bool(sans and sans[-1].endswith('#'))
    if full_mate and not mate:raise ValueError('expected concrete mating continuation')
    if hit is None:raise ValueError('target not present')
    result=('1-0' if c==-1 else '0-1') if mate else '*'
    # A terminal target may be drawn, but do not falsely assert a draw for an unfinished witness.
    if not mate:
        extras=[(i,abs(p)) for i,p in enumerate(b) if p and abs(p)!=6]
        if not extras or len(extras)==1 and extras[0][1] in (2,3) or extras and all(p==3 for i,p in extras) and len({(i%8+i//8)%2 for i,p in extras})==1 or next(moves_legal(b,c,ep),None) is None:result='1/2-1/2'
    comments=['{Requested material composition reached at the initial position.}'] if hit==0 else []
    for i,s in enumerate(sans):
        if i%2==0:comments.append(f'{i//2+1}.')
        comments.append(s)
        if i+1==hit:comments.append('{Material reached with colors interchanged.}' if swapped else '{Requested material composition reached.}')
    pgn='[Event "Chess Material Reachability proof game"]\n[Site "Local certificate explorer"]\n[Date "????.??.??"]\n[Round "?"]\n[White "Constructed"]\n[Black "Constructed"]\n[Result "'+result+'"]\n\n'+' '.join(comments+[result])+'\n'
    return dict(moves=ms,san=sans,boards=boards,targetPly=hit,swapped=swapped,pgn=pgn,source=source,note=note,result=result)

# Assign independent typed slots to the requested multiset. No 4^k enumeration.
def assign_slots(slots,need,domains):
    if sum(need)!=len(slots) or min(need)<0:return None
    slots=sorted(slots,key=lambda j:len(domains[j]));need=list(need)
    @lru_cache(None)
    def rec(i,rem):
        if i==len(slots):return () if not any(rem) else None
        for t in domains[slots[i]]:
            if rem[t-1]:
                r=list(rem);r[t-1]-=1;x=rec(i+1,tuple(r))
                if x is not None:return (t,)+x
        return None
    res=rec(0,tuple(need));return None if res is None else dict(zip(slots,res))

def fit(b,ids,domains,target):
    choices={}
    for c,tgt in zip((1,-1),target):
        fixed=[0]*5;slots=[]
        for i,p in enumerate(b):
            if p*c<=0 or abs(p)==6:continue
            if ids[i]>=0:slots.append(ids[i])
            else:fixed[abs(p)-1]+=1
        a=assign_slots(slots,[x-y for x,y in zip(tgt,fixed)],domains)
        if a is None:return None
        choices.update(a)
    return {j:choices.get(j,ds[0]) for j,ds in enumerate(domains)}

# Ordinary records may contain flexible promotions later captured. Reconstruct
# exactly the domains used by symbolic_all.cpp, then substitute the types.
def ordinary(ms,target,source='',hint=None):
    b=v.initial();c=1;ep=-1;ids=[-1]*64;domains=[];orig=[];promidx=[];snaps=[]
    for i,m in enumerate(ms):
        a,z,pr=parse(m);p=b[a];cap=bool(b[z] or abs(p)==1 and a%8!=z%8);q=moved(b,c,m,ep)
        if q is None:raise ValueError('ordinary source illegal')
        j=ids[a]
        if j>=0:domains[j]=tuple(t for t in domains[j] if geom(t,a,z))
        if cap and not b[z]:ids[z-8*c]=-1
        ids[a]=-1;ids[z]=j
        if pr:ids[z]=len(domains);domains.append((2,3,4,5));orig.append(pr);promidx.append(i)
        k=v.king(q,c)
        for a2,j2 in enumerate(ids):
            if j2>=0 and q[a2]*c<0:domains[j2]=tuple(t for t in domains[j2] if not hits(q,t,a2,k))
        ep=next_ep(b,m);b=q;c=-c
        if cap or pr:snaps.append((i+1,b.copy(),ids.copy()))
    for j in ids:
        if j>=0:domains[j]=(orig[j],)
    if any(not ds for ds in domains):return None
    snaps.sort(key=lambda x: x[0]!=hint if hint else False)
    for desired in (target,target[::-1]):
        for _,b,ids in snaps:
            ch=fit(b,ids,domains,desired)
            if ch is None:continue
            out=ms.copy()
            for j,k in enumerate(promidx):out[k]=out[k][:4]+PC[ch[j]]
            return concrete(out,target,full_mate=True,source=source,note='Concrete proof game; promotion types instantiated from a checked ordinary certificate.')
    return None

class Template:
    def __init__(self,lines,masks=(15,15)):
        self.lines=lines;self.masks=masks;self.b=v.initial();self.c=1;self.ids=[-1]*64;self.dom=[];self.ops=[];self.snaps=[];self.target_ops=None;self.target_snap=None;self.storage=None
        for m in lines[0].split():self.fixed(m);self.snap()
        i=1
        while i<len(lines):
            t=lines[i].split();tag=t[0];i+=1
            if tag=='SUFFIX':continue
            if tag=='STORAGE':self.storage=t[1:];self.mate=lines[i].split()[1:];break
            if tag=='TARGET':
                b,ids,c,ops=self.b.copy(),self.ids.copy(),self.c,self.ops.copy()
                self.fixed(t[1]);self.target_snap=(self.b.copy(),self.ids.copy());self.target_ops=self.ops.copy()
                self.b,self.ids,self.c,self.ops=b,ids,c,ops;continue
            if tag in ('MOVE','CAP'):self.fixed(t[1]);self.snap();continue
            if tag=='REVEAL':
                j=self.ids[v.sq(t[1])];self.dom[j]=(PC.index(t[2]),);continue
            if tag=='SHIFT':
                a=v.sq(t[1]);j=self.ids[a];park=t[2:];z=v.sq(park[3+2*(self.dom[j][0]-2)][2:4]);self.ops.append(('shift',j,park));self.b[z]=self.b[a];self.b[a]=0;self.ids[z]=j;self.ids[a]=-1;continue
            if tag=='OPTION':
                a=v.sq(t[1]);j=len(self.dom);self.dom.append((1,2,3,4,5));self.ids[a]=j;self.b[a]=7*self.c;self.ops.append(('option',j,t[2:]));self.snap();continue
            if tag=='PROM':
                a,z,_=parse(t[1]);j=len(self.dom);self.dom.append(tuple(t for t in (2,3,4,5) if masks[0 if self.c==1 else 1]&(1<<(t-2))))
                self.b[a]=0;self.ids[a]=-1;self.b[z]=7*self.c;self.ids[z]=j;self.c=-self.c;park=[]
                if i<len(lines) and lines[i].startswith('PARK '):
                    park=lines[i].split()[1:];i+=1;end=v.sq(park[3+2*(self.dom[j][0]-2)][2:4]);self.b[end]=self.b[z];self.b[z]=0;self.ids[end]=j;self.ids[z]=-1
                self.ops.append(('prom',j,t[1],park));self.snap();continue
            raise ValueError('unknown template instruction '+tag)
    def fixed(self,m):
        a,z,pr=parse(m);p=self.b[a];self.b[a]=0;self.b[z]=self.c*pr if pr else p;self.ids[z]=self.ids[a];self.ids[a]=-1;self.c=-self.c;self.ops.append(('move',m))
    def snap(self):self.snaps.append((self.b.copy(),self.ids.copy()))
    def render(self,ch,ops=None):
        out=[]
        for op in self.ops if ops is None else ops:
            tag=op[0]
            if tag=='move':out.append(op[1]);continue
            j=op[1];t=ch[j]
            if tag=='option':out.extend(op[2][8*(t-1):8*t]);continue
            if tag=='prom':out.append(op[2]+PC[t]);p=op[3]
            else:p=op[2]
            if p:out.extend([p[0],p[2+2*(t-2)],p[1],p[3+2*(t-2)]])
        return out
    def witness(self,target,source):
        for desired in (target,target[::-1]):
            for b,ids in self.snaps:
                ch=fit(b,ids,self.dom,desired)
                if ch is not None:return concrete(self.render(ch),target,full_mate=True,source=source,note='Expanded universal promotion template, with common mating continuation.')
            if self.target_snap:
                ch=fit(*self.target_snap,self.dom,desired)
                if ch is not None:return concrete(self.render(ch,self.target_ops),target,source=source,note='Expanded terminal-target branch; the verifier checks a separate mating continuation.')
        return None

def admissible(a,b):
    if any(len(t)!=5 or min(t)<0 or sum(t)>15 for t in (a,b)):return False
    u=[sum(max(0,x-y) for x,y in zip(t[1:],INIT[1:])) for t in (a,b)]
    d=[8-t[0]-p for t,p in zip((a,b),u)];C=30-sum(a)-sum(b)
    return min(d)>=0 and u[0]<=C+d[1] and u[1]<=C+d[0]

def storage_witness(lines,target,source):
    meta=verify_one_storage(lines);t=Template(lines);b=t.b;ids=t.ids
    homes={1:v.sq(t.storage[0]),-1:v.sq(t.storage[2])}
    for desired in (target,target[::-1]):
        for sac in [0]+meta['sac']:
            ch={};keep=set(homes.values());keep.update(i for i,p in enumerate(b) if abs(p)==6);ok=True
            for c,goal in zip((1,-1),desired):
                fixed=[[] for _ in TYPES];slots=[]
                for i,p in enumerate(b):
                    if p*c<=0 or abs(p)==6 or i==homes[c]:continue
                    if ids[i]>=0:slots.append(i)
                    else:fixed[abs(p)-1].append(i)
                need=list(goal);need[1]-=c!=sac
                if min(need)<0:ok=False;break
                for k,lst in enumerate(fixed):
                    take=min(need[k],len(lst));keep.update(lst[:take]);need[k]-=take
                if need[0] or sum(need)>len(slots):ok=False;break
                for typ,n in enumerate(need,1):
                    for _ in range(n):
                        i=slots.pop(0);ch[ids[i]]=typ;keep.add(i)
                for i in slots:ch[ids[i]]=t.dom[ids[i]][0]
            if not ok:continue
            ch={j:ch.get(j,ds[0]) for j,ds in enumerate(t.dom)}
            if any(ch[j] not in ds for j,ds in enumerate(t.dom)):continue
            out=t.render(ch);routes=meta['route_moves'];deleted=[i for i in routes if i not in keep]
            for i in deleted:out.extend(routes[i])
            if sac:
                out.extend(meta['sacrifice_moves'][sac]);return concrete(out,target,source=source,note='Universal storage certificate: selected deletions and a verified final helper sacrifice.')
            for i in routes:
                if i in keep:out.extend(routes[i])
            out.extend(t.mate)
            return concrete(out,target,full_mate=True,source=source,note='Universal storage certificate: selected deletions, followed by the common two-knight mating continuation.')
    return None

def mirror_move(m):return m[0]+str(9-int(m[1]))+m[2]+str(9-int(m[3]))+m[4:]
def try_flip(result,target):
    if not result['swapped']:return result
    ms=result['moves'];mir=list(map(mirror_move,ms));mate=result['result'] in ('1-0','0-1')
    def attempt(seq):
        try:
            r=concrete(seq,target,full_mate=mate,source=result['source'],note=result['note']+' Color-reversed witness, replayed from the orthodox initial position.')
            if not r['swapped']:return r
        except (ValueError,AssertionError):pass
        return None
    if len(mir)>=2 and abs(int(mir[1][1])-int(mir[1][3]))==2 and mir[1][0]==mir[1][2]:
        m=mir[1];mid=m[0]+str((int(m[1])+int(m[3]))//2)
        r=attempt([m[:2]+mid,mir[0],mid+m[2:]]+mir[2:])
        if r:return r
    # A legal reversible five-ply tempo gadget, after reordering an early
    # pair of moves. The endpoint has the same board and opposite turn.
    b=v.initial();prefix=[];ep=-1
    def quiet(b,c,ep):
        for m in moves_legal(b,c,ep):
            a,z,p=parse(m)
            if abs(b[a])>1 and not b[z] and not p:yield m,moved(b,c,m,ep)
    for k in range(0,min(20,len(mir)-1),2):
        for m,c in ((mir[k+1],1),(mir[k],-1)):
            q=moved(b,c,m,ep)
            if q is None:return result
            ep=next_ep(b,m);b=q;prefix.append(m)
        if ep>=0: # safe only if next mirrored move is not en passant; validate below
            pass
        for w1,b1 in quiet(b,1,ep):
            a,x,_=parse(w1)
            for bmove,b2 in quiet(b1,-1,-1):
                ba,bz,_=parse(bmove);back=sq(bz)+sq(ba)
                for z in range(64):
                    if z in (a,x) or b2[z]:continue
                    w2=sq(x)+sq(z);q=moved(b2,1,w2)
                    if q is None:continue
                    q2=moved(q,-1,back)
                    if q2 is None:continue
                    w3=sq(z)+sq(a);q3=moved(q2,1,w3)
                    if q3!=b:continue
                    r=attempt(prefix+[w1,bmove,w2,back,w3]+mir[k+2:])
                    if r:return r
        # Bound the gadget search to early positions, before complex tactics.
    return result

class Explorer:
    def __init__(self,replay):
        self.replay=Path(replay).resolve();self.files=sorted(self.replay.glob('games_*.families'))+sorted(self.replay.glob('templates_*.families'))
        if len(self.files)!=8:raise ValueError('The replay directory must contain the eight verified family indexes. Run verify.py first.')
        self.bin=self.replay/'explorer_lookup';source=Path(__file__).with_name('lookup.cpp')
        if not self.bin.exists() or self.bin.stat().st_mtime<source.stat().st_mtime:
            subprocess.run([os.environ.get('CXX','c++'),'-O3','-std=c++17',str(source),'-o',str(self.bin)],check=True)
        self.small=ROOT/'examples/small';self.small_index=self.replay/'explorer_small.families'
        if not self.small_index.exists():
            binary=self.replay/'symbolic_all'
            if not binary.exists():subprocess.run([os.environ.get('CXX','c++'),'-O3','-std=c++17',str(ROOT/'src/symbolic_all.cpp'),'-o',str(binary)],check=True)
            subprocess.run([str(binary),str(self.small/'mate_games.uci'),str(self.small_index)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        self.files.append(self.small_index);self.storage=json.loads((self.replay/'storage_0.storage.json').read_text());self.offsets={}
    def record(self,p,n,block=False):
        p=Path(p);key=(p,block)
        if key not in self.offsets:
            offs=[]
            with p.open('rb') as f:
                while True:
                    pos=f.tell();l=f.readline()
                    if not l:break
                    if not block or l.startswith(b'BEGIN '):offs.append(pos)
            self.offsets[key]=offs
        with p.open('rb') as f:
            f.seek(self.offsets[key][n-1]);l=f.readline().decode().strip()
            if not block:return l.split()
            h=l.split();ls=[]
            for l in f:
                s=l.decode().strip()
                if s=='END':return h,ls
                ls.append(s)
        raise ValueError('unterminated certificate')
    def finish(self,r,target):return try_flip(r,target) if r and r['swapped'] else r
    def find(self,a,b,_exhaustive=False):
        target=(tuple(a),tuple(b));a,b=target
        if not admissible(a,b):return {'status':'impossible','reason':'The requested material violates the individual material or capture/promotion constraints.'}
        if a==b==INIT:
            ms=(ROOT/'examples/14_queens_game.uci').read_text().split()
            return dict(concrete(ms,target,source='14_queens_game.uci',note='The target is present before the first move and throughout the opening until the first capture.'),status='ok')
        # Dead terminal witnesses have their own separately verified mate-prefix evidence.
        if sum(a)+sum(b)<=1:
            for i,l in enumerate((self.small/'dead_games.uci').read_text().splitlines(),1):
                try:return dict(self.finish(concrete(l.split(),target,source=f'dead_games.uci #{i}',note='Explicit terminal witness; the original verifier checks an alternative mating continuation.'),target),status='ok')
                except (ValueError,AssertionError):pass
        # Search the exact family relation, not individual concrete material profiles.
        paths=self.files;cmd=[str(self.bin),*map(str,a),*map(str,b),*map(str,paths)]
        env=os.environ.copy()
        if _exhaustive:env["EXPLORER_ALL"]="1"
        result=subprocess.check_output(cmd,text=True,env=env);fallback=None;errors=[]
        for l in result.splitlines():
            fi,n,ply,fam=l.split();fi,n,ply=int(fi),int(n),int(ply);p=paths[fi];source=f'{p.name} certificate #{n}'
            try:
                if p.name.startswith('templates_'):
                    h,ls=self.record(p.with_suffix('.txt'),n,True);masks=tuple(map(int,h[4:6])) if len(h)>=6 else (15,15)
                    check_template(ls,masks);r=Template(ls,masks).witness(target,source)
                else:
                    f=self.small/'mate_games.uci' if p==self.small_index else p.with_suffix('.uci')
                    r=ordinary(self.record(f,n),target,source,ply)
                if r:
                    if not r['swapped']:return dict(r,status='ok')
                    if fallback is None:fallback=r
            except (ValueError,AssertionError,IndexError) as e:errors.append(f'{source}: {e}')
        if fallback:return dict(self.finish(fallback,target),status='ok')
        # The storage/deletion families have no ordinary family index; match
        # the exact inequalities used by finish_union.py and expand a route.
        if 9<=sum(a)+sum(b)+2<=23:
            def down(goal,base,w,m):return goal[0]<=base[0] and goal[1]>=m and sum(max(0,x-y) for x,y in zip(goal[1:],base[1:]))<=w
            for q in self.storage:
                match=False
                for s in [0]+q['sac']:
                    aa=q['a'].copy();bb=q['b'].copy();aa[1]-=s==1;bb[1]-=s==-1
                    if any(down(x,aa,q['w'],0 if s==1 else 1) and down(y,bb,q['z'],0 if s==-1 else 1) for x,y in (target,target[::-1])):match=True;break
                if not match:continue
                try:
                    _,ls=self.record(self.replay/q['source'],q['index'],True);r=storage_witness(ls,target,f"{q['source']} certificate #{q['index']}")
                    if r:return dict(self.finish(r,target),status='ok')
                except (ValueError,AssertionError,IndexError) as e:errors.append(f"storage #{q['index']}: {e}")
        if not _exhaustive:return self.find(a,b,True)
        return {'status':'error','reason':'The material is admissible, but the explorer could not reconstruct a witness. This is not an impossibility result.','details':errors[:5]}
