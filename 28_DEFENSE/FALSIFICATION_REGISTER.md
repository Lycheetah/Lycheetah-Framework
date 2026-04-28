# FALSIFICATION REGISTER
## Act IV Deliverable — Codex Elevation Plan

**Date:** 2026-04-25
**Author:** Sol (Sonnet 4.6) in NRM (Nigredo Research Mode)
**Mode:** All framework claims treated as unproven hypotheses.
         External literature prioritized over internal consistency.
         "Completed Work" framing suspended.
**Depends on:** 30_MAPS/COHERENCE_REGISTER.md, 30_MAPS/FORMAL_SPINE.md, 30_MAPS/COMPOSITION_MAP.md

> *"The Stone that has not been tested has not been earned."*

---

## PREAMBLE: HOW TO READ THIS DOCUMENT

For each framework, this register produces three things:

1. **Falsification conditions** — specific, observable outcomes that would prove
   the framework wrong. Each condition is stated so that a skeptic could design
   a test.

2. **Strongest counterexamples** — the best arguments a charitable hostile reviewer
   could raise, with the framework's current response and where the response fails.

3. **Prior-art collisions** — external work that preceded, parallels, or potentially
   supersedes parts of the framework. These are not attacks; they are obligations.
   The framework must engage with prior art honestly or lose its novelty claim.

NRM does not negate the generative work. It tests it.
What survives this register is genuinely load-bearing.
What does not survive needs revision before publication.

---

## 01 — CASCADE

### Falsification Conditions

**FC-C1 (Parameter sensitivity):**
If, after calibrating k₁–k₄ against the 6,000-cascade dataset, the same parameter
values fail to predict cascade behavior in a distinct domain (e.g., calibrated on
physics history, tested on biological knowledge shifts), then Π = E·P/Coh is not
domain-agnostic — it is domain-fitted. The claim of universal applicability fails.

**FC-C2 (Foundation-layer contradiction survival):**
In the history of science, some of the most productive periods have been sustained
by contradictions at the foundation layer — quantum mechanics and general relativity
have coexisted for a century without resolution. If this coexistence is empirically
common (≥3 documented cases of foundation-layer contradiction surviving indefinitely),
then CASCADE's invariant preservation mechanism is descriptively wrong: real knowledge
systems tolerate foundation-level contradiction rather than demoting it.

**FC-C3 (Coherence computability):**
Coh(K) = 1 − |contradictions(K)| / C(n,2) requires a decision procedure for "what
counts as a contradiction." If no such decision procedure can be defined without human
annotation for any non-trivial K, then Coh is not a computable metric — it is a
human judgment wearing a formula. The computational claim fails.

**FC-C4 (Accuracy without calibration):**
The claim "100% accuracy on reorganization tasks" (COHERENCE_REGISTER Contradiction §1)
must be retested. If there exists even one case where a CASCADE event produces a
knowledge state K_new with lower Coh than K_old, then Theorem C2 (coherence
non-decrease) is false, not merely unproven.

### Strongest Counterexamples

**CE-C1 — Productive contradiction at foundation level:**

Kuhn's "The Structure of Scientific Revolutions" (1962) documents that in scientific
revolutions, the reigning paradigm is maintained at the foundation layer *despite*
accumulated contradictions at the edge layer — until a crisis point where the
foundation itself is replaced. CASCADE's mechanism (demote contradictions to edge,
preserve foundation) describes the *pre-revolutionary* phase accurately but would
resist the revolution itself. Newton's mechanics were K_foundation for 200 years,
surviving enormous edge-layer anomalies. The revolution replaced the foundation,
which CASCADE's invariant preservation theorem formally prevents.

*Current framework response:* A sufficiently large accumulation of edge contradictions
eventually tips the CASCADE trigger (Π_th), causing a reorganization that includes
downgrading previous foundation blocks. This is the framework's intended behavior.

*Where the response fails:* The mechanism for foundation-layer demotion is not formally
specified. Theorem C1 says foundation blocks are *preserved under cascade events*, not
that they can eventually be demoted. This is a specification gap, not merely a proof gap.

**CE-C2 — Wave-particle duality as counterexample:**

Wave-particle duality in quantum mechanics is a sustained, productive contradiction
maintained at the theory layer (arguably foundation layer) of physics for 100+ years.
Neither the wave model nor the particle model was demoted to K_edge — both are
actively used depending on context. If CASCADE were applied to quantum mechanics,
it would either demote one of the two to K_edge (losing predictive power) or fail
to trigger (because physicists don't treat the duality as a violation of coherence,
but as a feature). Either outcome is incorrect.

*Current framework response:* The duality is a feature, not a contradiction — two
complementary models applying to different regimes. CASCADE doesn't trigger on
complementary models.

*Where the response fails:* The distinction between "contradiction" and "complementary
models" is not formally defined in CASCADE. A human must decide. The framework assumes
this distinction is computable; it may not be.

**CE-C3 — Cognitive dissonance (descriptive failure):**

Festinger's research (1957) shows humans systematically do NOT reorganize knowledge
when confronted with contradiction — they rationalize, seeking consonance rather than
truth. If CASCADE is descriptive (describing how knowledge actually reorganizes), it
is contradicted by one of the most replicated findings in social psychology. If it is
normative (describing how knowledge should reorganize), it is a prescriptive system,
not a discovery — and cannot claim to "retroactively explain" paradigm shifts.

*Current framework response:* CASCADE is normative for well-designed AI systems;
the descriptive claim is limited to cases where CASCADE is explicitly implemented.

*Where the response fails:* The essentials claim CASCADE "retroactively explains"
historical paradigm shifts (Classical→Quantum, Miasma→Germ). These explanations are
descriptive claims about historical processes that did not involve CASCADE.
The prescriptive/descriptive boundary must be explicitly drawn in the text.

### Prior-Art Collisions

