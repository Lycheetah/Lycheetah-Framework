# Stripe API v1 Refund Recovery Contract — v2.2

**Research date:** 2026-10-17  
**Status:** Offline reference decision policy; no Stripe API calls were made.

## Why this operation

A partial refund is a consequential side effect: duplicate execution can send money twice, while premature success claims are also unacceptable. Stripe's documented API v1 idempotency semantics are detailed enough to support a practical, conservative recovery policy. This adapter covers `POST /v1/refunds`, not all Stripe APIs and not Stripe API v2.

## Documented contract facts

- API v1 saves a status and response body for a key after endpoint execution begins, including `500` responses; same-key retries replay that result.
- Validation failures and concurrent idempotency conflicts that occur before endpoint execution are not saved as idempotent results.
- Stripe compares parameters for a key and errors if they differ.
- Stripe API v1 idempotency keys are at most 255 characters. Keys can be pruned once they are at least 24 hours old; reusing a pruned key can start a new request.
- Refund creation accepts a Charge or PaymentIntent, optional positive minor-unit amount, supported reason values, and metadata. Refund listing can be scoped to a charge or PaymentIntent and paginated.
- Refund status can be `pending`, `requires_action`, `succeeded`, `failed`, or `canceled`.
- Stripe metadata supports up to 50 keys; keys have a 40-character limit and values 500 characters. Metadata is not itself an authorization control.

## Policy implemented here

1. Persist one immutable operation envelope before sending the request. It binds operation UUID, idempotency key, Stripe account context, live/test mode, API version, endpoint, and canonical request payload fingerprint. During recovery, the helper recomputes the fingerprint from the actual retry payload and current account/mode/API-version, and compares the actual idempotency key to the persisted one; it accepts no caller-supplied `payload_matches=True` style flags.
2. Always set `metadata[lycheetah_operation_id]` when creating the refund. The key is reserved and cannot be overridden by caller metadata.
3. For an unknown network outcome inside a **23-hour automated retry cutoff**, retry only with the exact saved payload, exact same key, and same account/mode/API-version context. The one-hour margin is a local conservative policy, not a Stripe guarantee.
4. If the known outcome is a cached server error, reconcile rather than interpreting the error as proof that no effect occurred. Same-key retries may replay the stored error.
5. At or beyond the local cutoff, do not automatically issue another create request. Enumerate all pages of refunds scoped to the original charge or PaymentIntent and match operation metadata plus target, amount, currency, and status. The offline helper rejects a bare “listing complete” boolean; it checks list-response markers, `has_more`, page order and the `starting_after` cursor chain, and binds reconciliation to the original account/mode/API-version.
6. Exactly one correlated `succeeded` refund is accepted as completed. A `pending` or `requires_action` object waits for further provider resolution. A `failed` or `canceled` object requires new approval before a new operation/key is created. Zero results, multiple results, mismatched fields, incomplete pagination or untrustworthy lookup always route to reconciliation.

## Non-claims and residual limits

- Stripe's idempotency protects the duplicate-request path within its documented contract; it does **not** make Lycheetah's authorization/evidence predicate transactional with Stripe's refund commit.
- The refund listing docs describe filters and pagination but do not promise that a zero-result scan is a strongly consistent proof of non-execution. This policy therefore never treats absence alone as evidence that no refund occurred.
- A metadata operation tag assists correlation; it must not contain secrets or personal information and it is not a provider-issued authenticity proof. `RefundListPage` envelopes must be created by a trusted adapter from the actual cursor sent and response received; arbitrary fabricated fixtures do not establish provider provenance.
- No API credentials were provided, no sandbox call was made, and no real refund was created.
- The repository integration, Stripe API contract and any webhook/event-based reconciliation still require dedicated sandbox validation before use.

## Official references

- Idempotent requests: https://docs.stripe.com/api/idempotent_requests
- Create a refund: https://docs.stripe.com/api/refunds/create
- List all refunds: https://docs.stripe.com/api/refunds/list
- Refund object/statuses: https://docs.stripe.com/api/refunds/object
- Metadata constraints: https://docs.stripe.com/api/metadata
