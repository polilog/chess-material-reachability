# Constructive proof examples and recovered witnesses

The full theorem depends on the standalone replay of the certificate streams in `data/` and the small terminal witnesses. The following small certificates are included to make the constructive techniques understandable and individually reproducible.

- `independent_promotions/chess25_universal/`: one 25-piece template with 15 independent promotions, covering 19,800 final profiles and 62,106 including promotion prefixes. Run `python3 verify.py` inside that directory.
- `no_promotion_deletion/chess_math_proof/`: a constructive certificate for all 118,341 profiles whose counts do not exceed the starting material, with service-knight deletion routes and terminal cases. Run `python3 verify.py` there.
- `promotion_deletion/`: 14 independent promotion choices combined with 22 independent deletion operations. Run `python3 verify.py` in that directory.
- `optional_and_doubled_pawns/`: optional pawn/promotion choices, a local doubled-pawn module, and historical conditional reduction arguments. Run `python3 verify_all.py` in that directory.

The miniature examples are illustrative independent evidence. Their experimental reduction proposals are historical and conditional: they are not used as lemmas establishing the final 29,045,304-profile equality. Do not sum their family sizes as new profiles, since their coverage overlaps.
