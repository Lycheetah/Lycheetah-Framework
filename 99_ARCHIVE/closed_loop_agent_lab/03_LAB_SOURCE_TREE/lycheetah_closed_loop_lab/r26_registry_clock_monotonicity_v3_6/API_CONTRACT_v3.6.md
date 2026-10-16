# API Contract v3.6 — Registry Clock Monotonicity and Replay-Window Housekeeping

## Purpose

v3.6 hardens the v3.5 spent-challenge registry simulator against one additional class of local operational failures: backward wall-clock movement and unbounded accumulation of authenticated request IDs.

## Normative behavior

1. The service samples its clock only after it acquires `BEGIN IMMEDIATE`, so requests are ordered by the same transaction boundary that advances the clock state.
2. After request authentication succeeds, a singleton clock record is created or advanced in the same transaction as request-ID insertion and route processing.
3. The clock record authenticates four fields: singleton ID, `high_water_ms`, `prune_before_ms`, and the fixed `replay_window_ms` configuration.
4. Any current clock below the authenticated high-water mark is rejected as `registry-clock-rollback`. Tampered or incompatible clock-state fields fail closed.
5. The replay-window configuration is pinned into the HMAC-authenticated clock state. A configuration change fails closed rather than widening the timestamp acceptance window after old request IDs have been pruned.
6. Request IDs remain immutable while they are within the active replay window. SQLite triggers prohibit updates and prevent deletion until a request timestamp is older than the persisted prune floor.
7. After advancing the clock, the service prunes request IDs older than `now - replay_window_ms`. Old signed requests then fail timestamp validation even though their cache row has been removed, provided the registry clock/ledger has not itself been rolled back.
8. Challenge consumption is checked against the one validated clock sample used for the transaction. A registered challenge cannot be consumed before `issued_at_ms`, or at/after `expires_at_ms`.

## Failure modes

- `registry-clock-rollback`: service fails closed; do not lower the floor or delete the clock row to recover.
- `registry-clock-state-integrity-invalid` / other `registry-clock-state-*`: halt request processing and investigate the persisted state and key custody.
- `registry-clock-window-config-changed`: do not silently change the replay window. Use a versioned migration/re-key plan.
- `registry-request-nonce-schema-incompatible`: stop and perform a reviewed schema migration; no automatic destructive migration is attempted.

## Retention

Challenge rows remain append-only and are not automatically deleted in this prototype. They record spent nonces and avoid re-registration of an expired nonce. Request-ID replay-cache entries are pruned once strictly older than the authenticated replay cutoff. Peak cache size is still proportional to accepted request traffic during the replay window; production needs request rate limits, monitoring, and capacity planning.

## Trust boundary

This protocol only detects wall-clock rollback and request replay while the persisted registry state remains current. Restoring an older copy of the registry database can restore an earlier clock high-water mark and request-ID cache. Coordinated rollback of the primary and registry databases remains outside this local prototype's guarantee and requires a separately administered monotonic/append-only anchor.
