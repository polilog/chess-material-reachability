"""Small local certificate: zero, one, or two promotions of doubled pawns.
All branches have common occupancy and side to move, plus a common deletion/mate continuation.
"""
from rules import *
from pathlib import Path
from collections import deque
ROOT=Path(__file__).resolve().parent

def read(f):return (ROOT/f).read_text().split()

def name(z):return chr(97+z%8)+str(1+z//8)

def branch(front=0,back=0):
    assert front in (0,2,3,4,5) and back in (0,2,3,4,5) and (front or not back)
    if not front:return []
    park={2:['e8d6','d6b7','b7a5','a5c6'],3:['e8f7','f7e8','e8d7','d7c6'],4:['e8f8','f8e8','e8c8','c8c6'],5:['e8f8','f8e8','e8c8','c8c6']}
    ret={2:['c6d8','d8e6'],3:['c6d7','d7e6'],4:['c6d6','d6e6'],5:['c6e8','e8e6']}
    backret={2:['e8f6','f6e4'],3:['e8g6','g6e4'],4:['e8e6','e6e4'],5:['e8e6','e6e4']}
    white=['e6e7','e7e8'+PC[front]]+park[front]
    if back:white+=['e4e5','e5e6','e6e7','e7e8'+PC[back]]+backret[back]
    white+=ret[front]
    assert len(white)%2==0
    return [m for i,w in enumerate(white) for m in (w,'h4f3' if i%2==0 else 'f3h4')]

def knight(a,z):return abs(a%8-z%8)*abs(a//8-z//8)==2

def clear_route(b,z):
    # Black knight goes to the optional square, while white knight shuttles.
    home=sq('h4');other=sq('b1');wait=sq('c3');k=sq('a1')
    queue=deque([home]);prev={home:None}
    while queue and z not in prev:
        a=queue.popleft()
        for x in range(64):
            if knight(a,x) and x not in prev and x!=wait and not knight(x,k) and (not b[x] or x==z):prev[x]=a;queue.append(x)
    assert z in prev
    path=[z]
    while prev[path[-1]] is not None:path.append(prev[path[-1]])
    path.reverse();tour=path+path[-2::-1];seq=[]
    for i,(a,x) in enumerate(zip(tour,tour[1:])):seq+=['b1c3' if i%2==0 else 'c3b1',name(a)+name(x)]
    return seq

def main():
    initial_prefix=read('prefix.txt')+read('setup.txt');s=State()
    for m in initial_prefix:s.play(m)
    assert s.c==1 and {name(i):p for i,p in enumerate(s.b) if p}=={'a1':6,'b1':2,'h2':-6,'h4':-2,'e4':1,'e6':1}
    # Both choices are frozen after the pair macro. Q+N attacks are a safe upper bound, including P.
    sym=s.b.copy();sym[sq('e4')]=sym[sq('e6')]=7
    core=sym.copy();clear=[];c=1
    for loc in ('e4','e6'):
        z=sq(loc);seq=clear_route(core,z);clear+=seq
        for m in seq:
            core=moved(core,c,m);assert core is not None;c=-c
        assert core[z]==0 and c==1
    assert sum(bool(p) for p in core)==4
    choices=[(0,0)]+[(t,0) for t in TYPES]+[(t,u) for t in TYPES for u in TYPES]
    for f,b in choices:
        st=s.copy();ms=branch(f,b)
        for m in ms:st.play(m)
        exp=s.b.copy();exp[sq('e6')]=f or 1;exp[sq('e4')]=b or 1
        assert st.b==exp and st.c==1
        for m in clear+read('mate.txt'):st.play(m)
        assert attacked(st.b,king(st.b,st.c),-st.c)
        for a,p in enumerate(st.b):
            if p*st.c<=0:continue
            for z in range(64):assert moved(st.b,st.c,name(a)+name(z)) is None
    print('PASS: reachable six-piece setup,',s.plies,'plies')
    print('PASS: all',len(choices),'local branches with identical occupancy and side to move')
    print('PASS: shared deletion and checkmate continuation for all choices')
    print('15 distinct material outcomes: 1 + 4 + 10; no global profile enumeration')
    if __import__('sys').argv[1:]:
        a,b=map(int,__import__('sys').argv[1:]);print(' '.join(initial_prefix+branch(a,b)+clear+read('mate.txt')))
if __name__=='__main__':main()
