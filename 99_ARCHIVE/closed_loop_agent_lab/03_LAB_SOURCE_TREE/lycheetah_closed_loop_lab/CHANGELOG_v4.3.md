# Changelog v4.3

- Adds opt-in SQLite-backed per-coordinator active-request and rate quotas shared across gateway processes on one host.
- Adds transactional quota reservation, lease heartbeat/expiry, boot-ID handling and persisted token buckets.
- Requires consistent active/rate/TTL config across replicas; mismatches fail closed.
- Adds filesystem hardening for DB path, symlink, owner-only mode and parent-directory write permissions.
- Adds 13 quota-store tests and two mTLS gateway integration tests.
- Retains v4.2 authenticated identity fairness and prior quorum/witness regressions.
- 100 local test methods pass across three suites; no upstream source modifications or hosted service calls.
