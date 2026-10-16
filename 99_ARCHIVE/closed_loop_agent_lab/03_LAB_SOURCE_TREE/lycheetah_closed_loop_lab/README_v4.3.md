# Current Research Snapshot v4.3

The newest research section extends the mTLS gateway with a shared same-host SQLite coordinator quota ledger.

The safety-relevant property tested is that per-coordinator active slots and request-rate tokens are no longer independently replenished by each gateway process when those processes share the same database file. Reservations and token updates run in SQLite write transactions; active slots are represented as expiring leases renewed by live request handlers.

Verification: 13 shared quota tests + 38 retained quorum tests + 49 mTLS gateway/witness tests = 100 passing test methods. Ten source pins and Python compilation also pass. No upstream repository changes or hosted service calls were made.

See `r33_shared_coordinator_quota_v4_3/README_v4.3.md` for setup and commands, and `r33_shared_coordinator_quota_v4_3/THREAT_MODEL_v4.3.md` for residual risks. This remains a local reference implementation, not production certification or cross-host coordination.
