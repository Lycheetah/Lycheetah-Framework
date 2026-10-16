# Lycheetah Closed-Loop Agent Lab v4.3 — Shared Coordinator Quotas

v4.3 extends the bounded mTLS gateway with a transactional SQLite quota authority shared between gateway processes on the same host.

## New behavior

- Active-request slots and per-coordinator token buckets are reserved in SQLite write transactions.
- The same coordinator's quota is shared across gateway instances that use the exact same local database path.
- Rate buckets persist across process restarts during the same OS boot.
- Active requests renew a lease; crashed handler leases expire.
- OS boot-ID change resets active lease/rate state because monotonic time cannot be compared across boots.
- Replicas with conflicting limits or TTL fail closed.
- Database path and local filesystem checks restrict unsafe configurations.

## Tests

- Shared quota store suite: 13 tests.
- Remote witness / gateway suite: 49 tests.
- Retained quorum suite: 38 tests.
- Combined: 100 passing test methods across separate invocations.
- Python compilation, source pins and archive CRC are checked by `run_v4.3_tests.sh` and the build script.

## Run

```bash
./run_v4.3_tests.sh checks
./run_v4.3_tests.sh shared
./run_v4.3_tests.sh quorum
./run_v4.3_tests.sh gateway
# or `./run_v4.3_tests.sh all`
```

To enable shared quota mode, configure `shared_coordinator_quota_db_path` to the same absolute, local SQLite path for all gateway processes on a host. Keep the parent directory owned by the service identity and not group/world-writable. Use a local filesystem. This does not aggregate quotas across hosts.

## Boundaries

The default remains process-local if the shared DB path is omitted. This is a local reference implementation, not production-certified. Pre-TLS global/per-IP quotas remain process-local. No upstream source or CI was changed and no hosted service was contacted.
