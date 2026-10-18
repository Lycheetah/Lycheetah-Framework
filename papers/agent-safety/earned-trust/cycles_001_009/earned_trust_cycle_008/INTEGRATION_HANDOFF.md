# C008 → Lycheetah real-framework integration handoff

## Status: NOT EXECUTED

Container network DNS does not resolve github.com; `lycheetah` is not installed. Attempted native bridge file from C007 exits code 4 with `No module named 'lycheetah'`. Do not substitute `upstream_dispatch_fence.py` for the Framework's classes and call that integration.

The true Framework source referenced in prior cycles is `Lycheetah/Lycheetah-Framework` at `d4a65ff64efa0a512c5c07ca64f6ec76242dd775`:
- `lycheetah.assurance.runtime.AssuranceRuntime`
- `lycheetah.assurance.finality.FinalityGate`
- `lycheetah.assurance.action_guard.PersistentActionGuard`
- `lycheetah.assurance.models.AssuranceEvent, Phase, Disposition`

C008's lab integrates only with a byte-identical copy of the synthetic **C007** `Fence`. It is not yet a patch against the Framework's official code.

## Critical design decision before native integration

Choose **one authoritative writer** for every governance challenge/approval/evidence epoch and the dispatch outbox. If Cycle 006 keeps accepting challenges in a separate registry, a crashed relay preserves the original stale-dispatch gap. It is *not* solved by adding an outbox to the downstream database. Either migrate the governance authority completely, enforce a provider-side fencing token with a real trusted issuer, or design and test a multi-system protocol with explicit availability/trust semantics.

## Actual native test route

```bash
git clone https://github.com/Lycheetah/Lycheetah-Framework.git
cd Lycheetah-Framework
git checkout d4a65ff64efa0a512c5c07ca64f6ec76242dd775
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
PYTHONPATH=. python /absolute/path/to/earned_trust_cycle_007/run_actual_framework_contract.py
```

Then build an adapter that binds `FinalityGate.finalize` and `PersistentActionGuard.claim_dispatch` to one durable authority or an authenticated conditional provider endpoint. Do not simply call them sequentially and assert atomicity. Test a real failure injection between *every* persistence or provider boundary.

## Explicit blockers before a pilot

1. Full mediation: provider credentials held by a protected gateway, not by the untrusted agent.
2. Governance source of truth: no accepted external challenge invisible to finality.
3. Provider reconciliation: authenticated, action-bound observations and an explicitly defined `ABSENT`/`PENDING`/`SUCCEEDED`/`FAILED` status model.
4. Idempotency retention, command substitution, human identity and secure key isolation.
5. Authorized and independently reviewed threat model, deployment permissions and vendor API semantics.
6. Honest baseline with the same guarantees (conventional SQL outbox + provider idempotency).
7. Crash/power-loss/restart tests on the target host/database configuration.

**External effects: DISABLED.** No customer system, payment provider, production credential or remote GitHub write is needed to reproduce C008.
