# Verification Results v4.5 — Process-Bound Ingress Leases

## Outcome

All four local suites completed successfully against the final v4.5 sources in separate invocations.

| Suite | Methods | Run time | Result |
|---|---:|---:|---|
| Shared ingress quota store | 20 | 7.704 s | PASS |
| Shared coordinator quota store | 13 | 3.237 s | PASS |
| Checkpoint quorum | 38 | 6.709 s | PASS |
| Remote witness and mTLS gateway | 51 | 35.366 s | PASS |
| **Total** | **122** | Separate invocations | **PASS** |

The gateway runner additionally emitted `LIFECYCLE_SUMMARY tests=51 errors=0 failures=0 surviving_non_main_threads=[]`. Two shared-ingress gateway integration tests were run again in isolation on final code; both passed in 9.533 seconds total. The separate focused run is additional coverage and is not added to the total above because those methods are already included in the 51-test suite.

## New v4.5 controls exercised

- A lease owner remains counted after expiry if its PID and process-start ticks still match; a second process cannot steal its slot.
- A crashed process's lease is reclaimed only after TTL and proven owner death.
- A process cannot renew or release another process's lease through the public API.
- Stores inherited across `fork()` fail closed until the child initializes its own store.
- Shared configuration includes the Linux PID namespace inode, preventing replicas in different PID namespaces from silently interpreting the same stored PIDs.
- A `/proc` PID-view mismatch fails closed.
- A prior-boot namespace identity can be cleared on boot-ID change; same-boot namespace/config disagreement fails closed.
- A v4.4 schema-1 database is not implicitly migrated; it fails closed on config mismatch.
- The two shared-ingress mTLS gateway integration tests passed on final code.

## Artifact checks

- 14 exact local source fingerprints verified.
- Python compilation passed.
- ZIP CRC checks are performed by the packager.

## Boundaries

This is local reference evidence, not upstream CI or production certification. The database and directory remain trusted local infrastructure. Scope is Linux `/proc`, same host, same PID namespace, exact shared SQLite path, and matching configuration. A live wedged process may pin quota, preferring capacity loss over over-admission. This is not a hard execution fence for arbitrary code that resumes, and not a distributed quota service. No upstream files or pull request were changed and no hosted service was called.
