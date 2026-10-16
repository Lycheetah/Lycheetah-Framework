# Pack Manifest v3.0

## Complete historical lab
- `r10_evidence_lease_v2_0/` through `r19_integrity_key_rotation_v2_9/`: retained research and local regression artifacts from the earlier closed-loop agent-safety work.
- `r20_external_checkpoint_v3_0/`: current external freshness/anti-rollback checkpoint reference implementation, CLI, 33-test suite, copied authenticated-store dependencies, source pin, threat model, scenario matrix, and test runner.
- Historical directories and logs are retained for traceability. The cumulative diagnostic attempt is incomplete because the R18 test process did not exit cleanly. Counts from separate invocations are not represented as a single upstream CI result.

## Current v3.0 verified claims
- 33 focused test methods pass in the current `run_v3_tests.sh` invocation.
- Checkpoint approval binds the exact primary database logical hash and previous anchor head.
- Restoring only the primary to a previous valid snapshot is detected while the separate anchor retains the newer checkpoint.
- Schema, data, checkpoint-chain, anchor authentication, approval reuse and CAS append races are tested.

## Not claimed
- No complete upstream Lycheetah checkout, branch, pull request, or CI run.
- No hosted Stripe API call or real refund.
- No security guarantee against an attacker who can restore both the primary DB and the local reference anchor together.
- No production-grade remote anchor connector.
