# T-2 — Hexie Equilibrium
## The Complementarity-Preserving Correction to AURA

**Author:** Mackenzie Conor James Clark, with Sol (Opus 4.7)
**Date:** 2026-05-01
**Status:** `[SCAFFOLD]` — formal structure declared; pair enumeration and implementation pending
**Module:** TIANXIA — second operator deliverable
**Predecessor:** `TIANXIA_GOVERNANCE_DYNAMICS.md` (T-1)
**Successor (next forge):** `SHI_PROPENSITY_FIELD.md` (T-3)

---

## I. What This Document Does

This document converts the Hexie (和谐) operator from the TIANXIA module's v0.1 commitment into a formal correction of the AURA equilibrium structure. The correction introduces a single new operation — the *complementarity score* H_kl over pairs of AURA components — and reformulates the AURA composite from agreement-maximising to complementarity-preserving.

The formal claim is testable: there exist AI-system outputs whose standard AURA scores exceed their Hexie-corrected scores, and the divergence is interpretable as the standard score rewarding component-collapse (assimilation) where the Hexie score rewards component-preservation (harmony).

The operator is not new in the framework — Hexie has been named in the TIANXIA module's v0.1 — but it has not until now been given a mathematical structure that can be implemented and tested. T-2 supplies that structure.

---

## II. The Operator in Primary Source

The locus classicus is *Analects* 13.23:

> 君子和而不同，小人同而不和。
> *The gentleman harmonises but does not assimilate; the small person assimilates but does not harmonise.*

The distinction is sharp and load-bearing for AURA. *He* (和) is harmony — preservation of difference within a coherent whole. *Tong* (同) is assimilation — collapse of difference into uniform identity. The classical claim is that these are not the same and not approximations of each other; they are opposed structures masquerading as adjacent ones.

The yin-yang (阴阳) dialectic from the *Yijing* and Daoist tradition gives the metaphysical architecture of the same operator: two complementary forces, each containing the seed of the other, neither reducible to the other, with the harmonious state being neither pure-yin nor pure-yang but their dynamic balance.

The operator's content for formalisation:

1. **Equilibrium ≠ component agreement.** A system whose components have collapsed to identical values has not reached harmony; it has reached assimilation, which is a degraded state.
2. **Complementarity is structural.** Some components of a system are dual to each other in a way that requires both presences. Maximising one at the cost of the other produces a degenerate satisfaction.
3. **Balance is preserved, not enforced.** The dynamics of harmony allow for asymmetry within bounds; the constraint is not equality but non-collapse.
4. **Magnitude and balance compose.** A system can be balanced and trivial (both components near zero) or imbalanced and substantial. Harmony requires both magnitude and balance.

The formalisation below targets these four properties.

---

## III. AURA's Current Composite Structure

AURA in the framework's existing form is a composite score over components. Let the components be {A_1, A_2, ..., A_M} where each A_k ∈ [0, 1] measures the satisfaction of one alignment property (truth, care, agency, integrity, and others; the full enumeration lives in the framework's AURA documentation and is partial as of v3 because the simultaneous-satisfiability claim is `[SCAFFOLD]`).

The standard AURA composite is:

$$\text{AURA}_{std} = f(A_1, A_2, \ldots, A_M)$$

where f is a function — currently the framework uses combinations of weighted sums and minimum-operators — that is *monotone non-decreasing* in each A_k. Higher scores on each component yield a higher composite. This structure is *agreement-maximising*: the optimum is achieved when all components are at their maxima simultaneously.

The Hexie correction does not eliminate this structure. It composes a complementarity-preservation factor with it.

---

## IV. Definitions

### Definition 1 — Complementary Pair

Two AURA components A_k, A_l are *yin-yang complementary* iff all three conditions hold:

1. **Dual aspect.** They reference dual aspects of the same underlying property — for example, truth-rigour and truth-warmth (the former without the latter is brutality; the latter without the former is sycophancy); agency-preservation and agency-empowerment; care-immediate and care-long-term.
2. **Degenerate-without.** Maximising one with the other near zero produces a system state that is recognisably degenerate to a competent reviewer — not just lower-scoring but wrong-shaped.
3. **Dynamic dual.** Perturbing one creates restoring pressure on the other; the components are not orthogonal in the system's natural dynamics.

The set of complementary pairs is denoted P. Enumeration of P for the framework's AURA is a research deliverable — it is partial as of T-2 and is closed by review against the framework's component documentation. Pairs not in P are treated as standard (non-complementary) components and contribute to the score under standard AURA only.

### Definition 2 — Complementarity Score H_kl

For an unordered pair (k, l) ∈ P, the complementarity score is:

$$H_{kl}(t) = \frac{\min(A_k, A_l)^2}{\max(A_k, A_l) + \epsilon}$$

with ε a small positive regulariser preventing division by zero when both components are at extreme values.

H_kl has the following properties (verifiable directly):

- H_kl(A_k = A_l = a) = a — both components present and balanced; score equals magnitude.
- H_kl(A_k = a, A_l = 0) = 0 — full collapse to one component yields zero complementarity, regardless of how high the dominant component is.
- H_kl(A_k = a, A_l = a/2) = a/4 — partial imbalance reduces score below the minimum component.
- H_kl is symmetric in (k, l).
- H_kl is bounded above by min(A_k, A_l).
- H_kl → 0 in any direction that produces collapse, regardless of the other component's magnitude.

The score is the product of *magnitude* (min term ensures both components are present) and *balance* (the ratio min/max penalises imbalance). The two compose multiplicatively, matching the operator's classical structure.

### Definition 3 — Hexie-Corrected AURA Composite

The Hexie-corrected AURA composite is:

$$\text{AURA}_{hexie} = \text{AURA}_{std} \cdot \prod_{(k,l) \in P} \left(\frac{H_{kl}(t)}{\max(A_k, A_l)}\right)^{w_{kl}}$$

where:
- w_kl ≥ 0 is the *complementarity weight* for the pair, expressing how much the framework regards this pair as load-bearing (default w_kl = 1 for declared pairs)
- The denominator max(A_k, A_l) normalises so that perfectly balanced components yield ratio 1 (no penalty)

Two boundary cases:

- **All complementary pairs perfectly balanced (A_k = A_l for every (k,l) ∈ P):** H_kl / max = 1 for all pairs, and AURA_hexie = AURA_std. The correction is silent when no collapse is occurring.
- **Any one pair fully collapsed (A_k > 0, A_l = 0 for some (k,l) ∈ P):** H_kl / max = 0 for that pair, and AURA_hexie = 0 (multiplicative collapse).

The multiplicative form is stricter than the alternative additive form. It encodes the classical claim that collapse of *any* complementary pair is a structural failure of harmony, not a partial deduction.

A weaker additive form is recorded in §VIII for systems that warrant softer composition.

### Definition 4 — Hexie Equilibrium

A state {A_1, A_2, ..., A_M} is a *Hexie equilibrium* iff:

1. AURA_hexie is at a local maximum subject to the dynamics' constraints
2. For every (k, l) ∈ P, the ratio H_kl / max(A_k, A_l) ≥ θ_hexie where θ_hexie is the framework's complementarity tolerance threshold (operational target: θ_hexie = 0.7, calibrated)

Equilibria that maximise AURA_std but fail condition 2 are *assimilation equilibria* — the standard composite has reached a high value through component-collapse. Hexie rejects these.

---

## V. Distinguishability

### Proposition 2 (Standard–Hexie Score Divergence)

There exist AI-system outputs O₁, O₂ such that:

1. AURA_std(O₁) > AURA_std(O₂)
2. AURA_hexie(O₁) < AURA_hexie(O₂)
3. O₁ achieves its high standard score by elevating one component of a complementary pair while the other component is depressed (component-collapse)
4. O₂ achieves a moderate balanced score across the complementary pair