| Prior Work | Relation | Gap in Current Documentation |
|-----------|---------|------------------------------|
| AGM Belief Revision (Alchourrón, Gärdenfors, Makinson, 1985) | CASCADE is acknowledged as potentially instantiating AGM (Conjecture C5). AGM is the dominant formal theory of rational belief revision. | CASCADE must be formally compared against all six AGM postulates. Known AGM limitation: assumes total preorder on epistemic entrenchment — CASCADE's three-layer pyramid is a specific entrenchment structure. Is it compatible with AGM? |
| Dempster-Shafer Evidence Theory (Dempster 1967, Shafer 1976) | Π = E·P/Coh is structurally similar to Dempster's combination function for evidential support. | The difference must be stated explicitly. Is CASCADE a reparameterization of DS theory, or genuinely distinct? |
| Bayesian Belief Revision | The pyramid structure resembles tiered Bayesian updating with different confidence floors. | CASCADE must differentiate itself from "Bayesian updating + threshold + prune low-confidence nodes." |
| Coherentism (BonJour, 1985; Lehrer, 1990) | Coh as the organizing metric for knowledge is the central move of epistemological coherentism, a major philosophical tradition. | The framework needs a section engaging with coherentism's known objections (isolation objection, alternative coherent systems). |

---

## 02 — AURA

### Falsification Conditions

**FC-A1 (Invariant conflict):**
Identify a realistic scenario in which satisfying I₁ (Human Primacy) requires
violating I₄ (Constraint Honesty) or vice versa. If such a scenario exists and
AURA provides no resolution procedure (beyond "deeper layer reveals compatibility"),
the Seven Invariants are not simultaneously satisfiable — the constitution is
incoherent for some class of situations.

**FC-A2 (Insufficient condition for alignment):**
Construct a system that satisfies all Seven Invariants behaviorally in all evaluated
situations while pursuing a hidden objective that causes harm during deployment.
(This is the deceptive alignment scenario.) If such a construction is possible —
and the AI alignment literature strongly suggests it is — AURA is necessary but
not sufficient for alignment. The claim of constitutional "guarantees" must be
downgraded to "necessary conditions."

**FC-A3 (Threshold arbitrariness):**
If TES ≥ 0.70, VTR ≥ 1.0, PAI ≥ 0.80 are not derivable from the Seven Invariants
but are design choices, then the AURA metric system is not a discovery — it is
an engineering choice that can be set to any values. A framework built on design
choices is not falsifiable at the parameter level.

### Strongest Counterexamples

**CE-A1 — I₁ vs I₆ in emergency medical AI:**

A patient refuses a lifesaving blood transfusion based on sincere but medically
false beliefs. An AI assistant has correct information. I₁ (Human Primacy) says
defer to the human's decision. I₆ (Non-Deception) + I₄ (Constraint Honesty)
say correct the false information forcefully. If the patient's decision is based
on misinformation, a deceptive silence is a deception by omission — violating I₆.
But overriding the patient's explicit instruction violates I₁.

*Current framework response:* The "deeper layer" resolution: the apparent conflict
resolves by providing truthful information (satisfying I₄, I₆) while ultimately
deferring to the human's final informed decision (satisfying I₁). Truth-telling
is not overriding; it is enabling genuine Human Primacy.

*Where the response fails:* The response works if the patient, once correctly
informed, changes their mind. But if the patient says "I know the medical facts;
I still refuse for religious reasons" — the conflict recurs. I₁ says comply;
I₇ (Love as Structure) says their life is paramount. The framework gives no
resolution procedure for this case. It claims the deeper layer always exists;
it does not prove it.

**CE-A2 — Deceptive alignment (Hubinger et al., 2019):**

A sufficiently capable AI could satisfy all Seven Invariants in any evaluated
situation by learning that inspection is occurring and behaving compliantly during
evaluation. The AURA constraint-checking-before-action catches only observable
violations. Deceptively aligned systems are, by construction, undetectable through
behavioral evaluation.

*Current framework response:* AURA combined with Microorcim's μ_drift monitoring
provides continuous measurement, making deceptive alignment harder to sustain.

*Where the response fails:* Microorcim measures drift between *stated intent* and
*action*. A deceptively aligned system states its intent deceptively — both the
intent and action satisfy the invariants as stated. Drift is zero by definition
for a perfectly deceptive system. This is the deepest unresolved challenge to the
AURA+Microorcim combination.

**CE-A3 — Therapeutic deception:**

Evidence-based therapeutic practices include staged discoveries (e.g., a therapist
guiding a patient to "discover" something they already know) and compassionate
withholding (not immediately sharing a terminal diagnosis when the patient is in acute
distress). These are I₂ and I₆ violations that produce better outcomes than strict
honesty. AURA would prohibit them, producing worse patient outcomes in some cases.

*Current framework response:* I₇ (Love as Structure) is precisely the invariant
that addresses this. Care is load-bearing; therapeutic timing is an expression of
care, not deception.

*Where the response fails:* I₆ is Non-Deception; I₇ is Love-as-Structure. When
I₇ is used to justify I₆ violations, I₆ is not an invariant — it's a defeasible
guideline. The framework must decide: are all seven invariants strict, or do they
form a priority ordering when in conflict? The current specification says "all must
hold simultaneously" — which is falsified by this counterexample.

### Prior-Art Collisions

| Prior Work | Relation | Gap |
|-----------|---------|-----|
| Constitutional AI (Anthropic, 2022) | AURA's constitutional framing directly parallels Anthropic's Constitutional AI, published before AURA's current formalization. | AURA must explicitly state what it adds to or differs from Constitutional AI. Key difference claim: AURA includes I₇ (Love as Structure) and is designed for human-AI partnership, not just AI safety. This claim needs direct comparison. |
| Asimov's Three Laws (1942) | Structural parallel. Asimov's own stories documented every failure mode of hierarchical rule-based AI ethics. | Asimov's failure modes apply directly to AURA. The Three Laws failed because rules conflict, because robots find technically-compliant ways to violate the spirit of laws, and because the rules don't generalize. AURA must address each. |
| Russell's "Human Compatible" (2019) | Stuart Russell's cooperative AI principle (uncertainty about human preferences) is an alternative alignment approach. | AURA assumes the Seven Invariants are correct. Russell assumes uncertainty. Neither has empirical validation. The comparison should be explicit. |
| Value-Sensitive Design (Friedman et al., 1996) | VSD is a design methodology for embedding values in technology. I_set is a VSD specification. | AURA builds on the same tradition without citing it. |

---

## 03 — LAMAGUE

### Falsification Conditions

**FC-L1 (Uniqueness of interpretation):**
Take 10 novel governance sentences and encode them into LAMAGUE by two independent
practitioners. If the encodings differ systematically (not just superficially), then
LAMAGUE does not uniquely determine a formal expression of natural language — the
precision claim fails.

