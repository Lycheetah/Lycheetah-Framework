# Pack Manifest v3.8

Artifact: Remote Witness Process Boundary reference prototype.

- 4 witness subprocesses tested over authenticated loopback HTTP.
- 17 new process/HTTP tests passed.
- 38 retained v3.7 quorum tests passed.
- 55 methods passed across two separate invocations.
- Source pin check and Python compilation passed.
- No hosted service calls, no upstream modifications.

Primary files: `remote_witness_http.py`, `test_remote_witness_process.py`, `API_CONTRACT_v3.8.md`, `THREAT_MODEL_v3.8.md`, `RESULTS_v3.8.md`, `UPSTREAM_INTEGRATION_PLAN_v3.8.md`.

Security note: processes run on one host and use loopback HTTP + per-witness HMAC; this is not a production distributed trust service.
