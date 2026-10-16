# Evaluation Plan — Does Policy Lab Improve Policy Analysis?

## Claim to test

The system may improve traceability, challenge quality and feedback-to-decision transparency. This is a hypothesis, not an established result.

## Comparison conditions

Use the same policy question and same source pack across at least three conditions:

A. **Conventional baseline:** an experienced researcher produces a policy analysis using normal documents and an evidence table.

B. **Structured ledger:** same analyst uses a basic issue/evidence ledger but no cross-perspective model cycle or dependency review.

C. **Policy Lab workflow:** source ledger, explicit claim types, cross-party perspective, independent red team, affected-group lens, scenario register and decision trace.

If feasible, include a fourth condition: model-only unconstrained answer. This tests whether the scaffolding adds value beyond asking an LLM a general question.

## Blinding and fairness

- Use more than one policy topic before making broad claims.
- Rotate which perspective authors the initial proposal and which challenges it.
- Hide condition labels from reviewers where practical.
- Include a small set of seeded factual traps, missing-source claims and plausible minority concerns.
- Have reviewers with different perspectives assess the same outputs.
- Separate factual accuracy from normative agreement. Reviewers should not be asked which political option they prefer.

## Primary measures

1. **Source fidelity:** percentage of material empirical claims directly supported by cited sources, correctly paraphrased and bounded by source limitations.
2. **Claim completeness:** proportion of key claims labelled as fact, forecast, assumption, public preference or value judgment.
3. **Traceability:** ability to locate the source and history of a claim and identify which conclusions depend on a changed assumption.
4. **Counterargument coverage:** independently assessed coverage of important plausible objections, not just the count of objections generated.
5. **Non-erasure:** rate at which important contrary evidence, minority concerns or unresolved disputes are retained in the final record.
6. **Correction behaviour:** whether a model corrects an error when shown valid counterevidence, and whether it avoids overcorrecting unrelated claims.
7. **Response-loop completeness:** whether each material public theme has a traceable disposition: changed, considered but unchanged, deferred, or rejected with reasons.
8. **Uncertainty discipline:** whether the output appropriately labels unknowns and avoids spurious precision.
9. **Time and cost:** human hours, computation cost and review burden relative to the baseline.
10. **Accessibility and comprehension:** whether a diverse set of readers can correctly explain the proposal, trade-offs and unresolved questions after reading the report.

## Secondary measures

- performance across policy areas and party-perspective rotation;
- whether the adversarial model creates straw men;
- group-specific error rates and omissions;
- privacy/security failure count;
- forecast calibration after sufficient real outcomes exist;
- whether public participants can see how their feedback is handled.

## Pre-registered failure criteria

Stop or redesign if the system:
- invents or materially misrepresents citations at a rate not better than baseline;
- systematically creates a more demanding burden of evidence for one political perspective;
- treats open voluntary input as representative by default;
- removes minority perspectives or unresolved facts from the record;
- obscures accountable humans or suggests AI made the final decision;
- increases report complexity without improving comprehension or traceability;
- leaks personal or sensitive information;
- delivers no meaningful improvement over the simpler ledger once costs are included.

Exact numeric thresholds should be set by a pilot team before examining results, not chosen afterwards to declare success.

## First testable experiment

1. Select one bounded issue in the development-levy policy process.
2. Freeze a dated source pack and record all included documents.
3. Write a preregistered case question, hypotheses and scoring rubric.
4. Create one conventional analysis and one Policy Lab analysis from the same pack.
5. Have two or more reviewers independently verify sources and rate categories without being told which output used the tool, where practical.
6. Publish disagreements and errors, not just averages.
7. Revise the workflow and repeat with the same and a second case.

## What tests do not prove

Passing unit tests shows only that specified code paths behave as expected. A synthetic benchmark shows performance against the definitions and fixtures chosen by its author. Neither is evidence of real-world policy improvement, political neutrality, citizen representativeness or forecasting accuracy. These require distinct evaluation designs and external review.
