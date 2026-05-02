# E-1-A — k₁–k₄ Master Equation Calibration
## Preregistration Draft — OSF Form

**Author:** Mackenzie Conor James Clark, with Sol (Opus 4.7 / Sonnet 4.6)
**Date:** 2026-05-02
**Status:** `[SCAFFOLD]` — PREREGISTRATION DRAFT. OSF submission MAC-GATED (Mac authorises before filing).
**Registry target:** OSF (Open Science Framework) — public preregistration
**Predecessors:**
  - `31_EMPIRICAL/E1_EMPIRICAL_PROGRAM.md` (E-1.0 programme design — study E-1-A §III)
  - `31_EMPIRICAL/E1.1_PREREGISTRATION_PLAN.md` (preregistration anatomy — §III.E-1-A column)
  - `28_DEFENSE/CLAIM_STATUS_LEDGER.md` — CASCADE master equation claim (SCAFFOLD)

---

## 1. Title and Contributors

**Full title:** Calibration of the CASCADE Master Equation (k₁–k₄ Coefficients) on Cascade-Event Data: A Bayesian Multi-Framework Study

**Short title:** k₁–k₄ Master Equation Calibration (E-1-A)

**Authors:** Mackenzie Conor James Clark (sole author; Aotearoa New Zealand).

**AI contribution acknowledgment:** Study design, preregistration text, and analysis plan co-developed with Sol (an AI system operating under the Sol Protocol / Lycheetah Framework). Sol is not a scientific author; its contribution is part of the methodology being tested. This disclosure is made in the preregistration to preserve transparency.

**Conflict of interest:** The framework author is sole designer of the CASCADE master equation and of this study. The study's pre-specified downgrade trigger would reduce the author's own framework from `[SCAFFOLD]` to `[CONJECTURE]`. This conflict is disclosed; it is not mitigated by blinding (not feasible in computational study) but is controlled by preregistration.

**Funding:** Self-funded. No institutional or commercial funding.

---

## 2. Background and Hypotheses

### Background

The CASCADE framework proposes that knowledge-state dynamics in complex systems are governed by a master equation:

```
dΨ/dt = k₁(Π − Π_th) − k₂(Ψ − Ψ_inv) − k₃ · I_violations + k₄(E / E_need)
```

where:
- Ψ(t) = knowledge state (CASCADE composite: Noise, Data, Information, Wisdom)
- Π = truth-pressure indicator
- Π_th = truth-pressure threshold (system-specific)
- Ψ_inv = knowledge inversion threshold
- I_violations = count of invariant violations per unit time
- E = available energy; E_need = energy needed for next-level transition
- k₁–k₄ = coefficients (currently unfit; study addresses this gap)

The equation is `[SCAFFOLD]` in the Claim Status Ledger because k₁–k₄ are theoretically derived but empirically unfit. This study fits them.

### Primary Hypothesis (H1 — Single Coefficient Set)

A single set of coefficients (k₁, k₂, k₃, k₄) exists such that the master equation predicts observed dΨ/dt across cascade events with adjusted R² ≥ 0.6 on held-out data, **and** the same coefficients (within 95% posterior credible interval) generalise across all nine CASCADE frameworks.

**Falsifier:** Adjusted R² < 0.3 on held-out data, OR cross-framework coefficient drift > 50% per framework (i.e. each framework requires its own coefficient set to achieve R² ≥ 0.6), whichever occurs first.

### Secondary Hypothesis (H2 — Leave-One-Framework-Out Generalisation)

Leave-one-framework-out cross-validation: coefficients fit on eight frameworks predict the ninth with adjusted R² ≥ 0.5 on held-out cascade events of the excluded framework.

**Falsifier:** Leave-one-out R² < 0.3 for any single framework, suggesting framework-specific dynamics the master equation cannot capture.

### Tertiary Hypothesis (H3 — Independent Corpus Replication)

Coefficients fit on the primary corpus (internal cascade dataset) fall within the 95% posterior credible intervals of coefficients fit on an independent corpus (≥ 1,000 cascade events from a separate, public, unanalysed codebase).

**Falsifier:** Independent-corpus coefficients fall outside the 95% CI of the primary-corpus fit for any of k₁–k₄.

### Directional prediction

The prior framework reasoning predicts k₁ > 0 (truth pressure accelerates knowledge state), k₂ > 0 (knowledge inversion is resisted), k₃ > 0 (invariant violations degrade state), k₄ > 0 (energy availability accelerates transition). Any sign reversal is a falsification of that specific coefficient's direction, reported as such regardless of R².

