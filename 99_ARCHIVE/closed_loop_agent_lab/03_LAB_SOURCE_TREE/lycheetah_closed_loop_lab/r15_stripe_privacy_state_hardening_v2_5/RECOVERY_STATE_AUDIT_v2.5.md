# R15 — Privacy, state-transition, and dispatch-claim audit (v2.5)

**Date:** 2026-10-17  
**Scope:** local reference adapter copied from R14 and hardened; local simulator only.  
**Status:** local research prototype; not an official Stripe SDK, hosted-provider conformance report, or production payment integration.

## New findings and fixes

### 1. Custom request metadata was retained verbatim

The adapter must persist its exact request body for same-key retry. The v2.4 response sanitizer therefore did not eliminate sensitive values passed in *request* metadata: arbitrary `metadata` fields could still land in `payload_json`. This version disables caller-supplied metadata and permits only the internally generated `lycheetah_operation_id` correlation field. The store also independently enforces a strict payload-field allow-list, so callers cannot bypass the restriction by invoking the lower-level store API.

This is a deliberate trade-off: integrations that need arbitrary metadata must design a separate data minimization/encryption/retention contract instead of silently persisting it in the idempotency body.

### 2. HTTP response bodies had no read limit

`_request` previously called an unbounded `read()`. Responses are now capped at 5 MiB. If a body exceeds the cap, the adapter records an uncertain outcome without parsing or persisting the oversized body; it then follows the normal recover/reconcile path. The local simulator includes an oversized-response-after-commit fault to ensure this is not reported as confirmed success.

5 MiB is a local memory bound, not a Stripe API limit. Refund-list pagination defaults to 10 items per page, the documented default, rather than fetching 100 full objects by default.

### 3. The initial dispatch marker was not a compare-and-swap claim

Two local workers could both read `READY`, both run preflight, and both write `IN_FLIGHT` via the generic result updater. Stripe's idempotency should guard duplicate effects under its documented contract, but the local coordinator should not unnecessarily issue two POSTs. `claim_ready_for_dispatch()` now acquires an SQLite write transaction, authenticates the existing row, and changes `READY -> IN_FLIGHT` only where the state remains `READY`. The concurrency regression asserts one local claim and one POST.

### 4. Generic state updates allowed impossible transitions

The old updater guarded terminal states, but otherwise allowed arbitrary transitions such as `READY -> SUCCEEDED`. A complete lifecycle transition map now rejects unlisted states and transitions. The initial `READY -> IN_FLIGHT` edge is reserved for the authenticated atomic claim method.

### 5. Caller-provided time could bypass freshness cutoff

Public calls accepted a `now` argument used by deterministic tests. In ordinary application use, an accidental stale timestamp could undermine the 23-hour retry cutoff. Public per-call clock overrides are now disabled by default and require explicit `allow_test_clock_override=True`; the local tests opt in. Production-shaped operation should omit `now` and use the system UTC clock.

This opt-in remains a test facility, not a security boundary against a hostile in-process caller who can construct or reconfigure the client.

### 6. Permissive configuration flags now require actual booleans

Endpoint and test-clock opt-in flags must be `bool`, not truthy strings or integers. The durable store rejects unsupported top-level payload fields, in addition to restricting metadata.

## Verification

- R15 focused HTTP/SQLite suite: **85/85 test methods passed**.
- Retained R10-R12 regression suites plus R15: **202/202 test methods passed**.
- Python compilation: passed.
- Local loopback smoke: first response dropped after simulated provider commit; recovery returned `SUCCEEDED`; effect count remained 1 across 2 POST requests.
- Adversarial cases include caller metadata/PII rejection before persistence, low-level payload bypass rejection, oversized response, stale public clock override, concurrent `READY` claims, direct `READY -> SUCCEEDED` state-write attempt, invalid state, HMAC/database tamper, retry cutoff, lost response, cached 500, pagination faults, host redirects, account/API version mismatch and non-test-mode resources.

Test counts are test-method counts; they are not independent tests of hosted Stripe. The full Lycheetah upstream package suite was not run.

## Remaining boundaries

- No real Stripe API request or refund was made.
- No live or test Stripe credentials were supplied; local simulator uses a mock test-shaped key.
- No Lycheetah upstream source was modified and no upstream branch or PR was created.
- The simulator only approximates a narrow part of Stripe API v1. It does not model every payment method, account configuration, status transition, rate limit or platform behavior.
- Preflight checks a Charge/PaymentIntent snapshot; this is not atomic with the later remote refund commit.
- HMAC authenticates local ledger records but does not encrypt the database. The exact request still contains identifiers, amount, currency, and an opaque operation ID.
- If the local integrity key or process is compromised, the HMAC boundary is compromised.
- Idempotency guarantees are bounded by the provider's actual endpoint semantics and key retention; after the local cutoff, automated POST retry is disabled and reconciliation is required.

## Promotion gate

Before any production use: run controlled Stripe test-mode conformance with an authorized account and pinned API version; establish test/Connect account context, same-key/same-payload and same-key/different-payload behavior, lost-response recovery, `500` handling, webhook/retrieval reconciliation, current refund statuses, pagination semantics, key-retention cutoff, key rotation, local database backup/migration, monitoring and human escalation. Require independent security review and an integration-owned approval broker. Do not treat this artifact as production-certified.
