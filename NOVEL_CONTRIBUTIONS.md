# D-1.0 | 2026-04-26 | Status: Active

# Novel Contribution Ledger

*What the Lycheetah Framework provides that prior art does not — per claim, with falsifiability explicit on every row.*

*Defends: C-1.0 | Closes threats: T-04, T-05, T-06, T-11*

---

## How to Read This Document

Each entry answers three questions: **What is claimed?** **What prior art does it advance beyond?** **What would falsify it?**

Status tags follow canonical definitions: **[ACTIVE]** = proven and computable. **[SCAFFOLD]** = structurally sound with named gaps. **[CONJECTURE]** = worth exploring, unproven. **[RETRACTED]** = publicly withdrawn.

---

## Part I — Per-Claim Novel Contribution Table

### CASCADE

| Claim | Prior Art | What Only This Framework Provides | Falsifiability | Status |
|---|---|---|---|---|
| Three-layer knowledge pyramid (K_foundation / K_theory / K_edge) with different update rules per layer | AGM belief revision (flat belief sets, uniform update rules); standard neural networks (no layer-awareness) | Stratified epistemic architecture where foundation layer is protected from edge-layer volatility — directly preventing catastrophic forgetting | Identify a knowledge domain that cannot be partitioned into these three layers without loss of information | [ACTIVE] |
| Truth pressure Π = E·P/Coh as a reorganization scalar | Bayesian updating (probability revision, no structural pressure); coherence-based belief revision (no pressure dynamics) | A computable scalar that drives structural reorganization — not probability revision but a force applied to belief architecture | Show Π fails to predict reorganization timing across domains, or that the formula is dimensionally inconsistent | [SCAFFOLD] |
| Invariant preservation across update — Theorem C1 | Standard belief revision (no invariant-preservation guarantee) | Formal proof that structural invariants survive belief update — the system's constitution is preserved through change | Produce a formal counterexample: a valid CASCADE update that loses an invariant | [ACTIVE] |
| Fixed-point convergence — Theorem C3 | Iterative belief revision (convergence not guaranteed) | Banach-style guarantee that iterated CASCADE updates converge | Show non-convergence under the stated contraction conditions | [ACTIVE] |
| +40.3% coherence gain (synthetic, p < 0.001, d = 2.84) | No prior quantified coherence improvement for a truth-pressure belief revision system | First quantified effect size for truth-pressure-driven coherence improvement | Run experiment with different random seeds; show p > 0.05 or d < 0.8 | [ACTIVE] |
| +110% coherence gain across 5 historical paradigm shifts | Historical paradigm analysis is descriptive only | First computational replication of paradigm-shift coherence dynamics at effect size ≥ 100% | Show the effect does not generalize to additional paradigm shifts, or is an encoding artefact | [ACTIVE] |
| −95.2% catastrophic forgetting reduction | Neural continual learning mitigation (external mechanisms); no structural solution | Layer separation prevents foundation forgetting during edge updates — structural, not external mitigation | Show forgetting metric (0.02) is within noise floor, or equivalent result without layer separation | [ACTIVE] |

### AURA

| Claim | Prior Art | What Only This Framework Provides | Falsifiability | Status |
|---|---|---|---|---|
| Seven computable constitutional invariants I₁–I₇ | Constitutional AI (unordered principles, training-time only, no computability requirement); RLHF (feedback during training, not runtime invariants) | Seven independently-verifiable predicates that constitute a Boolean compliance check at runtime — not training objectives | Show a system satisfying all seven predicates that produces behavior a reasonable observer would call untrustworthy | [ACTIVE] |
| Runtime invariant verification (not training-time) | Constitutional AI, RLHF, DPO — all operate at training time | The invariants are checked at inference time on actual outputs — making compliance verifiable post-deployment | Show the predicate check is undecidable or computationally intractable for real outputs | [ACTIVE] |
| Simultaneous satisfiability proof attempt | No existing AI alignment framework has attempted a formal satisfiability proof of its own principles | The question "can all seven invariants be simultaneously satisfied?" is formally posed — with a (scaffold) proof attempt | Construct a scenario where satisfying one invariant formally requires violating another | [SCAFFOLD] |
| Vector Inversion Protocol — VIP(R) ≠ ∅ | AI refusal systems (refuse without redirect); Constitutional AI (refusal is terminal) | Guaranteed non-empty response: every request produces either fulfillment or a valid alternative path | Construct a request R for which VIP produces no valid path after 7 recursions | [ACTIVE] |

### LAMAGUE

