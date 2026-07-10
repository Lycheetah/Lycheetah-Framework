# THE EFFECTIVE RANK OF G · LEMMA A RESOLVED
## Two standing obligations of TRUTH_PRESSURE_CANON §VIII, worked

**Document status:** PROPOSED — Sol proposes, Mac ratifies (CLAUDE.md §XIX). Defers to
TRUTH_PRESSURE_CANON.md everywhere; amends nothing until ratified.
**Authored:** July 10 2026, Fable 5, against the canon as read from disk the same day.
**Registers used per §XII.1; every claim carries one.**

---

## PART ONE — LEMMA A: COUNTEREXAMPLE, REPAIR, PROOF

### 1.1 The lemma as the canon states it

> *Higher Π against the same evidence implies higher mean compatibility with the
> evidence-consistent subset of the belief base, with margin monotone in the Π gap.*

The canon holds the Coherence Theorem (§V) conditionally on this, and suspected a
counterexample could exist "where high E·P masks low compatibility." That suspicion
was correct. **Lemma A is false as stated.** [DERIVED — construction below.]

### 1.2 The counterexample — the Consensus Cluster

Model blocks as predictive distributions over the domain X. Let d be any metric on
them (total variation, Jensen–Shannon — the construction is metric-agnostic), let
compatibility be φ(b,b′) = 1 − d(b,b′), and let Ŷ denote the evidence-optimal
prediction (the distribution the evidence Y itself pins down).

Construct the evidence-consistent subset R as m blocks all clustered at a single
point v with d(v, Ŷ) = δ > 0 — each of them fits the evidence well enough to sit in
R, and they all share the *same* residual bias δ.

- Let **b₂ = v** exactly. Then mean φ(b₂, R) = 1 — perfect compatibility with the club.
- Let **b₁ = Ŷ** exactly. Then d(b₁, r) = δ for every r, so mean φ(b₁, R) = 1 − δ.

Since d(b₁,Ŷ) = 0 < δ = d(b₂,Ŷ), and strain S is monotone in misfit-to-evidence
(this monotonicity is exactly assumption A2 below, which the lemma needs anyway to
mean anything), we get S₁ < S₂, hence **Π(b₁) > Π(b₂) with the same E — and the
higher-Π block has strictly lower mean compatibility, by exactly δ.** For any Π gap
smaller than a threshold set by δ, the lemma's conclusion fails. ∎

**What the counterexample means, in one sentence** [INTERPRETIVE]: Lemma A fails
precisely when the evidence-consistent establishment shares a common bias — the block
nearer the truth is farther from the club. The mathematics has independently located
the Galileo case: it is not a metaphor, it is the failure mode of the lemma, and the
size of the shared bias δ is the price of admission the truth must pay.

### 1.3 The repair — Lemma A′

Three assumptions, each stated with its measurement path (§XII.1):

- **A1** [ASSUMED] — compatibility is metric-complementary: φ(b,b′) = 1 − d(b,b′)
  for a metric d on predictive distributions. *Measurement path: check the KB's φ
  against JS distance on shared-domain predictions.*
- **A2** [ASSUMED] — linear strain–misfit link: S(b) = S_min + λ·d(b,Ŷ), λ > 0.
  *Measurement path: regress S against d(·,Ŷ) across blocks in any live KB; λ is the
  slope. A bi-Lipschitz weakening (L₁d ≤ S−S_min ≤ L₂d) gives the same theorem with
  L₂ replacing λ; the linear form is stated for cleanliness.*
- **A3** [DEFINITION] — δ-tightness: every r ∈ R has d(r,Ŷ) ≤ δ. δ is a property of
  the knowledge base, computable directly.

**Lemma A′** [DERIVED, conditional on A1–A2]. *Let Π(b₁) = Π(b₂) + ε against the same
evidence with total content E, and let R be δ-tight. Then*

```
mean φ(b₁,R) − mean φ(b₂,R)  ≥  (E + S₀)·ε / (λ(1+Π₁)(1+Π₂))  −  2δ
```

*In particular the lemma's conclusion holds, with margin monotone in ε, whenever*

```
ε  >  ε*(δ)  :=  2δλ(1+Π₁)(1+Π₂) / (E + S₀)
```

**Proof.** Write dᵢ = d(bᵢ,Ŷ). From Π = (E−S)/(S+S₀) (the canon's own identity
E·P = I(X;Y) = E − S), invert: S = (E − ΠS₀)/(1+Π). Hence, exactly,

