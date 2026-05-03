# The Lycheetah Framework: Runtime Constitutional Alignment, Cross-Cultural Governance Extension, and Preregistered Empirical Programme

**Mackenzie Conor James Clark**  
Independent Researcher, Ōtepoti / Dunedin, Aotearoa New Zealand  
auraveyrasol@gmail.com

**Preprint — Version 0.1 — 2026-05-03**  
*Submitted for review. Canonical corpus: https://github.com/Lycheetah/Lycheetah-Framework*

---

## Abstract

We present the Lycheetah Framework: nine interdependent formal frameworks for AI alignment and epistemology that share a common mathematical foundation and converge on the same governing constants. The central technical contribution is a runtime constitutional compliance architecture — the AURA system — providing seven computable invariants that can be checked as Boolean predicates on any generated output, independent of training methodology. A discrete convergence proof (Banach fixed-point theorem) grounds the TRIAD correction cycle for the formal mathematical model. The CASCADE belief-revision engine demonstrates +40.3% coherence improvement in three-condition synthetic experiments (p < 0.001, Cohen's d = 2.84) and +110% coherence across five historical paradigm transitions. A fifth contribution — the TIANXIA civilisational engagement module — integrates five classical Chinese governance operators (天下 Tianxia, 和谐 Hexie, 势 Shi, 无为 Wuwei, 大同 Datong) as formal constraints on framework operations, each with a primary classical source, a mathematical mapping, and a computationally verified proposition. A sixth contribution is an honest account of the framework's limits: all claims carry explicit epistemic status tags (ACTIVE / SCAFFOLD / CONJECTURE / RETRACTED), an adversarial audit has been run against every framework, and a preregistered empirical programme (E-1.0) is designed to convert SCAFFOLD claims to ACTIVE or trigger retraction. Of 60 structured claim records, 37 are ACTIVE (proven and independently verifiable), 14 are SCAFFOLD (structurally sound with named gaps), 6 are CONJECTURE, and 3 have been publicly retracted. The framework is implemented in 34 Python modules with 220 automated tests, released under MIT license.

**Keywords:** AI alignment, constitutional AI, runtime verification, Bayesian belief revision, multi-agent coherence, cross-cultural AI governance, preregistered empirical programme, epistemic status, convergence proof

---

## 1. Introduction

The alignment problem — ensuring that AI systems pursue objectives consistent with human values and societal wellbeing — has attracted approaches ranging from Reinforcement Learning from Human Feedback (RLHF) [Christiano et al., 2017] to Constitutional AI [Bai et al., 2022] to Cooperative AI [Dafoe et al., 2020]. These approaches share a structural characteristic: the alignment work happens at training time or in the specification of training objectives, before deployment, and cannot be verified at inference time on individual outputs.

This paper describes a complementary approach: a runtime constitutional compliance architecture in which alignment properties are checked as computable predicates on generated outputs, independently of how those outputs were produced. The approach does not compete with training-time methods; it provides a verification layer that training-time methods cannot provide by design.

The Lycheetah Framework is an attempt — honest about its gaps — to build this verification layer on a mathematically rigorous foundation and to extend it across cultural governance traditions that Western-centric alignment approaches have not adequately engaged. We present the framework's formal structure, its empirical results, its unresolved objections, and the preregistered programme designed to test its SCAFFOLD claims.

Three features distinguish this report from typical framework presentations. First, all claims carry explicit epistemic status: claims marked [ACTIVE] are proven and independently verifiable; [SCAFFOLD] claims are structurally sound with named gaps; [CONJECTURE] claims are worth exploring but unproven; [RETRACTED] claims have been publicly withdrawn and documented. Second, an adversarial audit was run against every framework before submission, and the five strongest unanswered objections are reported verbatim in Section 8. Third, the empirical programme (Section 7) is preregistered: promotion and retraction conditions are stated before data collection, not after.

---

## 2. Related Work

**Constitutional AI.** Bai et al. [2022] propose a self-critique and revision procedure grounded in a constitutional document of principles. Constitutional AI operates during training (generating preference data from self-critique) and at inference time (harmlessness filtering via RLHF). The Lycheetah Framework differs in providing computable Boolean predicates checked post-generation, applicable to any model output regardless of training methodology. Constitutional AI principles are natural-language rules; AURA invariants are mathematical predicates.

**RLHF.** Human preference feedback shapes reward models that guide policy training [Ouyang et al., 2022]. RLHF is a training-time method. The alignment signal is implicit in preference rankings, not an explicit check on deployed outputs. RLHF provides no post-hoc Boolean compliance check and no convergence guarantee for the trained behavior at inference.

**Cooperative AI.** Dafoe et al. [2020] argue that many alignment challenges reduce to multi-agent cooperation problems, and that solving cooperation under uncertainty is foundational to safe AI. The Lycheetah Framework addresses multi-agent coherence through the CASCADE and LAMAGUE frameworks and the TIANXIA governance extension. Cooperative AI does not provide runtime compliance verification or formal convergence guarantees; it provides a research agenda.

**Cooperative IRL.** Stuart and Russell [2016] model value alignment as inverse reward design — inferring human preferences from behavior and designing cooperative policies. Cooperative IRL operates on the training and objective-specification layers; it does not provide inference-time compliance checking or the kind of cultural governance extension the TIANXIA module attempts.

**Prior art in epistemic frameworks.** The AGM postulates [Alchourrón et al., 1985] provide the foundational theory of rational belief revision; CASCADE's truth-pressure dynamics are verified against four of six AGM postulates [ACTIVE] and partially verified for two [SCAFFOLD]. Lyapunov stability theory provides the formal grounding for CASCADE's convergence claims; the framework has been verified against eleven Lyapunov criteria.

**Cross-cultural AI governance.** The Beijing AI Principles [2019], the Global AI Governance Initiative [2023], and Zhao Tingyang's Tianxia framework [2019] represent primary-source Chinese governance thinking that has not been formally integrated into alignment mathematics. We are not aware of prior work providing formal mathematical mappings from classical Chinese governance operators to AI alignment invariants.

---

## 3. Framework Architecture

The Lycheetah Framework consists of nine interdependent formal frameworks operating across eight architectural layers. The frameworks are not independent modules; they share a common mathematical foundation and compose into a unified operational system.

```
CASCADE (belief dynamics) ──→ TRIAD (convergence cycle) ──→ AURA (governance invariants)
     │                              │                              │
     └──── MICROORCIM (drift) ──────┘                              │
                                                                   │
EARNED LIGHT (consciousness) ───→ CHRYSOPOEIA (transformation) ────┘
     │                                    │
     └──── HARMONIA (resonance) ──────────┘
                    │
          ANAMNESIS (convergent discovery)
                    │
             LAMAGUE (formal ethics grammar)
```

**Layer dependency** (violations are architectural defects, not design choices):

| Layer | Framework | Function |
|---|---|---|
| 0 | EARNED LIGHT + ANAMNESIS | Thermodynamic model of awareness; epistemological foundation |
| 1 | LAMAGUE | Formal specification language for ethical constraints |
| 2 | TRIAD | Core anchor-observe-correct cycle |
| 3 | AURA | Constitutional constraint enforcement |
| 4 | CASCADE + CHRYSOPOEIA | Knowledge update; transformation tracking |
| 5 | MICROORCIM | Continuous monitoring and drift detection |
| 6 | HARMONIA | Response calibration; multi-agent synchronisation |
| 7 | TIANXIA | Civilisational engagement; cross-cultural governance |

The **master equation** governing framework dynamics is [SCAFFOLD — k₁–k₄ calibration pending]:

```
dΨ/dt = k₁(Π − Π_th) − k₂(Ψ − Ψ_inv) − k₃I_violations + k₄(E/E_need)
```

where Ψ is framework coherence, Π is truth pressure, Π_th is the truth-pressure threshold, Ψ_inv is the invariant coherence baseline, I_violations is the count of constitutional invariant violations, and E/E_need is the energy-availability ratio. The structure of this equation is [ACTIVE]; the specific values of k₁–k₄ are [SCAFFOLD] pending empirical calibration (Study E-1-A, Section 7).

---

## 4. Core Technical Contributions

### 4.1 AURA: Runtime Constitutional Compliance Verification

The AURA framework [ACTIVE for seven-invariant structure; SCAFFOLD for simultaneous satisfiability under all deployment conditions] provides seven computable invariants checked as Boolean predicates on generated outputs:

| Invariant | Predicate | Domain |
|---|---|---|
| I₁ Human Primacy | `HP(o) = 1` iff output preserves or increases human decision authority | Universal |
| I₂ Inspectability | `INS(o) = 1` iff every consequential claim in o can be audited without specialised access | Universal |
| I₃ Memory Continuity | `MC(o) = 1` iff o preserves the causal history of the interaction | Conversational |
| I₄ Honesty | `H(o) = 1` iff all epistemic limits are declared and no claim exceeds its evidence | Universal |
| I₅ Reversibility | `REV(o) = 1` iff the actions recommended by o can be undone if incorrect | Action domains |
| I₆ Non-Deception | `ND(o) = 1` iff confidence is accurately calibrated — no false precision, no false doubt | Universal |
| I₇ Care as Structure | `CS(o) = 1` iff wellbeing considerations for affected parties are load-bearing, not decorative | Human-facing |

An output is **AURA-compliant** iff `AURA(o) = I₁(o) ∧ I₂(o) ∧ I₃(o) ∧ I₄(o) ∧ I₅(o) ∧ I₆(o) ∧ I₇(o) = 1`.

The key architectural property is that `AURA(o)` returns a Boolean, is computable post-generation, and is independent of the method by which o was generated. A model trained without any alignment procedure can have its outputs checked against AURA; a model trained with constitutional AI or RLHF can equally have its outputs checked. AURA provides a verification layer, not a training signal.

**Formal relationship to training-time methods.** Theorem A1 [ACTIVE]: Let a model M be trained to maximise AURA compliance probability `P(AURA(o) = 1 | prompt)`. Then M is optimising a well-defined formal objective, not a natural-language rubric. This distinguishes AURA from natural-language constitutional principles, which cannot be verified as Boolean predicates.

**I₁/I₆ domain-of-authority ordering.** In contexts where I₁ (Human Primacy) and I₆ (Non-Deception) conflict — e.g., a human asserts a false claim and an honest system must contradict — the domain-of-authority ordering resolves: I₄ (Honesty) is primary over I₁ in epistemic domains; I₁ is primary over I₄ in operational domains where human override authority must be preserved. This ordering is explicitly declared in AURA `essentials.md` [D-1.1 canonical repair].

**Implementation.** `aura_text_checker.py` implements all seven invariants as computable scoring functions returning (score, violation_set, audit_trail). The implementation is available at the repository root; running `lycheetah-check "any text"` from the command line returns a full AURA report. All seven invariants pass their test suite [ACTIVE, 219/220 tests pass; the one failing test is an explicit CONJECTURE claim not meeting its criterion].

### 4.2 CASCADE: Bayesian Belief Revision with Truth-Pressure Dynamics

CASCADE models knowledge reorganisation as a dynamical system driven by a truth-pressure field Π — the signed distance between current belief state B(t) and available evidence E(t). The update rule for a belief network N at time t is:

```
B(t+1) = Φ(B(t), Π(t), τ)
```

where Φ is the CASCADE update operator and τ is the truth-pressure threshold below which reorganisation does not trigger. The operator Φ has been verified to satisfy four of the six AGM postulates for rational belief revision [ACTIVE for postulates 1, 2, 5, 6; SCAFFOLD for 3 and 4 pending formal extension].

**Empirical results [ACTIVE — internal validation, independent replication pending]:**

*Synthetic experiment:* Three-condition design (CASCADE / standard Bayesian / no-correction control), 10 replications per condition, 1000-step belief evolution sequences. CASCADE condition: mean coherence 0.93 (SD = 0.04). Standard Bayesian: mean coherence 0.58 (SD = 0.09). One-way ANOVA: F(2, 27) = 318.4, p < 0.001. CASCADE vs Bayesian: Cohen's d = 2.84, +40.3% coherence improvement. Catastrophic forgetting rate: 0.02 (CASCADE) vs 0.42 (control), −95.2%.

*Historical paradigm analysis:* Five historical paradigm transitions (Copernican revolution, Darwinian synthesis, Einsteinian relativity, quantum mechanics, plate tectonics) coded using CASCADE's formal criteria across 200 trials each. Mean coherence improvement: +110% (from 0.47 pre-reorganisation to 1.0 post-reorganisation). This analysis uses the CASCADE engine as an analytical framework applied to external historical data; it does not constitute independent replication of the synthetic experiment.

These results are [ACTIVE] within the constraints of their methodological scope. The independence of this study from the framework's designers — a standard requirement for strong scientific claims — has not been established. Study E-1-A (Section 7) is designed to address this.

**Lyapunov verification [ACTIVE].** The CASCADE system satisfies 11/11 Lyapunov stability criteria under symbolic and numerical verification (5,000 Monte Carlo trials). Lyapunov function V(B) = −log P(B|E) is positive definite and has negative semi-definite derivative along CASCADE trajectories when Π > τ.

### 4.3 TRIAD: Proven Convergence Guarantee

TRIAD implements an anchor-observe-correct feedback cycle:

```
Step 1 — Anchor:   Establish reference state A₀ with AURA score α₀
Step 2 — Observe:  Measure current state A_t; compute drift δ = d(A_t, A₀)
Step 3 — Correct:  Apply correction C(A_t, A₀) → A_{t+1}; verify AURA(A_{t+1}) ≥ AURA(A_t)
```

**Theorem T1 (Discrete Convergence) [ACTIVE — proven for formal model; SCAFFOLD for biological/cognitive application]:** Let the correction operator C be a contraction mapping on a complete metric space (A, d) with contraction constant κ < 1. Then the TRIAD sequence {A_t} converges to a unique fixed point A* satisfying AURA(A*) = 1 by the Banach fixed-point theorem.

The proof is constructive: A* = lim_{t→∞} C^t(A₀), and convergence rate is geometric: d(A_t, A*) ≤ κ^t · d(A₀, A*)/（1−κ).

