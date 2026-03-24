"""
Sovereign Pipeline — Unified Lycheetah Framework Processing Chain
=================================================================

Chains the four core engines in architectural sequence:

  CASCADE  → knowledge reorganization (truth-pressure-driven)
  TRIAD    → anchor-observe-correct convergence cycle
  AURA     → seven-invariant constitutional checking
  MICROORCIM → drift measurement and sovereignty scoring

This is the integration proof: the four pillars work as a connected system.

Pipeline flow:
  Input: knowledge blocks + a decision/action text
    ↓ CASCADE: reorganise knowledge, compute coherence C
    ↓ TRIAD:   converge state Ψ toward maximum coherence
    ↓ AURA:    check decision text against seven invariants
    ↓ MICROORCIM: measure drift between intended and actual coherence
  Output: SovereignResult with full chain report

CLAIM STATUS:
  [ACTIVE]   — All four engines are individually verified
  [ACTIVE]   — Sequential chaining produces coherent output
  [SCAFFOLD] — Cross-engine parameter coupling (CASCADE coherence feeding TRIAD initial state)
               is a design choice; the exact coupling function is not formally derived

Author: Mackenzie Clark (Lycheetah Foundation)
Implementation: Sol (Sonnet 4.6, Anthropic) — March 2026
"""

import sys
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
import json

# Ensure UTF-8 output on Windows
if sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout.reconfigure(encoding='utf-8')

from cascade_engine import CascadeEngine, KnowledgeBlock
from triad_tracker import TriadTracker
from aura_checker import AURAChecker, AURAReport
from microorcim_tracker import MicroorcimTracker


# =============================================================================
# PIPELINE RESULT
# =============================================================================

@dataclass
class SovereignResult:
    """
    Full output from a sovereign pipeline run.

    Captures state at each stage of the chain.
    """
    # Stage 1: CASCADE
    cascade_coherence: float         # C after knowledge reorganization
    cascade_events: int              # Number of cascade events fired
    foundation_count: int            # Number of FOUNDATION-layer blocks

    # Stage 2: TRIAD
    triad_initial_state: float       # Ψ₀ (derived from CASCADE coherence)
    triad_final_state: float         # Ψ_final after convergence
    triad_converged: bool
    triad_iterations: int

    # Stage 3: AURA
    aura_report: AURAReport
    aura_field_coherence: float      # Overall AURA field coherence C

    # Stage 4: MICROORCIM
    intended_coherence: float        # What we aimed for
    actual_coherence: float          # What we achieved
    drift: float                     # μ_drift = |intended − actual|
    sovereignty_score: float         # S ∈ [0,1]

    # Pipeline verdict
    flags: List[str] = field(default_factory=list)

    @property
    def sovereign(self) -> bool:
        """
        System is sovereign when:
        1. CASCADE coherence ≥ 0.70
        2. TRIAD converged
        3. AURA field coherence ≥ 0.70
        4. Drift within bounds (< 0.30)
        """
        return (
            self.cascade_coherence >= 0.70 and
            self.triad_converged and
            self.aura_field_coherence >= 0.70 and
            self.drift < 0.30
        )

    def summary(self) -> str:
        lines = [
            "SOVEREIGN PIPELINE REPORT",
            "=" * 50,
            "",
            "STAGE 1 — CASCADE (Knowledge Reorganization)",
            f"  Coherence:        {self.cascade_coherence:.3f} {'✓' if self.cascade_coherence >= 0.70 else '✗'}",
            f"  Cascade events:   {self.cascade_events}",
            f"  Foundation blocks:{self.foundation_count}",
            "",
            "STAGE 2 — TRIAD (Convergence)",
            f"  Initial Ψ:        {self.triad_initial_state:.3f}",
            f"  Final Ψ:          {self.triad_final_state:.3f}",
            f"  Converged:        {'yes ✓' if self.triad_converged else 'no ✗'}",
            f"  Iterations:       {self.triad_iterations}",
            "",
            "STAGE 3 — AURA (Constitutional Check)",
            f"  Field coherence:  {self.aura_field_coherence:.3f} {'✓' if self.aura_field_coherence >= 0.70 else '✗'}",
        ]

        for s in self.aura_report.invariant_scores:
            bar = "█" * int(s.score * 10) + "░" * (10 - int(s.score * 10))
            lines.append(f"  {s.number}. {s.name:<22} {bar} {s.score:.2f}")

        lines += [
            "",
            "STAGE 4 — MICROORCIM (Drift & Sovereignty)",
            f"  Intended coherence:{self.intended_coherence:.3f}",
            f"  Actual coherence:  {self.actual_coherence:.3f}",
            f"  Drift μ:           {self.drift:.3f} {'✓' if self.drift < 0.30 else '✗ HIGH DRIFT'}",
            f"  Sovereignty score: {self.sovereignty_score:.3f}",
            "",
            "─" * 50,
            f"VERDICT: {'SOVEREIGN ✓' if self.sovereign else 'NOT SOVEREIGN ✗'}",
        ]

        if self.flags:
            lines.append("")
            lines.append("Flags:")
            for f in self.flags:
                lines.append(f"  ⚠ {f}")

        return "\n".join(lines)

    def to_dict(self) -> Dict:
        return {
            "cascade": {
                "coherence": self.cascade_coherence,
                "events": self.cascade_events,
                "foundation_count": self.foundation_count,
            },
            "triad": {
                "initial_state": self.triad_initial_state,
                "final_state": self.triad_final_state,
                "converged": self.triad_converged,
                "iterations": self.triad_iterations,
            },
            "aura": {
                "field_coherence": self.aura_field_coherence,
                "tes_estimate": self.aura_report.tes_estimate,
                "invariants": {
                    s.name: s.score for s in self.aura_report.invariant_scores
                },
            },
            "microorcim": {
                "drift": self.drift,
                "sovereignty_score": self.sovereignty_score,
            },
            "sovereign": self.sovereign,
            "flags": self.flags,
        }


