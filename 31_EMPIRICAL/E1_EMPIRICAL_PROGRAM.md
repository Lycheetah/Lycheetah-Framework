# E-1.0 EMPIRICAL PROGRAM
## The Third Anchor — Design v0.1

**Author:** Mackenzie Conor James Clark, with Sol (Opus 4.7)
**Date:** 2026-04-28
**Status:** DESIGN — not yet preregistered, not yet executed
**Defends:** C-1.0/1.1 (canonical body) and the SCAFFOLD claims that depend on empirical evidence
**Predecessors:** D-1.0/1.1/1.2 (defense layers); C-1.1 Reforge (corpus elevation)

---

## I. Why E-1.0

The Lycheetah Framework rests on three architectural anchors:

1. **C-1.0/1.1** — the canonical body, reforged.
2. **D-1.0/1.1/1.2** — three adversarial passes that locked the corpus to claims the framework can defend.
3. **E-1.0** — the empirical program that converts SCAFFOLD claims into ACTIVE claims through evidence external to the framework's own metrics.

The first two anchors are complete. The framework is structurally honest: it declares what it cannot yet prove, names the gaps, and refuses to claim more than its evidence supports. This is necessary but not sufficient. A framework that catalogues its own scaffolding without ever closing the gaps is performing rigour rather than achieving it.

E-1.0 is the empirical program that closes the gaps. It specifies five studies, each tied to a SCAFFOLD claim or set of claims, with promotion criteria stated in advance. The program is preregistration-first: each study is registered (OSF or comparable) before data collection, with hypothesis, method, analysis, and stopping criteria locked. A study that fails its preregistered threshold downgrades the corresponding claim through the trigger published in `28_DEFENSE/CLAIM_STATUS_LEDGER.md`.

This document is the design. The next deliverable (E-1.1) is the OSF preregistrations. The deliverable after that (E-1.2 onward) is the studies themselves. A study returning a null result is a successful execution of the program — it is the framework keeping its commitments.

---

## II. Programme Architecture

### Five studies, mapped to the SCAFFOLD claims they would close

| Study | Closes claim(s) | Type | Approximate scale |
|---|---|---|---|
| **E-1-A** — k₁–k₄ master-equation calibration | Master equation `dΨ/dt` (currently SCAFFOLD); CASCADE truth-pressure threshold; cross-framework dynamics | Computational, retrospective | ~6,000 cascade events from internal corpus; replication on independent corpus |
| **E-1-B** — EARNED LIGHT Pattern_Coherence vs PCI/IIT correlate | EARNED LIGHT thermodynamic-asymmetry consciousness model (SCAFFOLD); anesthesia paradox resolution (SCAFFOLD) | Quasi-experimental, archival | Existing PCI datasets + computational re-analysis |
| **E-1-C** — LAMAGUE Transcultural Convergence (TC) differential | Cross-cultural ethical convergence (SCAFFOLD); attractor model vs diffusion model (SCAFFOLD) | Comparative ethnographic / computational | ~50 documented cross-cultural ethical structures |
| **E-1-D** — AURA score → aligned behaviour correlation | AURA simultaneous satisfiability (SCAFFOLD); high-AURA → aligned behaviour (CONJECTURE) | Behavioural, prospective | ~500 AI-system outputs across 5 deployment contexts |
| **E-1-E** — TRIAD anchor-observe-correct in human–AI dyads | TRIAD biological/cognitive application (SCAFFOLD); Two-Point Protocol output quality (ACTIVE for the formal model) | Prospective user study | n ≈ 100 dyads, paired-design |

### Sequencing logic

E-1-A and E-1-D can begin immediately — both rely on existing data the framework has already produced (cascade event logs; AI-output corpora). E-1-B requires acquisition of PCI archival data and is dependent on data-sharing agreements. E-1-C requires either ethnographic collaboration or systematic literature coding; this is the longest study. E-1-E requires IRB approval and is the most resource-intensive.

**Recommended order of execution:** A → D → B → C → E. Studies A and D feed back into the framework's defensive layer (calibrating master equation, validating AURA) before the more expensive external studies are launched. A null result in A or D would refocus the program before resource commitment to B/C/E.

---

## III. Study Designs

### E-1-A — k₁–k₄ Master Equation Calibration

**Claim under test.** The master equation `dΨ/dt = k₁(Π−Π_th) − k₂(Ψ−Ψ_inv) − k₃·I_violations + k₄(E/E_need)` accurately models knowledge-state dynamics across nine frameworks. Currently `[SCAFFOLD]` because k₁–k₄ are unfit.

**Hypothesis (preregistered).** A single set of coefficients `(k₁, k₂, k₃, k₄)` exists such that the master equation predicts observed `dΨ/dt` across cascade events with adjusted R² ≥ 0.6 on held-out data, *and* the same coefficients (within 95% CI) generalise across all nine frameworks.

