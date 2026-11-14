A symbolic, universally branching proof game for 25-piece material profiles.

Run: python verify.py (Python 3, no third-party packages).
It verifies one common legal initial prefix, 15 independent promotions to N/B/R/Q,
3 type-dependent PARK macros with identical resulting occupancy, and a common
legal suffix ending in checkmate for every assignment. Unknown promoted pieces
stay stationary except in their local PARK macro. Their attacks are overapproximated
by queen OR knight attacks. For the final mate test, unknown enemy attackers are
instead treated as inert blockers and all queen/knight defender moves are allowed.
A conservative color-only repetition check covers all branch histories. The common
mate suffix proves that no earlier position was dead. All moves are ordinary chess
moves without castling or en passant. The final universal mate has no pawns; castling
cannot escape check. The 25-piece prefix has 8 white and 7 black surviving pawns,
all white originals, and black king and queen (seven black captures).

There are 4^15 assignments, 19,800 distinct fully promoted material profiles, and
62,106 distinct 25-piece profiles counting the intermediate promotion prefixes.

To expand a particular ordinary proof game (promotion choices in chronological order):
  python verify.py --choices qqqqqqqqqqqqqqq > all_queens.uci
  python verify.py --choices nbrqnbrqnbrqnbr > mixed.uci

The four possible choices are n, b, r, q. Each PARK line encodes the opponent's
quiet move, its reverse, and the two moves of the new piece for each of N/B/R/Q.
The board after each macro is identical up to the new piece's type. The verifier
uses a different representation (64 squares in Python) than the 0x88 C++ search.

Optional cross-check with the previous archive:
  python check_union.py /path/to/chess_material_28_proof.zip
Requires g++/C++17 and the old archive; replays all 684,045 games and computes
an exact set union, not a sum. This can take several minutes.
