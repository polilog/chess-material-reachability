#!/usr/bin/env python3
"""Verify ordinary wildcard certificates and final-capture branches.
A TARGET move is an alternative to the common mating continuation. Thus the
prefix is non-dead for every assignment, even if TARGET itself is terminal.
"""
import sys,os
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT))
from verify_special import verify_one,read_templates,sig_family
from storage_prefix import verify_one as prefix,v

def verify(lines,masks):
 ids=[i for i,x in enumerate(lines) if x.startswith('TARGET ')]
 if not ids:
  if lines[-1]=='SUFFIX':
   # A capture may itself deliver mate. No further moves are then possible.
   # Replay the entire prefix and test the final position as a mate.
   assert lines[-2].startswith('CAP ') and not any(x.startswith('OPTION ') for x in lines)
   st=prefix(lines,masks)
   v.universal_mate(st)
   import verify_special as sv
   sv.v.MASKS={1:masks[0],-1:masks[1]}
   return {sig_family(st.b)}
  return verify_one(lines,masks)
 assert len(ids)==1
 i=ids[0];assert lines[i+1]=='SUFFIX'
 # Independent replay to a common mate proves non-deadness at every earlier ply.
 fs=verify_one(lines[:i]+lines[i+1:],masks)
 st=prefix(lines[:i]+['SUFFIX'],masks)
 m=lines[i].split()[1];a,z,pr=v.parse(m)
 assert not pr and st.b[z]*st.c<0 and abs(st.b[z])!=6 and abs(st.b[a])!=7
 st.play(m)
 fs.add(sig_family(st.b))
 return fs

def check_file(name):
 p=Path(name);good=bad=0;families={};errs=[]
 for n,h,ls in read_templates(p):
  try:
   fs=verify(ls,tuple(map(int,h[4:6])) if len(h)>=6 else (15,15))
   for f in fs:families.setdefault(f,n)
   good+=1
  except Exception as e:bad+=1;errs.append(f'{n}: {e!r}')
 p.with_suffix('.families').write_text(''.join(f'{f} {n} 0\n' for f,n in families.items()))
 p.with_suffix('.validation').write_text(f'{good} valid {bad} invalid {len(families)} families\n'+'\n'.join(errs))
 return p.name,good,bad,len(families)
if __name__=='__main__':
 with ProcessPoolExecutor(max_workers=min(4,len(sys.argv)-1)) as ex:
  for r in ex.map(check_file,sys.argv[1:]):print(*r,flush=True)