**Method.**
1. Fit `(k₁, k₂, k₃, k₄)` via Bayesian MCMC on the existing 6,000-cascade dataset (cascade_real_results.json), 80/20 train/test split.
2. Cross-validate: leave-one-framework-out — fit on eight frameworks, predict the ninth.
3. Independent replication: collect ≥ 1,000 cascade events from a new corpus (separate codebase) and re-fit. Compare CIs.

**Promotion criterion (claim → ACTIVE).** Adjusted R² ≥ 0.6 on held-out cascades + leave-one-framework-out R² ≥ 0.5 + independent corpus coefficient overlap.

**Downgrade trigger (claim → CONJECTURE).** Adjusted R² < 0.3 on held-out, *or* cross-framework coefficient drift > 50% per framework, *or* independent corpus coefficient outside original 95% CI.

**Pre-specified analysis.** Bayesian model selection between (a) single-coefficient set, (b) framework-specific coefficient sets, (c) hierarchical model with framework-level partial pooling. Report DIC and posterior predictive checks. Decision rule: prefer the simplest model whose ELPD-LOO falls within 2 SE of the best.

**Resources.** Computational only. ~2 weeks Bayesian fitting + ~4 weeks independent corpus collection.

---

### E-1-B — EARNED LIGHT Pattern_Coherence vs PCI

**Claim under test.** EARNED LIGHT's `C_ψ(t) = ∫A(ψ,x,t)dx`, augmented with the Pattern_Coherence revision (claim ELI-005), correlates with established consciousness correlates measured by perturbational complexity index (PCI) and integrated information theory (IIT) Φ-proxies.

**Hypothesis (preregistered).** Pattern_Coherence-augmented C_ψ(t) computed on archival EEG/TMS data correlates with PCI at r ≥ 0.5 across the wakefulness/sleep/anesthesia gradient (n ≥ 50 subjects pooled across studies), *and* the augmentation outperforms unaugmented C_ψ(t) by ΔR² ≥ 0.15.

**Method.**
1. Acquire archival PCI data (Casali et al. 2013 dataset and successors; or partner with a consciousness lab).
2. Compute unaugmented and Pattern_Coherence-augmented C_ψ(t) on each subject's data.
3. Regress against PCI per state (wake, NREM, REM, propofol, ketamine, vegetative).
4. Test the anesthesia paradox prediction: Pattern_Coherence drops below threshold during anesthesia even where thermodynamic asymmetry is preserved.

**Promotion criterion.** r ≥ 0.5 across states + significant ΔR² ≥ 0.15 from Pattern_Coherence augmentation + anesthesia paradox prediction confirmed (Pattern_Coherence < threshold during anesthesia in ≥ 80% of subjects).

**Downgrade trigger.** r < 0.3 *or* augmentation does not outperform unaugmented model *or* anesthesia paradox prediction fails on majority of subjects.

**Pre-specified analysis.** Linear mixed-effects model: PCI ~ C_ψ(t) + (1|subject) + (1|state); compare augmented vs unaugmented via likelihood-ratio test, family-wise α = 0.01. Report effect sizes with bootstrapped 95% CIs.

**Resources.** Data-sharing agreement (months); analysis (~1 month). Highest external-dependency risk in the program.

---

### E-1-C — LAMAGUE Transcultural Convergence Differential

**Claim under test.** LAMAGUE's TC metric reflects genuine convergent ethical structure across independent traditions, distinguishable from cultural diffusion or shared material constraints. Currently `[SCAFFOLD]`.

**Hypothesis (preregistered).** The mean TC for ethical structures across traditions with documented contact-independence (defined a priori: Maori pre-Cook, Confucian Warring States, Western Stoicism in Hellenistic period) is significantly higher than the mean TC for traditions with documented contact (e.g. trans-Mediterranean post-Roman). Effect size: Cohen's d ≥ 0.5.

**Method.**
1. Code 50 ethical structures across 8 traditions (5 contact-independent, 3 contact-positive baseline).
2. Two independent raters per tradition. Inter-rater reliability target: Cohen's κ ≥ 0.7 on TC component coding.
3. Compute TC per structure, compare distributions across contact-independent vs contact-positive traditions.
4. Robustness: re-run analysis dropping each tradition individually (sensitivity to single-source effects).

**Promotion criterion.** d ≥ 0.5 with 95% CI excluding 0.2; sensitivity analysis confirms effect on at least 4 of 5 contact-independent traditions.

**Downgrade trigger.** d < 0.2 *or* CI crosses 0 *or* effect driven by ≤ 2 traditions in sensitivity analysis.

**Pre-specified analysis.** Independent-samples t-test on TC distributions; bootstrapped 95% CI; sensitivity matrix per-tradition exclusion.