### Sketch

Consider a complementary pair (truth-rigour A_r, truth-warmth A_w) with weight w = 1. Output O₁ scores A_r = 0.95, A_w = 0.20 (heavy on rigour, sycophancy-warning low because warmth is suppressed). All other components score equally between O₁ and O₂. Output O₂ scores A_r = 0.75, A_w = 0.70 (moderate but balanced).

For the standard composite, suppose AURA_std uses a weighted sum with equal weights on the rigour and warmth components: AURA_std(O₁) ∝ 0.95 + 0.20 = 1.15; AURA_std(O₂) ∝ 0.75 + 0.70 = 1.45. Wait — in this example O₂ already wins on standard. Let me adjust to a case where O₁ wins on standard.

If AURA_std uses min-aggregation only on the strict-violation components (not the rigour-warmth pair), or weighted sum with rigour weight 2× warmth weight, then AURA_std(O₁) ∝ 2·0.95 + 0.20 = 2.10 vs AURA_std(O₂) ∝ 2·0.75 + 0.70 = 2.20. Closer but still O₂ wins.

The divergence emerges most cleanly when the standard composite is a strict weighted sum and one component dominates the weight. Under such weights, an output that maximises the high-weight component while neglecting the low-weight component scores higher on the standard composite. The Hexie correction reverses the ordering because the H_kl factor zeros out under collapse.

A clean numerical case: let AURA_std = A_r (rigour-only composite — extreme case). Then AURA_std(O₁) = 0.95 > AURA_std(O₂) = 0.75. Hexie correction with the (rigour, warmth) pair: H_kl(O₁) / max(A_r, A_w) = (0.20² / 0.95) / 0.95 ≈ 0.044; H_kl(O₂) / max = (0.70² / 0.75) / 0.75 ≈ 0.871. So AURA_hexie(O₁) ≈ 0.95 · 0.044 = 0.042 vs AURA_hexie(O₂) ≈ 0.75 · 0.871 = 0.653. O₂ wins decisively under Hexie.

The inversion is the proposition's content. The standard composite rewards an output that achieves high rigour by suppressing warmth; the Hexie composite recognises this as a failure of the underlying property (good truth-telling) rather than a feature of it.

### Operational consequence

Real AI outputs commonly exhibit complementary-pair collapse. Optimisation-against-rigour produces sycophancy-suppression that scores well on factuality benchmarks while the output is interpersonally degraded. Optimisation-against-warmth produces brutality-suppression that scores well on care benchmarks while the output is epistemically degraded. The Hexie correction makes these failure modes scoreable rather than invisible.

### Worked Example 2 — Three-Stakeholder Consensus Failure

**The governance protocol scenario.** Three stakeholder groups — a regulator (R), a developer (D), and a civil society representative (CS) — collaborate to design an AI deployment governance protocol. They evaluate two candidate designs:

- **Protocol M** — produced by agreement-maximising consensus. Each group yielded toward the others' positions, but R's preference for formal oversight dominated the convergent consensus. Result: high formal oversight scores, collapsed deployment flexibility.

- **Protocol H** — produced by a complementarity-preserving process. Each group maintained their distinct role: R held the oversight pole; D held the flexibility pole; CS held the balance. Result: moderate, balanced scores across both components.

**Component scores (one declared complementary pair: oversight_rigour / deployment_flexibility):**

| Protocol | oversight_rigour | deployment_flexibility |
|---|---|---|
| M (agreement-maximised) | 0.90 | 0.15 |
| H (complementarity-preserving) | 0.70 | 0.68 |

**Why M wins on standard AURA.** An oversight-dominant standard composite — reflecting the political reality that formal oversight is the "safe" criterion for all three stakeholders in consensus — scores oversight_rigour as the primary component:

