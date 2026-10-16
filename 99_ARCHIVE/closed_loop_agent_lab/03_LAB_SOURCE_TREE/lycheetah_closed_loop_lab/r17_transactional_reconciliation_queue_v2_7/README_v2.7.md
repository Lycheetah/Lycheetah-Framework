# Lycheetah R17 — Transactional Webhook-to-Reconciliation Queue v2.7

**Status:** local reference implementation and adversarial tests. Not production-certified. No hosted Stripe calls or real refunds were performed.

## Why this iteration exists

R16 authenticated and durably stored a minimal webhook event, then allowed a later caller to ask for a reconciliation hint. That created an operational gap: an endpoint could acknowledge an event while a process failed before durably registering follow-up work. R17 adds a transactional queue row in the same SQLite transaction as the inbox insert.

The core invariant is:

> For a newly accepted event, either its authenticated inbox row and its reconciliation job both commit, or neither commits.

The queue contains only a minimal, authenticated routing record. A webhook's reported refund status never marks a refund successful. A trusted worker must retrieve current provider state and durably record its own reconciliation decision before it acknowledges queue work.

## What's new

- **Atomic handoff:** `StripeWebhookInbox.ingest()` inserts the inbox row and queue job within the same transaction. A job-insert failure rolls back the inbox insert, so the HTTP receiver can return retryable `503` rather than acknowledge lost work.
- **Durable claims:** `claim_reconciliation_jobs()` takes a SQLite write lock, issues a random one-use claim token and stores only its SHA-256 digest.
- **Lease recovery:** expired worker leases requeue read-only reconciliation work. At eight attempts, work is routed to `MANUAL` instead of looping forever.
- **Bounded retries:** retry delays and sanitized reason codes are validated.
- **Account-scope binding:** when a database is reopened under a different platform/Connect account configuration, stale jobs are routed to manual reconciliation instead of being dispatched.
- **Migration safety:** an older inbox database is backfilled only after every legacy inbox row's HMAC is verified. Existing queue states are preserved; a tampered legacy row aborts initialization.
- **State semantics:** `DONE` means the trusted reconciliation worker says it recorded its current-state decision. It does **not** mean the webhook itself proved success, and the queue does not store a refund success state.

## Files

- `stripe_webhook_inbox.py` — R16 signature-verified inbox plus R17 durable queue API.
- `test_transactional_reconciliation_queue.py` — atomicity, migration, account scope, one-use claims, retries, HMAC integrity and concurrency coverage.
- `test_stripe_webhook_inbox.py` — existing signature/parsing tests plus a concurrent duplicate assertion that only one queue job is created.
- `test_webhook_http_receiver.py` — adds a test proving queue-write failure returns `503` and does not acknowledge the event.
- `run_webhook_tests_v2_7.py` — focused inbox, HTTP and queue suite.
- `run_complete_tests_v2_7.sh` — diagnostic cumulative runner for the retained R10–R17 suite set.
- `RESULTS_v2.7.md` and `SOURCE_PIN_v2.7.json` — verification boundaries and source identity.

## Run

Python 3.10+; standard library only.

```bash
cd r17_transactional_reconciliation_queue_v2_7
python run_webhook_tests_v2_7.py
python run_local_smoke.py
```

The focused command runs the R16 inbox and loopback HTTP tests along with the new R17 queue tests. The smoke should show `200 / INGESTED`, then `200 / DUPLICATE`, and a `RETRIEVE_CURRENT_PROVIDER_STATE` hint—not a direct success result.

## Production boundary

The receiver is a loopback-only test harness. The included signature verifier is a constrained reference implementation; production should use Stripe's official SDK with the exact raw request body and endpoint secret. Stripe recommends verifying the raw body, deduplicating events already being processed/processed, and acknowledging duplicate delivery with `200`; it documents automatic webhook retries for up to three days. See [Stripe webhook endpoint management](https://docs.stripe.com/events/manage-webhook-endpoints).

The inbox HMAC key must be external to the SQLite database. HMAC detects changes to surviving rows; it does not encrypt the database or reliably detect whole-row deletion/rollback without an external monotonic anchor. Deployments still need access controls, key rotation, retention/deletion, monitoring, backups, worker authentication, and a durable operation-state ledger.

`RECONCILED` must only be sent by a trusted worker after authenticated current-state retrieval and a durable update of the operation record. If the worker crashes between those steps, it must be safe to retrieve and record again. This queue is for reconciliation retrieval, not for issuing a second refund.

## Verification summary

- Focused R16+R17 suite: 84 / 84 passed.
- Prior R10, R11, R12 and R15 suites were rerun in separate processes: 49 / 49, 29 / 29, 39 / 39 and 85 / 85 passed respectively.
- Latest watchdog-bounded cumulative runner: 286 / 286 passed in one invocation.
- Python bytecode compilation and loopback smoke: PASS.
- No hosted Stripe requests, no real refunds and no upstream source changes.

Earlier unbounded runner attempts intermittently hung inside the retained R15 local HTTP simulator. The revised runner adds per-group timeouts and the latest cumulative invocation completed successfully; repeat it in CI before promotion.
