# Pack Manifest v3.3 — Quorum Verifier Hardening

## Included
- `checkpoint_witness_quorum.py` — v3.3 strict verifier and witness guard validation.
- `test_checkpoint_witness_quorum.py` — 37 focused tests; 6 new tests compared with v3.2.
- `reproduce_v3_2_findings.py` plus `baseline_v3_2/` — executable before/after reproduction against frozen v3.2 sources.
- `remote_anchor_http.py` — pinned primary-record verifier dependency.
- `demo_quorum_v3_3.py` — no-network two-checkpoint demo.
- `API_CONTRACT_v3.3.md`, `THREAT_MODEL_v3.3.md`, `BASELINE_FINDINGS_v3.3.md`, `RESULTS_v3.3.md`, `SCENARIO_MATRIX_v3.3.json`, `SOURCES_v3.3.md`, `SOURCE_PIN_v3.3.json`.
- Focused and retained historical test logs.

## Verification
- v3.3 focused: 37 passed.
- Frozen v3.2 acceptance reproductions: 5 cases accepted by baseline; corresponding v3.3 negative tests reject the classes.
- Retained v3.1 protocol groups: 33 + 14 + 14 + 13 passed in separate processes.
- Aggregate current + retained: 111 passing test methods across five invocations; not a monolithic run or upstream CI.
- Demo: PASS; no external network calls.
- `cryptography` Ed25519 key operations only; no hosted anchor/Stripe API calls and no real refunds.

## Scope limits
No upstream source files changed. `SQLiteCASGuard` is a local reference adapter, not a production non-rollbackable guard. Distinct public keys do not guarantee independent control domains.
