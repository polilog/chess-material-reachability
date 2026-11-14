# Certificate format and verification contract

## Material encoding

Each side is represented by counts `(P,N,B,R,Q)`, with one king implicit. A material family string begins with five lowercase letters: `a` means zero, `b` one, and so on. Each trailing symbol encodes a choice domain. For a symbol with ASCII code `65+m`, the nonzero bits of `m` correspond to N, B, R, Q in bits 0–3. `P` is mask 15 (all four promotions), while `Z` denotes the optional pawn-or-promotion domain. For example, `abcabP` represents `(0,1,2,0,1)` plus one arbitrary promoted piece. A pair is `side1:side2`, with its strings sorted. The coverage code expands each side independently and identifies color interchange at the material level. The sorting convention of the material relation is based on actual side profiles, not the ordering of strings.

Ordinary records are one game per line, UCI coordinate notation (e.g. `e2e4 e7e5`, `e7e8q` for promotion). All game evidence starts from the orthodox initial position. Raw historical data may include rejected exploratory records; the checker is the only authority for acceptance.

## Symbolic record structure

A block is bounded by `BEGIN ...` and `END`. The header carries research identifiers and optional White/Black type masks. The first payload line is a concrete setup sequence. Its material count must be one of the accepted setup sizes (24–27) and its board must be free of unknown pieces. The rest consists of operations:

| Operation | Meaning |
|---|---|
| `MOVE m` | A common move by a fixed piece; no promotion during the symbolic core unless encoded explicitly |
| `PROM fromto` | Check all allowed promotion types, then store a wildcard at the common resulting location |
| `PARK ...` | Type-specific short moves, with the same geometry and turn at all branch endpoints |
| `SHIFT square ...` | Relocate a previously promoted unknown by temporarily resolving its type, then rejoin |
| `OPTION square ...` | Five local branches, leaving a pawn or any promotion type on the same square |
| `REVEAL square type` | Specialize a previous unknown; discard unqualified earlier coverage |
| `CAP m` | Capture during the symbolic core by a fixed piece; the victim cannot be a king |
| `SUFFIX` | Common sequence of verified moves ending in a mate valid for every retained assignment |
| `TARGET m` | Alternative final capture from a prefix with a separately verified common mating suffix; a target may be terminal |
| `STORAGE ...`, `MATE ...` | Storage geometry with two service knights and waiting squares, followed by a core mating continuation; verified by the storage checker |

`src/verify_special.py`, `src/verify_branch.py`, and `src/storage_prefix.py` define the precise executable syntax, including branch lengths and endpoint checks. The human-readable description is not a replacement for their checks.

## Why branch compression is sound

A wildcard is not a fairy-chess piece that can move as both a queen and a knight. Its union of attacks is used only as a conservative *obstacle* to legality. The actual type is resolved when its own move must be checked; the resulting occupancy, colors, and side to move must agree at the rejoin. Because any choice's attacks are a subset of the union, a common move accepted by the conservative model is legal under every assignment. For common checkmate, use the reverse conservatism: require a check that is present for all assignments, then rule out every potential defender move under an underapproximation of enemy attacks. No castling escape from check is possible; en passant is ruled out in symbolic mate tests by the final-move restriction. An optional pawn stays on rank six/three and has no special double-push or en passant escape from those ranks.

The concrete generalized-game checker tracks promoted-piece identities. It restricts each alternate type by the promoted piece's moves and by the requirement that it not attack the moving side's king after every move. It fixes the type of surviving promoted pieces at the terminal mate. Thus all variations of captured promoted pieces in the retained domains lead to the same final mating board. The checker uses a conservative repetition signature; type changes cannot invalidate its repetition bound. It does not infer validity of a type substitution without checking geometry and attacks.

## Draw rules and terminal states

The FIDE Laws require no move after an automatic terminal position. A complete verified mating continuation proves all positions on its path are non-dead. For a terminal target, an alternate legal path from the immediately preceding position to a verified mate proves that the preceding position is not dead; then the target move itself is legal. Repetition is conservatively bounded by counting signatures at least as coarse as actual equality. The 75-move counter resets on pawn moves and captures. The verifiers reject witnesses conservatively if a boundary is uncertain; they are not intended to recognize all legal histories. The mate on the final move is checked separately. In storage certificates, each capture separates material counts, so repetition intervals across captures cannot contain an exact position in both intervals.

## Storage coverage

A storage verifier checks the common prefix and full-board local capture routes, verifies that stationary pieces cannot attack an enemy king on an empty board, and establishes repetition and quiet-move bounds for concatenations of the modules. It generates a compact record with the fixed counts `a,b`, wildcard counts `w,z`, and the explicitly supported final single-helper sacrifices `sac`. The main coverage checker uses the following safe subfamily: for fixed material `a`, `w` independent nonpawn choices, and a required service knight, a target is covered if its pawn count is at most the fixed pawn count, and the sum of nonpawn deficits beyond `a` is at most `w`, with at least one knight. An explicitly certified helper sacrifice reduces the relevant fixed count and relaxes that side's knight requirement. Deletion rectangles are credited only for sizes 9–23 in the full replay, a conservative restriction matching the original verification. There is no blanket claim that both service knights can be deleted independently in all these geometries.

## Coverage and proof obligations

1. Every accepted raw record must establish reachability from the initial board, respecting the rule-set above.
2. Every emitted family must be a subset of the material profiles supported by that record, including any specialization.
3. The aggregator must union exact family sets and identify color interchange correctly. It rejects coverage outside the candidate relation.
4. The final bitset comparison must find no missing candidate profile. A matching total without the subset check is insufficient.

The standalone `verify.py` performs these operations from the consolidated certificate streams in `data/`, without cached family outputs or historical archives. The small examples in `proof/` are supplementary; the terminal witnesses in `examples/small/` are used by the full replay.
