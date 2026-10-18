# Failure Museum — Cycle 11

**Do not remove failures to make the presentation look better.**

## FM-11-01 — Rejection vanished between sessions

Observed in the v1.0 behavior: clicking reject returned `REJECTED`, but the decision lived only in the reviewer object. After process restart, the event ledger contained neither an admission nor a rejection record. Reproduced in `demo_review_journal.py`; fixed in *opt-in* `journal_v1` mode by a signed, persistent rejection.

## FM-11-02 — Approval can persist without journal entry if split across transactions

Explored as an injected `review_decisions` INSERT failure. Cycle 11 writes the admission event, approval nonce and decision journal inside one SQLite transaction. The test proves the attempted commit rolls back all three after the journal trigger fails. It does not simulate actual sudden power loss, filesystem faults or distributed writes.

## FM-11-03 — Valid-looking actor approval does not equal human attention

Persistent unresolved limitation. Login, a checked confirmation box, signed permits and measured screen time prove software events only. Named-human identity or substantive review are **not** established. Do not label automated fixture reviewers as human reviewers.

## FM-11-04 — Offline hash chain can be wholly replaced

Without an independently retained journal-head anchor, an attacker with full database access can truncate or replace the local history. The test demonstrates the independently anchored head detects tail deletion. External anchoring is not implemented by the gateway.

## FM-11-05 — Untrusted keys and rotation remain operational boundaries

The service requires the operator-provided HMAC key for decision verification. The append operation refuses to build on a previous chain whose signing keys cannot be checked. Long-lived key migration and separation of key custody from the reviewer process remain unimplemented.

## FM-11-06 — Journal integrity is not semantic truth

A perfectly signed decision can approve a mistaken interpretation of a source. This revision does not improve model inference, temporal RAG performance or CASCADE effectiveness. Independent extraction and human usability evaluations remain required.

## FM-11-07 — A local file transaction is not a distributed effect guarantee

SQLite `BEGIN IMMEDIATE` protects the local record against concurrent local writers and ordinary rollback conditions. This is not a distributed transaction, security certification, hardware-backed immutability or a proof of production filesystem reliability.

## FM-11-08 — Legacy history is not retroactively certified

Attempting to enable journal mode on a database that already contains unjournaled knowledge events raises an error. Migration with independently auditable provenance remains future work; prior events are not rewritten or backfilled as if signatures existed at their creation.

## FM-11-09 — Existing test suite emits connection lifetime warnings

The 254 tests pass, but inherited SQLite baseline and test-fixture code can emit `ResourceWarning` for database connections under Python 3.13. The warning is not treated as a passing security property. A later cleanup should prove explicit closure under every error path instead of merely suppressing warnings in the release output.
