# Threat Model v4.3 — Shared Coordinator Quota Authority

## Objective

Prevent multiple gateway replicas on one host from independently granting each authenticated coordinator its own full active-request and request-rate budget. Retain v4.2 identity validation and pre-TLS admission controls.

## Attacker / failure model

- A valid coordinator sends concurrent requests through several gateway instances.
- A gateway process restarts while request-rate buckets should remain in force.
- A process dies while holding an active coordinator slot.
- Two replicas are configured with different limits but point to one DB.
- The quota DB is missing, corrupt, replaced by a symlink, unavailable, or placed in a group/world-writable directory.
- Several OS processes try to claim the same identity's last active slot simultaneously.
- The OS reboots, invalidating comparisons based on persisted monotonic timestamps.

## Controls

- SQLite `BEGIN IMMEDIATE` serializes token-bucket updates and active-slot reservations.
- The same transaction checks current active leases, refills the identity token bucket and inserts a lease.
- Per-request leases renew in a background heartbeat; abandoned leases expire after a TTL.
- A config fingerprint stored in SQLite requires all replicas to agree on active and rate limits and lease TTL.
- Database path must be absolute; symlinks are rejected where `O_NOFOLLOW` is supported; DB mode is set to `0600`; unsafe parent directory ownership/write modes are rejected.
- Store failures fail closed: the gateway issues a signed 503 and does not dispatch.
- Rate buckets and active leases reset only on observed OS boot-ID change, when monotonic values cannot be compared across boots.
- Operational snapshots return aggregate counts, not principal identifiers.

## Evidence

The reference suite tests distinct store instances, independent coordinator identities, rate persistence after reconstruction, active slot sharing across gateway objects, heartbeat renewal, stale-lease expiry, config mismatch, mode/symlink/parent directory controls, monotonic clock rollback, boot-ID transition, and two independent OS processes racing for one slot. Gateway integration tests exercise the shared SQLite path across distinct mTLS gateway instances.

## Boundaries / remaining risks

- Shared quotas cover only gateways on one host that share the exact DB path. Do not put SQLite on an unsupported network filesystem or treat this as cross-host coordination.
- Process-local pre-TLS caps, listen backlog and IP connection counts remain per instance, so total pre-auth ingress budgets scale with replica count.
- SQLite durability assumptions, filesystem semantics and power-loss behavior depend on the deployment storage stack.
- A process with write permission to the database can alter state. Owner-only filesystem permissions are the access boundary, not cryptographic row authentication.
- A live handler whose heartbeat cannot renew for longer than TTL can outlive its quota lease. Deployments must bound downstream handling time, monitor renewal failure and choose TTL/heartbeat settings accordingly.
- A reboot resets persisted buckets and active leases. If budgets must survive reboot or work across hosts, use a dedicated external quota service with authenticated, atomic reservation and explicit clock/failover semantics.
- No production CA/revocation policy, reverse proxy, OS-level FD limits, multi-host design, or upstream CI was tested.
