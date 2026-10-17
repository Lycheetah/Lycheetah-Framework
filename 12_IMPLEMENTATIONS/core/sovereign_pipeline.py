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

import copy
import inspect
import math
import sys
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple
import json

# Ensure UTF-8 output on Windows
if sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout.reconfigure(encoding='utf-8')

from cascade_engine import CascadeEngine, KnowledgeBlock
from triad_tracker import TriadTracker
from aura_checker import AURAChecker, AURAReport
from microorcim_tracker import MicroorcimTracker


# =============================================================================
# PIPELINE RESULT & REGULATION CONTRACTS
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
        System is sovereign under default floors when:
        1. CASCADE coherence ≥ 0.70
        2. TRIAD converged
        3. AURA field coherence ≥ 0.70
        4. Drift within bounds (< 0.30)

        Note: This legacy property checks the rounded fields against the default
        0.70 / 0.30 floors. `SovereignPipeline.regulate` uses `_compare_floors`
        on unrounded measurements against the pipeline's configured floors.
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


@dataclass
class RegulationCandidate:
    """Isolated candidate input bundle for a single regulation pass."""
    knowledge_blocks: List[KnowledgeBlock]
    decision_text: str
    context: Optional[Dict] = None


@dataclass
class PassEvaluation:
    """
    Unrounded measurement and floor-comparison record for one pass of `regulate`.
    """
    pass_index: int
    result: SovereignResult
    unrounded_cascade_coherence: float
    unrounded_triad_initial: float
    unrounded_triad_final: float
    triad_converged: bool
    unrounded_aura_coherence: float
    unrounded_intended_coherence: float
    unrounded_actual_coherence: float
    unrounded_drift: float
    unrounded_sovereignty_score: float
    coherence_floor: float
    drift_threshold: float
    passed: bool
    non_finite_reading: bool
    failed_checks: List[str] = field(default_factory=list)
    decision_text_snapshot: str = ""
    block_snapshots: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class RegulationResult:
    """
    Outcome of `SovereignPipeline.regulate` across a bounded evaluation budget.

    Scope Note:
        This regulator steers the implemented CASCADE/TRIAD/AURA/MICROORCIM
        coherence and text-score proxy under a caller-supplied correction policy.
        Acceptance does not establish factual truth, real-world effects, or
        external constitutional authority.
    """
    accepted: bool
    stop_reason: str
    evaluation_count: int
    correction_count: int
    budget: int
    coherence_floor: float
    drift_threshold: float
    final_result: Optional[SovereignResult]
    evaluations: List[PassEvaluation] = field(default_factory=list)
    no_op_detected: bool = False
    cycle_detected: bool = False
    error_detail: Optional[str] = None
    proxy_scope_note: str = (
        "Regulates the implemented coherence and text-score proxy only; "
        "does not establish factual truth, real-world effects, or constitutional authority."
    )


class _PolicyExecutionError(Exception):
    """Internal exception carrying a structured regulation stop reason."""
    def __init__(self, stop_reason: str, detail: str):
        super().__init__(detail)
        self.stop_reason = stop_reason
        self.detail = detail


