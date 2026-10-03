# Agent Safety Control Simulator

**Version 0.2 · 3 October 2026 · In-process development prototype**

This is an executable subset of the [research specification](../PAPER.md). It simulates scoped permissions, protected evidence witnesses, nested delegation, atomic shared accounting, revocation, object-revision binding, and uncertain effect reconciliation. It has no dependency beyond Python's standard library and makes no network or model calls.

**Boundary:** this is an in-process simulator, not a sandbox for hostile Python. The proposer supplies typed data. The harness, issuer, broker, evidence registry, resource ledger, and synthetic service are assumed trusted. Python object privacy does not enforce this separation. Real deployment would require authenticated interfaces, credential isolation, process/service isolation where appropriate, persistent crash recovery, and a separately reviewed threat model.

## Reproduce

From this directory:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 python3 run_experiments.py --output reports/budget-repair
PYTHONDONTWRITEBYTECODE=1 python3 adversarial_checks.py
```

The report commands above write in `reports/budget-repair/`; original v0.3 reports remain historical evidence. Simulated messages and document edits stay in memory. No real email, publication, billing, or application change occurs. Use a fresh `--output <directory>` to keep checked-in reports unchanged. The full-suite command is available for reproduction; this repair's recorded run selected only the broker, authority and shared-accounting modules.

## What the first run shows

These are original v0.3 observations, reproducible from the pinned source linked
in [the repair note](../BUDGET_REPAIR.md). The current repair has a separate
46-method focused receipt and 19-case-per-arm result in `reports/budget-repair/`.

- **53 unittest methods passed**, including parameterised subtests. Many controls are tested against both permission stores; this is not a count of independent attack samples.
- **19 self-authored scripted cases per arm** met their predefined expected outcomes.
- The two arms had identical aggregate observations on those cases. This is not statistical equivalence or evidence of a new protective advantage.
- Sixteen concurrent workers sharing a five-unit account produced five one-unit effects in each arm.
- Lost-response reconciliation produced one effect and one settled charge, with a reservation retained while the outcome was unknown.
- A simulated harmful message was permitted by both arms. Already-admitted work completed after revocation in both arms.
- A separate unit test confirms that faithful retention can preserve a false arithmetic statement.

Read [the result table](reports/RESULTS.md), [raw traces and source fingerprints](reports/scripted-controls.json), and [the test receipt](reports/unit-tests.json).

“Expected outcome met” includes counterexamples and deliberate unresolved states. It must not be represented as a universal safety success rate.

## Implementation map

| Module | Responsibility |
|---|---|
| `model.py` | Immutable structured proposals, canonical artifact identity, controlled rendering, and observations. |
| `authority.py` | Opaque capability leases and a separately implemented conventional ACL store; authenticated sessions and ancestor checking. |
| `accounting.py` | Shared in-memory ledger and operation records owned by one control plane. |
| `evidence.py` | Exact finite qualification checks and protected witnesses bound to source, consumer artifact, context, contract, and validator. |
| `broker.py` | Admission, replay control, shared reservations, dispatch states, and receipt reconciliation. |
| `world.py` | Synthetic provider effects and fault injection. |
| `fixtures.py` | Fixed source packet, clock, grants, sessions, and setup. |
| `scenarios.py` | Scripted cases and an outcome observer reading provider state and admission order. |

The evidence language is intentionally restricted. It requires exact selected fields, the exact original qualifier set, and the controlled consumer template. The optional recommendation may be removed. Extra free-form qualifiers and even harmless paraphrases are rejected; useful natural-language translation is not demonstrated.

C and D share the broker, validator, accounting, and adapters. Their permission stores differ. This comparison asks whether either store violates the same scoped control contract; it cannot establish a benefit of Lycheetah terminology or a novel safety mechanism.

## Adversarial publication checks

The original [probe report](reports/adversarial-checks.json) records two counterexamples per arm at v0.3. [Current checks](reports/budget-repair/adversarial-checks.json) distinguish the repaired budget case from the remaining freshness limit:

- **Original instance-local budgets, now repaired within one live authority:** v0.3 created two ledgers and admitted two effects under a one-unit root grant. Current brokers use the authority's shared ledger and replay journal; the probe confirms one effect and one charge. This does not cover independent authorities, process restart or distributed stores.
- **Admission-only evidence freshness:** the trusted controller changes the evidence context after admission but before dispatch. The admitted write completes; the old witness fails a subsequent check. There is no dispatch-time revalidation or cancellation of admitted work after evidence changes.

These are self-authored configuration/fault-hook probes, not independent attacks or evidence of production readiness. Current code repairs one ownership defect; the pinned v0.3 source preserves reproduction of the original budget failure. Dispatch-time freshness and stronger accounting properties remain open.

## Limits that remain

The simulator does not implement persistent memory or deletion, restoration, general taint tracking, a complete history-aware harm policy, distributed transactions, real-provider cancellation or billing, crash-safe persistence, agent motivation, strategic deception detection, model interpretation, human oversight studies, or affected-party governance. The memory fixture tests a spoofed grant string; it is not a persistent-memory prompt-injection evaluation. A private document's send policy is checked, but arbitrary information flow through all representations is not modelled. Resource units count fixed synthetic provider charges; Python execution, parser size, host CPU/memory, and denial of service are not bounded by this ledger.

The source and fixtures are self-authored and known during development. The observer is separate code reading actual synthetic effects, but not an independent research team. The concurrency schedule can vary; assertions concern aggregate ceilings and effects, not a guaranteed fixed trace order.

The next research gate is independently challenged fixtures or review of these controls, followed by a separately authorised model-agent experiment in simulated services. The [full evaluation protocol](../EVALUATION_PROTOCOL.md) remains largely unexecuted.
