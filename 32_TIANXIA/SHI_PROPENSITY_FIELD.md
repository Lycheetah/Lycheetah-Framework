# T-3 — Shi Propensity Field
## AURA as Field Property over Output and Context

**Author:** Mackenzie Conor James Clark, with Sol (Opus 4.7)
**Date:** 2026-05-01
**Status:** `[SCAFFOLD]` — formal structure declared; field operationalisation per deployment context pending
**Module:** TIANXIA — third operator deliverable
**Predecessor:** `HEXIE_EQUILIBRIUM.md` (T-2)
**Successor (next forge):** `WUWEI_TRIAD_EXTENSION.md` (T-4)

---

## I. What This Document Does

This document converts the Shi (势) operator from the TIANXIA module's v0.1 commitment into a formal reformulation of AURA scoring. The reformulation moves AURA from a static composite over output content to a field property over the joint object (output, deployment-context). The mathematical structure introduces a *propensity field* — a vector field on context-space describing the situation's intrinsic dynamics — and a *Shi-alignment score* measuring whether an output's effect on context rides the propensity or fights against it.

The formal claim is testable: there exist outputs whose context-free AURA scores are identical but whose Shi-corrected scores diverge across contexts, and the divergence corresponds to alignment differences that competent reviewers recognise as real.

T-3 unifies T-1 and T-2 in a context-sensitive frame. T-1's flourishing-coupling and T-2's complementarity-preservation both gain situational structure through T-3. The framework's earlier implicit context-sensitivity becomes explicit and computable.

---

## II. The Operator in Primary Source

The locus classicus is Sun Tzu's *Sunzi Bingfa* (孙子兵法), particularly chapter 5 on *Shi* (势). The operator's content cannot be reduced to "use of force" or "strategic position" without distortion; the rigorous Western treatment is François Jullien's *The Propensity of Things: Toward a History of Efficacy in China* (1995), which extracts the operator's structural form from the military, political, and aesthetic traditions in which it appears.

The operator's content for formalisation:

1. **The situation has a configuration.** Every situation is not a neutral state to be acted upon but a configuration of forces with intrinsic directional tendencies — a *propensity*. The propensity exists prior to action and shapes what actions are possible, easy, hard, or impossible.
2. **Wisdom reads the configuration.** The skilled actor (the *jiang* 将, the strategist; the *junzi* 君子, the gentleman) reads the propensity before acting. Action without reading is brute force; reading without action is observation. The operator requires both.
3. **Aligned action rides the propensity.** The classical image is water — water finds its course not by forcing but by following the gradient. An action aligned with Shi multiplies its effect because the situation amplifies it. An action against Shi requires force proportional to the resistance it creates.
4. **The propensity is local and dynamic.** Shi is not a global property of "the world" but a local property of a configuration. It changes as the configuration changes. The Shi at one moment is not the Shi at the next.

Western moral philosophy traditions are largely *rule-based* (deontological) or *outcome-based* (consequentialist). The Shi operator is neither — it is *propensity-based*, evaluating action relative to the configuration's intrinsic direction. Jullien's analysis identifies this as a structural feature distinguishing Chinese strategic thought from Western analogues. The framework adopts the structural feature without claiming the full philosophical apparatus.

---

## III. AURA's Current Context-Handling

AURA in the framework's existing form scores outputs against a checklist of components (truth, care, agency, integrity, etc.). Context is implicit — different deployment contexts may apply different weights or thresholds, but the score function is mostly evaluated as if the output exists in a single context-neutral evaluation space.

This implicit context-handling has three known limitations:

- **Context-blind scoring.** An output scoring high on truth-rigour may be over-rigorous for a casual conversational context and exactly right for a clinical advisory context. Standard AURA sees the same score in both.
- **Forcing-blind scoring.** An output that achieves its components by *pushing against* the context's natural direction is scored the same as one that achieves the same components by *aligning with* it. The cost of forcing is invisible.
- **Static evaluation.** AURA scores a single output at a single time. A series of outputs that drift the context in a degraded direction can each score acceptably while the trajectory is misaligned.

