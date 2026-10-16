# API Contract v4.3 — Shared Coordinator Quotas

## Opt-in configuration

`MTLSAnchoredRegistryHTTPServer` accepts two additional parameters:

- `shared_coordinator_quota_db_path: str | None`: when omitted, v4.2 process-local quotas remain in use. When supplied, the authenticated coordinator active-request slots and token buckets use a shared SQLite ledger. The path must be absolute, reside in a directory owned by the service account and not group/world-writable, and the database itself is forced to mode `0600`.
- `coordinator_quota_lease_ttl_seconds: float`: must be finite and greater than `request_timeout_seconds`. Active reservations renew while handlers are executing. If a process crashes, an abandoned reservation becomes eligible for reclamation after its lease expires.

Every process sharing one database must use the same quota configuration. A mismatch refuses startup/reservation instead of silently multiplying or weakening the quota.

## Store protocol

`SharedCoordinatorQuotaStore.reserve(principal)` returns `(lease, None)` when admitted, or `(None, reason)` for a rate or active-slot denial. Database authority failures raise `SharedQuotaError`; the gateway maps these to signed HTTP 503 and does not dispatch the request.

`lease.close()` stops the renewer and releases the active slot. Leases expire if the owner crashes. Token buckets and active leases use monotonic time. A detected OS boot-ID change resets buckets and clears old leases, because monotonic timestamps cannot safely be compared across boots.

## Security properties in scope

- Across gateway instances/processes on the same host and sharing the same SQLite path, active limits and rate buckets are serialized in SQLite write transactions.
- Coordinator principals retain isolated buckets/active slots.
- A process restart during the same OS boot does not reset the persisted request-rate bucket.
- Duplicate or conflicting gateway configuration fails closed.

## Explicit non-guarantees

- This is not a multi-host/distributed quota service. Separate hosts or database paths have separate budgets.
- Global and per-IP pre-TLS controls remain process-local. They are not aggregated by this shared store.
- Authenticated coordinator quotas begin only after HTTP headers are parsed; pre-TLS controls must continue to bound slow headers and TLS handshakes.
- SQLite is trusted local infrastructure. A local administrator or process with write access to the quota database can interfere with quota state; the database is not cryptographically tamper-evident.
- On OS reboot, rate buckets reset because persisted monotonic timestamps no longer share a clock origin. This is an explicit boundary, not a claim of reboot-proof quota continuity.
- Lease heartbeats and TTLs provide recovery for crashed request handlers, not a proof that any downstream business operation is cancelled when a gateway thread dies.
