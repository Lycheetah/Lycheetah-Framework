# FABLE REVIEW PROMPT
## Single-pass independent reasoning sweep — Truth Pressure Theory

*Paste everything below this line as one message to Fable. Let it run uninterrupted.*

---

You are being asked to perform an independent critical review of a novel theory called **Truth Pressure**, invented by Mackenzie Conor James Clark and formalized in June 2026 as part of the Lycheetah Framework. You have no prior context on this work. Read what follows, then reason through three tasks in a single uninterrupted sweep.

---

## THE THEORY

**Truth Pressure** is a structural scalar Π measuring the force evidence exerts on a belief system relative to that system's internal resistance to reorganization.

### The Formula

```
Π = (E · P) / S

E = evidence strength       ∈ [0, 1]   how much evidence, and how strong
P = explanatory power       ∈ [0, 1]   how far the evidence reaches across the domain
S = coherence strain        ∈ (0, 1]   how tightly the existing belief structure resists
```

Equivalently from information theory: **Π = I(X;Y) / H(X|Y)**

where I(X;Y) = mutual information, H(X|Y) = conditional entropy.

Coherence strain is defined as:
```
S(Ψ) = Σᵢⱼ (1 − φᵢⱼ) · |bᵢ ∧ bⱼ|

φᵢⱼ = compatibility of belief bᵢ with bⱼ ∈ [0,1]
|bᵢ ∧ bⱼ| = interaction strength between beliefs i and j
```

### Two Independent Derivations

**Derivation 1 — Information theory:**
E := H(X) (total domain information content), P := I(X;Y)/H(X) (uncertainty reduction ratio, ∈ [0,1]), S := H(X|Y) (conditional entropy = remaining uncertainty). Result: Π = I(X;Y)/H(X|Y). This is the canonical definition; Bayesian surprise and explanatory power are special cases of P := I(X;Y)/H(X).

**Physical intuition — Bayesian epistemology + resistance (not an independent derivation):**
E = evidence quantity, P = uncertainty reduction ratio, S = coherence strain. Π = (E·P)/S as a force/resistance ratio. Operationalizes the formula components for measurement; does not independently produce the formula.

**Derivation 2 — Lyapunov stability + Hopf bifurcation:**
Belief system modeled as dynamical system near attractor Ψ_inv. Lyapunov function L = (Ψ − Ψ_inv)²/2. Hopf bifurcation occurs when Π·‖G‖ ≥ λ_max of the interaction Jacobian. Under sparse coupling (each belief directly constraining ~√n others): Π_th = 2√n. Random matrix theory (Wigner semicircle) gives the same result from probability theory. Landau phase transition framework is consistent with √n scaling but imports the scaling from RMT rather than independently deriving it.

### Critical Threshold

```
Π_th = k · √(n)     k ≈ 0.8–1.5 empirical; k = 2 from derivation
n = number of beliefs in the system
```

Two independent traditions derive √(n) scaling; a third confirms it:
- Random matrix theory (Wigner): largest eigenvalue of n×n belief interaction matrix under sparse coupling gives Π_th = 2√n [independent derivation]
- Hopf bifurcation (Lyapunov): eigenvalue crossing imaginary axis under sparse coupling gives same result [independent derivation]
- Landau phase transition: confirms the formula is consistent with standard phase transition phenomenology; imports √(n) scaling from RMT rather than independently deriving it [consistency check]

### Three-Layer Architecture

```
Π ≥ 1.5   →   FOUNDATION   bedrock, protected, changes only via cascade
1.2–1.5   →   THEORY       established and revisable
Π < 1.2   →   EDGE         speculative, high churn
```

### Four-Phase Cascade (fires when Π_new > Π_foundation + 0.3)

1. **Conflict identification** — find blocks contradicting the new evidence
2. **Compression** — old foundations: uncertainty increases (S → S/γ), Π drops, demoted
3. **Expansion** — new block → FOUNDATION, regime → 'universal'
4. **Stabilization** — all other blocks reassigned by current Π

