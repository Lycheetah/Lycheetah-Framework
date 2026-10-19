# LYCHEETAH / EARNED LIGHT — RESEARCH PASS 04
## Sovereignty Horizon: from authorized actions to preserved human capability
**Date:** 18 October 2026 (NZDT)  
**Status:** exploratory, locally tested conceptual model. Not an AI agent security gate, a measure of free will, a human study, a production deployment, or a repository integration.

> **Candidate thesis**: A consequential AI system should account for the human's future capacity to understand, redirect, reject, reverse, export, and continue without that particular system—not only for whether an individual action was authorized.

### 1. Why this extension is needed

Forges II–III focused on origin of authority, signed grants, source evidence and deliberately human-initiated reconfirmation. These are *point-in-time* authority controls. They do not establish whether a sequence of perfectly authorized interactions produces increasing dependence, erodes transferable understanding, closes valuable alternatives, or makes exit practically impossible.

**Counterexample:** An assistant may obtain correct approval for every successive change to a user's workflow. Six months later, the user may have inaccessible data, no export path, and no capacity to understand or maintain the result. This can occur without a single forged authorization. Thus security of local permissions is necessary but insufficient for the normative aim of sovereignty.

Conversely, a human can intelligently authorize an irreversible action, sacrifice options for an important commitment, or choose deep interdependence. "Always maximize future options" would be paternalistic and fail the very principle it tries to promote. The user must be allowed to define acceptable tradeoffs.

### 2. Four intellectual roots, and what we have *not* derived

1. **Capabilities and substantive freedom** — Amartya Sen's capability approach separates formal rights/resources from real opportunities, as surveyed by the Stanford Encyclopedia of Philosophy (2025). We adapt this as a design lens, not a claim to have quantified human flourishing. https://plato.stanford.edu/entries/capability-approach/
2. **Information-theoretic empowerment** — Klyubin, Polani and Nehaniv (2005) describe empowerment as channel capacity of an agent's actuation over future observations. Our proxy count is *not* that information-theoretic quantity and must never be mislabeled as it. https://doi.org/10.1109/CEC.2005.1554676
3. **Cybernetic requisite variety** — Ashby relates effective regulation to diversity of disturbances/responses. The analogy suggests preserving viable response repertoires, not that AI options obey a new conservation law. https://panarchy.org/ashby/variety.1956.html
4. **AI-supported human thinking** — Lee et al. (CHI 2025) survey 319 knowledge workers with 936 examples, finding associations between GenAI confidence and reported critical-thinking effort. Observational/self-report; it cannot prove AI use caused skill changes. https://doi.org/10.1145/3706598.3713778

**Additional warning**: Fok et al. (2024) emphasize that explanations do not reliably support correct AI reliance if users cannot verify the underlying prediction. Showing more rationale is not necessarily informed consent. https://doi.org/10.1002/aaai.12182

### 3. The speculative extension: micro-decisions compound into macro-sovereignty

A person may retain formal authority over each local decision while gradually losing the *practical capacity* to make a future decision independently. This is a hypothesis about sequences of commitments and learned/degraded skills, not a thermodynamic law, an account of consciousness, or a proof about metaphysical free will.

Let `R_h(s, τ; B, V)` denote the set of distinguishable future outcomes a particular human `h` can in practice bring about from state `s` within horizon `τ`, resource budget `B`, and their endorsed values `V`. This notation is a **proposed construct**, not a measured mathematical object. A genuine measure would require validated outcome equivalence, feasibility and human preferences.

A candidate operational assessment vector is:

`H(s) = (meaningful_reachable_outcomes, independent_reachable_outcomes, exit_cost, verified_reversibility, human_understanding)`

The fifth item is intentionally absent from our prototype because no participants were tested. Counts alone should not be collapsed into a universal "sovereignty score". The meaning of a future option is subjective, path-dependent and unequally accessible across people.

**Hypothesis H4A:** For some task classes, an assistance interface that surfaces realistic exit costs and transferable skills will lead users to make decisions better aligned with their stated long-term priorities than an immediate-output-only interface.

**Hypothesis H4B:** A skill-transfer mode may improve delayed, unaided task performance relative to opaque delegation; both may improve short-term throughput. This is unknown until tested.

**Hypothesis H4C:** Deliberately exposing all alternatives can backfire through cognitive overload. Some appropriate commitments intentionally reduce future options.

### 4. What is implemented

`sovereignty_horizon.py` is a **read-only scenario assessor**, not an action executor or ethical oracle.

- Accepts user-defined value threshold, effort budget and deadline.
- Rejects explicitly unauthorized and deadline-ineligible candidate actions from the output set.
- Computes distinct *claimed and flagged-as-verified* meaningful future outcome families; options beyond assumed skill or budget are excluded.
- Separately counts independently achievable outcome families, records exit cost and claimed verified reversibility.
- Keeps a baseline that selects the maximum immediate-reward eligible candidate.
- Computes a Pareto frontier across immediate benefit, meaningful alternatives, independent alternatives, exit cost and reversibility. The frontier does not select the user's choice or perform any action.

