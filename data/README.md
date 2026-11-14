# Standalone certificate data

This directory contains the complete input data for the consolidated verifier, in nine losslessly compressed streams:

- `games_0.uci.zst` through `games_3.uci.zst`: one concrete UCI move sequence per line. The checker also derives sound families by allowing changes of promoted types when their moves and attacks permit it.
- `templates_0.txt.zst` through `templates_3.txt.zst`: parameterized certificate blocks in `BEGIN ... END` format.
- `storage_0.txt.zst`: certificates for independent deletion operations.
- `manifest.json`: SHA-256 digests and compressed lengths for all nine files.

No historical archives, search programs, cache files, or saved coverage matrices are required. The small terminal-target witnesses are included in `../examples/small/`. Run `python3 verify.py` from the repository root; decompression and verification are automatic. For inspection only, `zstd -dc data/templates_0.txt.zst` prints a raw certificate stream.

The selected corpus is sufficient, not globally minimum. Exact duplicates were removed and certificates were retained when previously verified family outputs indicated new coverage. Those outputs were used only to select a subset, not to prove it: the standalone replay rechecks every retained record from moves and rebuilds all coverage. The original research archive chain is superseded for reproduction purposes by this release.

## License

Original certificate data is dedicated to the public domain under [CC0 1.0 Universal](../LICENSES/CC0-1.0.txt). See [license scope](../LICENSE.md) for details.