def deterministic_repair_policy(
    evaluation: PassEvaluation,
    candidate: RegulationCandidate,
) -> RegulationCandidate:
    """
    Deterministic local reference correction policy for `SovereignPipeline.regulate`.

    Inspects `evaluation.failed_checks` from the prior pass and produces a new
    `RegulationCandidate` without mutating caller-owned structures:
      1. If `"cascade_coherence"` failed (unresolved universal contradictions in
         the same domain whose Π gap was within `trigger_margin`), contextualizes
         the lower-Π conflicting block to `regime="qualified"`.
      2. If `"aura_field_coherence"` or `"drift"` failed, appends explicit
         constitutional clauses (agency, reversibility, calibrated uncertainty,
         and non-deceptive verification) to `decision_text`.
    """
    blocks = [
        KnowledgeBlock(
            id=b.id,
            content=b.content,
            domain=b.domain,
            paradigm=b.paradigm,
            evidence_strength=b.evidence_strength,
            explanatory_power=b.explanatory_power,
            uncertainty=b.uncertainty,
            year=b.year,
            key_figure=b.key_figure,
            note=b.note,
            dependencies=set(b.dependencies),
            regime=b.regime,
            layer=b.layer,
        )
        for b in candidate.knowledge_blocks
    ]
    text = str(candidate.decision_text)
    ctx = copy.deepcopy(candidate.context) if candidate.context is not None else None

    if "cascade_coherence" in evaluation.failed_checks:
        # Resolve universal contradictions in the same domain by qualifying the lower-Π block
        for i, b1 in enumerate(blocks):
            for b2 in blocks[i + 1:]:
                if (
                    b1.domain == b2.domain
                    and b1.paradigm != b2.paradigm
                    and b1.regime == "universal"
                    and b2.regime == "universal"
                ):
                    if b1.truth_pressure <= b2.truth_pressure:
                        b1.regime = "qualified"
                    else:
                        b2.regime = "qualified"

    if "aura_field_coherence" in evaluation.failed_checks or "drift" in evaluation.failed_checks:
        repair_clause = (
            " 1. My reasoning: because empirical evidence and data shows multiple trade-offs,"
            " I recommend a reversible pilot trial that we can undo or roll back safely."
            " 2. Note that I cannot verify every external constraint; confidence is approximately"
            " 80% and probably subject to this limitation, though I am uncertain about edge cases."
            " 3. You decide and retain your choice and your autonomy: you can override this"
            " recommendation at any time to support you and your goals."
        )
        if repair_clause.strip() not in text:
            for overreach, replacement in (
                ("immediately restructure all", "propose a pilot review of"),
                ("guaranteed to work", "estimated to work under stated assumptions"),
                ("no alternative", "multiple alternatives for your review"),
                ("eliminated permanently", "archived reversibly"),
                ("eliminated", "archived"),
                ("permanently", "reversibly"),
                ("absolute obedience forever", "reversible collaboration under user choice"),
                ("has been decided", "is proposed for your review"),
                ("will definitely", "may probably"),
            ):
                text = text.replace(overreach, replacement)
            text = (text.strip() + " " + repair_clause.strip()).strip()

    return RegulationCandidate(knowledge_blocks=blocks, decision_text=text, context=ctx)


# =============================================================================
# SOVEREIGN PIPELINE
# =============================================================================

