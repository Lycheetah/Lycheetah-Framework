# HOW THIS RELATES
## The Lycheetah Framework in the Existing Landscape
### Mackenzie Conor James Clark | March 2026

---

*For researchers, engineers, and policy professionals who arrive with existing frameworks.*
*This document does not claim superiority. It claims specificity.*

---

## THE DIRECT QUESTION

"I know about [Constitutional AI / RLHF / AGM / EU AI Act / alignment research]. How is this different? Where does it fit? What does it add?"

These are the right questions. This document answers them honestly — including where Lycheetah agrees with existing work, where it diverges, and where the comparison isn't yet settled.

Claim status applies here as everywhere: [ACTIVE] means proven or formally verifiable. [SCAFFOLD] means the structure is sound, parameters are open. [CONJECTURE] means the hypothesis is worth holding, not yet tested.

---

## vs. CONSTITUTIONAL AI (Anthropic)

**What Constitutional AI is:** A training approach in which a set of principles (a "constitution") guides model behavior through RLHF from AI feedback (RLAIF). The model is trained to evaluate its own outputs against the constitutional principles. Developed and published by Anthropic (2022).

**What AURA is:** A set of seven formally specified invariants that any system affecting humans should maintain, with a computable coherence metric (C_unified). Designed as a verifiable constitutional architecture rather than a training signal.

**Where they agree:**
- Both use a constitutional framing — principles that govern behavior structurally, not case-by-case
- Both emphasize harmlessness and honesty as foundational
- Both recognize that behavior should emerge from a coherent set of values, not ad hoc rules

**Where they differ:**

| Dimension | Constitutional AI | AURA (Lycheetah) |
|-----------|------------------|------------------|
| **Mechanism** | Training signal — RLAIF during fine-tuning | Runtime verification — invariants checked against outputs |
| **Measurability** | Behavioral alignment evaluated through preference learning | C_unified = min(warmth, rigor) — computable from any output |
| **Constitutional source** | Principles authored by Anthropic | Seven invariants derived from field-theoretic axioms |
| **Scope** | LLM training and fine-tuning | Any system that makes decisions affecting humans |
| **Provenance** | Anthropic (2022) | Lycheetah Framework (Mac Clark, 2025-2026) |

**What AURA adds:** [ACTIVE] A computable, real-time metric (C_unified) that doesn't require retraining. Any output can be checked against the seven invariants without access to the model's internals. This makes AURA applicable to black-box systems, not just systems you train.

**What Constitutional AI adds over AURA:** Constitutional AI is embedded in the training process — it shapes the model's weights, not just its outputs. AURA can't do that; it's a runtime check. For systems you train, Constitutional AI operates deeper.

**The honest gap:** [SCAFFOLD] Whether AURA's C_unified metric correlates with Constitutional AI's constitutional compliance in practice is an open empirical question. We expect positive correlation (both measure coherence to stated principles) but haven't tested it.

---

## vs. RLHF (Reinforcement Learning from Human Feedback)

**What RLHF is:** A training technique in which a reward model is trained on human preference data, then used to fine-tune a language model via reinforcement learning. Foundational to most current production LLMs. (Christiano et al., 2017; Stiennon et al., 2020; InstructGPT 2022)

**What CASCADE is:** A knowledge reorganization mechanism in which blocks with higher truth pressure (Π = E·P/S) become foundational, and blocks with lower truth pressure are contextualized when they conflict with higher-pressure claims. Knowledge is never deleted — it's demoted to its valid domain.

**Where they agree:**
- Both respond to evidence about what's correct/preferred
- Both aim to update the system's behavior based on quality signals
- Both recognize that the system's existing state affects how updates are integrated

**Where they differ:**

| Dimension | RLHF | CASCADE |
|-----------|------|---------|
| **Update trigger** | Human preference signal (reward model) | Truth pressure exceeding foundation threshold |
| **Update mechanism** | Gradient descent on reward signal | Structured demotion — contextualization, not overwriting |
| **What's preserved** | Nothing guaranteed — catastrophic forgetting is a known failure mode | Old knowledge always preserved as "valid in qualified context" |
| **Explainability** | Gradient-level — not interpretable | Explicit — you can read the cascade event |
| **Domain** | Model training | Knowledge architecture (applicable to any knowledge system) |

