# Changelog — v2.5

- Reject arbitrary caller-supplied Stripe refund metadata before durable write. Only the adapter's internal operation ID is sent/persisted for reconciliation.
- Extend privacy regression tests to inspect SQLite raw rows and prove test email/token/free-text markers do not enter the ledger.
- Add explicit malformed/non-object metadata rejection tests.
- Create/open the SQLite operation database as an owner-only file on POSIX, reject symlink database paths, and reject `:memory:` because this store opens a new SQLite connection per operation and requires durability.
- Preserve v2.4 provider response allow-listing, secret-free errors, `IN_FLIGHT` recovery state, target preflight, idempotency cutoff, and reconciliation behavior.
- Focused suite: 81/81 passed. Retained R10-R12 plus R15: 198/198 passed. Loopback lost-response smoke passed. Python compilation passed.
- No hosted Stripe calls or real refunds. No upstream source changes. No full upstream CI.
