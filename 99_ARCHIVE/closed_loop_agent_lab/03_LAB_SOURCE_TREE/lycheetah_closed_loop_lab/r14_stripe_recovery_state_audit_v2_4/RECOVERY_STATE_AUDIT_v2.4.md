# Recovery State Audit — v2.4

**Date:** 2026-10-17  
**Scope:** static source review of v2.3's local HTTP adapter plus source changes and local regression tests. No hosted Stripe API calls.

## Findings and repairs

### R14-1 — Public send path bypassed the retry cutoff

In v2.3, the public `dispatch()` accepted `READY`, `UNKNOWN` and `CONFLICT`; the 23-hour cutoff existed in `recover()`, not inside `dispatch()`. A caller invoking `dispatch()` directly with an old stored operation could therefore POST after the local cutoff. This mattered because Stripe documents that idempotency keys can be pruned after they are at least 24 hours old, after which reusing a key can start a new request.

**Repair:** cutoff enforced within `_dispatch_persisted()` regardless of whether called from `dispatch()` or `recover()`. Stale operations go through read-only reconciliation. Only `READY` is accepted by public `dispatch()`; repeat states require `recover()`.

**Regression:** `test_direct_dispatch_cannot_bypass_cutoff_for_old_ready_intent`, `...old_unknown_intent`, and `...old_conflict` assert no POST after cutoff.

### R14-2 — The first request had no durable in-flight marker

In v2.3, the row stayed `READY` during the provider POST. A process death after provider commit but before local response persistence could leave a row indistinguishable from “never sent.” Retrying the same key may be safe only while the provider's idempotency semantics still protect that key.

**Repair:** v2.4 writes and authenticates `IN_FLIGHT` before the first refund POST. A recovered `IN_FLIGHT` operation reuses the exact persisted request and same key inside the cutoff; stale operations reconcile without POST.

**Regression:** `test_in_flight_marker_is_committed_before_provider_post` checks the row state from inside the simulator's POST handler. `test_crash_state_in_flight_recovers_using_same_key` exercises restart recovery.

### R14-3 — `WAITING` could become permanent local status

In v2.3, `recover()` returned the stored `WAITING` result without querying the provider again. A pending refund could later succeed while the local row remained waiting indefinitely.

**Repair:** `recover()` revalidates the stored waiting result, then calls `reconcile()`. A matching current refund response is persisted as `WAITING`, `SUCCEEDED`, or `NEW_APPROVAL_REQUIRED` as appropriate. Confirmed `SUCCEEDED` and terminal `NEW_APPROVAL_REQUIRED` state cannot be downgraded by late concurrent responses.

**Regression:** `test_waiting_refund_is_rechecked_and_promoted_after_provider_changes`, `test_waiting_refund_that_remains_pending_stays_waiting`, and `test_late_timeout_cannot_downgrade_confirmed_success`.

### R14-4 — Currency was only checked after the effect

In v2.3, the adapter classified `refund.currency` after a successful POST. An intent with `expected_currency="usd"` could still POST a refund for a EUR target before returning `RECONCILE` for the mismatch.

**Repair:** before the first POST from `READY`, v2.4 retrieves the target Charge or PaymentIntent and requires exact ID/object identity, explicit `livemode=false`, matching currency, a paid-and-captured Charge or succeeded PaymentIntent, and simple amount/balance constraints. A substantive preflight mismatch is persisted as `PRECHECK_FAILED`; no refund POST is sent, and recovery requires a new reviewed operation.

**Regression:** tests cover mismatched currency, uncaptured charges, insufficient remaining Charge balance, fully refunded Charge, unsucceeded PaymentIntent, non-test-mode resource, valid PaymentIntent and preflight transport failure.

**Limit:** the retrieved state is a snapshot, not a remote lock or funds reservation. The adapter does not claim atomicity between retrieval and Stripe's create-refund endpoint. Stripe remains the final authority for current refundable amount and request validity.

### R14-5 — Configuration/input hardening

**Repair:** reject nonstandard ports for the official host, malformed ports, non-finite timeouts, API-version header control characters, idempotency key whitespace/control characters and target identifiers that could alter the request path.

**Regression:** the focused suite includes cases for each of these conditions.

## Safety invariant

Once a refund request may have reached the provider, the system must never invent certainty from a local flag or a zero-match list response. It may return success only when an authenticated local record contains a response classified against the exact persisted intent or when reconciliation finds one unique matching refund with the expected operation metadata, target, amount (when specified), currency, explicit test-mode marker and acceptable status. Missing, incomplete, ambiguous or mismatched evidence routes to `RECONCILE`.

## Evidence level

This is a source-informed reference implementation and local simulator test suite. It is not a test against Stripe's hosted API, not a full checkout of Lycheetah-Framework, and not production approval.

### R14-6 — HMAC integrity was being mistaken for enough protection for stored responses

v2.3 persisted full provider response mappings. That is broader than recovery needs, and HMAC does not encrypt the stored response.

**Repair:** v2.4 persists allow-listed fields only: target/refund IDs and object type, amount, currency, status, livemode, and the operation-correlation key. Failed-preflight summaries exclude fields such as PaymentIntent `client_secret`; provider error summaries omit free-text messages and URLs.

**Regression:** `test_unsucceeded_payment_intent_is_rejected_before_post`, `test_success_record_stores_only_recovery_fields_and_operation_metadata`, and `test_cached_error_record_omits_provider_error_message`.
