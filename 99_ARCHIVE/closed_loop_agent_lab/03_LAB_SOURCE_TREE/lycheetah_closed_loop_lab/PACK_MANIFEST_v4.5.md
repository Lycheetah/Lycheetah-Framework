# Pack Manifest v4.5

- `r35_process_bound_ingress_v4_5/shared_ingress_quota.py`: process-bound shared ingress store, schema/config v2.
- `test_shared_ingress_quota.py`: 20 focused tests.
- `registry_gateway_mtls.py`, `test_remote_witness_process.py`: gateway integration and remote-witness behavior.
- `shared_coordinator_quota.py`, `test_shared_coordinator_quota.py`: 13 coordinator quota tests.
- `registry_checkpoint_quorum.py`, `test_registry_checkpoint_quorum.py`: 38 checkpoint quorum tests.
- `run_gateway_suite_v4.5.py`: gateway suite runner with lifecycle check.
- `run_v4.5_tests.sh`: source pin, compile and modular suite runner.
- `SOURCE_PIN_v4.5.json`: hashes 14 source/runner files; it records a base commit, not upstream equivalence.
- `RESULTS_v4.5.md`, `THREAT_MODEL_v4.5.md`, `API_CONTRACT_v4.5.md`, `UPSTREAM_INTEGRATION_PLAN_v4.5.md` and raw suite logs.

Four local suite invocations passed: 20 + 13 + 38 + 51 = 122 methods. Local reference only; Linux same-host/same-PID-namespace SQLite authority; no upstream source or CI changes.
