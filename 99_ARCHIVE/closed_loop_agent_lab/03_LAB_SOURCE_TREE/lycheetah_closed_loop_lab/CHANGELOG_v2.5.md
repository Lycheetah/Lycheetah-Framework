# Changelog — v2.5

- R15 closes the v2.4 request-metadata privacy gap by permitting only internally generated `lycheetah_operation_id` metadata in persisted request payloads.
- Enforced a strict top-level refund payload allow-list at the store layer; lower-level callers cannot reintroduce arbitrary persisted fields.
- Bounded HTTP response reads to 5 MiB and added oversized-response-after-commit recovery testing; default refund-list page size is 10.
- Added an atomic SQLite compare-and-swap `READY -> IN_FLIGHT` claim so only one local worker starts the initial POST.
- Replaced terminal-only state checks with an explicit lifecycle transition map, preventing direct `READY -> SUCCEEDED` writes and arbitrary state labels.
- Disabled caller-supplied time overrides by default; deterministic tests require a named opt-in.
- Required endpoint/clock opt-in flags to be actual Boolean values.
- 85 focused test methods passed; 202 combined retained+focused test methods passed; Python compilation and local recovery smoke passed.
- No hosted Stripe calls, real refunds, real credentials, upstream edits or complete upstream CI.