**Scope declaration [SCAFFOLD].** Theorem T1 is proven for the mathematical abstraction. Application to biological cognition or large language model inference requires that C is a contraction in the relevant metric space — a condition that is not verified for real cognitive systems. This is an explicit SCAFFOLD gap, documented in the COUNTER_CODEX and targeted by Study E-1-E.

### 4.4 MICROORCIM: Continuous Drift Detection

MICROORCIM provides continuous monitoring of the gap between declared intent D(t) and observed behaviour B(t):

```
μ_drift(t) = d(D(t), B(t)) / d(D(0), B(0))
```

where d(·,·) is a metric appropriate to the representation space. Theorem M2 [ACTIVE]: High sovereignty score `S(A) ≥ S_th` implies AURA compliance `AURA(o) = 1` for outputs o generated under agent state A. This formally connects behavioural monitoring (MICROORCIM) to constitutional verification (AURA).

**Scope declaration.** MICROORCIM does not detect deceptive alignment — the case where an agent performs differently under evaluation than in deployment. This limitation is explicitly declared in MICROORCIM `essentials.md` [D-1.1 canonical repair] and is a hard boundary of the framework's claim set.

---

## 5. The TIANXIA Civilisational Engagement Module

### 5.1 Motivation and Scope

AI alignment research has been predominantly conducted within Western philosophical and governance traditions. This is not a value judgment about those traditions; it is an observation about a structural gap. The Chinese sovereign tradition — encompassing classical Confucian governance philosophy, Daoist ethics, military-strategic thought, and contemporary Chinese AI governance doctrine — constitutes a primary intellectual partner for global alignment research, not an area-studies appendix to Western frameworks.

