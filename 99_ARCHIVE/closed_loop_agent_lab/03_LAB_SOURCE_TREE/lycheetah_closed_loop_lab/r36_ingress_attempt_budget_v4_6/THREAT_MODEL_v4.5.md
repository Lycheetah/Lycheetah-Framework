# Threat Model v4.5 — Process-Bound Ingress Leases

## Threat addressed

A gateway handler can be paused longer than the ingress lease TTL, while another process sees expiry and reclaims the active slot. The original handler may later resume, making actual active work exceed the shared quota. PID interpretation can also be incorrect when replicas in different Linux PID namespaces share the same database file.

## Control

A lease is attributed to `(boot_id, PID, process start-time ticks)`. Replica config binds the Linux PID namespace inode and startup checks that the mounted `/proc` PID view matches `os.getpid()`. TTL expiry alone is insufficient for reclamation. The store reads Linux `/proc/<pid>/stat`:

- Same PID and same start ticks: owner is alive; retain its slot even when expired.
- Missing process or same PID with different start ticks: owner is proven dead/reused; reclaim only once the TTL has elapsed.
- Permission/read/parse ambiguity: do not reclaim.
- Different PID namespace or mismatched `/proc` view: fail closed.

Renew and release are scoped to the initializing process identity, and store methods that mutate quota state reject use after `fork()`.

A real OS boot change clears old monotonic time/lease state and updates namespace configuration; config disagreement in the same boot still fails closed. The test-only `boot_id` injection exists for deterministic tests; production callers should use the OS-derived boot ID.

## Tests

- Live owner past TTL cannot have its slot stolen by a second store.
- Dead child process's lease remains until TTL, then is reclaimed.
- A separate process cannot renew or release the owner's lease through the public API.
- A store inherited across fork refuses new reservation.
- PID-namespace identity is bound into the shared configuration; same-boot mismatch fails closed.
- Boot change clears stale monotonic state and can adopt a new PID-namespace identity.
- A v4.4 schema-1 store fails closed without implicit migration.
- Existing multi-process race still admits only one contender for one shared slot.

## Residual risks and trade-offs

- A live wedged process may pin quota indefinitely until it is recovered/restarted.
- This protects shared slot accounting; it does not kill or hard-fence a paused handler.
- `/proc` process identity is Linux-specific. On ambiguous liveness, the store fails safe for capacity by retaining the slot.
- Local SQLite file and directory remain trusted infrastructure.
- A compromised same-UID process or local administrator can still tamper with the DB.
- Only same-host processes in the same PID namespace sharing the exact DB path/configuration are coordinated.
- It does not provide distributed quota guarantees across hosts.
