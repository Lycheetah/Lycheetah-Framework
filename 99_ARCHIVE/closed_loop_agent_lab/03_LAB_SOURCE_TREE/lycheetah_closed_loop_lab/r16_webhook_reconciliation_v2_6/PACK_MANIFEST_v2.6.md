# Pack manifest — v2.6

Research addition: authenticated Stripe webhook inbox and reconciliation hint for the local test-mode refund adapter.

Core runtime files:
- `stripe_webhook_inbox.py`
- `webhook_http_receiver.py`
- `stripe_test_adapter.py` (copied from local R15 reference for complete standalone kit)
- `stripe_contract_simulator.py` (local provider simulator, not hosted Stripe)

Tests and runners:
- `test_stripe_webhook_inbox.py`
- `test_webhook_http_receiver.py`
- `test_stripe_test_adapter.py` (retained R15 suite)
- `run_webhook_tests_v2_6.py`
- `run_complete_tests_v2_6.sh` and `run_complete_tests_v2_6.py` (complete archive runner)
- `run_local_smoke.py`

Evidence / docs:
- `STRIPE_WEBHOOK_INBOX_DESIGN_v2.6.md`
- `PROVIDER_CONTRACT_SOURCES_v2.6.md`
- `RESULTS_v2.6.md`
- `combined_tests_v2.6.log`
- `combined_group_1_r10_durable_outbox_evidence_lease.log` through `combined_group_5_r16_webhook_inbox_and_loopback_receiver.log`
- `focused_tests_v2.6.log`
- `smoke_output_v2.6.log`
- `smoke_v2.6.json`
- `results_v2.6.json`
- `python_compile_v2.6.log`
- `SOURCE_PIN_v2.6.json`
- `SHA256SUMS_v2.6.txt`

All secrets and event payloads used in tests are synthetic. No Stripe credentials, hosted API requests, live operations or upstream source edits are included.
