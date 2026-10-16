# Changelog v2.9

- Added offline atomic re-signing of v2.8 webhook inbox, reconciliation queue, and operation-ledger HMAC rows under a replacement local integrity key.
- Added full preflight verification, a protected SQLite backup, exclusive-lock revalidation, logical fingerprint comparison against the backup, and post-write verification before commit.
- Added fault-injection tests to prove a failure after some re-sign attempts rolls back every table.
- Added refusal cases for a wrong key, pre-existing tamper in each authenticated table, incomplete schema, same-key request, existing backup path, and a database changed between backup and exclusive lock.
- Added environment-based base64 key loading and read-only CLI verification mode. The CLI never takes key bytes as command-line arguments and never prints keys.
- Explicitly documented downtime, restore, stale backup, HMAC and upstream-integration limits.
