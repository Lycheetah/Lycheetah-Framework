# Lycheetah v3.6 — Registry Clock Monotonicity

## Summary

v3.6 hardens the v3.5 external spent-challenge registry against backward wall-clock movement and unbounded accumulation of request-ID replay-cache records. It adds an HMAC-authenticated, non-decreasing clock floor; pins the replay-window configuration into that state; prunes expired request IDs only after the timestamp window has passed; guards active request IDs from ordinary SQL edits; and requires the challenge to be within its issue/expiry interval under the same clock sample used by the transaction.

## Run

```bash
cd r26_registry_clock_monotonicity_v3_6
./run_v3_6_tests.sh
```

## Results

- **11 new focused methods passed**.
- **82 retained + new test methods passed** in one invocation (71 retained v3.5 groups + 11 new tests).
- All retained source-pin checks passed.
- Five frozen v3.2 acceptance cases were reproduced as expected negative controls.
- The v3.4 and v3.5 local demos passed.

See `RESULTS_v3.6.md`, `API_CONTRACT_v3.6.md`, `THREAT_MODEL_v3.6.md`, and `CLOCK_ROLLBACK_RECOVERY_RUNBOOK.md`.

## Important limits

The clock high-water mark is stored in the registry SQLite database. A coherent restore of that database can restore the old high-water mark too; coordinated rollback of the primary and registry stores remains possible. The external registry also remains a local simulator—not a production independent service. No upstream source changed, no live provider was contacted, and upstream CI remains unrun.
