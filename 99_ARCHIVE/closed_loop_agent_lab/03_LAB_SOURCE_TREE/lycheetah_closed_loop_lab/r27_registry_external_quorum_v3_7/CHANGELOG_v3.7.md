# Changelog v3.7

- Added a quorum checkpoint wrapper around the real local spent-challenge registry database.
- Added signed, parent-linked checkpoints over logical registry data and schema, including nonce and clock state.
- Added fresh nonce-bound witness head reports and 3-of-4 decision/certificate threshold for f=1.
- Added a guarded loopback HTTP boundary, outbox recovery, authenticated response cache and signed 503 fail-closed response.
- Added 38 focused tests covering current state, rollback, quorum split/partial publication, cache and pending integrity, response loss, retries and HTTP concurrency.
- Added an explicit negative control for coordinated rollback of every local witness store.
- Current v3.7 tests: 38 passed. Retained v3.6 tests: 82 passed in a separate invocation. 120 methods passed across both local suites.

- Added fail-closed handling and recovery regression for an unexpected handler exception after a committed mutation.
