# Registry Checkpoint Quorum API Contract v3.7

## Dispatcher

`RegistryQuorumAnchor.dispatch(service, method, path, raw_body, headers)` returns the service-style triple `(status, signed_envelope, dropped)`.

- A request is authenticated against the registered client key, request ID, timestamp, HTTP method/path and exact raw-body digest.
- A current quorum and exact live-registry fingerprint are checked before mutation.
- A durable `PREPARED` intent is committed before calling the registry service.
- A state-changing operation is checkpointed, and a quorum certificate is freshly compared to current witness heads before its response is cached/returned.
- Failures at the checkpoint boundary return a signed 503 with `reconciliation_required: true`; clients must not infer success.
- Repeating the same request within the signed time window returns its authenticated cached response without re-executing the mutation. Changing the payload under the same client/request ID returns 409.
- A response lost after registry commit is represented as outcome-unknown, not success.

## Checkpoint semantics

Each record binds `registry_id`, positive monotonic `sequence`, logical `state_sha256`, `previous_record_sha256`, unique `request_id`, and `issued_at_ms`, signed by the registry checkpoint issuer. Witness votes bind the exact record digest and state digest. For `n=4` and `f=1`, this implementation requires `n >= 3f+1` and threshold `q=3`.

## Failure semantics

- `CURRENT`: local head, live DB fingerprint, and a fresh witness-head quorum agree.
- `UNINITIALIZED`: only returned when no local head exists and the remote witness quorum is at genesis.
- `RegistryRollbackDetected`: local state is behind/diverges from the current quorum or a pending transition conflicts with state.
- `RegistryQuorumUnavailable`: no sufficient valid unique votes or a fresh current quorum cannot confirm the candidate.
- Guard-owned request failures return signed fail-closed errors; callers must reconcile rather than treating HTTP 503 as successful action.

## Limits

The HTTP server can be bound only to a loopback IP address. It is a local reference adapter and uses POSIX flock. In a deployed architecture, each witness must have distinct administrative, key-management, persistence, and recovery boundaries. No witness quorum can guarantee anti-rollback if all of its trust domains and backups can be coordinatedly restored by the same attacker.
