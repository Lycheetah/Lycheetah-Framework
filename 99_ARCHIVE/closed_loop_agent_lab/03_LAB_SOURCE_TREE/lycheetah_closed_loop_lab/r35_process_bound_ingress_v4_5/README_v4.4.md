# Lycheetah Closed-Loop Agent Lab v4.4 — Shared Pre-TLS Quotas

v4.3 shared authenticated coordinator quotas but retained per-process pre-TLS connection limits. With multiple gateway replicas on one host, those earlier caps could be multiplied by replica count. v4.4 adds an opt-in shared ingress quota store to address that specific gap.

## New behavior

- Shared aggregate active connection limit across gateway instances using the same SQLite file.
- Shared active connection count per canonical peer IP.
- Shared global new-connection token bucket across replicas.
- Reservations atomically check the aggregate limit(s), rate budget, and insert a lease before TLS handshake / thread creation.
- Lease heartbeat and expiry permit cleanup after a handler process crashes.
- Configuration mismatch, database error, untrusted parent directory, symlink path, and invalid peer input fail closed.
- Process-local v4.3 safeguards remain active in addition to the shared limits.

## Run

```bash
./run_v4.4_tests.sh checks
./run_v4.4_tests.sh ingress
./run_v4.4_tests.sh coordinator
./run_v4.4_tests.sh quorum
./run_v4.4_tests.sh gateway
./run_v4.4_tests.sh all
```

To enable the feature, set `shared_ingress_quota_db_path` to the same absolute, owner-only local SQLite path for each gateway process on the host. Use identical active/per-IP/rate limits and TTL across replicas. `ingress_quota_lease_ttl_seconds` must exceed handshake plus request socket timeouts. The option is off when the path is omitted.

## Evidence

The local reference suites cover 15 shared ingress store methods, 13 shared coordinator quota methods, 38 quorum methods, and 51 remote witness/gateway methods: 117 passing methods when run as separate invocations. The gateway integration tests use two gateway objects and one DB; the store race uses two spawned OS processes.

## Boundaries

This does not create cross-host quotas or a guarantee against a handler paused longer than its TTL resuming after lease reclamation. SQLite is trusted local infrastructure and row-level tamper resistance is not claimed. Process-local caps still exist as an additional conservative layer. `request_timeout_seconds` is a socket I/O timeout, not a complete hard wall-clock cancellation for all server-side logic. No upstream CI, production CA lifecycle, proxy, host firewall, cgroup/FD limits, or distributed quota service was tested.