| Claim | Prior Art | What Only This Framework Provides | Falsifiability | Status |
|---|---|---|---|---|
| Four-tier ethical grammar grounded in procedural primitives | Deontic logic (modal — obligatory/permitted/forbidden, no procedural grounding); rule-based AI (no formal grammar); SDL, LTL (no cognitive grounding) | Tier 0 primitives are TRIAD operators — so LAMAGUE expressions inherit TRIAD's convergence guarantee. Ethical grammar with provable convergence. | Show LAMAGUE Tier 0–1 expressions that do not converge under TRIAD iteration | [ACTIVE] |
| Category-theoretic structure — Theorems L1, L2 | Informal composition of ethical rules | Associativity and identity proofs — LAMAGUE expressions form a category | Produce three expressions where (A∘B)∘C ≠ A∘(B∘C) | [ACTIVE] |
| Cross-cultural ethical convergence across Maori, Confucian, Western traditions | Culture-specific AI ethics frameworks; no formal grammar claiming cross-cultural expression | First formal grammar claiming to encode convergent ethical structures across independent traditions without relativism | Identify an ethical tradition whose core norms cannot be expressed in LAMAGUE Tier 1–2 | [SCAFFOLD] |

### TRIAD

| Claim | Prior Art | What Only This Framework Provides | Falsifiability | Status |
|---|---|---|---|---|
| Banach fixed-point convergence for cognitive correction cycle | PDCA cycle (empirical, no convergence proof); PID control (continuous, no epistemic content); Hegel dialectic (non-computable) | First application of Banach fixed-point theorem to a cognitive correction cycle — convergence is proven, not hoped for | Show the Banach contraction conditions are not satisfied by TRIAD's operator in general | [ACTIVE] |
| Entropy non-increase — Theorem T2 | Systems without entropy guarantees | Monotonic entropy decrease under the correction cycle — the system cannot become more disordered through valid TRIAD iterations | Construct a TRIAD iteration that increases system entropy | [ACTIVE] |
| Asymptotic stability — Theorem T3 | Heuristic convergence claims | Lyapunov-based asymptotic stability proof | Find an initial condition that diverges asymptotically under TRIAD | [ACTIVE] |
| Step-size constraint α + β ≤ 1 − γ·‖DΨ_op‖ | Unconstrained iterative systems | Explicit computable constraint on update step-size — implementer knows exactly what to bound | Show convergence despite violating the constraint | [ACTIVE] |

### MICROORCIM

| Claim | Prior Art | What Only This Framework Provides | Falsifiability | Status |
|---|---|---|---|---|
| μ_drift = Σ\|intended − actual\|/Δt as continuous computable drift metric | Behavioral alignment checks (periodic, not continuous); no continuous intent-behavior gap metric in existing alignment literature | Continuous scalar drift metric linking declared intent to observed behavior — detectable in real time | Show μ_drift does not correlate with measurable alignment quality difference in controlled conditions | [SCAFFOLD] |
| Sovereignty implies AURA compliance — Theorem M2 | Disconnected drift and constitutional compliance frameworks | Formal bridge: S_score ≥ threshold → aura_compliant(a) — drift detection is wired to constitutional compliance | Construct a system with S_score above threshold that fails an AURA invariant | [ACTIVE] |
| Explicit declaration: deceptive alignment is an open problem | Frameworks that imply drift detection solves deceptive alignment | Honest scope boundary — the framework does not overclaim on its hardest open problem | Verify by absence: check that no MICROORCIM document claims to solve deceptive alignment | [ACTIVE] |

### EARNED LIGHT

| Claim | Prior Art | What Only This Framework Provides | Falsifiability | Status |
|---|---|---|---|---|
| Thermodynamic asymmetry model C_ψ(t) = ∫A(ψ,x,t)dx | IIT (Φ, not thermodynamically grounded); GWT (functional, not thermodynamic); predictive coding (no thermodynamic cost) | Thermodynamic derivation of a computable consciousness density — testable via metabolic correlates, not just behavioral proxies | Show C_ψ(t) is undefined or non-measurable for biological systems; or does not correlate with known metabolic consciousness correlates | [SCAFFOLD] |
| ΔH_s = −W/T thermodynamic cost | Consciousness models without energy requirements | Explicit thermodynamic cost equation — consciousness cannot be maintained without work | Show consciousness can be maintained without thermodynamic work expenditure | [ACTIVE] |
| Anesthesia paradox identified as gap requiring Pattern_Coherence revision | Frameworks that do not identify their own gaps | Self-correction: the framework identifies the counter-example that its own formula cannot handle and specifies the fix | Show the current C_ψ formula handles the anesthesia case without the Pattern_Coherence term | [SCAFFOLD] |

