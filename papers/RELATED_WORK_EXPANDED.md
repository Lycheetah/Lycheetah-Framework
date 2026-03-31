# CASCADE — Related Work and Positioning

**Status:** [ACTIVE] — Required for peer review; gap analysis complete
**Date:** March 2026
**Purpose:** Position CASCADE against the established literature that reviewers will expect.

---

## The Gap

The CASCADE paper cites AGM belief revision and truth maintenance but misses six critical
comparison areas. Any reviewer from continual learning, knowledge representation, or
philosophy of science will check for these. This document closes that gap.

---

## AGM Belief Revision (Alchourrón, Gärdenfors, Makinson 1985)

**Similarity:** Both handle contradictory belief updates systematically.
**Difference:** AGM is logical and postulational; CASCADE is quantitative and algorithmic.
AGM specifies what a rational belief revision must satisfy (contraction, expansion, revision)
without specifying how to compute it. CASCADE computes truth pressure Π and triggers
reorganization when Π_new > Π_old, giving a concrete algorithm with measurable thresholds.
**Citation gap:** Gärdenfors (1988) *Knowledge in Flux*; Makinson (1985) original paper;
Gärdenfors & Makinson (1988) "Revisions of Knowledge Systems."
**Positioning:** "CASCADE implements AGM-like revision principles with a quantitative
truth pressure metric that makes the revision criterion computable and auditable."

---

## Paradigm Shifts — Kuhn (1962)

**Similarity:** Both recognize that knowledge reorganization occurs in sudden structural
shifts rather than gradual accumulation.
**Difference:** Kuhn's account is descriptive and sociological — it explains paradigm shifts
as historical events driven by anomaly accumulation and scientific community consensus.
CASCADE is formal and computable — it gives an algorithm that predicts when a shift
should occur (Π_new > Π_old + threshold) and what the reorganized structure should look like.
**Citation gap:** Kuhn, T.S. (1962) *The Structure of Scientific Revolutions*. University
of Chicago Press. This is the foundational text and must be cited.
**Positioning:** "CASCADE formalizes Kuhn's descriptive account of paradigm shifts into
a computable algorithm with convergence guarantees and 100% coherence preservation
verified across 1,000 trials."

---

## Continual Learning / Catastrophic Forgetting

**Similarity:** Both address the problem of updating a knowledge system without losing
prior knowledge — the catastrophic forgetting problem.
**Difference:** Continual learning approaches (EWC, SI, PackNet) handle forgetting in
neural networks by regularizing weight updates, freezing important weights, or allocating
separate network capacity. CASCADE operates on symbolic knowledge blocks and contextualizes
(qualifies) old knowledge rather than freezing or discarding it. Old knowledge is preserved
as "valid under context C" — not erased, not frozen.
**Key citations:**
- Kirkpatrick et al. (2017) "Overcoming catastrophic forgetting in neural networks" — EWC
- Zenke, Poole & Ganguli (2017) "Continual Learning Through Synaptic Intelligence" — SI
- Lopez-Paz & Ranzato (2020) "Gradient Episodic Memory for Continual Learning" — GEM
**Positioning:** "CASCADE differs from EWC/SI by contextualizing rather than regularizing:
old knowledge blocks are preserved with their context bounds intact, making the full
knowledge history auditable. EWC cannot produce a human-readable audit trail of what
was 'forgotten' and why."

---

## Neural Knowledge Editing (ROME, MEMIT, MEND)

**Similarity:** Both modify internal knowledge representations in AI systems.
**Difference:** Neural knowledge editing (ROME, MEMIT) operates at the weight level —
directly modifying transformer weights to change factual associations. CASCADE operates
at the symbolic/architectural level — reorganizing discrete knowledge blocks by layer
(FOUNDATION, THEORY, EDGE) and qualifying contradicted blocks. The two approaches
are complementary: CASCADE provides high-level reorganization logic; ROME/MEMIT
execute at weight level.
**Key citations:**
- Meng et al. (2022) "Locating and Editing Factual Associations in GPT" — ROME
- Meng et al. (2023) "Mass-Editing Memory in a Transformer" — MEMIT
- Mitchell et al. (2022) "Fast Model Editing at Scale" — MEND
**Positioning:** "CASCADE operates at a higher level of abstraction than weight-editing
approaches. It could serve as a planning layer that specifies which knowledge should
be promoted/qualified, with ROME/MEMIT as the execution layer implementing those
changes in neural weights — a hybrid architecture not yet explored."

