# Provider contract source log — v2.5

Checked during this research run on 2026-10-17. These sources describe the documented contract; no hosted requests were made.

1. **Stripe idempotent requests** — https://docs.stripe.com/api/idempotent_requests
   - Stripe saves the first request's response status/body for a key, including `500` responses.
   - Keys may be pruned after they are at least 24 hours old; reusing a pruned key can initiate a new request.
   - Incoming parameters are compared with the original request; differing parameters are rejected.
   - The local 23-hour policy is a conservative client-side cutoff, not a Stripe-guaranteed 23-hour retention SLA.

2. **Stripe Refund API** — https://docs.stripe.com/api/refunds
   - Refunds can be created for a Charge or PaymentIntent.
   - Refund listing can be filtered by Charge or PaymentIntent and uses cursor parameters such as `starting_after`.
   - The reference adapter persists only the response fields needed to classify/recover, and page limit defaults to 10 rather than the endpoint's maximum 100.

3. **Stripe List Refunds API reference** — https://docs.stripe.com/api/refunds/list
   - The list response contains a `data` array and `has_more`; pagination must be followed using a cursor for complete listing.
   - Absence from an incomplete or eventually changing scan is not proof that a refund did not happen.

4. **Stripe API authentication/reference** — https://docs.stripe.com/api
   - Test-mode secret keys use the `sk_test_` prefix; live-mode keys use `sk_live_`.
   - Hosted API requests require HTTPS. Local HTTP is permitted only for the explicit loopback simulator in this reference adapter.

The adapter pins an API version from the test fixture in each operation record. The pin is an explicit compatibility choice for the harness and is not asserted to be the newest Stripe API version.
