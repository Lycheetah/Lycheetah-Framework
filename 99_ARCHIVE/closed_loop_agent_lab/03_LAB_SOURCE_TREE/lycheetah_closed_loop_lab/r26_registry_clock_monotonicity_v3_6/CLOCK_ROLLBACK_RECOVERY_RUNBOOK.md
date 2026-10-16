# Registry Clock Rollback / Integrity Recovery Runbook

This prototype intentionally stops if its clock goes backward or its authenticated clock state fails validation. Do not clear the clock row, edit the high-water value downward, delete the registry database, or restore an old snapshot merely to make requests work.

## First response

1. Stop accepting challenge register/consume requests and retain signed logs, process logs, database snapshots and service configuration.
2. Check the host's time source, NTP synchronization, virtualization clock settings, and any recent VM/container restore or host migration.
3. Compare the reported current UTC time with the authenticated `high_water_ms` and convert both to UTC for incident notes.
4. If time is temporarily behind a valid high-water mark, keep the service closed until trusted time has caught up. Do not force a lower clock floor.
5. If clock state is tampered, the storage key may be unavailable, or a database restore occurred, treat the registry as untrusted. Fail closed and preserve the evidence.
6. Resume only after an owner-approved recovery plan re-establishes monotonic state from an independently protected current checkpoint. This prototype does not implement that production recovery authority.

## Change replay-window policy

The configured clock/replay window is pinned to the authenticated clock state. Do not change it in-place. A production migration needs a versioned migration that preserves replay resistance across old/new timestamp acceptance windows; widening the window without preserving pruned request IDs may make previously stale signed requests valid again.

## Backup/restore warning

A restore of the registry database restores the clock high-water mark too. This runbook alone is not an anti-rollback anchor. Production requires an external monotonic checkpoint or an independently administered append-only/conditional-write authority.
