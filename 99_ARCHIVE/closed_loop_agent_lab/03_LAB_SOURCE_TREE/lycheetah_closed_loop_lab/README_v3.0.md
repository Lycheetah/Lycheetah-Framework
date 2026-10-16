# Lycheetah Closed-Loop Agent Lab v3.0 — External Freshness Anchor

The newest round attacks a gap explicitly named by the v2.8/v2.9 work: row HMACs detect editing of records by parties without the key, but cannot tell whether a database is an old, once-valid backup.

v3.0 adds a logical digest of the entire SQLite schema and table contents, a hash-chained anchor sequence in a separate store, independent anchor and operator keys, short-lived exact-state operator-HMAC approvals, one-use approval nonces, compare-and-swap checkpoint append, and a fail-closed startup gate.

**Focused verification:** 33 test methods pass under `python -W error::ResourceWarning -m unittest -v test_external_checkpoint.py`. Historical suites are archived as separate group logs. The latest cumulative diagnostic reached the R18 summary of 121 passing tests but the process did not exit cleanly, so this release does not claim a fresh monolithic aggregate pass or upstream CI.

The included SQLite anchor is a reference/test adapter only. Production anti-rollback requires an independent remote monotonic append-only/CAS store with a non-rollbackable high-water mark. Coordinated rollback of both local primary and anchor files is out of scope. No real Stripe calls/refunds and no upstream source changes were made.

Start at `r20_external_checkpoint_v3_0/README.md` and `r20_external_checkpoint_v3_0/THREAT_MODEL_v3.0.md`.
