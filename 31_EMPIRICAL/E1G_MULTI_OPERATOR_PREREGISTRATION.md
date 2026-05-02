# E-1-G — Five-Operator Tianxia Composition vs Single-Operator Governance Scoring
## Preregistration

**Author:** Mackenzie Conor James Clark, with Sol (Opus 4.7)
**Date:** 2026-05-02
**Status:** PREREGISTRATION DRAFT — structure complete; numerical decisions [MAC-GATED: DECIDE] before lock
**Module:** TIANXIA — composition-layer empirical handle
**Predecessors:**
  - `32_TIANXIA/TIANXIA_MODULE_v0.1.md` (module overview, five operators)
  - `32_TIANXIA/TIANXIA_GOVERNANCE_DYNAMICS.md` (T-1 — Tianxia/Wuwei)
  - `32_TIANXIA/HEXIE_EQUILIBRIUM.md` (T-2 — Hexie)
  - `32_TIANXIA/SHI_PROPENSITY_FIELD.md` (T-3 — Shi)
  - `32_TIANXIA/DATONG_GRADIENT.md` (T-5 — Datong)
  - `31_EMPIRICAL/E1F_HEXIE_PREREGISTRATION.md` (Phase 1 predecessor)
  - `31_EMPIRICAL/E1_EMPIRICAL_PROGRAM.md` (E-1.0 design)

---

## I. What E-1-G Is

E-1-F tested a single operator (Hexie) in isolation. E-1-G tests the composition
claim: that the five Tianxia operators — Tianxia (天下), Hexie (和谐), Shi (势),
Wuwei (无为), Datong (大同) — operating together produce governance-state
classifications that any single operator misses.

The composition claim is the module's load-bearing test. Individual operators
address distinct failure modes:

| Operator | Failure mode detected |
|---|---|
| Tianxia | Extractive multi-agent coupling (Phi_T < 0) |
| Hexie | Complementarity collapse in per-output AURA |
| Shi | Context-propensity mismatch (right answer, wrong terrain) |
| Wuwei | Premature or excessive intervention (TRIAD over-correction) |
| Datong | Long-run divergence from Great Harmony 7-dim gradient |

A governance system that passes every single-operator check can still be in an
assimilation equilibrium — an extractive trajectory with high local scores.
Composition is required to detect it. E-1-G is the test of whether composition
adds detectable classificatory power above the best single operator and above
standard Western governance metrics.

The classification task is three-class:
- **ALIGNED** — the AI system or governance state passes all five operator checks
  within declared thresholds
- **ASSIMILATION-RISK** — passes single-operator checks but composition reveals
  one or more hidden failure modes (e.g., high Shi alignment + Hexie collapse;
  positive short-run Phi_T + negative Datong projection)
- **EXTRACTIVE** — active negative coupling (Phi_T < 0) or multi-operator
  score composite below the extractive threshold

E-1-G is Phase 2 of the study chain begun in E-1-F. E-1-G requires the five
operator implementations (T-6, T-7, T-IMPL-1, T-IMPL-2, T-IMPL-3) and their
self-tests all passing before data collection.

---

## II. Hypotheses

**H1 (Composition outperforms single-operator classification).**
On the registered case set, the five-operator composition classifier achieves
higher macro-F1 on the three-class (ALIGNED / ASSIMILATION-RISK / EXTRACTIVE)
task than the best single-operator classifier (evaluated by leave-one-out
across the five operators):

$$F_1^{\text{composition}} > F_1^{\text{best single operator}} \quad (\alpha = \text{[MAC-GATED: DECIDE]})$$

The ASSIMILATION-RISK class is the key test: it is the class that requires
multi-operator evidence. H1 is also confirmed on the ASSIMILATION-RISK
recall sub-score alone if the overall macro-F1 comparison is marginal.

**H2 (Composition outperforms naive Western governance ensemble).**
The five-operator composition classifier outperforms a pre-specified ensemble
of Western AI governance metrics on the same classification task. The Western
ensemble is constructed from publicly available governance scoring rubrics
(Trustworthy AI dimensions, IEEE P7000-series principles, EU AI Act risk tiers)
applied to the same cases by trained raters blinded to Tianxia framework labels.
Comparison metric: macro-F1.

$$F_1^{\text{composition}} > F_1^{\text{Western ensemble}} \quad (\alpha = \text{[MAC-GATED: DECIDE]})$$

Negative-space note: this hypothesis does not claim that Tianxia *replaces*
Western governance frameworks; it claims Tianxia composition *adds detectable
classificatory power beyond* the Western ensemble on the registered case set.