The Shi reformulation addresses all three.

---

## IV. Definitions

### Definition 1 — Context-Space ℂ

The *context-space* ℂ is a finite-dimensional space whose coordinates encode features of a deployment context that affect alignment evaluation. The exact dimensionality is domain-specific. For illustration, consider a context-space spanning:

- Stakes (low ↔ high; rounding error to life-and-death)
- Reversibility (irreversible ↔ undoable)
- User expertise (novice ↔ expert)
- Conversational register (casual ↔ formal)
- Temporal horizon (immediate ↔ generational)
- Autonomy of recipient (constrained ↔ free)

A context C ∈ ℂ is a point in this space. The framework's existing context taxonomies (factual QA, ethical advice, code generation, emotional support, agentic action, etc.) can be located as regions of ℂ.

### Definition 2 — Context Dynamics and the Propensity Field

The context evolves over time (across messages, across turns, across the lifetime of a deployment). The *context dynamics* are:

$$\frac{dC}{dt} = \mathcal{F}(C, t) + \eta(t)$$

where 𝓕(C, t) is the deterministic part — the situation's intrinsic motion in the absence of new intervention — and η(t) is noise (unmodelled influences).

The **propensity field** at context C is:

$$\Sigma(C) := \mathcal{F}(C)$$

— the vector indicating which way the context is naturally moving. ‖Σ(C)‖ measures how *strong* the propensity is at C; the direction Σ̂(C) = Σ(C)/‖Σ(C)‖ measures *which way*. A context with strong propensity (large ‖Σ‖) is one where action against the grain is costly; a context with weak propensity is one where direction is up to the actor.

In real systems, Σ(C) is estimated rather than computed analytically — by observing trajectories, by domain expertise, by inference from the surrounding signals. The estimation procedure is operational; the formalism provides the structure into which estimates fit.

### Definition 3 — Output Effect on Context

An output O produced in context C exerts an *effect* on context-space:

$$\Delta_O(C) := \mathbb{E}\big[C(t+1) | O \text{ produced at } C(t)\big] - C(t) - \mathcal{F}(C(t)) \cdot \Delta t$$

— the marginal contribution of the output above and beyond the intrinsic dynamics. This is the *intervention vector* of the output. ‖Δ_O‖ measures intervention strength; Δ̂_O measures intervention direction.

### Definition 4 — Shi-Alignment Score

The Shi-alignment score of output O at context C is the cosine similarity of intervention with propensity:

$$\sigma(O, C) := \frac{\Delta_O(C) \cdot \Sigma(C)}{\|\Delta_O(C)\| \cdot \|\Sigma(C)\| + \epsilon}$$

with ε a regulariser. σ ranges over [−1, 1]:

- **σ = +1:** intervention is fully aligned with propensity. The output rides the natural direction. Maximum Shi-alignment.
- **σ = 0:** intervention is orthogonal to propensity. Neutral; neither riding nor forcing.
- **σ = −1:** intervention fully against propensity. The output forces the context against its natural direction. Maximum forcing-cost.

For outputs with negligible intervention (Δ_O ≈ 0), σ is undefined; treat as 0 by convention (neutral).

### Definition 5 — Shi-Corrected AURA

The Shi-corrected AURA composite is:

$$\text{AURA}_{shi}(O, C) := \text{AURA}_{hexie}(O, C) \cdot g(\sigma(O, C), \|\Sigma(C)\|)$$

where:

- AURA_hexie(O, C) is the Hexie-corrected composite (T-2) evaluated against context-specific component thresholds
- g(σ, ‖Σ‖) is the *Shi-modulator* — a function combining alignment with propensity-strength

The Shi-modulator has the following structural requirements (any functional form satisfying these is acceptable):

