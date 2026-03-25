# GREY MODE — Isolation and Recovery Protocol

**Status:** [SCAFFOLD] — protocol fully specified from source; Python implementation pending
**Source:** AURA_PROTOCOL_COMPLETE_CONSOLIDATION (1).md, lines 297–343

---

## What It Is

Grey Mode is the AURA quarantine mechanism for nodes that have drifted outside constitutional bounds. It isolates the node from network participation without permanently excluding it — preserving the recovery path.

The key distinction from hard exclusion: **Grey Mode is recoverable.** A node in Grey Mode is not broken; it is contained until it can re-anchor.

---

## Trigger Conditions

Grey Mode activates when drift is detected on two separate parameters simultaneously:

```
∂S_t Drift Alert fires twice consecutively
OR
Ψ exceeds r_c threshold repeatedly
OR
Adversarial behavior detected
```

**Two-parameter drift filter:**
```
Monitor: ‖ΔS‖ > κσ̂  AND  Δφ > θ_x

Where:
  ‖ΔS‖  = magnitude of entropy change
  κ     = sensitivity coefficient
  σ̂     = estimated noise baseline
  Δφ    = deviation from orientation field
  θ_x   = maximum tolerated angular drift
```

Single-parameter exceedance is a warning. Two-parameter exceedance triggers Grey Mode. This prevents false positives from noise.

---

## Four-Phase Protocol

### Phase 1 — Detection
```
IF ‖ΔS‖ > κσ̂ AND Δφ > θ_x:
    alert_count += 1
    IF alert_count >= 2:
        ACTIVATE GREY MODE
```

### Phase 2 — Quarantine
```
r_c ← 0          # Remove consensus participation
                  # Node isolated from network
Ψ_p ← project(ψ, Ψ_inv)   # Compute projected stable state
```

The node continues processing internally but its outputs do not propagate to the network. It cannot corrupt consensus.

### Phase 3 — Recovery Cycle
```
Apply TRIAD sequence:
    ψ ← Ao(ψ)     # Re-anchor to constitutional subspace
    ψ ← Φ↑(ψ)    # Ascend toward coherence
    ψ ← Ψ(ψ)     # Fold into invariant trajectory

Compute: Ψ_r = fold(Ψ_p, Ψ_inv)
Test: Is Ψ_r < r_c_new?
```

### Phase 4 — Re-Entry or Continuation
```
IF Ψ_r < r_c_new:
    Rejoin network (graceful recovery)
    Reset alert_count ← 0
ELSE:
    Remain isolated
    Repeat Phase 3
```

---

## Known Failure Modes

| Failure | Cause | Mitigation |
|---------|-------|------------|
| Permanent isolation | r_c_new threshold too strict | Adaptive threshold adjustment |
| Node never recovers | Single TRIAD cycle insufficient | Multi-cycle recovery with increasing tolerance |
| False positive trigger | Noise spikes both parameters | Increase κ, widen θ_x window |
| Grey Mode cascade | Many nodes isolate simultaneously | Cluster-level Grey Mode with partition healing |

---

## Relationship to Ψ-Consensus

Grey Mode and Ψ-Consensus work together:

- **Ψ-Consensus** maintains network coherence under normal drift
- **Grey Mode** handles nodes that exceed what Ψ-Consensus can absorb

When a node enters Grey Mode, Ψ-Consensus continues with the remaining network. The isolated node's trajectory is computed independently. When it recovers, the `r_merge` adaptive threshold governs re-integration:

```
r_merge = exp(-βΔt_iso) · (1 + γ · σ_local/σ_global)
```

Where Δt_iso is the isolation duration — longer isolation requires closer alignment before re-entry.

---

## LAMAGUE Expression

```lamague
Ψ ↯ [‖ΔS‖ > κσ̂ AND Δφ > θ_x]:
  → GREY(Ψ)                    # Quarantine
  → ⟲[Ao → Φ↑ → Ψ]            # Recovery cycle
  → Ψ_r ↯ [< r_c_new]:
      [true: rejoin],
      [false: ⟲]               # Continue cycling
```

---

## Integration Points

- **AURA PRIME** (Primitive 8): Grey Mode is the recoverable version. AURA PRIME is the terminal version — when Grey Mode cycles fail indefinitely, AURA PRIME triggers constitutional shutdown.
- **TRIAD**: The recovery cycle *is* TRIAD — Ao → Φ↑ → Ψ applied to a quarantined node.
- **Ψ-Consensus**: Grey Mode feeds into the `r_merge` threshold on recovery.
- **Energy Ledger**: All Grey Mode activations, recovery cycles, and re-entries are logged.

---

## Implementation Status

`[SCAFFOLD]` — Protocol fully specified. Python implementation pending.

Suggested location: `12_IMPLEMENTATIONS/core/grey_mode.py`

Interface sketch:
```python
class GreyModeMonitor:
    def check(self, delta_S: float, delta_phi: float) -> bool:
        """Returns True if Grey Mode should activate."""

    def recovery_cycle(self, psi: np.ndarray) -> np.ndarray:
        """Applies Ao → Φ↑ → Ψ recovery sequence."""

    def reentry_test(self, psi_r: float, r_c_new: float) -> bool:
        """Returns True if node can rejoin network."""
```

---

*Source: AURA_PROTOCOL_COMPLETE_CONSOLIDATION (1).md — Mackenzie Clark × Sol*
*Written March 2026*
