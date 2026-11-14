# Reproducibility and publication audit

## Standalone compact edition

The proof no longer requires the four historical archives. The supplied `data/` streams and `examples/small/` contain every input needed by `verify.py`. In selecting a smaller corpus we used previously checked family outputs only as an index: first credit storage/deletion families, then retain template and concrete records whose recorded families add coverage. Exact duplicates were removed. This is a sufficient-corpus selection heuristic, not a claim of minimality. The final validation replays the raw records independently of the selection indexes; no saved family list or coverage matrix is an input to the proof.

## Reproduce the full result

1. Install Python 3.10+, NumPy (`python3 -m pip install -r requirements.txt`), a C++17 compiler and `zstd`. On macOS, `brew install zstd` and, if necessary, `CXX=clang++ python3 verify.py`. Linux is the reference environment.
2. Run `python3 verify.py` from the repository root. The default work directory `replay/` must be new. You can choose `--work another-directory`. Do not run Python with `-O`.
3. The script checks SHA-256, decompresses the nine input streams, builds the checkers, validates concrete games and parameterized branches, validates storage/deletion certificates, and checks small terminal-target witnesses using their alternative mating prefixes. It reconstructs the candidate relation from the mathematical conditions and tests exact set equality. The run credits supported intermediate profiles as well as target profiles.
4. The output directory contains `VERIFIED.json` only after successful exact equality, plus freshly derived `.families`, `.storage.json`, checker logs, an intermediate coverage state, and `summary.tsv`. The final checker tests exact admissible row masks rather than merely comparing the totals. If coverage is incomplete, it saves the exact missing profiles and exits unsuccessfully. Failure to find a witness is never evidence of impossibility.
5. `results/expected.tsv` records the target table; `results/final_replay.log` records the fresh cold replay of the integrated 1.0.0 draft; `results/compact_replay.log` records the earlier standalone run.

## Earlier audit history (not required by this edition)

The initial full publication replay of the older archive chain left 82 candidates uncovered because the earlier standalone 26-piece archive had been reduced to preserve size-26 coverage only. Seven ordinary games and 28 templates were recovered from the original research records. After rechecking them, the full set equality held. A subsequent packaging regression caused a filename collision between the recovered game and template outputs, yielding ten missing profiles; assigning distinct output filenames fixed the error. The earlier audit logs are retained as historical records only. All needed records are incorporated in the consolidated streams, not supplied as additional dependencies.

## Independent review

Review necessity and the grouped counting formula separately from the software. Audit `src/verify_base.py`, `verify_special.py`, `verify_branch.py`, `symbolic_all.cpp`, and `verify_storage.py` for chess move legality, conservative attack and repetition handling, the common mating continuations, and the deletion invariant. Review `aggregate.cpp` and `finish_union.py` for the exact candidate relation and coverage union. Independent implementations and third-party reproduction are encouraged. The original Tomic messages have not been recovered; priority remains unresolved. No prior cached coverage or AI assertion is part of the trusted proof input.
