# Changelog v4.5 — Process-Bound Shared Ingress Leases

- Replaces TTL-only lease reclamation with TTL plus proven owner-process death.
- Binds each lease to Linux PID and process-start ticks.
- Binds shared config to PID namespace inode and rejects mismatched `/proc` PID view.
- Restricts renew/release to the owner process and rejects store mutation after fork.
- Handles boot changes by clearing stale monotonic lease/rate state and adopting current PID namespace configuration.
- Fails closed on same-boot configuration mismatch and v4.4 schema-1 database; no implicit migration.
- Adds 5 key test families: live owner past TTL, dead process reclaim, cross-process ownership, fork guard, and PID namespace/old-schema behavior.
- Verification: 122 test methods passed across four local suite invocations; 14 source fingerprints and Python compilation passed.
- Scope: Linux, same host, same PID namespace, shared trusted SQLite file; not hard process fencing or distributed quota service.