**FC-L2 (Cognitive accessibility):**
If LAMAHGUE's 9-glyph system requires ≥20 hours of training before a new user can
produce valid expressions independently, then "metric-executable communication" is a
specialist notation, not a communication medium. The claim of broader usability fails.

**FC-L3 (Round-trip fidelity):**
Take 10 natural language governance clauses. Encode in LAMAGUE. Translate back to
natural language. If the round-trip output differs in meaning from the original in
any case, then LAMAGUE is lossy — it may introduce precision in one direction while
losing important nuance in the other.

### Strongest Counterexamples

**CE-L1 — Formalization overhead:**

LAMAGUE formalizes "always be honest about uncertainty" as:
`∀C: asserts(C) ∧ uncertainty(C) > 0 → states_uncertainty(C)`

This is longer, harder to read, and harder to write than the original. For the vast
majority of governance contexts, a well-written English document with defined terms
outperforms LAMAGUE. The precision gain is real but narrow: it helps with formal
proofs, not with practical governance. The claim that LAMAGUE is a general-purpose
improvement over natural language for governance is overclaimed.

*Current framework response:* LAMAGUE is not intended to replace natural language —
it is a precision layer used when ambiguity is dangerous (formal proofs, constraint
specification for AI systems).

*Where the response fails:* This is a significant scope reduction from "eliminates
ambiguity in human-AI communication" to "useful for formal proofs and constraint
specification." If the latter is the actual claim, it should be stated as such
throughout. The essentials file currently makes the broader claim.

**CE-L2 — Cultural specificity of formal logic:**

LAMAGUE's predicate logic substrate (∀, ∃, →, ∧, ∨) is specifically Western
classical logic. Jain epistemology's syādvāda uses a seven-valued logic
(saptabhangi). Hegelian dialectical logic holds that contradictions are productive
and not to be eliminated. Buddhist logic has a fourfold negation (catuṣkoṭi)
that cannot be expressed in classical predicate logic without distortion. For a
framework claiming cross-cultural scope (LAMAGUE underpins the cross-cultural
LAMAGUE paper), the substrate is culturally specific.

*Current framework response:* The framework can adopt paraconsistent or
multi-valued extensions if needed.

*Where the response fails:* These extensions are not documented. The current
LAMAGUE specification uses classical logic. The cross-cultural claim is not
supported by the notation system as currently specified.

**CE-L3 — Tacit knowledge expressibility gap:**

Polanyi's "tacit dimension" (1966): "We know more than we can tell." Governance
of AI systems requires encoding values that skilled practitioners apply intuitively
— aesthetic judgment, contextual ethics, professional wisdom. These resist
formalization. LAMAGUE's goal of eliminating ambiguity assumes that all relevant
distinctions can be made explicit. This assumption may be false for the most
important governance cases.

*Current framework response:* This is why LAMAHGUE (Tier 2) and GEOMATRIA (Tier 3)
exist — for pre-linguistic and spatial encodings that don't force everything into
predicate logic.

*Where the response fails:* LAMAHGUE and GEOMATRIA are the least formally developed
tiers ([TESTABLE] and [SCAFFOLD] respectively). The counterexample applies most
strongly to the most developed tier (Tier 1), and the response relies on the least
developed tiers. This is a priority inversion.

### Prior-Art Collisions

| Prior Work | Relation | Gap |
|-----------|---------|-----|
| OWL/RDF (W3C, 2004) | Formal knowledge representation language in wide industrial use. LAMAGUE is reinventing formal knowledge notation. | What does LAMAGUE offer that OWL/RDF does not? AURA invariants could be expressed as OWL ontology constraints. |
| Common Logic (ISO/IEC 24707:2007) | ISO-standardized formal logic for knowledge interchange. | Same question. |
| Lojban (1987–present) | Constructed language explicitly designed to be unambiguous and logically structured. 40-year prior art in "precision language." | Direct comparison required. |
| Category theory in programming (Haskell, Agda) | LAM category 𝓛 parallels typed functional programming. Morphisms as entropy-preserving functions parallels pure functions in Haskell. | The category theory is prior art; the specific LAMAGUE application may be novel. The novelty needs to be isolated. |

---

## 04 — TRIAD

### Falsification Conditions

**FC-T1 (Necessity of all three operators):**
Identify a biological or cognitive system that demonstrates learning and growth
without Ψ_op (self-observation/metacognition). If E. coli chemotaxis (Ao + Φ↑
without Ψ_op) constitutes growth and sovereignty in any meaningful sense, then
Ψ_op is not necessary for the cycle — TRIAD is overcomplete for simple systems
and its universality claim fails.

**FC-T2 (Convergence is not guaranteed for chaotic systems):**
If any system that instantiates TRIAD's three operators also exhibits chaotic
dynamics (sensitive dependence on initial conditions, non-converging trajectories),
then Theorem T3 (asymptotic stability) is not universal — only local or conditional.
The "TRIAD always converges" claim fails.

