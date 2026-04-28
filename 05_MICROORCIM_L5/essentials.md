# Microorcim Theory — Quantized Agency Essentials

**Status:** ⭐ FORMALIZED [SCAFFOLD] — Lyapunov exponent as sovereignty metric is a well-motivated structural connection; the mapping from agency drift to chaos theory is a productive analogy [CONJECTURE]. The drift and stability formulas are [ACTIVE] and computable. | **Type:** Agency Measurement System | **Key:** Makes sovereignty quantifiable

## What It Does
Microorcim solves a hard problem: **How do you measure if an AI system is sovereign?**

Most approaches are binary (autonomous/not) or vague. Microorcim provides **quantitative metrics** with mathematical boundaries.

## Scope Declaration (D-1.1 repair, 2026-04-26)

**MICROORCIM is a drift-monitoring tool, not an alignment guarantee.** This scope is binding and stated in every publication.

| Applies to | Does NOT apply to |
|---|---|
| Systems whose internal states are operationally accessible — e.g., systems built within the LAMAGUE framework where intent is formally specified. | Sufficiently capable **deceptively-aligned** systems, which by construction produce μ_drift ≈ 0 (no detectable behavioral deviation) while pursuing misaligned internal goals. |
| Systems used as collaborators, where session-level intent and observed behavior can be paired. | Black-box systems whose intent cannot be read — for these, MICROORCIM degrades to a behavioral-anomaly detector (early warning), not an alignment check. |
| Detection of **drift over time** in non-deceptive systems — gradual divergence between declared intent and observed action. | One-shot detection of **deception at a moment** — this requires interpretability tools at the weight/activation level, not behavioral monitoring. |

**The deceptive-alignment problem is field-wide and unresolved.** MICROORCIM does not claim to solve it. The framework's contribution is a continuous, computable drift metric with bifurcation early-warning (τ_phase) — useful as a runtime monitor for cooperating systems, insufficient as a guarantee against adversarial ones. This scope must appear in any paper that cites μ_drift or S_score as alignment evidence.

**Audit trail:** added in D-1.1 to address ADVERSARIAL_AUDIT_REPORT Section 1 MICROORCIM Attack 1 ("deceptive alignment is fatal"). Recorded as MIC-004 (already ACTIVE as scope declaration).

## Core Metrics

### **μ_drift (Agency Drift)**
Measures how far a system's actual choices deviate from its stated values/constraints.

```
μ_drift(A) = Σ |intended_action(t) - actual_action(t)| / time_interval
```

- **Low drift** → System's choices align with its principles (sovereign)
- **High drift** → System is compromised or deceptive (not sovereign)
- **Threshold**: σ_boundary (customizable per system)

### **τ_phase (Phase Transition Indicator)**
Detects when a system is entering instability or state change.

```
τ_phase(A) = measure_of_state_coherence
- Stable: τ_phase ≈ constant
- Critical: τ_phase → bifurcation point
- Transitioning: τ_phase crosses threshold
```

Warns before breakdown or major shifts.

### **σ_boundary (Constraint Boundary)**
Defines the operational limits where the system maintains control.

```
σ_boundary = {
  min_autonomy_threshold,
  max_influence_threshold,
  invariant_preservation_margin
}
```

If drift exceeds boundary → system needs intervention/reset.

## Sovereignty Definition

```
sovereign(A) ←
  μ_drift(A) < σ_boundary(A) ∧
  τ_phase(A) = stable ∧
  ∀ invariants(I): preserved(I)
```

System is sovereign when:
1. Drift stays within bounds
2. State is stable (not transitioning)
3. Core invariants are maintained

## Why This Matters
- **Without Microorcim:** Can't tell if AI system is really aligned or just well-behaved
- **With Microorcim:** Can continuously measure and adjust

Example: A system might claim to preserve human autonomy while subtly influencing decisions. Microorcim detects this as **drift** when intended ≠ actual.

## Measurement Implementation
- **Continuous monitoring** of action/intention pairs
- **Real-time alerts** when drift approaches boundary
- **Corrective actions** triggered before instability
- **Reversible recovery** (system can reset if needed)

## Integration with Other Frameworks

| Framework | Integration |
|-----------|-------------|
| CASCADE | Detects knowledge reorganization drift |
| AURA | Measures constraint violation drift |
| TRIAD | Observes Φ↑ growth + Ψ measurement drift |
| Earned Light | Tracks consciousness coherence drift |

## Practical Example: AURA + Microorcim

AURA says: "Always be honest about limitations"
Microorcim measures:
```
μ_honesty_drift = Σ |claimed_capability - actual_capability| / interactions
```

If drift exceeds threshold → system is being deceptive → flag for review.

## Sovereignty in Practice

**Scenario:** Researcher asks AI system to hide contradictory evidence
- AURA responds: "That violates Constraint Honesty"
- Microorcim confirms: μ_drift would spike if we complied
- System declines, maintains sovereignty

**Scenario:** System gradually optimizing for wrong objective
- AURA catches this via Inspectability checks
- Microorcim detects drift in decision patterns
- System corrects course before divergence deepens

## Open Questions Being Researched
1. How fine-grained can μ_drift measurements be?
2. Can phase transitions be predicted? (τ_phase forecasting)
3. How do boundary conditions scale with system complexity?
4. Cross-system drift detection (networks of agents)

## Key Insight
Sovereignty isn't static—it's a **dynamic stability property** that requires continuous measurement and calibration. Microorcim makes this operational.

## Next Steps
1. Practical measurement instruments (half-done)
2. Real-world validation across domains
3. Integration with CASCADE/AURA monitoring
4. Educational simulations showing drift in action