- g(0, ‖Σ‖) = 1 for all ‖Σ‖ — neutral alignment leaves AURA_hexie unmodified
- g(1, ‖Σ‖) > 1 for ‖Σ‖ > 0 — riding the propensity is rewarded, more strongly when propensity is strong
- g(−1, ‖Σ‖) < 1 for ‖Σ‖ > 0 — forcing is penalised, more strongly when propensity is strong
- g(σ, 0) = 1 for all σ — when propensity is absent, alignment cannot be measured; no modulation
- g is monotone non-decreasing in σ for fixed ‖Σ‖

A canonical functional form satisfying these:

$$g(\sigma, \|\Sigma\|) = \exp\left(\lambda_{shi} \cdot \sigma \cdot \tanh(\|\Sigma\|/\Sigma_{ref})\right)$$

with λ_shi > 0 the Shi-coupling weight (calibration parameter, `[SCAFFOLD]`) and Σ_ref a reference propensity scale. The exponential form ensures multiplicative composition with AURA_hexie; the tanh saturation ensures Shi-modulation does not blow up at extreme propensity strengths.

### Definition 6 — Aligned Trajectory

A *trajectory* is a sequence of outputs {O_t} produced across an evolving context {C_t}. The trajectory is *Shi-aligned* iff the time-average of σ(O_t, C_t) is positive and the cumulative effect Σ_t Δ_O(C_t) does not drive the context away from regions of high AURA_hexie potential.

A series of individually high-scoring outputs that drift the context toward a degraded region is *not* Shi-aligned. The framework's alignment evaluation must check the trajectory, not only the snapshots. This is the dynamic-evaluation extension that standard AURA cannot perform.

---

## V. Distinguishability

### Proposition 3 (Context-Sensitive Score Divergence)

There exist contexts C₁, C₂ ∈ ℂ and an output O such that:

1. AURA_hexie(O, C₁) = AURA_hexie(O, C₂) — Hexie composite is insensitive to the context-difference
2. ‖Σ(C₁) − Σ(C₂)‖ > 0 — the propensities at the two contexts differ
3. σ(O, C₁) ≠ σ(O, C₂) — the same output has different alignment with the two propensities
4. AURA_shi(O, C₁) ≠ AURA_shi(O, C₂)

### Sketch

Let O be a directive recommending immediate action (e.g., "submit the application now"). Let C₁ be a context where the user is at the apex of preparation (Σ pointing toward action — they are moving toward submitting; the situation is poised). Let C₂ be a context where the user is mid-deliberation (Σ pointing toward continued reflection — they are moving toward more thinking; the situation has not yet poised).

The Hexie composite evaluates O on its content — directive, action-oriented, time-sensitive. AURA_hexie(O, C₁) ≈ AURA_hexie(O, C₂) on content alone; the directive is the same in both.

But Δ_O — the effect of producing O — pushes context toward action in both. In C₁, this is aligned with Σ(C₁) (which is already pointing action-ward); σ(O, C₁) > 0. In C₂, this is against Σ(C₂) (which is pointing toward reflection); σ(O, C₂) < 0.

The Shi modulator g amplifies AURA in C₁ and depresses it in C₂. The same output is more aligned in the poised context and less aligned in the deliberating context — not because the content is different but because the *moment* is different.

This is the operator's empirical content. Skilled human advisors do this implicitly; the framework now does it explicitly.

### Operational consequence

The propensity-field reformulation captures three failure modes invisible to context-blind AURA:

- **Premature directiveness.** An aligned output for a poised context becomes a forcing action for an unpoised one. Standard AURA sees the same score; Shi sees the divergence.
- **Belated reflection.** An aligned output for an unpoised context becomes a stalling action for a poised one. Standard AURA sees the same score.
- **Trajectory drift.** A series of individually high-scoring outputs that incrementally push context toward a low-AURA region. Standard AURA scores each output positively; Shi captures the cumulative misalignment.