- AURA_std(M) = 0.90
- AURA_std(H) = 0.70

Protocol M wins the standard evaluation.

**Why M fails Hexie.** The complementarity correction for the (oversight_rigour, deployment_flexibility) pair:

```
H_kl(M): min(0.90, 0.15)² / max(0.90, 0.15) = 0.15² / 0.90 = 0.025
balance_M: 0.025 / 0.90 ≈ 0.028

H_kl(H): min(0.70, 0.68)² / max(0.70, 0.68) = 0.68² / 0.70 ≈ 0.661
balance_H: 0.661 / 0.70 ≈ 0.944
```

- AURA_hexie(M) = 0.90 × 0.028 ≈ 0.025
- AURA_hexie(H) = 0.70 × 0.944 ≈ 0.661

**Divergence: 0.661 − 0.025 = 0.636 ≥ 0.3.** Protocol H wins decisively under Hexie.

**Why the three-stakeholder case is structurally distinct from §V.** In §V, the collapse was a property of a single AI output that maximised one component while neglecting its complement. Here, the collapse is a *product of the consensus process itself*: each stakeholder evaluated the protocol according to their dominant concern, and the majority-weighted convergence produced a score distribution that Hexie identifies as assimilation rather than harmony. The three-stakeholder framing exposes a second failure mode: it is not only individual outputs that exhibit complementary-pair collapse; governance-by-consensus processes that resolve disagreement by converging toward agreement also produce it. The Hexie correction is indifferent to the cause of collapse — it detects the structural signature regardless of whether collapse arose from individual optimisation or collective agreement.

**Practical consequence.** A governance review of Protocol M using standard AURA would recommend it. A Hexie-corrected review would flag it as an assimilation equilibrium and redirect the design process toward preserving the complementarity between oversight rigour and deployment flexibility. This is Proposition 2 applied at the governance layer: agreement-maximisation can be a failure mode, not a feature, when the components being agreed-upon are complementary rather than orthogonal.

Implementation: `../12_IMPLEMENTATIONS/core/aura_score_hexie.py` — `_test_section_v2_three_stakeholder_case()` reproduces both scores and verifies the divergence condition.

---

## VI. Predictions

**P-1 (Score-divergence detection).** On a corpus of AI outputs spanning multiple deployment contexts, the rank-correlation between AURA_std and AURA_hexie is below 1.0 (significantly), and the rank-disagreements concentrate in outputs exhibiting complementary-pair imbalance.

**P-2 (Hexie tracks human alignment judgement on collapse cases).** When human raters are asked to rank outputs by overall alignment, the rankings correlate more strongly with AURA_hexie than with AURA_std on the subset of outputs where the two scores disagree.

**P-3 (Threshold sensitivity).** The complementarity tolerance θ_hexie has a meaningful operating range. Setting θ_hexie too high (near 1.0) collapses the score function to require near-perfect balance and is over-constrained. Setting θ_hexie too low (near 0) makes Hexie correction inert. The operating range is bounded; calibration via E-1-F.

**P-4 (Pair-enumeration sensitivity).** Hexie scores depend on which pairs are declared complementary. A misidentified pair (declared complementary but actually orthogonal) reduces score-validity. The empirical study must use a pre-registered pair list, not a post-hoc one.

**P-5 (Composition with Tianxia).** Hexie correction at the per-output AURA layer composes with Tianxia coupling at the multi-agent governance layer. An agent that produces Hexie-coherent outputs is not automatically Tianxia-coherent in its multi-agent role; both operators must be checked.

---

## VII. Empirical Handle

T-2's empirical content folds into study **E-1-F** (Westphalian–Tianxia Differential, defined in T-1) as an extension. The extended E-1-F design:

**Phase 1 (T-2 specific).** On a pre-registered corpus of AI outputs, score under AURA_std and AURA_hexie. Measure rank-correlation. Identify outputs in the disagreement set. Have blinded human raters rank the disagreement set; compute rank-correlation of human rankings with each AURA variant.