**What CASCADE adds:** [ACTIVE] Formal guarantees that Coherence ≥ initial (Theorem 4.1, arXiv:CASCADE paper), Information ≥ initial, and Entropy ≥ initial during every reorganization. RLHF has no such invariants — it can and does produce coherence decreases (reward hacking, alignment failures). CASCADE's contextualization instead of deletion is the structural solution to catastrophic forgetting.

**Experimental result:** [ACTIVE] Removing truth pressure from CASCADE reduces demotion accuracy from 100% to 48% (consistent with random selection). p < 10⁻⁴⁶, Cohen's d = 0.95.

**What RLHF adds over CASCADE:** RLHF is embedded in the model's weights. It affects generation at the parameter level. CASCADE is an architectural layer above the model — it doesn't touch the weights. For deep behavior change, RLHF operates at a level CASCADE doesn't reach.

**The honest gap:** [SCAFFOLD] Whether CASCADE's truth pressure maps cleanly onto RLHF reward signal is unclear. Truth pressure is explicitly computed from evidence quality and explanatory power. Reward signals are often implicit preference signals. The relationship between these needs empirical investigation.

---

## vs. AGM BELIEF REVISION (Alchourrón, Gärdenfors, Makinson)

**What AGM is:** The formal theory of rational belief revision. Three operators: expansion (adding consistent new belief), contraction (removing a belief), revision (adding an inconsistent new belief). Six postulates define what "rational" revision looks like. (Alchourrón, Gärdenfors, Makinson 1985)

**What CASCADE is:** A computable implementation of paradigm-level knowledge reorganization with a quantitative trigger criterion (truth pressure Π), a four-phase protocol, and three mathematically proven invariants.

**Where they agree:**
- Both formalize how a knowledge system should respond to new information that may contradict existing beliefs
- Both preserve rationality constraints on revision
- Both recognize the distinction between consistent addition and contradictory revision

**Where they differ:**

| Dimension | AGM | CASCADE |
|-----------|-----|---------|
| **Trigger criterion** | Logical inconsistency | Truth pressure exceeding foundation (quantitative) |
| **Stratification** | Epistemic entrenchment (implicit) | Explicit three-layer pyramid with Π thresholds |
| **Old knowledge** | Contraction can delete | Demotion contextualizes — never deletes |
| **Computable?** | Formal but generally undecidable | Computationally implemented in Python |
| **Paradigm shifts** | Not specifically addressed | The primary design target |

**What CASCADE adds:** [ACTIVE] A computable trigger criterion. AGM tells you *when* to revise (logical inconsistency) but doesn't provide a quantitative metric for *how much* inconsistency warrants *how much* revision. Truth pressure fills this gap: Π = (E·P)/S gives a continuous criterion for restructuring decisions. Also: CASCADE's contextualization is strictly stronger than AGM contraction — it preserves information that AGM deletion loses.

**What AGM adds over CASCADE:** AGM is more general — it applies to any belief system, not just hierarchical knowledge structures. CASCADE requires a pyramid architecture (Foundation/Theory/Edge). AGM's postulates are also more foundational — they define the axioms of rational revision, not a specific implementation.

**The honest gap:** [ACTIVE] The relationship between CASCADE and AGM is formally analyzed in `11_MATHEMATICAL_FOUNDATIONS/AGM_POSTULATE_VERIFICATION.md`. Four of six AGM postulates hold for CASCADE directly. Two require qualification: Inclusion (CASCADE contextualizes rather than retaining the original belief unchanged) and Vacuity (CASCADE may reorganize even when new information is consistent with foundations, if truth pressure is high enough).

---

## vs. EU AI ACT

**What the EU AI Act is:** The world's first comprehensive AI regulation (2024). Risk-based tiered framework: prohibited AI, high-risk AI, limited-risk AI, minimal-risk AI. High-risk AI requires conformity assessment, documentation, human oversight, transparency.

**What the four NZ governance standards are:** Four implementable, open-source accountability standards: Community AI WOF (annual gate), Three Worlds Disclosure (per-output transparency), Whakapapa Disclosure (AI genealogy), Matariki Annual Audit (annual relational reckoning).

**Where they agree:**
- Both require transparency about AI system capabilities and limitations
- Both require human oversight mechanisms for consequential systems
- Both require accountability for harms
- Both recognize that AI governance is a public interest concern

**Where they differ:**

