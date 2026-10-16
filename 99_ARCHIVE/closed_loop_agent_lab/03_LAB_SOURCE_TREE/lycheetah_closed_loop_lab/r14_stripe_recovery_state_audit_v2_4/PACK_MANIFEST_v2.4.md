# Pack Manifest — Stripe Recovery State Audit v2.4

## Purpose

A source-informed local reference implementation for testing Stripe Refund operation recovery through a loopback HTTP simulator. It is not a production payment adapter or hosted Stripe conformance report.

## Core files

- `stripe_test_adapter.py` — HTTP adapter, durable SQLite operation ledger, HMAC row authentication, request binding, preflight and recovery logic.
- `stripe_contract_simulator.py` — local-only simulator with response-loss and malformed-contract fault hooks.
- `test_stripe_test_adapter.py` — 76 focused regression and adversarial test methods.
- `run_local_smoke.py` — local dropped-response recovery scenario.
- `run_complete_tests_v2_4.py` — combined regression runner. It expects retained v2.0–v2.2 folders from the complete lab archive.
- `RECOVERY_STATE_AUDIT_v2.4.md` — findings and fixes.
- `STRIPE_TESTMODE_HTTP_ADAPTER_v2.4.md` — adapter contract and limitations.
- `SOURCE_LOG_v2.4.md` — official Stripe documentation references reviewed for the contract.
- `SCENARIO_MATRIX_v2.4.json` — machine-readable test groups and aggregate counts.
- `RESULTS_v2.4.md` and `results_v2.4.json` — latest verification record.
- `focused_tests_v2.4.log`, `combined_tests_v2.4.log`, `local_smoke_v2.4.json`, `python_compile_v2.4.log` — captured successful local outputs.

## Latest verification

- Focused suite: 76/76 methods passed (latest run 7.104 seconds).
- Retained R10–R12 plus focused suite: 193/193 methods passed (16.401 seconds).
- Python compile: PASS.
- Loopback smoke: PASS, one simulated effect after two POST requests and response loss.
- Hosted Stripe API calls: 0.
- Real refunds created: 0.
- Upstream Lycheetah source changed: no.
- Full upstream CI: not run.

## Safety boundaries

HMAC protects record integrity, not confidentiality. Persisted provider responses are reduced to allow-listed recovery fields. The retrieved Charge/PaymentIntent is only a preflight snapshot; it does not atomically reserve the refundable balance with the later provider operation. The 23-hour retry cutoff is local policy, not a Stripe SLA. Unresolved states must reconcile instead of guessing.