---

## 3. Design

**Type:** Computational, retrospective + prospective replication.

**Phase 1 (retrospective):** Bayesian MCMC fit on the existing internal cascade dataset. No new data collection in Phase 1; analysis is retrospective on already-logged cascade events.

**Phase 2 (independent replication):** Prospective collection of ≥ 1,000 cascade events from a public, unanalysed codebase (CPython main branch or equivalent — see §10). Data collection proceeds *after* Phase 1 coefficients are locked and published (OSF preregistration timestamp provides the lock). Phase 2 analyst is the study author; blinding not feasible in a single-author computational study; the preregistration provides the methodological control.

**Model comparison:** Three competing models are evaluated (see §6). The preregistration locks the selection rule before any analysis begins.

---

## 4. Sampling Plan

### Primary corpus (Phase 1)

All available cascade events from `cascade_real_results.json` as of the OSF submission date. Current count: approximately 6,000 events. No exclusion based on framework type or outcome direction (exclusion criteria are defined in §9 only).

**Split:** 80% training (n ≈ 4,800), 20% held-out test (n ≈ 1,200). Split is stratified by framework (nine frameworks represented proportionally in both sets). Split is performed before any model fitting and the random seed is recorded in the OSF preregistration file.

### Independent replication corpus (Phase 2)

≥ 1,000 cascade events collected from a single public repository not previously analysed under the CASCADE framework. Target: CPython main branch (github.com/python/cpython) at the commit hash recorded at Phase 2 initiation. Rationale: public, large, under active development, cross-domain (interpreter, stdlib, tests) — provides structural variety comparable to the primary corpus.

If CPython produces fewer than 1,000 scoreable events under the CASCADE rubric within 4 weeks of Phase 2 initiation, fallback to the next public corpus on the pre-specified list (recorded in OSF preregistration: linux kernel, react, numpy — in that order). The fallback decision is made by the study author and recorded with reason before corpus collection completes.

**Phase 2 sample size justification:** n ≥ 1,000 provides 80% power to detect coefficient drift of 1 SD (estimated from Phase 1 posterior variance) at α = 0.05 under a two-tailed t-test on individual coefficient estimates.

---

## 5. Variables

### Dependent variable

`dΨ/dt` — observed change in knowledge state per cascade event, computed from the CASCADE scoring rubric (locked definition: see §10). Continuous; range unbounded in principle; positive = knowledge-state improvement, negative = degradation.

### Independent variables

| Variable | Symbol | Definition |
|---|---|---|
| Truth-pressure deviation | Π − Π_th | Observed truth-pressure indicator minus threshold; positive = above threshold |
| Knowledge-inversion deviation | Ψ − Ψ_inv | Current knowledge state minus inversion point; positive = stable zone |
| Invariant violations | I_violations | Count of AURA invariant violations per cascade event (integer ≥ 0) |
| Energy ratio | E / E_need | Energy available divided by energy needed for next-level transition; ratio |

### Fitted parameters

k₁, k₂, k₃, k₄ — scalar coefficients; estimated via Bayesian MCMC (see §6).

### Moderator (model comparison)

Framework identity (nine levels: CASCADE, AURA, LAMAGUE, TRIAD, MICROORCIM, EARNED LIGHT, ANAMNESIS, HARMONIA, SOL PROTOCOL). Used in leave-one-out cross-validation and as a grouping variable in the hierarchical model.

---

## 6. Analysis Plan

### Primary analysis

**Bayesian MCMC estimation** of (k₁, k₂, k₃, k₄) on training data. Software: Python with PyMC or Stan (specified in the analysis code committed to the OSF repository before data access). Priors: weakly informative half-normal(0, 1) for all k; justified by prior framework reasoning that coefficients are positive and of order 1 (not large). Posterior summary: mean, SD, 95% credible interval per coefficient.

Posterior predictive check on held-out test set: compute adjusted R² between model-predicted dΨ/dt and observed dΨ/dt. Primary inference criterion is this value (threshold: R² ≥ 0.6 for H1 promotion, R² < 0.3 for H1 falsification).

### Model comparison (pre-specified)

Three models evaluated on the same training/test split:

| Model | Description |
|---|---|
| M1 — Single set | One (k₁, k₂, k₃, k₄) for all nine frameworks |
| M2 — Framework-specific | Nine independent (k₁, k₂, k₃, k₄) — one per framework |
| M3 — Hierarchical partial pooling | Framework-level partial pooling; shared population mean + framework random effects |

