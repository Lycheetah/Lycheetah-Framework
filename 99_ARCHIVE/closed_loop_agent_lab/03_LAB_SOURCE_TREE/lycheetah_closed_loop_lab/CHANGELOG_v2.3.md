# Changelog — v2.3

## Stripe Test-Mode HTTP Adapter

- Advanced v2.2's offline decision helper into a local HTTP contract-tested adapter.
- Added SQLite durable intent records written before network requests.
- Bound payload, endpoint, account scope, connected account, test mode, API version and expected currency into the local request fingerprint.
- Added HMAC authentication of the full local ledger row (intent, lifecycle state, provider response and timestamps); key supplied separately from DB.
- Restricted to `sk_test_` credentials, `api.stripe.com` by default, explicit loopback HTTP only for local simulator, and no redirects.
- Added lost-response, provider-committed-response-lost, stored-500, stale-key, tamper, pagination, currency/status, connected-account and concurrent-request tests.
- Added bounded reconciliation pagination to avoid unbounded malformed-provider loops.
- Combined verification: 51 R13 tests; 168 total retained + new test methods passed.
- No hosted Stripe calls, no real refunds, no live-mode keys, no upstream files changed.

## Limits

This is a local reference adapter, not a production integration, official Stripe SDK, hosted-service certification, or complete upstream test run. Before any production consideration, require a real Stripe test-mode conformance exercise, webhook/retrieval reconciliation, external approval integration, secrets-management review, migration/backup review, and independent security assessment.