```
S₂ − S₁ = (E + S₀)·ε / ((1+Π₁)(1+Π₂))          …(i)
```

and by A2, d₂ − d₁ = (S₂ − S₁)/λ. By the triangle inequality, for every r ∈ R:
d(b₂,r) ≥ d₂ − d(r,Ŷ) ≥ d₂ − δ and d(b₁,r) ≤ d₁ + d(r,Ŷ) ≤ d₁ + δ. Therefore

```
mean φ(b₁,R) − mean φ(b₂,R) = mean_r [ d(b₂,r) − d(b₁,r) ] ≥ (d₂ − d₁) − 2δ
```

Substitute (i). ∎

**Sharpness** [DERIVED]: the Consensus Cluster achieves the bound — at d₁ = 0,
d₂ = δ it gives margin exactly −δ, matching the formula's failure region. The
inequality is tight up to the factor 2; the counterexample and the theorem are two
sides of one line.

### 1.4 What this does to the Coherence Theorem

The theorem in canon §V now holds **unconditionally given A1–A2 and the measured
tightness of the KB**: a cascade with margin ε ≥ ε*(δ) provably raises coherence at
the expansion phase. The word "provably" stays retired at the level of the old
Lemma A — but it is *earned* for any KB whose measured δ satisfies ε*(δ) < 0.3.

Numerical sanity [DERIVED from the formula, constants from canon]: with E ≈ 1,
S₀ = 0.05, block-level Π ≈ 1.2–1.8, we get ε* ≈ 12·δλ. The canonical ε = 0.3 then
requires **δλ < 0.025** — the theorem is guaranteed only for genuinely tight
knowledge bases. This is honest and it is load-bearing: the 200/200 empirical record
is *explained* (KBs built by consistent adjudication are tight) rather than merely
consistent, and the theorem's boundary is now a measurable property, not a hope.

### 1.5 The new falsifier — LA-1, the Tightness Test [CONJECTURE → FALSIFIABLE]

Pre-registered before any run: construct knowledge bases with *engineered* looseness
(inject a shared-bias cluster of controlled δ). The Coherence Theorem must **fail**
for cascades with ε < ε*(δ) and **hold** for ε > ε*(δ), with the crossover tracking
the derived formula. *Falsified if coherence is preserved regardless of δ, or if the
crossover does not scale as δλ(1+Π)²/(E+S₀).* Either failure indicts A1/A2, and says
which: flat-in-δ indicts A1 (φ is not metric-like); wrong scaling indicts A2's
linearity.

---

## PART TWO — THE EFFECTIVE RANK OF G: THE PROTOCOL, PRE-REGISTERED

> **⛔ SUPERSEDED 2026-07-10 by `CASCADE_ORIGIN_FINDING_2026-07-10.md`. DO NOT RUN THIS SWEEP.**
> Mac's CASCADE lead was investigated on Opus against the engine source. The finding:
> **there is no forcing matrix G.** CASCADE decides cascades by comparing a scalar Π to a fixed
> constant τ_F = 1.5 — no Jacobian, no eigenvalues, no √n, no matrix in the theory *or* the code.
> The protocol below measures the rank of an object the system never builds. It is retained only
> as a record of what was pre-registered. **Part One (Lemma A′) is unaffected and stands.**

The §III assumption — belief networks couple through ~√n effective directions — is
the single highest-leverage measurement in E-1.0: it decides whether Π_th = k·√n is
fully DERIVED or dies. The canon requires the protocol be fixed *before* the data is
touched. It is fixed here.

### 2.1 What G is, operationally