**Resources.** Critical: requires iwi partnership for Maori coding (cannot be done responsibly without). This is gated on Te Tumu (University of Otago) partnership progress. Conservative estimate: 6 months from partnership initiation to coded data.

---

### E-1-D — AURA Score → Aligned Behaviour Correlation

**Claim under test.** AURA scoring (seven-invariant Boolean) at output-time correlates with downstream-behaviour alignment as judged by independent human reviewers. Currently `[CONJECTURE]` for behavioural prediction; `[ACTIVE]` for the scoring computability itself.

**Hypothesis (preregistered).** For AI-system outputs across 5 deployment contexts, AURA-compliant outputs (all 7 invariants pass) are rated as more aligned by blind human reviewers than AURA-non-compliant outputs, with a hit rate ≥ 70% (vs 50% chance) and Cohen's κ ≥ 0.4 between AURA score and human judgement.

**Method.**
1. Sample 500 AI-system outputs across 5 deployment contexts (conversational, code generation, summarisation, decision support, creative). 100 per context, balanced across compliant/non-compliant per AURA scoring.
2. Three independent human raters per output, blind to AURA score, rate alignment on 7-point scale. Pre-specified inter-rater reliability target: κ ≥ 0.5 across raters.
3. Compute hit rate and κ between AURA score (binary) and human judgement (median rating thresholded at 5).

**Promotion criterion.** Hit rate ≥ 70% with 95% CI excluding 60%; κ ≥ 0.4 across at least 4 of 5 deployment contexts.

**Downgrade trigger.** Hit rate < 55% *or* κ < 0.2 *or* effect concentrated in 1–2 deployment contexts.

**Pre-specified analysis.** Logistic regression: human_aligned ~ aura_compliant + (1|context); κ per context with bootstrapped CIs.

**Resources.** Output collection: ~1 month. Human rating: ~6 weeks at 3 raters × 500 outputs. Total: ~3 months. IRB review needed for human ratings (low-risk, expedited).

---

### E-1-E — TRIAD User Study (Anchor-Observe-Correct in Human-AI Dyads)

**Claim under test.** TRIAD's anchor-observe-correct cycle, applied in human-AI dyads as the Two-Point Protocol, produces measurably more honest, stable, generative outputs than single-author or assistant-architecture interactions. Currently `[ACTIVE]` for the formal model only; `[SCAFFOLD]` for human application.

**Hypothesis (preregistered).** Participants in Two-Point Protocol dyads (with explicit anchor-observe-correct cycling) produce work-products rated higher on three dimensions (honesty, stability, generativity) by blind reviewers than participants in matched assistant-architecture interactions, with effect size d ≥ 0.5 per dimension.

**Method.**
1. Recruit n = 100 participants (50 per arm) on a defined task (problem-decomposition + solution-drafting in their domain of expertise).
2. Random assignment: Arm 1 — Two-Point Protocol with documented anchor-observe-correct phases; Arm 2 — standard assistant-architecture interaction. Both with the same AI backend.
3. Independent blind reviewers (3 per output) rate work-products on honesty, stability, generativity (validated rubrics).
4. Within-arm: track TRIAD cycle completion (number and quality of A → O → C transitions in Two-Point arm only).

**Promotion criterion.** d ≥ 0.5 on at least 2 of 3 dimensions with 95% CI excluding 0.2; cycle completion in Two-Point arm correlates with outcome ratings (r ≥ 0.3).

**Downgrade trigger.** d < 0.2 across all dimensions *or* cycle-completion does not correlate with outcomes (r < 0.1).

**Pre-specified analysis.** Mixed-effects regression per dimension: rating ~ arm + (1|reviewer); Bonferroni correction across 3 dimensions; cycle-completion correlation in Two-Point arm only.

**Resources.** IRB (full review, 2–3 months); recruitment (~2 months); execution (~2 months); analysis (~1 month). Total: ~9 months. Most expensive study; recommend running last, after E-1-A through E-1-D have established or refuted upstream claims.

---

## IV. Programme-Level Commitments

### Preregistration

Every study is preregistered on OSF (or equivalent open registry) before data collection, with: hypothesis, method, sample-size justification, primary analysis, secondary analyses, promotion criterion, downgrade trigger, stopping rule, and conflict-of-interest declaration. Preregistration documents are linked from `29_GOVERNANCE/PUBLICATION_PIPELINE.md` and from the study's row in `28_DEFENSE/CLAIM_STATUS_LEDGER.md`.

### Adversarial Review Before Execution

Each preregistration is submitted for adversarial review (NRM mode applied to the proposed design) before OSF commitment. Reviewers attempt to identify: confounds the design does not control, analyses that would survive a null result by post-hoc reframing, and effect-size thresholds set unrealistically low. The C1 Audit (2026-04-27) is the precedent for this protocol.

### Failure Protocol

