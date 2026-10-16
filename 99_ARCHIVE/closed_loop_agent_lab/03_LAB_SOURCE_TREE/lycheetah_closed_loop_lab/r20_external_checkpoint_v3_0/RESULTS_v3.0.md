# Verification Results v3.0

**Date:** 2026-10-17 (Pacific/Auckland project context); Python 3.13 reference runtime.

## Focused suite

Command:

```bash
python -W error::ResourceWarning -m unittest -v test_external_checkpoint.py
```

Result: **33 test methods passed**.

Coverage includes no-anchor fail-closed startup, initial checkpoint and matching verification, stale primary snapshot restoration after a newer anchor, valid-but-uncheckpointed row state, schema drift, wrong DB integrity key, direct row tampering, exact digest-bound approval, database identity binding, expiry, wrong operator key, independent keys, anchor row/key-ID/approval-use tampering, one-use approval, chain sequence, row insertion order canonicalization, untrusted anchor key, CAS race with two competing appenders, CLI publish/verify with operator key absent in read-only verification, missing CLI anchor, and forged snapshot component rejection.

## Verified local conclusions

- A primary database restored to an older checkpoint while the latest anchor is preserved returns `STALE_SNAPSHOT`, `safe_to_continue=false`.
- A row-valid but uncheckpointed change returns `CHECKPOINT_MISMATCH`, `safe_to_continue=false`.
- Row tampering returns `PRIMARY_DATABASE_UNVERIFIED`; schema drift returns `SCHEMA_CHANGED`; a tampered/unverifiable anchor returns `ANCHOR_UNVERIFIED`.
- In the two-thread anchor compare-and-swap race, exactly one of two candidates using the same parent checkpoint can append.
- A read-only verification command does not require the operator approval key.

## Regression context

The v2.9 runbook's retained groups total 343 test methods in the v2.9 full runner (R10, R11, R12, R15, R16/R17/R18, plus 20 key-rotation tests). v3.0 adds 33 focused methods. The historical aggregate attempt is retained as `diagnostic_aggregate_attempt_v3.0.log`. It completed R10, R11, R12, and R15 normally and printed a successful R18 test summary, but its process did not exit cleanly. This release therefore does not claim a fresh monolithic aggregate pass.

## Not established

- No hosted Stripe calls, real refunds, upstream source modification, branch, PR, or complete upstream Lycheetah CI run.
- The SQLite reference anchor is not an independent remote/witness service. It detects primary-only rollback if its latest chain remains intact, but cannot detect a coordinated restore of both the primary and local anchor files to the same older valid state.
- The operator HMAC proves possession of a secret key, not the human identity or authority of the issuer.
- Production must replace `SQLiteReferenceAnchor` with an independently protected monotonic/CAS anchor service and rehearse recovery under crash/uncertain-append conditions.
