# Verification Results v4.6 — Attempt-Based Ingress Quotas

## Final outcome

| Suite | Methods | Result |
|---|---:|---|
| Shared ingress quota store | 24 | PASS |
| Shared coordinator quota store | 13 | PASS |
| Checkpoint quorum | 38 | PASS |
| Gateway mTLS and remote witness integration | 53 | PASS |
| **Combined** | **128** | **PASS** |

The gateway lifecycle runner reported `LIFECYCLE_SUMMARY tests=53 errors=0 failures=0 surviving_non_main_threads=[]`.

## New v4.6 cases

- Active-slot denials spend the shared global connection-attempt token.
- Per-peer denials spend the shared global connection-attempt token.
- After denied attempts exhaust the token budget, freeing an active slot does not let a later attempt bypass the rate guard.
- IPv4 and IPv4-mapped IPv6 strings resolve to the same quota identity.
- The gateway process-local account uses the same canonical peer identity for reservation and release.
- A v4.5 replica sharing a same-boot database with v4.6 fails closed on policy configuration mismatch.
- Direct differential probe against preserved v4.5 source reproduced the prior behavior and confirmed the intended v4.6 delta.

## Measured baseline comparison

With global active capacity 1 and rate-token capacity 2: v4.5 admitted the first connection, denied one over-capacity attempt without charging its token, denied more attempts without charging, then admitted a new connection after the first slot released. v4.6 charges the denied attempt and rate-limits later attempts even after the slot becomes available.

The mapped identity probe also showed v4.5 treating `192.0.2.44` and `::ffff:192.0.2.44` as separate keys; v4.6 normalizes them and the second reservation is rejected by the per-peer quota.

## Test-run anomaly disclosed

The first buffered full gateway run timed out with output stopped at the shared-ingress rate integration test. The test and its immediately preceding shared-ingress integration test passed together in isolation. A later unbuffered full gateway run passed all 53 tests in 27.022 seconds with no surviving non-main threads. After changing the packaged runner to unbuffered mode, a complete `run_v4.6_tests.sh all` invocation passed all four suites (128 total), with the gateway lifecycle summary clean. The first timeout's cause was not established and is not silently discarded from the record.

## Verification boundaries

- 16 exact local reference fingerprints verified.
- Python compilation passed.
- ZIP CRC check is performed by the artifact builder.
- These are local reference artifact results, not upstream CI.
- The shared database and parent directory are trusted same-host infrastructure; scope is Linux `/proc` in one PID namespace.
- Rate limiting starts after TCP accept; it does not prevent SYN floods or upstream connection floods.
- The current mTLS gateway is IPv4-bind-only. The mapped-IPv6 canonicalization is tested for the generic quota store/helper, not as an externally reachable bypass on that listener.
- IPv6 prefix aggregation is not included.
- No upstream file or branch changed, and no hosted service was called.