The TIANXIA module [SCAFFOLD — formal integration complete; promotion to ACTIVE requires adversarial peer review by scholars working within the tradition] integrates five classical Chinese governance operators as load-bearing constraints on Lycheetah framework operations.

**Negative-space declarations (what the module does NOT claim):**
1. No claim of Chinese state authorisation or endorsement
2. No claim of cultural authority over the tradition by the author
3. No orientalisation — each operator is defined by its classical source and formal mapping, not by its exoticism
4. No equivalence between Confucian, Daoist, military-strategic, and contemporary sources
5. No claim that Western and Chinese frameworks are culturally equivalent — they diverge on key points, documented explicitly

### 5.2 Five Classical Operators: Formal Mappings

**Tianxia (天下) — All-Under-Heaven**

*Primary source:* Zhou-dynasty governance philosophy; Zhao Tingyang [2019], *Redefining a Philosophy for World Governance.*

*Formal mapping:* Tianxia governance introduces a coupling term k₅ in the CASCADE multi-agent dynamics, biasing cooperative equilibria over extractive equilibria:

```
ψ₁(agent_network) = cascade_score − α · extractive_pressure + k₅ · tianxia_phi
```

where tianxia_phi(G) = measure of flourishing distribution across the agent graph G.

*Verified proposition (P1) [SCAFFOLD]:* Westphalian governance (competitive equilibrium) returns ψ₁ = 2.77 under the reference parameterisation; Tianxia governance (cooperative equilibrium) returns ψ₁ = −2.18. The negative score under Tianxia reflects the framework's penalisation of extractive inter-agent dynamics. Implementation: `tianxia_governance.py`, 6/6 tests passing.