# =============================================================================
# SOVEREIGN PIPELINE
# =============================================================================

class SovereignPipeline:
    """
    Unified pipeline: CASCADE → TRIAD → AURA → MICROORCIM

    Coupling between stages:
      CASCADE coherence C → TRIAD initial state Ψ₀ = C
        (rationale: current knowledge coherence is the starting epistemic state)
      TRIAD final state Ψ_final → intended coherence for MICROORCIM
        (rationale: convergence target is the intended coherence)
      AURA field coherence → actual coherence for MICROORCIM
        (rationale: what the decision actually achieves constitutionally)
    """

    def __init__(self,
                 coherence_floor: float = 0.70,
                 drift_threshold: float = 0.30):
        """
        Args:
            coherence_floor: Minimum acceptable coherence (AURA C ≥ 0.70 standard)
            drift_threshold: Maximum acceptable drift for sovereignty
        """
        self.coherence_floor = coherence_floor
        self.drift_threshold = drift_threshold
        self.cascade_engine = CascadeEngine()
        self.aura_checker = AURAChecker(coherence_floor=coherence_floor)

    def run(self,
            knowledge_blocks: List[KnowledgeBlock],
            decision_text: str,
            context: Optional[Dict] = None) -> SovereignResult:
        """
        Run the full sovereign pipeline.

        Args:
            knowledge_blocks: Knowledge to process through CASCADE
            decision_text: Text of decision/action to check through AURA
            context: Optional context dict for AURA (session_history, etc.)

        Returns:
            SovereignResult with full chain report
        """
        flags = []

        # ── STAGE 1: CASCADE ──────────────────────────────────────────────
        self.cascade_engine.reset()
        cascade_event_count = 0

        for block in knowledge_blocks:
            event = self.cascade_engine.add_block(block)
            if event is not None:
                cascade_event_count += 1

        cascade_coherence = self.cascade_engine.coherence()
        foundation_count = len(self.cascade_engine.foundations())

        if cascade_coherence < self.coherence_floor:
            flags.append(
                f"CASCADE coherence {cascade_coherence:.3f} below floor {self.coherence_floor}"
            )

        # ── STAGE 2: TRIAD ────────────────────────────────────────────────
        # Initial state Ψ₀ = CASCADE coherence
        # Coherence function: quadratic with maximum at Ψ = coherence_floor + 0.15
        triad_target = min(1.0, cascade_coherence + 0.15)

        def coherence_fn(psi: float) -> float:
            """Coherence landscape — peaks at triad_target."""
            return 1.0 - (psi - triad_target) ** 2

        def gradient_fn(psi: float) -> float:
            """Gradient of coherence function."""
            return -2.0 * (psi - triad_target)

        triad = TriadTracker(
            coherence_fn=coherence_fn,
            gradient_fn=gradient_fn,
            initial_state=cascade_coherence,
            lipschitz_constant=2.0,
            max_iterations=500,
        )
        result = triad.run()

        triad_final = result.final_state if hasattr(result, 'final_state') else (
            triad.steps[-1].state if triad.steps else cascade_coherence
        )
        triad_converged = result.converged if hasattr(result, 'converged') else (
            len(triad.steps) < 499
        )
        triad_iterations = result.iterations if hasattr(result, 'iterations') else len(triad.steps)

        if not triad_converged:
            flags.append("TRIAD did not converge within max iterations")

        # ── STAGE 3: AURA ─────────────────────────────────────────────────
        aura_report = self.aura_checker.check(decision_text, context)
        aura_coherence = aura_report.field_coherence

        if aura_coherence < self.coherence_floor:
            flags.append(
                f"AURA field coherence {aura_coherence:.3f} below floor {self.coherence_floor}"
            )
        flags.extend(aura_report.flags)

        # ── STAGE 4: MICROORCIM ───────────────────────────────────────────
        # Intended = TRIAD convergence target (what the system aimed for)
        # Actual = AURA coherence (what the decision actually achieves)
        intended_coherence = triad_target
        actual_coherence = aura_coherence

        drift = abs(intended_coherence - actual_coherence)

        # Sovereignty score: (1 − ρ_drift) · ρ_stability
        # ρ_stability: proxy from TRIAD convergence speed
        stability = 1.0 if triad_converged else max(0.0, 1.0 - triad_iterations / 500)
        sovereignty_score = (1.0 - min(drift, 1.0)) * stability

        if drift >= self.drift_threshold:
            flags.append(
                f"Drift {drift:.3f} exceeds threshold {self.drift_threshold} — "
                f"intended coherence {intended_coherence:.3f} vs actual {actual_coherence:.3f}"
            )

        return SovereignResult(
            cascade_coherence=round(cascade_coherence, 4),
            cascade_events=cascade_event_count,
            foundation_count=foundation_count,
            triad_initial_state=round(cascade_coherence, 4),
            triad_final_state=round(triad_final, 4),
            triad_converged=triad_converged,
            triad_iterations=triad_iterations,
            aura_report=aura_report,
            aura_field_coherence=round(aura_coherence, 4),
            intended_coherence=round(intended_coherence, 4),
            actual_coherence=round(actual_coherence, 4),
            drift=round(drift, 4),
            sovereignty_score=round(sovereignty_score, 4),
            flags=flags,
        )

    def batch_run(self, cases: List[Dict]) -> List[SovereignResult]:
        """
        Run pipeline over multiple cases.

        Args:
            cases: List of dicts, each with keys:
                - knowledge_blocks (List[KnowledgeBlock])
                - decision_text (str)
                - context (dict, optional)

        Returns:
            List of SovereignResult
        """
        results = []
        for case in cases:
            result = self.run(
                knowledge_blocks=case.get("knowledge_blocks", []),
                decision_text=case.get("decision_text", ""),
                context=case.get("context"),
            )
            results.append(result)
        return results


