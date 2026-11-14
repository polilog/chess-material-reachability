# Compact constructive material-profile proofs, next step

This package contains three finite chess certificates and a combinatorial reduction. It does **not** prove that all 29,045,304 Tomic candidates are reachable. The larger prior corpus is not needed to check these certificates.

## Verify

Run `python3 verify_all.py`. All files use Python 3 and the standard library. The verifier checks the actual histories from the ordinary initial board, the local branches, independent deletions, repetition/75-move limits, and a mating continuation. It then counts families using polynomial dynamic programming and inclusion-exclusion, rather than enumerating the two-sided material profiles.

- `promotion_deletion/`: previously obtained 26-piece master with 14 four-way choices, 22 commuting deletions; 733,950 unordered pawnless profiles with both helper knights.
- `optional_master/`: new 25-piece master with 9 four-way choices and 2 five-way choices (P,N,B,R,Q), 21 commuting deletions; 1,143,269 unordered profiles with both helper knights. Generate a concrete game with `python3 optional_master/generate.py '4,1,2,2,4' '0,2,2,0,6'` (P,N,B,R,Q, including the helpers).
- `doubled_pair/`: a reachable six-piece position with white pawns e4 and e6. A pair module gives all 21 local branches: no promotion, front pawn alone promoted to any of four types, or both promoted to any types. Each branch ends with the same color occupancy and side to move; there is a common deletion and mating continuation. `python3 doubled_pair/verify.py 3 2` also prints one UCI game with front bishop/back knight (piece codes N=2,B=3,R=4,Q=5; 0 means stay pawn).
- `count_and_reduction.py`: counts the union of the two large families and the number of master classes. The union consists of 1,672,566 unordered profiles, of which 938,616 contain at least one pawn. This is NOT a count of additions to the earlier large corpus.

## New mathematical reduction (conditional on constructing the remaining masters)

Let `o=(2,2,2,1)` be the original N,B,R,Q counts per color; let `t` denote the target nonpawn counts, `p` target pawns, and `m=1+p+sum(t)` total pieces of that color. Kings are implicit and mandatory. The individual-pawn resource constraint is

    p + sum(max(0,t_i-o_i)) <= 8.

Hence the number of original nonpawn matches `a=sum(min(t_i,o_i))` satisfies `a >= m-9`.

**Definition of a master.** A universal master for an initial loss vector has a legal history with exactly those original losses, allows each surviving pawn (or an equivalent indistinguishable block of pawns) to realize arbitrary aggregate counts of P,N,B,R,Q, and can subsequently delete arbitrary surplus material while reaching the intended terminal/nonterminal target without premature game termination. This includes removal of helpers when required. The existing two large certificates are partial masters: both helpers remain, and some promotions are compulsory.

### All targets with N <= 24

If both colors have at least nine pieces, set `c_i=16-m_i`. Then `0<=c_i<=7` and `c_W+c_B>=8`. Choose `e_W+e_B=8` with `0<=e_i<=c_i`. All eight initial losses can be nonpawns. For each side retain `r_i=7-e_i` original nonpawns, including at least `m_i-9` matches to the target. This is possible since `r_i>=m_i-9` and `a_i>=m_i-9`. The target requires at most eight remaining pieces of that color beyond the matched fixed material, so the eight pawn resources can supply them; delete unmatched surplus material. The number of such eight-nonpawn-loss classes, up to color swap, is `( [x^8]F(x)^2 + [x^4]F(x) ) / 2 = 248`, for `F(x)=(1+x+x^2)^3(1+x)`.

If either side has at most eight pieces, one special master suffices: the larger side has all original material and eight flexible pawns; the smaller side has lost one pawn and six original nonpawns, retaining one original nonpawn (choose a knight) and seven flexible pawns. Seven flexible pawns alone can supply any <=7 nonking target pieces of that side; delete the original survivor if unnecessary. The larger side can supply any target satisfying its pawn-resource constraint. This master starts at 25 pieces, with a weighted loss cost of eight.

Thus **249 master classes suffice for all N<=24**, conditional on the required chess histories and flexible deletion/retention properties. No enumeration of target material profiles is needed. The earlier reduction to 1123 classes did not exploit replacing deliberately sacrificed original pieces with additional promotions.

### N=25

Let `d_i=8-p_i-sum(max(0,t_ij-o_j))` be the minimal-history original pawn loss count. If `d_W+d_B>=1`, choose one side `s` with `d_s>=1`; use exactly one pawn loss there, plus six nonpawn losses in total. Retain `m_s-8` matching original nonpawns on that side, and `m_other-9` on the other. These are nonnegative, <=7, and total 8. They are available because `a_s>=m_s-9+d_s` and `a_other>=m_other-9`. The remaining seven/eight pawn resources reproduce the rest. Thus 483 one-pawn-loss master classes suffice. If the minimal history has no pawn losses, the Tomic constraint gives at most seven promotions per side, and at least one pawn per side is retained. Seven nonpawn losses, seven flexible pawns and one permanently retained pawn per color suffice; there are 267 such classes. The special master above is already one of the 483 classes. The conditional bound for all N<=25 is therefore 248+483+267=998 classes.

### Abstract two-file nonpawn-capture geometry

Only two types of two-capture modules are needed for the 248 classes, up to color swap. Capture-square color (needed for bishop delivery) is not an obstruction in the abstract pawn model:

- Two captures by white: on adjacent files a,b prepare white A at a4 or a5, white B at b2 or b3, black B at b4. White A captures a nonpawn on b5 or b6. Then black A goes down its now-empty file to a2 or a3 (the rank of white B). White B captures another nonpawn on a3 or a4. The two white pawns are now above the two black pawns, one white and one black on each file. Both captures can independently be assigned either square color. Actual sacrifice delivery, waiting moves and king safety must still be realized.
- One capture by each: white A moves from a2 or a3 and captures on b3 or b4; black B moves from b7 or b6 and captures on a6 or a5. Keep white B at b2 and black A at a7. The two white pawns now occupy b, the two black pawns occupy a. Both capture-square colors are flexible. The new doubled-pawn module deals with choosing zero/one/two promotions once a suitable workspace is available.

For the full chess proof, it remains to construct the 249 universal masters, or a reusable delivery/storage invariant that implies them. The six-piece pair module is not a proof that it can be embedded unchanged into every crowded 24-piece arrangement. In particular, placing an arbitrary five-way wildcard on every file makes an entirely unshielded king impossible: each wildcard could be a queen. Guarded king safety or different storage geometry is required. The package makes this remaining limitation explicit.
