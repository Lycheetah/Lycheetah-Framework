# Changelog — v1.9

- Added a durable local outbox tied atomically to one-use witness consumption.
- Added a cooperating remote provider model with durable idempotency key + request digest + effect in the same SQLite transaction.
- Added retry-safe recovery after response loss and worker crash before local acknowledgement.
- Added fail-closed reconciliation state for providers without a durable idempotency contract.
- Added a pre-dispatch persisted-action integrity check after code review caught the need to check payloads before—not after—remote side effects.
- Added tests for evidence-provider TOCTOU to preserve the known limitation in visibility.
- Added 22-test local suite, failure matrix, threat model and staged upstream integration plan.

No upstream source file was changed.