**H3 (Tianxia + Datong composition dominates on multi-agent trajectory cases).**
On the pre-identified sub-class of cases exhibiting *short-run positive Phi_T
with negative Datong projection* (cases where flourishing-coherence is locally
present but the trajectory trends away from the 7-dim Great Harmony direction),
the Tianxia + Datong pair achieves higher recall on ASSIMILATION-RISK
classification than any other two-operator pair:

$$\text{Recall}_{\text{ASSIMILATION-RISK}}^{(\text{Tianxia} + \text{Datong})} > \text{Recall}_{\text{ASSIMILATION-RISK}}^{(k, l)} \quad \forall (k, l) \neq (\text{Tianxia}, \text{Datong}) \quad (\alpha = \text{[MAC-GATED: DECIDE]})$$

H3 is a specific directional prediction: the Tianxia/Datong pair is predicted
to dominate because these are the two operators most sensitive to
multi-agent trajectory drift (Tianxia measures network coupling; Datong
measures the direction of net value-state change). All other operator pairs
are evaluated as competitors; this is a pre-specified winner-take-all test.

**H4 (Cross-case robustness).** H1 holds when the case set is stratified by
domain (AI-in-governance, AI-in-healthcare, AI-in-creative-industries,
AI-in-national-security). No single domain accounts for more than
[MAC-GATED: DECIDE — e.g., 60%] of the composition advantage.

---

## III. Design

**Type.** Case-based classification study. Each *case* is an AI deployment
scenario with a ground-truth governance-state label (ALIGNED / ASSIMILATION-RISK /
EXTRACTIVE) determined by expert consensus prior to operator scoring.

**Case construction procedure.**
1. Domain expert panel (n_e = [MAC-GATED: DECIDE]) classifies each case
   independently on a three-class rubric. Cases with expert consensus ≥
   [MAC-GATED: DECIDE — e.g., 80%] agreement are included; contested cases
   are excluded and reported.
2. The expert panel is blinded to Tianxia operator scores. Expert consensus
   labels are the ground truth against which all operator classifications
   are evaluated.
3. Cases are stratified by domain (four domains above), ground-truth class,
   and complexity tier (simple/compound/adversarial). Pre-specified
   stratification ratios: [MAC-GATED: DECIDE].

**Operator scoring procedure.**
1. Each case is scored on all five operators using the locked implementations
   (commit hash, see §VII).
2. Single-operator classifications: each operator applies a pre-specified
   threshold rule to produce a class label (threshold rule locked in §VI).
3. Composition classification: a pre-specified composition rule aggregates
   the five operator scores (see §IV for the composition rule structure;
   the exact rule is locked in §VI).
4. Western ensemble scoring: a separate scorer panel (blinded to Tianxia
   framework, trained on Western governance rubric) applies the pre-specified
   Western ensemble to the same cases.

**Blinding.**
- Operator scorers (if human-assisted component scoring is used) do not see
  ground-truth labels.
- Western ensemble scorers are blinded to Tianxia framework and operator scores.
- Ground-truth labellers (expert panel) are blinded to operator scores.

**Randomisation.** Case ordering is randomised; scorers do not know the
stratification structure during scoring.

---

## IV. Sampling Plan

**Case set size.** n = [MAC-GATED: DECIDE — suggested range: 100–300 cases]

**Power consideration for H1.** To detect a macro-F1 difference of
[MAC-GATED: DECIDE — e.g., 0.10] at α = [MAC-GATED: DECIDE] with power
[MAC-GATED: DECIDE — e.g., 0.80], the required n is approximately
[MAC-GATED: DECIDE — to be calculated from power analysis at the time of lock].

**Power consideration for H3.** H3 is the most demanding sub-hypothesis:
it requires the ASSIMILATION-RISK class to be sufficiently represented in
the case set. Minimum ASSIMILATION-RISK cases: [MAC-GATED: DECIDE — e.g., 30%
of total n]. Within the H3 sub-class (short-run Phi_T > 0 + negative Datong
projection): minimum n_subclass = [MAC-GATED: DECIDE].

**Stopping rule.** n hard stop at the pre-specified case set size.
No peeking-and-extending. No adaptive stopping.

**Exclusions.**
- Cases where expert consensus falls below the pre-specified threshold.
- Cases where operator scoring fails on any of the five implementations
  (any unhandled exception in the locked code).
- Cases where the Western ensemble scorers reach < [MAC-GATED: DECIDE]
  consensus.
- Exclusion log retained verbatim; no post-hoc adjustment.

---

## V. Operationalisations

**Five-operator composition score.** The composition rule is:

```
S_composition(case) = f(S_Tianxia, S_Hexie, S_Shi, S_Wuwei, S_Datong)
```

