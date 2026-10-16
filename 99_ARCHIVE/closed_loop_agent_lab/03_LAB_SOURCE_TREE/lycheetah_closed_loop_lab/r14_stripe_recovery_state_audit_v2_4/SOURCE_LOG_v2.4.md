# Source Log — v2.4

Inspected 2026-10-17. These are official Stripe API reference pages consulted to ground the adapter's narrow contract. The resulting code is not a Stripe certification.

1. **Create a refund** — https://docs.stripe.com/api/refunds/create
   - Refund target can be a Charge or PaymentIntent; amount is specified in the currency's minor unit; metadata is a supported parameter.
2. **Idempotent requests** — https://docs.stripe.com/api/idempotent_requests
   - Stripe documents result caching after endpoint execution begins, including 500 responses; reused keys require the same parameters; conflicting concurrent requests can fail before an endpoint begins; keys can be pruned once they are at least 24 hours old.
3. **Retrieve a Charge** — https://docs.stripe.com/api/charges/retrieve
   - Used as the documented source for the Charge preflight fields (ID, currency, livemode, paid/captured, amount and already-refunded amount).
4. **Retrieve a PaymentIntent** — https://docs.stripe.com/api/payment_intents/retrieve
   - Used as the documented source for PaymentIntent identity, currency, livemode, status and received amount.
5. **List refunds** — https://docs.stripe.com/api/refunds/list
   - Used for charge/PaymentIntent filters, `limit`, `starting_after`, `data` and `has_more` pagination semantics.
6. **Metadata** — https://docs.stripe.com/api/metadata
   - Metadata is application-provided structured data. In this adapter it is a correlation marker only—not an authorization primitive.

## Project-authored conservative policy

- The 23-hour local retry cutoff is shorter than Stripe's documented “at least 24 hours” pruning statement; it is not itself a Stripe retention SLA.
- A preflight read cannot atomically reserve the target's balance or predicate with the later create-refund call. Stripe's endpoint remains the final authority for actual eligibility and balance constraints.
- Refund-list zero matches, incomplete pages, multiple matches and mismatches all route to `RECONCILE`.
