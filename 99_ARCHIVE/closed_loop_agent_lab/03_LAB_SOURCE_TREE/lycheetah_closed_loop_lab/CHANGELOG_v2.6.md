# Changelog — v2.6

- Added R16: signed Stripe refund webhook inbox and loopback HTTP receiver.
- Signature verification precedes strict raw-body JSON parsing; duplicate and malformed events fail closed.
- Inbox stores a minimal HMAC-authenticated event summary, not the raw body or arbitrary provider fields.
- Added account-scope revalidation at reconciliation time, event-ID deduplication and conflict detection.
- Event reception never marks a refund successful; it only signals authenticated current-provider-state retrieval.
- 54 focused tests passed and 256 combined retained tests passed, plus Python compilation and local smoke.
- No hosted Stripe calls, real refunds, upstream repository modifications or full upstream CI.
