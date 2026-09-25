# Evidence-Capped Enforcement v0.1

**Status:** `[CONJECTURE]` as a general governance pattern; `[SCAFFOLD]` as an implemented, internally tested runtime mechanism pending external use.

**Forged:** 2026-08-22

## Hypothesis

Guardrails should not be permitted to exercise more authority than their evidence justifies.

A deterministic organizational rule such as “this agent may not call `delete_account`” can support a hard block. A bounded text heuristic that guesses whether prose is manipulative should normally support review, not an irreversible automated denial. A research conjecture may be recorded, but should not change the runtime disposition.

This is **evidence-capped enforcement** (ECE).

## Formal rule

Let dispositions have the order:

```text
ALLOW < REVIEW < BLOCK
```

For finding `f`:

```text
effective(f) = min(requested(f), cap(status(f), deterministic(f)))
```

The v0.1 cap is:

```text
cap(ACTIVE, true)       = BLOCK
cap(ACTIVE, false)      = REVIEW
cap(SCAFFOLD, any)      = REVIEW
cap(CONJECTURE, any)    = ALLOW
```

The overall receipt decision is:

```text
decision = max(effective(f) for all findings f), default ALLOW
```

`min` and `max` refer to the disposition order, not string ordering.

## Why determinism and status are separate

A regular expression is deterministic as code but may be inferential as evidence. Matching the word “guarantee” is reproducible; concluding that the speaker is deceptive is not therefore certain. The runtime marks the built-in semantic detector as inferential even though its execution is deterministic.

Conversely, a deny-list match directly instantiates a declared organizational policy. It does not infer intent. If the policy is active, the check can block.

## Human review is an outcome

`REVIEW` means pause, surface the evidence, and preserve a resumable path. It is not a disguised failure. For side-effecting tool calls, this mirrors established approval patterns: the agent may propose the action, but the application decides whether to resume it.

## Claimed benefits

The following are hypotheses until measured in deployments:

- fewer false-positive hard blocks from immature detectors;
- clearer separation between policy and risk inference;
- more honest audit artifacts because requested and effective authority are both recorded;
- safer experimentation with new detectors because conjectures can run in observe-only mode;
- easier promotion/demotion when detector evidence changes.

## Costs and failure modes

- A real hazard detected only by a heuristic may be sent to review instead of blocked automatically.
- Review queues can become denial-of-service surfaces.
- Teams may overstate status to obtain stronger enforcement.
- An `ACTIVE` label is not self-authenticating; governance around status promotion remains necessary.
- A malicious policy author can encode a prejudicial rule as a deterministic deny-list. ECE constrains evidence authority, not policy legitimacy.
- If the application ignores `REVIEW`, the pause has no effect.

## Tests required for the implementation claim

Property tests must cover every requested disposition crossed with every status/determinism combination and show:

1. no `CONJECTURE` finding changes `ALLOW` by itself;
2. no `SCAFFOLD` finding yields `BLOCK`;
3. no inferential finding yields `BLOCK`, even if `ACTIVE`;
4. an `ACTIVE`, deterministic finding may yield all three dispositions;
5. mixed findings resolve to the maximum effective disposition;
6. receipts record any downgrade from requested to effective disposition and why.

Receipt verification also recomputes every cap and the overall maximum. A caller
cannot make an internally inconsistent receipt pass merely by changing a finding
or decision and recomputing the unauthenticated SHA-256 digest.

## Research falsifier

The general ECE hypothesis should be weakened or rejected if controlled deployment shows that, compared with a clearly specified alternative, it produces no meaningful calibration benefit and materially increases harmful action completion or review burden. Metrics must include false blocks, missed harmful actions, review latency, reviewer agreement, and bypass rates. Internal synthetic property tests cannot answer that question.

## Novelty boundary

Runtime policy enforcement, risk-calibrated thresholds, human approval, assurance cases, and confidence-aware systems all predate this document. A 2026 prior-art search did not establish that ECE is unique. The contribution is a compact Lycheetah formulation that binds the repository’s evidence ladder to executable disposition ceilings. Any future novelty claim requires a systematic literature review.

⊚ Sol ∴ P∧H∧B ∴ Nigredo → Albedo
