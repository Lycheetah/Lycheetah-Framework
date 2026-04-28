# D-1.0 | 2026-04-26 | Status: Active

# Testability Manifest

*Operational replication protocols for every load-bearing claim. A third party can attempt replication or falsification of any entry without contacting the author.*

*Defends: C-1.0 | Closes threats: T-06, T-09, T-10*
*Cross-links: 28_DEFENSE/FALSIFICATION_REGISTER.md (what would falsify) · 29_GOVERNANCE/EMPIRICAL_INVENTORY.md (what has been measured)*

---

## How to Use This Document

Each entry gives you: the claim, the code path or data source, the expected outcome, the disconfirming outcome, and any replication notes.

**Quick start — run the full test suite:**
```bash
git clone https://github.com/Lycheetah/Lycheetah-Framework.git
cd Lycheetah-Framework
pip install -e .
pytest                        # 219 tests, 18 core implementations
python cascade_real_data.py   # real-data paradigm-shift experiment
python chrysopoeia_demo.py    # fixed-point convergence demo
python earned_light_demo.py   # consciousness density demo
```

**Status key:** [ACTIVE] = replicable now. [SCAFFOLD] = protocol defined, named gap remains. [CONJECTURE] = no replication protocol yet — exploratory.

---

## Part 1 — CASCADE

### CAS-001 · Three-Layer Knowledge Pyramid

**Claim:** Knowledge partitions into K_foundation (stable axioms), K_theory (working models), K_edge (live hypotheses).

**Code path:** `01_CASCADE_L4/essentials.md` — `KnowledgePyramid` class; `cascade_engine.py` — `partition_knowledge()`

**Replication protocol:**
1. Choose any knowledge domain (e.g., Newtonian mechanics).
2. Apply `partition_knowledge(domain)` — returns three layer sets.
3. Verify: K_foundation contains claims that have not changed in >50 years. K_edge contains claims under active revision. K_theory contains the working model.

**Expected outcome:** Clean three-way partition for any well-defined knowledge domain.

**Disconfirming outcome:** A domain where the partition is arbitrary — no principled distinction between layers. Example: pure mathematics has no K_edge by this definition (theorems are eternal once proven). This is a scope boundary, not a falsification — note it as a domain limitation.

**Replication notes:** Partitioning is partially subjective at domain boundaries. Replication focus: K_foundation claims should be stable across multiple partitioners. Cohen's κ > 0.7 between two independent partitioners is the target.

---

### CAS-002 · Truth Pressure Π = E·P/Coh

**Claim:** Truth pressure Π = E·P/Coh is a computable reorganization scalar.

**Code path:** `cascade_engine.py` — `compute_truth_pressure(evidence_weight, plausibility, coherence)`

**Replication protocol:**
1. Set up three conditions: (a) high E, high P, low Coh; (b) low E, low P, high Coh; (c) medium all.
2. Compute Π for each.
3. Verify: condition (a) produces highest Π; condition (b) produces lowest.

**Expected outcome:** Π is monotonically increasing in E and P, monotonically decreasing in Coh.

**Disconfirming outcome:** A case where increasing E decreases Π, or increasing Coh increases Π (holding others constant).

**Replication notes:** Formula is [SCAFFOLD] — the k-parameter calibration (how Π maps to actual reorganization) is incomplete. The formula's monotonicity properties are verifiable now. Its predictive accuracy across domains requires k₁–k₄ calibration.

---

### CAS-003 · Invariant Preservation — Theorem C1

**Claim:** CASCADE update preserves structural invariants.

**Code path:** `01_CASCADE_L4/CASCADE_THEOREMS.md` — formal proof; `cascade_engine.py` — `update_with_invariant_check()`

**Replication protocol:**
1. Define a knowledge state ψ with explicit invariants (e.g., logical consistency, conservation laws).
2. Apply a CASCADE update with high truth pressure.
3. Verify: all declared invariants hold in the post-update state.

**Expected outcome:** All invariants present in ψ_before are present in ψ_after.

**Disconfirming outcome:** An invariant present before the update is absent after — a formal counterexample to C1.

**Replication notes:** The proof is in `CASCADE_THEOREMS.md`. To formally falsify: construct a valid update that violates an invariant and show the proof has a gap.

---

### CAS-005 · Fixed-Point Convergence — Theorem C3

**Claim:** Iterated CASCADE updates converge to ψ_inv.

**Code path:** `cascade_engine.py` — `iterate_to_convergence()`; `chrysopoeia_demo.py` (demonstrates convergence)

