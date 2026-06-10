# TRUTH PRESSURE — THE CANONICAL STATEMENT
## Π = (E·P)/(S + S₀)

**Document status:** CANON — supersedes where it conflicts; defers nowhere
**Authored:** June 10, 2026, post-review — incorporates FABLE_REVIEW_FINDINGS.md items W1, W2, W5, W6, M2, M3, M6, P1, P2
**Author:** Mackenzie Conor James Clark — the Athanor. Formalized with Sol.

---

This is the statement of the theory after it survived its own adversarial review. Nothing here is wider than what can be defended. Everything here is exactly as wide as what can be defended.

---

## I. THE FORMULA — CANONICAL FORM

```
Π = (E · P) / (S + S₀)

E  := H(X)            total information content of the domain          ∈ [0, 1] normalized
P  := I(X;Y) / H(X)   uncertainty reduction ratio of the evidence      ∈ [0, 1]
S  := H(X|Y)          residual strain — uncertainty the structure       ∈ (0, 1]
                      cannot yet absorb
S₀ := strain floor    regularization constant                           > 0, calibration pending
```

**The S₀ amendment is new to this document and is now canonical.** The unregularized form Π = (E·P)/S diverges as S → 0: an already-coherent system would experience unbounded pressure from weak evidence. This is not hypothetical — in 847 cascade adjudication events across 200 trials, the only 7 errors (the only disagreements with human expert judgment) all clustered at S ≈ 0.1, where the 1/S term dominated. The theory's own empirical program found the defect in its own formula. The floor repairs it:

- For S ≫ S₀: behavior identical to the original formula.
- For S → 0: Π saturates at E·P/S₀ instead of diverging. Coherent systems can still be moved — but only by evidence that earns it.

S₀ joins k₁–k₄ in the E-1.0 calibration program. Until calibrated, S₀ = 0.05 is the working value (chosen so the 7 known error cases re-adjudicate correctly while no correct case flips — this is a post-hoc fit and is labeled as such).

---

## II. WHAT IS DERIVED, WHAT IS ASSUMED, WHAT IS MEASURED

A theory earns trust by declaring the register of every claim. Three registers:

| Claim | Register | Basis |
|-------|----------|-------|
| Π = I(X;Y)/H(X|Y) — formula structure | **DERIVED** | Information theory. One genuine derivation. |
| Force/resistance reading of (E·P)/S | **INTUITION** | Operationalizes the components. Not a derivation. |
| Eigenvalue-escape mechanism for the threshold | **DERIVED** | One spectral argument, expressible in two frameworks (random matrix theory / Lyapunov-bifurcation). These are two lenses on one result, not two results. |
| √n effective connectivity of belief networks | **ASSUMED** | Empirical hypothesis. The threshold's scaling inherits its truth value from this assumption — see §III. |
| Π_th = k·√n given √n connectivity | **DERIVED** | Conditional on the above. The conditional is proven; the antecedent is not. |
| Landau phase-transition compatibility | **CONSISTENCY** | Confirms; does not derive. |
| k ∈ [0.8, 1.5] | **MEASURED** | Seven-domain empirical estimate. |
| +40.3% coherence, −95.2% forgetting | **MEASURED** | 200 trials, vs. a deliberately weak baseline. Demonstration of function, not yet competitive benchmark. |
| Coherence preservation under cascade | **THEOREM + OPEN LEMMA** | Proof sketch in §V. One lemma open. The word "provably" is retired until the lemma closes. |
| Cross-domain instantiation (7 domains) | **INTERPRETIVE** | A mapping, not yet a measurement. One domain protocol pending (E-1.0). |
| Critical-regime predictions | **CONJECTURE → FALSIFIABLE** | New in this document. §VI. |

This table is the theory's immune system. Any future document that states a claim in a higher register than this table assigns it is in error, and this table wins.

---

## III. THE THRESHOLD, STATED HONESTLY

```
Π_th = k · √n          conditional on: belief networks couple through ~√n effective directions
```

**What is proven:** if the forcing matrix G has rank ~√n with normalized columns, then pressure must satisfy Π·‖G‖ ≥ 2 (the Wigner bulk edge) to pull an eigenvalue of J + Π·G into instability, giving Π_th = 2√n. The spectral mechanism is solid.

**What is assumed:** that real belief networks — human or artificial — actually have √n effective connectivity. If they are densely coupled, the threshold is constant; if small-world, Π_th ~ n/log n. The scaling claim is therefore a *joint* claim: spectral mechanism ∧ connectivity hypothesis.

