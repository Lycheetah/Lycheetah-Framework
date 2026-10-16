# Verification Results v4.4

## Outcome

All four local suites completed successfully in separate invocations. The gateway suite's final runner report indicates clean shutdown with no surviving non-main threads.

| Suite | Methods | Observed run time | Result |
|---|---:|---:|---|
| Shared ingress quota store | 15 | 3.740 s | PASS |
| Shared coordinator quota store | 13 | 3.456 s | PASS |
| Retained checkpoint quorum | 38 | 5.783 s | PASS |
| Remote witness and mTLS gateway | 51 | 31.615 s | PASS |
| **Total** | **117** | Separate invocations | **PASS** |

## v4.4-specific evidence

- Fifteen ingress-store methods cover shared active slots, per-IP counts, the global token bucket, persistence, lease expiry/heartbeat, reboot and clock behavior, configuration consistency, aggregate-only snapshots, symlink/file mode/parent-directory safeguards, malformed peer input, and one multiprocess race in which exactly one contender is admitted for one shared slot.
- Two additional real mTLS gateway integration cases use separate gateway objects sharing one local SQLite database: one verifies the shared active limit, the other verifies the shared connection-rate budget.
- The gateway suite completed 51 tests and reported `surviving_non_main_threads=[]`.
- Fourteen exact local artifact fingerprints and Python compilation passed. ZIP CRC verification is recorded in the top-level archive verification JSON.

## Limitations

This evidence is from local reference code, not a clean upstream package install or upstream CI. The source-pin file records the observed base commit but does not claim file equivalence with upstream. No upstream files were changed, no PR was created, and no hosted service was used.

The quota store is same-host SQLite only. The DB and directory are trusted local infrastructure; the store does not provide cryptographic tamper resistance. A handler paused beyond its TTL could resume after reservation reclamation, so this is not a hard execution fence. Production certificate lifecycle, reverse proxy behavior, host firewalling, OS-level FD/cgroup limits, and multi-host deployment remain untested.