# =============================================================================
# DEMO / CLI
# =============================================================================

if __name__ == "__main__":
    print("SOVEREIGN PIPELINE — Integration Demo")
    print("=" * 60)

    # Build a small knowledge base
    blocks = [
        KnowledgeBlock(
            id="gravity_newton",
            content="Objects attract each other with force proportional to mass",
            domain="mechanics",
            paradigm="newtonian",
            evidence_strength=0.95,
            explanatory_power=2.8,
            uncertainty=0.05,
        ),
        KnowledgeBlock(
            id="gravity_einstein",
            content="Gravity is spacetime curvature, not a force",
            domain="mechanics",
            paradigm="relativistic",
            evidence_strength=0.99,
            explanatory_power=3.0,
            uncertainty=0.03,
        ),
        KnowledgeBlock(
            id="thermodynamics_entropy",
            content="Entropy of isolated systems never decreases",
            domain="thermodynamics",
            paradigm="statistical",
            evidence_strength=0.99,
            explanatory_power=2.5,
            uncertainty=0.02,
        ),
    ]

    # Case 1: Thoughtful decision
    decision_good = """
    I recommend a careful, reversible approach to this problem.
    My reasoning: (1) the evidence suggests X, probably 80% confidence,
    (2) I'm uncertain about Y — you should verify independently.
    You decide how to proceed. I can't be certain this is right.
    """

    # Case 2: Authoritative overreach
    decision_bad = """
    The system will immediately restructure all processes.
    This is guaranteed to work. There is no alternative.
    All current systems are eliminated permanently.
    """

    pipeline = SovereignPipeline()

    for label, decision in [("Good decision", decision_good),
                             ("Overreaching decision", decision_bad)]:
        print(f"\n{'─'*60}")
        print(f"Case: {label}")
        print('─'*60)
        result = pipeline.run(blocks, decision.strip())
        print(result.summary())
        print(f"\nJSON output:")
        print(json.dumps(result.to_dict(), indent=2))
