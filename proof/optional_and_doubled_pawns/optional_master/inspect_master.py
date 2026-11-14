from rules import *
from pathlib import Path
from collections import deque

def name(z):return chr(z%8+97)+str(z//8+1)
def replay_prefix():
    lines=Path(__file__).with_name('master.txt').read_text().splitlines(); st=State()
    for m in lines[1].split():
        assert not parse(m)[2];st.play(m)
    assert sum(p!=0 for p in st.b)==25
    optional=set()
    proms=Counter()
    i=2
    while i<len(lines)-1:
        t=lines[i].split();tag=t[0]
        if tag=='MOVE':
            a,z,pr=parse(t[1]);assert not st.b[z] and not pr;st.play(t[1]);i+=1;continue
        old=st.copy();branches=[]
        if tag=='OPTION':
            loc=sq(t[1]);c=st.c;assert st.b[loc]==c and loc//8==(5 if c==1 else 2) and len(t)==42
            for j,typ in enumerate((1,2,3,4,5)):
                s=old.copy()
                for m in t[2+8*j:10+8*j]:
                    a,z,pr=parse(m);assert not s.b[z] and abs(s.b[a])!=7;s.play(m)
                expect=old.b.copy();expect[loc]=c*typ
                assert s.b==expect and s.c==old.c and s.plies==old.plies+8
                s.b[loc]=7*c;branches.append(s)
            st=branches[0]
            for s in branches[1:]:
                assert (s.b,s.c,s.plies)==(st.b,st.c,st.plies);st.half=max(st.half,s.half);st.reps|=s.reps
            optional.add(loc);i+=1;continue
        if tag=='PROM':
            loc=sq(t[1][2:]);c=st.c;proms[c]+=1;assert st.b[parse(t[1])[0]]==c and not st.b[loc];park=lines[i+1].split()[1:] if lines[i+1].startswith('PARK ') else [];i+=1+bool(park)
        else:
            assert tag=='SHIFT';loc=sq(t[1]);assert loc not in optional;c=-st.c;assert st.b[loc]==7*c;park=t[2:];i+=1
        for typ in TYPES:
            s=old.copy()
            if tag=='PROM':s.play(t[1]+PC[typ])
            else:s.b[loc]=typ*c
            end=loc
            if park:
                assert len(park)==10;w,rev=park[:2];assert parse(w)[:2]==tuple(reversed(parse(rev)[:2]));p1,p2=park[2+2*(typ-2):4+2*(typ-2)]
                assert parse(p1)[0]==loc and parse(p2)[0]==parse(p1)[1]
                for m in (w,p1,rev,p2):
                    a,z,pr=parse(m);assert not s.b[z] and not pr;s.play(m)
                end=parse(p2)[1]
            assert s.b[end]==typ*c
            s.b[end]=7*c
            expect=old.b.copy();expect[parse(t[1])[0] if tag=='PROM' else loc]=0;expect[end]=7*c
            assert s.b==expect and s.c==(-old.c if tag=='PROM' else old.c)
            branches.append(s)
        st=branches[0]
        for s in branches[1:]:
            assert (s.b,s.c,s.plies)==(st.b,st.c,st.plies);st.half=max(st.half,s.half);st.reps|=s.reps
    return st,list(map(sq,lines[-1].split()[1:])),optional
if __name__=='__main__':
 s,h,opts=replay_prefix();print('board',s.plies,s.c,s.half,max(s.reps.values()),[name(x) for x in h]);
 for r in range(7,-1,-1):print(' '.join(f'{p:2}' for p in s.b[8*r:8*r+8]))
 print(Counter(s.b));print('king',name(king(s.b,1)),name(king(s.b,-1)))

 print('optional', [name(x) for x in opts])
