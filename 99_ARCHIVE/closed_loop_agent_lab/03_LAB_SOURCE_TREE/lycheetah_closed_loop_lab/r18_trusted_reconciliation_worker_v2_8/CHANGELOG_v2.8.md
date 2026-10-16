# Changelog v2.8

- Added a read-only trusted reconciliation worker for current provider refund retrieval.
- Added authenticated minimal operation ledger and provider observation digest.
- Enforced at the queue API that `DONE` requires a matching authenticated terminal ledger record for the exact operation, provider refund, target, amount/currency, account scope and event ID.
- Added migration audit: old `DONE` queue records without terminal proof are demoted to `MANUAL`; tampered authentication records fail closed.
- Added regression for terminal proof across restart, unproven legacy completion, transient reads, pending states, provider mismatch, and sanitized adapter failures.
- Added provider source notes and refreshed local HTTP smoke and verification results.
