# Verification Results v2.9

## Focused tests

Command:

```bash
python -W error::ResourceWarning -m unittest -v test_integrity_key_rotation.py
```

Result: **20 tests passed**.

Coverage includes all three HMAC-authenticated tables, backup validity under the old key, restrictive backup permissions, successful webhook dedup after rotation, queue claim-token continuity, sequential rotations, wrong-key refusal, same-key refusal, overwrite prevention, separate inbox/queue/operation tampering, injected partial-rekey failure rollback, incomplete-schema refusal, and detection of a validly MACed database change between backup and write-lock acquisition.

## Regression context

The retained groups were re-executed as isolated commands and each produced a complete passing result: R10 49, R11 29, R12 39, R15 85, and R16-R18 121. The v2.9 rotation suite passed separately with 20 tests. Total: **343 test methods across separate isolated invocations**, not one monolithic invocation.

A wrapper attempt that chained all groups in one shell intermittently stalled after the prior groups while launching the v2.9 group. The runbook therefore ships the reliable focused command for the new tool, and the individual group logs are retained as evidence. No single all-groups pass is claimed. This does not replace the full upstream Lycheetah test suite.

## Smoke / scope

- Focused rotation tests use temporary SQLite files and synthetic test keys.
- No real key material or Stripe secrets are included.
- No Stripe hosted API requests or refunds were made.
- No upstream source or GitHub branch was modified.
- Test fixture timestamp and IDs are synthetic.

## Status

**Local reference utility verified to its stated boundary.** The migration is intentionally offline and single-key-at-a-time. Production use requires a maintenance window, external secret-manager controls, a backup/restore rehearsal, project-owner review, and upstream integration tests.
