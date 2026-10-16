# Pack Manifest v3.7

Version: `3.7`

- Standalone core pack: `lycheetah_registry_external_quorum_v3.7.zip`
- Complete research-history pack: `lycheetah_closed_loop_agent_lab_v3.7.zip`

Included core files:
- `registry_checkpoint_quorum.py` — new local quorum/checkpoint wrapper
- `test_registry_checkpoint_quorum.py` — 38 focused regression methods
- `spent_nonce_registry.py` — inherited local v3.6 registry implementation
- `checkpoint_witness_quorum.py` — retained helper, source-pinned
- `remote_anchor_http.py` — retained helper, source-pinned
- `demo_external_quorum_rollback_v3_7.py` — rollback demonstration
- `verify_source_pins_v3.7.py` — source pin verification
- source, API, threat model, scenario matrix, and upstream promotion guidance
- test/compile/pin-check logs and SHA-256 manifest

No hosted endpoint is contacted by the test suite. No upstream repository was modified.
