# Complete Lab Manifest v4.3

- Current section: `r33_shared_coordinator_quota_v4_3/`
- Parent artifact: v4.2 authenticated coordinator fairness.
- New module: `shared_coordinator_quota.py`.
- Modified integration surface: `registry_gateway_mtls.py` with opt-in `shared_coordinator_quota_db_path`; default remains process-local.
- Tests: 13 shared quota, 38 quorum, 49 gateway/witness = 100 passing test methods in separate invocations.
- Source pins: 10 local reference file fingerprints.
- All top-level Python modules compile.
- Standalone package and complete historical lab ZIPs are CRC-checked at build time.
- Scope: same-host shared SQLite quota only; no distributed/multi-host quota claim.
- No upstream write, hosted API call, or production deployment.