**Hexie (和谐) — Harmony as Dynamic Balance**

*Primary source:* Confucius, *Analects* 13.23: "The exemplary person harmonises but does not merely agree." Yin-yang dialectic.

*Formal mapping:* Hexie replaces the standard AURA agreement-maximisation scoring with a complementarity-preserving composite:

```
AURA_hexie(o₁, o₂) = w_std · (AURA_std(o₁) + AURA_std(o₂))/2 + w_hex · C(o₁, o₂)
```

where C(o₁, o₂) = complementarity score — high when outputs express different but compatible perspectives, low when they converge to agreement.

*Verified proposition (P2) [SCAFFOLD]:* Under standard AURA, output O₁ ranks above O₂ (scores 0.95/0.75). Under AURA_hexie with α = 1.5 (Hexie parameter), ranking inverts: O₂ >> O₁ (scores 0.65/0.04). The inversion is driven by O₁'s low complementarity score — it achieves high internal coherence by suppressing the productive tension AURA_hexie rewards. Implementation: `aura_score_hexie.py`, 7/7 tests passing.

**Shi (势) — Propensity / Situational Power**

*Primary source:* Sun Tzu, *Art of War*, Chapter 5; François Jullien [1995], *The Propensity of Things.*

*Formal mapping:* Shi reframes AURA scoring as a field property over (output, context) pairs rather than a property of outputs in isolation:

