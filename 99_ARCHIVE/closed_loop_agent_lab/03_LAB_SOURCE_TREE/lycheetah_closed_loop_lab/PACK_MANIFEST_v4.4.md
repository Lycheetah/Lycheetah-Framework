# Pack Manifest v4.4

## Files and contents

- `r34_shared_preauth_quota_v4_4/shared_ingress_quota.py`: shared SQLite global/per-peer active socket reservations and global rate tokens.
- `r34_shared_preauth_quota_v4_4/registry_gateway_mtls.py`: opt-in pre-TLS shared-ingress hooks.
- `r34_shared_preauth_quota_v4_4/test_shared_ingress_quota.py`: 15 ingress-store tests including a spawned process race.
- `r34_shared_preauth_quota_v4_4/test_remote_witness_process.py`: 51 remote witness/gateway methods, including two v4.4 shared-ingress integration tests.
- `r34_shared_preauth_quota_v4_4/test_shared_coordinator_quota.py`: 13 prior coordinator quota tests.
- `r34_shared_preauth_quota_v4_4/test_registry_checkpoint_quorum.py`: 38 retained quorum tests.
- `r34_shared_preauth_quota_v4_4/run_gateway_suite_v4.4.py`: reproducible runner checks test outcome and clean thread shutdown.
- `r34_shared_preauth_quota_v4_4/SOURCE_PIN_v4.4.json`: hashes the local reference sources and runner scripts.
- Test logs, API contract, threat model, results and upstream integration plan are included in the section folder.

## Verification summary

117 test methods passed across separate invocations (15 + 13 + 38 + 51). Source pins and Python compilation passed. ZIP CRC checks are performed at build time.

## Interpretation limits

The base commit is recorded for reproducibility; no file is claimed to have been written upstream. Local hashes prove archive consistency, not production security. The quota authority is shared only by gateway processes on one host using the same trusted SQLite file.