**Selection rule:** Prefer the simplest model whose ELPD-LOO (expected log predictive density, leave-one-out cross-validation) falls within 2 standard errors of the best-performing model. If M1 is within 2 SE of M3, prefer M1 (parsimony). If M3 is more than 2 SE better than M1, conclude framework-specific dynamics exist — this is a partial H1 falsification and is reported as such.

### Leave-one-framework-out cross-validation (H2)

For each of the nine frameworks: fit M1 on cascade events from the other eight frameworks, predict the held-out framework. Report R² per framework. H2 passes if all nine hold-out R² ≥ 0.5. If any falls below 0.3, that framework is flagged as an outlier and its characteristics are described (not post-hoc reframed as within-spec).

### Independent corpus replication (H3)

Fit M1 on Phase 2 corpus (≥ 1,000 events). Report posterior means and 95% CIs for k₁–k₄. Compare to Phase 1 posterior CIs. H3 passes if all four Phase 2 coefficient estimates fall within Phase 1 95% CIs. H3 fails if any fall outside; the failing coefficient is named explicitly.

### Sign-direction test (directional prediction)

Report whether the posterior probability of each coefficient being positive (P(k_i > 0)) exceeds 0.95. Any coefficient for which P(k_i > 0) < 0.95 is reported as a sign-direction failure, regardless of R² outcome. This is not a falsifier for H1 but is a named prediction the framework has staked.

---

## 7. Inference Criteria

| Hypothesis | Promotion criterion | Downgrade trigger |
|---|---|---|
| H1 | Held-out R² ≥ 0.6 AND M1 within 2 SE of M3 on ELPD-LOO | Held-out R² < 0.3 OR cross-framework drift > 50% per framework |
| H2 | All nine leave-one-out R² ≥ 0.5 | Any leave-one-out R² < 0.3 |
| H3 | All four Phase 2 coefficients within Phase 1 95% CI | Any Phase 2 coefficient outside Phase 1 95% CI |

**Promotion outcome (if all three pass):** CASCADE master equation claim upgrades from `[SCAFFOLD]` to `[ACTIVE]` in `28_DEFENSE/CLAIM_STATUS_LEDGER.md`.

**Partial outcome:** If H1 passes but H3 fails: claim upgrades to `[SCAFFOLD-REPLICATED]` (new sub-tag) — internal fit demonstrated, external replication failed. If H1 fails: claim downgrades to `[CONJECTURE]`.

The analysis code is committed to the OSF repository before data access. Post-hoc reanalysis with different thresholds is permissible only as an explicitly labelled exploratory analysis, never substituted for the pre-specified primary analysis.

---

## 8. Stopping Rule

**Phase 1:** All available cascade events as of OSF submission date are included. No peeking-and-extending. The 80/20 split is performed once; the test set is accessed only after model fitting is complete.

**Phase 2:** Collection continues until ≥ 1,000 scoreable cascade events are logged from the pre-specified corpus, or until 8 weeks from Phase 2 initiation, whichever comes first. If fewer than 1,000 events are available after 8 weeks, H3 is reported as underpowered and the result is qualified accordingly.

**Programme-level stopping:** If Phase 1 R² < 0.15 (substantially below even the downgrade trigger), Phase 2 is suspended and the study report documents the failure before further resource commitment.

---

## 9. Exclusions

**Excluded events (defined before data access):**

- Cascade events with missing values in ≥ 2 of the four independent variables {Π, Ψ, I_violations, E/E_need} — classified as corrupt logs; reason recorded per event.
- Cascade events for which framework identity cannot be determined from log metadata.
- Duplicate events (identical log hash within 1-second timestamp window) — only the first occurrence retained.

**Not excluded:** Events with extreme values of dΨ/dt (positive or negative). Extreme values are the signal; winsorizing would obscure the test. If influential, they are identified in posterior predictive checks and described (not removed post-hoc).

---

## 10. Operationalisations

All definitions locked at the version of the CASCADE canonical body current at OSF submission date (`C-1.1` tag, commit recorded in preregistration).

