# Pack Manifest v2.8

This folder is the standalone source pack for the trusted reconciliation worker. It intentionally contains no Stripe secret, hosted API result, or live refund identifier.

Core implementation:
- `stripe_webhook_inbox.py`
- `operation_ledger.py`
- `reconciliation_worker.py`
- `webhook_http_receiver.py`

Tests and repeatability:
- `test_stripe_webhook_inbox.py`
- `test_webhook_http_receiver.py`
- `test_transactional_reconciliation_queue.py`
- `test_trusted_reconciliation_worker.py`
- `run_worker_tests_v2_8.py`
- `run_worker_smoke.py`
- `focused_tests_v2.8.log`
- `smoke_result_v2.8.json`

Design, provenance and limitations:
- `TRUSTED_RECONCILIATION_WORKER_DESIGN_v2.8.md`
- `PROVIDER_CONTRACT_SOURCES_v2.8.md`
- `RESULTS_v2.8.md`
- `SOURCE_PIN_v2.8.json`

Historical group logs under this directory record the separately executed R10/R11/R12/R15 test groups. Their combined count with the 121-test R18 suite is 323.
