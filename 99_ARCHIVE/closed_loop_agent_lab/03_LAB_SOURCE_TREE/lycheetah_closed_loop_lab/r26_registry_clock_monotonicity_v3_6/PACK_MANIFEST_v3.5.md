# Pack Manifest v3.5

## Runtime code
- `spent_nonce_registry.py`: authenticated local HTTP registry simulator, atomic spent nonce state, service-side row HMAC, signed receipts, client anti-replay and response validation.
- `remote_monotonic_verifier.py`: adapter from retained v3.4 quorum verifier to the independent registry.
- `durable_freshness_verifier.py`: retained v3.4 primary ledger.
- `checkpoint_witness_quorum.py`, `remote_anchor_http.py`: retained quorum and signed-anchor protocol.

## Tests
- `test_remote_monotonic_verifier.py`: 15 focused integration cases.
- `test_checkpoint_witness_quorum.py`: 37 retained quorum cases.
- `test_durable_freshness_verifier.py`: 19 retained challenge lifecycle cases.
- `baseline_v3_2/` plus `reproduce_v3_2_findings.py`: frozen baseline and five historical acceptance demonstrations.

## Results and reproducibility
- `run_v3_5_tests.sh`, Python compile/test outputs, current-chain demo, scenario matrix, source pins and this manifest.
- 71 combined test methods pass. Tests include one deliberately successful local rollback negative control and one deliberately successful coordinated rollback negative control in addition to defensive regressions. Those controls are documented limitations, not defensive successes.
- No external service calls; no upstream changes; not production-certified.
