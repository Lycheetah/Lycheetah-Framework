# Changelog — v2.6

- Added a signed Stripe refund-event inbox for `refund.created`, `refund.updated`, and `refund.failed` snapshot events.
- Verifies timestamped `v1` HMAC over the exact raw bytes before JSON parsing; accepts multiple configured secret labels for controlled rotation.
- Rejects duplicate JSON keys, nonstandard constants, stale/future signature timestamps, malformed headers, oversized bodies, unknown types and non-test-mode records.
- Adds account-scoped event admission and repeat-checks account context before routing stored records into recovery.
- Deduplicates event IDs transactionally and rejects event-ID reuse with a different payload digest.
- Persists only the minimum refund correlation summary, not the raw event body or arbitrary metadata.
- HMAC authenticates inbox rows; lookups refuse tampered records.
- Loopback HTTP harness rejects ambiguous duplicate `Content-Length` framing as well as transfer encoding.
- A webhook can only request current provider retrieval or manual reconciliation; it cannot directly mark an operation successful.
- Added loopback HTTP receiver and 54 focused signature/parser/privacy/account/dedup/HTTP tests.
- 54 focused test methods and 256 combined retained test methods passed; Python compilation and local smoke passed.
- No hosted Stripe calls, real refunds, upstream source changes or full upstream CI.
