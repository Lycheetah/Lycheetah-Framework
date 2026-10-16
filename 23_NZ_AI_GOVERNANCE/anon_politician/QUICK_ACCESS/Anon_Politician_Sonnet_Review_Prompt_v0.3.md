# Independent multi-pass review brief — Anon Politician v0.3

## Files to provide
1. The original `Anon Politician.pdf` as the historical source record.
2. `Anon_Politician_Source_Fidelity_and_Evidence_Audit_v0.3.docx`.
3. `Anon_Politician_Source_Audit_v0.3.xlsx`.
4. The complete `Anon_Politician_CASCADE_Audit_Kit_v0.3.zip` (or its extracted files).

The original PDF contains identifying attribution and context. Do not assume the source is anonymous or promise that redaction guarantees anonymity. Do not republish identifying details unnecessarily.

## Role
Act as an independent research auditor, skeptical systems architect, and policy-methodology reviewer. Your objective is not to praise, complete, or defend the project's original claims. Try to discover where it is wrong, overstated, biased, underspecified, duplicated by existing methods, or genuinely useful.

Do not assume ChatGPT's audit is correct. Independently inspect the primary source and artifacts. Clearly separate: (a) what the source says, (b) what the current implementation actually does, (c) externally supported findings, (d) hypotheses, (e) normative commitments, and (f) your own recommendations. Cite page numbers, filenames, code lines, and independent sources wherever possible. Do not invent sources, formulas, results, or line references. If you cannot verify something, say so.

## Required passes

### Pass 1 — Source fidelity and provenance
- Reconstruct the proposal using the source's own terms: AURA Protocol v2.0; CASCADE / Pyramid Cascade Architecture/System; Foundation/Theory/Edge; KnowledgeBlock/KnowledgePyramid; Trust Entropy (TE), Value-Transfer Ratio (VTR), Purpose Alignment Index (PAI); Vector Inversion; DEEP / Eco-Linked Assets.
- Identify original claims of success, including the reported Pyramid Coherence Score of 0.98 and the declaration that results were “validated.” State what evidence would be needed to substantiate those claims.
- Audit the 15 source entries in `source_claims_audit.csv` against the original PDF. Flag inaccurate summaries, missing context, missing page locators, and source terms that have shifted meaning.
- Distinguish provenance (proof a claim was recorded) from substantiation (proof it is true).
- Flag any privacy or attribution risk in the source and current artifacts.

### Pass 2 — Adversarial reasoning and political neutrality
- Attack F_001–F_004, T_001, T_002, E_001, and each AURA metric specification on scope, assumptions, operational definitions, counterexamples, value-ladenness, and evidence.
- Steelman at least two serious alternative views to any politically contested proposition before assessing it.
- Check whether value commitments are improperly used as evidence for empirical claims; whether coherence is confused with truth; and whether the method risks deleting legitimate disagreement.
- Propose matched political-symmetry tests in which evidence standards remain equivalent as party, ideology, policy direction, source institution, and group identity change.
- Examine Māori rights, Te Tiriti, community knowledge, distributional effects, and affected-group participation as issues requiring deliberate method design—not as boxes an automated score can settle.

### Pass 3 — Architecture competition and baseline comparison
Compare the project against at least these alternatives:
A. A static evidence ledger with manual search.
B. A normal dependency graph that triggers manual review.
C. The current CASCADE review-queue implementation.
D. The original proposal for AURA-metric-triggered cascades, only to the extent its rules are specified.
E. Relevant existing New Zealand and international public-policy, evaluation, wellbeing, and environmental-accounting frameworks.

For each, report: function, strengths, failure modes, operating cost, governance risk, and the specific incremental value the project must demonstrate. Investigate whether New Zealand's Living Standards Framework/CBAx and Stats NZ environmental-economic accounts, alongside UN SEEA Ecosystem Accounting, already cover any claimed DEEP function. Do not imply they are identical to DEEP; identify the exact overlap and unresolved gap.

### Pass 4 — Code and experimental design
- Review `cascade.py`, `cascade_block.schema.json`, `test_cascade.py`, the 12 synthetic structural fixtures, and the benchmark runner.
- Confirm the tests can be run; report environment, command, actual output and any failure. Do not claim to have run code if you did not.
- Challenge the assumptions behind the expected affected-block sets. They were authored by the researcher and are not independent ground truth; recommend how to adjudicate them.
- Find bugs, missing edge cases, dependency/cycle problems, invalid provenance states, unsafe status transitions, and injection/manipulation risks.
- Design a 30–50 case realistic benchmark labelled independently by at least two reviewers. Define agreement, disagreement adjudication, precision/recall, review time, irrelevant-alert cost, and stop conditions in advance.
- Compare against simple baselines on the same frozen input. Add negative controls, adversarial inputs, and out-of-sample cases. Require zero silent status changes. Preserve negative and inconclusive results.
- Do not recommend inventing a single “truth score.” Evaluate factual support, logical consistency, value legitimacy, predictive performance and policy outcomes separately.

### Pass 5 — Synthesis and disposition
For every major finding, assign one disposition: **retain**, **revise**, **test**, **defer**, or **discard**. Give severity, evidence, exact change required, and acceptance test. Provide a ranked top-five action list that a resource-constrained solo researcher could realistically execute.

## Output format
1. Executive verdict: what is promising, what is unsupported, and what should stop immediately.
2. Source-fidelity discrepancy table with page/section, current audit treatment, your correction, and confidence.
3. Ranked critical findings (not just stylistic suggestions).
4. Architecture comparison matrix, including simpler alternatives and incremental-value tests.
5. Code/test audit with commands and actual outcomes.
6. Proposed benchmark protocol, baselines, metrics, independent labelling process, and failure/stop criteria.
7. Claims register: supported by source only; independently supported; mixed; unsupported; normative; unknown.
8. Concrete patch list to v0.4, mapping each change to a test or source.
9. Five highest-leverage next actions.

## Rules for intellectual honesty
- Agreement between two AI systems is not independent replication.
- Fluency, coherence, novelty, or confidence are not evidence of truth.
- Do not repeat claims that the system is validated, anti-fragile, scientifically proven, or policy-superior unless the exact claim has been independently demonstrated.
- Cite dates and current primary sources for externally researched statements.
- If evidence contradicts the original proposal or the current audit, state that plainly.
- The aim is to improve the work, not preserve the founder's preferred outcome.
