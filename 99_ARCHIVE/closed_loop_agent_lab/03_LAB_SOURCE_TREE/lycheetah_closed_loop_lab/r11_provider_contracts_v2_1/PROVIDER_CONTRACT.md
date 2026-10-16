# Provider Contract v2.1 — minimum semantic guarantees

This contract is for a provider adapter used by a human-supervised agent to perform a consequential side effect. A capability flag is descriptive only; production adoption requires tests against the actual provider sandbox and its documented semantics.

## Required operations

- `execute(operation_id, payload, condition)`: execute one logical effect with a stable operation ID and a provider-enforced condition.
- `lookup(operation_id, payload_fingerprint)`: return the durable committed result, return a definitive not-found result, or report an idempotency conflict. If the provider cannot distinguish not-found from unknown/temporarily unavailable, the caller must reconcile.
- `operation_id` must be scoped to the relevant account/tenant and operation family, and retained at least as long as the maximum retry/recovery horizon.

## Required semantic properties

1. **Durable deduplication:** repeated identical operation IDs and payload fingerprints return the first committed result and do not repeat the side effect.
2. **Payload binding:** reusing the key for different content fails with a conflict; it must not silently replay the earlier response or run a new operation.
3. **Atomic effect/result:** the provider persists the idempotency record and business mutation together, or exposes an equivalent documented mechanism. Crash after commit must permit result recovery.
4. **Commit-time condition:** the condition relied on for authorization is checked at the operation's linearization/commit point, not only in a prior read. A separate `GET` followed by `POST` does not meet this property.
5. **Observable ambiguity:** after timeout, lookup resolves the original operation. Absence of a row is definitive only if provider documentation makes that guarantee under the relevant consistency model.
6. **Retention and scope:** key retention, uniqueness scope, response-replay behavior and payload comparison are documented and fit the complete recovery horizon.
7. **Fail-closed adapter:** if any required property is unknown or absent, the broker must not blindly retry an irreversible action. It records `RECONCILE` and requires authoritative lookup/manual resolution.

## Important non-guarantees

- Exactly-once *delivery* is not required; delivery can be at-least-once with durable deduplication.
- A broker cannot impose a condition atomically on an independent provider merely by making its own database transactional.
- The atomic reference in this pack places condition state and effect state in one provider-owned SQLite database. It is a model of a strong provider contract, not proof that a real external API offers it.
- For evidence owned by another service, use a provider-supported conditional version, lease/fencing token, reservation, or transaction that is actually enforced at effect commit. Otherwise the TOCTOU window remains and the operation must be treated as weaker / require reconciliation.

## Conformance method

Run black-box tests against a sandbox account or local provider with the exact production adapter, including restart, lost response, same-key/different-payload, concurrent duplicate dispatch, condition revocation races, unknown network outcome, and expiry. Save provider name/version, docs URL, environment, test timestamp, raw request/response hashes, and test results. A mock pass is necessary but never sufficient.
