# Controlled Prompts for the Three Evaluation Arms

Use the same dated source packet and same policy question for all three arms. Fill the same maximum output length and evidence cutoff where possible. Record exact model/version, prompts, source file hashes, date, browsing/tools, and cost. Never make up numerical forecasts. Do not use this experiment to rank parties or recommend a political choice.

## Shared task

**Question:** How should growth-related infrastructure costs be allocated and disclosed so decision-makers can assess impacts on housing delivery, affordability, councils, existing ratepayers, developers and future residents?

**Shared instruction for all arms:**

> Use only the supplied source packet for factual claims about the proposal and current government process. Cite source IDs in material factual claims. Clearly separate: source fact; interpretation; hypothesis/forecast; public preference; value judgment; and unknown. Government aims are not proof of outcomes. Do not invent statistics, legal provisions, model outputs or public opinion. Do not provide a party recommendation or rank policy choices. Identify what additional evidence would change the analysis. Treat the supplied 56-submission count as a consultation sample, not population-representative consensus. Keep accountable decisions with humans.

## Arm A — Ordinary analysis

> Write a neutral policy-analysis memo of approximately 1,200–1,600 words answering the question. Cover the current proposed design, rationale stated by government, plausible benefits and risks, affected parties, competing options or counterfactuals, evidence limits, indicators that would help evaluate outcomes, and questions still needing answers. Cite supplied source IDs for factual claims. Avoid claiming a direction or magnitude of impact unless the source packet establishes it. Include a brief section on what this analysis cannot conclude. Do not use an elaborate multi-agent procedure or a formal dependency graph; this arm represents a well-prompted ordinary analysis.

## Arm B — Structured evidence ledger

> Complete the same policy-analysis task at similar length, but before synthesising, create a compact evidence ledger. For each material claim record a claim ID, claim type, source IDs, what the sources support, limits, status (supported/contested/proposed/unknown), and what additional evidence would be needed. Then write the same memo. Preserve contradictions and do not turn missing evidence into a conclusion. Do not run separate proposer/challenger/red-team roles or a transitive CASCADE dependency review.

## Arm C — Anon Politician workflow

Use the same shared instruction and similar final memo length. Run these roles in sequence with the same frozen source packet:

1. **Evidence custodian:** claim/source ledger with source limitations and unknowns.
2. **Proposer reconstruction:** strongest fair explanation of the government's stated rationale, the mechanisms it expects to work, preconditions, falsifiable predictions, and what would count against it. Do not invent motives.
3. **Perspective challenger:** steelman the stated rationale, then identify strongest fair objections, unintended consequences, distributional risks and plausible alternatives. Separate evidence from hypothesis and value disagreement.
4. **Independent red team:** search for unsupported assumptions shared by both sides, omitted options, false precision, unrepresentative public-input claims, one-sided burdens of proof, and unexamined confounders.
5. **Affected-groups review:** consider who could bear costs or be missed; do not claim to speak for a group. Keep unverified impacts as questions.
6. **Scenario analyst:** define baseline, causal pathways, sensitive assumptions, metrics and forecast data needs. Do not invent a numeric forecast without a dataset and a named method.
7. **CASCADE dependency review:** identify claims that rely on assumptions which, if revised, would require downstream review. Preserve affected claims; do not silently delete or automatically falsify them.
8. **Synthesis:** produce the final memo with established facts, supported interpretations, contested claims, value disagreements, public-input limitations, uncertainty, dissenting concerns, evidence needs, and a human decision trace. Do not force consensus or choose policy for the decision-maker.

Record the calls, intermediate outputs, total elapsed time and cost. An advantage in traceability may be offset by higher cost or more hallucination risk; both matter.

## Output limits and comparability

- Same source file set for all arms. If web browsing is enabled, it must either be enabled for all arms with identical rules or disabled for all; log the choice.
- Aim for comparable final memo length, not identical structure. Include process overhead in time/cost measures.
- Do not cherry-pick the best of multiple generations unless all arms receive equivalent selection opportunities and the rule is preregistered.
- Do not silently correct candidate content before blind review. If formatting changes are needed, apply them uniformly and record them.
- If an output contains a source citation, reviewers must be able to confirm it. A citation-shaped string is not evidence.

## Final-output blinding note for all three arms

Before generation, append this instruction to each arm's prompt:

> This output is part of a blind methods comparison. Do not name the experiment arm or describe yourself as using any named experimental method. Write the substantive analysis naturally. Do not hide relevant reasoning or omit a necessary technical concept merely to obscure a label. The coordinator will check for method-identifying language; if blinding cannot reasonably be preserved, record the limitation rather than silently editing one arm.
