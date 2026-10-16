# Defense Blueprint: Witness Provenance and Single-Use Finality

## Security properties

| Property | Existing inspected API | Required stronger property |
|---|---|---|
| Body mutation detection | Public SHA-256 digest | Retain as corruption check |
| Issuer provenance | Not shown in witness structure | HMAC / signature or gate-owned ledger ID |
| Requirement authority | Requirements passed to `admit()` and embedded in witness | Trusted configuration owns requirements |
| Admission receipt linkage | Digest copied into witness | Verify receipt exists, verifies, and belongs to event/policy |
| Action binding | Canonical event digest | Retain; include idempotency key and target identity where relevant |
| Freshness | No explicit expiry in inspected witness | Trusted issue/expiry timestamps and policy |
| Replay resistance | No consumed ID in inspected witness | Durable single-use reservation ledger |
| Current state | Runtime + evidence are re-evaluated at finality | Retain and log evidence versions |
| Remote-effect atomicity | Explicitly not guaranteed | Effect broker with provider idempotency/reconciliation |

## Minimal interface proposal

```python
admitted = gate.admit(event, trusted_requirement_set)
# admission creates server-side ledger record and opaque witness_id

permit = gate.reserve_finality(
    witness_id=admitted.witness_id,
    event=event,
    action_id=stable_idempotency_key,
)
if permit.ready:
    effect_broker.execute_once(action_id, exact_action_payload)
```

`trusted_requirement_set` must come from a trusted release/policy resolver; passing caller-supplied requirements is not enough. `reserve_finality` must atomically mark the witness/action as reserved or return an already known result for the same `action_id`. If a provider doesn't support idempotency, the broker still cannot guarantee exactly-once remote effects under every crash window; it must define reconciliation and uncertainty states.

## Authentication trade-off

- **Server-side ledger + opaque ID:** strongest default when gate and effect broker are one trusted service; the caller cannot mint a witness from public fields.
- **HMAC token + replay ledger:** appropriate for serialized transport between trusted services; requires protected key storage, key rotation, audience/version binding and durable single-use state.
- **Plain SHA-256 digest:** useful for accidental-corruption/tamper detection only when the trusted digest is known independently. It is not proof of the issuer or of authorization.

## Scope boundaries

This proposal does not imply that text heuristics can judge real-world intent, that an `ALLOW` makes an action safe, or that a local gate can atomically commit arbitrary remote effects. It addresses only provenance and binding of the finality admission artifact.
