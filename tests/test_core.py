import sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'src'))
from upper_bound import upper_bound, side_profiles
import verify_base as v
from check_example import check

class CoreTests(unittest.TestCase):
    def test_candidate_count(self):
        self.assertEqual(len(side_profiles()),8694)
        up=upper_bound();self.assertEqual(sum(up),29045304)
        self.assertEqual((up[2],up[8],up[25],up[26],up[27],up[28],up[29],up[30],up[31],up[32]),(1,2520,4243148,3783484,2178319,613655,83625,6090,155,1))
    def test_initial_moves(self):
        b=v.initial();self.assertIsNotNone(v.moved(b,1,'e2e4'))
        self.assertIsNone(v.moved(b,1,'e2e5'));self.assertIsNone(v.moved(b,1,'c1h6'))
        self.assertIsNone(v.moved(b,1,'e1e2'));self.assertIsNone(v.moved(b,1,'a7a6'))
    def test_promotion_and_mate(self):
        check()
    def test_pinned_piece(self):
        b=[0]*64;b[v.sq('e1')]=6;b[v.sq('a8')]=-6;b[v.sq('e8')]=-4;b[v.sq('e2')]=4
        self.assertIsNone(v.moved(b,1,'e2d2'))
        self.assertIsNotNone(v.moved(b,1,'e2e3'))
    def test_wildcard_attack(self):
        b=[0]*64;b[v.sq('e4')]=-7
        self.assertTrue(v.attacked(b,v.sq('f6'),-1))
        self.assertTrue(v.attacked(b,v.sq('e1'),-1))
        self.assertFalse(v.attacked(b,v.sq('g5'),1))
if __name__=='__main__':unittest.main()
