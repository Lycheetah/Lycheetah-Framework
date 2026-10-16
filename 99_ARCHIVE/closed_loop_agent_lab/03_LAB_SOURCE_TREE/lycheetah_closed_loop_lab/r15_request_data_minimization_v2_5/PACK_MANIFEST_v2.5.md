# Pack Manifest — v2.5

- `stripe_test_adapter.py` — test-mode-only HTTP refund reference client, SQLite operation ledger, authenticated state and response, privacy-minimized metadata.
- `stripe_contract_simulator.py` — local HTTP simulator with response-loss and adversarial response hooks.
- `test_stripe_test_adapter.py` — 81 focused tests.
- `run_complete_tests_v2_5.py` — combined retained R10-R12 and R15 regression runner.
- `run_local_smoke.py` — one-effect/two-POST lost-response recovery smoke.
- `PRIVACY_DATA_MINIMIZATION_AUDIT_v2.5.md` — scope and threat model.
- `STRIPE_TESTMODE_HTTP_ADAPTER_v2.5.md` — adapter contract and boundaries.
- `SOURCE_LOG_v2.5.md` — official Stripe API documentation reviewed.
- `SCENARIO_MATRIX_v2.5.json` — machine-readable focused scenarios.
- `RESULTS_v2.5.md`, `focused_tests_v2.5.log`, `combined_tests_v2.5.log`, `local_smoke_v2.5.json`, `python_compile_v2.5.log` — reproducible test evidence.

## Verification summary

81/81 focused tests and 198/198 combined methods pass. Local loopback smoke and compilation pass. No hosted API calls or real refunds. No upstream source change and no production certification.
