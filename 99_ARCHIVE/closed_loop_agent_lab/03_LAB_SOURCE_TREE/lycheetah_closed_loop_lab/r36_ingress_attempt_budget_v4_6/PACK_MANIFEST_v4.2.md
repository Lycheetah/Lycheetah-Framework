# Pack Manifest v4.2

- Version: 4.2; parent: v4.1.
- Scope: authenticated coordinator-level dispatch fairness atop bounded mTLS ingress.
- Main implementation: `registry_gateway_mtls.py`.
- Integration suite: `test_remote_witness_process.py`.
- Retained suite: `test_registry_checkpoint_quorum.py`.
- Source pin manifest: `SOURCE_PIN_v4.2.json` (8 files).
- Test runner: `run_v4.2_tests.sh`; run quorum and gateway invocations separately.
- Default pre-TLS limits: 32 active connections, 16 per direct peer IP, 120 new connections/minute, listen backlog 64.
- Default authenticated limits: 8 active dispatches/coordinator and 60 request tokens/minute/coordinator.
- Validation: source pin pass; compile pass; 38 quorum tests; 47 gateway/witness tests; 85 total methods.
- No live or hosted service calls. No upstream source/CI change.
- Limit: process-local quotas, not distributed fairness or production certification.
