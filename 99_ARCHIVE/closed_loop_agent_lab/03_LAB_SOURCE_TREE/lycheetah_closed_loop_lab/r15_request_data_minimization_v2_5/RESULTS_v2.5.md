# Verification Results — v2.5

**Date:** 2026-10-17  
**Python runtime:** 3.13  
**Dependency surface:** Python standard library only

## Local execution

- Focused R15 adapter suite: **81/81 test methods passed**.
- Retained R10-R12 suites plus R15 adapter: **198/198 test methods passed**.
- Python compilation: passed for the adapter, simulator, focused tests and full regression runner.
- Loopback smoke test: passed; simulated provider committed one refund, dropped first response, and recovery reused the persisted idempotency key. Result was one effect across two POST attempts, final local state `SUCCEEDED`.
- POSIX permissions test: local operation database set to owner read/write only (`0600`).
- Caller metadata privacy tests: non-empty metadata rejected before any operation row or provider POST; malformed metadata is also rejected.

## Added R15 test coverage

- Customer email, token-like values, and unrelated free text cannot be passed as caller metadata.
- Rejected metadata does not reach SQLite and does not trigger network I/O.
- Successful request stores and sends only the internal operation-correlation metadata.
- Existing provider response allow-list remains enforced.
- Non-object caller metadata rejected before persistence.
- SQLite path must be durable; per-connection `:memory:` path is rejected.
- SQLite database path must not be a symlink.
- POSIX SQLite database file is owner-only (`0600`).

## External actions and limits

No hosted Stripe API calls were made. No real Stripe key was supplied. No refund was created. No upstream Lycheetah source file was changed, and upstream CI was not run. The retained tests and local simulator are not an independent proof of Stripe behavior.

## Promotion gate

Before considering deployment: run hosted Stripe test-mode conformance with an explicitly authorized test account; review data retention and encryption requirements; ensure caller operation IDs are opaque/non-PII; inspect backup and log permissions; integrate into a non-default upstream branch; run complete package tests and CI. Production approval is not established by this artifact.
