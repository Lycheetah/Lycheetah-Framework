# API Contract v4.5 — Shared Ingress Quota Store

## `reserve(peer_ip, auto_renew=None)`

- Canonicalizes a literal IP address.
- Requires `/proc/self/stat` PID to match the process PID and binds replica configuration to the Linux PID namespace inode.
- Requires the store to be used only by the OS process that initialized it.
- Atomically consumes a shared global rate token and reserves the global/per-peer active slot.
- Persists `lease_id`, peer IP, created/expiry times, owner PID, and process-start ticks in the same SQLite transaction.
- Returns `(lease, None)` on success or `(None, reason)` for quota denial.
- Raises `SharedIngressQuotaError` for authority/process-identity failure.

## Lease renew and release

- `renew(lease_id)` succeeds only for a lease owned by this OS process identity. An expired lease owned by a still-live process may renew: expiry alone does not revoke ownership.
- `release(lease_id)` removes only a lease owned by this OS process identity.
- An expired lease is reclaimed only when the owner process is proven dead or its PID has been reused. Unknown liveness is treated as alive/indeterminate.
- A forked child must instantiate a fresh store; inherited store mutations fail closed.
- A v4.4 schema-1 database is not migrated implicitly; config/schema mismatch fails closed.
- On OS boot-ID change, old monotonic lease and rate state is cleared and current PID-namespace configuration is adopted; same-boot namespace/config changes fail closed.

## Scope

Linux `/proc`, same host, same Linux PID namespace, same trusted SQLite file, matching shared configuration. Not a multi-host service, not cryptographic DB tamper resistance, and not a hard fence for arbitrary code execution after handler resume.