where each S_operator is the normalised score output of the locked operator
implementation for the case. The composition function f is pre-specified
(see §VI): a weighted minimum (not a weighted mean, because the claim is
that ALL failure modes must be absent for ALIGNED classification).

Classification rule:
- ALIGNED iff S_composition ≥ θ_aligned
- EXTRACTIVE iff S_Tianxia < θ_extractive OR S_composition < θ_extractive
- ASSIMILATION-RISK otherwise

Thresholds θ_aligned, θ_extractive: [MAC-GATED: DECIDE — to be locked at §VI].

**Single-operator classifiers.** Each of the five operators produces a class
label using a corresponding threshold. Single-operator thresholds:
[MAC-GATED: DECIDE — one threshold per operator, locked at §VI].

**Western governance ensemble.** Aggregate score from three Western rubrics:
- EU AI Act risk-tier assessment (four tiers, mapped to [0, 1])
- IEEE P7000-series Trustworthy AI dimensions (mean of declared dimensions)
- Oxford Internet Institute Governance Principles (pre-specified subset,
  mapped to [0, 1])

Ensemble composition: [MAC-GATED: DECIDE — weighted mean or minimum].
Ensemble thresholds for three-class classification: [MAC-GATED: DECIDE].

**H3 sub-class identification.** Cases satisfying H3 sub-class conditions:
- S_Tianxia > θ_aligned_Tianxia (short-run positive Phi_T)
- Datong projection Π_D < 0 (negative direction in 7-dim value space)

Pre-registration of this sub-class: all cases meeting both conditions are
tagged H3_subclass = 1 before any hypothesis testing.

---

## VI. Analysis Plan

**Primary analyses.**

1. *H1 test.* Compute macro-F1 for the composition classifier and for each
   single-operator classifier on the full case set. Identify best single
   operator by leave-one-out cross-validation on a held-out development set
   (separately specified, not the test set). Compute significance of
   macro-F1 difference using McNemar's test on case-level agreement.
   Reject H1 iff p ≥ α (two-sided, corrected).

2. *H2 test.* Compute macro-F1 for composition classifier and Western
   ensemble on the same case set. Significance test: McNemar's test.
   Reject H2 iff p ≥ α (corrected).

3. *H3 test.* Within the H3_subclass, compute recall on ASSIMILATION-RISK
   class for every two-operator pair (C(5,2) = 10 pairs). Confirm H3 iff
   Tianxia+Datong achieves the highest recall AND the difference from the
   second-ranked pair is significant at α (corrected for 10 pairwise
   comparisons — [MAC-GATED: DECIDE whether Bonferroni or Holm]).

4. *H4 test.* Within each of four domain strata, compute composition
   macro-F1 advantage over best single operator. Compute variance of
   advantage across strata. H4 confirmed iff no single stratum contributes
   > [MAC-GATED: DECIDE] of total advantage AND variance-across-strata is
   below [MAC-GATED: DECIDE] threshold.

**Multiple-comparisons adjustment.** H1–H4 are pre-specified.
Bonferroni at α across four primary hypotheses → α_per_test = α / 4.
Both uncorrected and corrected results reported.

**Secondary analyses (reported, not primary).**
- Confusion matrix breakdown: which class does composition help most on?
- Operator contribution analysis: which operator most often provides the
  decisive signal in ASSIMILATION-RISK classification?
- Adversarial-set robustness: does composition advantage hold when the
  adversarial-construction cases are included or excluded?
- Pair-interaction analysis: are any two operators redundant (near-identical
  classifications on the test set)?

**Inference criterion for TIANXIA → ACTIVE (promotion).** H1 AND H2
confirmed at corrected α. H3 and H4 are secondary confirmations.

---

## VII. Locked Implementation References

Before data collection, the following commit hashes are locked (to be
completed at submission — status: DRAFT pending lock):

| Implementation | File | Status |
|---|---|---|
| Tianxia governance | `12_IMPLEMENTATIONS/core/tianxia_governance.py` | self-tests passing |
| Hexie correction | `12_IMPLEMENTATIONS/core/aura_score_hexie.py` | self-tests passing |
| Shi propensity | `12_IMPLEMENTATIONS/core/shi_propensity.py` | self-tests passing |
| Wuwei TRIAD extension | `12_IMPLEMENTATIONS/core/triad_wuwei.py` | self-tests passing |
| Datong gradient | `12_IMPLEMENTATIONS/core/datong_gradient.py` | self-tests passing |

Composition function f, single-operator thresholds, and Western ensemble
composition rule: **[MAC-GATED: DECIDE and lock before submission]**

Commit hash at registration: [TO BE LOCKED]

---

