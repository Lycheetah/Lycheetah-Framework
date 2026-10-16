# Upstream Integration Plan — v3.7

This pack is an external reference prototype. No branch or upstream source has been modified.

## Proposed integration sequence

1. Create a clean non-default branch from upstream commit `8ae1b367dcf09997e82ce66f9ad5d30ff36e5d65` after repository write access is available.
2. Verify source fingerprints for inherited modules before patching; inspect current upstream versions and do not overwrite any changed source.
3. Add the quorum wrapper behind an explicitly experimental feature flag; preserve direct registry behavior unless the caller opts into the guarded adapter.
4. Run existing registry, nonce, clock, HTTP, package-install and CLI tests before the new suite.
5. Run full tests on Linux and Windows; replace `fcntl.flock` or guard the feature as POSIX-only.
6. Replace in-process witness objects with separately deployed witness services. Separate hosts, administrators, key-management systems, backups, and recovery procedures must be demonstrably independent.
7. Run one-witness failure/equivocation, network partition, quorum loss, client restore, registry restore, and coordinated restore of two versus all trust domains.
8. Establish a documented operator recovery process before serving persistent challenges or nonces in a real deployment.

## Promotion criteria

- Source-compatible patch passes exact upstream tests and package CI.
- No success response is returned unless mutation state is visible and the current quorum agrees.
- Every relevant state-changing result is checkpointed, including deterministic rejection outcomes if the registry mutates replay state.
- Lost response, partial publish, process restart and retry recover without false success.
- Real witness administrative separation is demonstrated, not just simulated by separate local SQLite files.
- An independently reviewed backup/restore and key-recovery procedure can detect each rollback scenario.
