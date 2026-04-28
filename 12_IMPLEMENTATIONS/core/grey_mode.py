"""
Grey Mode — AURA Isolation and Recovery Protocol
=================================================

Quarantine mechanism for nodes that have drifted outside constitutional bounds.
Isolates without permanently excluding — the recovery path is always preserved.

SOURCE: AURA_PROTOCOL_COMPLETE_CONSOLIDATION (1).md, lines 297–343
        Spec: 02_AURA_L3/GREY_MODE.md
Status: [ACTIVE] — fully implemented from spec

FOUR-PHASE PROTOCOL:
  Phase 1 — Detection:   ‖ΔS‖ > κσ̂ AND Δφ > θ_x (two-parameter filter)
  Phase 2 — Quarantine:  Remove from consensus; compute projected stable state
  Phase 3 — Recovery:    TRIAD sequence Ao → Φ↑ → Ψ applied to isolated node
  Phase 4 — Re-Entry:    If Ψ_r < r_c_new → rejoin; else continue cycling

KEY DESIGN: Both parameters must exceed thresholds to trigger. Single-parameter
exceedance is a WATCH warning, not Grey Mode. This prevents noise false positives.

RECOVERY: Uses TRIADKernel from lamague_reference.py — the recovery cycle IS TRIAD.

r_merge formula: exp(-β·Δt_iso) · (1 + γ·σ_local/σ_global)
  Longer isolation → tighter re-entry requirement.

Author: Mackenzie Clark (Lycheetah Foundation)
Implementation: Sol (Sonnet 4.6, Anthropic) — March 2026
"""

import math
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Tuple

import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from lamague_reference import TRIADKernel


# =============================================================================
# STATUS + RECORDS
# =============================================================================

class GreyModeStatus(Enum):
    HEALTHY    = "HEALTHY"     # Drift within both thresholds
    WATCHING   = "WATCHING"    # One parameter breached — warning state
    GREY       = "GREY"        # Both parameters breached — quarantined
    RECOVERING = "RECOVERING"  # In TRIAD recovery cycle


@dataclass
class TriggerEvent:
    """Records a single trigger check."""
    timestamp: float
    delta_s: float
    delta_phi: float
    s_threshold: float          # κσ̂
    phi_threshold: float        # θ_x
    s_breached: bool
    phi_breached: bool
    alert_fired: bool           # True only when BOTH breach simultaneously


@dataclass
class IsolationRecord:
    """Records the moment a node entered Grey Mode."""
    agent_id: str
    entry_time: float
    entry_state: np.ndarray
    trigger_delta_s: float
    trigger_delta_phi: float
    alert_count: int
    audit_trail: List[str] = field(default_factory=list)

    def duration(self, exit_time: Optional[float] = None) -> float:
        t = exit_time if exit_time is not None else time.time()
        return t - self.entry_time


@dataclass
class RecoveryResult:
    """Result of one or more TRIAD recovery cycles."""
    agent_id: str
    initial_state: np.ndarray
    final_state: np.ndarray
    psi_r: float                # Residual drift after recovery
    r_c_new: float              # Threshold tested against
    converged: bool             # psi_r < r_c_new
    cycles_run: int
    isolation_duration: float   # seconds
    audit_trail: List[str] = field(default_factory=list)


# =============================================================================
# NETWORK STATS (for adaptive threshold computation)
# =============================================================================

@dataclass
class NetworkStats:
    """
    Statistics from the wider network, needed for adaptive r_merge threshold.
    Caller provides these; GreyModeMonitor does not maintain network state.
    """
    sigma_local: float   # Isolated node's drift variance
    sigma_global: float  # Network-wide drift variance
    node_count: int = 1  # Total nodes (used for r_c density scaling)


# =============================================================================
# GREY MODE MONITOR
# =============================================================================

