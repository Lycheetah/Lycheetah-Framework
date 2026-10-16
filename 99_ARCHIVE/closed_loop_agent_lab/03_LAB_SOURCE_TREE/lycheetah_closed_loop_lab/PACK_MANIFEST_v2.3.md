# Pack Manifest — v2.3

## Full pack

`lycheetah_closed_loop_agent_lab_v2.3.zip` retains the prior closed-loop lab research and adds `r13_stripe_testmode_http_adapter_v2_3/`.

## Standalone adapter kit

`lycheetah_stripe_testmode_http_adapter_v2.3.zip` contains only the R13 test-mode HTTP adapter, local provider simulator, test suite, runner, source documentation, results, and runbook.

## R13 directory contents

- `stripe_test_adapter.py` — HTTP adapter and HMAC-authenticated SQLite ledger
- `stripe_contract_simulator.py` — local-only Stripe-contract simulator
- `test_stripe_test_adapter.py` — 51 local HTTP/SQLite regression methods
- `run_complete_tests_v2_3.py` — combined v2.0–v2.3 test runner
- `run_local_smoke.py` — local simulator smoke scenario; no hosted network request
- `README.md`
- `STRIPE_TESTMODE_HTTP_ADAPTER_v2.3.md`
- `RESULTS_v2.3.md`
- `SOURCES_v2.3.md`
- `SCENARIO_MATRIX_v2.3.json`
- `test_output_v2.3.log`
- `combined_test_output_v2.3.log`
- `python_compile_v2.3.log`

## Key limitations

- Stripe hosted API and test mode were not contacted.
- No refund was created.
- No Stripe credentials were supplied.
- No Lycheetah upstream files, branch, or PR changed.
- Full upstream Lycheetah CI was not run.
- Local HMAC protects rows only while its key is secret and uncompromised.
- Reference SQLite use is single-host; remote authorization/evidence is not atomically coupled to Stripe commit.