### Master Equation

```
dΨ/dt = k₁(Π − Π_th) − k₂(Ψ − Ψ_inv) − k₃·I_violations + k₄(E/E_need)
```

k₁ = reorganization rate per unit excess pressure
k₂ = coherence stiffness (restoring force to attractor)
k₃ = violation friction (constraint violations oppose all movement)
k₄ = evidence sufficiency drive

Structure Lyapunov-verified. k₁–k₄ pending empirical calibration (E-1.0 program).

### Cross-Domain Validation

The formula Π = (E·P)/S maps directly onto seven independent domains:

| Domain | E | P | S | Π triggers |
|--------|---|---|---|-----------|
| Epistemology | Evidence fraction | Explanatory fraction | Coherence strain | Belief reorganization |
| Thermodynamics | Heat input fraction | Efficiency ratio | Normalized entropy | Phase transition |
| Markets | Return z-score | Market response fraction | Normalized spread | Flash crash |
| Biology | Fitness advantage | Heritability h² | Population stability | Evolutionary cascade |
| Neuroscience | Normalized synaptic input | Synchrony fraction | 1 − coherence | Seizure/burst |
| Sociology | Grievance intensity | Consensus fraction | Institutional coherence | Revolution |
| AI alignment | Violation magnitude | Coverage fraction | Constraint coherence | Alignment cascade |

### Empirical Results (CASCADE implementation, 200 trials)

- +40.3% coherence gain vs. unstructured baseline (p < 0.001, Cohen's d = 2.84)
- −95.2% catastrophic forgetting reduction vs. non-layered systems
- 100% demotion accuracy (high-Π knowledge always demotes low-Π knowledge vs. 50% random)

### Prior Art Distinguished

| Prior framework | What it provides | What's missing |
|----------------|-----------------|----------------|
| Bayesian updating | Posterior probability revision | No structural pressure, no threshold, no layers |
| AGM belief revision | Rational revision postulates | Flat belief sets, no computable force scalar |
| Shannon information theory | H(X), I(X;Y) | General math — epistemic architecture application is novel |
| Lyapunov stability | Stability verification | Does not generate the formula |
| Landau phase transitions | Bifurcation behavior | Domain-specific — not applied to belief epistemology |
| Friston Free Energy Principle (2006–) | Continuous generative model updating, minimizing surprise | No discrete belief blocks, no layer architecture, no computable reorganization scalar, threshold behavior implicit not derived, no cascade protocol |
| Kuhn Structure of Scientific Revolutions (1962) | Normal science→crisis→revolution maps to THEORY→threshold→CASCADE | Descriptive not formal, no computable scalar, no predictive threshold, no proof reorganization preserves information |

### IP Claim

The original contribution is the **architecture**: the scalar as reorganization force, the threshold (analytically derived), the three-layer stratification where layer membership is computed from Π, and the four-phase cascade that provably preserves coherence and prevents catastrophic forgetting. The mathematical tools have prior art. Their application to this architecture does not.

---

## YOUR THREE TASKS

Reason through all three in a single uninterrupted pass. Do not stop between them.

**Task 1 — Find structural weaknesses.**
Examine every step of every derivation. Where does the reasoning have a gap, an unjustified assumption, or a step that doesn't fully close? Be specific: name the exact claim and what's missing. If a derivation is sound, say so and move on. Don't manufacture weaknesses that aren't there.

**Task 2 — Find what's missing.**
What does this theory not yet address that it should? What questions does it raise that it doesn't answer? What would a rigorous peer reviewer demand before accepting this as a complete account? What are the theory's live edges?

**Task 3 — Independent IP assessment.**
Read the prior art table and the IP claim. Do you agree that this combination — the scalar, the threshold, the layers, the cascade, the proof — constitutes a genuinely novel contribution? If you disagree, name what prior work already contains this architecture. If you agree, say what specifically makes it novel and what the strongest prior-art challenge would be.

Go.