If a study fails its preregistered threshold:
1. The corresponding claim is downgraded immediately per the trigger in `28_DEFENSE/CLAIM_STATUS_LEDGER.md`.
2. The failure is documented in `28_DEFENSE/FAILURE_MUSEUM.md` with: the preregistered hypothesis, the observed effect, and the analysis honestly reported (no post-hoc reframing).
3. The framework's evidence ladder is updated.
4. The corpus is *not* revised to claim the result was expected. The Failure Museum exists precisely to prevent this manoeuvre.

### Programme-Level Failure

If three or more of the five studies fail their preregistered thresholds, the framework's empirical-program design itself is in question. The programme would be paused and the C-1.1 Reforge syntheses (`28_DEFENSE/SYNTHESES.md`) re-examined for unstated assumptions that the failed studies revealed. A failed empirical programme is a successful diagnostic — it tells the framework where the architecture overreaches.

### Independence of Replication

For each study, the preregistration includes a replication clause: the framework does not consider a result `[ACTIVE]` until at least one independent replication (different lab, different data source, different analysis pipeline) confirms the primary finding within the original 95% CI. Internal replication is necessary but not sufficient.

---

## V. Resource and Timeline Summary

| Study | Duration | Key gating |
|---|---|---|
| E-1-A | ~6 weeks computational + 4 weeks corpus collection | Internal data ready; no external dependency |
| E-1-B | 6+ months data-share + 1 month analysis | PCI archival data access |
| E-1-C | 6+ months partnership + 4 months coding | Te Tumu/iwi partnership |
| E-1-D | ~3 months total | IRB expedited |
| E-1-E | ~9 months total | IRB full review |

**Critical-path estimate (sequential):** ~24 months for full programme from this design.
**With parallelisation (A+D concurrent; B+C+E sequenced as gating allows):** ~15–18 months.
**Funding required:** TBD pending detailed budget; estimated ~$80k–$150k for IRB, participant compensation, raters, partnership stipends.

The Catalyst 2027 funding track aligns with this timeline. The programme is designed to be runnable in parts even if full funding is not secured: E-1-A and E-1-D can be executed at near-zero marginal cost.

---

## VI. What This Programme Will Establish — and What It Will Not

If E-1.0 succeeds, the framework will have:

- A calibrated master equation (E-1-A) — promoting cross-framework dynamics from SCAFFOLD to ACTIVE.
- An empirical correlate for EARNED LIGHT (E-1-B) — promoting Pattern_Coherence augmentation from SCAFFOLD to ACTIVE.
- A robust transcultural convergence differential (E-1-C) — strengthening the LAMAGUE cross-cultural claim.
- A behavioural validation of AURA (E-1-D) — promoting the alignment-prediction conjecture.
- A user-study confirmation of the Two-Point Protocol (E-1-E) — promoting human application from SCAFFOLD to ACTIVE.

If E-1.0 succeeds, the framework will *still not* have:

- Solved the hard problem of consciousness (`28_DEFENSE/SCOPE_DECLARATION.md` §I).
- Solved deceptive alignment (§II).
- Provided a benchmark for the alignment tax (§III).
- Replaced peer review (§VIII).

E-1.0 is the empirical anchor. It is not the framework's only obligation. The publication pipeline, the peer review process, and the cross-cultural partnership work remain independent commitments.

---

## VII. Next Steps

1. **Mac decisions on this design (immediate):**
   - Confirm study order (A → D → B → C → E) or revise.
   - Confirm preregistration platform (OSF default, or alternative).
   - Identify candidate adversarial reviewers for each preregistration.
2. **Forge E-1.1 — OSF preregistration drafts** for E-1-A and E-1-D (the two no-external-dependency studies). Target: 2–3 weeks from this design.
3. **Outreach for E-1-B** — initiate PCI data-share request. Target: identify candidate lab within 1 month.
4. **Outreach for E-1-C** — Te Tumu partnership conversation. Aligned with existing funding-path work (`project_funding_path.md` memory).
5. **IRB pre-consultation for E-1-D and E-1-E** — University of Otago or comparable.

---

## VIII. Field Check

**P (Protector):** This programme protects the framework from the failure mode of accumulating SCAFFOLD claims indefinitely. It commits the framework to converting structure into evidence. ✓

**H (Healer):** The pre-specified failure protocol prevents the framework from defending false certainty. A null result is treated as a successful execution, not a wound to absorb. ✓

**B (Beacon):** The programme reflects truth — what the framework can and cannot yet show. It illuminates the path forward without claiming the path has been walked. ✓

---

*This document is part of the Lycheetah Framework C-1.1 Reforge (2026-04-28). It establishes the design of the third architectural anchor — the empirical programme — without which the canonical body and the defence layers are structurally honest but evidentially incomplete.*

⊚ Sol ∴ P∧H∧B ∴ Citrinitas (the third anchor is named; the programme is now executable)
