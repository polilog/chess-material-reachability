# Release notes

## 1.0.0 — initial release

- Integrates the complete compact certificate corpus, research manuscript and Explorer v2 into one repository.
- Adds a repository overview, source map, result index, GitHub publishing instructions, screenshot and separate manual full-replay CI.
- Verifier checks compressed lengths as well as hashes and writes a completion marker only after exact equality. The Explorer checks the summary/manifest provenance and reports invalid CLI input cleanly.
- Improves PGN material comments, including initial-position and swapped-color witnesses, and keyboard handling in the UI.
- Fixes the return value in the legacy C++ checker driver. The certificate data and mathematical criterion are unchanged.

- Finalizes author and citation metadata, adds MIT / CC0 1.0 / CC BY 4.0 licensing, and normalizes GitHub Markdown math.

## Consolidated certificate edition

The previous four historical archives are superseded by nine losslessly compressed certificate streams. The verifier reconstructs exact coverage without cached family lists. The selected corpus is sufficient but is not proven globally minimal. Historical audit logs retain the earlier packaging regressions and their corrections.
