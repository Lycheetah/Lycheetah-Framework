# Changelog — v1.9

Focus changed from witness authentication alone to the authorization-to-effect boundary.

- Atomic local transaction: consume one-use witness + insert durable outbox intent.
- Stable operation ID travels as the downstream idempotency key.
- Provider contract binds the idempotency key to request digest, persisted result and simulated effect in one provider-side transaction.
- Pending actions recover after restart; lost response after remote commit safely retries the same operation key in the cooperating provider model.
- Providers without durable idempotency are not called; uncertain operations route to `RECONCILE`.
- Added current policy, signed-witness expiry, exact event, evidence and stored-payload integrity checks immediately before dispatch.
- Fixed a prototype-level integrity gap by checking persisted action digest before any remote call.
- Added 27 local tests; concurrency test exercises 25 independent two-dispatcher races.
- Added status-only recovery after lost enqueue acknowledgement, even after expiry; an expired item cannot dispatch and moves to reconciliation.
- Deliberately retained a test that demonstrates external evidence can change after returning a snapshot and before the effect provider is called.

Not integrated into upstream; no production safety or exactly-once claim.
