# Results and audit records

| File | Meaning |
|---|---|
| `expected.tsv` | Expected candidate and coverage table for each total piece count. |
| `verified_summary.tsv` | Recorded successful compact-edition replay summary. |
| `final_replay.log`, `final_verification_marker.json` | Fresh complete verification of the integrated 1.0.0 draft; marker records the matching manifest and summary hashes. |
| `final_quick_checks.log`, `final_explorer_smoke.log`, `final_browser_checks.log` | Fresh quick-check suite, witness retrieval tests and Chromium UI checks (using a bridge to the live local HTTP server) for the integrated draft. |
| `compact_replay.log` | Recorded complete replay of the consolidated inputs. |
| `corpus_counts.json` | Number of concrete, template and storage records. |
| `environment.txt` | Reference Linux/Python/compiler/NumPy/zstd versions. |
| `explorer_v2_smoke.log` | Recorded 10 concrete witness retrieval checks for Explorer v2, including invalid-input rejection. |
| `cold_replay.log`, `first_cold_replay*.tsv`, `orchestration_*`, `previous_final_replay.log`, `historical_publication_manifest.json` | Historical audit records from older packaging/coverage iterations; not proof inputs. |

The historical logs intentionally include earlier failures and corrections. They are not the final result. The consolidated proof does not read those logs or saved coverage states; reproduce it with `python verify.py --work replay-fresh`. The exact-set equality test is the primary verification; the expected table is a regression check.
