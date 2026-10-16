# Pack Manifest v3.4 — Durable Freshness Challenge Lifecycle

## Core
- `durable_freshness_verifier.py`: persisted one-use challenge state, policy fingerprint, HMAC row authentication, strict schema/type checks, current-chain verification, and atomic consumption.
- `checkpoint_witness_quorum.py`: retained v3.3 quorum implementation.
- `remote_anchor_http.py`: retained source-pinned primary signed-record verifier.

## Tests and reproduction
- `test_checkpoint_witness_quorum.py`: 37 retained v3.3 test methods.
- `test_durable_freshness_verifier.py`: 19 new lifecycle test methods including one intentional snapshot-rollback negative control.
- `baseline_v3_2/`: frozen historical verifier used by `reproduce_v3_2_findings.py`.
- `run_v3_4_tests.sh`, `focused_tests_v3.4.log`, `python_compile_v3.4.log`, `demo_durable_freshness_v3.4.json`, `baseline_v3_2_reproduction_v3.4.log`.

## Docs
- `BASELINE_FINDINGS_v3.4.md`
- `API_CONTRACT_v3.4.md`
- `THREAT_MODEL_v3.4.md`
- `RESULTS_v3.4.md`
- `SOURCES_v3.4.md`
- `SOURCE_PIN_v3.4.json`
- `SCENARIO_MATRIX_v3.4.json`
- `CHANGELOG_v3.4.md`
- `SOURCE_SHA256SUMS_v3.4.txt`

## Verification
- 56 combined test methods passed in one local run; one is a deliberate positive assertion of the whole-ledger rollback limitation.
- Five previous v3.2 baseline acceptance cases were re-executed and reproduced.
- Current-chain demo passed and showed same-challenge replay rejected.
- No hosted API calls, real refunds, upstream branch, pull request or upstream source changes.
