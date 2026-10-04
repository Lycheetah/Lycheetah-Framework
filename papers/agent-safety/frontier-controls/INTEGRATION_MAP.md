# Frontier Controls — Live Repository Reconciliation

**Integration packet:** v0.1  
**Reconciled against:** `Lycheetah/Lycheetah-Framework` `master` at `db36241ff1d88cf04f2cae4477db5d59e230d9ee`  
**Status:** PR-ready research integration packet. **Not deployed. Not a production safety claim.**

## Current live repository facts

The current public `papers/agent-safety/` packet is working draft v0.4. Its live
documentation says:

- the original multi-broker accounting counterexample was repaired **within one
  live in-process control plane**;
- distributed/restart-safe accounting remains outside that repair;
- **admission-only evidence freshness still reproduces**;
- no model-agent benchmark, real-provider experiment, independent security
  review, or production safety implementation has been completed.

The current `34_ASSURANCE_RUNTIME/` remains explicitly `[SCAFFOLD]`. It already
has policy evaluation and a same-corpus policy regression gate.

## Reconciliation decisions

| Frontier packet | Live-repo disposition | Why |
|---|---|---|
| v0.7 Commit-Time Authorization | frontier research | Not represented as a production effect-commit fence in the inspected Assurance Runtime. |
| v0.8 Shared Resource Commitment | **historical/supporting** | Live agent-safety v0.4 already repaired the demonstrated in-process multi-broker ownership defect. Do not publish v0.8 as if the current repo still has it. |
| v0.9 Atomic Authority/Resource Finality | frontier research | Useful composition experiment; remote-provider atomicity remains outside claim. |
| v1.0 Evidence Finality | **primary runtime candidate** | Directly targets the live packet's still-reproduced freshness counterexample. |
| v1.1 Hazard Obligations | frontier research | Adds closed-world required-control semantics beyond current runtime claims. |
| v1.2 Policy Evolution | frontier research | Complements existing policy regression work; bounded Boolean semantics only. |
| v1.3 Assurance Mutation | **primary regression-tooling candidate** | Extends the existing policy regression gate from outcome comparison to test-sensitivity/falsification. |
| v1.4 External Threat Auditor | **primary threat-backlog candidate** | Fits beside the existing Assurance Runtime industry/frontier crosswalk and keeps missing controls explicit. |

## What must not happen in this PR

Do **not**:

- copy these prototypes into `lycheetah/assurance/` and call them shipped;
- change Assurance Runtime status from `SCAFFOLD`;
- claim a safety advantage over conventional controls;
- claim the v0.8 accounting defect still exists in the current public simulator;
- imply the v1.4 proposed extended manifest is implemented;
- collapse `SYNTHETIC_ENGINEERING_VALIDATED` into `PRODUCTION_VALIDATED`.

## Runtime promotion order

1. **Evidence finality** — native implementation against current Assurance Runtime
   models/policy/receipt contracts; reproduce the current freshness
   counterexample first, then make it fail closed at the declared finality point.
2. **Mutation sensitivity** — extend current regression tooling with explicit
   non-equivalent safety-semantics mutants and a frozen denominator.
3. **External threat manifest** — keep as architecture-review tooling; do not turn
   control-name coverage into an attack-resistance score.
4. **Execution confinement** — real sandbox/filesystem/network/credential
   boundaries for a coding-agent pilot.
5. Only then run a human-supervised real repository pilot with consequential
   actions still requiring human final approval.

## Reality-use threshold

The first credible real-world pilot is **shadow/human-supervised**:

```text
coding agent
    -> Lycheetah assurance gateway
    -> disposable/sandboxed execution cell
    -> evidence + mutation + threat audit
    -> human final approval
```

No autonomous production deploy, customer messaging, payments, or unrestricted
host shell should be enabled by this research integration.

## v1.4 packaging note

The original standalone v1.4 `benchmark.py` was not present in the mounted
artifact during consolidation. Its frozen report is preserved unchanged. This
integration packet adds a **new independent reproducer**,
`08_external_threat_boundary_auditor_v1_4/reproduce_boundary_audit.py`, which
reproduces the frozen headline counts. See `PACKAGING_REPRODUCER_NOTE.md`.
