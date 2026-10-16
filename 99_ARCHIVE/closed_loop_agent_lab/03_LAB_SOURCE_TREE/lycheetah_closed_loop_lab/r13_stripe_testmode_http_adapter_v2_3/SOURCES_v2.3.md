# Source Log — v2.3

Inspected 2026-10-17. URLs are provider documentation pages; the adapter is based on these documented contracts but does not constitute a provider certification.

1. Stripe API: Create a refund — https://docs.stripe.com/api/refunds/create
   - Normal refund flow specifies a Charge or PaymentIntent; amount is optional for partial refunds; reason values and metadata are documented.
2. Stripe API: Idempotent requests — https://docs.stripe.com/api/idempotent_requests
   - API v1 stores the first response after endpoint execution begins, including 500 responses; incoming parameters are compared on key reuse; keys can be pruned after at least 24 hours; invalid pre-execution requests and concurrent conflicts are treated differently.
3. Stripe API: List all refunds — https://docs.stripe.com/api/refunds/list
   - List can be filtered by charge or payment_intent; `limit` is 1–100; `starting_after` is used for forward cursor pagination and `has_more` reports continuation.
4. Stripe API: Retrieve a refund — https://docs.stripe.com/api/refunds/retrieve
   - Reviewed as a potential reconciliation path; not invoked by the implementation in this iteration.

Local reference docs:
- v2.2 `r12_stripe_refund_contract_v2_2/STRIPE_REFUND_CONTRACT_v2.2.md`
- v2.2 source snapshot `r12_stripe_refund_contract_v2_2/SOURCES_v2.2.md`

Policy interpretation (23h cutoff, strict explicit `livemode=false`, row HMAC, local HTTP-only test server) is project-authored engineering policy, not a Stripe guarantee.
