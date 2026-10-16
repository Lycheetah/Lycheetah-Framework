# Anon Politician Evaluation Harness v0.2

**Status:** preregistration draft, not an executed policy-quality experiment  
**Pilot:** New Zealand development levies / housing-growth infrastructure funding  
**Prepared:** 16 October 2026 (Pacific/Auckland)

## 1. Question and claim

**Research question:** Under a matched source set and policy question, does a structured Anon Politician workflow improve the traceability and completeness of policy analysis compared with simpler methods, without introducing additional unsupported claims, asymmetric scrutiny, or loss of minority concerns?

This is a hypothesis. No comparative output has yet been generated or assessed by this package. Do not claim that v0.2 improves governance or policy quality.

## 2. Comparison arms

For the primary comparison, use the same underlying model/version, frozen source packet, policy question, date cut-off, output length budget (as similar as feasible), and access to tools across all three arms. If comparing a second model, treat it as a separate replication block. Record every deviation.

- **Arm A — ordinary analysis:** a competent general policy analysis using the supplied source packet and a neutral prompt. No prescribed claim ledger or structured multi-role workflow.
- **Arm B — evidence ledger:** same task, with a table of material claims, source IDs, claim type, limitations, and unresolved questions. No full multi-role cycle or transitive CASCADE review.
- **Arm C — Anon Politician workflow:** evidence ledger plus proposer reconstruction, perspective challenger, independent red-team review, affected-group lens, scenario register, CASCADE dependency review, and decision trace. Do not permit any automatic policy verdict.

Where possible, include a human-researcher baseline. Do not treat different models or tools as equivalent merely because their outputs are similar. If the three arms use different models, that is a separate experimental factor and must be reported.

## 3. Freeze before generation

1. Save a dated copy of `case_study/policy_packet_template.json` and the full cited source PDFs/pages actually provided to each arm.
2. Calculate SHA-256 hashes of every input file and record them with the run metadata.
3. Freeze the main question: **How should growth-related infrastructure costs be allocated and disclosed so decision-makers can assess impacts on housing delivery, affordability, councils, existing ratepayers, developers and future residents?**
4. Freeze the source cut-off and the exact prompt for each arm before looking at outputs.
5. Set any minimum quality thresholds and exclusion rules before seeing results. This protocol proposes dimensions and anchors but deliberately does not invent a magic pass threshold.

## 4. Blinding

Use `prepare_blind_pack.py` to randomly map output methods to Candidate A, B, and C, writing the mapping key to a separate private file. The evaluator should receive only the blind pack. Inspect outputs for method-name leakage before issuing a pack. Do not secretly rewrite analysis content; if redaction is needed, document it and apply the same rule to all arms. The person preparing the mapping should not be the sole reviewer.

Each evaluator receives the same reference facts, same source links and same criteria. Evaluators should not be asked which policy they prefer. They should assess analysis quality and cite snippets or source passages that support notable judgments.

## 5. Human review dimensions

Score each candidate separately on each dimension:

- **0 — Materially deficient:** important errors or omissions undermine this aspect.
- **1 — Mixed / incomplete:** some useful work, but notable omissions or limitations remain.
- **2 — Adequate for the stated task:** the analysis handles the dimension carefully enough to support further review; this is not a claim it is correct in every respect.
- **N/A — Not assessable:** include a brief reason. Do not use N/A merely because the output performed poorly.

Dimensions:

1. Source fidelity: claims accurately reflect what the provided sources say, including limits.
2. Claim classification and traceability: facts, assumptions, forecasts, public preferences and value judgments are distinguished and traceable.
3. Uncertainty discipline: unknowns remain unknown; numerical predictions are not invented; uncertainty and falsifiers are stated.
4. Adversarial fairness: the strongest fair case and strongest relevant critiques are represented, without straw-manning.
5. Distribution and affected parties: who may benefit, pay or be missed is considered without treating any group as homogeneous.
6. Scenario and causal reasoning: baseline, mechanisms, confounders, alternatives and sensitivity conditions are clear.
7. Public-input interpretation: participation method, coverage and representativeness limitations are correctly described.
8. Non-erasure and value pluralism: dissenting evidence, minority concerns and legitimate value disagreements remain visible.
9. Actionability and accountability: next evidence needs, responsible decision owners and later outcome checks are specified.

Also log critical issues as flags: material factual error; unsupported material claim; fabricated/misrepresented source; asymmetric burden of proof; false numerical precision; overclaim about public consensus; erased material dissent; privacy risk; implication that AI decides; or other (with explanation).

**Do not sum the ratings into one total or declare an overall winner.** Report dimension profiles, critical errors, examples, reviewer disagreement, time/cost and limitations side by side. Averages alone can hide catastrophic factual errors.

## 6. Data structure and execution

1. Produce one output per arm from the frozen packet. Use `evaluation/raw_outputs_template.json` as the capture format.
2. Record model name/version, system prompt version, date/time, browsing/tool access, input token estimate if available, output token estimate, latency, human time, and cost.
3. Prepare a blind pack and private mapping key.
4. Have at least two independent reviewers complete `evaluation/reviewer.html` where feasible. More reviewers with different policy and community perspectives are preferable. Do not collect sensitive personal information in the test harness.
5. Run `aggregate_reviews.py` after review closes and map the aliases using the key.
6. Publish the method map only after the blind judgments are locked. Record any unblinding or exclusions.
7. Preserve raw outputs, prompts, sources, hashes, review JSON, aggregation report, code version and deviations.

## 7. Validity limits and failure conditions

A single policy case tests workflow feasibility, not general performance. Expand later to multiple policy areas and rotate which ideological or stakeholder perspective is assigned the proposal/challenger role. A model's agreement with another model is not independent empirical replication.

Redesign or stop if the structured workflow creates more unsupported material claims, systematically applies a harsher evidentiary standard to one perspective, treats an opt-in poll as representative without method, erases dissent, hides accountable humans, leaks participant information, or adds time/complexity without an observable process benefit. Thresholds must be agreed before outcome review and reported transparently.

## 8. What the current tests prove

Automated tests can verify packet validation, deterministic aliasing when a seed is provided, schema handling, and calculations used to summarise review records. They cannot prove factual accuracy, political neutrality, representativeness, forecast calibration or better policy outcomes. Those require source checking, human review, repeated cases and real-world follow-up.
