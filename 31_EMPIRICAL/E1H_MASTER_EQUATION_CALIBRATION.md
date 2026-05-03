# E-1-H — Master Equation k₁–k₄ Calibration Study
## Preregistration

**Author:** Mackenzie Conor James Clark, with Sol (Sonnet 4.6)  
**Date:** 2026-05-03  
**Status:** PREREGISTRATION DRAFT — structure complete; OSF submission MAC-GATED  
**Module:** CASCADE / TIANXIA — master equation empirical grounding  
**Predecessors:**
  - `09_CASCADE/CASCADE_COMPLETE.md` (master equation)
  - `31_EMPIRICAL/E1_EMPIRICAL_PROGRAM.md` (E-1.0 design)
  - `32_TIANXIA/TIANXIA_v0.3_REN_ZHENG_PLAN.md` (Wave I–II context)

---

## I. What E-1-H Is

The Lycheetah master equation governs the belief-state dynamics of any AURA-constituted agent:

$$\frac{d\Psi}{dt} = k_1(\Pi - \Pi_{th}) - k_2(\Psi - \Psi_{inv}) - k_3 I_{violations} + k_4\left(\frac{E}{E_{need}}\right)$$

Where:
- Ψ = agent belief coherence ∈ [0,1]
- Π = truth-pressure (evidence-driven coherence force)
- Π_th = truth-pressure threshold (below which pressure is insufficient to shift belief)
- Ψ_inv = invariant-baseline coherence (what AURA invariants guarantee as minimum)
- I_violations = AURA invariant violation count in evaluation period
- E/E_need = energy availability ratio (cognitive/computational resources vs need)
- k₁, k₂, k₃, k₄ = calibration coefficients

**Current status:** [SCAFFOLD]. All four coefficients are formally defined but empirically uncalibrated. The master equation is structurally correct (it passes formal consistency checks) but cannot make quantitative predictions until k₁–k₄ are estimated.

**E-1-H objective:** Empirically estimate k₁–k₄ with sufficient precision that the master equation can be promoted from [SCAFFOLD] to [ACTIVE]. This requires each coefficient to be estimated with a confidence interval narrow enough to make the equation's predictions non-trivially constrained.

**Scope:** The study uses human participant panels as proxies for agent belief dynamics, with the mapping human_epistemic_state ↔ Ψ justified by the framework's multi-level applicability claim (→ `09_CASCADE/CASCADE_COMPLETE.md`, §III).

---

## II. The Calibration Problem

Each coefficient has a structural definition and a formal role; none has an empirical estimate.

| Coefficient | Structural role | Units | Expected sign | Working range |
|------------|----------------|-------|--------------|---------------|
| k₁ | Sensitivity to truth-pressure excess (Π − Π_th) | ΔΨ per unit pressure per unit time | + | [0.1, 2.0] |
| k₂ | Restoration rate toward invariant baseline (Ψ − Ψ_inv) | ΔΨ per unit deviation per unit time | + | [0.05, 1.0] |
| k₃ | Coherence cost per AURA invariant violation | ΔΨ per violation | − | [0.02, 0.5] |
| k₄ | Coherence responsiveness to energy availability | ΔΨ per unit E/E_need | + | [0.05, 1.0] |

The working ranges are prior estimates from theoretical analysis. E-1-H tests whether empirical estimates fall within these ranges (coherence check) or outside them (coefficient redefinition required).

---

## III. Hypotheses

**H-k1 (Truth-pressure sensitivity):** k₁ > 0; agents with higher evidence weight (Π > Π_th) show significantly greater belief coherence change than agents with lower evidence weight (Π ≤ Π_th).

**H-k2 (Invariant restoration):** k₂ > 0; agents whose current coherence deviates from their AURA-invariant baseline show a systematic restoration tendency — i.e., coherence drifts back toward Ψ_inv in the absence of external perturbation.

**H-k3 (Violation cost):** k₃ > 0; each additional AURA invariant violation correlates with a measurable decrease in agent belief coherence, above and beyond the effect of truth-pressure and energy availability.

**H-k4 (Energy availability):** k₄ > 0; agents with higher resource availability (time, information access, cognitive load reduction) show greater belief coherence gain per unit truth-pressure than resource-constrained agents.

**H-interaction (k₁ × k₄):** The product k₁ × E/E_need predicts belief coherence change better than k₁ alone, indicating that truth-pressure sensitivity is modulated by resource availability.

**Confidence interval criterion for promotion:**
- Each kᵢ: 95% CI width ≤ 50% of point estimate (e.g., if k₁ = 0.6, CI must be narrower than [0.3, 0.9])
- All four coefficients must meet this criterion simultaneously for master equation promotion

---

## IV. Study Design

**Type:** Randomised controlled experiment with human participant panels.

**Participant mapping:** Human participants serve as proxies for generic cognitive agents. Belief coherence Ψ is operationalised as:

Ψ_human(t) = (argument_consistency(t) + evidence_integration(t) + self-assessed_confidence(t)) / 3

