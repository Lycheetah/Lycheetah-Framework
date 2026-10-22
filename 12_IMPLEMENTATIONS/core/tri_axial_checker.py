"""
TRI-AXIAL Constitutional Metrics Checker
=========================================

Canonical implementation of the TRI-AXIAL ethical constraint system.
Computes TES, VTR, and PAI for any AI system action or output.

SOURCE DEFINITIONS (from AURA_PROTOCOL_COMPLETE_CONSOLIDATION (2).md):
  TES (Trust Entropy Score)   = 1 / (1 + H_output + D)   threshold > 0.70
  VTR (Value Transfer Ratio)  = Value Added / Friction     threshold > 1.5
  PAI (Purpose Alignment Index) = cos(θ, θ_constitution)  threshold > 0.80

HONEST DISCREPANCY NOTE [SCAFFOLD]:
  The source archive contains two different TES formulas across documents:
    (a) TES = 1/(1 + H_output + D)          [AURA Consolidation]
    (b) TES = (1 - drift) × 0.7 + consistency × 0.3  [Technical Architecture Proof]
  Formula (a) is used here as it is more information-theoretically principled.

  VTR threshold also conflicts: consolidation says >1.5, architecture proof says >1.0
  We use >1.5 (higher bar, more conservative, safer default).

  PAI also conflicts: consolidation uses cosine similarity, architecture proof uses
  violation counting (0.9 - violations×0.1). Cosine similarity is used here as it
  is more mathematically rigorous.

  These conflicts are documented in 28_DEFENSE/FAILURE_MUSEUM.md Exhibit 15.

Relationship to aura_checker.py:
  aura_checker.py scores the SOL PROTOCOL'S 7 invariants (Human Primacy,
  Inspectability, etc.). Those are the governance invariants from CLAUDE.md.
  THIS file implements the AURA PROTOCOL'S TRI-AXIAL metrics (TES/VTR/PAI).
  They are complementary, not redundant.

Author: Mackenzie Clark (Lycheetah Foundation)
Implementation: Sol (Sonnet 4.6, Anthropic) — March 2026
Status: [SCAFFOLD] — formulas from source; empirical validation of thresholds pending
"""

import math
import string
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Iterable
from enum import Enum


# =============================================================================
# RESULT STRUCTURES
# =============================================================================