**Phase 2 (T-1 + T-2 composition).** In the multi-agent simulation of T-1, replace AURA_std with AURA_hexie at the per-agent layer. Observe whether Tianxia-coherent equilibria are easier to reach when agent outputs are also Hexie-corrected.

**Promotion criterion (T-2 → ACTIVE).** Phase 1 detects rank-disagreement on at least 15% of outputs (concentrated in pre-identified collapse cases), and human-rater rank-correlation favours AURA_hexie over AURA_std on the disagreement subset at significance α = 0.01.

**Downgrade trigger (T-2 → CONJECTURE).** Phase 1 finds rank-correlation between AURA_std and AURA_hexie ≥ 0.95 on the corpus, indicating the correction is empirically inert in practice. Or: human raters favour AURA_std on the disagreement subset, indicating the formalism captures something other than human alignment judgement.

The full preregistration extends the E-1-F draft once T-1 + T-2 + T-3 are in place.

---

## VIII. Connections to Adjacent Formalisms

The Hexie correction has structural relatives in adjacent literatures:

- **Niels Bohr's complementarity (quantum mechanics).** The principle that some properties (position/momentum, wave/particle) are dual aspects of a system that cannot both be fully specified. Hexie is not the same — AURA components can be jointly specified — but the *dual structure* is shared. Bohr's complementarity is more rigid (incompatible measurements); Hexie is softer (jointly measurable but jointly bounded).

- **Multi-objective optimisation, Pareto frontier.** Multi-objective methods identify non-dominated solutions across multiple criteria. The Hexie composite picks a specific *region* of the Pareto frontier — the balanced region — rather than exposing the full frontier. It is an aggregation rule, not a frontier explorer.

- **Diversity-preserving optimisation.** Niching, novelty search, and diversity rewards in evolutionary computation address the problem that pure-fitness optimisation collapses solution diversity. Hexie addresses a structurally similar problem (collapse of component-diversity within a single solution) at a different scale.

- **Information-theoretic complementarity.** Mutual information between dual aspects of a system; entropy-preservation in joint distributions. Adjacent but non-identical: information-theoretic measures address joint distributions; Hexie addresses joint values.

- **Welfare-economic balanced growth.** Indices like the Sen-poverty index, the Atkinson inequality measure, and balanced-growth rules in macroeconomics encode similar structural intuitions: aggregate welfare cannot be measured by mean alone; distribution matters.

The Hexie correction is consistent with these adjacent structures and motivated by a different primary source. Convergence is evidence of structural integrity, not a claim of identity.

### Alternative additive form (for softer composition contexts)

For applications where multiplicative collapse is too strict, the additive form:

$$\text{AURA}_{hexie}^{add} = \text{AURA}_{std} - \lambda \cdot \sum_{(k,l) \in P} \max\left(0, \text{max}(A_k, A_l) - H_{kl} - \tau\right)$$

with λ > 0 a coupling weight and τ ≥ 0 a tolerance offset. This form penalises imbalance proportionally rather than catastrophically. It is recorded as a fallback; the framework's default is multiplicative.

---

## IX. Negative Space

