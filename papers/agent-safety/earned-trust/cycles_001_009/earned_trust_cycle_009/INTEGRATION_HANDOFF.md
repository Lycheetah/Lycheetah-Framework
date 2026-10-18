# C009 → Real Lycheetah Framework handoff

## Integration status

**NOT EXECUTED.** The native package `lycheetah` is not installed and container GitHub DNS is unavailable; the provided `run_actual_framework_contract.py` remains a candidate to run on a genuine checkout. Do not classify C009 as a tested Framework integration.

The actual repository at `Lycheetah/Lycheetah-Framework` has these distinct research components:
- `lycheetah.assurance.runtime.AssuranceRuntime`: policy decision/receipt. A model-supplied `human_approved=True` is not proof of human identity.
- `lycheetah.assurance.finality.FinalityGate`: evidence revalidation near dispatch, but not an external atomicity broker.
- `lycheetah.assurance.action_guard.PersistentActionGuard`: durable action-bound approval and dispatch claim, not a provider's authenticated capability issuer.

## Proposed native adapter

1. On the **trusted host**, receive a typed action proposal from the agent socket using operating-system principal binding or stronger verified identity.
2. Look up trusted human approval **outside the model-facing payload**, and produce an `AssuranceEvent` in `Phase.TOOL` with independently derived side-effect status and approval.
3. Evaluate the actual `AssuranceRuntime`. `BLOCK` stops; `REVIEW` pauses for a real person; do not treat model-supplied approval as authority.
4. Bind `FinalityGate.finalize` evidence to the *exact approved action and subject* and to policy provenance. Preserve `REVIEW` as a pause.
5. Call `PersistentActionGuard.claim_dispatch` against an externally anchored local journal and trusted action, **while enforcing any separately recorded governance changes at the same authoritative boundary**. Sequential calls alone do not remove a race.
6. Only then mint an action-specific provider capability; do not show the key or capability to the agent. Enforce expiration, scope, action hash and idempotency at the provider.
7. If the provider outcome is ambiguous, enter UNKNOWN and reconcile with separately authenticated provider evidence rather than automatically replaying.

## Required exact tests

- Provider direct access as an untrusted UID; ensure no ambient provider credential.
- Cross-UID principal spoofing and same-UID challenge; prove credential files are inaccessible under deployment permissions.
- Source challenge, policy update and approval revocation at every boundary before/after local reservation.
- Crash between guard/finality/read, capability mint, provider write and receipt persistence.
- Tampering and replay against the provider, including key rotation/revocation and bearer theft.
- Replace self-authored fixtures with separately authored malicious behaviors; measure false refusals as well as missed unauthorized effects.
- Compare to a conventional gateway with identical controls and credentials.

## Blocking threat assumptions

Protection collapses if untrusted code can read signer credentials, mutate trusted ledger/keys, execute as the gateway UID, or invoke a separate provider endpoint with ambient credentials. A real deployment requires process isolation, policy-specific principal enrollment, firewall/network namespaces or equivalent reachability controls, secure signer key management, TLS where applicable and vendor-supported idempotency and conditional semantics. Without these, C009 demonstrates a narrow local proof of concept, not a secure deployment.

**No GitHub write or live external action authorized or attempted.**