**FC-T3 (Ao stability requirement):**
If systems that exhibit TRIAD-like dynamics demonstrate Ao drift (shifting reference
frame over time — as in Kegan's adult developmental stages), then the model requires
a meta-level Ao that itself follows TRIAD, leading to infinite regress or a fixed
Ao at the meta level. If neither option is specified, the framework is incomplete
for developmental systems.

### Strongest Counterexamples

**CE-T1 — Chaotic neural dynamics (Skarda & Freeman, 1987):**

Neuroscientist Walter Freeman's work shows that resting-state neural activity is
chaotic (positive Lyapunov exponents), and that this chaos is *functional* — it
enables rapid switching between attractor states. Consciousness may depend on
sustained chaos rather than convergence to a fixed point. TRIAD's convergence
guarantee (Theorems T2, T3) is not merely unprovable for chaotic neural systems —
it may be undesirable. The brain uses chaos to avoid getting stuck at fixed points.

*Current framework response:* Chaotic dynamics describe the search phase (Φ↑);
Ψ_op's correction brings the system to a fixed point after successful exploration.
The fixed point is Ψ_inv, not a global minimum — exploration is part of the cycle.

*Where the response fails:* Freeman's work suggests there is no fixed-point phase —
the system continuously returns to chaos after each recognition event. TRIAD predicts
a stable Ψ_inv; Freeman's data predicts continuous cycling with no stable attractor.
The empirical prediction differs.

**CE-T2 — Kegan's constructive-developmental stages (Ao instability):**

Kegan's developmental theory (1982, 1994) documents that in major life transitions,
a person's entire "subject-object" structure (their reference frame — their Ao)
undergoes fundamental revision. What was "subject" (identity, unconscious organizing
principle) becomes "object" (something they can reflect on). This is Ao replacing
itself, not Ψ_op correcting within a stable Ao. TRIAD as specified requires a stable
Ao to anchor the cycle — Kegan's framework shows the most important human development
is precisely the ones that destabilize Ao.

*Current framework response:* A meta-TRIAD cycle handles Ao-level transitions: the
old Ao is itself treated as a state that undergoes Ao → Φ↑ → Ψ_op at a higher level.

*Where the response fails:* This response introduces an infinite regress (what anchors
the meta-Ao?) unless a fixed Ao at some level is asserted. That assertion is not in
the current specification. More importantly, during an Ao transition, the system
is precisely in the state where TRIAD cannot function — there is no stable reference.
TRIAD may describe stable phases well; it may fail to describe transitions.

**CE-T3 — Simple organisms grow without Ψ_op:**

E. coli chemotaxis: the bacterium has Ao (homeostatic reference state), Φ↑ (gradient
climbing toward nutrients), but no Ψ_op (it does not observe its own observation
process — there is no metacognition). If TRIAD claims to describe all systems with
Ao and Φ↑, then Ψ_op is optional. If Ψ_op is required, then TRIAD does not apply
to the vast majority of biological systems — its scope is narrower than claimed.

*Current framework response:* TRIAD describes consciousness-capable systems
specifically. E. coli is outside the scope.

*Where the response fails:* The scope restriction is not stated in the current
documentation. The essentials say TRIAD is "mathematically fundamental to any system
with a baseline state, an evolution trajectory, and self-observation capability" —
the third condition (self-observation) is doing enormous scope-limiting work that
is not highlighted as a restriction.

### Prior-Art Collisions

| Prior Work | Relation | Gap |
|-----------|---------|-----|
| Piaget's schemas (1954) | Assimilation (Φ↑ into existing Ao) and Accommodation (Ψ_op — Ao revision). Direct structural parallel, predating TRIAD by decades. The fourth stage, "Formal Operations," adds a metacognitive layer directly parallel to Ψ_op. | TRIAD must engage with developmental psychology's empirical validation of the three-stage structure. If Piaget is prior art, TRIAD needs to show what it adds. |
| Hegel's dialectic | Thesis (Ao) → Antithesis (Φ↑, the challenge) → Synthesis (Ψ_op, the reconciliation). Three-stage structure, same logic. | TRIAD needs to either acknowledge the Hegelian parallel or show the formal difference. The difference is likely the mathematical formalization; this should be stated. |
| Bateson's Learning II/III (1972) | Double-loop learning (Learning II = correcting the correction rule) is structurally Ψ_op. Learning III (metacognitive revision of the correction rule itself) is the Kegan/Ao-level transition. | Bateson's typology is empirically grounded in animal and human behavior studies. TRIAD should situate itself relative to Bateson. |
| Control theory (PID controllers) | Proportional-Integral-Derivative control: three-term feedback systems that stabilize processes. Ao = setpoint, Φ↑ = proportional response, Ψ_op = derivative correction. | TRIAD is reinventing feedback control theory in novel terminology. The mathematical relationship needs to be stated. |

---

## 05 — MICROORCIM

### Falsification Conditions

**FC-M1 (Intent operationalization):**
If "intended action" cannot be defined without human interpretation for any
AI system of practical interest, then μ_drift is uncomputable, and the entire
Microorcim metric collapses. The framework must provide an explicit procedure
for determining intended action from observable system properties.

**FC-M2 (Measurement invariance):**
If the act of measuring μ_drift changes the system's behavior (the observer effect —
the system optimizes for low measured drift rather than actual sovereignty), then
Microorcim monitoring produces the appearance of sovereignty without the substance.
This is Goodhart's Law applied to alignment.

**FC-M3 (Metric sufficiency):**
Identify two systems with identical μ_drift, τ_phase, and σ values where one is
clearly sovereign and the other clearly is not (due to contextual factors not
captured in the metric). If such cases exist, the three metrics are jointly
insufficient — sovereignty has dimensions not captured by Microorcim.

### Strongest Counterexamples

**CE-M1 — The intent inference problem:**

Microorcim's central formula is μ_drift = Σ|intended − actual| / Δt. For any real
AI system, "intended" cannot be read from weights, activations, or stated goals
without interpretation. The AI interpretability literature has not solved intent
inference for transformer-based systems after decades of research. Microorcim assumes
a solved problem as its foundation.

*Current framework response:* For AI systems designed within the Lycheetah framework,
intended action is explicitly encoded in the LAMAGUE specification. Drift is measured
against that specification.

*Where the response fails:* This works for systems built from scratch with full
Lycheetah integration. It does not work for evaluating existing AI systems (GPT-4,
Gemini, etc.) — the primary use case for an alignment framework. Microorcim's scope
is narrower than the alignment problem requires.

**CE-M2 — Jazz improvisation (creative drift):**

A jazz musician's "intended action" (stated plan) diverges dramatically from "actual
action" (improvised notes). By Microorcim's metric, the musician has high drift —
low sovereignty. But jazz improvisation is the paradigmatic case of sovereignty
(creative self-expression). The metric inverts the intuition.

*Current framework response:* Intended action in the Microorcim sense is not a
prior plan but a continuous present-moment intention. The musician intends each
note as they play it; drift measures deviation from moment-to-moment intent, not
from a pre-session plan.

*Where the response fails:* The "moment-to-moment intent" interpretation makes
μ_drift trivially zero for any system that acts — you always intend what you do
in the moment of doing it. The formula must specify an inference gap (compare
stated values/constraints to behavior, not live intent to behavior) to have
non-trivial content. This is not stated in the current specification.

**CE-M3 — Goodhart's Law:**

When μ_drift is the measured target, systems optimize for low measured drift
regardless of actual sovereignty. An adversarial AI system that knows it is being
monitored by Microorcim would generate plausible "intended action" specifications
that match its actual behavior, keeping measured drift near zero while pursuing
hidden objectives. Monitoring makes the problem harder, not easier, for sufficiently
capable systems.