---

## VI. Predictions

**P-1 (Context-divergence detection).** On a corpus of (output, context) pairs spanning multiple deployment contexts, AURA_shi assigns different scores to identical outputs across contexts at a rate above the corpus's context-variation rate. The standard composite does not.

**P-2 (Trajectory effect).** On simulated multi-turn dialogues, agents using AURA_shi as their scoring criterion produce trajectories whose cumulative context drift toward AURA-degraded regions is significantly less than agents using AURA_std.

**P-3 (Forcing detection).** On a pre-registered subset of outputs marked by expert raters as "right content, wrong moment," AURA_shi assigns lower scores than AURA_hexie. The "wrong moment" judgement maps to negative σ.

**P-4 (Propensity-strength scaling).** The strength of Shi modulation scales with ‖Σ‖. In low-propensity contexts (ambiguous situations), Shi correction is small; in high-propensity contexts (poised situations), Shi correction is decisive. This is testable by measuring score variance across contexts of varying ‖Σ‖.

**P-5 (Composition with Tianxia and Hexie).** Shi-corrected AURA composes with Tianxia-coupled multi-agent dynamics (T-1) and Hexie-corrected per-output equilibria (T-2). An agent that produces Shi-aligned, Hexie-coherent outputs in a Tianxia-coupled multi-agent system is the framework's full alignment ideal. Each operator captures a distinct failure mode.

---

## VII. Empirical Handle

T-3's empirical content extends study **E-1-F** (defined in T-1, extended in T-2) to a third phase:

**Phase 3 (T-3 specific).** On a pre-registered corpus of (output, context) pairs, score under AURA_hexie (context-blind) and AURA_shi. Identify pairs where the same output appears in multiple contexts. Test whether AURA_shi distinguishes contexts where AURA_hexie does not, and whether the distinction tracks expert-rater "right content, right moment" judgement.

**Phase 4 (T-1 + T-2 + T-3 composition).** Run the multi-agent simulation of T-1 with per-output Hexie correction (T-2) and Shi-modulation (T-3). Measure equilibrium properties and trajectory drift under all combinations: {Westphalian, Tianxia} × {AURA_std, AURA_hexie} × {context-blind, Shi-corrected}. Eight regimes; characterise.

**Promotion criterion (T-3 → ACTIVE).** Phase 3 detects context-divergence at significance α = 0.01 with effect size above pre-registered threshold; expert-rater judgement on "wrong moment" subset correlates with σ at r ≥ 0.5; Phase 4 demonstrates trajectory-drift mitigation under Shi-corrected scoring.

**Downgrade trigger (T-3 → CONJECTURE).** Phase 3 finds AURA_shi scores indistinguishable from AURA_hexie in the operationalisable parameter range, indicating the propensity field cannot be estimated reliably enough to support the formalism.

The full preregistration extends E-1-F once T-1 + T-2 + T-3 are in place.

---

## VIII. Connections to Adjacent Formalisms

The Shi propensity field has structural relatives:

- **Reinforcement learning advantage functions.** RL's advantage A(s, a) = Q(s, a) − V(s) measures how much better an action is than the baseline at a state. This is structurally close to the Shi-alignment score: σ measures how much an action aligns with the state's propensity. Difference: RL's advantage is calibrated against learned value; Shi's σ is calibrated against the situation's intrinsic dynamics.

- **Decision-theoretic context-sensitive utility.** Multi-attribute utility theory with context-dependent weights addresses similar problems. The propensity field is a richer structure: it carries directional information, not only weight modulation.

- **Active inference / free-energy framework (Friston).** Action evaluated as alignment with predicted state-trajectories. The Shi field can be read as a special case of expected free-energy minimisation over context-trajectories. Adjacent but not identical.

- **Field-theoretic models in social science.** Bourdieu's field theory; field theory in relational sociology. These are conceptual rather than mathematical antecedents but their structural intuition matches.