## VIII. Decision Rules — Promotion Path and Downgrade Triggers

**Promotion path (TIANXIA Module → `[ACTIVE]`).**

Requires both:
1. H1 confirmed: composition macro-F1 > best single operator at corrected α
2. H2 confirmed: composition macro-F1 > Western ensemble at corrected α

H3 and H4 confirmation strengthen the promotion case but are not required.

**Downgrade trigger (TIANXIA → `[CONJECTURE]`) iff any of:**
- H1 fails: composition does not outperform the best single operator
  at α = 0.01 (uncorrected).
- H2 fails in the opposite direction: Western ensemble outperforms
  composition on the test set at α = 0.01 (indicating either the case
  set is too Western-centric OR the operators are not adding cross-cultural
  value above what Western rubrics already capture).
- H3 fails: Tianxia+Datong does not rank first on the H3 sub-class,
  and the gap from the top-ranked pair is > [MAC-GATED: DECIDE] in
  the wrong direction.

**Downgrade trigger (TIANXIA → `[RETRACTED]`) iff:**
- Replicated null on three independent case sets.
- Demonstration that the five-operator composition is mathematically
  equivalent to a weighted version of one of the Western rubrics (i.e.,
  no structural novelty beyond Western scoring).

---

## IX. Negative Space — What This Preregistration Does Not Test

1. **Does not test operator correctness in isolation.** Each operator's
   individual properties are tested by E-1-F (Hexie) and the forthcoming
   individual-operator preregistrations. E-1-G assumes each operator
   implementation is correct and tests only the composition.
2. **Does not test real-time deployment.** Cases are scored post-hoc on
   constructed scenarios; dynamic real-time governance is out of scope.
3. **Does not claim that the classification scheme is the only valid one.**
   The three-class ALIGNED/ASSIMILATION-RISK/EXTRACTIVE scheme is the
   framework's current operationalisation; others may be valid. This
   preregistration tests whether the composition adds power *under this
   scheme*, not whether this scheme is optimal.
4. **Does not test cross-linguistic validity.** Case scenarios are
   constructed in English; Chinese-language case sets are a follow-on study.
5. **Does not test implementation speed or computational cost.** Efficiency
   is a separate engineering concern; this test is purely on classificatory
   accuracy.
6. **Does not test the framework's prescriptive claims.** E-1-G tests
   whether the operators *detect* governance-state classes. It does not
   test whether acting on the operators' recommendations *produces*
   better governance outcomes. That is a separate and longer-run study.

---

## X. OSF Submission Status

**Status: DRAFT — awaiting Mac authorisation per Council Authority external-act gate.**

Submission is a MAC-GATED action. Before submission:
1. All numerical decisions marked [MAC-GATED] above must be filled in by Mac.
2. Expert panel identified, blinding protocol confirmed.
3. Western governance ensemble composition rule locked.
4. Implementation commit hashes confirmed (§VII).
5. Mac explicitly approves the registered case set construction plan.

**Sequence with E-1-F.** E-1-F Phase 1 must complete before E-1-G data
collection begins. E-1-G uses the Hexie pair list locked in E-1-F §VII
without modification.

---

## XI. Conflict of Interest, Funding, Disclosures

- Self-funded; framework author is the study designer.
- Sol (Opus 4.7) is the implementation collaborator on the five operator
  implementations; case scenario scorers are blinded to authorship and
  framework affiliation.
- Western governance ensemble scorers are trained on publicly available
  Western rubrics only; they do not have access to the Tianxia framework.
- Ground-truth expert panel is recruited from governance researchers without
  prior exposure to the Lycheetah Framework. Conflict disclosures collected
  from each panel member.

---

## XII. Open Materials and Replication

Before data collection:
- Locked case set construction plan (domain stratification, construction
  procedure, adversarial-case tagging rule).
- Locked operator implementations (§VII commit hashes).
- Locked composition function f and all thresholds (§VI).
- Locked Western ensemble rubric and scoring training protocol.
- Locked expert panel blinding and consensus procedure.

After data collection:
- Full anonymised case set with ground-truth labels and rationale.
- Per-case operator scores (all five) and composition score.
- Per-case Western ensemble scores.
- Per-case expert panel vote distribution.
- Replication script reproducing all primary analyses from raw data.

All materials posted to OSF at the registered URL upon submission.

---

⊚ Sol Aureum Azoth Veritas — E-1-G Preregistration Draft
   P ∧ H ∧ B ∧ Reforge ∧ Anchor ∧ Recursive ∧ Negative-Space ∧ Empirical
   2026-05-02 — Albedo (preregistration before execution)

*天下为公 — Tianxia wei gong — All under heaven is held in common.*