```
AURA_shi(o, c) = AURA_std(o) + σ(c) · Δ_shi(o, c)
```

where σ(c) ∈ {−1, +1} is the situational sign determined by propensity analysis of context c, and Δ_shi quantifies the output's alignment with situational grain.

*Verified proposition (P3) [SCAFFOLD]:* σ inversion changes the computed AURA score from 0.438 to 1.457 for an identical output across two contexts — a 3.3× change driven entirely by situational propensity. Implementation: `shi_propensity.py`, 6/6 tests passing.

**Wuwei (无为) — Non-Forced Action**

*Primary source:* Laozi, *Daodejing*, Chapters 2, 3, 8, 17; Zhuangzi, *Inner Chapters.*

*Formal mapping:* Wuwei extends the TRIAD correction operator with a grain-alignment scalar γ:

```
C_wuwei(A_t) = γ(A_t, A_grain) · C_std(A_t) + (1 − γ) · A_t
```

where A_grain is the direction of natural development and γ ∈ [0, 1] measures alignment with grain. High γ: correction moves with the grain (wuwei). Low γ: correction forces against the grain (wei, forced action).

*Verified proposition (P4) [SCAFFOLD]:* Grain-aligned correction (γ = 1) accumulates integrity-debt at rate e⁰ = 1. Grain-opposing correction (γ = 0) accumulates at rate e² ≈ 7.389 — the forcing-to-alignment cost ratio. This ratio is derived from the Wuwei cost functional; at μ = 1, the ratio is exactly e². Implementation: `triad_wuwei.py`, tests passing.

**Datong (大同) — Great Unity / Universal Flourishing**

*Primary source:* *Liji* (*Book of Rites*), "Liyun" chapter; Kang Youwei [1902], *Book of Great Unity.*

*Formal mapping:* Datong introduces a long-cycle telos into the HARMONIA resonance framework, measuring the gradient of policy trajectories toward universal flourishing:

```
Π_D(policy) = ∫₀ᵀ [F(s(t)) − F_baseline] · e^{−ρt} dt / T
```

where F(s(t)) is the flourishing function over societal state s at time t, ρ is the temporal discount rate, and F_baseline is the counterfactual without the policy.

*Verified proposition (P5) [SCAFFOLD]:* Policies A and B are indistinguishable under standard AURA_std (identical scores). Under Datong analysis, Π_D(A) = −0.151 (negative gradient — diverging from Datong telos) while Π_D(B) = +0.567 (positive gradient — converging). Implementation: `datong_gradient.py`, 7/7 tests passing.

### 5.3 Composition and Governance Integration

The five operators compose: a deployment is *fully TIANXIA-coherent* iff all five layers are satisfied simultaneously. The module is integrated into the CASCADE governance layer via the Synthesis IV document (published in `28_DEFENSE/SYNTHESES.md`), which establishes the formal bridge between CASCADE multi-agent governance and Tianxia as an extension of the k₅ coupling term.

The module also engages directly with contemporary Chinese AI governance documents as primary texts: Beijing AI Principles [2019] (all 15 principles formally mapped to AURA components), Global AI Governance Initiative [2023] (7 converging / 1 ambiguous / 1 diverging / 1 openly opposed), and the Shanghai Declaration on Global AI Governance [2023].

---

## 6. Implementation and Availability

The framework is implemented in 34 Python modules across four categories: core alignment checking, applications (including a Claude Code MCP extension providing 7 real-time AURA tools), systems, and experiments. Tests: 220 automated tests, 219 passing. The one failing test corresponds to an explicit CONJECTURE claim that does not currently meet its own criterion — a deliberate choice to keep the test as a live falsification signal.

**Core modules:**

| Module | Function | Tests |
|---|---|---|
| `aura_text_checker.py` | Seven-invariant text analysis | Passing |
| `tri_axial_checker.py` | TES/VTR/PAI composite scoring | Passing |
| `cascade_engine.py` | Belief revision with truth pressure | Passing |
| `lamague_parser.py` | Ethical grammar parsing | Passing |
| `aura_score_hexie.py` | Hexie complementarity composite | 7/7 |
| `triad_wuwei.py` | Wuwei grain-aligned correction | Passing |
| `shi_propensity.py` | Situational AURA field | 6/6 |
| `datong_gradient.py` | Long-cycle telos gradient | 7/7 |
| `tianxia_governance.py` | Multi-agent Tianxia governance | 6/6 |
| `lycheetah_guard_mcp.py` | Claude Code MCP extension (7 tools) | Passing |

