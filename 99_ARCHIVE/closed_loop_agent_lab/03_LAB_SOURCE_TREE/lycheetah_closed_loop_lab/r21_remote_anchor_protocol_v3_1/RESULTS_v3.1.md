# Results — Remote Anchor Protocol v3.1

## Summary

The v3.1 reference implementation introduces an HTTP request/response protocol around the previous local checkpoint model. It tests signed operator approval, authenticated client requests, server signatures, compare-and-swap history appends, idempotent request IDs, and recovery when POST outcomes are ambiguous.

## Recorded local tests

All groups below exited with status `0` and printed `OK` in their individual recorded runs:

| Test command | Cases | Time |
|---|---:|---:|
| `python -W error::ResourceWarning -m unittest -q test_external_checkpoint.py` | 33 | 12.894 s |
| `python -W error::ResourceWarning run_remote_group1.py` | 14 | 8.923 s |
| `python -W error::ResourceWarning run_remote_group2.py` | 14 | 8.964 s |
| `python -W error::ResourceWarning run_remote_group3.py` | 13 | 7.629 s |
| **Total** | **74** | **38.410 s** |

Exact stdout excerpts are retained in `test_logs/`. Python compilation and ZIP CRC verification were also run during packaging.

## Important runner note

A single combined shell invocation was interrupted by this environment's tool/process time limit while it was running the multi-group script. Each test group was therefore executed separately and independently; all four completed successfully with their own process exit status `0`. The checked-in `run_v3_1_tests.sh` remains a normal convenience runner for a host that permits the full ~40-second run.

## Behaviors covered by the v3.1 protocol suite

- Successful publish creates one signed record.
- Lost response before/after commit is resolved with stable request ID and authoritative status lookup.
- An unavailable lookup leaves the operation `UNKNOWN` rather than claiming failure or success.
- Same request ID + same body returns the original record; same ID + changed body conflicts.
- Concurrent publishers competing against the same sequence/head yield one CAS winner.
- Malformed/replayed request authentication, modified approval signatures, unknown key IDs, expired approvals, body tampering, response tampering and redirect forwarding are refused.
- Server restart can resolve a committed operation through its durable request index.
- Service history/request/approval indexes are cross-checked; orphan request-index entries cannot masquerade as a committed checkpoint.
- Local outbox tampering and attempts to rewrite terminal states are refused.

## What is not proven

- No production remote service or WORM store exists in this artifact.
- The simulator's SQLite data can be rolled back with its surrounding environment. Detection of coordinated rollback of the anchor, keys, and all external records requires an independent trust domain/high-water mark.
- No actual remote host, TLS certificate, key management service, service availability, database failover, or backups/restore drills were tested.
- No Stripe API calls or refunds were made.
- The full Lycheetah upstream package suite and CI were not run; the 33 regression tests are the v3.0 checkpoint tests retained in this pack.
- No upstream repo branch/source changes or pull request were created.
