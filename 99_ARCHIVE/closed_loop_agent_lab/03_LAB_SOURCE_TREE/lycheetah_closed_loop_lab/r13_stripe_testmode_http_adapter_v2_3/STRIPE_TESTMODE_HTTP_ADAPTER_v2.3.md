# Stripe Test-Mode HTTP Adapter — v2.3

**Research date:** 2026-10-17  
**Scope:** test-mode-only, one endpoint family: `POST /v1/refunds`, and `GET /v1/refunds` reconciliation.  
**Status:** local HTTP contract prototype. Not production-ready; not integrated upstream.

## Why this iteration matters

v2.2 had a pure recovery-policy helper. v2.3 connects the decision to an actual HTTP client boundary, a durable operation record and an HTTP server simulator. This makes it possible to exercise failures across the serialization/HTTP boundary without spending money or relying on a test API account.

The prototype persists an immutable request snapshot and random idempotency key before making a request. It pins the configured provider-account scope, optional `Stripe-Account` header, `Stripe-Version`, and test-mode constraint. It rejects live keys, arbitrary HTTPS hosts by default, non-root API base paths, and redirects. A redirect is treated as a provider-contract failure so the Authorization header is not forwarded to a redirect target.

The SQLite row has an HMAC over request identity, state, response and timestamps. The HMAC key is passed separately and must not be stored in the database. This detects database edits by an actor who can write the database but does not possess the HMAC key; it does not protect a compromised application process, compromised key, malicious administrator with both capabilities, or host-level rollback to an older valid database snapshot.

## Operational state logic

- **READY:** durable request intent exists, but no outcome is established. Dispatch may send the persisted request.
- **UNKNOWN:** transport ended without an authoritative response. Inside the conservative retry window, recovery repeats the same key and exact persisted request.
- **AMBIGUOUS_5XX:** Stripe API v1 can replay a stored 500 response, so the adapter does not blindly retry. It queries refund history and remains in reconciliation if no matching refund is found.
- **SUCCEEDED:** a response or reconciled object matched the operation metadata, target, expected amount when specified, currency, status and explicit test-mode marker. The persisted state is HMAC-authenticated.
- **WAITING:** a correlated refund exists but is `pending` or `requires_action`; the system does not claim final success.
- **NEW_APPROVAL_REQUIRED:** a correlated refund is failed/canceled; any new effect requires a separate operation and approval.
- **RECONCILE:** account/API/payload mismatch, malformed or incomplete listing, duplicate matches, stale idempotency window, missing correlation, conflicting output or another ambiguous boundary.

The adapter uses a **23-hour local cutoff** to stop automated same-key retry before Stripe API v1's documented minimum 24-hour pruning point. This is a conservative local policy; it is not a promise that Stripe retains any particular key for exactly 23 or 24 hours. Idempotency keys are compared in the provider account scope, and API version and account scope are also part of the local request identity.

## Official provider facts used

1. The create-refund endpoint requires a Charge or PaymentIntent in the normal refund flow, accepts optional amount/reason/metadata, and returns a Refund object: <https://docs.stripe.com/api/refunds/create
2. Stripe API v1 idempotency records the first response once endpoint execution begins, including `500`; parameters are compared for reuse; keys can be pruned once at least 24 hours old; pre-execution validation failures and concurrent conflicts have special semantics: <https://docs.stripe.com/api/idempotent_requests
3. Listing refunds supports Charge/PaymentIntent filters, `limit` (1–100), `starting_after` cursor pagination, and a `has_more` flag: <https://docs.stripe.com/api/refunds/list
4. The Retrieve Refund endpoint exists, but this prototype does not use it: <https://docs.stripe.com/api/refunds/retrieve

Documentation was inspected on 2026-10-17. These facts should be rechecked against Stripe documentation, the intended Connect account model, and the project's pinned API version during integration.

## What the tests prove

The local simulator exercises the serialized form request, HTTP headers, response parsing, durable pre-request intent, response loss after simulated commit, retry with same key, restart recovery, account/mode/API-version drift, tampered database rows, redirect denial, pagination faults, stale-key reconciliation, and duplicate request races. The local provider simulator returns the same successful result for the same idempotency key/body, and rejects same-key/different-body use.

**The tests prove behavior of this reference adapter against the local simulator contract, not the behavior of Stripe's hosted service.** The simulator is deliberately narrow and is not intended to replicate all Stripe errors, network behavior, idempotency concurrency responses, object states, Connect semantics, webhook behavior, or provider consistency.

## Unresolved limitations and promotion gates

- **No actual Stripe call:** no secret was supplied, no Stripe API was called, and no refund was created.
- **No end-to-end authority gate:** the adapter does not independently authenticate human approvers or call the real Lycheetah `FinalityGate`. The calling application must ensure `prepare_refund` receives an already-authorized request.
- **No atomic provider-side policy commit:** Stripe's idempotency contract does not atomically validate Lycheetah's external evidence lease at refund commit. Local DB checks cannot lock provider-side state.
- **No proof from absence:** no correlated refund after pagination still returns `RECONCILE` because list absence is not proof of no effect.
- **No webhook integration:** event ordering, duplicate webhook delivery, `eventually consistent` behavior, and webhook signature validation are not included.
- **Key ownership:** `account_scope` is an application-supplied label. It must be bound to a vetted secret-manager mapping; the adapter cannot prove that a given key actually belongs to the declared Stripe platform account.
- **Single-host store:** SQLite is for a local reference prototype. Multi-host deployments need a durable transactional database, race-safe claims, migrations and explicit consistency guarantees.
- **Key retention:** the conservative 23h cutoff is policy. Recovery past it is reconciliation-only; an empty list stays ambiguous.
- **Status surface:** success requires exact operation metadata, target, currency, amount (when explicit) and test-mode marker. When provider object shape or semantics vary, this may route to reconciliation rather than guess.
- **No full Lycheetah upstream test run:** GitHub write access was not used; no branch or pull request exists from this work.

Before production consideration, run a controlled Stripe test-mode conformance exercise with a real test account and API version, validate Connect scope, demonstrate recovery after response loss, add signed webhook/retrieval reconciliation, test rate limiting and concurrent conflicts, review secrets/key rotation and database migration/backup, and receive independent security review. Never use live-mode credentials for this research package.
