# Results v4.8 — Hierarchical IPv6 Quota

## Final complete local run

Command: `./run_v4.8_tests.sh all`

Result: **PASS — 143 test methods across four suite groups, with 15 gateway lifecycle shards.**

| Suite | Tests | Result |
|---|---:|---|
| Shared ingress quota store | 33 | PASS |
| Shared coordinator quota | 13 | PASS |
| Registry checkpoint quorum | 38 | PASS |
| mTLS gateway lifecycle | 59 | PASS across 15 shards |
| **Combined** | **143** | **PASS** |

Every gateway shard reported zero errors, zero failures, and no surviving non-main threads. The shell run exited `0`. The complete run log is `full_suite_v4.8.log`; focused outputs are retained separately.

## New v4.8 differential

`differential_probe_v4.8.py` compared the preserved local v4.7 exact-/64 source fixture with the v4.8 hierarchical store using a leaf `/64`, aggregate `/56`, and aggregate active ceiling of two:

- v4.7 admitted all three test addresses from three different `/64`s within one `/56` under a per-leaf limit of one.
- v4.8 admitted two and denied the third with `ipv6-aggregate-connection-limit`.
- A peer under another `/56` was admitted into an independent aggregate bucket.

The paired probe passed and its machine-readable output is `differential_probe_v4.8.json`.

## New focused cases

- Atomic shared-SQLite aggregate reservations under 16 competing threads.
- Aggregate configuration fingerprint mismatch across store instances.
- Invalid or partially specified aggregate settings rejected.
- Dead-process lease reclamation removes associated aggregate occupancy.
- Process-local gateway quotas and shared-store wiring both enforce the configured aggregate cap.

## Verification

- Source pin checker: 26 exact local artifact fingerprints verified.
- Python syntax compile: passed.
- Shared ingress suite: 33 tests passed.
- Three focused gateway cases: passed; the full gateway suite also passed.

## Limitations

This evidence comes from local reference components and tests, not upstream repository CI, a public Internet load test, or production certification. The v4.7 baseline is a preserved local source fixture; local fingerprints do not assert byte identity with GitHub. Broader-prefix quotas are optional because they can group unrelated legitimate clients; they do not create an authenticated identity and do not replace edge, OS or network-layer DoS protections. The shared quota service remains same-host and same-PID-namespace SQLite infrastructure. No upstream file, branch or PR was changed and no hosted service was called.