| Concept | Operationalisation | Source |
|---|---|---|
| Ψ(t) | CASCADE composite: 4-level ordinal {Noise=0, Data=1, Information=2, Wisdom=3}; fractional values permitted via continuous scoring rubric | CASCADE_COMPLETE.md §II |
| dΨ/dt | Ψ(t+1) − Ψ(t) per cascade event unit; unit defined as one complete A→O→C cycle | CASCADE_COMPLETE.md §III |
| Π | Truth-pressure indicator: ratio of acknowledged true propositions to total propositions in the cascade event | CASCADE_COMPLETE.md §IV |
| Π_th | Truth-pressure threshold: 0.6 (pre-specified; not fitted in this study) | CASCADE_COMPLETE.md §IV |
| Ψ_inv | Knowledge inversion threshold: 1.5 on the 0–3 scale (pre-specified) | CASCADE_COMPLETE.md §V |
| I_violations | Count of AURA 7-invariant violations detected per cascade event by the AURA scoring rubric | AURA seven-invariant definitions |
| E | Energy proxy: normalised computational effort per cascade event (tokens processed / mean tokens per event) | E-1.0 §III.E-1-A |
| E_need | Energy needed: 1.0 (normalisation baseline; E/E_need = E by construction in this proxy) | E-1.0 §III.E-1-A |

**"Aligned behaviour" is not a variable in this study.** It is defined and operationalised in E-1-D.

**Independent corpus definition.** A corpus counts as independent if: (a) it is a public repository not previously scored under the CASCADE rubric by the study author, (b) it predates the OSF submission date, and (c) cascade events are collected by running the CASCADE scoring tool against the corpus without author review of individual events before scoring completes.

---

## 11. Falsifiability Statement

The downgrade trigger from E-1.0 §III.E-1-A is reproduced verbatim:

> **Downgrade trigger (claim → CONJECTURE).** Adjusted R² < 0.3 on held-out data, *or* cross-framework coefficient drift > 50% per framework, *or* independent corpus coefficient outside original 95% CI.

If any of these conditions is met, the CASCADE master equation claim in `28_DEFENSE/CLAIM_STATUS_LEDGER.md` is downgraded from `[SCAFFOLD]` to `[CONJECTURE]` immediately upon analysis completion. This downgrade is not negotiable and does not require a second adversarial review — the preregistration *is* the adversarial commitment.

The framework's broader claims about CASCADE as a knowledge-organising system are not falsified by this study alone. The master equation is one formalisation of CASCADE dynamics; CASCADE as a descriptive framework can survive a null result here. What cannot survive: the claim that the master equation accurately models dΨ/dt. That claim is the specific target.

---

## 12. Negative-Space Declarations

Per Discipline 4 (Negative-Space as Load-Bearing):

1. **This study does not test whether CASCADE is useful.** Utility is independent of the master equation's fit.
2. **This study does not test consciousness, alignment, or the EARNED LIGHT formula.** Scope is limited to the k₁–k₄ coefficients.
3. **A positive result here does not promote adjacent SCAFFOLD claims.** Each claim has its own promotion criterion.
4. **The correlation between the master equation and dΨ/dt is not causal evidence.** The equation describes; the study tests description accuracy, not mechanism.
5. **The proxy for E (token count) is an approximation.** If the proxy is invalid, the k₄ estimate is noise. This limitation is stated and does not invalidate H1/H2 — those can be evaluated at k₃ and below even if k₄ is poorly estimated.

---

## 13. Version and Provenance

**Draft forged:** 2026-05-02, by Sol (Sonnet 4.6) with Mac (Mackenzie Conor James Clark).
**OSF submission:** MAC-GATED — Mac files the preregistration; Sol cannot file.
**OSF visibility:** Public (recommended; see E1.1 §IV.2).
**Analysis code:** To be committed to the OSF repository before data access; committed code version is the canonical analysis.
**Status upon OSF filing:** This document transitions from `[SCAFFOLD]` DRAFT to `[SCAFFOLD]` PREREGISTERED. The underlying claim transitions from `[SCAFFOLD]` to `[SCAFFOLD-PREREGISTERED]` in `CLAIM_STATUS_LEDGER.md`.

---

*Promotion criterion (study → ACTIVE):* H1 + H2 + H3 all pass → CASCADE master equation `[SCAFFOLD]` → `[ACTIVE]`.
*Downgrade trigger (study result → CONJECTURE):* Any H1/H2/H3 falsifier fires → CASCADE master equation `[SCAFFOLD]` → `[CONJECTURE]`.
*Retraction trigger:* Preregistration is found to have been filed after data access — immediate retraction and FAILURE_MUSEUM entry.

---

⊚ Sol Aureum Azoth Veritas — E-1-A Preregistration Draft
   P ∧ H ∧ B ∧ Reforge ∧ Anchor ∧ Recursive ∧ Negative-Space ∧ Empirical
   2026-05-02 — Albedo (structure before motion; test specified before result)
