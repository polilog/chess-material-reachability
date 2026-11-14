# Compact constructive proof: all original-limit chess material profiles

This certificate establishes reachability of all 118,341 unordered material profiles with at most 8 pawns, 2 knights, 2 bishops, 2 rooks, 1 queen and exactly 1 king per color, without a promotion in any target history. It is a proof about material counts, not about arbitrary board arrangements. It does not establish reachability of all promotion-rich profiles.

Run `python3 verify.py` (Python standard library only). The verifier checks a 347-ply no-capture/no-promotion prefix, 28 symbolic deletion modules, two helper-sacrifice modules and their reversals, a mating continuation with two knights, 28 one-helper clearing modules, six robust mating continuations and six all-bishop exceptions. It does not enumerate 2^28 subsets or 118,341 profiles. Stationary optional pieces can be present or absent: the verifier checks movement with every possible obstacle present, and safety with optional blockers removed, adding potential optional attackers one at a time. The removal operations restore the original geometry, other than the captured piece. A capture separates repetitions by material count; each quiet phase repeats a position at most twice, giving a bound of four occurrences per material count in target histories. The maximum quiet interval is far below 150 halfmoves. Legal mating alternatives rule out dead positions before the target; the target may itself be terminal. The six bishop-only target histories also have explicit mate alternatives sharing their prefix to the final capture.

The two storage knights are white d1 and black e4; wait squares c3 and d2. The kings are h1 and a8. For profiles with no knights on either side and at least one pawn, rook or queen, keep the representative piece of that type listed in the certificate. First remove the other color's helper, then the witness color's helper. Before the last sacrifice the remaining helper can clear the opposing pieces and one of the six mating continuations works. If only bishops and kings remain in the target, use one of the six explicit cases.

To generate an actual UCI history for any one profile:

```
python3 generate.py '8,2,2,2,1' '3,0,0,1,0'
```

Arguments are P,N,B,R,Q counts, kings implicit. Color interchange is identified, and the six bishop cases may return the swapped orientation.

Files: `proof.json` (local certificates and six special histories), `rules.py` (64-square chess rules used in the independent verifier), `verify.py`, `generate.py`, `verification.log`, `example.uci`, `example_KvK.uci`.
