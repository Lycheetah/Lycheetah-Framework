# Pack Manifest v4.5

Core files:
- `shared_ingress_quota.py`: process-bound same-host/same-PID-namespace ingress quota ledger (schema 2).
- `test_shared_ingress_quota.py`: 20 tests including live-owner TTL retention, crashed-owner reclaim, cross-process ownership, fork guard, namespace config binding and old-schema rejection.
- `registry_gateway_mtls.py` and `test_remote_witness_process.py`: retained gateway integration and remote-witness tests.
- `test_shared_coordinator_quota.py`: retained coordinator quota tests.
- `test_registry_checkpoint_quorum.py`: retained quorum tests.
- `run_gateway_suite_v4.5.py`: lifecycle-checked gateway suite runner.
- `verify_source_pins_v4.5.py` / `SOURCE_PIN_v4.5.json`: local exact-artifact fingerprints.
- `run_v4.5_tests.sh`: reproducible suite runner.

Scope: local reference implementation only; Linux `/proc`; same host and same PID namespace using one trusted SQLite file. Not a hard cancellation mechanism or distributed quota service. See `THREAT_MODEL_v4.5.md` and `RESULTS_v4.5.md`.
