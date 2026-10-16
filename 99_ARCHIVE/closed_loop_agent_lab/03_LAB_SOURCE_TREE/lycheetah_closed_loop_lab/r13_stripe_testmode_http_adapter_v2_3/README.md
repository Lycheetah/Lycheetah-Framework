# Lycheetah Stripe Test-Mode HTTP Adapter v2.3

**Status: local contract-testing reference implementation.** This is not an officially supported Stripe SDK, a production payment adapter, or an upstream Lycheetah integration.

## What is included

- `stripe_test_adapter.py` — test-mode-only HTTP client and HMAC-authenticated SQLite operation ledger.
- `stripe_contract_simulator.py` — local HTTP simulator for the narrow create/list-refunds contract used by the tests. It is not a Stripe emulator.
- `test_stripe_test_adapter.py` — 51 focused tests.
- `run_complete_tests_v2_3.py` — runs the retained v2.0–v2.2 regression suites plus the new HTTP suite.
- `STRIPE_TESTMODE_HTTP_ADAPTER_v2.3.md` — design and provider-contract notes.
- `RESULTS_v2.3.md`, `SCENARIO_MATRIX_v2.3.json`, `SOURCES_v2.3.md` — results, adversarial cases, and source log.

Only Python's standard library is required. No `stripe` SDK dependency is used.

## Run the local HTTP contract tests

From this directory:

```bash
python -m unittest -v test_stripe_test_adapter.py
```

From the `lycheetah_closed_loop_lab` root to run all preserved suites:

```bash
python r13_stripe_testmode_http_adapter_v2_3/run_complete_tests_v2_3.py
```

The tests talk only to a server bound to `127.0.0.1` and use the fixture key `sk_test_local_mock`. They do not call Stripe, create a real refund, or require credentials.

## Critical safety limits

1. The adapter rejects live-mode keys. It defaults to `https://api.stripe.com`; custom HTTPS hosts require explicit opt-in, and redirects are not followed.
2. The exact request, account scope, connected-account header, API version, test mode, and expected currency are bound into a request fingerprint. The complete persisted row is HMAC-authenticated.
3. The HMAC key is deployment secret material and must be stored outside the SQLite database. The test suite uses only a test fixture key. A process compromise that exposes the key defeats this local tamper control.
4. A stable idempotency key is stored before network I/O. A dropped response after simulated provider commit is recovered using the same key and exact persisted request.
5. API v1 stored server errors are not blindly retried. Refund listing requires valid pagination, checks metadata/target/amount/currency/status, and never treats zero matches as proof of no effect.
6. SQLite here is a single-host reference. It is not a distributed multi-worker ledger or a guarantee of atomicity between a local transaction and Stripe.
7. No live-mode, webhook, Stripe test-mode sandbox, upstream package, or real provider conformance test was run. Production promotion requires a separate threat review and controlled Stripe test-mode run.

## Source contract

The implementation is narrowly based on the official API reference for [creating refunds](https://docs.stripe.com/api/refunds/create), [idempotent requests](https://docs.stripe.com/api/idempotent_requests), and [listing refunds](https://docs.stripe.com/api/refunds/list). Source details can change; review these pages and the account's pinned API version before an integration release.