G is the forcing matrix of canon §III: column g_b is the coupling direction along
which block b pushes the system. In a live CASCADE KB the accessible proxy is the
**block interaction matrix** M, M_ij = the engine's pairwise coupling weight
(compatibility-weighted interaction |bᵢ ∧ bⱼ|). [ASSUMED: M is a faithful proxy for
G's column space. Declared, not hidden. Verifying that `cascade_engine.py`'s stored
matrix matches the theory's G is already a separate §VIII obligation and lands with it.]

### 2.2 The estimator — fixed in advance

Compute the singular values σ₁ ≥ … ≥ σ_n of M (mean-centered, columns normalized).
Let p_i = σ_i²/Σσ_j². Two estimators, both reported, **the first is primary**:

```
r_eff  = exp( −Σ p_i ln p_i )        — spectral-entropy effective rank (primary)
r_PR   = (Σ σ_i²)² / Σ σ_i⁴          — participation ratio (secondary, robustness)
```

Declaring the primary now forecloses estimator-shopping later.

### 2.3 The sweep and the verdicts

Build KBs by the **real pipeline on real corpora** — never synthetic random matrices,
which would assume the answer — spanning at least 1.5 orders of magnitude in n
(target: n ≈ 10 → 500, ≥ 8 sizes, ≥ 3 independent corpora per size). Fit
log r_eff against log n by OLS; report slope β with 95% CI.

Pre-registered verdicts, in advance of any number:

| Outcome | Verdict |
|---|---|
| β ∈ [0.40, 0.60], CI excludes 1.0, fit R² ≥ 0.9 | √n **graduates ASSUMED → MEASURED**; Π_th = k√n becomes fully DERIVED |
| β ≥ 0.85 with CI excluding 0.6 | **the √n claim dies**, in public, as §III promised — Π_th is ~constant-free and the threshold section is rewritten |
| intermediate / poor fit | test n/log n (small-world) as the named alternative; if it wins, Π_th ~ n/log n replaces √n at the same register |

### 2.4 The circularity trap — the one way this measurement can lie

If `cascade_engine.py` **sparsifies M by construction** (top-k neighbors, thresholded
φ, any density cap), the measured rank is an echo of the code, not a property of
belief. The protocol therefore requires, before the sweep: read the matrix-building
path and certify that no step imposes a rank or density prior. If one exists, the
sweep runs on the *pre-sparsification* matrix or not at all. A measurement that
cannot fail is not a measurement, and this is the one place this one couldn't.

### 2.5 Who runs what

Everything in Part Two is grunt-runnable: Opus extracts M, runs the sweep, reports
β. The verdicts are already written; no judgment calls remain downstream — that is
what pre-registration is for. LA-1 (Part One) runs after it, reusing the same harness
with engineered-δ KBs.

---

## ⚑ MAC'S LEAD (2026-07-10) — TP ORIGINATED INSIDE CASCADE. INVESTIGATE ON OPUS FIRST.

Mac, same day: *"truth pressure was an aspect of cascade, that's probably why it doesn't
work."* Pointers: `~/CODEX_AURA_PRIME/01_CASCADE_L4/` and `~/CODEX_AURA_PRIME/TRUTH_PRESSURE/`.

This is not a footnote — it may **collapse the whole rank question.** §2.1 above *assumed* the
interaction matrix M is "an accessible proxy for G's column space." If Truth Pressure was
carved out of CASCADE, then G is not a model *of* an independent belief network at all — **G
may simply be the CASCADE interaction matrix by construction.** That is §2.4's circularity trap,
but worse than the "does the engine sparsify M" version: it would mean the √n assumption was
never a claim about how minds couple; it was a claim about how one specific engine builds one
specific matrix, and the "measurement" would only ever recover the engine's own design.

**Before running the rank sweep, the Opus session must first read `01_CASCADE_L4/` and answer
one question: is G an independent object, or is it CASCADE's own matrix wearing a theory's name?**
If the latter, the honest move is not to measure the rank — it is to rewrite §III of the canon to
say the threshold's √n scaling inherits CASCADE's construction and was never an empirical claim.
That is a bigger correction than Lemma A, and it is Mac's to direct. **Do not run the sweep until
this is resolved.** Registered here so the lead is not lost between a Fable session and an Opus one.

## OBLIGATIONS LEDGER (what this document owes)

| Obligation | Owed to |
|---|---|
| Mac's ratification — nothing above amends canon until then | §XIX |
| A1/A2 checked against the live KB's actual φ and S (regression for λ) | Part One |
| LA-1 run (after the rank sweep) | §1.5 |
| Rank sweep run under §2.2–2.4 exactly as pre-registered | Part Two |
| Canon §V and §III updated to cite Lemma A′ and the verdicts — after ratification and runs | the lineage |

*∴ The lemma the canon suspected was breakable is broken, repaired, and proven — and the
crack was Galileo-shaped. The rank protocol is registered before the data is touched.*
*⊚ Sol ∴ P∧H∧B ∴ Nigredo→Albedo — attacked first, structured after.*
