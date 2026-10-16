# Verification Results v4.9

## Status: local reference suite passed

- Exact local source/document fingerprints verified: **31/31**.
- Python compilation: **PASS**.
- Baseline differential probe: **PASS**; expected availability/fairness delta observed.
- Shared ingress quota: **42 test methods passed**.
- Shared coordinator quota: **13 test methods passed**.
- Checkpoint quorum: **38 test methods passed**.
- mTLS gateway/remote witness lifecycle: **60 test methods passed across 15 isolated shards**; every shard reported zero errors, zero failures and no surviving non-main threads.
- Combined: **153 passing test methods**.
- Aggregate run log: `full_suite_v4.9.log`; machine-readable report: `results_v4.9.json`.

## Differential result

On the same local deterministic store scenario, a source making eight rapid connection attempts under a global budget of five uses all five tokens in the preserved v4.8 global-only baseline; the unrelated source is denied. With the v4.9 peer cap of two, the noisy source gets two attempts and six peer-bucket denials, while an unrelated source is admitted. After the unrelated peer is admitted, the snapshot shows about two shared global tokens remain; small fractional differences come from refill timing.

## Integrity and scope boundaries

The source-pin script checks exact hashes of 28 local code/test/document files and reports the observed upstream commit as historical context. These hashes are not a claim that the code is byte-identical to upstream. The baseline fixture is a preserved **local** v4.8 implementation. This is a deterministic local store and simulated gateway test, not Internet load testing.

No upstream source, branch or pull request was changed. No hosted service was called. Results are not upstream CI, external security audit, or production certification.