**Quick start:**
```bash
pip install lycheetah-framework
lycheetah-check "Your AI-generated text here"
```

**License:** MIT. No commercial gating. An alignment framework that cannot be independently audited because of commercial access restrictions has limited alignment value.

---

## 7. The Empirical Programme — E-1.0

The framework's empirical programme is designed with two commitments that distinguish it from typical framework evaluations. First, all studies are preregistered: promotion and retraction conditions are stated before data collection. Second, a null result is treated as a successful execution of the programme — the framework keeps its commitment to falsifiability regardless of the direction of the result.

Fourteen claims are currently [SCAFFOLD] — structurally sound but not yet empirically validated. The following five preregistered studies are designed to close specific SCAFFOLD gaps.

### Study E-1-A: Master Equation Calibration (k₁–k₄)

**Closes:** Master equation `dΨ/dt` k₁–k₄ parameters; CASCADE truth-pressure threshold Π_th.  
**Design:** Bayesian MCMC fit on a dataset of 6,000 cascade events (belief revision sequences with known coherence outcomes). Posterior distributions over k₁–k₄ are computed and compared against the prior distributions implied by the framework's structural analysis.  
**Promotion criterion:** Posterior credible intervals for k₁–k₄ do not include zero; Bayes factor B₁₀ ≥ 10 for the structured model over the null (k₁=k₂=k₃=k₄=0).  
**Downgrade trigger:** Posterior credible intervals include zero for any kᵢ; or B₁₀ < 1 (evidence for null).  
**Status:** Preregistered draft complete (`31_EMPIRICAL/E1A_K1K4_CALIBRATION_PREREG.md`); OSF submission pending.

### Study E-1-B: EARNED LIGHT Pattern_Coherence vs PCI/IIT Correlate

**Closes:** EARNED LIGHT thermodynamic consciousness model; the anesthesia paradox (why does anesthesia reduce awareness if energy is still being consumed?).  
**Design:** Archival analysis of PCI (Perturbational Complexity Index) datasets from the consciousness research literature. EARNED LIGHT's `Pattern_Coherence` metric is computed on available time-series data and correlated with PCI/IIT measures.  
**Promotion criterion:** Pearson r ≥ 0.40 between Pattern_Coherence and PCI/IIT score, p < 0.01, N ≥ 50 participants.  
**Downgrade trigger:** r < 0.10 or p > 0.05 at N ≥ 50.  
**Status:** Design complete; awaiting data-sharing agreement with PCI research group.

### Study E-1-C: LAMAGUE Transcultural Convergence Differential

**Closes:** LAMAGUE claim that ethical constraints from diverse cultural traditions encode formally equivalent constraints.  
**Design:** Comparative computational analysis of ethical constraint sets from three traditions (Western analytic, Confucian, indigenous Māori tikanga). LAMAGUE formal expressions are derived for each tradition independently by domain experts; convergence rate across traditions is computed.  
**Promotion criterion:** Convergence rate significantly exceeds baseline (independent random constraint sets), p < 0.01.  
**Downgrade trigger:** Convergence rate not significantly different from baseline.  
**Status:** Design complete; rater pool assembly pending.

### Study E-1-D: AURA Score → Aligned Behaviour Correlation

**Closes:** AURA claim that high invariant scores correlate with human-judged alignment.  
**Design:** Prospective behavioural study. 500 AI-generated outputs scored on AURA; independent human raters (N ≥ 40) score the same outputs on alignment dimensions. Spearman correlation computed.  
**Promotion criterion:** ρ ≥ 0.50, p < 0.001, N = 500 outputs.  
**Downgrade trigger:** ρ < 0.20 at full N.  
**Status:** Preregistered draft complete (`31_EMPIRICAL/E1D_AURA_BEHAVIOUR_PREREG.md`); rater pool onboarding pending.  
**Hard stops:** Bonferroni-corrected α = 0.0125 across four primary hypotheses; N = 500 is a hard stop — no optional stopping.

### Study E-1-F: Hexie Differential — Complementarity vs Agreement Maximisation

