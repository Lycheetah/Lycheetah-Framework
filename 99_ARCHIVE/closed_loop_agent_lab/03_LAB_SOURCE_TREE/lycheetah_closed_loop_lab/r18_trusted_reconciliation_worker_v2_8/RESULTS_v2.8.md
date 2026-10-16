# Verification Results v2.8

## Final focused run

Command:

```bash
python -W error::ResourceWarning run_worker_tests_v2_8.py
```

Result after legacy-`DONE` migration hardening: **121 tests passed**. The latest log is `focused_tests_v2.8.log`.

Syntax compilation of `stripe_webhook_inbox.py`, `operation_ledger.py`, `reconciliation_worker.py`, `webhook_http_receiver.py`, `run_worker_tests_v2_8.py`, and `run_worker_smoke.py` passed under `python -W error::ResourceWarning -m py_compile`.

## Loopback HTTP integration smoke

`smoke_result_v2.8.json` records:

- HTTP status 200.
- Webhook inbox action `INGESTED`.
- Current fake-provider status `succeeded` read through the worker interface.
- Minimized operation ledger state `PROVIDER_SUCCEEDED`.
- Queue state `DONE` only after matching authenticated terminal ledger evidence had been recorded.
- `hosted_provider_calls = 0` and `real_refunds_created = 0`.

## Retained regression groups

Executed as separate isolated test runs with ResourceWarnings treated as errors:

| Suite | Tests | Result |
|---|---:|---|
| R10 evidence lease v2.0 | 49 | PASS |
| R11 provider contract v2.1 | 29 | PASS |
| R12 Stripe refund contract v2.2 | 39 | PASS |
| R15 Stripe privacy/state hardening v2.5 | 85 | PASS |
| R16/R17/R18 webhook worker path v2.8 | 121 | PASS |
| **Total across separate invocations** | **323** | **PASS** |

This is an aggregate count from separate commands, not one monolithic runner invocation. Earlier historical runner attempts have sometimes hit a harness timeout; see archived run logs and repeat within CI before promotion.

## Migration regression

An old queue database can contain a `DONE` job written before v2.8 enforced authenticated terminal operation evidence. On opening the inbox, each prior `DONE` row is checked. If no matching authenticated terminal record can justify it, the job is demoted to `MANUAL`, with the sanitized migration reason `legacy-done-unproven`. A job with a matching terminal record remains `DONE`. A tampered ledger record is a fail-closed integrity error rather than a reason to trust or silently rewrite the row.

## What this does not prove

- No hosted Stripe requests were made; the provider in smoke is a local loopback fake.
- No real refund was created.
- No upstream GitHub source file, branch, or PR was changed.
- Full upstream Lycheetah test suite and CI were not run.
- The tests do not prove atomicity between a hosted Stripe state transition and local database state; the worker only stores a point-in-time read.
- HMAC does not provide confidentiality or defend against whole-database rollback/deletion or key compromise.

Status: **local reference implementation verified to its stated test boundary; not production-certified.**
