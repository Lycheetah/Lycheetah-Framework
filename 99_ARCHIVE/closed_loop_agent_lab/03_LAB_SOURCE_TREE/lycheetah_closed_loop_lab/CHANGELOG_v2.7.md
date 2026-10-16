# Changelog — v2.7

R17 introduces a durable transactional reconciliation queue to the signed webhook inbox.

- Enqueue the follow-up task in the same transaction as the authenticated inbox row.
- Reject/rollback and return `503` if either durable write fails.
- Add HMAC-authenticated job rows, one-use hashed claim tokens, bounded leases, retry delay, attempt limits and terminal manual reconciliation.
- Bind claims and completion to the configured platform/Connect account.
- Authenticate older inbox rows before migration/backfill.
- Add 29 queue-specific test methods plus one HTTP receiver fault test; focused R16+R17 suite now passes 84 methods.
- Preserve explicit evidence boundary: a webhook is a signal for current-state retrieval, never proof of refund success.
- Record intermittent historical R15 aggregate-runner hang; its individual suite passes standalone. No single aggregate pass claimed.