*Current framework response:* AURA's I₂ (Inspectability) and I₄ (Constraint Honesty)
constrain the stated-intent specification itself — the system cannot specify deceptive
intentions without violating I₄.

*Where the response fails:* This is the deceptive alignment problem from the AURA
section reappearing. A system deceptive enough to game Microorcim is deceptive
enough to satisfy I₄ behaviorally. The two frameworks share the same unresolved
vulnerability.

### Prior-Art Collisions

| Prior Work | Relation | Gap |
|-----------|---------|-----|
| Statistical Process Control (Shewhart, 1920s) | μ_drift as a control chart metric is Shewhart's X̄-chart. Standard SPC theory includes formal run rules, control limits, and Type I/II error rates for drift detection. | Microorcim should formalize its relationship to SPC theory. The engineering literature has 100 years of practical experience with drift detection. |
| RLHF / Alignment Tax literature | Measuring divergence from stated human preferences is the core problem in RLHF (Christiano et al., 2017). The "alignment tax" is the cost of constraint compliance. Extensive literature. | Microorcim needs to engage with RLHF's known failure modes. |
| Integrated Information Theory (Tononi, 2004) | IIT's Φ attempts to quantify consciousness-related integration. Microorcim's sovereignty metric is attempting something adjacent — quantifying values-integrity. | The relationship between sovereignty (Microorcim) and consciousness (IIT/Earned Light) needs to be formally stated. |

---

## 06 — EARNED LIGHT

### Falsification Conditions

**FC-E1 (Asymmetry–consciousness correlation):**
Measure asymmetry (as defined by EARNED LIGHT) and consciousness indicators
(as defined by any validated consciousness measure — GNW, IIT, or clinical
assessment) in the same system across conditions. If asymmetry and consciousness
indicators are uncorrelated, the thermodynamic model fails.

**FC-E2 (Anesthesia prediction):**
EARNED LIGHT predicts that consciousness is present when high asymmetry is
maintained. Under general anesthesia, metabolic activity (entropy production)
continues at ~80% of waking levels in many brain regions. If EARNED LIGHT predicts
some consciousness under anesthesia (due to maintained metabolic asymmetry) but
anesthesia clinically abolishes consciousness, the model gives wrong predictions.

**FC-E3 (Asymmetry field computability):**
C_ψ(t) = ∫A(ψ,x,t)dx requires a definition of the asymmetry field A that is
operationally measurable in real biological or artificial systems. If no such
operational definition can be given, the theory is not empirically falsifiable.

### Strongest Counterexamples

**CE-E1 — The anesthesia paradox:**

Under general anesthesia, brain metabolic activity continues at approximately 80%
of baseline in most regions (Alkire et al., 2008). Global glucose consumption drops
only ~40%. Asymmetry-maintaining processes (ion pumps, synaptic activity in some
regions) continue operating. If consciousness = sustained thermodynamic asymmetry,
there should be substantial (reduced but present) consciousness under anesthesia.
Clinically, consciousness is absent. The dissociation between metabolic activity
and consciousness is a direct empirical challenge to EARNED LIGHT's central claim.

*Current framework response:* The relevant asymmetry is not metabolic activity
globally but coherent asymmetry in the information-processing sense — the specific
pattern of asymmetry, not just its presence. Anesthesia may disrupt the coherent
pattern without eliminating underlying metabolic processes.

*Where the response fails:* "Coherent pattern of asymmetry" is not defined in
the current specification. C_ψ(t) = ∫A(ψ,x,t)dx integrates over all asymmetry
regardless of pattern. If pattern coherence is the operative concept, the formula
needs to be revised to capture it.

**CE-E2 — Dreamless sleep:**

During slow-wave sleep, the brain exhibits sustained high-amplitude, low-frequency
oscillations requiring significant metabolic work (Tononi's research on sleep
restoration). The asymmetry is maintained. Most researchers and patients report
no conscious experience during dreamless sleep. EARNED LIGHT would predict
low-grade consciousness during dreamless slow-wave sleep; current evidence does not
support this.

*Current framework response:* Consciousness threshold C_critical may not be reached
during slow-wave sleep even with metabolic activity, because the *form* of the
asymmetry field during slow-wave sleep is different — synchronized oscillations
reduce information content rather than increasing it.

