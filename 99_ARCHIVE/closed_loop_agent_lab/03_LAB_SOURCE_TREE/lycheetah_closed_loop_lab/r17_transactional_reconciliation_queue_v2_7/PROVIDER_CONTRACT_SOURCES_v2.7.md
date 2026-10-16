# Provider / platform contract references — v2.7

Checked 2026-10-17. This work used synthetic signed fixtures and a loopback receiver; no hosted Stripe API was contacted.

1. **Stripe — Manage webhook endpoints:** https://docs.stripe.com/events/manage-webhook-endpoints
   - Verify with the `Stripe-Signature` header, endpoint secret and exact raw body.
   - Stripe automatically retries undelivered events for up to three days.
   - A manual processor should skip events already processing/processed and return `200` for duplicates.
   - R17 makes inbox acceptance and durable follow-up job atomic so an event is not acknowledged if its job cannot be recorded.
2. **Stripe — Set up events / signature checking:** https://docs.stripe.com/events/set-up-events
   - Official webhook setup and signature verification guidance.
3. **Stripe Python SDK webhook verifier:** https://github.com/stripe/stripe-python/blob/master/stripe/_webhook.py
   - Production integration should use the official SDK's webhook helper with unchanged raw bytes; the standard-library verifier here is only a narrow testable reference.
4. **Stripe Event object:** https://docs.stripe.com/api/events/object
   - Event payload `data` reflects resource state at event creation; current provider retrieval remains the safer source for terminal reconciliation decisions.
5. **Stripe Retrieve Refund:** https://docs.stripe.com/api/refunds/retrieve
   - Authenticated current-state retrieval target; queue jobs request reconciliation rather than asserting success based on event payload.

## Evidence boundary

These pages document platform contracts but do not prove that any particular connected-account configuration, API version, or hosted webhook endpoint matches the synthetic fixtures. Actual test-mode conformance remains a separate gate.
