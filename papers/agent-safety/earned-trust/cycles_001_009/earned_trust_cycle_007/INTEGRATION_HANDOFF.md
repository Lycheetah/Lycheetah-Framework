# C007 native integration handoff — explicit blocker

## Pinned source

Existing Lycheetah-Framework research reference: `Lycheetah/Lycheetah-Framework`, `master` commit `d4a65ff64efa0a512c5c07ca64f6ec76242dd775`. Important real source classes inspected in prior cycles:

- `lycheetah.assurance.models.AssuranceEvent`, `Phase`, `Disposition`
- `lycheetah.assurance.runtime.AssuranceRuntime`
- `lycheetah.assurance.finality.FinalityGate`
- `lycheetah.assurance.action_guard.PersistentActionGuard`

The external pinned checkout cannot be cloned in the current container (network DNS unavailable) and the `lycheetah` package is not installed. C007 `run_actual_framework_contract.py` therefore exits code 4 on import; **zero real Framework tests have run.**

## Run this in the true Framework checkout

```bash
git clone https://github.com/Lycheetah/Lycheetah-Framework.git
cd Lycheetah-Framework
git checkout d4a65ff64efa0a512c5c07ca64f6ec76242dd775
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
PYTHONPATH=. python /absolute/path/to/earned_trust_cycle_007/run_actual_framework_contract.py
```

Do not modify GitHub while verifying. Expected observations include: (i) `FinalityGate` detects changed evidence; (ii) Action Guard refuses a revoked permission despite an earlier passing finality result; (iii) dispatch claims are single-use; (iv) finality reconsideration after a local claim does not undo `DISPATCHING`. Failed assertions are meaningful and must be preserved, not patched around.

## Correct architectural seam

`FinalityGate.finalize()` supplies a current **evidence decision**, not a provider transaction. `PersistentActionGuard.claim_dispatch()` supplies a local **dispatch permission transition**, not guaranteed cancellation of an already remote dispatched request. C006 `GovernedRegistry.apply()` produces an accepted **provenance change**, not an atomic update to Action Guard's database.

A straightforward sequence — C006 challenge → local C007 relay → native Action Guard claim — has **no crash-safe atomicity** across distinct datastores. Before production, specify who holds the one authoritative governance/approval/evidence epoch, which operation is linearized, how issuer identities are authenticated, how a provider enforces conditionality, and how uncertain effects are reconciled. Hold external effects disabled until verified by independent reviewers.

## Explicit red-team tests after installation

1. Valid signed C006 challenge between admission and native dispatch; stale approval denied.
2. Crash after governance commit but before dispatch-ledger mirror: do not silently permit a stale claim.
3. Approval revocation after native finality but before claim; native Action Guard must deny.
4. External effect executes after local permission claim and before later challenge; system records possible/actual effect, no false reversal.
5. Same-content, different-user and different-order action substitutions.
6. Missing, false and source-substituted evidence; no truth certification from valid HMAC alone.
7. Concurrent process claims and duplicated provider idempotency key; one effect, no unbounded retries.
8. Corrupted audit and materialized-state mismatches; pause, do not fabricate successful verification.
9. Baseline using conventional ACL/SQL conditional commit with the same controls.

No user approval for live transactions was requested or given by this research. Keep all write-capable production adapters disabled.