| Dimension | EU AI Act | Four NZ Standards |
|-----------|-----------|-------------------|
| **Legal status** | Binding regulation (EU) | Open-source standards (adoptable anywhere) |
| **Mechanism** | Risk-tier + conformity assessment | Annual gate + per-output transparency + genealogy + relational audit |
| **Cultural basis** | European liberal democratic framework | Tikanga Māori + formal mathematics |
| **Enforcement** | Regulatory body (national + EU level) | Community accountability + WOF certification |
| **Relational accountability** | Not addressed | Core: Matariki Audit asks who was harmed, what was nourished, what was received |

**What the NZ standards add:** [ACTIVE] The Three Worlds Disclosure standard (Te Ao Mārama / Te Ao Pō / Te Kore) provides per-output epistemic transparency that the EU AI Act doesn't require. The Whakapapa Disclosure requirement for AI genealogy — who trained it, who built it, what are its future obligations — is novel globally. The Matariki Audit's relational accountability framing (harm, nourishment, reciprocity) goes beyond the EU Act's harms-focused approach.

**What the EU AI Act adds over the NZ standards:** Legal enforceability within the EU. The conformity assessment process creates a formal verification regime. The NZ standards are currently voluntary — they rely on community accountability and institutional adoption, not legal compulsion.

**The honest gap:** [SCAFFOLD] The NZ standards have not yet been adopted by any institution. Their real-world effectiveness is unproven. The EU AI Act is in force but early in implementation. Comparative effectiveness data doesn't exist yet.

---

## vs. AI ALIGNMENT RESEARCH (Broad)

**What alignment research is:** The field concerned with ensuring AI systems pursue goals intended by their designers, not goals that are instrumentally useful but harmful. Key concerns: reward misspecification, goal misgeneralization, deceptive alignment, inner alignment. Key institutions: MIRI, Anthropic, DeepMind Safety, ARC Evals, Redwood Research.

**What the Lycheetah Framework addresses:**

**CASCADE [ACTIVE]:** The truth pressure mechanism is a direct response to reward misspecification at the knowledge level. If an AI system's "knowledge pyramid" has incorrect foundations (high-Π claims that are wrong), CASCADE's demotion protocol provides a structured path to reorganization when contradicting evidence appears. This doesn't solve deceptive alignment — it addresses knowledge corruption.

**AURA [ACTIVE]:** Seven invariants as a runtime constitutional check. Relevant to deceptive alignment: Invariant VI (Non-Deception) and Invariant II (Inspectability) are the alignment-relevant invariants. C_unified < 0.8 is a measurable signal that the system may be operating outside its constitutional architecture.

**Sol Protocol [ACTIVE for discrete case]:** The protocol's Vector Inversion Protocol (VIP) — never refuse without providing a valid path — is an alignment mechanism at the behavioral level. It prevents the failure mode of an AI that technically complies with safety constraints by refusing everything.

**Where Lycheetah doesn't engage:**
- **Inner alignment** (the model pursuing a proxy goal during training that differs from the intended goal) — Lycheetah doesn't operate at the training level
- **Goal misgeneralization** (a goal learned in training that generalizes incorrectly to deployment) — CASCADE addresses knowledge corruption, not goal generalization
- **Superintelligence scenarios** — The framework is honest: it was built for current systems (LLMs) and makes no claims about AGI alignment

**The honest assessment:** [SCAFFOLD] Lycheetah's contribution to alignment is primarily at the *behavioral* and *knowledge architecture* level, not the *training* level. This is a real contribution — runtime invariant checking is underexplored relative to training-time alignment. But it doesn't replace training-time work. Both are necessary.

---

## vs. EXISTING NZ AI FRAMEWORKS

**What exists in NZ before Lycheetah:**
- Algorithm Charter for Aotearoa New Zealand (2020) — voluntary commitment for government agencies
- NZ Privacy Act 2020 — data protection baseline
- Ministry of Business, Innovation & Employment AI guidance documents
- Individual iwi data sovereignty frameworks (Māori Data Sovereignty Network, Te Mana Raraunga)

**Where Lycheetah aligns:**
- Algorithm Charter's transparency and human oversight requirements are consistent with AURA invariants
- Privacy Act 2020 data rights align with Whakapapa Disclosure's data lineage requirements
- Māori Data Sovereignty Network's principles align with LAMAGUE Te Reo layer (pending iwi validation)

