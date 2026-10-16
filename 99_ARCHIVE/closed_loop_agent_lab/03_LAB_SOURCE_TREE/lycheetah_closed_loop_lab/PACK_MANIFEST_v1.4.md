# Research pack manifest — v1.4

The archive retains prior closed-loop, observer, authority-gate, recovery and parser experiments, and adds `r4_schema_parser_parity_v1_4/`.

## R4 contents

- `SCHEMA_PARSER_PARITY_AUDIT.md` — source observations, 20-row results, and limitations.
- `receipt.schema.json` — readable semantic reconstruction of the inspected upstream receipt schema; not a byte-for-byte archive.
- `receipt.schema.strict-candidate.json` — candidate with closed `finding` and `controlReference` definitions.
- `schema_parser_parity.py`, `run_differential.py`, `test_schema_parser_parity.py` — source-equivalent reproduction, matrix runner, and local tests.
- `differential_results.json`, `differential_run.log`, `test_output.txt`, `verification_summary.json` — machine-readable evidence and logs.
- `SCHEMA_CHANGE_PROPOSAL_v1.4.md` and `STRICT_PARSER_PATCH_DELTA_v1.4.md` — proposed upstream changes and compatibility decisions.
- `PROPOSED_UPSTREAM_TESTS_v1.4.py` — real-package integration tests for a clean checkout; not executed against upstream here.
- `VERIFICATION_RESULTS_v1.4.md` and `CHANGELOG_v1.4.md` — verification boundary and iteration history.

## Result summary

- 20 differential rows: source-equivalent parser accepts 18, current schema rejects 10, strict parser candidate rejects 20, strict schema candidate rejects 20.
- Eight original HMAC-sealed type mutations still verify after normalization to the same canonical body. This is not an HMAC break.
- Six local unit-test methods pass. Full upstream package, wheel and CI are not run.
- The GitHub branch-write attempt remained denied; no public files, branches, issues or pull requests were changed.

## Evidence status

Local source-equivalent fixture and proposed upstream change only. Not a production deployment finding and not a demonstrated unauthorized action.