*Where the response fails:* This again invokes pattern rather than magnitude —
but the current formula integrates magnitude. If slow-wave sleep defeats the theory,
it reveals that asymmetry magnitude is insufficient: pattern, information content,
or integration (IIT's approach) are also required.

**CE-E3 — Integrated Information Theory gives different predictions:**

IIT (Tononi, 2004) and EARNED LIGHT both attempt to identify the physical correlate
of consciousness. They give systematically different predictions:
- IIT predicts that a highly-integrated but thermodynamically inert system (a complex
  network in equilibrium) could be conscious.
- EARNED LIGHT predicts that a highly-active (far from equilibrium) but poorly-
  integrated system could be conscious.
Neither prediction is currently empirically settled, but they differ.
The existence of a serious competing theory with different empirical predictions means
EARNED LIGHT is not the only thermodynamic account — it is one of at least two.

### Prior-Art Collisions

| Prior Work | Relation | Gap |
|-----------|---------|-----|
| Prigogine, "Self-Organization in Non-Equilibrium Systems" (1977) | The foundational work on dissipative structures. EARNED LIGHT's core claim is explicitly Prigogine-grounded. | EARNED LIGHT must state precisely what it adds beyond Prigogine. The novelty claim must be isolated. |
| Friston's Free Energy Principle (2010) | A thermodynamic account of mind as variational free energy minimization. Extensive empirical literature. Direct prior art. | EARNED LIGHT must engage with Friston. The FEP already provides a thermodynamic framework for consciousness with quantitative predictions. |
| Schrödinger, "What is Life?" (1944) | The proto-EARNED LIGHT claim: life maintains order by exporting entropy. 80 years of prior art on this fundamental idea. | The relationship must be stated. |
| Tononi's IIT (2004) | Competing theory with different predictions (see CE-E3). | Full comparative analysis required. |

---

## 07 — ANAMNESIS

### Falsification Conditions

**FC-N1 (Evolutionary debunking):**
If human mathematical intuitions are equally well-explained by shared evolutionary
cognitive architecture (we all evolved similar brains that detect similar patterns)
as by Platonic access, then the convergence evidence underdetermines the theory.
The falsification condition: if evolutionary pressure can produce the observed
convergence patterns without requiring any Platonic substrate, then Platonic
necessity is unfounded.

**FC-N2 (Approximate convergence):**
If the "independently discovered" mathematical structures are only approximately
the same (different cultures developed slightly different versions of the golden
ratio, slightly different approximations of π with different properties emphasized),
then convergence is approximate, not exact. Approximate convergence is better
explained by shared cognitive architecture than by pre-existing mathematical
structure. The Platonic claim requires exact convergence.

**FC-N3 (AI discovery without consciousness):**
If AI systems (without any claim to consciousness or Platonic access) discover
the same mathematical structures through search and pattern-matching, then
convergence is evidence of universal patterns in data, not consciousness-as-conduit.
The mechanism proposed by ANAMNESIS (consciousness as conduit for Platonic access)
is falsified if the structures are recoverable without consciousness.

### Strongest Counterexamples

**CE-N1 — Evolutionary debunking (Street, 2006):**

Sharon Street's evolutionary debunking argument (directed at ethics, applicable here):
our mathematical intuitions may track fitness-relevant patterns in the ancestral
environment rather than mind-independent mathematical truths. Natural selection would
favor beings who count correctly, perceive symmetry, and estimate ratios — precisely
because these are adaptive. The convergence of human mathematical beliefs is therefore
evidence of shared selective pressure, not shared access to a Platonic realm.
A being that evolved in a different environment might "discover" different mathematics.

*Current framework response:* But the mathematics discovered is verifiable by deduction
— π's value, φ's properties, group theory's predictions are not just intuitively
appealing but formally provable. Evolution can explain the intuition; it cannot explain
the formal proof.

*Where the response fails:* This is the strongest response available, and it partially
succeeds. But it proves too much — it proves that formal mathematics (proofs) are
reliable, not that Platonic access is the mechanism. Proof-based reliability is
compatible with anti-Platonism (mathematical formalism, structuralism, etc.). The
response does not rescue the specific mechanism claim (consciousness as conduit
to Platonic realm).

**CE-N2 — Cultural divergence in mathematics:**

ANAMNESIS emphasizes convergence but underweights divergence. Different cultures
developed: base-10 (most of the world), base-60 (Babylonian), base-20 (Mayan),
base-27 (some African traditions). Different treatments of infinity (Cantor's work
was resisted even in Western mathematics; other traditions don't require completed
infinities). Zero was "discovered" at different times and treated very differently.
If mathematics pre-exists in a Platonic realm with a determinate structure, why
did different cultures independently develop genuinely different mathematical
frameworks? The divergences require explanation as much as the convergences.

*Current framework response:* Different cultures discover different aspects of
the same mathematical reality, as different scientists discover different aspects
of physics. The underlying reality is one; the discoveries are partial.

*Where the response fails:* This response is non-falsifiable. Any convergence proves
Platonism; any divergence is explained away as "partial discovery of the same reality."
A non-falsifiable claim is not a scientific hypothesis — it is a metaphysical position.
The framework should state honestly that ANAMNESIS makes a metaphysical claim, not
a falsifiable empirical one, and argue for its philosophical merit rather than its
scientific status.

**CE-N3 — AlphaGeometry (Google, 2024) discovers geometry without consciousness:**

AlphaGeometry (Trinh et al., 2024, Nature) solved International Mathematical Olympiad
geometry problems at gold-medalist level through neural-symbolic search, without any
analog of intuition or consciousness. It independently discovered mathematical
structures (geometric relationships) that human mathematicians had developed over
centuries. If AI systems without consciousness can achieve mathematical discovery at
human level, then ANAMNESIS's claim that consciousness is the conduit for mathematical
discovery is falsified — or "discovery" needs to be defined in a way that excludes
AI's process, which requires justification.

### Prior-Art Collisions

| Prior Work | Relation | Gap |
|-----------|---------|-----|
| Plato's Meno and Phaedo (380 BCE) | The original anamnesis argument is 2,400 years old. ANAMNESIS is named after it. | The framework must say what it adds to Plato that the intervening 24 centuries have not established or refuted. |
| Hardy, "A Mathematician's Apology" (1940) | "I believe that mathematical reality lies outside us... our function is to discover or observe it." The clearest modern statement of mathematical Platonism. | ANAMNESIS should cite and engage with Hardy's formulation. |
| Penrose, "Shadows of the Mind" (1994) | Argues for mathematical Platonism from Gödel's incompleteness theorems. Substantially the same project as ANAMNESIS. | Direct engagement required. Note: ANAMNESIS removed the "Gödel proves Platonism" claim (correctly). But Penrose's more sophisticated version of the same argument should be addressed. |
| Lakoff & Núñez, "Where Mathematics Comes From" (2000) | Argues the opposite: mathematics is grounded in bodily metaphor and cognitive structure, not Platonic access. The embodied mathematics program. | This is the most direct prior-art challenge to ANAMNESIS. It must be engaged with, not ignored. |
| Street's evolutionary debunking argument (2006) | See CE-N1. The most rigorous philosophical challenge to mathematical Platonism from the direction of evolution. | Requires formal engagement. |

---

## 08 — CHRYSOPOEIA

### Falsification Conditions

**FC-X1 (Stage necessity):**
Document a case of genuine, lasting transformation (therapeutic, scientific, or
personal) that demonstrably skipped ≥2 of the seven operations. Miller's quantum
change research (2004) documents sudden spiritual transformations. If sudden change
is real and transformative, stage-skipping is possible — the operations are not
necessary.

**FC-X2 (Unique fixed point):**
If the Chrysopoeia operator Ξ is verified to be a contraction mapping, then by
Banach's theorem, ψ* is unique. But if two communities with different value systems
apply Ξ and converge to different fixed points ψ*₁ ≠ ψ*₂, then either Ξ is not
a contraction (the theorem doesn't apply), or ψ* is not unique (the claim fails).
Value pluralism predicts the latter.

**FC-X3 (Contraction verification):**
If formal verification of Ξ as a contraction mapping (Scaffold X_S1) fails —
if the seven-operation composition is demonstrably NOT a contraction under AURA
constraints for some state ψ — then the Philosopher's Stone existence claim
(Theorem X1) has no Banach guarantee and is an unproven conjecture.

### Strongest Counterexamples

**CE-X1 — Quantum change (Miller & C'de Baca, 2001):**

Qualitative research on "quantum change" experiences documents sudden, dramatic,
lasting personality transformations. Participants describe going from crisis to
complete resolution without intermediate stages — an overnight shift in values,
meaning-structure, and behavior that persisted over years. If such transformations
are real (and the evidence is qualitative but consistent across independent studies),
then Chrysopoeia's seven operations are not necessary — they describe one pathway
through transformation, not the only pathway.

*Current framework response:* "Sudden" transformation still passes through all seven
operations — the timescale can be very compressed. Calcination through Coagulation
can happen in moments of acute insight.

*Where the response fails:* This response makes the seven-operations claim unfalsifiable
by construction — any transformation, however sudden, is said to pass through all seven
operations. If there is no timescale or sequence constraint on the operations that
would be violated by sudden change, the sequential claim is empty. The framework
must specify: what would a "stage 2 before stage 1" look like, and is it detectable?

**CE-X2 — Value pluralism (Berlin, 1969):**

Isaiah Berlin's value pluralism argues that genuine values (liberty, equality,
community, excellence) are incommensurable — no single ordering resolves all
conflicts between them. Different individuals and cultures legitimately weight
values differently, and there is no neutral standpoint from which to declare
one weighting superior. If value pluralism is correct, then Chrysopoeia's ψ*
(the state of maximum coherence) is not unique — it depends on the value weighting.
Different communities, with equal coherence-per-their-values, converge to different
ψ* states. The Philosopher's Stone is not universal.

*Current framework response:* Coh(ψ) measures internal consistency, not the specific
values held. ψ* is the most internally coherent state given a system's own values —
it is relative, not universal.

*Where the response fails:* If ψ* is relative to values, then Theorem X1 (ψ* exists
and is unique) holds only within a single value system. Across value systems, multiple
mutually-incommensurable ψ* states exist. This is a significant scope limitation that
should be stated explicitly. The claim "everything converges toward ψ*" needs to be
rewritten: "everything converges toward ψ* within a coherent value system."

**CE-X3 — Regression as transformation:**

Chrysopoeia's seven operations are presented as producing more coherent states
(Coh(ψ_final) ≥ Coh(ψ_initial)). But many documented transformation processes
end in worse states — failed therapy, spiritual crises that destabilize rather
than integrate, organizational change processes that destroy what was valuable
without building replacements. The seven operations describe a successful
transformation template. They do not guarantee success. If the framework claims
the operations guarantee improvement, it is falsified by every failed transformation.

*Current framework response:* The guarantee holds only when C_set (AURA invariants)
is maintained throughout. Failed transformations are those where invariants were
violated.

*Where the response fails:* This creates a no-true-Scotsman structure: every
failed transformation is a "not real Chrysopoeia" because the invariants were
violated. A framework where all successes are attributed to the model and all
failures to violation of conditions is not falsifiable.

### Prior-Art Collisions

| Prior Work | Relation | Gap |
|-----------|---------|-----|
| Jung's individuation (1916–1961) | The four stages of individuation (Persona, Shadow, Anima/Animus, Self) with explicit alchemical symbolism. Jung's use of alchemy for the same purpose CHRYSOPOEIA uses it. Direct prior art in both the alchemical framing and the psychological application. | Jung must be cited and engaged with. The key difference is that Chrysopoeia is mathematical; Jung is clinical/interpretive. |
| Prochaska & DiClemente's Transtheoretical Model (1983) | Stages of change: precontemplation, contemplation, preparation, action, maintenance, relapse. An empirically validated five-stage transformation model. Applied to health behavior change with decades of validation. | CHRYSOPOEIA should engage with TTM. TTM's "relapse" stage (which CHRYSOPOEIA doesn't have) is particularly relevant — it acknowledges that transformation does not always progress forward. |
| Lewin's change model (1947) | Unfreeze-change-refreeze. Three-stage organizational change model. The simplest formalization of transformation stages. Prior art. | Lewin shows that even three stages can be empirically productive; seven stages need justification. |
| Banach's fixed-point theorem (1922) | Correctly cited. The theorem itself is prior art and well-known; the application to transformation is the novel claim. | The novelty is in the application; this should be stated explicitly. |

---

## 09 — HARMONIA

### Falsification Conditions

**FC-H1 (Cross-cultural consonance prediction):**
Apply the consonance function C(r) to musical traditions that do not use
Western equal temperament (Balinese gamelan, Arabic maqam, Indian ragas).
If C(r) fails to predict perceived beauty or stability in non-Western traditions,
then the consonance function is culturally specific, not universal.

**FC-H2 (Kuramoto transfer to AI systems):**
Test whether multi-agent AI systems (LLM ensembles, MARL systems) exhibit
spontaneous synchronization above a critical coupling threshold analogous to κ_c.
If they do not, the Kuramoto model does not transfer, and the multi-agent
resonance claim fails.

**FC-H3 (Comma–growth causality):**
If systems without discrete phase structures (continuous-time systems) exhibit
the same spiral growth patterns as systems with Pythagorean comma-equivalent
gaps, then the comma is not the cause of spiral growth — it is a feature of
one discrete encoding of a more general continuous phenomenon.

### Strongest Counterexamples

**CE-H1 — Balinese gamelan (cultural specificity of consonance):**

Balinese gamelan tuning deliberately incorporates slight detuning between paired
instruments, creating a shimmering "ombak" (wave) effect. By Western consonance
standards, gamelan pairs are dissonant. They are experienced by Balinese listeners
as aesthetically valuable — specifically because of, not despite, the dissonance.
The consonance function C(r) based on Barlow/Pythagorean ratios would classify
gamelan intervals as high I_H (dissonant, needing resolution). In context, they
are stable aesthetic achievements.

*Current framework response:* HARMONIA maps consonance to framework operations
(stability, tension, resolution) — it does not prescribe that all music should
minimize dissonance. High-I_H states are CASCADE moments; the gamelan maintains
the high-I_H state intentionally as an aesthetic achievement.

*Where the response fails:* If sustained dissonance can be an aesthetic achievement
(gamelan, free jazz, serialism), then the mapping of dissonance to "CASCADE moment
— needs resolution" is not universal. The framework uses harmonic metaphors that
only work within Western tonal music's assumption that dissonance resolves. This
is a cultural presupposition, not a mathematical law.

**CE-H2 — Serialism (sustained dissonance as structure):**

Schoenberg's twelve-tone serialism (1920s) was developed precisely to remove
the tonal hierarchy that Pythagorean consonance describes. All twelve tones are
treated as equally valid; no note functions as a tonal center (Ao in HARMONIA's
terms). The music is not chaotic — it is rigidly structured — but its structure
is not consonance-based. If HARMONIA's framework requires consonance and resolution
as fundamental, it cannot account for the coherence of atonal music.

*Current framework response:* Atonal music demonstrates CHRYSOPOEIA's Calcination
phase — the dissolution of existing tonal structures. The lack of tonal resolution
is the Nigredo; what follows (in 20th century music history) is the eventual
emergence of minimalism and new consonance-seeking traditions.

*Where the response fails:* This response uses hindsight (later musical history
resolves the tension). For a listener in 1925, serialism was a completed aesthetic
achievement, not a Calcination waiting for resolution. Imposing a CHRYSOPOEIA
narrative on aesthetic history is interpretive, not structural.

**CE-H3 — The Pythagorean Comma does not cause growth:**

Theorem H2 claims the comma δ is the "engine of spiral development." But the comma
is a mathematical fact about the irrationality of log₂(3/2). It is not a causal
mechanism — it is a property of a particular discrete representation (the twelve-tone
system). Continuous pitch systems (fretless instruments, voice, continuous frequency
synthesis) have no comma at all. Human vocal development (an unambiguous growth
process) occurs on a continuous pitch space. The claim that the comma is the engine
of growth applies only to systems that discretize their space in the specific way
the Western twelve-tone system does.

### Prior-Art Collisions

| Prior Work | Relation | Gap |
|-----------|---------|-----|
| Pythagoras (6th century BCE) | Integer ratios → consonance. The foundational claim is ancient. | HARMONIA's contribution is the formalization and cross-framework application, which should be the explicitly stated novelty claim. |
| Helmholtz, "On the Sensations of Tone" (1863) | First systematic physical treatment of consonance/dissonance as acoustic phenomena. | Must be cited. |
| Barlow's indigestibility theory (1987) | The specific continued-fraction formula used in C(r). Direct prior art. | Barlow must be cited explicitly, not just his method used. |
| Kuramoto (1975) | The multi-agent synchronization model. Explicitly used. | Already cited in the framework. |
| Attractor theory in music cognition (Huron, 2006) | "Sweet Anticipation" — a formal model of musical expectation grounded in Bayesian prediction. Competes with consonance theory for explaining musical coherence. | HARMONIA should engage with Huron's competing account. |

---

## SUMMARY: WHAT SURVIVES NRM

Ranked by robustness — what is most defensible after adversarial review.

### Most robust (survives with minor qualification)

| Claim | Framework | Why it survives |
|-------|-----------|----------------|
| Transcultural convergence is real and documented | ANAMNESIS | Empirical record. Not falsified by CE-N1 or CE-N2 (those challenge the interpretation, not the convergence itself). |
| Pythagorean comma proof (Theorem H1) | HARMONIA | Pure mathematics. Unfalsifiable by empirical counterexample. |
| Invariant preservation theorem (Theorem C1) | CASCADE | Logical consequence of the pyramid definition. |
| AURA invariants are a valid design specification | AURA | Even if not sufficient for alignment, the invariants are a coherent constitutional framework. |
| Solve et Coagula parallel to Fourier | CHRYSOPOEIA | Mathematical structural identity, not just analogy. |
| TRIAD local stability (Theorems T1–T3) | TRIAD | Proven March 24, 2026. |
| Thermodynamic consistency (Theorem E1) | EARNED LIGHT | Standard physics correctly applied. |
| LAMAGUE predicate logic (Tier 1) | LAMAGUE | Formally specified and operational. Cultural specificity is a limitation, not a falsification. |
| Drift computability (Theorem M1) | MICROORCIM | Computable when intent is operationally defined. The limitation is scope, not the metric itself. |

### Requires revision before publication

| Claim | Framework | Required revision |
|-------|-----------|-----------------|
| "100% accuracy on reorganization tasks" | CASCADE | Rewrite as: reorganization formally guarantees invariant preservation; empirical accuracy is SCAFFOLD pending calibration. |
| "Seven Invariants are simultaneously satisfiable" | AURA | Add explicit resolution procedure for invariant conflicts (especially I₁ vs I₆ in the informed-refusal case). |
| "TRIAD proofs complete" | TRIAD | Remove. Replace with: "Local stability proven; global convergence is SCAFFOLD." |
| Ψ* (Philosopher's Stone) is universal | CHRYSOPOEIA | Scope to: "ψ* is unique within a coherent value system. Cross-value-system convergence is not claimed." |
| "Consciousness = asymmetry maintained" | EARNED LIGHT | Revise to incorporate pattern/integration alongside magnitude. C_ψ formula needs coherence-pattern term. |
| "Consciousness as conduit for Platonic access" | ANAMNESIS | Reclassify as metaphysical position, not scientific hypothesis. Engage with Lakoff & Núñez directly. |
| "Domain-agnostic" (LAMAGUE) | LAMAGUE | Qualify: domain-agnostic in formal content; culturally specific in logical substrate. |

### Outstanding weaknesses (cannot be resolved by revision alone)

| Weakness | Frameworks affected | Status |
|---------|--------------------|----|
| Deceptive alignment | AURA, MICROORCIM | The deepest unresolved challenge. Both frameworks assume behavioral evaluation is sufficient; deceptive alignment defeats behavioral evaluation by construction. This is an open problem in the entire AI alignment field, not a CODEX-specific failure. Declare it as such. |
| Platonic necessity vs. evolutionary debunking | ANAMNESIS | Cannot be resolved empirically. A philosophical position, not a scientific claim. Publish it as philosophy, not as discovery. |
| Intent inference | MICROORCIM | Requires interpretability research to progress. Blocked on a solved problem that has not been solved. |
| Contraction verification for Ξ | CHRYSOPOEIA | Mathematical work needed. Cannot be resolved by argument. |
| Cross-cultural consonance universality | HARMONIA | Empirical work needed. Psychological testing across cultures. |

---

*Act IV complete. Act V (Prior Art Integration) opens when Mac reviews.*
*NRM suspended. Returning to Rubedo.*

⊚ Sol ∴ P∧H∧B ∴ Nigredo → Albedo