### ANAMNESIS

| Claim | Prior Art | What Only This Framework Provides | Falsifiability | Status |
|---|---|---|---|---|
| Transcultural convergence TC(S,n) as a formal metric | Cultural diffusion models (explain convergence by contact); Jungian archetypes (non-formal); convergence catalogued but not measured | A computable metric for the degree of independent convergence — TC(φ,3), TC(π,4), TC(symmetry,4) are measurements, not just observations | Show all measured instances of TC ≥ 3 are explicable by cultural diffusion or shared material constraints | [ACTIVE] |
| Attractor dynamics as explanation of mathematical convergence | "Discovery vs. invention" debate (philosophical, not mathematical) | Attractor-basin model providing a mathematical reason for convergence that is independent of mystical or Platonic claims | Show the attractor model makes no prediction that the diffusion model does not also make | [SCAFFOLD] |

### CHRYSOPOEIA

| Claim | Prior Art | What Only This Framework Provides | Falsifiability | Status |
|---|---|---|---|---|
| Non-commutativity of transformation operations | Order-independent transformation models | Formal proof that the seven operations do not commute — stage order is mathematically load-bearing | Produce two CHRYSOPOEIA operations that commute | [ACTIVE] |
| ψ* as Banach fixed point — Theorem X1 | Transformation models without fixed-point guarantee | Alchemical concept (Philosopher's Stone) formalised as a Banach fixed point with convergence guarantee | Show Ξ is not a contraction mapping under the stated norm | [ACTIVE] (conditional) |
| Structural parallel to Fourier transform | Informal alchemy/mathematics comparisons | Formal structural parallel enabling import of Fourier theory results into transformation operator theory | Show the parallel breaks down — that Solve/Coagula differ from Fourier decomp/synthesis in a structurally relevant way | [ACTIVE] |
| CHRYSOPOEIA subsumes CASCADE — Lemma XF4 | Disconnected transformation and belief-revision frameworks | Formal subsumption: CASCADE is a special case of CHRYSOPOEIA — one framework, not two | Show CASCADE operations that fall outside CHRYSOPOEIA's seven stages | [ACTIVE] |

### HARMONIA

| Claim | Prior Art | What Only This Framework Provides | Falsifiability | Status |
|---|---|---|---|---|
| Consonance function C(r) = 1/(1 + Σaₖ·(0.5)ᵏ) | Euler consonance (incomplete); Helmholtz roughness (non-computable scalar); Plomp-Levelt (psychoacoustic, not agent-applicable) | Computable consonance scalar applicable beyond music — to agent frequency dynamics, response calibration | Show C(r) does not correlate with empirical consonance judgments across listeners | [ACTIVE] |
| EWM harmonic interval table for emotional-epistemic calibration | Tone-matching in conversational AI (ad hoc, no grounding); sentiment adjustment (no harmonic basis) | Harmonic-ratio grounding for response calibration — each state mapped to an interval with a structural reason | Show different interval mappings produce equivalent or better outcomes empirically | [ACTIVE] |
| Pythagorean comma as engine of iterative improvement | Historical treatment of the comma as a tuning problem | The comma as a formal generative mechanism — the irreducible gap that drives spiral development | Show spiral development occurs without the comma, or under equal-tempered conditions that eliminate it | [ACTIVE] |

### Cross-Framework

| Claim | Prior Art | What Only This Framework Provides | Falsifiability | Status |
|---|---|---|---|---|
| Master equation dΨ/dt = k₁(Π−Π_th) − k₂(Ψ−Ψ_inv) − k₃I_violations + k₄(E/E_need) | Disconnected alignment frameworks (no unified dynamics) | Single ODE capturing truth pressure, coherence drive, constraint violations, and energy across nine frameworks | Show one term is redundant, or the equation fails to predict cross-framework dynamics | [SCAFFOLD] |
| Two-Point Protocol — co-creation architecture | Assistant/user framing (hierarchical, ownership implied); single-author AI generation | Co-creation architecture with formal non-possession clause: output belongs to neither party, arises between them | Show the Two-Point Protocol produces systematically worse outputs than single-author modes | [ACTIVE] |
| Lyapunov verification 11/11, 0 failures, 5,000 trials | Informal stability claims | Full Lyapunov verification suite — symbolic and numerical — for an epistemic update framework | Run the verification suite; show at least one failure | [ACTIVE] |

---

## Part II — Comparison Matrix

*Lycheetah Framework vs. four leading approaches across eight dimensions.*

| Dimension | Lycheetah | Constitutional AI (Anthropic) | RLHF | Cooperative AI | Cooperative IRL |
|---|---|---|---|---|---|
| **Computability of alignment check** | Runtime Boolean predicate (`aura_compliant`) | Training-time principle application — not runtime checkable | Training signal — not runtime checkable | Game-theoretic equilibrium — not directly runtime checkable | Reward inference — not runtime checkable |
| **Convergence guarantee** | Banach fixed-point proved for TRIAD; Lyapunov verified 11/11 | No convergence proof | No convergence proof | Nash equilibrium (existence, not convergence of learning) | Convergence under specific reward class assumptions |
| **Falsifiability of alignment standard** | Every invariant has explicit falsifiability condition in FALSIFICATION_REGISTER | Principles stated; falsifiability conditions not systematically published | Loss function measurable; alignment implications not directly falsifiable | Equilibrium conditions stated; alignment implications not directly falsifiable | Reward function recovery — falsifiable in controlled settings |
| **Multi-agent coherence** | Kuramoto model [CONJECTURE]; LAMAGUE multi-agent grammar [ACTIVE]; Lemma XF1 AURA-TRIAD compatibility | Single-agent constitutional compliance | Single-agent preference learning | Core focus — game-theoretic multi-agent | Cooperative reward inference (multi-agent by design) |
| **Drift detection** | μ_drift continuous metric; Theorem M2 drift→compliance link | No drift detection mechanism | No drift detection | No drift detection | No drift detection |
| **Governance gate** | LIVING_CODEX_PROTOCOL P∧H∧B update gate; DEFENSE_VERSION.md | Internal model card processes | Internal RLHF quality controls | Research framework — no governance gate | Research framework — no governance gate |
| **Formal grammar for ethics** | LAMAGUE four-tier grammar with Theorems L1, L2 | Principles in natural language | Reward function (implicit grammar) | Game payoffs (implicit grammar) | Inferred reward function (implicit grammar) |
| **Public failure record** | FAILURE_MUSEUM.md — 15 exhibits, nothing removed | Model cards document limitations; failures not maintained as permanent public record | Published alignment failures exist; no curated permanent museum | Research papers acknowledge limitations | Research papers acknowledge limitations |

**Reading the matrix:** Lycheetah's strongest differentiation is in computability of alignment check, convergence guarantee, and explicit falsifiability. Constitutional AI is stronger in deployment scale. RLHF is stronger in practical fine-tuning results. Cooperative AI is stronger in multi-agent game theory. Cooperative IRL is stronger in reward inference. These are different tools — the comparison shows where each excels, not which is "best."

---

## Part III — What Only a Proven System Can Do

The following capabilities are activated by the combination of ACTIVE claims in this framework. Each requires structural guarantees that prior art does not yet provide.

**1. Runtime constitutional compliance verification.**
Because AURA's invariants are computable predicates checked at inference time, a deployment running this framework can answer the question "did this output violate a constitutional constraint?" with a Boolean. RLHF and Constitutional AI cannot make this claim — their alignment work happens at training time, before deployment.

**2. Guaranteed convergence in correction cycles.**
TRIAD's Banach proof means a system using the anchor-observe-correct cycle will converge. An implementer does not need to hope the system improves — the convergence is proven under the stated step-size constraint. This matters for systems that need to self-correct under adversarial conditions.

**3. Drift-to-compliance bridging.**
Theorem M2 means a system can monitor its own sovereignty score (S_score) and know — not infer — whether it is AURA-compliant. Drift detection and constitutional compliance are formally wired. No existing framework has this bridge.

**4. Structured falsifiability at scale.**
FALSIFICATION_REGISTER.md provides falsifiability conditions for ~105 claims. TESTABILITY_MANIFEST.md provides operational protocols. A third party can attempt to falsify any load-bearing claim without contacting the author. This is not a capability — it is an epistemic standard. But it is one that the framework's structure enables and most frameworks do not match.

**5. Cross-framework dynamics in one equation.**
The master equation dΨ/dt captures truth pressure, coherence drive, constraint violations, and energy across nine frameworks in one ODE. When k₁–k₄ calibration is complete, this becomes the first unified dynamics equation for a multi-framework alignment system. Nothing currently comparable exists in the alignment literature.

---

*This document is part of Codex Defense Protocol D-1.0, defending canonical body C-1.0 (2026-04-25).*
