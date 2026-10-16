# Verification Results v3.2 — Independent Witness Quorum

## Current focused suite

- Command: `./run_v3_2_tests.sh`
- Result: **31 test methods passed in 0.796 seconds**.
- Source: `focused_tests_v3.2.log`.
- The suite covers valid/invalid primary records, one-vote-per-sequence locking, CAS competition, local-vote tampering, local-ledger rollback while the independent guard survives, 3-of-4 quorum creation, fault-budget enforcement, one-key and two-key equivocation scenarios, complete chain continuity, nonce replay, stale reports, split-view freshness disagreement, and the check that currentness is not inferred from an old but valid certificate.

## Retained protocol regression groups

The v3.1 reference implementation and its historical groups were run in separate isolated processes. Their recorded results are:

| Group | Tests | Status | Log |
|---|---:|---|---|
| v3.1 external checkpoint | 33 | PASS | `verification_logs_v3.2/02_v3_1_external_checkpoint.log` |
| v3.1 remote HTTP group 1 | 14 | PASS | `verification_logs_v3.2/03_v3_1_remote_group_1.log` |
| v3.1 remote HTTP group 2 | 14 | PASS | `verification_logs_v3.2/04_v3_1_remote_group_2.log` |
| v3.1 remote HTTP group 3 | 13 | PASS | `verification_logs_v3.2/05_v3_1_remote_group_3.log` |

The evidence is **105 passing test methods across five separate test-process invocations** (31 current + 74 retained). This is an aggregate of isolated runs, not one monolithic process and not a claim about upstream CI. The no-network demo also completed successfully: two checkpoint records were verified in sequence, four of four witnesses reported the same nonce-fresh current head, and the chain tip matched it.

## Principal findings

For four pinned witnesses with a one-Byzantine-witness budget, three signatures are required. The threshold calculation is `q = floor((n + f) / 2) + 1`, provided `n >= 3f + 1`; it is tested across a matrix of roster sizes and fault budgets. This guarantees two quorums intersect in at least `f+1` identities. An honest witness's sequence lock prevents it from signing both sides of a same-sequence fork while its independent monotonic guard remains intact.

A quorum certificate verifies a checkpoint statement, but a prior signed certificate is not proof of *currentness*. A fresh, unpredictable nonce is required to ask witness heads now, and the client compares the verified chain tip with the fresh head quorum.

Two compromised signing identities exceed the configured fault assumption. The test constructs two conflicting quorum certificates and extracts their overlapping signed double-votes as evidence of equivocation.

## Limits

- `SQLiteCASGuard` is a local reference adapter; it is not tamper-proof or anti-rollback if both the guard and witness files/backups can be rolled back together.
- Independent failure domains, real remote CAS/high-water storage, key custody, roster governance, and a deployed witness HTTP service are not implemented.
- No real hosted anchor/Stripe calls or refunds occurred. No upstream Lycheetah code was changed and full upstream CI has not run.