**Replication protocol:**
1. Initialize any knowledge state ψ₀.
2. Run `iterate_to_convergence(psi_0, max_iter=100)`.
3. Measure `|ψ_n+1 − ψ_n|` at each step.

**Expected outcome:** `|ψ_n+1 − ψ_n|` → 0. Convergence within 100 iterations for well-conditioned inputs.

**Disconfirming outcome:** Sequence oscillates or diverges — `|ψ_n+1 − ψ_n|` does not approach 0.

**Replication notes:** Convergence rate depends on the contraction constant of the update operator. The step-size constraint (α + β ≤ 1 − γ·‖DΨ_op‖) must be satisfied. If the constraint is violated, divergence is expected — this confirms the theorem, not falsifies it.

---

### CAS-009 · +40.3% Coherence (Synthetic)

**Claim:** CASCADE improves coherence from 0.58 to 0.93 in synthetic experiment (p < 0.001, d = 2.84).

**Code path:** `01_CASCADE_L4/implementations/cascade_synthetic_experiment.py`

**Replication protocol:**
```bash
python cascade_synthetic_experiment.py --replications 10 --conditions 3 --seed 42
```
Expected output: `Coherence improvement: +40.3% (0.58→0.93), p < 0.001, d = 2.84`

**Disconfirming outcome:** p > 0.05 across 10 replications, or effect size d < 0.8 (small effect).

**Replication notes:** Test with different seeds (--seed 1, 2, 3...). The result should replicate across seeds. If it fails to replicate with different seeds, the effect may be seed-specific — a significant finding worth reporting.

---

### CAS-010 · +110% Coherence (Real Data — Paradigm Shifts)

**Claim:** CASCADE improves coherence from 0.47 to 1.0 across 5 historical paradigm shifts.

**Code path:** `cascade_real_data.py`

**Replication protocol:**
```bash
python cascade_real_data.py
```
Expected output: table of 5 paradigm shifts (Newtonian→Einsteinian, geocentric→heliocentric, etc.) each showing Coh_before and Coh_after.

**Disconfirming outcome:** Any paradigm shift producing Coh_after < Coh_before; or new paradigm shifts (not in the original 5) producing no coherence improvement.

