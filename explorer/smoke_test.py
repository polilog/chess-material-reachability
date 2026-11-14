"""Run witness-reconstruction smoke tests against a completed cold replay."""
import argparse
from pathlib import Path
from engine import Explorer,admissible,PC

def counts(board,white):
    return tuple(board.count(t.upper() if white else t) for t in 'pnbrq')

def main():
    p=argparse.ArgumentParser();p.add_argument('replay',type=Path);a=p.parse_args();e=Explorer(a.replay)
    tests=[
        ((8,2,2,2,1),(8,2,2,2,1)), # initial board
        ((0,2,2,2,9),(0,2,2,2,5)), # ordinary certificate, 14 queens
        ((0,2,2,2,5),(0,2,2,2,9)), # reversed orientation
        ((0,0,0,0,9),(0,0,0,0,9)), # symbolic template
        ((0,0,0,0,0),(0,0,0,0,0)), # terminal branch
        ((0,0,0,0,0),(0,1,0,0,0)),
        ((0,0,1,0,0),(0,0,0,0,0)),
        ((0,9,0,0,2),(1,1,1,0,0)), # storage routes
        ((0,0,0,3,0),(2,7,0,0,0)), # storage + helper sacrifice
        ((1,0,1,2,0),(1,9,0,0,0)), # storage + reversed orientation
    ]
    for white,black in tests:
        r=e.find(white,black);assert r['status']=='ok',r
        b=r['boards'][r['targetPly']];assert (counts(b,True),counts(b,False))==(white,black),r['source']
        assert len(r['boards'])==len(r['moves'])+1 and len(r['san'])==len(r['moves'])
        print('PASS',white,black,r['targetPly'],r['source'])
    assert e.find((8,2,2,2,2),(8,2,2,2,1))['status']=='impossible'
    print('PASS: invalid material rejected; all 10 witnesses have the exact requested orientation.')
if __name__=='__main__':main()