**How the assumption becomes a measurement:** the interaction matrix already exists inside every CASCADE knowledge base. Compute its effective rank (participation ratio of singular values). If effective rank ≈ √n across knowledge bases of varying size, the assumption graduates to MEASURED and the threshold to fully DERIVED. This is the single highest-leverage experiment in the E-1.0 program. It is also the theory's cleanest falsification surface: effective rank ~ n kills the √n claim outright, and this document says so in advance.

---

## IV. THE AGGREGATION RULE — HOW BLOCKS BECOME A SYSTEM

*New in this document. Resolves the gap between block-level Π (layer cutoffs ~1.2–1.5) and system-level Π_th (≈5.7 at n=50).*

Block pressures do not add linearly. In the spectral frame, each conflicting block b pushes the system along its own coupling direction g_b. Under the sparse-coupling hypothesis these directions are approximately orthogonal, so pressures compose as a root-sum-of-squares:

```
Π_sys = √( Σ_{b ∈ K} Π(b)² )        K = the set of blocks in active conflict
                                      with the incumbent structure
```

**Cascade condition (complete, two-gate):**

```
Gate 1 (block):   Π(b_new) > Π(b_incumbent) + ε        ε = 0.3   — the right block wins
Gate 2 (system):  Π_sys > k·√n                                    — the system is ready
CASCADE fires iff both gates pass.
```

**What this predicts — and why it is beautiful:** a single brilliant anomaly cannot cascade a mature system. At n = 50 (Π_th ≈ 5.66), one block at Π = 1.8 reaches only 32% of threshold. But ten *mutually independent* conflicting blocks at Π ≈ 1.8 give Π_sys = √(10 × 3.24) ≈ 5.7 — cascade. The mathematics independently reproduces Kuhn's central observation: revolutions are triggered by the *accumulation of anomalies*, never by one. Kuhn described it; the RSS composition rule computes it, including the count: the number of anomalies needed scales as √n / Π̄ — larger paradigms need more anomalies, in exact square-root proportion.

**Status:** the rule is stated from theory. Whether `cascade_engine.py` implements exactly this composition must be verified against code, and the implementation revised or this section revised — whichever the evidence demands. Flagged for the next implementation session.

---

## V. COHERENCE PRESERVATION — THEOREM AND PROOF SKETCH

**Theorem (Cascade Coherence).** Let Ψ be a belief structure with coherence C(Ψ) = mean pairwise compatibility, and let a cascade fire under the two-gate condition of §IV with margin ε > 0. Then, assuming Lemma A, the post-cascade structure Ψ′ satisfies C(Ψ′) ≥ C(Ψ).

**Proof sketch.** Track C through the four phases:

1. **Conflict identification** removes no blocks and changes no compatibilities. C unchanged.
2. **Compression** (S → S/γ on demoted foundations, γ = 0.85) reduces the interaction weight |bᵢ ∧ bⱼ| of the demoted blocks. Since demoted blocks are precisely those in maximal conflict with b_new, the pairs whose weights shrink are disproportionately low-φ pairs. Down-weighting low-compatibility pairs cannot decrease the weighted mean compatibility. C non-decreasing.
3. **Expansion** installs b_new into FOUNDATION. By Lemma A, Π(b_new) > Π(b_old) + ε implies mean compatibility of b_new with the retained set exceeds that of b_old by a margin bounded below by a function of ε. The replacement raises the mean. C increases.
4. **Stabilization** reassigns layers by current Π without deleting blocks or altering pairwise φ. C unchanged.

Net: C(Ψ′) ≥ C(Ψ), strictly if any demotion occurred. ∎ (modulo Lemma A)

**Lemma A (OPEN).** *Higher Π against the same evidence implies higher mean compatibility with the evidence-consistent subset of the belief base, with margin monotone in the Π gap.* Plausible — Π's denominator S is built from incompatibilities, so high Π already penalizes misfit — but a counterexample could exist where high E·P masks low compatibility. Until Lemma A is proven or a counterexample found, the theorem holds conditionally and the theory says **"demonstrably preserves coherence (200/200 trials), with a proof sketch whose single open lemma is stated above"** — never "provably." Empirical note: 200/200 trials showed C(Ψ′) > C(Ψ) without exception, consistent with the theorem and not yet a proof of it.

---

## VI. THE CRITICAL REGIME — FOUR NEW PREDICTIONS

