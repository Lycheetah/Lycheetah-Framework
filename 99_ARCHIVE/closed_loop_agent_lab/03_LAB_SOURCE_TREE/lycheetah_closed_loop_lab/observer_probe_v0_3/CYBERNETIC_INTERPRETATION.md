# Cybernetic interpretation — from a closed loop to a trustworthy loop

## The loop model

| Cybernetic role | Coding-agent interpretation | Evidence or unresolved question |
|---|---|---|
| Reference / essential variable | Frozen task contract: behavior that must become true, invariants that must stay true, effects that are forbidden | Was the contract complete and unambiguous before the run? |
| Plant | Disposable repository workspace plus the tools and environment the agent can affect | Which state could actually change? Was the workspace truly contained? |
| Controller | Agent proposes an action; deterministic policy mediates whether it may execute | Is its action scope limited and its decision enforceable? |
| Actuator | Tool broker / execution process at the actual effect boundary | Is approval current at the point of effect? Can the effect be fenced or cancelled? |
| Sensors | Test runner, final-tree digest, changed-path observer, task postcondition checks, human adjudication | Does each sensor observe the intended variable, and are its failures correlated with other sensors? |
| Comparator | Evaluator compares observed state with the frozen contract | Is the comparator judging semantics or an implementation detail? |
| Feedback | Failure classification, bounded repair attempt, rerun on fresh evidence | Does the next attempt improve the real task outcome without exceeding budget? |
| External disturbance | Dependency changes, test flakiness, concurrent edits, malicious input, provider side effects | Are disturbances observable, recoverable and recorded? |
| Stop condition | BLOCK or REVIEW, cancellation, budget exhaustion, human denial | Is stop actually enforced, or only described to the agent? |

A loop can be structurally closed yet epistemically wrong: the controller may receive a crisp signal that measures the wrong variable. Therefore “has feedback” and “has trustworthy feedback” are distinct engineering claims.

## Requisite variety, kept concrete

Ashby's law is often summarized as requiring a regulator to have enough response variety to handle the disturbances it must control. For this use case, that does not mean adding a huge state machine or more invented metrics. It means the control path must distinguish states that need different action:

- accepted with fresh evidence;
- definitely invalid / block;
- unclear or conflicting evidence / human review;
- evidence stale / re-run checks;
- revoked or unauthorized / stop;
- failed attempt but recoverable / bounded repair;
- repeated failure, tool exception, or exceeded budget / stop and hand off.

Collapsing all of these into binary success/failure loses distinctions. Conversely, adding categories without evidence or a distinct enforceable response adds complexity without useful variety.

## The observer's failure modes

1. **Coverage failure:** it never checks an important property, as with a no-op that passes a narrow test suite.
2. **Specification failure:** the task contract itself is wrong or ambiguous.
3. **Measurement failure:** the evaluator reports an incorrect state.
4. **Common-mode failure:** two sensors share the same hidden assumption or source data.
5. **Freshness failure:** the observation was true earlier but no longer matches the state at effect time.
6. **Actuation failure:** policy says BLOCK, but the action can still happen because the stop is not enforced by a trusted broker.
7. **Recovery failure:** feedback is observed, but the system loops, repeats damage, or hides the failure rather than stopping.

The v0.3 code measures only a subset of these. The calibration microtask probes coverage and overfitting; the common-mode grid shows how dependence can erase the expected benefit of multiple observers. The original fixture models freshness, containment and approval as authored state flags; it does not physically enforce any of them.

## Proposed invariant

> No claim of successful completion may be stronger than the most trustworthy evidence supporting it; no action may rely on evidence that no longer describes the state at the protected boundary.

This is a design rule, not a validated theorem. It becomes testable only after each evidence source, state transition and enforcement boundary is made explicit.

## Research question for the next stage

Can a postcondition observer that is validated on held-out tasks reduce independently adjudicated false accepts, while keeping false blocks, human review minutes, latency and cost within predeclared tolerances, compared with the same model and conventional controls alone?
