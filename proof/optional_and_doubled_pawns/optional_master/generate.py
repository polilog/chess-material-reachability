"""Build a concrete game for any certified profile. P,N,B,R,Q counts, knights include helper."""
from inspect_master import *
import sys,json
root=Path(__file__).resolve().parent

def get_choices(lines):
    ids={};colors=[];opts=set();i=2
    while i<len(lines)-1:
        t=lines[i].split();tag=t[0]
        if tag=='OPTION':
            z=sq(t[1]);num=len(colors);colors.append(1 if z//8==5 else -1);ids[z]=num;opts.add(num);i+=1
        elif tag=='PROM':
            z=sq(t[1][2:]);num=len(colors);colors.append(1 if z//8==7 else -1);end=z;i+=1
            if lines[i].startswith('PARK '):end=parse(lines[i].split()[-1])[1];i+=1
            ids[end]=num
        elif tag=='SHIFT':
            z=sq(t[1]);end=parse(t[-1])[1];ids[end]=ids.pop(z);i+=1
        else:i+=1
    return ids,colors,opts

def build(w,b):
    s,h,options=replay_prefix();board=s.b;homes={1:h[0],-1:h[2]};lines=(root/'master.txt').read_text().splitlines();ids,colors,opts=get_choices(lines)
    types=[2]*len(colors);keep=set(homes.values())|{king(board,1),king(board,-1)}
    for c,tgt in ((1,w),(-1,b)):
        if len(tgt)!=5 or min(tgt)<0 or tgt[1]<1:raise ValueError('expected P,N,B,R,Q; N >=1')
        req=tgt.copy();req[1]-=1
        for typ in range(1,6):
            for i,p in enumerate(board):
                if i not in keep and p==typ*c and req[typ-1]>0:keep.add(i);req[typ-1]-=1
        free=[i for i in ids if board[i]==7*c];op=[i for i in free if ids[i] in opts]
        if req[0]>len(op) or sum(req)>len(free):raise ValueError('profile outside master family')
        for i in range(req[0]):
            z=op.pop();free.remove(z);types[ids[z]]=1;keep.add(z)
        for typ in TYPES:
            for j in range(req[typ-1]):
                z=free.pop();types[ids[z]]=typ;keep.add(z)
    actual=State();moves=[]
    def play(m):actual.play(m);moves.append(m)
    for m in lines[1].split():play(m)
    i=2;num=0;active={}
    while i<len(lines)-1:
        t=lines[i].split();tag=t[0]
        if tag=='MOVE':play(t[1]);i+=1;continue
        if tag=='OPTION':
            typ=types[num];num+=1;loc=sq(t[1]);active[loc]=typ
            for m in t[2+8*(typ-1):10+8*(typ-1)]:play(m)
            i+=1;continue
        if tag=='PROM':
            typ=types[num];num+=1;loc=sq(t[1][2:]);play(t[1]+PC[typ]);i+=1;park=lines[i].split()[1:] if lines[i].startswith('PARK ') else [];i+=bool(park)
        else:
            assert tag=='SHIFT';loc=sq(t[1]);typ=active.pop(loc);park=t[2:];i+=1
        end=loc
        if park:
            wait,rev=park[:2];p1,p2=park[2+2*(typ-2):4+2*(typ-2)]
            for m in (wait,p1,rev,p2):play(m)
            end=parse(p2)[1]
        active[end]=typ
    assert num==len(types)
    assert actual.b==[p if abs(p)!=7 else sgn(p)*types[ids[i]] for i,p in enumerate(board)]
    deletion={sq(z):seq for z,seq in json.loads((root/'deletions.json').read_text())}
    for z,seq in sorted(deletion.items()):
        if z not in keep:
            for m in seq:play(m)
    for c,tgt in ((1,w),(-1,b)):assert [actual.b.count(c*t) for t in range(1,6)]==tgt
    target=len(moves)
    for z,seq in sorted(deletion.items()):
        if z in keep:
            for m in seq:play(m)
    for m in (root/'mate.txt').read_text().split():play(m)
    assert attacked(actual.b,king(actual.b,actual.c),-actual.c)
    for a,p in enumerate(actual.b):
        if p*actual.c<=0:continue
        for z in range(64):assert moved(actual.b,actual.c,name(a)+name(z)) is None
    return moves,target
if __name__=='__main__':
    w,b=[list(map(int,x.split(','))) for x in sys.argv[1:3]]
    try:m,target=build(w,b)
    except ValueError:m,target=build(b,w)
    print(' '.join(m));print('Target ply',target,'mate ply',len(m),file=sys.stderr)
