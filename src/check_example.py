#!/usr/bin/env python3
"""Replay the included concrete UCI example and check its extreme milestone."""
from pathlib import Path
from collections import Counter
from verify_base import State, universal_mate
ROOT=Path(__file__).resolve().parent.parent

def check():
    st=State();moves=(ROOT/'examples/14_queens_game.uci').read_text().split()
    for i,m in enumerate(moves,1):
        st.play(m)
        if i==258:
            assert Counter(st.b)==Counter({0:36,6:1,-6:1,5:9,-5:5,4:2,-4:2,3:2,-3:2,2:2,-2:2})
            print('PASS: after 129...a1=Q+, White has 9 queens, Black has 5; 28 pieces.')
    assert len(moves)==271;universal_mate(st)
    print('PASS: legal 271-ply game ending in checkmate.')
if __name__=='__main__':check()