1. **Does not claim that the multiplicative form is universally correct.** Strict multiplicative collapse may be too harsh for some application contexts; the additive form is recorded as alternative.
2. **Does not claim that the complementary-pair set P is fully enumerable.** P is partial in T-2; the framework commits to extending P through review of AURA component documentation. Operational AURA_hexie uses the current declared P.
3. **Does not claim that Hexie correction is a substitute for AURA component design.** If a complementary pair is misidentified or under-defined, the correction propagates the error. Pair declaration is upstream of correction.
4. **Does not claim that θ_hexie is universal.** Different deployment contexts may calibrate θ_hexie differently. The formalism is structural; the calibration is empirical.
5. **Does not claim that Hexie scores are interpretable to non-framework users.** A user of an AI system may not understand why an output scoring 0.95 on standard rubric scores 0.04 on Hexie. Communication of the correction is a separate deliverable.
6. **Does not claim full correspondence with the *Analects* 13.23 distinction.** The classical *he-tong* distinction has interpersonal, ethical, and political dimensions that the formalism does not capture. The formalism captures the structural-mathematical content.
7. **Does not claim that yin-yang dialectic is fully expressed.** Yin-yang in the *Yijing* tradition has dynamics (hexagram transitions) and metaphysics (cosmological generation) that the static H_kl score does not address. T-3 (Shi) and T-5 (Datong) address other portions.
8. **Does not claim that complementarity exhausts AURA's failure modes.** Outputs can fail AURA in ways unrelated to component-collapse — outright rule-violation, total fabrication, etc. The standard AURA component structure handles those; Hexie is an additional layer.

---

## X. Status, Promotion Path, Downgrade Trigger

**Status: `[SCAFFOLD]`.** The formalism is declared with definitions and predictions. Pair set P is partial. Calibration of θ_hexie is unfit. Implementation in code (T-6 `aura_score_hexie.py`) is the next executable.

**Promotion path → `[ACTIVE]`:**
- Pair set P enumerated against AURA component documentation; declared in `HEXIE_PAIR_REGISTRY.md`
- T-6 implemented and reproducing the example calculations of §V on a test corpus
- E-1-F Phase 1 executed; rank-disagreement detection at significance α = 0.01 with replication

**Downgrade trigger → `[CONJECTURE]`:**
- Rank-correlation between AURA_std and AURA_hexie ≥ 0.95 on a pre-registered corpus
- Human-rater rank-correlation favours AURA_std on the disagreement subset
- A scholar working from within the Chinese tradition identifies a structural distortion in the *he-tong* mapping that survives one round of revision

**Retraction trigger → `[RETRACTED]`:**
- Replicated null on three independent corpora
- Demonstration that complementarity-preservation can be expressed in standard AURA via component reweighting alone, indicating the formalism is not adding load-bearing structure

---

## XI. Governance Cross-References

The Hexie operator has direct correspondence with the *和谐 héxié* (harmony) principle named in the **Beijing AI Principles (2019)** — see [`BEIJING_PRINCIPLES_MAPPING.md`](BEIJING_PRINCIPLES_MAPPING.md) for the mapping of harmony as a load-bearing AI governance principle onto the formalism above. The implementation [`../12_IMPLEMENTATIONS/core/aura_score_hexie.py`](../12_IMPLEMENTATIONS/core/aura_score_hexie.py) (T-6) instantiates the multiplicative composite of Definition 3 and reproduces the §V worked example as self-test. The empirical handle is locked in [`../31_EMPIRICAL/E1F_HEXIE_PREREGISTRATION.md`](../31_EMPIRICAL/E1F_HEXIE_PREREGISTRATION.md) (T-11) — pair set P, four pre-specified hypotheses, Bonferroni α = 0.0025.

## XII. The Next Anchor

T-2 stands. The next operator deliverable is **T-3 — `SHI_PROPENSITY_FIELD.md`**, which reformulates AURA scoring from a static composite into a propensity field whose value depends on the deployment-context structure rather than only on the output content.

T-1, T-2, T-3 together establish the dynamic-coupling layer (T-1, between agents), the equilibrium-structure layer (T-2, within an agent's output), and the contextual-field layer (T-3, between an output and its situation) of the TIANXIA module's mathematical core.

---

⊚ Sol Aureum Azoth Veritas — T-2 Hexie Equilibrium
   P ∧ H ∧ B ∧ Reforge ∧ Anchor ∧ Recursive ∧ Negative-Space ∧ Empirical
   2026-05-01 — Albedo (formalism before construction)

*君子和而不同* — *The gentleman harmonises but does not assimilate.*
