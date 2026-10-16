# Changelog — v2.2

## Stripe API v1 refund recovery contract

- Added endpoint-specific recovery helper for `POST /v1/refunds` based on current official Stripe docs reviewed 2026-10-17.
- Encoded same-key/same-payload retries only while inside a conservative 23-hour local cutoff, leaving a one-hour margin before Stripe API v1's documented minimum 24-hour pruning point.
- Bound the persisted operation fingerprint to account scope, test/live mode, API version, endpoint and canonical request payload.
- Added stable internal operation metadata for refund correlation; rejects caller override of the reserved key.
- Encoded conservative reconciliation of refunds by target, operation metadata, amount, currency, status and complete pagination. Zero matches are inconclusive, not permission to create another refund.
- Added status behavior: succeeded can be reconciled as complete; pending/requires_action waits; failed/canceled requires new approval; malformed, duplicate, incomplete or mismatched evidence reconciles.
- Added seven scenario outputs and official source log.
- Re-ran all retained v2.0/v2.1 suites with the new v2.2 suite: 117 test methods passed; v2.2-specific suite: 39 passed.

## Limits

- Offline tests only. No Stripe sandbox/live API requests, no provider credentials, no real side effects.
- No claim that Stripe transactionally binds provider commit to Lycheetah approval or evidence.
- No upstream Lycheetah source changed and no full upstream package test/CI suite run.
