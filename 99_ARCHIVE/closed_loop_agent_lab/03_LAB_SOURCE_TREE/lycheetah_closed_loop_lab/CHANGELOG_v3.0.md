# Changelog v3.0 — External Monotonic Checkpoint

- Added logical fingerprinting of schema and data for the whole primary SQLite database, not just the three HMAC-authenticated Lycheetah tables.
- Added external sequence/hash-chain checkpoints, distinct anchor and operator keys, exact-fingerprint operator-HMAC-authenticated approvals, expiry and one-use approval IDs/nonces.
- Added startup readiness statuses for stale snapshots, uncheckpointed valid changes, schema drift, row-HMAC failure and anchor-chain failure.
- Added compare-and-swap append under an anchor transaction and primary SQLite writer lock during checkpoint publication.
- Added strict internal snapshot digest relationship checks so a caller cannot submit a made-up data digest alongside a valid logical digest.
- Added fail-closed CLI modes for fingerprint, verify and approved publish; read-only verification requires no operator key.
- Added 33 focused tests, including stale restore, schema drift, exact-state approvals and concurrent checkpoint CAS.
- Explicitly documented that the local SQLite anchor is only a reference adapter and cannot detect coordinated rollback of both files.
- No upstream changes or hosted Stripe calls.