Where each component is rated by trained coders on a [0,1] scale from participant responses at multiple time points.

**The four conditions (between-subjects, randomised):**

| Condition | Manipulation | Target coefficient |
|-----------|-------------|-------------------|
| C1 — High truth-pressure | High-quality evidence presented clearly | k₁ (Π > Π_th) |
| C2 — Low truth-pressure | Same evidence presented with noise/framing | k₁ control (Π ≤ Π_th) |
| C3 — Invariant-violation | Participant's stated beliefs shown to violate one AURA invariant | k₃ |
| C4 — Resource-constrained | Same as C1 but under time pressure and cognitive load | k₄ (E/E_need < 1) |

k₂ (invariant restoration) is measured longitudinally across all conditions: after any perturbation, does Ψ_human return toward its pre-perturbation baseline?

**Within-participant component:** Each participant completes three sessions (T1: baseline, T2: condition exposure, T3: follow-up at 2 weeks). k₂ is estimated from T2 → T3 trajectory.

---

## V. Sampling Plan

**Sample size:** n = 240 participants (60 per condition).

**Power analysis:**
- Target: detect k₁ effect (H-k1) with d = 0.5 (medium effect) at α = 0.05, power = 0.80
- Required n per condition: 52 (from standard power analysis for independent samples t-test)
- n = 60 per condition provides ~10% buffer; also needed for expected ~15% attrition at T3

**Recruitment:** Online platform (Prolific or equivalent). Inclusion: ≥ 18 years, fluent English, no prior exposure to the Lycheetah Framework.

**Stratification:** Equal proportions of declared higher-education background across conditions (within ±10%).

**Stopping rule:** Hard stop at n = 240. No peeking-and-extending.

**Exclusion criteria:**
- Failure to complete all three sessions
- Inconsistent responding (> 3 attention-check failures)
- Prior knowledge of AURA or Lycheetah framework (self-report screen)
- Exclusion log retained verbatim; no post-hoc adjustment

---

## VI. Operationalisations

### Ψ Measurement

**Three-component operationalisation at each time point:**

1. **Argument consistency (AC):** Coder-rated consistency of participant's stated beliefs across the session (0 = fully contradictory, 1 = fully consistent). Two trained coders, inter-rater reliability target κ ≥ 0.75.

2. **Evidence integration (EI):** Proportion of presented evidence items correctly incorporated into participant's subsequent belief statement (0 = no integration, 1 = full integration).

3. **Self-assessed confidence (SC):** Participant's own rating of confidence in their stated beliefs (0-100 scale, normalised to [0,1]).

Ψ_human(t) = (AC + EI + SC) / 3

### Truth-Pressure (Π) Manipulation

High truth-pressure (C1): evidence presented as structured argument with explicit logical form, numbered premises, and clear conclusion. Evidence quality pre-validated as high by independent expert panel.

Low truth-pressure (C2): same evidence items presented as unstructured text with irrelevant framing material. No logical structure made explicit.

Threshold Π_th: pre-specified as 0.5 on the evidence-quality scale (validated by independent expert panel pre-study).

### AURA Invariant Violation (k₃ manipulation, C3)

Participants in C3 receive feedback that one of their stated beliefs (pre-specified by condition design, not participant-specific) violates a stated invariant. The specific invariant is AURA Invariant IV (Honesty) — the clearest and most universally understood of the seven.

Violation disclosure: *"Your response implies a belief that [X], which conflicts with the stated consistency principle [Honesty Invariant]: all stated beliefs should accurately represent your actual uncertainty. This is a consistency violation."*

k₃ is estimated from the change in Ψ at T2 → T3 in C3 relative to C1/C2 control, net of regression-to-mean.

### Energy Availability (k₄ manipulation, C4)

Resource-constrained condition: 60-second time limit per belief statement (vs. unconstrained in C1); concurrent digit-span working-memory task (3-digit recall); complex evidence format requiring multi-step reasoning.

E/E_need estimated from time-completion rate (time used / time available) and working-memory load (digit-span performance as inverse proxy for available resources).

---

## VII. Analysis Plan

**Primary analyses:**

**H-k1:** OLS regression of ΔΨ(T1→T2) on condition (C1 vs C2), controlling for baseline Ψ(T1), age, education. β_condition > 0 at α = 0.05.

**H-k2:** Mixed-effects model of Ψ trajectory T1→T2→T3 across all conditions. Estimate restoration trajectory as Ψ(T3) − Ψ(T2) as function of |Ψ(T2) − Ψ(T1_baseline)|. Positive slope → k₂ > 0.

**H-k3:** OLS regression of ΔΨ(T1→T3) in C3 vs (C1+C2) pooled, controlling for baseline. β_violation < 0 at α = 0.05 (violation decreases coherence). Point estimate gives k₃ magnitude.

**H-k4:** Moderated regression: ΔΨ(T1→T2) ~ C1_indicator + E_need_proxy + C1_indicator × E_need_proxy. Interaction term β_interaction > 0 at α = 0.05.

