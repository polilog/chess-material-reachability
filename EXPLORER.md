# Chess Material Explorer

This is the integrated interactive witness explorer for the complete certificate repository. It is a consumer of verified certificate indexes, not part of the mathematical proof itself.

## Run locally

The files are already included. From the repository root, follow the [installation instructions](README.md#installation). On macOS:

```sh
brew install zstd
python3 -m pip install -r requirements.txt
python3 explorer.py
```

Open http://127.0.0.1:8765 if your browser does not open automatically. The first launch runs the original cold verifier if a completed `replay/` directory does not exist. This can take minutes or longer depending on the machine and uses additional disk space for decompressed data and indexes. Subsequent searches reuse the replay outputs; lookup times depend on the certificate and hardware. If you already ran `verify.py --work some_directory`, use `python3 explorer.py --replay some_directory`. The server listens only on localhost.

Choose the total piece count (1–16, including the fixed king) for each side. Drag pieces into slots or click palette pieces to fill empty slots. Clicking a filled slot clears it; dragging onto it replaces it. Every edit is checked for the existence of a complete admissible composition, including the coupled capture/promotion constraints. Search is enabled only when all slots are filled. The app checks Tomic's criterion, selects a certificate, reconstructs the concrete witness, replays it from the standard initial position, and jumps to the material milestone. All matching positions, including the initial position when relevant, are highlighted in the move list and timeline. Jump between matches, use the slider, arrow keys or playback to step through the entire game, flip the board, or download a standard SAN PGN. The loaded game retains its own target while you edit the next query. The interface works offline after the dependencies have been installed.

Command line example (P,N,B,R,Q order):

```sh
python3 explorer.py --replay replay --query 0,2,2,2,9 0,2,2,2,5 > witness.pgn
```

### Scope and implementation

The published compact proof is for material classes modulo color interchange. The explorer first tries witnesses in the requested orientation. Where necessary it tries a legal color-reversal tempo construction, replaying it from the orthodox initial position; if this fails, it clearly labels the reversed-color witness. It never starts a game from a modified initial position.

The lookup uses the original verifier's emitted family indexes, not the binary coverage matrix alone. `explorer/lookup.cpp` matches fixed material and the independent promotion domains. `engine.py` reconstructs promotion assignments via a small exact dynamic program, expands the symbolic moves, or uses the verified deletion and helper-sacrifice routes. Ordinary witnesses use exactly the alternate promotion domains defined by the original symbolic checker. All returned concrete moves are replayed, and mating witnesses are checked to end in mate. Terminal target branches rely on the original verifier's alternative mating continuation. The displayed witness is not necessarily a shortest proof game.

The coverage proof and the viewer are distinct: full material coverage follows from the original replay. The viewer is a witness retrieval and reconstruction utility, not a second exhaustive test of all 29 million queries. A lookup failure is reported as an implementation error, never as proof of impossibility. No external APIs, hosted services, engines, or JavaScript libraries are required. The local Python backend is necessary for on-demand certificate expansion; a static GitHub Pages deployment by itself cannot serve this version.

## Files

- `explorer.py` — local HTTP server and CLI
- `explorer/index.html` — responsive material selector and game viewer
- `explorer/engine.py` — matching, expansion, concrete replay and PGN export
- `explorer/lookup.cpp` — small compiled family matcher
- `explorer/storage_details.py` — original storage verifier with an additional return value for the verified move routes

The original proof data remain unchanged. Developed with substantial assistance from OpenAI ChatGPT (GPT-6), consistent with the main repository's `AI_ASSISTANCE.md`.
