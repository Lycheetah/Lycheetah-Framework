# Provider Contract Source Notes (checked 2026-10-17)

The worker is deliberately narrow: it uses an interface equivalent to `retrieve_refund(refund_id)` and never creates or retries a refund. The sources below inform the interface and its limits; the tests in this pack use a local fake provider, not the hosted Stripe API.

1. **Stripe webhook signature and event guidance** — https://docs.stripe.com/webhooks
   - Webhook signature verification must use the exact raw request body and endpoint signing secret. The inbox receiver should be connected to Stripe's official SDK and exact request bytes in a real deployment.
   - Event payloads are snapshots from event creation time. Retrieving the current resource is appropriate when current state is needed. Return a 2xx response after durable receipt/queueing, not before the durable handoff commits.

2. **Create a refund** — https://docs.stripe.com/api/refunds/create
   - A refund targets a Charge or PaymentIntent and has amount/currency and a provider refund identifier. This worker does not invoke this endpoint.

3. **Retrieve a refund** — https://docs.stripe.com/api/refunds/retrieve
   - Current resource retrieval is the read-only contract used by the worker interface.

4. **List refunds** — https://docs.stripe.com/api/refunds/list
   - Refund listing is cursor-paginated through `starting_after`; a production reconciliation client must handle pagination and validate the complete query/result contract before treating a lookup as authoritative.

5. **Idempotent requests** — https://docs.stripe.com/api/idempotent_requests
   - Stripe documents replay of the first stored status/body for an idempotency key, including a cached `500`; keys may be pruned after they are at least 24 hours old. This motivates conservative recovery and reconcile-on-ambiguity. The v2.8 worker does not issue POST requests and does not rely on idempotency for current-state retrieval.

## Validation boundary

These sources are documentation, not a live contract test. Documentation was checked on 2026-10-17. A real deployment must pin the API version, configure an exact account scope and mode, use the official Stripe SDK for signature verification, and run authorized test-mode conformance tests before rollout.