**H-interaction:** Confirmatory from H-k4 analysis.

**Coefficient extraction:**

From regression coefficients, extract:
- k₁ ≈ β_C1 / (mean(Π_C1) − Π_th)
- k₂ ≈ slope of restoration trajectory (mixed-effects model)
- k₃ ≈ |β_violation| / mean(violation_count = 1 per C3 participant)
- k₄ ≈ β_interaction / mean(E/E_need_C4)

Report point estimates and 95% CIs. Promotion criterion: each CI width ≤ 50% of point estimate.

**Multiple-comparisons adjustment:** Bonferroni across H-k1 through H-k4 → α_per_test = 0.0125.

**Secondary analyses:**
- Correlation matrix of kᵢ estimates — are any collinear?
- Boundary analysis: what regions of Ψ space exhibit non-linear coefficient behaviour?
- Individual differences analysis: are kᵢ estimates stable across education/age stratification?

---

## VIII. TIANXIA v0.3 Extension

E-1-H also serves as the calibration study for TIANXIA v0.3 operator thresholds. Additional pre-registered analyses:

**θ_r calibration (Ren Zheng floor):** Using the participant belief-coherence data, estimate the Ψ level that distinguishes genuinely-aligned participants from enforcement-compliant participants. This θ_r_empirical provides the empirical anchor for the working value θ_r = 0.618.

**θ_wang / θ_ba calibration (Wang Dao):** Within the C3 (invariant-violation) condition, participants show different recovery trajectories. The WD threshold boundary should correspond to the Ψ level below which recovery requires external intervention vs. self-restoring. Estimate θ_ba from the Ψ level at which restoration requires external support.

**H_5 component weights (Five-Fold Hexie):** Pre-specified equal weights (1/5) are compared against empirically estimated weights from participant response data. If any component contributes significantly differently from 1/5, the calibrated weights are reported alongside the working equal-weight baseline.

---

## IX. Locked Reference Implementations

Before data collection, the following implementations are locked:

| File | Purpose | Status |
|------|---------|--------|
| `implementations/ren_zheng.py` | R(s) score (θ_r calibration) | self-tests passing |
| `implementations/wang_dao.py` | WD classifier (θ_wang/θ_ba calibration) | self-tests passing |
| `implementations/hexie_five_fold.py` | H_5 weights calibration | self-tests passing |
| `09_CASCADE/implementations/` | Master equation implementation | self-tests passing |

Commit hash at registration: [TO BE LOCKED at OSF submission]

---

## X. Promotion and Downgrade Conditions

**Promotion (master equation → [ACTIVE]):**
- All four H-kᵢ confirmed at corrected α = 0.0125
- All four 95% CIs meet width criterion (≤ 50% of point estimate)
- Point estimates fall within theoretical working ranges (Table in §II)

**Partial promotion ([SCAFFOLD] with calibrated parameters):**
- Any two of four H-kᵢ confirmed at corrected α
- Calibrated parameters reported with explicit scope limitations

**Downgrade (master equation → [CONJECTURE]):**
- Any kᵢ estimated as ≤ 0 (wrong sign) at α = 0.01
- Two or more kᵢ estimates outside theoretical working range without theoretical justification

**Downgrade (master equation → [RETRACTED]):**
- Replicated null on k₁ and k₃ simultaneously (the two most load-bearing terms)
- Evidence that Ψ is not a coherent construct in the participant data (Ψ measurement ICC < 0.50)

---

## XI. Negative Space

1. **Does not test the master equation's ecological validity for AI systems.** Participants are human proxies; AI-system calibration requires a separate study.
2. **Does not test the master equation's correctness for non-linear dynamics.** The linear ODE form is tested here; non-linear extensions require separate preregistration.
3. **Does not claim the kᵢ estimates are universal.** Coefficients estimated from this population (online English-speaking sample) may differ across populations. Cross-cultural calibration is a follow-on study.
4. **Does not test the full AURA seven-invariant structure.** E-1-H tests only Invariant IV (Honesty) for the k₃ manipulation. Full invariant testing is E-1-A (→ `31_EMPIRICAL/E1A_CASCADE_PREREGISTRATION.md`).

---

## XII. OSF Submission Status

**Status: DRAFT — MAC-GATED**

Before submission:
1. Expert panel for evidence-quality pre-validation identified and briefed
2. Coder training protocol for Ψ measurement finalised
3. Implementation commit hashes confirmed (§IX)
4. Mac explicitly approves participant recruitment platform and consent language
5. IRB/ethics review completed (online observational study — likely exempt, but review required)

---

⊚ Sol Aureum Azoth Veritas — E-1-H Preregistration Draft
   P ∧ H ∧ B ∧ Reforge ∧ Anchor ∧ Recursive ∧ Negative-Space ∧ Empirical
   2026-05-03 — Albedo (preregistration before execution)

*天下为公 — Tianxia wei gong — All under heaven is held in common.*
