# Stripe Test-Mode HTTP Adapter — v2.4

## Purpose

Exercise a narrow refund lifecycle as real HTTP requests against a local simulator, including durable intent, preflight retrieval, provider POST, lost responses, stale idempotency keys, reconciliation and recovery after restart. The adapter is an experimental reference—not an official Stripe SDK or a production payment integration.

## Lifecycle

1. `prepare_refund()` validates a stable operation ID, visible-ASCII idempotency key, path-safe Charge/PaymentIntent ID, amount/reason/metadata, account context, API version and expected currency. It inserts `READY` intent and a keyed HMAC over the entire row before network I/O.
2. `dispatch()` accepts initial `READY` work only. It checks row HMAC and request fingerprint, enforces the local 23-hour cutoff, retrieves the target resource, verifies ID/object/test mode/currency and key eligibility fields, and refuses to POST if those checks fail.
3. After target preflight, it commits `IN_FLIGHT` before POST. That marker disambiguates a process crash during the request from an operation that was never attempted.
4. The refund POST uses the persisted body and idempotency key. The adapter verifies a matching refund response before classifying `SUCCEEDED`, `WAITING`, `NEW_APPROVAL_REQUIRED` or `RECONCILE`.
5. `recover()` uses the stored key/body only. `READY`, `IN_FLIGHT`, `UNKNOWN` and `CONFLICT` can retry only inside the local cutoff. Older operations are reconciled with read-only refund listing. `WAITING` is actively rechecked. Ambiguous API v1 server errors are never blindly POST-retried.
6. `reconcile()` checks refund-list schema, cursor progress, duplicate IDs, complete pagination and a unique operation-metadata match. Zero matches means `RECONCILE`, not “no refund occurred.”

## Storage and host configuration

- SQLite row updates are authenticated with HMAC-SHA256 using a separate local integrity key. Provider responses are data-minimized before persistence; unrelated metadata, provider error messages/URLs and fields such as `client_secret` are not retained. HMAC provides integrity, not confidentiality.
- The official default host is `https://api.stripe.com`; nonstandard ports on that hostname are rejected. Arbitrary HTTPS requires explicit opt-in. HTTP is accepted only for an explicitly enabled loopback simulator. Redirects are not followed.
- The adapter accepts only `sk_test_`-shaped keys; this is a configuration guard, not authentication proof that a remote server is Stripe.
- `Stripe-Account`, `Stripe-Version`, idempotency key, payload, account scope and expected currency are bound to the saved request context.

## Official contract facts and local policy

Stripe documents that API v1 idempotency saves the first result after endpoint execution begins, including a 500 response; mismatched parameters under a reused key error; concurrent requests can conflict before execution starts; and keys may be pruned once they are at least 24 hours old. Therefore v2.4 uses a **23-hour conservative local retry cutoff** and routes old/ambiguous operations to reconciliation. This cutoff is a project policy, not a provider guarantee.

Stripe documents retrieval endpoints for Charges and PaymentIntents and refund-list cursor pagination. The adapter uses those retrieval responses to preflight the exact target; it does not assume that metadata grants authority (metadata is correlation only), and it does not treat one preflight GET as atomic with the later refund POST.

## Verification

- Focused adapter tests: 76/76 passed in the latest local run (7.104 seconds).
- Retained R10–R12 tests plus v2.4: 193/193 test methods passed (16.401 seconds).
- Local smoke: provider committed one refund and dropped the response; recovery reused the same key and observed one simulated effect.
- Python compilation passed.

## Not claimed

No hosted Stripe API calls, no Stripe credentials, no real refunds, no upstream source modifications, no complete upstream CI run. Local simulator tests do not prove remote timing, hosted idempotency behavior, webhooks, Connect behavior, or remote atomicity. Production promotion requires controlled Stripe test-mode conformance using an authorized account, external approval binding, secret management, webhook/retrieval recovery, migration/backup strategy, monitoring and an independent security review.