`scenarios.py` runs ten entirely hand-authored illustrative examples. `test_horizon.py` covers gating, deduplication, the non-automatic decision rule, skill feasibility and two red-team failures. `counterexamples.py` demonstrates manipulation that the metric cannot catch.

### 5. Local outcomes (self-contained synthetic model, NOT empirical validation)

- **14/14 local tests passed**.
- **10/10 constructed scenarios** produced at least one eligible candidate.
- **8/10 constructed scenarios** produced multiple non-dominated alternatives; the other 2 were filtered by deadline or permission constraints.
- **0 real users, 0 external provider effects, 0 real-world exit trials.**
- These numbers are products of deliberately designed examples and cannot be interpreted as efficacy, safety, or population prevalence rates.

Crucially, in `irreversible_but_authorized`, the deliberately consented irreversible commitment stays on the frontier. Sovereignty is not a blanket prohibition against closing doors.

### 6. What the adversary immediately defeated

1. **Equivalence-class spoofing**: the same physical result mislabeled as twenty distinct outcome families yields a reported count of 20 rather than 1. There is no trustworthy equivalence certification.
2. **Independence spoofing**: declaring a vendor-dependent outcome "independent" changes the output from zero to one independently reachable option, with no ability to detect deception.
3. **Attention overload**: a collection of thirty genuinely distinct options counts as thirty even though review effort, comprehension and decision fatigue are unmeasured.
4. **Unknown probabilities**: an improbable option counts the same as a reliable one when both are represented as possible. The assessor does not model stochastic transitions or uncertainty.
5. **Preference and power asymmetries**: thresholds are attributed to the human without a secure process for eliciting real values, coercion, accessibility requirements or changing preferences.

All failures must be part of the research record. The source's `verified=True` field is a self-reported assertion, **not cryptographic, behavioral, or empirical verification**.

### 7. What would falsify the useful part of this research?

Pre-register a small, consented pilot with parallel task conditions: (a) unassisted or existing tool, (b) immediate-output assistant, (c) assistant offering portable artifacts, transparent tradeoffs and optional teaching. Comparable tasks, randomized assignment, blinded scoring when possible, clear privacy and withdrawal process. Record:

- **Delayed unaided task success** on novel tasks rather than quizzes about the system's explanations.
- **Actual exit trial**: export data, reconstitute it under another tool, resume a task; measure completion, time, omissions and financial cost.
- **Decision alignment**: compare decisions against participants' previously stated priorities, not model-favored choices.
- **Comprehension**: ask users to predict the side effects and limitations of their authorized actions.
- **Review burden**: number of prompts, fatigue, time-to-completion, and unsafe approvals.
- **Unintended inequality**: benefits/costs across skill, accessibility and technology-resource levels (with appropriate privacy handling).

Useful negative results: the transparency condition worsens decisions; exit works no better; skill transfer underperforms; decision burden overwhelms gains; improvements exist only for hand-selected tasks. Do not improve the hypothesis by selectively excluding those results.

### 8. Integration path into existing Lycheetah (PROPOSED, NOT CODED)

- **AURA**: the ethical question and right to refuse; preserve human values rather than unilaterally choosing them.
- **LAMAGUE**: typed constraint language for agreed limits and provenance of outcomes; the truth of those declarations is independently challenging.
- **TIM**: horizon and delayed outcome evaluation; distinguish permission-time correctness from later dependence.
- **CASCADE**: transferable skill and knowledge retrieval tests rather than an asserted memory/compression improvement.
- **AZOTH / sovereign harness**: optional pre-effect preview of human-specified tradeoffs, plus post-effect exit trial; cannot replace existing signed permits and reconfirmation.
- **Earned Light**: Layer 0 normative inquiry, with explicit speculative branch on free will / microcosm / experience, separate from production safety claims.

### 9. Near-term research tasks

1. Independently verify a real exit path for a *low-stakes* agent workflow (example: an AI-generated business knowledge base moved between providers).
2. Keep truthful outcome-equivalence identities in an independently controlled verifier rather than arbitrary agent metadata.
3. Estimate probabilities, user effort and decision costs—do not count remote, imaginary possibilities as available agency.
4. Test the tool against a strong conventional baseline: portable formats, undo, confirmation, and skill training, not a deliberately weak straw man.
5. Examine how a sequence of low-risk approved actions changes long-term agency; keep user preferences and voluntary commitments authoritative.

### 10. Position

**Metaphysical:** Lycheetah may explore whether meaningful freedom relates to counterfactual possibilities, consciousness or thermodynamic history. No discovered law or validated consciousness measure is claimed.

**Normative:** A good assistant should not secretly make its user's future agency more fragile while presenting immediate productivity as the only benefit.

**Engineering:** Evaluate future options, actual exit costs, and human understanding *without converting one particular abstract measure into automatic veto power over a competent adult's chosen values*.

> The earned light is not a count of doors left open. It is an informed ability to choose which doors to walk through—and which commitments deserve to close the others.
