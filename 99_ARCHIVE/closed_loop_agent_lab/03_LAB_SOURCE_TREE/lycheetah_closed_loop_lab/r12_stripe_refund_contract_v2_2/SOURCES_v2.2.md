# Official Source Log — Stripe Refund Recovery Contract

Reviewed on 2026-10-17. These are official Stripe developer documentation pages. This pack encodes the subset required for the local contract and links directly to the source.

1. **Idempotent requests** — https://docs.stripe.com/api/idempotent_requests
   - API v1 caches status and body after endpoint execution starts, including `500` responses.
   - Validation failures and concurrent idempotency conflicts before endpoint execution are not cached.
   - Request parameters must match for a reused key.
   - Keys are at most 255 characters and can be pruned once at least 24 hours old.

2. **Create a refund** — https://docs.stripe.com/api/refunds/create
   - Refund target is a Charge or PaymentIntent for the supported flow described here.
   - Refund creation supports amount, reason and metadata parameters.

3. **List all refunds** — https://docs.stripe.com/api/refunds/list
   - Supports `charge` and `payment_intent` filters and cursor pagination.
   - No strong-consistency statement for using an empty listing as proof that an ambiguous create did not occur was found on this reviewed page. The policy therefore treats zero matches as unresolved.

4. **Refund object** — https://docs.stripe.com/api/refunds/object
   - Status values include `pending`, `requires_action`, `succeeded`, `failed` and `canceled`.

5. **Metadata** — https://docs.stripe.com/api/metadata
   - Up to 50 key/value pairs, key length up to 40 characters, value length up to 500 characters. Stripe says metadata is for structured annotation and is not itself used to authorize or decline a charge.

This source log records documentation statements, not experimental results against an account. Endpoint behavior can evolve; re-check the official documentation and test the exact account/API version at integration time.
