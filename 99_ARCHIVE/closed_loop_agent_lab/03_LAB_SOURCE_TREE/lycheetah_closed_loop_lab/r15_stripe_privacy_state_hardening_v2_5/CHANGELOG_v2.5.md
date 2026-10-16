# Changelog — v2.5

- Disabled arbitrary caller-supplied Stripe metadata in durable request payloads; only Lycheetah's opaque operation correlation ID is retained.
- Added a strict top-level refund payload allow-list at the durable store boundary.
- Added a 5 MiB provider-response read limit and oversized-response recovery test; default list page size is 10.
- Added atomic compare-and-swap `READY -> IN_FLIGHT` claims, ensuring only one local dispatcher claims the initial send.
- Enforced a complete state-transition map; disallowed direct `READY -> SUCCEEDED` updates and unknown lifecycle states.
- Disabled per-call clock overrides by default, with an explicit opt-in for deterministic test harnesses only.
- Required endpoint / clock override flags to be actual Booleans.
- Results: 85 focused tests and 202 combined retained+focused tests passed; smoke and compilation passed.
- No hosted Stripe calls, real refunds, secrets, upstream edits or complete upstream CI.
