# Source Log — v2.5

Source review performed on 2026-10-17. The adapter remains a local source-informed reference; documentation claims below are drawn from Stripe's official API documentation.

1. **Stripe metadata:** https://docs.stripe.com/api/metadata  
   Relevant to data minimisation: Stripe describes metadata as structured key-value data, documents shape limits, and says not to store sensitive information in metadata. The v2.5 adapter is stricter than Stripe's API: it disables arbitrary caller metadata in this recovery-specific path.

2. **Stripe idempotent requests:** https://docs.stripe.com/api/idempotent_requests  
   Relevant to recovery policy: Stripe documents replaying the first status/body for an idempotency key, including `500` responses; keys can be pruned once at least 24 hours old; parameters are compared on key reuse. The local 23-hour cutoff is an adapter policy, not an SLA.

3. **Stripe create refund:** https://docs.stripe.com/api/refunds/create  
   Relevant to operation shape: Refund creation uses a Charge or PaymentIntent and accepts optional amount, reason and metadata. The reference adapter requires exactly one target and injects its own correlation key.

4. **Stripe list refunds:** https://docs.stripe.com/api/refunds/list  
   Relevant to reconciliation: refund-list pagination uses `starting_after` and returns a list envelope with `data` and `has_more`; the adapter bounds page count and fails closed for incomplete or malformed pagination.

No requests were sent to `api.stripe.com`; no test secrets or real payment objects were used. Official documentation was inspected, but the remote provider contract was not exercised in this run.
