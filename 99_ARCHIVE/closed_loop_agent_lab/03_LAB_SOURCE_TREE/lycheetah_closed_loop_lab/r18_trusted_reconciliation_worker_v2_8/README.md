# Trusted Reconciliation Worker v2.8

A read-only worker that binds a verified webhook queue job to the authenticated Lycheetah operation ledger and current provider refund state.

## Files
- `stripe_webhook_inbox.py` — authenticated inbox and transactional reconciliation queue; enforces that `DONE` has matching terminal ledger evidence.
- `operation_ledger.py` — minimized, HMAC-authenticated operation-state ledger.
- `reconciliation_worker.py` — read-only provider reconciliation worker.
- `webhook_http_receiver.py` — local HTTP webhook receiver used by smoke/test path.
- `test_trusted_reconciliation_worker.py` — worker and invariant tests.
- `test_transactional_reconciliation_queue.py` — queue, migration, account and integrity tests.
- `test_stripe_webhook_inbox.py` — inbox tests.
- `test_webhook_http_receiver.py` — HTTP receive tests.
- `run_worker_tests_v2_8.py` — focused suite runner.
- `run_worker_smoke.py` — loopback-only integration smoke.

## Run

```bash
python -W error::ResourceWarning run_worker_tests_v2_8.py
python -W error::ResourceWarning run_worker_smoke.py
```

This worker does not send POST requests or create refunds. Configure a real provider client only after implementing and reviewing its read-only `retrieve_refund` adapter, pinning account/mode/API version and testing the exact provider contract in an authorized test environment.

See `TRUSTED_RECONCILIATION_WORKER_DESIGN_v2.8.md`, `PROVIDER_CONTRACT_SOURCES_v2.8.md`, and `RESULTS_v2.8.md`.
