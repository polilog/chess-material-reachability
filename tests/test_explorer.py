"""Fast Explorer checks; full corpus queries live in explorer/smoke_test.py."""
import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'explorer'))
from engine import admissible, concrete, INIT

class ExplorerTests(unittest.TestCase):
    def test_admissibility(self):
        self.assertTrue(admissible(INIT, INIT))
        self.assertFalse(admissible((8, 2, 2, 2, 2), INIT))
        self.assertFalse(admissible((7, 2, 2, 2, 2), INIT))
        self.assertTrue(admissible((0, 2, 2, 2, 9), (0, 2, 2, 2, 5)))
    def test_initial_position_pgn(self):
        result = concrete(['e2e4', 'e7e5'], (INIT, INIT))
        self.assertEqual(result['targetPly'], 0)
        self.assertIn('initial position', result['pgn'])
        self.assertEqual(len(result['boards']), 3)
    def test_illegal_move(self):
        with self.assertRaises(ValueError):
            concrete(['e2e5'], (INIT, INIT))
    def test_reversed_witness_pgn(self):
        white = INIT
        black = (7, 2, 2, 2, 1)
        r = concrete(['e2e4', 'd7d5', 'e4d5'], (black, white))
        self.assertTrue(r['swapped'])
        self.assertIn('colors interchanged', r['pgn'])
        self.assertEqual(r['targetPly'], 3)
