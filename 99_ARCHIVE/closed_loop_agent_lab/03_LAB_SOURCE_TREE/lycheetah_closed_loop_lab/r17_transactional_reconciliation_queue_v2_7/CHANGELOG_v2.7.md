# Changelog — v2.7

- Added a durable reconciliation-job table to the signed webhook inbox.
- Made inbox row + job row part of the same SQLite transaction.
- Added HMAC-authenticated job rows, one-use worker claims, lease expiry recovery, bounded retry/backoff and manual escalation.
- Bound job dispatch and completion to the inbox's configured platform/Connect account scope.
- Added fail-closed migration/backfill for existing inbox rows after verifying their row HMAC.
- Expanded tests for atomic rollback, migration, account-scope switching, queue tampering, concurrency and retry limits.
- Updated concurrent duplicate-ingestion regression to require one queue job.
- Added HTTP regression: queue storage failure returns `503` and does not acknowledge the event.
- Kept the core rule: webhook event status is only a reconciliation signal; only authenticated current-provider retrieval may inform a separate operation-state update.
- Documented an intermittent hang in the retained R15 aggregate-runner path; all suite groups passed separately, but the single cumulative runner has not been established as reliable.
