# v3.0 Standalone Pack Manifest

- `external_checkpoint.py`: snapshot, state approval, hash chain, local reference anchor, and startup gate.
- `external_checkpoint_cli.py`: CLI that keeps key material in environment-provided secret inputs and outputs no keys.
- `test_external_checkpoint.py`: 33 adversarial tests.
- `run_v3_tests.sh`: reproducible compile + focused suite.
- `operation_ledger.py`, `stripe_webhook_inbox.py`, `integrity_key_rotation.py`: copied v2.9 test dependencies.
- `THREAT_MODEL_v3.0.md`, `RESULTS_v3.0.md` / `RESULTS_v3.0.json`, `SCENARIO_MATRIX_v3.0.json`, `SOURCE_PIN_v3.0.json`, `REGRESSION_SCOPE_v3.0.md` and retained diagnostic/history logs.

Reference implementation only. The SQLite anchor must not be mistaken for a remote, rollback-proof service.
