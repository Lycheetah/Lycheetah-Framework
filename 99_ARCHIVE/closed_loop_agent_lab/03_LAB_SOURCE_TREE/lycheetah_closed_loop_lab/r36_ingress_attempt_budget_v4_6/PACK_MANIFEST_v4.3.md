# Complete Lab Manifest v4.3

- Current section: `r33_shared_coordinator_quota_v4_3/`
- Parent artifact: v4.2 authenticated coordinator fairness.
- New module: `shared_coordinator_quota.py`.
- Modified integration surface: `registry_gateway_mtls.py`, optional shared SQLite path and request leases.
- Tests: 13 quota-store, 49 gateway/witness, 38 quorum = 100 test methods, run as separate invocations.
- Source pins cover inherited protocol helpers and the exact v4.3 gateway/test implementation.
- Scope: shared quota state for same-host gateway processes only. Not a distributed quota service.
- No upstream write, hosted API call, or production deployment.
