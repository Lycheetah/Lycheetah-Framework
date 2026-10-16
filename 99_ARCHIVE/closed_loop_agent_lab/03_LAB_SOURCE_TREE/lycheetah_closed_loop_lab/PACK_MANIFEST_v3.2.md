# Pack Manifest v3.2

## Current iteration
- `r22_checkpoint_quorum_v3_2/checkpoint_witness_quorum.py`: witness state machine, votes, quorum certificate checks, freshness reports, chain validation and equivocation evidence.
- `r22_checkpoint_quorum_v3_2/test_checkpoint_witness_quorum.py`: 31 focused unit/integration-style reference tests.
- `r22_checkpoint_quorum_v3_2/demo_quorum_v3_2.py`: runnable no-network example of two checkpoints, witness quorum and fresh-head verification.
- `r22_checkpoint_quorum_v3_2/remote_anchor_http.py`: source-pinned v3.1 primary-record verifier dependency.
- `API_CONTRACT_v3.2.md`, `THREAT_MODEL_v3.2.md`, `SCENARIO_MATRIX_v3.2.json`, `SOURCES_v3.2.md`, `RESULTS_v3.2.md`.
- `verification_logs_v3.2/`: logs for the current suite and each retained v3.1 test group, run as separate processes.
- `ISOLATED_REGRESSION_SUMMARY_v3.2.json`: 105 passing test methods across five separate invocations; does not claim one monolithic process or upstream CI.

## Claims and limits
- Three-of-four signatures are required for a fault budget of one.
- Fresh nonce-bound reads are separated from historical certificate verification.
- The `SQLiteCASGuard` is only a reference/test adapter. It is not secure against coordinated rollback of guard and witness state on the same trust domain.
- No live hosted anchor/Stripe operation or real refund took place. No upstream Lycheetah source changed.
