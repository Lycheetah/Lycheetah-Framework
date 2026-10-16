# Changelog v3.4 — Durable Freshness Challenge Lifecycle

- Added persisted, one-use freshness challenges and bind them to database identity plus a fingerprint of protocol version, anchor/witness public-key roster, fault budget, report clock-skew limit, and TTL.
- Authenticated each challenge row with HMAC and fail closed on direct edit, wrong key, changed policy, or incompatible ledger schema.
- Verify signed chain and raw current-head witness reports before atomically consuming the challenge with one conditional transaction.
- Added restart, expiry, policy/roster mutation, wrong database, concurrent replay, malformed reports, schema mismatch, and tamper tests.
- Added an explicit negative control proving whole-database rollback permits replay even with authenticated row fields. This is a known blocker for production use until a separately administered non-rollbackable store is integrated.
- Corrected and reran the frozen v3.2 baseline repro harness; all five historical acceptance cases reproduce against v3.2.
- 56 combined local tests pass, including the one deliberate rollback negative control. No upstream modifications or hosted API calls.