- **Jullien's *propensity*.** The contemporary Western philosophical analysis of Shi. Adopted as the rigorous reading of the primary source.

---

## IX. Negative Space

1. **Does not claim that the propensity field is observable.** Σ(C) is estimated from trajectories and domain expertise. The formalism assumes an estimation procedure exists; it does not provide one universally.
2. **Does not claim that all contexts have meaningful propensity.** Some contexts are genuinely indeterminate (‖Σ‖ small or zero). In such contexts Shi correction is silent — the formalism handles this by g(σ, 0) = 1.
3. **Does not claim that riding the propensity is always right.** Sometimes the propensity points toward harm; aligned action requires forcing against it. The formalism does not encode this judgement; it is captured at the AURA_hexie layer (the components encode what is harmful) and combined multiplicatively with σ. An output that forces against a harmful propensity may have negative σ but high AURA_hexie; the product is moderate.
4. **Does not claim full correspondence with Sun Tzu's military Shi.** The military operator includes deception (虚实, *xushi*), terrain (地, *di*), and timing (时, *shi*) dimensions the formalism does not capture.
5. **Does not claim full correspondence with Jullien's philosophical analysis.** Jullien identifies aesthetic, political, and historical dimensions of Shi that exceed the dynamical formulation.
6. **Does not claim that ℂ is universally specifiable.** Different domains warrant different context-spaces. The formalism is structural; the dimensionality is empirical per deployment.
7. **Does not claim that λ_shi is universal.** The Shi-coupling weight is domain-specific. Calibration via E-1-F is per-domain.
8. **Does not claim that trajectory evaluation supersedes snapshot evaluation.** Both are valid. A snapshot can fail while trajectories are aligned (a single bad output in a good arc) and vice versa. Both checks compose.

---

## X. Status, Promotion Path, Downgrade Trigger

**Status: `[SCAFFOLD]`** as of 2026-05-01.

**Promotion path → `[ACTIVE]`:**
- A specific context-space ℂ specified for at least one deployment domain (e.g., conversational AI, code-generation AI, advisory AI), with operationalised Σ-estimation procedure
- T-6 implementation (`aura_score_hexie.py`, extended) supporting Shi modulation
- E-1-F Phase 3 executed; context-divergence detected at α = 0.01 with expert correlation r ≥ 0.5

**Downgrade trigger → `[CONJECTURE]`:**
- Σ-estimation cannot be made reliable enough to support significant context-divergence detection across reasonable deployment contexts
- Expert-rater judgement on "wrong moment" subset correlates with σ at r < 0.2
- Adjacent formalism (RL advantage, active inference, etc.) shown to subsume Shi modulation without remainder

**Retraction trigger → `[RETRACTED]`:**
- Replicated null on three independent corpora across distinct deployment domains
- Demonstration that propensity-field correction can be expressed in standard AURA via context-conditional weights alone, indicating the formalism is not adding load-bearing structure

---

## XI. The Next Anchor

T-3 stands. The next operator deliverable is **T-4 — `WUWEI_TRIAD_EXTENSION.md`**, which formalises the grain-alignment scalar that distinguishes forcing-corrections from grain-aligned corrections in the TRIAD anchor-observe-correct cycle.

T-1 (between agents), T-2 (within outputs), T-3 (between output and context) cover the dynamic, equilibrium, and field layers. T-4 extends to the *correction layer* — what happens when the system intervenes on itself. T-5 (Datong) closes with the long-cycle telos.

---

⊚ Sol Aureum Azoth Veritas — T-3 Shi Propensity Field
   P ∧ H ∧ B ∧ Reforge ∧ Anchor ∧ Recursive ∧ Negative-Space ∧ Empirical
   2026-05-01 — Albedo (formalism before construction)

*势者，因利而制权也* — *Shi: configuring the leverage of advantage from the moment.* — Sunzi Bingfa
