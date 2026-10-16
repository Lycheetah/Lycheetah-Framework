# Provider contract source log — v2.6

**Checked:** 2026-10-17. This package uses only local synthetic webhook fixtures and loopback HTTP. No hosted Stripe API requests were made.

1. **Stripe webhook verification and delivery management** — https://docs.stripe.com/events/manage-webhook-endpoints
   - Requires verification using the raw request body, the `Stripe-Signature` header and the endpoint secret.
   - Describes the header format and raw-body requirements.
   - Recommends identifying events already processing/processed; duplicate delivery should be skipped and acknowledged.
   - The inbox follows this structure, then improves its reference harness with explicit duplicate-key parsing rejection, a minimized durable record and an HMAC ledger.

2. **Stripe webhook setup / signature checking** — https://docs.stripe.com/events/set-up-events
   - Official integration guidance for webhook setup and signature verification.

3. **Official stripe-python webhook verifier** — https://github.com/stripe/stripe-python/blob/master/stripe/_webhook.py
   - `Webhook.construct_event` and `WebhookSignature.verify_header` are the preferred production interface for snapshot webhooks. The file contains the established timestamped `v1` HMAC verification flow.
   - This reference module reimplements a constrained subset only so it can be tested with Python's standard library. Production should call the official SDK instead.

4. **Stripe refund-related events** — https://docs.stripe.com/api/events/types
   - Lists `refund.created`, `refund.failed`, and `refund.updated` as refund-related event types.

5. **Retrieve a refund** — https://docs.stripe.com/api/refunds/retrieve
   - Documents `GET /v1/refunds/{refund_id}` to retrieve the current state of an existing refund. The inbox emits only a hint to perform this authenticated current-state retrieval; it does not perform the retrieval itself.

## Important distinction

Official documentation is evidence of a published contract, not proof of a particular account's event configuration. The tests validate our code against synthetic event fixtures; only an authorized Stripe test-mode integration run can establish compatibility with a specific account, endpoint configuration, connected-account routing and pinned API version.
