# Upstream Integration Plan v4.4

1. Obtain a full clean checkout of the reviewed upstream commit and a non-default branch; keep the upstream repo unchanged until the integration test is ready.
2. Port `shared_ingress_quota.py` and the small gateway option/process lifecycle change from `registry_gateway_mtls.py`.
3. Run the 15 shared ingress tests, the retained 13 coordinator-store tests, 38 quorum tests, and all 51 gateway/witness tests under the project's supported Python versions.
4. Test server shutdown with a connection mid-TLS and a slow/incomplete HTTP header; ensure leases release on all handler/error paths.
5. Run a process-pause test longer than TTL to measure and document the known stale-handler over-admission boundary. Do not claim lease TTL is a fence.
6. Validate operational topology: one local filesystem DB shared by the same service identity, matching config, WAL/SHM behavior, permissions, backup and power-loss semantics.
7. Keep default behavior unchanged when `shared_ingress_quota_db_path` is omitted. Only enable shared mode after operators understand this is same-host-only.

No branch, PR, upstream write, CI result, hosted service call, or deployment has been performed in this reference iteration.