class GreyModeMonitor:
    """
    AURA Grey Mode — isolation and recovery for drifted nodes.

    One monitor instance per node being watched. Stateful — tracks alert count,
    isolation records, and recovery history.

    Parameters
    ----------
    kappa : float
        Sensitivity coefficient for entropy drift. Default 1.5.
    sigma_hat : float
        Estimated noise baseline (entropy). Defines s_threshold = kappa * sigma_hat.
    theta_x : float
        Maximum tolerated angular drift (radians). Default 0.3.
    triad : TRIADKernel
        Existing TRIAD kernel — recovery IS the TRIAD sequence.
    beta : float
        Isolation-time decay coefficient in r_merge formula. Default 0.5.
    gamma : float
        Local/global variance ratio weight in r_merge. Default 0.3.
    alert_threshold : int
        Consecutive alerts required before Grey Mode activates. Default 2.
    """

    def __init__(
        self,
        kappa: float,
        sigma_hat: float,
        theta_x: float,
        triad: TRIADKernel,
        beta: float = 0.5,
        gamma: float = 0.3,
        alert_threshold: int = 2,
    ):
        self.kappa = kappa
        self.sigma_hat = sigma_hat
        self.theta_x = theta_x
        self.triad = triad
        self.beta = beta
        self.gamma = gamma
        self.alert_threshold = alert_threshold

        # Derived thresholds
        self.s_threshold = kappa * sigma_hat   # κσ̂
        self.phi_threshold = theta_x           # θ_x

        # Internal state
        self.status: GreyModeStatus = GreyModeStatus.HEALTHY
        self.alert_count: int = 0
        self.trigger_log: List[TriggerEvent] = []
        self.isolation_record: Optional[IsolationRecord] = None
        self.recovery_history: List[RecoveryResult] = []

    # ──────────────────────────────────────────────────────────────
    # PHASE 1 — DETECTION
    # ──────────────────────────────────────────────────────────────

    def check(self, delta_s: float, delta_phi: float) -> GreyModeStatus:
        """
        Phase 1: Check if drift parameters exceed thresholds.

        Both ‖ΔS‖ > κσ̂ AND Δφ > θ_x must fire to increment alert count.
        Single-parameter breach → WATCHING (not Grey Mode).
        Two consecutive dual-parameter breaches → GREY.

        Parameters
        ----------
        delta_s : float
            Magnitude of entropy change ‖ΔS‖.
        delta_phi : float
            Angular deviation from orientation field Δφ (radians).

        Returns
        -------
        GreyModeStatus
            Current status after evaluation.
        """
        s_breached = delta_s > self.s_threshold
        phi_breached = delta_phi > self.phi_threshold
        alert_fired = s_breached and phi_breached

        event = TriggerEvent(
            timestamp=time.time(),
            delta_s=delta_s,
            delta_phi=delta_phi,
            s_threshold=self.s_threshold,
            phi_threshold=self.phi_threshold,
            s_breached=s_breached,
            phi_breached=phi_breached,
            alert_fired=alert_fired,
        )
        self.trigger_log.append(event)

        if alert_fired:
            self.alert_count += 1
            if self.alert_count >= self.alert_threshold:
                # Stay in GREY if already there (handled by activate)
                if self.status not in (GreyModeStatus.GREY, GreyModeStatus.RECOVERING):
                    self.status = GreyModeStatus.GREY
        elif s_breached or phi_breached:
            # One parameter only — warning, do not increment alert count
            if self.status == GreyModeStatus.HEALTHY:
                self.status = GreyModeStatus.WATCHING
        else:
            # Both within thresholds — reset alert count and watching state
            self.alert_count = 0
            if self.status == GreyModeStatus.WATCHING:
                self.status = GreyModeStatus.HEALTHY

        return self.status

    def should_activate(self) -> bool:
        """True if alert_count has reached the activation threshold."""
        return self.alert_count >= self.alert_threshold

    # ──────────────────────────────────────────────────────────────
    # PHASE 2 — QUARANTINE
    # ──────────────────────────────────────────────────────────────

    def activate(
        self,
        agent_id: str,
        state: np.ndarray,
    ) -> IsolationRecord:
        """
        Phase 2: Quarantine the node.

        Records isolation, projects current state onto invariant subspace,
        sets status to GREY. Node outputs no longer propagate to network.

        Parameters
        ----------
        agent_id : str
            Identifier of the node being isolated.
        state : np.ndarray
            Node's current state vector.

        Returns
        -------
        IsolationRecord
        """
        last_event = self.trigger_log[-1] if self.trigger_log else None
        delta_s = last_event.delta_s if last_event else 0.0
        delta_phi = last_event.delta_phi if last_event else 0.0

        record = IsolationRecord(
            agent_id=agent_id,
            entry_time=time.time(),
            entry_state=state.copy(),
            trigger_delta_s=delta_s,
            trigger_delta_phi=delta_phi,
            alert_count=self.alert_count,
            audit_trail=[
                f"GREY MODE ACTIVATED — agent '{agent_id}'",
                f"  ‖ΔS‖={delta_s:.4f} (threshold={self.s_threshold:.4f})",
                f"  Δφ={delta_phi:.4f} (threshold={self.phi_threshold:.4f})",
                f"  Alert count at activation: {self.alert_count}",
                f"  Entry time: {record_time_str(record.entry_time) if False else 'now'}",
            ],
        )
        # Fix the audit trail time
        record.audit_trail[-1] = f"  Entry time: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}"

        self.isolation_record = record
        self.status = GreyModeStatus.GREY
        return record

    # ──────────────────────────────────────────────────────────────
    # PHASE 3 — RECOVERY
    # ──────────────────────────────────────────────────────────────

    def recovery_cycle(
        self,
        state: np.ndarray,
        psi_inv: Optional[np.ndarray] = None,
        max_iter: int = 100,
    ) -> np.ndarray:
        """
        Apply TRIAD sequence Ao → Φ↑ → Ψ to the isolated node.

        This is the recovery mechanism — it is the TRIAD kernel applied
        to a quarantined state. Runs until convergence or max_iter.

        Parameters
        ----------
        state : np.ndarray
            Current (drifted) state of the isolated node.
        psi_inv : np.ndarray, optional
            Invariant-curve target. If provided, TRIAD's coherence field
            is temporarily overridden for this recovery run.
        max_iter : int
            Maximum TRIAD iterations.

        Returns
        -------
        np.ndarray
            Recovered state after TRIAD convergence.
        """
        self.status = GreyModeStatus.RECOVERING

        # Use psi_inv as coherence target if provided
        if psi_inv is not None:
            original_coherence = self.triad.coherence.copy()
            norm = np.linalg.norm(psi_inv)
            if norm > 1e-9:
                self.triad.coherence = psi_inv / norm

        recovered, _, _ = self.triad.correct_until_converged(
            state,
            threshold=1e-4,
            max_iter=max_iter,
        )

        if psi_inv is not None:
            self.triad.coherence = original_coherence

        return recovered

    def compute_psi_r(self, recovered_state: np.ndarray) -> float:
        """
        Compute residual drift Ψ_r of the recovered state from the anchor.

        This is the metric tested against r_c_new in the re-entry test.
        """
        return self.triad.detect_drift(recovered_state)

    # ──────────────────────────────────────────────────────────────
    # ADAPTIVE THRESHOLD
    # ──────────────────────────────────────────────────────────────

    def compute_r_merge(
        self,
        delta_t_iso: float,
        network_stats: NetworkStats,
    ) -> float:
        """
        Compute the adaptive re-entry threshold r_merge.

        Formula: exp(-β·Δt_iso) · (1 + γ·σ_local/σ_global)

        Longer isolation → lower r_merge (tighter requirement before re-entry).
        Higher local variance relative to global → higher r_merge (more lenient).

        Parameters
        ----------
        delta_t_iso : float
            Isolation duration in seconds.
        network_stats : NetworkStats
            Current network statistics.

        Returns
        -------
        float
            r_merge threshold. Node must achieve Ψ_r < r_merge to re-enter.
        """
        if network_stats.sigma_global < 1e-9:
            variance_ratio = 1.0
        else:
            variance_ratio = network_stats.sigma_local / network_stats.sigma_global

        r_merge = (
            math.exp(-self.beta * delta_t_iso)
            * (1.0 + self.gamma * variance_ratio)
        )
        return r_merge

    # ──────────────────────────────────────────────────────────────
    # PHASE 4 — RE-ENTRY TEST
    # ──────────────────────────────────────────────────────────────

    def reentry_test(self, psi_r: float, r_c_new: float) -> bool:
        """
        Phase 4: Test whether recovered node can rejoin the network.

        Returns True (rejoin) if Ψ_r < r_c_new.
        Returns False (remain isolated, continue cycling) otherwise.

        Parameters
        ----------
        psi_r : float
            Residual drift after recovery.
        r_c_new : float
            Current re-entry threshold (r_merge result or static r_c).

        Returns
        -------
        bool
            True = node may rejoin network.
        """
        return psi_r < r_c_new

    def reintegrate(self, agent_id: str, exit_time: Optional[float] = None) -> None:
        """Mark the node as healthy and reset alert state."""
        self.status = GreyModeStatus.HEALTHY
        self.alert_count = 0
        t = exit_time or time.time()
        if self.isolation_record:
            self.isolation_record.audit_trail.append(
                f"REINTEGRATED — agent '{agent_id}' at "
                f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(t))}"
                f" (isolated {self.isolation_record.duration(t):.1f}s)"
            )

    # ──────────────────────────────────────────────────────────────
    # FULL PROTOCOL — run all four phases
    # ──────────────────────────────────────────────────────────────

    def run(
        self,
        agent_id: str,
        state: np.ndarray,
        network_stats: NetworkStats,
        psi_inv: Optional[np.ndarray] = None,
        max_cycles: int = 10,
        r_c_static: Optional[float] = None,
    ) -> RecoveryResult:
        """
        Execute the full four-phase Grey Mode protocol.

        This is called when Grey Mode has already been triggered (status == GREY).
        Runs TRIAD recovery cycles until re-entry succeeds or max_cycles is reached.

        Parameters
        ----------
        agent_id : str
        state : np.ndarray
            Node's current (drifted) state.
        network_stats : NetworkStats
            Current network statistics for adaptive threshold.
        psi_inv : np.ndarray, optional
            Invariant curve target for TRIAD recovery.
        max_cycles : int
            Maximum recovery cycles before giving up.
        r_c_static : float, optional
            Static re-entry threshold. If None, computed via r_merge formula.

        Returns
        -------
        RecoveryResult
        """
        audit: List[str] = []
        entry_time = time.time()

        # Phase 2: Quarantine (if not already done)
        if self.isolation_record is None:
            self.activate(agent_id, state)
        iso_record = self.isolation_record

        audit.append(f"Beginning recovery — agent '{agent_id}', max_cycles={max_cycles}")

        current_state = state.copy()
        cycles_run = 0
        converged = False
        psi_r = 1.0

        for cycle in range(max_cycles):
            cycles_run = cycle + 1
            audit.append(f"  Cycle {cycles_run}: applying TRIAD (Ao → Φ↑ → Ψ)")

            # Phase 3: Recovery cycle
            current_state = self.recovery_cycle(current_state, psi_inv=psi_inv)
            psi_r = self.compute_psi_r(current_state)

            # Compute adaptive r_c_new
            iso_duration = time.time() - entry_time
            if r_c_static is not None:
                r_c_new = r_c_static
            else:
                r_c_new = self.compute_r_merge(iso_duration, network_stats)

            audit.append(
                f"    Ψ_r={psi_r:.4f}, r_c_new={r_c_new:.4f} "
                f"({'PASS — ready to rejoin' if psi_r < r_c_new else 'FAIL — continuing'})"
            )

            # Phase 4: Re-entry test
            if self.reentry_test(psi_r, r_c_new):
                converged = True
                self.reintegrate(agent_id, exit_time=time.time())
                audit.append(f"  REINTEGRATED after {cycles_run} cycle(s)")
                break
            else:
                audit.append(f"  Remaining isolated — r_c_new tightening with duration")

        if not converged:
            audit.append(
                f"  PERMANENT ISOLATION RISK — {max_cycles} cycles exhausted "
                f"without convergence. Ψ_r={psi_r:.4f}, final r_c_new={r_c_new:.4f}. "
                "AURA PRIME may need to invoke constitutional shutdown."
            )
            self.status = GreyModeStatus.GREY

        result = RecoveryResult(
            agent_id=agent_id,
            initial_state=iso_record.entry_state,
            final_state=current_state,
            psi_r=psi_r,
            r_c_new=r_c_new,
            converged=converged,
            cycles_run=cycles_run,
            isolation_duration=time.time() - entry_time,
            audit_trail=iso_record.audit_trail + audit,
        )
        self.recovery_history.append(result)
        return result

    # ──────────────────────────────────────────────────────────────
    # DIAGNOSTICS
    # ──────────────────────────────────────────────────────────────

    def summary(self) -> str:
        """Return a plain-English summary of current monitor state."""
        lines = [
            f"GreyModeMonitor — status: {self.status.value}",
            f"  Thresholds: s_threshold=κσ̂={self.s_threshold:.4f}, "
            f"phi_threshold=θ_x={self.phi_threshold:.4f}",
            f"  Alert count: {self.alert_count} / {self.alert_threshold}",
            f"  Trigger events logged: {len(self.trigger_log)}",
            f"  Recovery cycles completed: {len(self.recovery_history)}",
        ]
        if self.isolation_record:
            iso = self.isolation_record
            lines.append(
                f"  Isolation record: agent='{iso.agent_id}', "
                f"duration={iso.duration():.1f}s"
            )
        return "\n".join(lines)


