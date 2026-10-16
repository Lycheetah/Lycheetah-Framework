# Lycheetah R16 — Stripe Webhook Reconciliation Inbox v2.6

**Status:** local reference implementation; signature logic and receiver are testable but not production-certified. No Stripe API call or refund is performed by this package.

## Why this iteration exists

R15 can reconcile uncertain refund outcomes by retrieving/listing the current provider resource. A signed webhook gives the recovery worker another prompt to look, but a webhook is not itself proof of current success: events can be redelivered, delayed, or observed out of order. The inbox therefore authenticates an event, records a minimal summary exactly once by event ID, and emits only `RETRIEVE_CURRENT_PROVIDER_STATE` (or a manual-reconciliation result). It never marks the refund successful itself.

## Files

- `stripe_webhook_inbox.py` — raw-byte signature verification, strict event parsing, account/mode/type filters, minimized durable inbox, HMAC-authenticated rows and reconciliation hints.
- `webhook_http_receiver.py` — loopback-only test receiver that keeps the raw body intact, applies size/method/path guards and returns sanitized diagnostics.
- `test_stripe_webhook_inbox.py` — signature, timestamp, parsing, privacy, cross-account, duplicate, tamper and concurrency cases.
- `test_webhook_http_receiver.py` — real loopback HTTP integration tests including invalid signature, duplicate delivery and oversized/missing framing.
- `run_webhook_tests_v2_6.py` — focused suite.
- `run_local_smoke.py` — reproducible HTTP acceptance/duplicate smoke.
- `run_complete_tests_v2_6.sh` / `.py` — retained R10–R12 and R15 contracts + R16 webhook tests (complete archive only).
- `RESULTS_v2.6.md`, `PROVIDER_CONTRACT_SOURCES_v2.6.md` — evidence and limits.

## Run

Python 3.10+; standard library only.

```bash
cd r16_webhook_reconciliation_v2_6
python run_webhook_tests_v2_6.py
python run_local_smoke.py
```

From the complete research archive root:

```bash
bash r16_webhook_reconciliation_v2_6/run_complete_tests_v2_6.sh
```

## Production boundary

Use Stripe's official SDK for webhook signature verification in a real integration (`stripe.Webhook.construct_event` for snapshot events). Preserve the exact raw request bytes until verification. Load endpoint secrets from a secret manager. Configure a production-grade framework/proxy to enforce body-size, timeout and HTTP framing limits. This custom standard-library verifier exists for controlled contract tests and intentionally has a bounded subset of the event schema.

The inbox HMAC key must be stored outside the SQLite database. HMAC detects tampering; it does not encrypt the database. Plan retention and deletion for the minimal event summaries. Do not expose the loopback receiver to a network.