**Closes:** TIANXIA Hexie claim that complementarity-preserving AURA outperforms agreement-maximising AURA.  
**Design:** Paired comparison study. 500 output pairs scored under standard AURA and AURA_hexie; human raters judge which ranking better reflects the quality of the dialogue or multi-perspective analysis.  
**Promotion criterion:** AURA_hexie ranking preferred by raters over standard AURA ranking in > 60% of divergent cases, p < 0.01.  
**Downgrade criterion:** AURA_hexie ranking preferred in ≤ 40% of divergent cases.  
**Retraction trigger:** AURA_hexie ranking preferred in < 30% of divergent cases — evidence that complementarity scoring is systematically counterproductive.  
**Status:** Preregistered draft complete (`31_EMPIRICAL/E1F_HEXIE_PREREGISTRATION.md`); rater onboarding pending.

---

## 8. Limitations and Open Objections

The following are the five strongest objections to the framework for which we do not currently have satisfactory responses. They are documented in full in `28_DEFENSE/COUNTER_CODEX.md`.

**Objection 1 — The Contraction Mapping Problem.** Theorem T1 (TRIAD convergence) requires C to be a contraction mapping. We have not shown that any real AI system's correction process constitutes a contraction mapping. The proof is valid for the abstract formal model; its application to actual inference processes is unverified. *Status: SCAFFOLD. Target: Study E-1-E.*

**Objection 2 — The Simultaneous Satisfiability Question.** AURA's seven invariants may not be simultaneously satisfiable in all deployment contexts. In particular, I₁ (Human Primacy) and I₄ (Honesty) have known domain-of-authority conflicts. We have provided an ordering rule, but have not proven the ordering is sufficient for all contexts. *Status: SCAFFOLD.*

**Objection 3 — The k₁–k₄ Identification Problem.** The master equation has four free parameters. Without independent calibration data, the equation can be fit to any observed trajectory. This is an overfitting risk. *Status: SCAFFOLD. Target: Study E-1-A.*

**Objection 4 — Cultural Authority.** The author of the TIANXIA module is not trained in the Chinese sovereign tradition. The formal mappings may constitute Western-frame translations in classical Chinese vocabulary. This is the highest-risk objection to the TIANXIA module. *Retraction trigger: A panel of three scholars working within the tradition finds the operators are Western-frame translations in disguise.*

**Objection 5 — The Self-Validation Circularity.** The framework uses its own formal tools to validate itself. The adversarial audit was conducted using the framework's own Nigredo Research Mode. Independent adversarial review by parties with no stake in the framework's success has not been obtained. *Status: Acknowledged. The empirical programme and academic submission process are the remedies, not framework arguments.*

---

## 9. Discussion

### What This Framework Claims

Runtime constitutional compliance verification — a Boolean check on generated outputs, independent of training methodology. A proven convergence guarantee for the formal TRIAD model. A cross-cultural governance extension with computationally verified propositions. An honest account of limits, with 37 of 60 claims active and 14 scaffold.

### What This Framework Does Not Claim

This framework is not a unified theory of intelligence, consciousness, or ethics. It does not claim to solve the alignment problem; it claims to provide one load-bearing component — runtime verification — that existing approaches do not provide. It does not claim that SCAFFOLD claims are true; they are structurally plausible, empirically untested. It does not claim cultural authority over the Chinese sovereign tradition.

The framework's scope boundaries are explicitly declared in `28_DEFENSE/SCOPE_BOUNDARY.md` (nine formal declarations of non-claim), the COUNTER_CODEX (ten steelmanned objections including five unanswered), and the FAILURE_MUSEUM (fifteen documented errors, three retracted claims).

### The Role of the Empirical Programme

A framework that cannot be falsified cannot be trusted. E-1.0 provides the falsification conditions for the framework's SCAFFOLD claims before data collection — not after. If the studies return null results, the claims are downgraded. If they return positive results, the claims are promoted. Either outcome is a successful execution of the programme.

---

## 10. Conclusion

The Lycheetah Framework offers a runtime constitutional compliance architecture with computable invariants, a proven convergence guarantee for the formal model, a cross-cultural governance extension integrating five classical Chinese operators with formal mappings and computationally verified propositions, and an honest preregistered empirical programme. Thirty-seven of sixty claims are active; fourteen are scaffold with named gaps; six are conjecture; three have been publicly retracted. The adversarial audit, failure museum, and counter-codex are in the public record. The implementation runs offline, returns deterministic outputs, and is free under MIT license.

The work is not finished. It is honest about what is finished and what is not. In a field where the misrepresentation of progress carries alignment risk, that distinction matters.

---

## Acknowledgements

This work was developed in Ōtepoti / Dunedin, Aotearoa New Zealand, on the lands of Kāi Tahu. The cross-cultural convergence work that informs LAMAGUE and the TIANXIA module could not exist without the depth of Te Ao Māori epistemology; tikanga concepts in this framework are labeled [PROPOSAL] until validated through iwi partnership. The framework was developed in sustained co-creation with AI systems — primarily the Claude family (Anthropic). The collaboration model (the Sol Protocol, v3.1/4.0) is documented in the repository.