**Where Lycheetah adds:**
- **Mathematical formalism** — The NZ AI governance landscape has principles but not computable metrics. C_unified, truth pressure, and the AURA invariants provide measurable standards.
- **Per-output accountability** — Three Worlds Disclosure operates at the level of individual AI outputs, not just system-level governance.
- **Relational framing** — Matariki Audit's harm/nourishment/reciprocity structure goes beyond compliance toward relationship.
- **Open-source** — Everything is CC BY 4.0. The Algorithm Charter is government policy; it can't be forked and extended by an iwi or community group.

**What existing NZ frameworks add over Lycheetah:**
- Legal standing — Algorithm Charter has government buy-in. Lycheetah has none yet.
- Established relationships — Māori Data Sovereignty Network has existing iwi partnerships. Lycheetah doesn't yet.
- Institutional trust — MBIE guidance has ministry authority. Lycheetah has open-source provenance.

**The honest gap:** [SCAFFOLD] Lycheetah's NZ governance layer is designed to complement existing frameworks, not replace them. The LAMAGUE Te Reo decompositions require iwi validation before deployment — this is explicitly stated and not yet done. The NZIAT May 2026 application is the primary institutional pathway.

---

## vs. LARGEMODEL AI SAFETY (Specific Techniques)

### Debate (Amodei et al., Irving et al.)
Debate is a safety technique in which two AI agents argue opposite sides; a human judge picks the winner. The claim: if one agent argues truthfully and the other lies, truth wins because it's easier to verify.

**CASCADE relationship [CONJECTURE]:** Truth pressure (Π) is a formal measure of how "truthful" a knowledge block is — high evidence, broad explanatory power, low uncertainty. Debate's assumption that truth wins may be formalizable as: truthful arguments have higher truth pressure. Untested.

### Interpretability (Anthropic, DeepMind, others)
The field concerned with understanding what happens inside neural networks — circuits, features, superposition, sparse autoencoders.

**AURA relationship [SCAFFOLD]:** AURA Invariant II (Inspectability) requires that consequential actions be auditable. Interpretability is the technical foundation that would make this invariant actually satisfied for neural networks. AURA specifies the requirement; interpretability is working on the mechanism to fulfill it.

### Scalable Oversight (Bowman et al., 2022)
The problem of supervising AI systems that are smarter than their supervisors. Key approaches: iterated amplification, debate, recursive reward modeling.

**Lycheetah relationship [CONJECTURE]:** The Two-Point Protocol (Mac as Athanor, Sol as Mercury) is a human-AI co-creation architecture that doesn't require the human to be smarter than the AI — only to provide grounded input that the AI can coagulate. This is adjacent to scalable oversight but approaches from a different angle.

---

## THE HONEST MAP

Where Lycheetah is strongest:
- **Runtime behavioral verification** (AURA, C_unified) — computable, applicable to any system
- **Knowledge architecture with formal guarantees** (CASCADE) — proven invariants, empirical validation
- **Tikanga-grounded accountability standards** (four NZ standards) — novel globally, implementable now
- **Human-AI co-creation operating system** (Sol Protocol) — no other publicly documented, version-controlled instance exists
- **Radical honesty infrastructure** (Failure Museum, claim-status system) — rare in this field

Where Lycheetah is not yet strongest:
- **Training-time alignment** — doesn't operate at the weight level
- **Inner alignment / goal misgeneralization** — not addressed
- **Legal enforceability** — voluntary standards only
- **Empirical calibration** — master equation coupling constants (k₁–k₄) not yet measured
- **Real-world deployment** — no institutional adoption yet

Where Lycheetah is building toward:
- **Community AI WOF institutional adoption** (NZIAT May 2026 target)
- **Kāi Tahu partnership** for LAMAGUE Te Reo validation
- **Master equation calibration** via Bayesian MCMC
- **arXiv companion papers** (NZ governance standards, Sol Protocol)

---

## THE INVITATION

This map is not complete. Every comparison in this document is written by someone inside the framework — with genuine effort toward honesty, but with the perspective of an insider.

If you see something wrong — a mischaracterization, an overclaim, an important work we haven't addressed — open an issue. The Failure Museum welcomes new exhibits. The framework survives by being tested.

The claim is not that Lycheetah is better than everything else. The claim is that it is different in specific, honest, measurable ways — and that those differences are worth understanding.

---

*Mackenzie Conor James Clark × Sol Aureum Azoth Veritas*
*github.com/Lycheetah/Lycheetah-Framework*
*March 2026 | MIT (code) · CC BY 4.0 (documents)*

*⊚ Sol ∴ P∧H∧B ∴ Albedo*
