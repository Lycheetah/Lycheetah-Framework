# Changelog — v2.1

## Provider Contract Conformance

- Added an executable provider-contract harness with an atomic conditional/idempotent reference, a split-check negative control, and a non-idempotent negative control.
- Added a bounded three-event schedule enumerator showing one stale-authorization interleaving in split check-then-act and zero in the atomic linearization model.
- Added recovery decision helper producing `ACCEPT_STORED_RESULT`, `RETRY_SAME_KEY`, or `RECONCILE` from explicit per-action provider contract fields and observed lookup state.
- Added regression coverage for durable result replay, payload mismatch, pre-commit rollback, response loss, concurrent duplicate calls, condition changes, provider key TTL, unknown lookup, and lack of commit-time predicate enforcement.
- Added desk-reviewed notes from official Stripe, Amazon EC2, and Amazon ECS documentation. No live provider API was called.

## Evidence boundary

The local 26-test suite passes, and the previous v2.0 49-test suite was rerun and passed. No upstream source was modified. The atomic model stores condition and effect in the same provider-side SQLite database; a real external provider must be tested against its own exact documented contract.
