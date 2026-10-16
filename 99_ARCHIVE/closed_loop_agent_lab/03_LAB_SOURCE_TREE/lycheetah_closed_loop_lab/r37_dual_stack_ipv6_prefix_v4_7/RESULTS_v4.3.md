# Verification Results v4.3 — Shared Coordinator Quotas

## Final local verification

- Local source pin check: **PASS**, 10 fingerprints checked.
- Python compilation: **PASS** for all top-level Python files in the section.
- Shared quota store suite: **PASS**, 13 tests in 4.196s.
- Retained quorum suite: **PASS**, 38 tests in 6.042s.
- mTLS gateway / remote witness suite: **PASS**, 49 tests in 28.646s.
- Total: **100 test methods passed across three separate invocations**.
- Hosted service calls: **0**.
- Upstream repository or CI modified: **No**.
- Archive CRC is checked by the build script before deliverables are linked.

## v4.3-specific evidence

1. Separate SQLite store objects share active slots and rate tokens.
2. A coordinator's request-rate bucket persists after reconstructing the store and after a temporary gateway instance is replaced by another instance.
3. A stalled authenticated request on gateway A consumes the shared active slot; the same identity sent through gateway B receives a signed 429 without dispatch, while a different allowed principal can still succeed.
4. Two spawned OS processes race for one active slot using separate SQLite connections. Exactly one is admitted while the winner holds its lease.
5. A live lease heartbeat keeps the active slot reserved past its original TTL; a simulated crashed/no-heartbeat lease expires and can be reclaimed.
6. Mismatched quota configuration, database symlinks, insecure parent directory modes, and invalid identities fail closed.
7. Token buckets do not refill when a test clock moves backward; an OS boot-ID transition clears leases/buckets so monotonic timestamps are not compared across boots.
8. Aggregate snapshot data does not include coordinator SPIFFE identifiers.

## Interpretation

The tests establish the listed behaviors for this local reference implementation, on a host using SQLite semantics and the tested Python/runtime environment. They do not prove production deployment security or cross-host quota consistency.

## Boundaries

- The shared quota DB only coordinates processes on one host when they point to the same local DB path and use matching configuration.
- Pre-TLS active connection, direct peer IP and new-connection token quotas remain process-local.
- The shared DB is trusted local infrastructure. Filesystem controls reduce exposure but do not make a compromised same-UID process unable to tamper with it.
- Quota buckets reset at OS boot ID change because a persisted monotonic timestamp has no valid cross-boot meaning.
- A request handler that remains active after repeated heartbeat backend failures can outlive its lease TTL; request/dispatch deadlines and monitoring remain operational responsibilities.
- No production CA lifecycle, reverse proxy, OS resource cap, multi-host topology or upstream CI was tested.
