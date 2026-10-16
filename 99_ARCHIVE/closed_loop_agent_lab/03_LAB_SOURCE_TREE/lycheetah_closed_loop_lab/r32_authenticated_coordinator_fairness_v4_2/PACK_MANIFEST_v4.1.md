# Pack Manifest v4.1

- Version: 4.1
- Parent: v4.0 Coordinator mTLS Registry Gateway
- New scope: bounded pre-TLS resource admission for coordinator-facing gateway.
- Main implementation: `registry_gateway_mtls.py`
- Main integration suite: `test_remote_witness_process.py`
- Retained quorum suite: `test_registry_checkpoint_quorum.py`
- Source pin manifest: `SOURCE_PIN_v4.1.json`.
- Runner: `run_v4.1_tests.sh` (run each test suite as a separate invocation).
- Docs: API contract, threat model, results and upstream integration plan.
- Default admission config: 32 global active connections, 16 per direct peer IP, 120 connection tokens/minute, backlog 64.
- Validation: 8 source pins; 38 retained tests; 44 gateway/witness tests; 82 combined methods; compile pass; archive CRC pass.
- No live/hosted service calls; no upstream source files or CI altered.
- Provenance note: inherited implementation files are local reference-harness components, not claimed to be identical to current upstream source files.