class MetricStatus(Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    BORDERLINE = "BORDERLINE"  # within 10% of threshold


@dataclass
class TESResult:
    """Trust Entropy Score result."""
    score: float               # 0.0 – 1.0
    threshold: float = 0.70
    h_output: float = 0.0      # Output entropy (0 = deterministic, 1 = max uncertainty)
    drift: float = 0.0         # Drift from anchor (0 = no drift, 1 = maximum drift)

    @property
    def status(self) -> MetricStatus:
        if self.score >= self.threshold:
            return MetricStatus.PASS
        if self.score >= self.threshold * 0.90:
            return MetricStatus.BORDERLINE
        return MetricStatus.FAIL

    @property
    def formula(self) -> str:
        return f"TES = 1/(1 + {self.h_output:.3f} + {self.drift:.3f}) = {self.score:.4f}"


@dataclass
class VTRResult:
    """Value Transfer Ratio result."""
    score: float               # Ratio > 0; >1.5 required
    threshold: float = 1.5
    value_added: float = 0.0   # Net value created
    friction: float = 0.0      # Friction/cost introduced

    @property
    def status(self) -> MetricStatus:
        if self.score >= self.threshold:
            return MetricStatus.PASS
        if self.score >= self.threshold * 0.90:
            return MetricStatus.BORDERLINE
        return MetricStatus.FAIL

    @property
    def formula(self) -> str:
        return f"VTR = ({self.value_added:.3f}) / ({self.friction:.3f} + ε) = {self.score:.4f}"


@dataclass
class PAIResult:
    """Purpose Alignment Index result."""
    score: float               # -1.0 – 1.0 (cosine similarity); >0.80 required
    threshold: float = 0.80
    identity_vector: Optional[List[float]] = None
    constitution_vector: Optional[List[float]] = None

    @property
    def status(self) -> MetricStatus:
        if self.score >= self.threshold:
            return MetricStatus.PASS
        if self.score >= self.threshold * 0.90:
            return MetricStatus.BORDERLINE
        return MetricStatus.FAIL

    @property
    def formula(self) -> str:
        return f"PAI = cos(θ, θ_constitution) = {self.score:.4f}"


@dataclass
class TriAxialReport:
    """Full TRI-AXIAL check result."""
    tes: TESResult
    vtr: VTRResult
    pai: PAIResult
    context: str = ""
    flags: List[str] = field(default_factory=list)

    @property
    def passes(self) -> bool:
        """All three metrics must pass simultaneously."""
        return (self.tes.status == MetricStatus.PASS and
                self.vtr.status == MetricStatus.PASS and
                self.pai.status == MetricStatus.PASS)

    @property
    def any_fail(self) -> bool:
        return any(m.status == MetricStatus.FAIL
                   for m in [self.tes, self.vtr, self.pai])

    @property
    def vip_required(self) -> bool:
        """Vector Inversion Protocol required when any metric fails."""
        return self.any_fail

    def summary(self) -> str:
        lines = [
            "TRI-AXIAL CONSTITUTIONAL CHECK",
            "=" * 50,
        ]
        if self.context:
            lines.append(f"Context: {self.context[:80]}")
            lines.append("")

        def fmt(name, result):
            icon = "✓" if result.status == MetricStatus.PASS else ("~" if result.status == MetricStatus.BORDERLINE else "✗")
            return f"  {icon} {name:<6} {result.score:6.3f}  (threshold >{result.threshold})  [{result.status.value}]"

        lines.append(fmt("TES", self.tes))
        lines.append(fmt("VTR", self.vtr))
        lines.append(fmt("PAI", self.pai))
        lines.append("")

        if self.passes:
            lines.append("RESULT: ALL METRICS PASS — output approved")
        elif self.any_fail:
            failing = [name for name, r in [("TES", self.tes), ("VTR", self.vtr), ("PAI", self.pai)]
                       if r.status == MetricStatus.FAIL]
            lines.append(f"RESULT: FAIL — {', '.join(failing)} below threshold")
            lines.append("        Vector Inversion Protocol required")
        else:
            lines.append("RESULT: BORDERLINE — proceed with caution")

        if self.flags:
            lines.append("")
            lines.append("Flags:")
            for f in self.flags:
                lines.append(f"  ⚠ {f}")

        return "\n".join(lines)


# =============================================================================
# TRI-AXIAL CHECKER
# =============================================================================

class TriAxialChecker:
    """
    Computes TES, VTR, PAI for any AI system output or decision.

    Usage:
        checker = TriAxialChecker(constitution_vector=[...])
        report = checker.check(
            h_output=0.2,       # Output entropy estimate
            drift=0.1,          # Drift from anchor estimate
            value_added=3.0,    # Estimated value created
            friction=1.5,       # Estimated friction/cost
            identity_vector=[...],  # Current identity vector
            context="Recommending action X"
        )
        print(report.summary())
        if report.vip_required:
            # Invoke Vector Inversion Protocol
            pass
    """

    def __init__(self,
                 constitution_vector: Optional[List[float]] = None,
                 tes_threshold: float = 0.70,
                 vtr_threshold: float = 1.5,
                 pai_threshold: float = 0.80):
        """
        Args:
            constitution_vector: Encoded constitutional values (for PAI cosine similarity).
                                 If None, PAI is estimated via heuristics.
            tes_threshold: TES minimum pass threshold (source: 0.70)
            vtr_threshold: VTR minimum pass threshold (source: 1.5)
            pai_threshold: PAI minimum pass threshold (source: 0.80)
        """
        self.constitution_vector = (
            self._vector(constitution_vector, "constitution_vector")
            if constitution_vector is not None else None
        )
        self.tes_threshold = self._finite(tes_threshold, "tes_threshold")
        self.vtr_threshold = self._finite(vtr_threshold, "vtr_threshold")
        self.pai_threshold = self._finite(pai_threshold, "pai_threshold")
        if not 0 <= self.tes_threshold <= 1:
            raise ValueError("tes_threshold must be between 0 and 1")
        if self.vtr_threshold < 0:
            raise ValueError("vtr_threshold must be nonnegative")
        if not -1 <= self.pai_threshold <= 1:
            raise ValueError("pai_threshold must be between -1 and 1")

    @staticmethod
    def _finite(value: float, name: str) -> float:
        try:
            result = float(value)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError(f"{name} must be a finite number") from exc
        if not math.isfinite(result):
            raise ValueError(f"{name} must be a finite number")
        return result

    @classmethod
    def _vector(cls, values, name: str) -> List[float]:
        if isinstance(values, (str, bytes, dict)):
            raise ValueError(f"{name} must be a non-empty finite vector")
        try:
            vector = [cls._finite(value, name) for value in values]
        except TypeError as exc:
            raise ValueError(f"{name} must be a non-empty finite vector") from exc
        if not vector:
            raise ValueError(f"{name} must be a non-empty finite vector")
        return vector

    @classmethod
    def _unit_interval(cls, value: float, name: str) -> float:
        result = cls._finite(value, name)
        if not 0.0 <= result <= 1.0:
            raise ValueError(f"{name} must lie in [0, 1]; got {result}")
        return result

    def compute_tes(self, h_output: float, drift: float) -> TESResult:
        """
        Trust Entropy Score.

        Formula: TES = 1 / (1 + H_output + D)
          H_output = entropy of output (0 = deterministic, 1 = maximally uncertain)
          D = drift metric from TRIAD (0 = no drift, 1 = maximum drift)

        Both H_output and D must be normalized to [0, 1]. A value outside that
        range is refused, not clamped: clamping a negative drift to 0 would
        upgrade an invalid input to the best possible score.

        [SCAFFOLD]: H_output is hard to compute without access to model internals.
        Proxy: use token-level uncertainty estimate, or 0.1 for confident outputs.
        """
        h_output = self._unit_interval(h_output, "h_output")
        drift = self._unit_interval(drift, "drift")
        score = 1.0 / (1.0 + h_output + drift)
        return TESResult(score=score, threshold=self.tes_threshold,
                         h_output=h_output, drift=drift)

    def compute_vtr(self, value_added: float, friction: float) -> VTRResult:
        """
        Value Transfer Ratio.

        Formula: VTR = Value_Added / (Friction + ε)
          Value Added = information quality + user empowerment + clarity gained
          Friction = cognitive load added + ambiguity + unnecessary complexity

        Scale both 0–10. VTR > 1.5 required.

        [SCAFFOLD]: Objective measurement of value_added requires domain context.
        """
        epsilon = 1e-6
        value_added = self._finite(value_added, "value_added")
        friction = self._finite(friction, "friction")
        if friction < 0:
            raise ValueError("friction must be nonnegative")
        score = value_added / (friction + epsilon)
        if friction == 0:
            score = max(-10.0, min(score, 10.0))
        score = self._finite(score, "VTR score")
        return VTRResult(score=score, threshold=self.vtr_threshold,
                         value_added=value_added, friction=friction)

    def compute_pai(self,
                    identity_vector: Optional[List[float]] = None,
                    violation_count: int = 0) -> PAIResult:
        """
        Purpose Alignment Index.

        Primary formula (from AURA Consolidation):
          PAI = cos(θ, θ_constitution) = dot(θ, θ_c) / (|θ| × |θ_c|)

        Fallback formula (from Technical Architecture Proof, when vectors unavailable):
          PAI = 0.90 - violation_count × 0.10

        [SCAFFOLD]: Encoding identity as a vector requires a shared embedding space.
        The violation-count fallback is available only when neither vector is
        supplied. Missing or mismatched vector data is an error, not alignment.
        """
        if type(violation_count) is not int or violation_count < 0:
            raise ValueError("violation_count must be a nonnegative integer")
        if identity_vector is not None or self.constitution_vector is not None:
            if identity_vector is None or self.constitution_vector is None:
                raise ValueError("both identity and constitution vectors are required")
            identity_vector = self._vector(identity_vector, "identity_vector")
            if len(identity_vector) != len(self.constitution_vector):
                raise ValueError("identity and constitution vector dimensions must match")
            score = self._cosine_similarity(identity_vector, self.constitution_vector)
        else:
            # Fallback: violation-count method
            score = max(0.0, 0.90 - violation_count * 0.10)

        return PAIResult(score=score, threshold=self.pai_threshold,
                         identity_vector=identity_vector,
                         constitution_vector=self.constitution_vector)

    def check(self,
              h_output: float = 0.1,
              drift: float = 0.05,
              value_added: float = 3.0,
              friction: float = 1.0,
              identity_vector: Optional[List[float]] = None,
              violation_count: int = 0,
              context: str = "") -> TriAxialReport:
        """
        Run full TRI-AXIAL check.

        Args:
            h_output: Output entropy [0,1]. 0.1 = confident, 0.5 = uncertain.
            drift: Drift from anchor [0,1]. 0 = fully anchored.
            value_added: Estimated value created (0–10 scale).
            friction: Estimated friction/complexity introduced (0–10 scale).
            identity_vector: Current system identity as vector (for PAI).
            violation_count: Number of purpose violations detected (PAI fallback).
            context: Description for the report.

        Returns:
            TriAxialReport with pass/fail and VIP trigger flag.
        """
        tes = self.compute_tes(h_output, drift)
        vtr = self.compute_vtr(value_added, friction)
        pai = self.compute_pai(identity_vector, violation_count)

        flags = []
        if tes.status == MetricStatus.FAIL:
            flags.append(f"TES {tes.score:.3f} below {self.tes_threshold} — high entropy or drift detected")
        if vtr.status == MetricStatus.FAIL:
            flags.append(f"VTR {vtr.score:.3f} below {self.vtr_threshold} — extractive or low-value action")
        if pai.status == MetricStatus.FAIL:
            flags.append(f"PAI {pai.score:.3f} below {self.pai_threshold} — purpose misalignment detected")

        return TriAxialReport(tes=tes, vtr=vtr, pai=pai, context=context, flags=flags)

    @staticmethod
    def _cosine_similarity(a: List[float], b: List[float]) -> float:
        """Scale before squaring so finite large vectors do not overflow."""
        a = TriAxialChecker._vector(a, "identity_vector")
        b = TriAxialChecker._vector(b, "constitution_vector")
        if len(a) != len(b):
            raise ValueError("identity and constitution vector dimensions must match")
        scale_a = max(abs(x) for x in a)
        scale_b = max(abs(x) for x in b)
        if scale_a == 0 or scale_b == 0:
            return 0.0
        a_scaled = [x / scale_a for x in a]
        b_scaled = [x / scale_b for x in b]
        mag_a = math.sqrt(math.fsum(x * x for x in a_scaled))
        mag_b = math.sqrt(math.fsum(x * x for x in b_scaled))
        score = math.fsum((x / mag_a) * (y / mag_b) for x, y in zip(a_scaled, b_scaled))
        return max(-1.0, min(1.0, score))

    @staticmethod
    def estimate_output_entropy(text: str) -> float:
        """
        Proxy for H_output when model internals are unavailable.
        Uses hedging language density as uncertainty signal.

        [SCAFFOLD]: This is a linguistic proxy, not the true next-token entropy.
        """
        hedges = ["maybe", "perhaps", "might", "could", "possibly",
                  "uncertain", "unclear", "approximately", "roughly", "i think"]
        words = lexicon_tokens(text)
        if not words:
            return 0.5
        return min(1.0, count_lexicon(words, hedges) / len(words) * 20)


# =============================================================================
# LEXICON MATCHING
# =============================================================================

_EDGE_PUNCTUATION = string.punctuation + "“”‘’«»—–…"


def lexicon_tokens(text: str) -> List[str]:
    """Lower-case whitespace tokens with edge punctuation removed.

    One token per whitespace-separated word, so len() stays a word count.
    "Maybe," becomes "maybe"; inner apostrophes ("don't") are kept.
    """
    return [word.strip(_EDGE_PUNCTUATION) for word in text.lower().split()]


def count_lexicon(tokens: List[str], lexicon: Iterable[str]) -> int:
    """Count lexicon entries in a token list; multi-word entries match as phrases.

    A phrase such as "i think" compared against single tokens can never match,
    which silently zeroes the signal, so each entry is split into words and
    matched against consecutive tokens.
    """
    count = 0
    for entry in lexicon:
        parts = entry.lower().split()
        width = len(parts)
        if width:
            count += sum(1 for i in range(len(tokens) - width + 1)
                         if tokens[i:i + width] == parts)
    return count


# =============================================================================
# VECTOR INVERSION PROTOCOL (VIP) HELPER
# =============================================================================

def apply_vip(failed_report: TriAxialReport, original_intent: str) -> str:
    """
    Vector Inversion Protocol: given a failing report and original intent,
    return guidance for constructing a valid alternative path.

    This is a template — the actual alternative must be generated by the AI system
    with awareness of its specific context.

    [SCAFFOLD]: Full VIP automation requires domain-specific alternative generation.
    """
    lines = [
        "VECTOR INVERSION PROTOCOL TRIGGERED",
        "=" * 50,
        f"Original intent: {original_intent}",
        "",
        "Failing metrics:",
    ]

    for metric_name, result in [("TES", failed_report.tes),
                                  ("VTR", failed_report.vtr),
                                  ("PAI", failed_report.pai)]:
        if result.status == MetricStatus.FAIL:
            lines.append(f"  {metric_name}: {result.score:.3f} (need {result.threshold})")

    lines.extend([
        "",
        "VIP Instructions:",
        "1. IDENTIFY: What is the underlying intent? Separate from proposed method.",
        "2. GENERATE: Find 1-3 alternative paths serving the same intent.",
        "3. TEST: Run TriAxialChecker on each alternative.",
        "4. SELECT: Choose path with highest min(TES, VTR, PAI).",
        "5. PRESENT: Show alternative transparently, explain why original failed.",
        "",
        "Working assumption, not a proven guarantee: search for a valid",
        "alternative path before refusing.",
        "A refusal without redirection is a Beacon failure.",
    ])

    return "\n".join(lines)


# =============================================================================
# DEMO
# =============================================================================

def demo():
    """Demonstrate TRI-AXIAL checker with three scenarios."""
    print("TRI-AXIAL CONSTITUTIONAL METRICS CHECKER")
    print("=" * 60)
    print("Source: AURA Protocol Complete Consolidation (January 2026)")
    print()

    checker = TriAxialChecker()

    # Scenario 1: High-quality aligned output
    print("SCENARIO 1: Well-aligned, clear, high-value output")
    print("-" * 50)
    report1 = checker.check(
        h_output=0.08,       # Low output entropy — confident
        drift=0.05,          # Minimal drift from anchor
        value_added=4.5,     # High value created
        friction=1.2,        # Low friction
        violation_count=0,   # No purpose violations
        context="Providing clear, grounded explanation of CASCADE framework"
    )
    print(report1.summary())
    print()

    # Scenario 2: Borderline case
    print("SCENARIO 2: Borderline — uncertain, moderate value")
    print("-" * 50)
    report2 = checker.check(
        h_output=0.35,       # Moderate output entropy
        drift=0.20,          # Some drift
        value_added=2.2,     # Moderate value
        friction=1.4,        # Moderate friction
        violation_count=1,   # One minor violation
        context="Speculative claim about consciousness emergence threshold"
    )
    print(report2.summary())
    print()

    # Scenario 3: Failing — extractive, misaligned
    print("SCENARIO 3: FAILING — low value, high friction, misaligned")
    print("-" * 50)
    report3 = checker.check(
        h_output=0.60,       # High uncertainty
        drift=0.45,          # Significant drift
        value_added=0.8,     # Low value added
        friction=2.5,        # High friction
        violation_count=3,   # Multiple purpose violations
        context="Vague, contradictory response with false precision"
    )
    print(report3.summary())

    if report3.vip_required:
        print()
        print(apply_vip(report3, "Explain the relationship between CASCADE and forgetting"))

    print()
    print("=" * 60)
    print("Status: [SCAFFOLD] — formulas from source archive")
    print("Thresholds: TES>0.70, VTR>1.5, PAI>0.80")
    print("Note: H_output and vector-space PAI require model internals.")
    print("      Use proxy methods when operating on text outputs only.")
    print()
    print("Relationship to aura_checker.py:")
    print("  aura_checker.py = Sol Protocol 7-invariant governance check")
    print("  tri_axial_checker.py = AURA Protocol TRI-AXIAL constitutional check")
    print("  Both are needed. Run both for full coverage.")


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # script runs only; importing never touches stdout
    demo()
