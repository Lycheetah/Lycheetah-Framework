# v4.5 — Process-Bound Shared Pre-TLS Leases

v4.4 used a lease TTL to reclaim stale shared ingress reservations. A live process can be paused longer than that TTL and later resume after another gateway has reclaimed its slot. v4.5 changes reclamation from **TTL-only** to **TTL plus proven owner-process death**.

Each lease records Linux PID and `/proc/<pid>/stat` start-time ticks. Shared configuration also binds the Linux PID namespace inode, so all participants must run on the same host and in the same PID namespace. A store that sees a mismatched `/proc` PID view or is used after `fork()` fails closed. An expired lease is reclaimed only if the owner is gone or its PID was reused; if liveness is uncertain, the slot is retained.

## Verification

- Shared ingress: 20/20 tests passed.
- Shared coordinator quota: 13/13 tests passed.
- Checkpoint quorum: 38/38 tests passed.
- Remote witness and mTLS gateway: 51/51 tests passed on final v4.5 code, including a clean lifecycle summary with no surviving non-main threads.
- **122 total test methods passed across four separate suite invocations.** Source fingerprints and Python compilation also passed.

## Trade-off

This prioritizes quota safety over automatic recovery. A live but wedged process may retain its reservations after TTL until it resumes/releases them or an operator restarts it. TTL is a cleanup grace period after owner death, not a hard cancellation mechanism. This is not distributed fencing and cannot forcibly stop arbitrary work already executing in a surviving process.

The lease schema/config signature changes to schema 2. Existing v4.4 stores should fail closed on configuration mismatch; deploy a new DB path or perform an explicit controlled migration after draining old gateway instances. Do not hand-edit the DB.
