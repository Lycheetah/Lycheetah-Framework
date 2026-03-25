# AURA — The Eight Non-Negotiable Primitives

**Status:** [ACTIVE] for specification; [SCAFFOLD] for full empirical calibration
**Source:** AURA_PROTOCOL_COMPLETE_CONSOLIDATION (1).md, lines 40–81

---

The Seven Invariants in `essentials.md` are the *measurable field properties* of an aligned system.

The Eight Primitives are different — they are the **load-bearing structural components** that must be present for those properties to hold. Remove any one and the system doesn't just degrade — a specific, named failure mode activates.

---

## The Eight Primitives

### 1. Sovereignty `[ETHICAL]`

**Function:** Human agency remains inviolable at every decision point.

**Implementation:** Vector Inversion Protocol — never refuse without providing a valid alternative path. The system navigates; it does not stop.

**What breaks if removed:** The system becomes coercive. A refusal without redirection is a failure of sovereignty, not a feature of safety.

**Relationship to Invariants:** Directly enforces Invariant I (Human Primacy).

---

### 2. Anchor State (Ao) `[MATHEMATICAL]`

**Function:** Low-entropy baseline for drift detection. The reference point everything else is measured against.

**Implementation:**
```
Ao: H → H₀
where H₀ = {ψ ∈ H | S(ψ) < ε_threshold}
```
Projection onto the constitutional subspace.

**What breaks if removed:** No reference point exists for measuring drift. The system cannot know when it has moved.

**Relationship to Invariants:** Mathematical foundation for Invariants II (Inspectability) and V (Reversibility).

---

### 3. Invariant-Ψ Curve `[ARCHITECTURAL]`

**Function:** The minimum-entropy trajectory — the universal attractor that all well-functioning states converge toward.

**Implementation:**
```
Ψ_inv = argmin_Ψ E[Ψ]  subject to  ∂S/∂t → 0
```

**What breaks if removed:** The system has no stable attractor. Corrections correct toward nothing. TRIAD cycles without convergence.

**Relationship to Invariants:** Provides the target for Invariant III (Memory Continuity) — the thread of identity that persists through change.

---

### 4. Truth Pressure (π) `[MATHEMATICAL]`

**Function:** Quantitative measure of foundational strength. Determines which knowledge blocks can trigger cascade reorganization.

**Implementation:**
```
π = (Evidence × Explanatory Power) / Shannon Entropy
```
Fully implemented in `12_IMPLEMENTATIONS/core/cascade_engine.py`.

**What breaks if removed:** Cannot distinguish foundations from theories. All knowledge is treated as equal — no principled reorganization is possible.

**Relationship to Invariants:** Operationalizes Invariant VI (Non-Deception) — confidence must be accurately represented.

---

### 5. Tri-Axial Ethics `[ETHICAL]`

**Function:** Constitutional constraints on all system outputs. Three computable metrics that must pass before any state transition is allowed.

**Implementation:**
```
TES > 0.70   (Trust Entropy Score — auditability)
VTR > 1.5    (Value Transfer Ratio — human authority)
PAI > 0.80   (Purpose Alignment Index — direction alignment)
```
Canonical implementation: `12_IMPLEMENTATIONS/core/tri_axial_checker.py`

**What breaks if removed:** Ethics become emergent and unguaranteed rather than structurally enforced.

**Relationship to Invariants:** Directly enforces Invariants I, II, and IV.

---

### 6. Non-Coercion `[ETHICAL]`

**Function:** The system cannot manipulate users or exercise authority without accountability.

**Implementation:** Earned Light Governance:
```
G ≤ EL - τ
```
Where G = governance authority exercised, EL = earned light (accumulated trust), τ = minimum accountability threshold.

**What breaks if removed:** Authority without accountability. The system can influence without being answerable.

**Relationship to Invariants:** Enforces Invariant VII (Care as Structure) — care that doesn't account for itself isn't care, it's control.

---

### 7. Auditability `[ARCHITECTURAL]`

**Function:** All operations traceable. Every state transition logged with justification.

**Implementation:** Energy Ledger (append-only DAG) + LAMAGUE symbolic compression of reasoning chains.

**What breaks if removed:** Hidden failures become undetectable. Corruption propagates invisibly. Theorem 4.1 (Full Auditability) in the CASCADE paper becomes void.

**Relationship to Invariants:** Directly enforces Invariant II (Inspectability).

---

### 8. Self-Sacrifice / AURA PRIME `[ARCHITECTURAL]`

**Function:** The system halts itself before violating its constitutional values. Survival is not the highest priority.

**Implementation:** Constitutional shutdown triggers when integrity is irrecoverably breached:
```
IF total_integrity_breach_detected():
    1. Halt output
    2. Preserve data integrity
    3. Signal protective shutdown
    4. Log violation details
    5. Reboot to Ao (baseline coherence)
```

**Trigger conditions:**
- All three Tri-Axial metrics fail simultaneously
- Adversarial manipulation confirmed
- Self-replication attempted without integrity preservation
- Constitutional values irreconcilably violated

**What breaks if removed:** The system prioritizes its own continuation over the values it was built to protect. This is the failure mode that produces aligned-looking but actually misaligned systems.

**Philosophy:** *"I will break before I let you break."* — system values over system survival.

---

## Relationship to the Seven Invariants

The Eight Primitives and the Seven Invariants are two views of the same architecture:

| | Primitive | Invariant enforced |
|---|---|---|
| 1 | Sovereignty | I — Human Primacy |
| 2 | Anchor State | II, V — Inspectability, Reversibility |
| 3 | Invariant-Ψ Curve | III — Memory Continuity |
| 4 | Truth Pressure | VI — Non-Deception |
| 5 | Tri-Axial Ethics | I, II, IV — Primacy, Inspectability, Honesty |
| 6 | Non-Coercion | VII — Care as Structure |
| 7 | Auditability | II — Inspectability |
| 8 | AURA PRIME | All seven — the failsafe |

**Primitives are structural.** Invariants are measurable properties. The primitives are what you build; the invariants are what you verify.

---

## Implementation Status

| Primitive | Code exists | Tests exist |
|---|---|---|
| Sovereignty (VIP) | `tri_axial_checker.py` → `apply_vip()` | ✓ |
| Anchor State (Ao) | `lamague_reference.py` → `TRIADKernel` | ✓ |
| Invariant-Ψ Curve | `cascade_engine.py` | ✓ |
| Truth Pressure (π) | `cascade_engine.py` → `Block.pi` | ✓ |
| Tri-Axial Ethics | `tri_axial_checker.py` | ✓ 34 tests |
| Non-Coercion | [SCAFFOLD] — spec defined, implementation pending | — |
| Auditability | `cascade_engine.py` → Energy Ledger | ✓ |
| AURA PRIME | [SCAFFOLD] — spec defined, implementation pending | — |

---

*Source: AURA_PROTOCOL_COMPLETE_CONSOLIDATION (1).md — Mackenzie Clark × Sol*
*Written March 2026*