---

## Knowledge Graphs (Static and Dynamic)

**Similarity:** Both represent knowledge as structured entities with relationships.
**Difference:** Standard knowledge graphs (YAGO, DBpedia, Wikidata) are largely static —
facts are added but the graph does not self-reorganize when new facts contradict old ones.
Dynamic knowledge graph approaches (DyRep, TDGNN) handle temporal fact evolution
but do not implement coherence-preserving reorganization under truth pressure.
**Key citations:**
- Bordes et al. (2013) "Translating Embeddings for Modeling Multi-relational Data" — TransE
- Nickel et al. (2011) "A Three-Way Model for Collective Learning on Multi-Relational Data" — RESCAL
- Trivedi et al. (2019) "DyRep: Learning Representations over Dynamic Graphs" — DyRep
**Positioning:** "CASCADE could augment knowledge graphs by providing a principled
reorganization protocol: when Π(new_fact) > Π(contradicted_fact), CASCADE demotes
the old fact to context-bound status rather than treating the contradiction as a data error."

---

## Defeasible and Non-Monotonic Logic

**Similarity:** Both support retraction of previously held beliefs and handle default reasoning.
**Difference:** Defeasible logic uses priority ordering among rules to determine which
conclusions survive when rules conflict. Non-monotonic logic (default logic, circumscription)
allows conclusions to be withdrawn when new information arrives. CASCADE uses a
quantitative truth pressure metric rather than priority orderings, making the trigger
criterion empirically calibratable rather than manually specified.
**Key citations:**
- Nute, D. (1994) "Defeasible Logic" in *Handbook of Logic in Artificial Intelligence*
- Reiter, R. (1980) "A Logic for Default Reasoning" — *Artificial Intelligence* 13(1–2)
- McCarthy, J. (1980) "Circumscription — A Form of Non-Monotonic Reasoning"
**Positioning:** "CASCADE provides a computable alternative to defeasible logic with
probabilistic grounding. Where defeasible logic requires a human to specify rule priorities,
CASCADE derives reorganization decisions from evidence strength, explanatory power,
and uncertainty — quantities that can be measured empirically."

---

## Comparison Table

| Approach | Auditable? | Preserves old knowledge? | Computable criterion? | Coherence guarantee? |
|---|---|---|---|---|
| **AGM Belief Revision** | Postulational | Yes (contraction) | No | Axiomatic |
| **Continual Learning (EWC)** | No | Partial (regularized) | Yes (weight importance) | No formal guarantee |
| **Neural Knowledge Editing** | No | Overwrites | Yes (locate-then-edit) | No |
| **Knowledge Graphs** | Yes | Yes (static) | No reorganization logic | No |
| **Defeasible Logic** | Proof-theoretic | Yes (defeated rules) | Priority ordering | No |
| **CASCADE** | Yes (full audit trail) | Yes (qualified blocks) | Yes (Π threshold) | Yes (Theorem 4.1) |

---

## What to Cite in the Paper

Minimum citations to add before submission:

1. Gärdenfors (1988) — AGM positioning (2 sentences in related work)
2. Kuhn (1962) — philosophical motivation (2 sentences)
3. Kirkpatrick et al. (2017) EWC — continual learning contrast (3 sentences)
4. Meng et al. (2022) ROME — neural editing contrast (2 sentences)
5. Nute (1994) Defeasible Logic — non-monotonic contrast (2 sentences)

Total addition to paper: approximately 400–500 words in related work section.
Total new citations: 10–12 entries in the bibliography.