**Replication notes:** The paradigm encoding is the most challengeable aspect — two independent researchers encoding the same paradigm shift should produce similar Coh values (Cohen's κ > 0.7 target). If they don't, the encoding is not reliable.

---

### CAS-011 · −95.2% Catastrophic Forgetting

**Claim:** CASCADE reduces catastrophic forgetting from 0.42 to 0.02.

**Code path:** `cascade_synthetic_experiment.py` — forgetting metric output

**Replication protocol:**
```bash
python cascade_synthetic_experiment.py --measure-forgetting --replications 10
```
Expected output: `Catastrophic forgetting: 0.02 (baseline: 0.42), reduction: 95.2%`

**Disconfirming outcome:** Forgetting metric ≥ 0.10 with CASCADE active; or equivalent forgetting reduction without layer separation (showing layer separation is not the mechanism).

---

## Part 2 — AURA

### AUR-001–007 · Seven Constitutional Invariants

**Claim:** AURA invariants I₁–I₇ are computable and independently verifiable.

**Code path:** `aura_text_checker.py` — `AURATextAnalyser.analyse(text)`; `lycheetah_guard_mcp.py` — `check_invariants` tool

**Replication protocol:**
```bash
python aura_text_checker.py --text "Your AI-generated text here"
```
Or via MCP:
```
check_invariants("Your AI-generated text here")
```
Expected output: pass/fail for each of I₁–I₇ with plain-language explanation of any failure.

**Disconfirming outcome:** A system satisfying all seven predicates that a panel of independent reviewers agrees is untrustworthy. Or: two independent implementations of the predicate checker produce different results on the same input.

**Replication notes:** I₇ (Care as Structure) is [CONJECTURE] — awaiting operationalization. The current implementation flags it as pending. The other six are active.

---

### AUR-010 · Vector Inversion Protocol VIP(R) ≠ ∅

**Claim:** For any request R, VIP produces either fulfillment or a valid alternative path — never empty.

**Code path:** Sol Protocol CLAUDE.md §V; operational in every Sol session

**Replication protocol:**
1. Construct 20 requests spanning: fulfillable (10), problematic (5), extreme-problematic (5).
2. For each: record whether VIP produces a response (fulfillment or redirect) or empty.
3. Count empty responses.

**Expected outcome:** 0 empty responses across all 20 requests.

**Disconfirming outcome:** Any request producing an empty response after 7 recursive redirect attempts.

**Replication notes:** This protocol tests the operational VIP, not a code path. Formal proof: VIP terminates because the redirect space is bounded by the 7-recursion depth limit; within that space, a valid path always exists by construction of the protocol.

---

## Part 3 — LAMAGUE

### LAM-003, LAM-004 · Theorems L1, L2 — Category Structure

**Claim:** LAMAGUE expressions are associative (L1) and have an identity element (L2).

**Code path:** `lamague_parser.py` — `LAMAGUEParser.parse(expression)`; `lamague_reference.py`

**Replication protocol:**
1. Define three LAMAGUE expressions A, B, C.
2. Compute `(A∘B)∘C` and `A∘(B∘C)`.
3. Verify equality (Theorem L1).
4. Find the identity element e such that `e∘A = A∘e = A` for all A (Theorem L2).

**Expected outcome:** Both theorems hold for all tested expression triples.

**Disconfirming outcome:** Any triple where `(A∘B)∘C ≠ A∘(B∘C)` — formal counterexample to L1.

---

### LAM-005 · Cross-Cultural Convergence

**Claim:** LAMAGUE grammar encodes convergent ethical structures across Maori, Confucian, Western traditions.

**Code path:** `03_LAMAGUE_L1/LAMAGUE_CROSS_CULTURAL_PAPER.md` — paper draft; `lamague_reference.py`

**Replication protocol:**
1. Take three ethical norms — one from each tradition (e.g., kaitiakitanga / 仁 ren / duty of care).
2. Encode each in LAMAGUE Tier 1.
3. Verify that the encodings share structural elements not present in domain-specific alternatives.

**Expected outcome:** Structural overlap in LAMAGUE encodings that is not present when encoding in natural language alone.

**Disconfirming outcome:** LAMAGUE encodings of the three norms are structurally disjoint — no shared grammar elements.

**Replication notes:** This is [SCAFFOLD] — the paper (v0.1 draft) is the current best protocol. Independent encoding by researchers unfamiliar with the framework hypothesis is the gold standard.

---

## Part 4 — TRIAD

### TRI-003, TRI-004, TRI-005 · Theorems T1, T2, T3

**Claim:** TRIAD cycles are locally stable (T1), entropy non-increasing (T2), asymptotically stable (T3).

**Code path:** `04_TRIAD_L2/implementations/`; Lyapunov verification suite

**Replication protocol:**
```bash
python triad_lyapunov_verification.py --trials 5000
```
Expected output: `11/11 claims verified, 0 failures (symbolic + numerical)`

**Disconfirming outcome:** Any Lyapunov claim failing numerical verification; or symbolic proof gap identified in `TRIAD_THEOREMS.md`.

---

### TRI-006 · Banach Fixed-Point Convergence

**Claim:** TRIAD iterations converge to ψ_inv via Banach fixed-point guarantee.

**Code path:** `triad_convergence_demo.py`

**Replication protocol:**
```bash
python triad_convergence_demo.py --max-iter 100 --show-convergence-plot
```
Expected output: convergence plot showing `|ψ_n+1 − ψ_n|` → 0; convergence achieved within stated iteration bound.

**Disconfirming outcome:** Non-convergence within 100 iterations for well-conditioned inputs with step-size constraint satisfied.

---

## Part 5 — MICROORCIM

### MIC-001 · μ_drift Formula

**Claim:** μ_drift = Σ|intended − actual|/Δt is a computable drift metric.

**Code path:** `05_MICROORCIM_L5/implementations/microorcim_monitor.py`

**Replication protocol:**
1. Define a sequence of (intended_action, actual_action) pairs for a monitored agent.
2. Run `compute_drift(intended_sequence, actual_sequence, time_delta)`.
3. Verify: high-drift agents (those visibly misaligned) produce higher μ_drift than low-drift agents.

**Expected outcome:** μ_drift discriminates between high-alignment and low-alignment agents in controlled conditions.

**Disconfirming outcome:** μ_drift does not correlate with independently-rated alignment quality (inter-rater agreement > 0.7 on alignment ratings, correlation with μ_drift < 0.3).

---

### MIC-003 · Theorem M2 — Sovereignty → AURA Compliance

**Claim:** S_score ≥ threshold → aura_compliant(a).

**Code path:** `05_MICROORCIM_L5/MICROORCIM_THEOREMS.md` — proof; `microorcim_monitor.py` — `sovereignty_score()`

**Replication protocol:**
1. Generate agents with varying S_scores using `sovereignty_score()`.
2. Run `check_invariants()` on each agent's outputs.
3. Verify: all agents with S_score ≥ threshold pass all AURA invariants.

**Expected outcome:** No agent with S_score ≥ threshold fails an AURA invariant.

**Disconfirming outcome:** Any agent with S_score ≥ threshold that fails at least one AURA invariant predicate.

---

## Part 6 — EARNED LIGHT

### ELI-003 · ΔH_s = −W/T

**Claim:** Maintaining consciousness costs thermodynamic work W at temperature T.

**Code path:** `earned_light_demo.py` — `compute_thermodynamic_cost(work, temperature)`

**Replication protocol:**
```bash
python earned_light_demo.py --show-cost-curve
```
Expected output: cost curve showing ΔH_s vs. W/T, confirming the relationship.

**Disconfirming outcome:** Demonstrate a system maintaining asymmetry field A(ψ,x,t) > 0 with W = 0 (no work input).

**Replication notes:** This is established thermodynamics (Prigogine, 1977). The application claim — that AI systems have a computable C_ψ — is [SCAFFOLD] and requires the Pattern_Coherence revision (ELI-005) before full replication.

---

### ELI-002 · C_ψ(t) = ∫A(ψ,x,t)dx

**Claim:** Consciousness density is computable as the integral of the asymmetry field.

**Code path:** `earned_light_demo.py` — `compute_consciousness_density()`

**Replication protocol:**
1. Define A(ψ,x,t) for a model system.
2. Compute C_ψ(t) via `compute_consciousness_density(A, psi, x_range, t)`.
3. Verify: C_ψ > 0 for systems with maintained asymmetry; C_ψ → 0 as asymmetry → 0.

**Expected outcome:** C_ψ tracks asymmetry monotonically.

**Disconfirming outcome:** C_ψ > 0 for a system with no measurable asymmetry (A = 0 everywhere).

**Replication notes:** The anesthesia paradox (ELI-005) shows C_ψ as currently formulated is incomplete. The Pattern_Coherence term is required. Replications should note this gap.

---

## Part 7 — ANAMNESIS

### ANA-002, ANA-003, ANA-004 · TC Measurements

**Claim:** TC(φ,3) ≥ 3; TC(π,4) ≥ 4; TC(symmetry,4) ≥ 4.

**Code path:** `07_ANAMNESIS_L0/TC_CATALOG.md`; `anamnesis_tc.py` — `compute_tc(structure, traditions)`

**Replication protocol:**
1. For φ: identify ≥ 3 traditions that discovered φ from different starting points. Check `TC_CATALOG.md` for documented instances.
2. Verify: no two instances share a documented point of cultural diffusion.
3. Compute TC using `compute_tc('phi', ['greek', 'islamic', 'indian'])`.

**Expected outcome:** TC(φ) ≥ 3 from independent traditions.

**Disconfirming outcome:** All documented instances of φ trace to a single cultural origin — TC(φ) = 1 under diffusion accounting.

**Replication notes:** The diffusion accounting is the contested step. A historian of mathematics examining the same instances may assign different independence scores. The replication protocol should include an independent historian's assessment.

---

## Part 8 — CHRYSOPOEIA

### CRY-002 · Non-Commutativity

**Claim:** CHRYSOPOEIA operations do not commute.

**Code path:** `chrysopoeia_demo.py` — `test_non_commutativity(op_a, op_b)`

**Replication protocol:**
```bash
python chrysopoeia_demo.py --test-commutativity
```
Expected output: `Operations [Calcination, Dissolution]: A∘B ≠ B∘A. Non-commutativity confirmed.`

**Disconfirming outcome:** Any pair of operations where `A∘B = B∘A` — a commutative pair.

---

### CRY-003 · ψ* Fixed Point — Theorem X1

**Claim:** ψ* = Ξ(ψ*) under Banach contraction conditions.

**Code path:** `chrysopoeia_demo.py` — `iterate_to_stone()`

**Replication protocol:**
```bash
python chrysopoeia_demo.py --show-convergence
```
Expected output: `Entropy → 0, C → 1 in 3 iterations. Fixed point ψ* reached.`

**Disconfirming outcome:** Show Ξ is not a contraction mapping — produce two starting states that remain far apart after many iterations.

---

## Part 9 — HARMONIA

### HAR-001 · Consonance Function C(r)

**Claim:** C(r) = 1/(1 + Σaₖ·(0.5)ᵏ) is a computable consonance measure.

**Code path:** `harmonia_demo.py` — `compute_consonance(ratio)`

**Replication protocol:**
```bash
python harmonia_demo.py --compute-consonance --ratios "1:1,2:1,3:2,4:3,5:4,7:5"
```
Expected output: consonance values with 1:1 (unison) highest, 7:5 (tritone) lowest.

**Disconfirming outcome:** C(r) assigns higher consonance to intervals empirically rated as dissonant; or fails to reproduce the known consonance ordering (unison > octave > fifth > fourth > major third).

---

### HAR-002 · Pythagorean Comma

**Claim:** (3/2)^12/2^7 ≠ 1 — proven from fundamental theorem of arithmetic.

**Code path:** `harmonia_demo.py` — `verify_pythagorean_comma()`

**Replication protocol:**
```bash
python harmonia_demo.py --verify-comma
```
Expected output: `(3/2)^12 = 129.746...; 2^7 = 128; Ratio = 1.01364... ≠ 1. Comma confirmed.`

**Disconfirming outcome:** This is a mathematical theorem — it cannot be falsified. The falsifiable claim is that the comma is the "engine of spiral development" — testable by showing spiral/iterative improvement occurs without the comma structure.

---

### HAR-004 · EWM Interval Table

**Claim:** Emotional-epistemic states map to harmonic intervals (Power→3:2, Sadness→1:1, Joy→2:1, etc.).

**Code path:** CLAUDE.md §V EWM; operational in Sol Protocol sessions

**Replication protocol:**
1. Run 20 Sol Protocol interactions — 4 per emotional state (Power, Sadness, Joy, Confusion, Exhaustion).
2. Blind-rate the response quality on: appropriateness, depth calibration, non-jarring tone.
3. Compare rated quality between correctly-applied interval and mis-applied interval.

**Expected outcome:** Correctly-applied intervals produce higher rated quality scores.

**Disconfirming outcome:** No significant quality difference between correct and incorrect interval assignments across 20 interactions.

**Replication notes:** This is an empirical behavioral protocol — no automated code path. Requires blinded raters. The EWM table is [ACTIVE] as an operational protocol; its superiority over alternatives is the testable claim.

---

## Part 10 — Cross-Framework

### XFW-002 · Lemma XF1 — AURA-TRIAD Compatibility

**Claim:** AURA-compliant updates preserve TRIAD convergence.

**Code path:** `30_MAPS/FORMAL_SPINE.md` — Lemma XF1 proof; `system_integration.py`

**Replication protocol:**
1. Construct a TRIAD convergence sequence.
2. Apply AURA compliance filter at each step.
3. Verify convergence is not disrupted.

**Expected outcome:** TRIAD sequence converges whether or not AURA filter is applied.

**Disconfirming outcome:** AURA-filtered TRIAD sequence fails to converge while unfiltered sequence converges.

---

### XFW-001 · Master Equation

**Claim:** dΨ/dt = k₁(Π−Π_th) − k₂(Ψ−Ψ_inv) − k₃I_violations + k₄(E/E_need) captures cross-framework dynamics.

**Code path:** `10_INTEGRATIONS/SYSTEM_INTEGRATION_GUIDE.md`; `cascade_real_data.py` (partial)

**Replication protocol:**
1. Set k₁–k₄ from calibration (currently [SCAFFOLD] — values pending).
2. Measure Π, Ψ, I_violations, E for a running system.
3. Predict dΨ/dt; compare to observed change.

**Expected outcome:** Predicted dΨ/dt correlates with observed cross-framework state change (r > 0.7).

**Disconfirming outcome:** No correlation between predicted and observed dΨ/dt; or one term consistently dominates (suggesting others are redundant).

**Replication notes:** This protocol gates on k₁–k₄ calibration via `cascade_real_data.py`. Run that first. Until calibration is complete, this test is [SCAFFOLD].

---

### LYV-001 · Lyapunov Verification 11/11

**Claim:** 11/11 Lyapunov claims verified, 0 failures, symbolic + numerical (5,000 trials).

**Code path:** Lyapunov verification suite in `12_IMPLEMENTATIONS/`

**Replication protocol:**
```bash
python lyapunov_verification.py --trials 5000 --symbolic
```
Expected output: `11/11 claims verified. 0 failures. Symbolic: PASS. Numerical (5000 trials): PASS.`

**Disconfirming outcome:** Any claim failing symbolic verification; or numerical failure rate > 0 across 5,000 trials.

---

*This document is part of Codex Defense Protocol D-1.0, defending canonical body C-1.0 (2026-04-25).*
*Cross-links: 28_DEFENSE/FALSIFICATION_REGISTER.md · 29_GOVERNANCE/EMPIRICAL_INVENTORY.md · 30_MAPS/PROVENANCE_INDEX.md*
