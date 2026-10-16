# Changelog v2.8

The lab now includes a read-only trusted reconciliation worker and HMAC-authenticated minimal operation ledger. Queue completion is enforced in the queue API rather than being left to worker convention: `DONE` requires authenticated terminal provider-state evidence bound to the same event and operation. Legacy completed jobs without proof are demoted to manual review on startup.

Local results: the worker/inbox path passed 121 focused tests; R10, R11, R12 and R15 isolated regression groups passed 49, 29, 39 and 85 tests. Total across separately executed groups: 323. Loopback HTTP smoke succeeded with zero hosted provider calls and zero refunds created.

No upstream source changed. This is not production certified; hosted Stripe conformance and upstream CI remain undone.
