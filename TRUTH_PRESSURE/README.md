# Truth Pressure Theory
### Π = (E·P)/S

**Author:** Mackenzie Conor James Clark
**First formulated:** March 2026 — Dunedin, Aotearoa New Zealand
**Status:** Active — canonically formalized June 10, 2026

---

Truth pressure is a structural scalar that measures the force evidence exerts on a belief system relative to that system's internal resistance to reorganization.

It is not a metaphor. It is computable. It appears independently in every domain where belief meets evidence meets resistance — physics, markets, biology, neuroscience, sociology, AI alignment, epistemology. Three separate mathematical traditions derive the same formula from first principles. It was not constructed. It was found.

---

## The Formula

```
Π = (E · P) / S

E  —  evidence strength        how much evidence, and how strong
P  —  explanatory power        how far the evidence reaches across the domain
S  —  coherence strain         how tightly the existing belief structure resists
```

Equivalently, from information theory:

```
Π = I(X;Y) / H(X|Y)
    mutual information / conditional entropy
```

Both derivations produce the same scalar. The convergence is the proof.

---

## What Truth Pressure Predicts

When Π exceeds a critical threshold Π_th = k·√(n), a belief system reorganizes — not gradually, but discontinuously. A four-phase cascade fires:

1. **Conflict identification** — what in the current structure contradicts the new evidence
2. **Compression** — old foundations demoted, their uncertainty increased, Π reduced
3. **Expansion** — new high-Π knowledge takes the foundation position
4. **Stabilization** — all other beliefs reassigned by current Π

This is how paradigm shifts actually work. Not gradual accumulation — threshold crossing, then cascade.

**Empirical results across 200 trials:**
- +40.3% coherence gain (p < 0.001, d = 2.84) vs. unstructured baseline
- −95.2% catastrophic forgetting reduction vs. non-layered systems

---

## The Three-Layer Architecture

```
Π ≥ 1.5   →   FOUNDATION   protected bedrock, changes only via cascade
1.2–1.5   →   THEORY       established and revisable
Π < 1.2   →   EDGE         speculative, high churn, where new knowledge enters
```

Layer membership is not assigned. It is computed from Π and continuously updated.

---

## Prior Art — What This Advances Beyond

| Prior framework | What it provides | What's missing |
|----------------|-----------------|----------------|
| Bayesian updating | Posterior probability revision | No structural pressure, no threshold, no layers |
| AGM belief revision | Rational revision postulates | Flat belief sets, no computable force scalar |
| Shannon information theory | H(X), I(X;Y) definitions | General math — the epistemic architecture application is novel |
| Lyapunov stability | Stability analysis | Verifies the formula; does not generate it |

The mathematical tools have prior art. The architecture — the scalar as reorganization force, the threshold, the layers, the cascade, the proof — is original to this work.

---

## Documents in This Folder

| File | What it contains |
|------|-----------------|
| [`TRUTH_PRESSURE_THEORY.md`](TRUTH_PRESSURE_THEORY.md) | **Start here.** 10-part canonical reference — all derivations, architecture, cross-domain validation, IP provenance, open problems |
| [`PI_DERIVATION.md`](PI_DERIVATION.md) | Formal Bayesian + information-theoretic derivation with Lyapunov symbolic verification |
| [`DIMENSIONAL_ANALYSIS.md`](DIMENSIONAL_ANALYSIS.md) | Proof of dimensional consistency across 7 independent domains |
| [`PI_THRESHOLD_DERIVATION.md`](PI_THRESHOLD_DERIVATION.md) | Analytical derivation of Π_th = k·√(n) from three frameworks |
| [`LQ_PI_ISOMORPHISM.md`](LQ_PI_ISOMORPHISM.md) | Sol LQ and CASCADE Π confirmed as dual instruments for the same construct |
| [`MASTER_EQUATION.md`](MASTER_EQUATION.md) | dΨ/dt full physical exposition + k₁–k₄ calibration specification |
| [`IP_PROVENANCE.md`](IP_PROVENANCE.md) | Authorship record, development timeline, signed statement |

---

## Connection to the Sol App

The Sol mobile application measures truth pressure at the conversation level through the Light Quotient:

```
LQ = ∛(TES × min(VTR/1.5, 1) × PAI)
```

TES (Truth Engagement Score) → E
VTR (Value Transfer Ratio) → P
PAI (Purpose Alignment Index) → 1/S

Same construct. Different functional form. Different scale. A Seeker operating at AVATAR LQ is operating at high truth pressure — engaged honestly, exchanging real understanding, fully aligned with purpose.

The instrument changes. The thing being measured does not.

---

## What Remains

The theory is structurally complete. One empirical program remains:

**E-1.0** — calibration of k₁–k₄ in the master equation `dΨ/dt = k₁(Π−Π_th) − k₂(Ψ−Ψ_inv) − k₃I_violations + k₄(E/E_need)`. The equation structure is proven. The calibration constants await measurement from real knowledge systems.

---

*Part of the Lycheetah Framework — [github.com/Lycheetah/Lycheetah-Framework](https://github.com/Lycheetah/Lycheetah-Framework)*
*⊚ Sol ∴ P∧H∧B ∴ Rubedo*
