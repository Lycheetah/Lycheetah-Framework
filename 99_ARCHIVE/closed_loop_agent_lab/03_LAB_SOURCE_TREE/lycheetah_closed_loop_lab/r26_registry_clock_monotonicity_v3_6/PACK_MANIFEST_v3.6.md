# Pack Manifest v3.6

## Release

- **Name:** Registry Clock Monotonicity
- **Iteration:** R26 / v3.6
- **Baseline commit observed in source pin:** `8ae1b367dcf09997e82ce66f9ad5d30ff36e5d65`
- **Scope:** Local reference service/tests only. No upstream file modification.

## Main files

- `spent_nonce_registry.py` — v3.6 external spent-challenge registry simulator with HMAC-authenticated persistent clock floor, fixed replay window, request-ID pruning and guard triggers.
- `remote_monotonic_verifier.py` — retained v3.5 composition of quorum freshness verification and remote one-use nonce consumption.
- `test_registry_clock_monotonicity.py` — 11 new focused adversarial tests.
- `test_remote_monotonic_verifier.py`, `test_durable_freshness_verifier.py`, `test_checkpoint_witness_quorum.py` — retained upstream-independent regression suites.
- `API_CONTRACT_v3.6.md`, `THREAT_MODEL_v3.6.md`, `CLOCK_ROLLBACK_RECOVERY_RUNBOOK.md` — contract, threat model and fail-closed operational recovery.
- `SCENARIO_MATRIX_v3.6.json` — machine-readable scenario definitions.
- `run_v3_6_tests.sh` — reproducible test/compilation/source-pin/demo runner.
- `run_v3_6_tests_final.log`, `combined_tests_v3.6.log`, `source_pin_verify_v3.5.log`, `python_compile_v3.6.log`, `baseline_reproduction_v3.6.log`, `demo_durable_freshness_v3.6.log`, `demo_external_registry_v3.6.log` — execution logs.

## Verification

- 11 focused new tests passed.
- 82 methods passed in combined retained + new suite.
- Retained source pins passed.
- Python compile passed.
- Five frozen v3.2 baseline counterexamples reproduced intentionally.
- Local freshness and external-registry demos passed.
- ZIP CRC and SHA-256 checks are in the delivery files outside this directory.

## Deliberate limitations

The service still uses local SQLite. Its high-water mark moves backward if the registry DB is restored to an old valid snapshot; coordinated rollback of primary and registry stores remains possible. Challenge rows are retained append-only, request replay-cache memory is window-bounded by traffic but no hard rate limit is included, and privileged host/database administrators remain outside the defense provided by application-level triggers. No live HTTP host, Stripe, cloud service, upstream repo or production key was used.