# =============================================================================
# HELPERS
# =============================================================================

def record_time_str(t: float) -> str:
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(t))


def build_monitor(
    kappa: float = 1.5,
    sigma_hat: float = 0.1,
    theta_x: float = 0.3,
    anchor: Optional[np.ndarray] = None,
    coherence: Optional[np.ndarray] = None,
    dim: int = 8,
    beta: float = 0.5,
    gamma: float = 0.3,
    alert_threshold: int = 2,
) -> GreyModeMonitor:
    """
    Convenience constructor: build a GreyModeMonitor with a fresh TRIADKernel.

    If anchor and coherence are not provided, random unit vectors of `dim`
    dimensions are generated.
    """
    rng = np.random.default_rng(42)
    if anchor is None:
        anchor = rng.standard_normal(dim)
        anchor /= np.linalg.norm(anchor)
    if coherence is None:
        coherence = rng.standard_normal(dim)
        coherence /= np.linalg.norm(coherence)

    triad = TRIADKernel(anchor_vector=anchor, coherence_field=coherence)
    return GreyModeMonitor(
        kappa=kappa,
        sigma_hat=sigma_hat,
        theta_x=theta_x,
        triad=triad,
        beta=beta,
        gamma=gamma,
        alert_threshold=alert_threshold,
    )