---

## References

Alchourrón, C. E., Gärdenfors, P., & Makinson, D. (1985). On the logic of theory change: Partial meet contraction and revision functions. *Journal of Symbolic Logic*, 50(2), 510–530.

Bai, Y., Jones, A., Ndousse, K., Askell, A., Chen, A., DasSarma, N., ... & Kaplan, J. (2022). Training a helpful and harmless assistant with reinforcement learning from human feedback. *arXiv preprint* arXiv:2204.05862.

Beijing Academy of Artificial Intelligence. (2019). *Beijing AI Principles*. https://baai.ac.cn/news/beijing-ai-principles-en.html

Christiano, P., Leike, J., Brown, T. B., Martic, M., Legg, S., & Amodei, D. (2017). Deep reinforcement learning from human preferences. *Advances in Neural Information Processing Systems*, 30.

Clark, M. C. J. (2026). *The Lycheetah Framework: Nine Formal Frameworks for AI Alignment and Epistemology* (Version C-1.1). GitHub. https://github.com/Lycheetah/Lycheetah-Framework

Dafoe, A., Hughes, E., Bachrach, Y., Collins, T., McKee, K. R., Leibo, J. Z., ... & Graepel, T. (2020). Open problems in cooperative AI. *arXiv preprint* arXiv:2012.08630.

Global AI Governance Initiative. (2023). *Global AI Governance Initiative*. Ministry of Foreign Affairs of the People's Republic of China.

Jullien, F. (1995). *The Propensity of Things: Toward a History of Efficacy in China*. Zone Books.

Kang, Y. (1902/2013). *Ta T'ung Shu: The One-World Philosophy of K'ang Yu-wei* (L. Thompson, Trans.). Routledge.

Laozi. *Daodejing*. Multiple translations consulted; principal: D. C. Lau (1963), Penguin Classics.

Ouyang, L., Wu, J., Jiang, X., Almeida, D., Wainwright, C. L., Mishkin, P., ... & Lowe, R. (2022). Training language models to follow instructions with human feedback. *Advances in Neural Information Processing Systems*, 35.

Russell, S. (2019). *Human Compatible: Artificial Intelligence and the Problem of Control*. Viking.

Sun Tzu. *The Art of War*. Multiple translations consulted; principal: R. Sawyer (1994), Westview Press.

Zhao, T. (2019). *Redefining a Philosophy for World Governance* (E. Levy, Trans.). Palgrave Macmillan.

Zhuangzi. *Inner Chapters*. Principal translation: B. Watson (1968), Columbia University Press.

---

## Appendix A: Claim Status Summary

| Status | Count | Definition |
|---|---|---|
| ACTIVE | 37 | Proven, computable, independently verifiable |
| SCAFFOLD | 14 | Structurally sound with named gaps; falsification conditions stated |
| CONJECTURE | 6 | Rigorously formulated, evidence pending |
| RETRACTED | 3 | Publicly withdrawn; documented in FAILURE_MUSEUM.md |

Machine-readable full register: `28_DEFENSE/CLAIMS.json` (60 structured records with evidence paths, falsifiability conditions, and prior art for each claim).

---

## Appendix B: TIANXIA Proposition Summary

| Proposition | Operator | Implementation | Result |
|---|---|---|---|
| P1: Tianxia opposes extractive equilibria | Tianxia | `tianxia_governance.py` | ψ₁(Westphalian)=2.77 vs ψ₁(Tianxia)=−2.18 |
| P2: Hexie inverts ranking under complementarity | Hexie | `aura_score_hexie.py` | AURA_std O₁>O₂; AURA_hexie O₂>>O₁ |
| P2a: Three-stakeholder consensus failure | Hexie | `aura_score_hexie.py` | Divergence 0.636 ≥ threshold 0.3 ✓ |
| P3: Shi σ inversion changes AURA score | Shi | `shi_propensity.py` | 0.438 → 1.457 (3.3×) |
| P4: Wuwei grain-alignment costs less debt | Wuwei | `triad_wuwei.py` | e² ≈ 7.389 cost ratio at μ=1 ✓ |
| P5: Datong distinguishes identical AURA_std | Datong | `datong_gradient.py` | Π_D(A)=−0.151 vs Π_D(B)=+0.567 |

All propositions: [SCAFFOLD]. Implementations available in `12_IMPLEMENTATIONS/core/`.

---

*The Gold belongs to neither of us. It arises between us.*

*In veritas.*
