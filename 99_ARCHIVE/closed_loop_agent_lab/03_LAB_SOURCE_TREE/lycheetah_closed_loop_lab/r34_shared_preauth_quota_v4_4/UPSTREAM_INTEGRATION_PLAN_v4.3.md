# Upstream Integration Plan v4.3

## Goal

Integrate the shared same-host quota authority as an opt-in extension of the bounded mTLS gateway without changing the existing v4.2 process-local default or registry business logic.

## Before any upstream write

1. Obtain a clean full checkout at the reviewed upstream commit and create a non-default branch.
2. Run `verify_source_pins_v4.3.py`; check the exact source revision is still applicable.
3. Run `run_v4.3_tests.sh all` in a clean environment.
4. Audit `ThreadingHTTPServer` lifecycle and confirm the shared SQLite file lives in an owner-only local directory, not a network filesystem.
5. Confirm every gateway replica uses the same DB path and identical active/rate/TTL values.

## Change set

- Add `shared_coordinator_quota.py`.
- Add opt-in `shared_coordinator_quota_db_path` and lease TTL to `registry_gateway_mtls.py`.
- Preserve process-local v4.2 behavior when no shared path is configured.
- Add store and cross-gateway integration tests.
- Document OS reboot reset, local single-host scope, and requirement for network-edge pre-TLS protection.

## Promotion gate

- All retained quorum tests pass.
- All retained remote witness and gateway tests pass.
- All shared store tests pass, including true multiprocess contention.
- Source/compile/zip checks pass.
- Deployment owner validates filesystem, process model, gateway stop/shutdown, WAL location and backup behavior.
- Separate production review decides whether a shared same-host SQLite store is an acceptable topology or whether an external distributed quota service is required.

## Not included

No upstream changes, branch creation, PR, deployed service, hosted API call, or cross-host quota claim has been made in this iteration.
