# Changelog v4.3

- Adds opt-in SQLite-backed per-coordinator active-request and rate quotas shared across gateway processes on one host.
- Adds transactional quota reservation, renew-and-expire active leases, boot-ID handling and persisted token buckets.
- Requires matching active/rate/TTL configuration across replicas; mismatches fail closed.
- Adds SQLite path, symlink, mode, parent directory and monotonic-clock handling checks.
- Adds 13 quota-store tests and two mTLS gateway integration tests.
- Retains v4.2 identity fairness and all quorum/witness regressions.
- No upstream source modifications or hosted service calls.
