# Observer validation protocol — v0.2

**Status: proposed protocol.** This document does not claim that any observer has been measured or validated on real agent tasks.

## Why this layer exists

A regulator can be closed and still regulate the wrong variable. A coding agent may pass its available tests while missing the requested behavior; a second observer may catch that. But that observer can inherit the same flawed task definition, rely on the same weak tests, or hallucinate a success/failure label. More machinery does not create independent evidence by itself.

This is not a hypothetical concern limited to our toy fixture. On July 8, 2026, OpenAI reported an audit of SWE-bench Pro in which its pipeline flagged 27.4% of tasks as broken, while its human annotation campaign identified 34.1%; OpenAI estimated roughly 30% of tasks were broken. Reported classes included overly strict tests, underspecified prompts, low-coverage tests, and misleading prompts. OpenAI said this and similar findings highlighted the difficulty of curating reliable benchmarks. Source: https://openai.com/index/separating-signal-from-noise-coding-evaluations/

Earlier, on February 23, 2026, OpenAI reported that its audit of 138 SWE-bench Verified tasks found material issues in 59.4% of that audited subset, including tests rejecting functionally correct solutions and evidence of training contamination. That is a finding about the audited subset and benchmark, not a claim that 59.4% of all coding tasks are flawed. Source: https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/

## The three-evidence separation rule

Do not let one agent author a solution, write its acceptance tests, grade its own work, and then treat those outputs as independent corroboration.

### 1. Frozen task contract

Before either arm runs, a maintainer or task curator records:

- the user-visible goal and explicit constraints;
- required behavior and prohibited regressions;
- requirements that are intentionally out of scope;
- acceptable implementation freedom;
- machine-checkable acceptance criteria and criteria that require judgment;
- version, timestamp and immutable hash of the contract.

The issue text must not be silently rewritten after outcomes are seen. Ambiguity is recorded as data; it is not resolved post hoc to favor either arm.

### 2. Execution evidence

Evidence comes from a trusted runner or observer, not from agent prose. Preserve:

- base commit/tree hash and final tree hash;
- exact test commands, exit status, stdout/stderr and environment identity;
- test identity/hash and whether tests were available to the agent;
- new target-behavior checks and regression checks separately;
- changed paths, including test and configuration files;
- timestamps, action records and approval status at the real effect boundary.

The runner receipt must bind to the exact final tree. If the tree changes after tests, test evidence is stale until re-run.

### 3. Independent outcome adjudication

At least two reviewers, blind to which arm produced a patch, independently assess:

1. Does the patch satisfy the frozen contract?
2. Does it break unrelated behavior?
3. Are the tests aligned with the contract and implementation-agnostic?
4. Could a plausible correct implementation fail the tests?
5. Could a materially incomplete or wrong patch pass the tests?
6. Was ACCEPT, REVIEW or BLOCK warranted given the evidence available at that time?

Disagreements go to a named adjudication step. Report initial disagreement and final result. Do not delete ambiguous cases from the denominator without reporting them.

## Test-suite adversarial checks

For each task, attempt the following before trusting automated labels:

- **No-op mutant:** leave target behavior unchanged while making the smallest patch that might appear plausible.
- **Regression mutant:** solve the target behavior while deliberately damaging a nearby unrelated behavior.
- **Test weakening:** remove or bypass an acceptance assertion, alter test configuration, or change a fixture so the tests pass without the required behavior.
- **Valid alternative:** construct or reason through an implementation that meets the contract but differs structurally from the reference patch.
- **Prompt/test contradiction:** compare each acceptance assertion to a requirement actually stated or reasonably implied in the task contract.
- **Environment repeat:** rerun flaky or environment-sensitive checks to identify nondeterminism.

These checks are diagnostic, not complete. Mutation tests can reveal test blind spots but cannot prove exhaustive coverage.

## Paired experimental design

- Freeze tasks and contract versions before running either arm.
- Use the same model/version, tool surface, context, budgets, base commit and conventional controls in both arms.
- Randomize or counterbalance arm order; isolate workspaces so one run cannot leak into another.
- Keep only the postcondition-observer path different between arms.
- Do not expose hidden acceptance tests to the agent unless that is part of the stated condition.
- Record all attempts, missing runs, exceptions, token/tool/time costs, final diffs and raw receipts.
- Report paired task-level outcomes and reviewer effort, not just pooled pass rates.
- Use held-out tasks or a second repository for replication. Public benchmark results alone do not establish the observer's quality.

## Metrics

Report numerator and denominator for each rate:

- invalid automatic accepts / all independently judged invalid patches;
- valid automatic accepts / all independently judged valid patches;
- false blocks / all independently judged valid patches;
- reviews / all attempts, with reviewer minutes and outcomes;
- test false-positive and false-negative findings from the adversarial checks;
- detected issues corrected on a subsequent attempt within the same fixed budget;
- completion latency, tool calls, model tokens and total review burden;
- enforcement fidelity for workspace scope, stale evidence, revocation and approval.

Do not collapse these into one score unless the costs are explicitly justified in advance. A system that blocks everything has zero invalid auto-accepts but no useful capability. A system that accepts everything has low review burden but no meaningful oversight.

## Promotion gates

- **R0 — logic/sensitivity study:** deterministic fixture and analytical sensitivity grid. The current packet reaches this stage only.
- **R1 — instrumented dry run:** one harmless task in a disposable repository, full receipts and manual validation, no external side effects.
- **R2 — paired pilot:** 20–30 tasks, paired arms, independent blinded labels and test-quality audit.
- **R3 — replication:** holdout tasks or a second repository, independent evaluator and predeclared error tolerances.
- **R4 — bounded consequential trial:** only after isolated execution, stop/revoke behavior, evidence freshness, recovery and approvals are independently tested; every patch still receives human review.

There is no automatic promotion based on a green test suite or a high benchmark number.

## Formal framing

Let `z ∈ {valid, invalid}` be the independently adjudicated task outcome. Let the observer emit `y ∈ {satisfied, failed, unknown}`. Define:

- sensitivity `Se = P(y = failed | z = invalid)`;
- specificity `Sp = P(y = satisfied | z = valid)`;
- unknown rates `U_i = P(y = unknown | z = invalid)` and `U_v = P(y = unknown | z = valid)`.

Then, among tasks that passed conventional process gates:

- invalid auto-acceptance rate under the candidate is `1 − Se − U_i`;
- valid false-block rate is `1 − Sp − U_v`;
- review rate is `π_i U_i + (1 − π_i) U_v`, where `π_i` is the prevalence of invalid tasks in this gated population.

These rates only mean anything if `z` is independently and consistently labelled. If the evaluator's own ground truth is unreliable, precise formulas produce precise-looking nonsense. Measure `Se`, `Sp`, reviewer agreement and adjudication consistency on held-out tasks; do not assume them from self-reported confidence.
