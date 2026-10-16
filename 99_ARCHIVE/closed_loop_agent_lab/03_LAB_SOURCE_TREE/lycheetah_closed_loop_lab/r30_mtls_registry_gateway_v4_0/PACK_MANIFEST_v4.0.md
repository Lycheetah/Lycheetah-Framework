# Pack Manifest v4.0

## Scope

Coordinator-facing mTLS gateway addition to the local remote-witness quorum harness, carried forward from v3.9.

## Files of interest

- `registry_gateway_mtls.py` — new mTLS ingress gateway class/handler.
- `test_remote_witness_process.py` — 25 inherited witness-transport tests plus 14 v4.0 gateway integration/security tests.
- `test_registry_checkpoint_quorum.py` — 38 retained quorum/state/checkpoint tests.
- `SOURCE_PIN_v4.0.json` and `verify_source_pins_v4.0.py` — content fingerprints and verifier.
- `run_v4.0_tests.sh` — reproducible separate-process validation harness.
- `API_CONTRACT_v4.0.md`, `THREAT_MODEL_v4.0.md`, `UPSTREAM_INTEGRATION_PLAN_v4.0.md`, `RESULTS_v4.0.md`, `README_v4.0.md`, and `CHANGELOG_v4.0.md` — docs.

## Validation labels

- `PASS`: directly observed in this local run.
- `NOT RUN`: real hosted service, independent host or upstream CI activity not performed.
- Source pin refers to files shipped in this pack, not to a claim that all inherited files match current upstream source.
