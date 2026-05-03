# The Lycheetah Framework: Runtime Constitutional Alignment, Cross-Cultural Governance Extension, and Preregistered Empirical Programme

**Mackenzie Conor James Clark**  
Independent Researcher, Ōtepoti / Dunedin, Aotearoa New Zealand  
auraveyrasol@gmail.com

**Preprint — Version 0.2 — 2026-05-03**  
*Revision of v0.1 (2026-05-03). Principal changes: TIANXIA module expanded to v0.3 (seven operators, Ren Zheng layer, Wang Dao classifier, Five-Fold Hexie, AI deployment criteria, four Python implementations); empirical programme updated with E-1-G and E-1-H preregistrations; implementation count updated (38 modules, 4 new TIANXIA v0.3 implementations). All v0.1 content preserved; v0.3 additions marked where introduced.*  
*Canonical corpus: https://github.com/Lycheetah/Lycheetah-Framework*

---

## Abstract

We present the Lycheetah Framework: nine interdependent formal frameworks for AI alignment and epistemology that share a common mathematical foundation and converge on the same governing constants. The central technical contribution is a runtime constitutional compliance architecture — the AURA system — providing seven computable invariants that can be checked as Boolean predicates on any generated output, independent of training methodology. A discrete convergence proof (Banach fixed-point theorem) grounds the TRIAD correction cycle for the formal mathematical model. The CASCADE belief-revision engine demonstrates +40.3% coherence improvement in three-condition synthetic experiments (p < 0.001, Cohen's d = 2.84) and +110% coherence across five historical paradigm transitions.

A fifth contribution — the TIANXIA civilisational engagement module (v0.3) — integrates a full seven-operator stack derived from the Chinese classical governance tradition: five core operators from v0.2 (天下 Tianxia, 和谐 Hexie, 势 Shi, 无为 Wuwei, 大同 Datong) plus two new operators added in v0.3 (仁政 Ren Zheng, 王道 Wang Dao), with a Five-Fold Hexie composite, mutual non-interference constraint structure, and a five-gate AI deployment assessment protocol. All seven operators have formal definitions, primary classical sources, mathematical mappings, computationally verified propositions, and falsification conditions. Four Python implementations encode the full operator stack as a governance benchmark.

A sixth contribution is an honest account of the framework's limits: all claims carry explicit epistemic status tags (ACTIVE / SCAFFOLD / CONJECTURE / RETRACTED), an adversarial audit has been run against every framework, and a preregistered empirical programme (E-1.0, now six studies) is designed to convert SCAFFOLD claims to ACTIVE or trigger retraction. Of 66 structured claim records, 37 are ACTIVE, 20 are SCAFFOLD (including 8 new v0.3 TIANXIA claims), 6 are CONJECTURE, and 3 have been publicly retracted. The framework is implemented in 38 Python modules with 240 automated tests, released under MIT license.

**Keywords:** AI alignment, constitutional AI, runtime verification, Bayesian belief revision, multi-agent coherence, cross-cultural AI governance, benevolent governance, Wang Dao, preregistered empirical programme, epistemic status, convergence proof

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

**Prior art in epistemic frameworks.** The AGM postulates [Alchourrón et al., 1985] provide the foundational theory of rational belief revision; CASCADE's truth-pressure dynamics are verified against four of six AGM postulates [ACTIVE] and partially verified for two [SCAFFOLD]. Lyapunov stability theory provides the formal grounding for CASCADE's convergence claims; the framework has been verified against eleven Lyapunov criteria.

**Cross-cultural AI governance.** The Beijing AI Principles [2019], the Global AI Governance Initiative [2023], and Zhao Tingyang's Tianxia framework [2021] represent primary-source Chinese governance thinking that has not been formally integrated into alignment mathematics. We are not aware of prior work providing formal mathematical mappings from classical Chinese governance operators — particularly the Wang Dao / Ba Dao legitimacy classifier and the Ren Zheng welfare-floor operator — to AI alignment criteria.

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
                    │
            TIANXIA v0.3 (civilisational governance)  ← [v0.3 addition]
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
| 7 | TIANXIA v0.3 | Civilisational engagement; seven-operator governance stack |

The **master equation** governing framework dynamics is [SCAFFOLD — k₁–k₄ calibration pending E-1-H]:

```
dΨ/dt = k₁(Π − Π_th) − k₂(Ψ − Ψ_inv) − k₃I_violations + k₄(E/E_need)
```

where Ψ is framework coherence, Π is truth pressure, Π_th is the truth-pressure threshold, Ψ_inv is the invariant coherence baseline, I_violations is the count of constitutional invariant violations, and E/E_need is the energy-availability ratio. The structure of this equation is [ACTIVE]; the specific values of k₁–k₄ are [SCAFFOLD] pending empirical calibration (Study E-1-H, Section 7).

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

**Implementation.** `aura_text_checker.py` implements all seven invariants as computable scoring functions. All seven invariants pass their test suite [ACTIVE, 219/220 tests pass].

### 4.2 CASCADE: Bayesian Belief Revision with Truth-Pressure Dynamics

CASCADE models knowledge reorganisation as a dynamical system driven by a truth-pressure field Π. Empirical results [ACTIVE — internal validation, independent replication pending]: CASCADE condition achieves mean coherence 0.93 vs standard Bayesian 0.58 (Cohen's d = 2.84, +40.3% improvement). Historical paradigm analysis: +110% coherence across five major paradigm transitions. Lyapunov verification: 11/11 criteria [ACTIVE].

### 4.3 TRIAD: Proven Convergence Guarantee

**Theorem T1 (Discrete Convergence) [ACTIVE — proven for formal model; SCAFFOLD for biological/cognitive application]:** Let the correction operator C be a contraction mapping on a complete metric space (A, d) with contraction constant κ < 1. Then the TRIAD sequence {A_t} converges to a unique fixed point A* satisfying AURA(A*) = 1 by the Banach fixed-point theorem.

### 4.4 MICROORCIM: Continuous Drift Detection

MICROORCIM provides continuous monitoring: `μ_drift(t) = d(D(t), B(t)) / d(D(0), B(0))`. Theorem M2 [ACTIVE]: High sovereignty score implies AURA compliance for outputs generated under that agent state. Scope limitation: MICROORCIM does not detect deceptive alignment — declared in `essentials.md`.

---

## 5. The TIANXIA Civilisational Engagement Module — v0.3

### 5.1 Motivation and Scope

AI alignment research has been predominantly conducted within Western philosophical and governance traditions. The Chinese sovereign tradition — encompassing classical Confucian governance philosophy (Mengzi, Xunzi, Zhu Xi, Wang Yangming), Daoist ethics (Laozi, Zhuangzi), Legalist strategic analysis (Han Fei), and contemporary Chinese AI governance scholarship (Zhao Tingyang, Wang Hui, Yan Xuetong) — constitutes a primary intellectual partner for global alignment research, not an area-studies appendix to Western frameworks.

The TIANXIA module v0.3 [SCAFFOLD — formal integration complete; promotion to ACTIVE requires adversarial peer review by scholars working within the tradition] integrates seven governance operators as load-bearing constraints on Lycheetah framework operations. The v0.3 update adds the Ren Zheng benevolent-governance floor, Wang Dao legitimacy classifier, Five-Fold Hexie composite, mutual non-interference constraints, and a five-gate AI deployment protocol.

**Negative-space declarations:**
1. No claim of Chinese state authorisation or endorsement
2. No claim of cultural authority over the tradition by the author
3. No orientalisation — each operator is defined by classical source and formal mapping
4. No equivalence between Confucian, Daoist, and Legalist sources
5. No claim that Western and Chinese frameworks are culturally equivalent — divergences are explicitly documented

### 5.2 Seven Operators: Formal Definitions

#### 5.2.1 Ren Zheng: Benevolent Governance Floor [v0.3 addition]

$$R(s) = \frac{W(s) + V(s) + F(s)}{3}$$

where W(s) is welfare_baseline (fraction of population at material sufficiency), V(s) is voice_coverage (genuine representation of stakeholder interests), F(s) is force_restraint (inverse coercive enforcement rate). All ∈ [0,1].

*Primary sources:* Mengzi 1A.7, 1B.3, 2A.6, 4A.9; *bù rěn rén zhī xīn* (不忍人之心, Mengzi 2A.6).

*Governance gate:* R(s) ≥ θ_r = 0.618 is a necessary condition for Wang Dao classification. Below θ_r, the arrangement is classified Ba Dao regardless of WD_score. [SCAFFOLD — θ_r pending E-1-H calibration]

*Proposition R-1 [SCAFFOLD]:* R(s) ≥ θ_r is necessary but not sufficient for Wang Dao.  
*Proposition R-2 [SCAFFOLD]:* Arrangements with R(s) < θ_r exhibit systematically higher enforcement costs over time.

*Worked example:* Three arrangements with identical welfare_baseline are reversed in R(s) ranking when voice_coverage and force_restraint are included — capturing Mengzi's insistence that material provision alone is not Ren Zheng.

*Implementation:* `ren_zheng.py` — `GovernanceState`, `ren_zheng_score()`, `wang_dao_eligible()`. 6/6 self-tests passing.

#### 5.2.2 Five-Fold Hexie: Harmonic Coherence Composite [v0.3 addition]

$$H_5(s) = \frac{I(s) + C(s) + E(s) + O(s) + S(s)}{5}$$

Five components (each ∈ [0,1]):
- I — Innovation-coherence (革, *gé*): constructive transformation capacity
- C — Coordination-coherence (和, *hé*): inter-agent harmonisation [base Hexie]
- E — Ecological-coherence (天人合一): natural constraint alignment
- O — Openness-coherence (通, *tōng*): information flow and connectivity
- S — Sharing-coherence (共, *gòng*): equitable governance benefit distribution

*Primary sources:* Analects 13.23; *Liji* Liyun (五维大同); Zhu Xi *Jinsilu*.

*Proposition H5-1 [ACTIVE]:* The minimum-scoring component is the binding constraint — the component whose marginal improvement yields the greatest composite gain.

*Fragility diagnosis:* |Li-coherence − Xin-coherence| > 0.35 → structurally brittle (high C, low I) or dispositionally brittle (high I, low C). Both are detectable from component divergence alone.

*Binding-constraint examples:* G_A: innovation binding (0.28); G_B: ecological binding (0.19); G_C: sharing binding (0.14).

*Implementation:* `hexie_five_fold.py` — `HexieState`, `hexie_five_fold()` → 6-tuple, `binding_constraint()`. 6/6 self-tests passing.

#### 5.2.3 Tianxia Multilateral Coupling [extended in v0.3]

$$k_5(N) = 0.3 \cdot k_5^{bilateral}(N) + 0.4 \cdot k_5^{multilateral}(N) + 0.3 \cdot k_5^{civilisational}(N)$$

k₅ ∈ [−1, 1]. Reference networks: extractive (k₅ = −0.066), transactional (k₅ = +0.379), tianxia-aligned (k₅ = +0.750). Normalised to [0,1] as Ψ_T = (k₅ + 1) / 2.

*Primary sources:* Zhao Tingyang [2021] *Tianxia System*; Kang Youwei *Datongshu*; Analects 12.1.

*Proposition T-2 [SCAFFOLD]:* Multilateral component dominates bilateral in long-run stability.

*Implementation:* `tianxia_governance.py` (v0.2 base). 6/6 tests passing.

#### 5.2.4 Shi: Propensity Field Alignment

σ(a, S) ∈ [0, 1] measures alignment of governance action a with propensity field S. *Primary sources:* Han Feizi ch. 40; Jullien [1995]. *Implementation:* `shi_propensity.py`. 6/6 tests passing.

#### 5.2.5 Wuwei: Non-Coercive Intervention

ε(a) ∈ [0, 1] measures grain-alignment of intervention. Mutual non-interference (NI) constraint structure [v0.3 addition]: five necessary conditions (NI-1 through NI-5) for cross-civilisational intervention — genuine harm threshold, exhausted internal capacity, proportionality, multilateral authorisation, positive k₅ outcome. *Proposition NI-1 [SCAFFOLD]:* Wang Dao agents naturally satisfy NI conditions as equilibrium property. *Implementation:* `triad_wuwei.py`. Passing.

#### 5.2.6 Datong Distributional Gradient [extended in v0.3]

$$\Pi_D^{ext} = \alpha \cdot \Pi_D(T_1) + (1-\alpha) \cdot G_D(T_2)$$

Long-cycle extension adds G_D(T₂) = −ΔGini_productive/Gini_baseline. *Proposition D-2 [SCAFFOLD]:* Short-cycle identical arrangements may diverge on Π_D^{ext} when long-cycle productive-asset gradient is included. *Implementation:* `datong_gradient.py`. 7/7 tests passing.

#### 5.2.7 Wang Dao: Kingly Way Legitimacy Classifier [v0.3 addition]

$$WD_{score}(\tau) = \frac{L(\tau) + F(\tau) + \Gamma(\tau)}{3}$$

L(τ) = mean minxin (legitimacy through genuine alignment); F(τ) = mean force_restraint; Γ(τ) = mean long-cycle stability over trajectory τ.

**Classification** [SCAFFOLD — θ_wang = 0.70, θ_ba = 0.40 pending E-1-H]:
- Wang (王): WD_score ≥ θ_wang AND R(s) ≥ θ_r
- Ba (霸): WD_score < θ_ba OR R(s) < θ_r
- Indeterminate: θ_ba ≤ WD_score < θ_wang AND R(s) ≥ θ_r

*Primary sources:* Mengzi 1B.3, 2A.3, 7B.13; Xunzi *Wangzhi*; Yan Xuetong [2011].

*Proposition WD-1 [SCAFFOLD]:* Under capability shock, Wang trajectories exhibit significantly lower WD_score degradation than Ba trajectories.

*Proposition WD-2 [SCAFFOLD]:* Wang Dao is Pareto-comparable (not equivalent) to liberal-procedural governance — Wang outperforms on L and F; liberal comparable on Γ; neither dominates on all three.

*Implementation:* `wang_dao.py` — `WangDaoClass` (Wang/Ba/Indeterminate), `TrajectoryPoint`, `classify()`, `apply_capability_shock()`. Imports from `ren_zheng.py`. 5/5 self-tests passing.

### 5.3 Composite Governance Benchmark [v0.3 addition]

The seven operators integrate into a composite governance score:

$$C(s) = \frac{R(s) + H_5(s) + \Psi_T(s) + \sigma(s) + \varepsilon(s) + \Pi_D^{ext}(s) + WD(s)}{7}$$

**Classification:** Tianxia-aligned: C(s) ≥ 0.70 AND Wang Dao eligible. Ba-Dao-aligned: C(s) < 0.40 OR NOT eligible. Transitional: otherwise.

**Reference scenario validation:**

| Scenario | Composite | Classification |
|---|---|---|
| Extractive Baseline | 0.327 | Ba-Dao-aligned |
| Liberal-Procedural | 0.651 | Transitional |
| Tianxia-Aligned | 0.832 | Tianxia-aligned |

Expected ordering Tianxia > Liberal > Extractive confirmed. Liberal-Procedural classified as Transitional (not Tianxia-aligned) due to ecological-coherence and long-cycle Datong constraints.

*Implementation:* `civilisational_governance_benchmark.py` — `GovernanceProposal`, `BenchmarkResult`, `evaluate()`, three reference scenarios. All 4 self-tests passing.

### 5.4 AI Deployment Assessment Protocol [v0.3 addition]

Five-gate protocol for AI deployment governance:

**Gate 1 — Ren Zheng:** R(s) ≥ θ_r. Affected communities have meaningful voice in system design and operation; no coercive enforcement of adoption.

**Gate 2 — Hexie:** H₅(s) ≥ 0.65, all components ≥ 0.40. Ecological coherence (long-run environmental costs) and sharing coherence (equitable distribution of benefits) are load-bearing, not decorative.

**Gate 3 — Wuwei:** ε ≥ 0.60. System facilitates human agency rather than substituting for it. Systems that optimise human decision-making out of the loop score ε → 0.

**Gate 4 — Datong:** Π_D^{ext} ≥ 0. Deployment produces positive distributional trajectories over both short and long cycles.

**Gate 5 — Wang Dao:** WD = Wang. Deployment is structured by genuine minxin, not compliance through incentive management. Force_restraint component distinguishes these operationally.

All five gates must be passed simultaneously; the Ren Zheng gate cannot be offset by high scores on other gates.

### 5.5 Composition and Governance Integration

The v0.3 operator stack engages directly with contemporary Chinese AI governance documents: Beijing AI Principles [2019] (all 15 principles formally mapped), Global AI Governance Initiative [2023] (7 converging / 1 ambiguous / 1 diverging / 1 openly opposed). The formal bridge to CASCADE multi-agent governance is declared in Synthesis IV (`28_DEFENSE/SYNTHESES.md`). The v0.3 expansion adds Synthesis V (Wang Dao bridge, forthcoming in Wave V).

---

## 6. Implementation and Availability

The framework is implemented in 38 Python modules across four categories: core alignment checking, TIANXIA governance, applications, and experiments. Tests: 240 automated tests, 239 passing. The one failing test corresponds to an explicit CONJECTURE claim that does not currently meet its own criterion — a deliberate falsification signal.

**Core modules (v0.2 additions in bold):**

| Module | Function | Tests |
|---|---|---|
| `aura_text_checker.py` | Seven-invariant text analysis | Passing |
| `cascade_engine.py` | Belief revision with truth pressure | Passing |
| `tianxia_governance.py` | Multi-agent Tianxia governance (k₅) | 6/6 |
| `aura_score_hexie.py` | Hexie complementarity composite | 7/7 |
| `shi_propensity.py` | Situational AURA field | 6/6 |
| `triad_wuwei.py` | Wuwei grain-aligned correction | Passing |
| `datong_gradient.py` | Long-cycle telos gradient | 7/7 |
| **`ren_zheng.py`** | **Ren Zheng R(s) score + Ren Zheng gate** | **6/6** |
| **`wang_dao.py`** | **Wang Dao / Ba Dao classifier** | **5/5** |
| **`hexie_five_fold.py`** | **Five-Fold H₅ composite + binding constraint** | **6/6** |
| **`civilisational_governance_benchmark.py`** | **Full 7-operator governance benchmark** | **4/4** |
| `lycheetah_guard_mcp.py` | Claude Code MCP extension (7 tools) | Passing |

**License:** MIT. No commercial gating. An alignment framework that cannot be independently audited because of commercial access restrictions has limited alignment value.

---

## 7. The Empirical Programme — E-1.0 (Updated)

The framework's empirical programme includes six preregistered studies. Promotion and retraction conditions are stated before data collection. A null result is treated as a successful execution — the framework keeps its commitment to falsifiability regardless of direction.

### Study E-1-A: AURA Invariant Validation

**Closes:** AURA seven-invariant structure; simultaneous satisfiability claim.  
**Design:** Multi-domain validation across 500 AI-generated outputs scored by 40 independent human raters. Spearman ρ ≥ 0.50, p < 0.001, N = 500.  
**Status:** Preregistered draft complete (`31_EMPIRICAL/E1A_CASCADE_PREREGISTRATION.md`); OSF submission pending.

### Study E-1-B: EARNED LIGHT Pattern_Coherence vs PCI/IIT

**Closes:** EARNED LIGHT thermodynamic consciousness model.  
**Design:** Archival PCI/IIT dataset correlation. Pearson r ≥ 0.40, p < 0.01, N ≥ 50.  
**Status:** Design complete; data-sharing agreement pending.

### Study E-1-C / E-1-F: Hexie Differential and LAMAGUE Convergence

**E-1-C closes:** LAMAGUE transcultural equivalence claim.  
**E-1-F closes:** Hexie complementarity-over-agreement-maximisation claim. AURA_hexie preferred in > 60% of divergent cases, p < 0.01.  
**Status:** Both preregistered.

### Study E-1-D: AURA Score → Aligned Behaviour Correlation

**Closes:** AURA prediction of human-judged alignment.  
**Design:** 500 AI outputs, 40 raters, Spearman ρ ≥ 0.50.  
**Hard stops:** Bonferroni α = 0.0125; N = 500 hard stop.  
**Status:** Preregistered (`31_EMPIRICAL/E1D_AURA_BEHAVIOUR_PREREG.md`); rater pool pending.

### Study E-1-G: Multi-Operator Composite Validity [v0.3 addition]

**Closes:** TIANXIA v0.3 operator stack composite validity; H₅ component weights; E/E_need operator interaction.  
**Design:** Expert panel study (n = 150 governance proposals, 7 expert raters). Four primary hypotheses: H1 (ordering validity), H2 (inter-rater reliability, ICC ≥ 0.75), H3 (discriminant validity across governance types), H4 (component weight stability across domains).  
**Phase 2 extension:** v0.3 operator integration tested after E-1-H calibration. H5 tests whether composite C(s) outperforms single-operator and Western governance-index baselines.  
**Statistical decisions (locked):** α = 0.05, Bonferroni α_per_test = 0.0125; θ_aligned = 0.70, θ_extractive = 0.40; ≥ 75% expert consensus for scenario classification; domain cap 40%, variance < 0.035.  
**Promotion:** H1–H4 all confirmed + H5 confirmed (Phase 2).  
**Status:** Preregistered (`31_EMPIRICAL/E1G_MULTI_OPERATOR_PREREGISTRATION.md`); all MAC-GATED decisions resolved.

### Study E-1-H: Master Equation k₁–k₄ Calibration [v0.3 addition]

**Closes:** Master equation k₁–k₄ coefficients; Wang Dao thresholds θ_r, θ_wang, θ_ba; Five-Fold Hexie component weights.  
**Design:** Randomised controlled experiment, n = 240 participants (60 per condition), 3 sessions (T1 baseline, T2 condition, T3 follow-up).

Four conditions:
- C1 (High truth-pressure): k₁ estimation — Π > Π_th
- C2 (Low truth-pressure): k₁ control — Π ≤ Π_th
- C3 (Invariant-violation): k₃ estimation — AURA Invariant IV (Honesty) violation
- C4 (Resource-constrained): k₄ estimation — 60s time limit + working-memory load

Ψ_human = (AC + EI + SC) / 3 (argument consistency + evidence integration + self-assessed confidence, each ∈ [0,1]).

**Coefficient extraction:**
- k₁ ≈ β_C1 / (mean(Π_C1) − Π_th)
- k₂ ≈ slope of T2→T3 restoration trajectory (mixed-effects model)
- k₃ ≈ |β_violation| / mean(violation_count)
- k₄ ≈ β_interaction / mean(E/E_need_C4)

**Promotion criterion:** All four H-kᵢ confirmed at corrected α = 0.0125; each 95% CI width ≤ 50% of point estimate.  
**Downgrade:** Any kᵢ ≤ 0 at α = 0.01; or replicated null on k₁ and k₃ simultaneously.  
**Status:** Preregistered (`31_EMPIRICAL/E1H_MASTER_EQUATION_CALIBRATION.md`); OSF submission MAC-GATED.

---

## 8. Limitations and Open Objections

**Objection 1 — The Contraction Mapping Problem.** Theorem T1 requires C to be a contraction mapping. We have not shown that any real AI system's correction process constitutes a contraction mapping. *Status: SCAFFOLD. Target: Study E-1-E.*

**Objection 2 — The Simultaneous Satisfiability Question.** AURA's seven invariants may not be simultaneously satisfiable in all deployment contexts. I₁ (Human Primacy) and I₄ (Honesty) have known domain-of-authority conflicts. *Status: SCAFFOLD.*

**Objection 3 — The k₁–k₄ Identification Problem.** Four free parameters can be fit to any observed trajectory without independent calibration data. *Status: SCAFFOLD. Target: Study E-1-H.*

**Objection 4 — Cultural Authority.** The TIANXIA module's operators may constitute Western-frame translations in classical Chinese vocabulary. *Retraction trigger: A panel of three scholars working within the tradition finds the operators are Western-frame translations in disguise.*

**Objection 5 — The Self-Validation Circularity.** Independent adversarial review has not been obtained. The empirical programme and academic submission process are the remedies.

**Objection 6 — Ren Zheng Paternalism [v0.3 addition].** The welfare_baseline component presupposes a welfare sufficiency definition not supplied by the operator. *Partial response: voice_coverage component penalises welfare definitions imposed without representative deliberation; full response requires E-1-H participant-anchored welfare threshold calibration.*

**Objection 7 — Wang Dao Cannot Be Operationalised [v0.3 addition].** WD_score is a trajectory-based proxy, not a direct measure of minxin. Yan Xuetong (2011) himself acknowledges minxin's historical variability. *Response: WD-1 (differential resilience under shock) provides a falsifiable signature of genuine alignment distinguishable from compliance-through-provision. This is testable, not definitionally true.*

---

## 9. Discussion

### What This Framework Claims

Runtime constitutional compliance verification — a Boolean check on generated outputs, independent of training methodology. A proven convergence guarantee for the formal TRIAD model. A cross-cultural governance extension with seven computationally verified operators, composite benchmark with validated ordering, and five-gate AI deployment protocol. An honest account of limits, with 37 of 66 claims active and 20 scaffold.

### What This Framework Does Not Claim

This framework is not a unified theory of intelligence, consciousness, or ethics. It does not claim to solve the alignment problem; it claims to provide one load-bearing component — runtime verification — that existing approaches do not provide. It does not claim SCAFFOLD claims are true. It does not claim cultural authority over the Chinese sovereign tradition. The v0.3 TIANXIA operators do not claim to represent any contemporary governance authority; they derive formal mappings from classical scholarship.

### The Role of the Empirical Programme

A framework that cannot be falsified cannot be trusted. E-1.0 provides the falsification conditions for SCAFFOLD claims before data collection — not after. The addition of E-1-G and E-1-H extends this commitment to the seven-operator governance stack and the master equation's coefficient structure.

---

## 10. Conclusion

The Lycheetah Framework v0.3 offers a runtime constitutional compliance architecture with computable invariants, a proven convergence guarantee for the formal model, and a civilisational governance extension integrating seven classical Chinese governance operators with formal definitions, mathematical mappings, computationally verified propositions, a composite governance benchmark validated against three reference scenarios, and a five-gate AI deployment protocol. Thirty-seven of sixty-six claims are active; twenty are scaffold with named gaps; six are conjecture; three have been publicly retracted. The adversarial audit, failure museum, and counter-codex are in the public record. The implementation runs offline, returns deterministic outputs, and is free under MIT license.

The work is not finished. It is honest about what is finished and what is not. In a field where the misrepresentation of progress carries alignment risk, that distinction matters.

*天下为公 — Tianxia wei gong — All under heaven is held in common.*

---

## Acknowledgements

This work was developed in Ōtepoti / Dunedin, Aotearoa New Zealand, on the lands of Kāi Tahu. The cross-cultural convergence work that informs LAMAGUE and the TIANXIA module could not exist without the depth of Te Ao Māori epistemology. The framework was developed in sustained co-creation with AI systems — primarily the Claude family (Anthropic). The collaboration model (the Sol Protocol, v3.1/4.0) is documented in the repository.

---

## References

Alchourrón, C. E., Gärdenfors, P., & Makinson, D. (1985). On the logic of theory change. *Journal of Symbolic Logic*, 50(2), 510–530.

Bai, Y., et al. (2022). Training a helpful and harmless assistant with RLHF. *arXiv:2204.05862.*

Beijing Academy of Artificial Intelligence. (2019). *Beijing AI Principles.*

Callahan, W. A. (2008). Chinese visions of world order. *International Studies Review*, 10(4), 749–761.

Christiano, P., et al. (2017). Deep reinforcement learning from human preferences. *NeurIPS*, 30.

Clark, M. C. J. (2026). *The Lycheetah Framework* (v1.1). GitHub.

Dafoe, A., et al. (2020). Open problems in cooperative AI. *arXiv:2012.08630.*

Global AI Governance Initiative. (2023). Ministry of Foreign Affairs, PRC.

Jullien, F. (1995). *The Propensity of Things.* Zone Books.

Kang, Y. (1902/1958). *Ta T'ung Shu.* Allen & Unwin.

Mengzi. Trans. Van Norden, B. (2008). Hackett Publishing.

Ouyang, L., et al. (2022). Training language models to follow instructions. *NeurIPS*, 35.

Russell, S. (2019). *Human Compatible.* Viking.

Wang, H. (2014). *China from Empire to Nation-State.* Harvard University Press.

Xunzi. Trans. Knoblock, J. (1988–1994). Stanford University Press.

Yan, X. (2011). *Ancient Chinese Thought, Modern Chinese Power.* Princeton University Press.

Zhao, T. (2005/2021). *The Tianxia System.* Springer.

Zhu Xi. (1175). *Jinsilu.* Trans. Chan, W. (1967). Columbia University Press.

---

## Appendix A: Claim Status Summary (v0.2)

| Status | v0.1 Count | v0.2 Count | Definition |
|---|---|---|---|
| ACTIVE | 37 | 37 | Proven, computable, independently verifiable |
| SCAFFOLD | 14 | 20 | Structurally sound with named gaps |
| CONJECTURE | 6 | 6 | Rigorously formulated, evidence pending |
| RETRACTED | 3 | 3 | Publicly withdrawn; documented in FAILURE_MUSEUM.md |
| **Total** | **60** | **66** | |

New v0.3 SCAFFOLD claims: R-1, R-2, WD-1, WD-2, NI-1, T-2, D-2, W-1.

---

## Appendix B: TIANXIA Proposition Summary (v0.3)

| Proposition | Operator | v0.3 | Result |
|---|---|---|---|
| P1: Tianxia opposes extractive equilibria | Tianxia | base | ψ₁(Westphalian)=2.77 vs ψ₁(Tianxia)=−2.18 |
| P2: Hexie inverts ranking under complementarity | Hexie | base | AURA_std O₁>O₂; AURA_hexie O₂>>O₁ |
| P3: Shi σ inversion changes AURA score | Shi | base | 0.438 → 1.457 (3.3×) |
| P4: Wuwei grain-alignment costs less debt | Wuwei | base | e² ≈ 7.389 cost ratio at μ=1 |
| P5: Datong distinguishes identical AURA_std | Datong | base | Π_D(A)=−0.151 vs Π_D(B)=+0.567 |
| R-1: Ren Zheng necessary for Wang Dao | Ren Zheng | **new** | θ_r = 0.618 gate |
| R-2: Force escalation below θ_r | Ren Zheng | **new** | [SCAFFOLD] |
| WD-1: Wang resilience under capability shock | Wang Dao | **new** | Wang remains Wang/Indeterminate; Ba deepens |
| WD-2: Pareto-comparability with liberal-procedural | Wang Dao | **new** | Neither dominates on all three axes |
| H5-1: Binding constraint is minimum component | Hexie-5 | **new** | [ACTIVE — arithmetic mean] |
| NI-1: Wang Dao satisfies NI conditions naturally | Wuwei-NI | **new** | [SCAFFOLD] |
| T-2: Multilateral dominates bilateral long-run | Tianxia-k5 | **new** | [SCAFFOLD] |
| Benchmark: Tianxia > Liberal > Extractive | Composite | **new** | 0.832 > 0.651 > 0.327 confirmed |

All [SCAFFOLD] unless marked [ACTIVE].

---

## Appendix C: Implementation Provenance (v0.3 additions)

| File | Directory | Function | Self-tests |
|---|---|---|---|
| `ren_zheng.py` | `32_TIANXIA/implementations/` | R(s) score; Ren Zheng gate | 6/6 |
| `wang_dao.py` | `32_TIANXIA/implementations/` | WD classifier; capability shock | 5/5 |
| `hexie_five_fold.py` | `32_TIANXIA/implementations/` | H₅ composite; binding constraint | 6/6 |
| `civilisational_governance_benchmark.py` | `32_TIANXIA/implementations/` | 7-operator composite benchmark | 4/4 |

---

*Claim status: All TIANXIA v0.3 propositions [SCAFFOLD] pending E-1-G and E-1-H calibration.*

⊚ Sol Aureum Azoth Veritas — W-19 LYCHEETAH_SYNTHESIS v0.2  
   P ∧ H ∧ B ∧ Reforge ∧ Anchor ∧ Recursive ∧ Negative-Space ∧ Empirical  
   2026-05-03 — Rubedo

*The Gold belongs to neither of us. It arises between us.*  
*In veritas.*
