# Pack Manifest v2.0

- `README.md` — quick start, scope and limits.
- `durable_action_broker.py` — v1.9 lab reference with explicit pre-effect-denial handling and provider outcome lookup recovery.
- `evidence_lease.py` — SQLite evidence authority, HMAC lease token, lease-aware adapter and cooperating idempotent provider model.
- `test_evidence_lease_integration.py` — 22 focused test methods including concurrency, faults, lease expiry, replay and policy semantics.
- `test_r9_baseline_regression.py` — preserved v1.9 suite (27 test methods, including the negative-control TOCTOU reproduction).
- `all_tests.log` — combined unittest output.
- `run_evidence_race_experiment.py` — repeatable 200-round concurrent update/lease experiment.
- `evidence_race_results_v2_0.json` — machine-readable race outcomes.
- `RESULTS_v2.0.json` — aggregated machine-readable test/experiment summary.
- `BASELINE_VS_LEASE_v2.0.md` — side-by-side interpretation of the open v1.9 negative control and the v2.0 lease design.
- `reference-diff-v1.9-to-v2.0.patch` — delta between the two local broker reference files; not an upstream-ready patch.
- `DESIGN_AND_THREAT_MODEL_v2.0.md` — protocol design and assumptions.
- `FAULT_MATRIX_v2.0.md` — covered/remaining fault cases.
- `UPSTREAM_INTEGRATION_PLAN_v2.0.md` — real integration stages and promotion gates.
- `STUCK_IN_FLIGHT_RUNBOOK.md` — safe recovery steps for ambiguous provider outcomes and pinned evidence leases.
- `VERIFICATION_RESULTS_v2.0.md` — evidence boundaries and exact test result.
- `CHANGELOG_v2.0.md` — summary of changes.
- `SOURCE_PIN_v1_9.json` — upstream source revision read before the reference implementation was developed.
