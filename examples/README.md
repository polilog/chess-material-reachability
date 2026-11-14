# Examples

- `14_queens_game.pgn` — human-readable example with nine White queens and five Black queens at ply 258 (129...a1=Q+), 28 total pieces. The game continues to checkmate at ply 271. Open it in a PGN viewer or run `python src/check_example.py` from the root.
- `14_queens_game.uci` — the same concrete move sequence in coordinate notation; used by the Explorer for the initial-material preset as well.
- `small/` — 1,110 mating witnesses and 3 terminal-target variants used by the full verifier. The alternate mating prefixes certify non-dead positions prior to the terminal move. Run `python examples/small/check.py` from the root. See `small/README.txt` for details.

The games illustrate material reachability, not optimal chess or minimal-length proof games.
