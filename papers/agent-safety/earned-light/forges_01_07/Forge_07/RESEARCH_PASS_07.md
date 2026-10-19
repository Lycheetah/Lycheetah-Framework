# LYCHEETAH — Earned Light — Forge VII
## Failure-injection, epistemic accountability and the limits of return

**Date:** 18 October 2026 (Pacific/Auckland)

**Status:** Runnable, local synthetic experiment. It neither establishes field security nor measures free will or a user's lived autonomy. Not integrated into GitHub or AZOTH.

### 1. Research question

When a delegated AI process dies during an external action or recovery, can the surviving system produce a consequence report that accurately distinguishes verified effects from unresolved ones **without inventing certainty**?

The strongest falsifier is a mature conventional durable-outbox, idempotent consumer, and saga implementation performing just as well. This is not a flaw in the research: Lycheetah can adopt established solutions and concentrate on the **human-facing semantics of consequence**.

### 2. Architecture tested

- Controller process keeps durable proposed/reserved/confirmed/compensating/restored/irreversible/blocked states in SQLite.
- Separate HTTP provider process keeps its own SQLite operations, effects, and compensations. Controller cannot transactionally commit with provider.
- Child worker dies abruptly with `os._exit(73)` at exact scripted points: before reserve, after reserve before send, after provider commit before controller ack, after controller ack, after compensation commit before ack, and after compensation ack.
- Operator revocation is a **simulation only**, invoked separately after the dispatch worker ends. Revocation prevents new proposals from being treated as authority, but cannot undo in-flight effects.
- After revocation, the controller reconciles by querying the provider before attempting an operation-idempotent compensation.
- A second scenario kills the provider process, confirms uncertainty on failed query, then restarts the provider from the same durable database and performs recovery.

Provider operations intentionally differentiate `write` (reversible synthetic effect) from `notify` (irreversible mock notification). No real email, customer record or external system is touched.

### 3. Evidence results

**31/31 locally authored tests pass.** The separate-process matrix has **16 distinct cut-point scenarios**. Statuses in `results/trial_results.json`:

| Consequence classification | Scenarios | Meaning |
|---|---:|---|
| `restored` | 5 | One simulated write effect observed and compensated |
| `irreversible` | 5 | Mock notification effect observed; cannot retract |
| `unresolved_effect` | 4 | Provider query suppressed or dispatch was reserved before death without decisive evidence |
| `not_dispatched` | 2 | Process died before any reservation |

The **two outbox comparator runs** start with the same crash immediately after the provider commit:

| Retry behaviour | Observed mock effects |
|---|---:|
| Conventional stable-ID outbox + idempotent provider | 1 |
| Deliberately broken non-idempotent retry | 2 |

The conventional baseline succeeds. The broken comparator is illustrative only; it does **not** imply state-of-the-art workflow engines are unsafe. The additional provider outage/restart test verifies: `unresolved_effect` while offline, `restored` upon return, and one provider effect plus one compensation.

### 4. The surprising result

The `after_reserve_before_send` trial is *known to the harness* to have produced zero provider effects. Nonetheless, the recovering controller reports `unresolved_effect`, not “no effect.” Why? A surviving controller cannot generally prove from its journal that a previously sent or reserved request will never arrive after a delay. This conservatism can cost usability, and must be managed with provider fences, authoritative receipt guarantees, timeouts plus verified quiescence, and clear human escalation in real systems.

**A truthful unknown is not a failed safety assertion; it is a correctly limited knowledge claim.** This is a design principle, not an assertion of a novel algorithm.

### 5. Abstract direction: Proof of Consequence / epistemic ladder

Proposed reporting layers:

1. `INTENDED` — an action was planned (local durable evidence).
2. `RESERVED` — controller prepared/authorized its dispatch (controller evidence; effect unknown).
3. `PROVIDER_REPORTED` — remote service says it committed (remote record; still defeasible).
4. `CORROBORATED` — independent tamper-evident evidence supports the effect claim (NOT IMPLEMENTED).
5. `HUMAN_UNDERSTOOD` — a person can correctly explain the consequences and choose recovery (NOT TESTED).

These must **not** be collapsed into a single “success” Boolean. A protocol that reports level 4 or 5 without evidence is laundering confidence.

A proposed research invariant: `claim_strength ≤ provenance_strength`, where both require explicit operational definitions and threat-relative trust assumptions. This inequality is a specification aspiration, not a numerical theorem.

### 6. Prior art / novelty boundary

- Transactional outbox plus idempotent consumer is established prior art: https://microservices.io/patterns/data/transactional-outbox and https://microservices.io/patterns/communication-style/idempotent-consumer.html
- Workflow retry semantics and idempotency: https://github.com/aws/aws-durable-execution-docs/blob/main/docs/patterns/best-practices/idempotency.md
- AWS Step Functions separates workflow execution guarantees from individual side-effect behavior: https://docs.aws.amazon.com/step-functions/latest/dg/choosing-workflow-type.html
- Forge VI established matching outcomes between the Right-of-Return prototype and a conventional saga baseline on four shared recovery cases.

Novelty being *investigated*, not claimed: a portable, typed, human-comprehensible consequence protocol that spans delegation, revocation, crash uncertainty, provider exit, and irreversible actions. There is no measured superiority yet.

### 7. How to falsify this branch next

- Use a serious external workflow engine and a separately administered dummy provider; compare correctness, operator burden, throughput, faults, and cost.
- Test forged remote receipts, reordered and delayed messages, provider outages during compensation, concurrent controllers, stale and duplicated revocations, malicious signing services and identity takeover.
- Test delayed delivery after a negative receipt; add provider-side epoch fences and prove when no effect can occur *after* revocation.
- Replace synthetic consequence labels with blinded operator comprehension trials: do people accurately distinguish `unknown` from `undone`?
- Test real provider APIs only under explicit approvals and safe sandbox accounts, never by silently attaching a production connector.

### 8. Integration map

- **AURA:** human may refuse, withdraw delegation, and accept real, visible consequences.
- **TIM:** record ordering, fencing epochs, freshness and recovery windows.
- **LAMAGUE:** make status vocabulary lossless; forbid “restored” when effects remain unresolved.
- **CASCADE:** preserve causal histories and decisions across provider substitution.
- **AZOTH:** eventual implementation location for runtime checkpoints and human review; not modified here.

**Central result:** The right of return includes the right to an honest unknown. A system cannot earn light by turning missing evidence into reassuring language.