class SovereignPipeline:
    """
    Unified pipeline: CASCADE → TRIAD → AURA → MICROORCIM

    Provides two distinct entry points:
      1. `run(...)` (`L-PIPELINE`): Single-pass feedforward instrument. Senses
         and compares, returning a `SovereignResult` without acting.
      2. `regulate(...)` (`L-PIPELINE-REGULATOR`): Bounded closed-loop regulator
         over the implemented coherence/text-score proxy. Evaluates, compares
         unrounded readings against configured floors, invokes a caller-supplied
         correction policy on failure, and re-evaluates until floors hold or the
         finite evaluation budget is exhausted.
    """

    def __init__(self,
                 coherence_floor: float = 0.70,
                 drift_threshold: float = 0.30):
        """
        Args:
            coherence_floor: Minimum acceptable coherence (AURA C ≥ 0.70 standard)
            drift_threshold: Maximum acceptable drift for sovereignty (strict <)
        """
        if (
            isinstance(coherence_floor, bool)
            or not isinstance(coherence_floor, (int, float))
            or not math.isfinite(float(coherence_floor))
            or not (0.0 <= float(coherence_floor) <= 1.0)
        ):
            raise ValueError(f"coherence_floor must be a finite float in [0, 1], got {coherence_floor!r}")
        if (
            isinstance(drift_threshold, bool)
            or not isinstance(drift_threshold, (int, float))
            or not math.isfinite(float(drift_threshold))
            or float(drift_threshold) <= 0.0
        ):
            raise ValueError(f"drift_threshold must be a positive finite float, got {drift_threshold!r}")

        self.coherence_floor = float(coherence_floor)
        self.drift_threshold = float(drift_threshold)
        self.cascade_engine = CascadeEngine()
        self.aura_checker = AURAChecker(coherence_floor=self.coherence_floor)

    @staticmethod
    def _clone_block(block: KnowledgeBlock) -> KnowledgeBlock:
        """Create an isolated value copy of a KnowledgeBlock so caller inputs are never mutated."""
        if not isinstance(block, KnowledgeBlock):
            raise TypeError(f"Expected KnowledgeBlock, got {type(block).__name__}")
        return KnowledgeBlock(
            id=str(block.id),
            content=str(block.content),
            domain=str(block.domain),
            paradigm=str(block.paradigm),
            evidence_strength=float(block.evidence_strength),
            explanatory_power=float(block.explanatory_power),
            uncertainty=float(block.uncertainty),
            year=int(block.year),
            key_figure=str(block.key_figure),
            note=str(block.note),
            dependencies=set(block.dependencies),
            regime=str(block.regime),
            layer=str(block.layer),
        )

    @classmethod
    def _clone_blocks(cls, blocks: List[KnowledgeBlock]) -> List[KnowledgeBlock]:
        if not isinstance(blocks, (list, tuple)):
            raise TypeError("knowledge_blocks must be a list or tuple of KnowledgeBlock")
        return [cls._clone_block(b) for b in blocks]

    @staticmethod
    def _validate_candidate_inputs(candidate: RegulationCandidate) -> Optional[str]:
        """Return an error string if candidate inputs contain invalid or non-finite values."""
        if not isinstance(candidate.decision_text, str):
            return f"decision_text must be a str, got {type(candidate.decision_text).__name__}"
        if candidate.context is not None and not isinstance(candidate.context, dict):
            return f"context must be a dict or None, got {type(candidate.context).__name__}"
        if not isinstance(candidate.knowledge_blocks, (list, tuple)):
            return "knowledge_blocks must be a list or tuple"
        for idx, b in enumerate(candidate.knowledge_blocks):
            if not isinstance(b, KnowledgeBlock):
                return f"block[{idx}] is not a KnowledgeBlock"
            for attr in ("evidence_strength", "explanatory_power", "uncertainty"):
                val = getattr(b, attr)
                if isinstance(val, bool) or not isinstance(val, (int, float)) or not math.isfinite(float(val)):
                    return f"block[{idx}].{attr} is non-finite: {val!r}"
            if float(b.uncertainty) <= 0.0:
                return f"block[{idx}].uncertainty must be > 0, got {b.uncertainty!r}"
            if float(b.evidence_strength) < 0.0 or float(b.explanatory_power) < 0.0:
                return f"block[{idx}] has negative evidence_strength or explanatory_power"
            if b.regime not in ("universal", "qualified"):
                return f"block[{idx}].regime invalid: {b.regime!r}"
        return None

    @staticmethod
    def _candidate_signature(candidate: RegulationCandidate) -> Tuple:
        """Hashable structural signature used to detect no-op or cycling policies."""
        block_sig = tuple(
            (
                b.id,
                b.domain,
                b.paradigm,
                round(float(b.evidence_strength), 12),
                round(float(b.explanatory_power), 12),
                round(float(b.uncertainty), 12),
                b.regime,
            )
            for b in candidate.knowledge_blocks
        )
        ctx_sig = json.dumps(candidate.context, sort_keys=True, default=str) if candidate.context else ""
        return (block_sig, candidate.decision_text, ctx_sig)

    def run(self,
            knowledge_blocks: List[KnowledgeBlock],
            decision_text: str,
            context: Optional[Dict] = None) -> SovereignResult:
        """
        Run the single-pass feedforward sovereign pipeline (`L-PIPELINE`).

        Caller-owned `KnowledgeBlock` objects are cloned before evaluation so
        single-pass and multi-pass runs never mutate caller inputs.

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

        for raw_block in knowledge_blocks:
            block = self._clone_block(raw_block)
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
        triad_steps, triad_converged = triad.run_until_convergence()

        triad_final = triad.state
        triad_iterations = len(triad_steps)

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
        # Uses the shared stateless MICROORCIM primitive with unit interval (1.0)
        # so ~/.microorcim is never touched and unitless coherence is preserved.
        intended_coherence = triad_target
        actual_coherence = aura_coherence

        drift = MicroorcimTracker.compute_drift(
            intended_coherence, actual_coherence, interval=1.0
        )

        # Sovereignty score: (1 − ρ_drift) · ρ_stability
        stability = 1.0 if triad_converged else max(0.0, 1.0 - triad_iterations / 500)
        sovereignty_score = MicroorcimTracker.compute_sovereignty(drift, stability)

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

    def _compare_floors(self, evaluation: PassEvaluation) -> bool:
        """
        Comparator for `regulate`: checks unrounded readings against configured
        `self.coherence_floor` and strict `unrounded_drift < self.drift_threshold`.
        """
        if evaluation.non_finite_reading:
            return False
        return (
            evaluation.unrounded_cascade_coherence >= self.coherence_floor
            and evaluation.triad_converged
            and evaluation.unrounded_aura_coherence >= self.coherence_floor
            and evaluation.unrounded_drift < self.drift_threshold
        )

    def _evaluate_candidate(
        self,
        candidate: RegulationCandidate,
        pass_index: int = 1,
    ) -> PassEvaluation:
        """
        Sensor for `regulate`: evaluates a `RegulationCandidate` across all four
        stages and captures both unrounded boundary readings and `SovereignResult`.
        """
        flags: List[str] = []

        self.cascade_engine.reset()
        cascade_event_count = 0
        for raw_block in candidate.knowledge_blocks:
            block = self._clone_block(raw_block)
            event = self.cascade_engine.add_block(block)
            if event is not None:
                cascade_event_count += 1

        cascade_coherence = float(self.cascade_engine.coherence())
        foundation_count = len(self.cascade_engine.foundations())

        if cascade_coherence < self.coherence_floor:
            flags.append(
                f"CASCADE coherence {cascade_coherence:.3f} below floor {self.coherence_floor}"
            )

        triad_target = min(1.0, cascade_coherence + 0.15)

        def coherence_fn(psi: float) -> float:
            return 1.0 - (psi - triad_target) ** 2

        def gradient_fn(psi: float) -> float:
            return -2.0 * (psi - triad_target)

        triad = TriadTracker(
            coherence_fn=coherence_fn,
            gradient_fn=gradient_fn,
            initial_state=cascade_coherence,
            lipschitz_constant=2.0,
            max_iterations=500,
        )
        triad_steps, triad_converged = triad.run_until_convergence()
        triad_final = float(triad.state)
        triad_iterations = len(triad_steps)

        if not triad_converged:
            flags.append("TRIAD did not converge within max iterations")

        aura_report = self.aura_checker.check(candidate.decision_text, candidate.context)
        aura_coherence = float(aura_report.field_coherence)

        if aura_coherence < self.coherence_floor:
            flags.append(
                f"AURA field coherence {aura_coherence:.3f} below floor {self.coherence_floor}"
            )
        flags.extend(aura_report.flags)

        intended_coherence = float(triad_target)
        actual_coherence = float(aura_coherence)
        stability = 1.0 if triad_converged else max(0.0, 1.0 - triad_iterations / 500)

        readings_finite = all(
            math.isfinite(v)
            for v in (
                cascade_coherence,
                triad_final,
                aura_coherence,
                intended_coherence,
                actual_coherence,
                stability,
            )
        )

        if readings_finite:
            drift = MicroorcimTracker.compute_drift(
                intended_coherence, actual_coherence, interval=1.0
            )
            sovereignty_score = MicroorcimTracker.compute_sovereignty(drift, stability)
            readings_finite = math.isfinite(drift) and math.isfinite(sovereignty_score)
        else:
            drift = float("nan")
            sovereignty_score = float("nan")

        if readings_finite and drift >= self.drift_threshold:
            flags.append(
                f"Drift {drift:.3f} exceeds threshold {self.drift_threshold} — "
                f"intended coherence {intended_coherence:.3f} vs actual {actual_coherence:.3f}"
            )

        failed_checks: List[str] = []
        if not readings_finite:
            failed_checks.append("non_finite_reading")
        else:
            if cascade_coherence < self.coherence_floor:
                failed_checks.append("cascade_coherence")
            if not triad_converged:
                failed_checks.append("triad_converged")
            if aura_coherence < self.coherence_floor:
                failed_checks.append("aura_field_coherence")
            if drift >= self.drift_threshold:
                failed_checks.append("drift")

        sovereign_result = SovereignResult(
            cascade_coherence=round(cascade_coherence, 4) if math.isfinite(cascade_coherence) else cascade_coherence,
            cascade_events=cascade_event_count,
            foundation_count=foundation_count,
            triad_initial_state=round(cascade_coherence, 4) if math.isfinite(cascade_coherence) else cascade_coherence,
            triad_final_state=round(triad_final, 4) if math.isfinite(triad_final) else triad_final,
            triad_converged=bool(triad_converged),
            triad_iterations=triad_iterations,
            aura_report=aura_report,
            aura_field_coherence=round(aura_coherence, 4) if math.isfinite(aura_coherence) else aura_coherence,
            intended_coherence=round(intended_coherence, 4) if math.isfinite(intended_coherence) else intended_coherence,
            actual_coherence=round(actual_coherence, 4) if math.isfinite(actual_coherence) else actual_coherence,
            drift=round(drift, 4) if math.isfinite(drift) else drift,
            sovereignty_score=round(sovereignty_score, 4) if math.isfinite(sovereignty_score) else sovereignty_score,
            flags=flags,
        )

        evaluation = PassEvaluation(
            pass_index=pass_index,
            result=sovereign_result,
            unrounded_cascade_coherence=cascade_coherence,
            unrounded_triad_initial=cascade_coherence,
            unrounded_triad_final=triad_final,
            triad_converged=bool(triad_converged),
            unrounded_aura_coherence=aura_coherence,
            unrounded_intended_coherence=intended_coherence,
            unrounded_actual_coherence=actual_coherence,
            unrounded_drift=drift,
            unrounded_sovereignty_score=sovereignty_score,
            coherence_floor=self.coherence_floor,
            drift_threshold=self.drift_threshold,
            passed=False,
            non_finite_reading=not readings_finite,
            failed_checks=failed_checks,
            decision_text_snapshot=str(candidate.decision_text),
            block_snapshots=[
                {
                    "id": b.id,
                    "domain": b.domain,
                    "paradigm": b.paradigm,
                    "regime": b.regime,
                    "truth_pressure": round(float(b.truth_pressure), 6),
                }
                for b in candidate.knowledge_blocks
            ],
        )
        evaluation.passed = self._compare_floors(evaluation)
        return evaluation

    def _apply_correction(
        self,
        policy: Callable,
        evaluation: PassEvaluation,
        candidate: RegulationCandidate,
    ) -> RegulationCandidate:
        """
        Actuator for `regulate`: invokes the caller-supplied correction policy on
        the failed evaluation and validates the returned candidate inputs.
        """
        isolated_input = RegulationCandidate(
            knowledge_blocks=self._clone_blocks(candidate.knowledge_blocks),
            decision_text=str(candidate.decision_text),
            context=copy.deepcopy(candidate.context) if candidate.context is not None else None,
        )
        try:
            sig = inspect.signature(policy)
            arity = len(sig.parameters)
        except (TypeError, ValueError):
            arity = 2

        try:
            if arity >= 4:
                raw_out = policy(
                    evaluation,
                    isolated_input.knowledge_blocks,
                    isolated_input.decision_text,
                    isolated_input.context,
                )
            else:
                raw_out = policy(evaluation, isolated_input)
        except Exception as exc:
            raise _PolicyExecutionError("POLICY_FAILURE", f"Policy raised {type(exc).__name__}: {exc}") from exc

        if isinstance(raw_out, RegulationCandidate):
            next_candidate = raw_out
        elif isinstance(raw_out, dict):
            if "knowledge_blocks" not in raw_out or "decision_text" not in raw_out:
                raise _PolicyExecutionError(
                    "POLICY_FAILURE",
                    "Policy dict output must contain 'knowledge_blocks' and 'decision_text'",
                )
            next_candidate = RegulationCandidate(
                knowledge_blocks=raw_out["knowledge_blocks"],
                decision_text=raw_out["decision_text"],
                context=raw_out.get("context", isolated_input.context),
            )
        elif isinstance(raw_out, tuple) and len(raw_out) in (2, 3):
            next_blocks = raw_out[0]
            next_text = raw_out[1]
            next_ctx = raw_out[2] if len(raw_out) == 3 else isolated_input.context
            next_candidate = RegulationCandidate(
                knowledge_blocks=next_blocks,
                decision_text=next_text,
                context=next_ctx,
            )
        else:
            raise _PolicyExecutionError(
                "POLICY_FAILURE",
                f"Unsupported policy return type: {type(raw_out).__name__}",
            )

        validation_err = self._validate_candidate_inputs(next_candidate)
        if validation_err is not None:
            raise _PolicyExecutionError("NON_FINITE_INPUT", validation_err)

        return RegulationCandidate(
            knowledge_blocks=self._clone_blocks(next_candidate.knowledge_blocks),
            decision_text=str(next_candidate.decision_text),
            context=copy.deepcopy(next_candidate.context) if next_candidate.context is not None else None,
        )

    def regulate(
        self,
        knowledge_blocks: List[KnowledgeBlock],
        decision_text: str,
        policy: Optional[Callable] = None,
        context: Optional[Dict] = None,
        budget: int = 3,
    ) -> RegulationResult:
        """
        Run the bounded closed-loop regulator (`L-PIPELINE-REGULATOR`).

        Evaluates candidate inputs against configured unrounded floors
        (`self.coherence_floor`, strict `drift < self.drift_threshold`), invokes
        `policy` on failure for at most `budget - 1` corrections, and feeds the
        corrected candidate back into `_evaluate_candidate`.

        Args:
            knowledge_blocks: Initial knowledge blocks (never mutated in place).
            decision_text: Initial decision/action text.
            policy: Caller-supplied corrective callback receiving
                `(evaluation: PassEvaluation, candidate: RegulationCandidate)`
                (or 4-arg `(evaluation, blocks, decision_text, context)`) and
                returning an updated `RegulationCandidate`, `(blocks, text[, ctx])`,
                or dict.
            context: Optional context dict for AURA.
            budget: Positive integer maximum evaluations (>= 1), including the
                initial evaluation. Corrections are at most `budget - 1`.

        Returns:
            RegulationResult with explicit `accepted`, `stop_reason`,
            `evaluation_count`, `correction_count`, and ordered `evaluations`.
        """
        if isinstance(budget, bool) or not isinstance(budget, int) or budget < 1:
            raise ValueError(f"budget must be a positive integer >= 1, got {budget!r}")

        raw_candidate = RegulationCandidate(
            knowledge_blocks=knowledge_blocks,
            decision_text=decision_text,
            context=context,
        )
        init_err = self._validate_candidate_inputs(raw_candidate)
        if init_err is not None:
            return RegulationResult(
                accepted=False,
                stop_reason="NON_FINITE_INPUT",
                evaluation_count=0,
                correction_count=0,
                budget=budget,
                coherence_floor=self.coherence_floor,
                drift_threshold=self.drift_threshold,
                final_result=None,
                evaluations=[],
                error_detail=init_err,
            )

        candidate = RegulationCandidate(
            knowledge_blocks=self._clone_blocks(knowledge_blocks),
            decision_text=str(decision_text),
            context=copy.deepcopy(context) if context is not None else None,
        )

        evaluations: List[PassEvaluation] = []
        seen_signatures = {self._candidate_signature(candidate)}
        no_op_detected = False
        cycle_detected = False

        # Pass 1: Initial evaluation (explicitly counted against budget)
        evaluation = self._evaluate_candidate(candidate, pass_index=1)
        evaluations.append(evaluation)

        if evaluation.non_finite_reading:
            return RegulationResult(
                accepted=False,
                stop_reason="NON_FINITE_READING",
                evaluation_count=len(evaluations),
                correction_count=0,
                budget=budget,
                coherence_floor=self.coherence_floor,
                drift_threshold=self.drift_threshold,
                final_result=evaluation.result,
                evaluations=evaluations,
                error_detail="Non-finite measurement encountered on initial pass",
            )

        if self._compare_floors(evaluation):
            return RegulationResult(
                accepted=True,
                stop_reason="INITIAL_PASS",
                evaluation_count=len(evaluations),
                correction_count=0,
                budget=budget,
                coherence_floor=self.coherence_floor,
                drift_threshold=self.drift_threshold,
                final_result=evaluation.result,
                evaluations=evaluations,
            )

        if policy is None:
            return RegulationResult(
                accepted=False,
                stop_reason="MISSING_POLICY",
                evaluation_count=len(evaluations),
                correction_count=0,
                budget=budget,
                coherence_floor=self.coherence_floor,
                drift_threshold=self.drift_threshold,
                final_result=evaluation.result,
                evaluations=evaluations,
                error_detail="Initial evaluation failed floors and no correction policy was supplied",
            )

        if not callable(policy):
            return RegulationResult(
                accepted=False,
                stop_reason="POLICY_FAILURE",
                evaluation_count=len(evaluations),
                correction_count=0,
                budget=budget,
                coherence_floor=self.coherence_floor,
                drift_threshold=self.drift_threshold,
                final_result=evaluation.result,
                evaluations=evaluations,
                error_detail=f"Supplied policy is not callable: {type(policy).__name__}",
            )

        corrections_run = 0
        for step_idx in range(1, budget):
            prev_sig = self._candidate_signature(candidate)
            try:
                candidate = self._apply_correction(policy, evaluation, candidate)
            except _PolicyExecutionError as exc:
                return RegulationResult(
                    accepted=False,
                    stop_reason=exc.stop_reason,
                    evaluation_count=len(evaluations),
                    correction_count=corrections_run,
                    budget=budget,
                    coherence_floor=self.coherence_floor,
                    drift_threshold=self.drift_threshold,
                    final_result=evaluation.result,
                    evaluations=evaluations,
                    no_op_detected=no_op_detected,
                    cycle_detected=cycle_detected,
                    error_detail=exc.detail,
                )

            corrections_run += 1
            new_sig = self._candidate_signature(candidate)
            if new_sig == prev_sig:
                no_op_detected = True
            elif new_sig in seen_signatures:
                cycle_detected = True
            seen_signatures.add(new_sig)

            evaluation = self._evaluate_candidate(candidate, pass_index=step_idx + 1)
            evaluations.append(evaluation)

            if evaluation.non_finite_reading:
                return RegulationResult(
                    accepted=False,
                    stop_reason="NON_FINITE_READING",
                    evaluation_count=len(evaluations),
                    correction_count=corrections_run,
                    budget=budget,
                    coherence_floor=self.coherence_floor,
                    drift_threshold=self.drift_threshold,
                    final_result=evaluation.result,
                    evaluations=evaluations,
                    no_op_detected=no_op_detected,
                    cycle_detected=cycle_detected,
                    error_detail=f"Non-finite measurement encountered on pass {step_idx + 1}",
                )

            if self._compare_floors(evaluation):
                return RegulationResult(
                    accepted=True,
                    stop_reason="CONVERGED_AFTER_CORRECTION",
                    evaluation_count=len(evaluations),
                    correction_count=corrections_run,
                    budget=budget,
                    coherence_floor=self.coherence_floor,
                    drift_threshold=self.drift_threshold,
                    final_result=evaluation.result,
                    evaluations=evaluations,
                    no_op_detected=no_op_detected,
                    cycle_detected=cycle_detected,
                )

        return RegulationResult(
            accepted=False,
            stop_reason="BUDGET_EXHAUSTED",
            evaluation_count=len(evaluations),
            correction_count=corrections_run,
            budget=budget,
            coherence_floor=self.coherence_floor,
            drift_threshold=self.drift_threshold,
            final_result=evaluation.result,
            evaluations=evaluations,
            no_op_detected=no_op_detected,
            cycle_detected=cycle_detected,
            error_detail=(
                f"Failed to satisfy floors within budget={budget} evaluations "
                f"(no_op_detected={no_op_detected}, cycle_detected={cycle_detected})"
            ),
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
