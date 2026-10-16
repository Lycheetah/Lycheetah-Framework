# API Contract v4.4 — Shared Ingress Quotas

## Gateway options

- `shared_ingress_quota_db_path: str | None`: when omitted, preserves the previous process-local pre-TLS behavior. When set, all same-host gateway instances must use the same absolute owner-protected local SQLite file.
- `ingress_quota_lease_ttl_seconds: float`: must be finite and greater than the configured handshake plus request socket timeouts. The store also requires identical limits and TTL across users of the DB.

The shared store uses the existing gateway limits `max_concurrent_connections`, `max_connections_per_ip`, and `max_new_connections_per_minute` to establish one aggregate budget across same-host instances.

## Store protocol

`SharedIngressQuotaStore.reserve(peer_ip)` returns `(lease, None)` if it reserves one global slot, one peer-IP slot, and one global new-connection token in one SQLite transaction. It returns `(None, reason)` on a policy denial. Store or config errors raise `SharedIngressQuotaError`; gateway admission drops the TCP connection without starting TLS.

A lease heartbeat renews expiry during a live handler. The request thread releases the shared lease at completion. A crashed process leaves a lease until expiry. The global rate token is consumed at admission even if the client does not finish TLS; this is intentional because pre-auth resources were allocated.

## Security properties in scope

- Two gateway instances sharing the same local DB cannot independently grant their own full active-connection and global request-rate budgets under the tested schedules.
- Per-peer active connection limits share the same transaction authority.
- Reservations are serialized by SQLite write transactions before request-thread creation/TLS handshake.
- Store errors fail closed; the DB path uses no-follow open where supported, a regular file, owner-only mode, and an owned non-group/world-writable parent directory.

## Non-guarantees

- No multi-host aggregation; each host/DB path remains its own quota domain.
- Process-local controls remain active, including per-instance connection/slow-header bounds.
- This does not authenticate peer identity before TLS; peer IP is taken from the accepted socket and can be affected by trusted proxy/NAT topology.
- Leases can be reclaimed after TTL if a handler process is paused longer than TTL and later resumes; this can over-admit in an extreme stall. A true fencing guarantee requires downstream participants to validate a fencing epoch or a design that doesn't reclaim live-but-stalled work.
- SQLite is trusted local state, not cryptographically tamper-evident against a process with write access.
- No upstream integration, deployed service or production certification is claimed.