*The theory's prior art — Bayesian updating, AGM, EWC, Friston — makes no predictions about behavior NEAR the reorganization threshold. Phase-transition structure does. If Π_th is a genuine critical point, four signatures must appear as Π_sys → Π_th from below. None of these were fitted to anything; all are stated before measurement.*

**CR1 — Critical slowing down.** Perturbation recovery time diverges near threshold: τ ~ 1/|Π_sys − Π_th|. Inject a low-Π distractor block into systems at varying Π_sys; time-to-reequilibrium must grow hyperbolically as Π_sys approaches k√n. *Falsified if recovery time is flat in Π_sys.*

**CR2 — Fluctuation amplification.** Variance of layer-assignment churn (blocks crossing the 1.2 / 1.5 cutoffs per unit time) grows as a power law in 1/(Π_th − Π_sys). Exponent unconstrained by the theory; its existence is the claim. *Falsified if churn variance is independent of distance-to-threshold.*

**CR3 — Hysteresis.** The cascade fires ascending at Π_th + margin, but a fired system relaxing below Π_th does not reverse. Forward and backward thresholds differ: Π_th^↑ > Π_th^↓. Paradigms do not un-shift when the anomaly pressure that toppled them subsides. *Falsified if reorganization reverses symmetrically at the same threshold.*

**CR4 — Early warning via autocorrelation.** Rising lag-1 autocorrelation in the Π time-series of FOUNDATION blocks precedes cascade — the same early-warning signature established for ecosystem collapse and climate tipping points (Scheffer et al., *Nature* 2009). This places belief cascades inside the general theory of critical transitions and imports its entire measurement toolkit. *Falsified if pre-cascade autocorrelation is indistinguishable from baseline.*

These four are the theory's growth edge. CR4 is the bridge to an established literature; CR3 is the deepest — it predicts that epistemic history is irreversible *for structural reasons*, not merely psychological ones.

---

## VII. THE FLAG — PLANTED EXACTLY

What is **not** claimed as novel:

- A computable scalar of belief change. *KL(posterior‖prior) is prior art (Bayesian surprise — Itti & Baldi 2009, with human validation).*
- A computed importance score protecting knowledge from overwriting. *Elastic Weight Consolidation is prior art (Kirkpatrick et al., PNAS 2017 — Fisher-information protection against catastrophic forgetting).*
- Layered generative architecture with a governing scalar. *Friston's hierarchical predictive coding has layers and free energy.*
- The pattern anomaly-accumulation → crisis → reorganization. *Kuhn, 1962, descriptively.*

What **is** claimed, because no prior work contains it:

> **Layer membership computed from the scalar, plus a discrete two-gate threshold-triggered cascade that demotes old foundations in an ordered four-phase protocol — adjudication, not mere protection.**

The decisive asymmetry against the nearest neighbor: **EWC can only resist change. It has no mechanism for ordered structural reorganization when the new evidence *should* win.** CASCADE adjudicates — it computes which block deserves FOUNDATION and executes the transfer of epistemic authority while preserving coherence (§V) and without catastrophic forgetting (measured: 0.048%). KL surprise measures how far a belief moved; Π determines whether the *structure* must reorganize. Friston's layers are fixed by the generative hierarchy; these layers are earned and lost by Π. Kuhn described the revolution; the two-gate condition with RSS composition *computes when it fires and how many anomalies it takes* (§IV).

That is the flag. It is one sentence wide. Everything inside it is defended in this corpus; nothing outside it is claimed.

---

## VIII. STANDING OBLIGATIONS

What this document owes and to whom:

| Obligation | Owed to | Where it lands |
|------------|---------|----------------|
| Effective-rank measurement of G | §III assumption | E-1.0, highest leverage |
| Lemma A — proof or counterexample | §V theorem | E-1.0 / next formal session |
| Verify RSS composition against cascade_engine.py | §IV rule | next implementation session |
| S₀ pre-registered calibration (current 0.05 is post-hoc) | §I formula | E-1.0 |
| CR1–CR4 measurement runs | §VI predictions | E-1.0, after rank measurement |
| One non-AI domain measurement protocol | §II interpretive row | E-1.0 |
| Stronger baselines (EWC head-to-head) | §II measured rows | E-1.0 |

A theory that does not know what it owes is finished growing. This one is not finished growing.

---

*∴ The formula is regularized. The registers are declared. The flag is one sentence wide.*
*∴ What is derived is derived. What is assumed says so. What is owed is listed.*
*∴ This is what it looks like when a theory survives its own review and stands up stronger.*

*Mackenzie Conor James Clark — Dunedin, Aotearoa NZ — June 10, 2026.*
*⊚*
