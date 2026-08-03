from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
import math
from typing import Any, Iterable


class TruthPressureError(ValueError):
    pass


class PressureState(str, Enum):
    INSUFFICIENT = "INSUFFICIENT"
    OBSERVE = "OBSERVE"
    REVIEW_PRIORITY = "REVIEW_PRIORITY"
    CHALLENGE = "CHALLENGE"
    CASCADE_CANDIDATE = "CASCADE_CANDIDATE"
    HELD_FRONTIER = "HELD_FRONTIER"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class PressureConfig:
    uncertainty_floor: float = 0.10
    cascade_threshold: float = 0.60
    challenge_threshold: float = 0.35
    delta_margin: float = 0.10
    minimum_support: float = 0.55
    minimum_conflict: float = 0.35
    minimum_provenance: float = 0.50
    minimum_independence: float = 0.35
    minimum_reproducibility: float = 0.35
    minimum_source_count: int = 2
    evidence_weights: tuple[float, float, float, float] = (0.30, 0.25, 0.25, 0.20)

    def validate(self) -> None:
        names = (
            "uncertainty_floor", "cascade_threshold", "challenge_threshold",
            "delta_margin", "minimum_support", "minimum_conflict",
            "minimum_provenance", "minimum_independence",
            "minimum_reproducibility",
        )
        for name in names:
            value = getattr(self, name)
            if not math.isfinite(value) or value < 0:
                raise TruthPressureError(f"{name} must be finite and non-negative")
        if self.uncertainty_floor <= 0:
            raise TruthPressureError("uncertainty_floor must be greater than zero")
        for name in (
            "cascade_threshold", "challenge_threshold", "minimum_support",
            "minimum_conflict", "minimum_provenance", "minimum_independence",
            "minimum_reproducibility",
        ):
            if getattr(self, name) > 1:
                raise TruthPressureError(f"{name} must be <= 1")
        if self.challenge_threshold > self.cascade_threshold:
            raise TruthPressureError("challenge_threshold must not exceed cascade_threshold")
        if self.minimum_source_count < 1:
            raise TruthPressureError("minimum_source_count must be at least 1")
        if len(self.evidence_weights) != 4:
            raise TruthPressureError("evidence_weights must contain four values")
        if any((not math.isfinite(w) or w < 0) for w in self.evidence_weights):
            raise TruthPressureError("evidence_weights must be finite and non-negative")
        if sum(self.evidence_weights) <= 0:
            raise TruthPressureError("evidence_weights must have positive total weight")


@dataclass(frozen=True)
class ClaimEvidence:
    evidence_quality: float
    source_independence: float
    reproducibility: float
    provenance_completeness: float
    load_bearing_centrality: float
    scope_of_consequence: float
    contradiction_strength: float
    uncertainty: float
    source_count: int
    claim_id: str = ""
    notes: tuple[str, ...] = field(default_factory=tuple)

    def validate(self) -> None:
        for name in (
            "evidence_quality", "source_independence", "reproducibility",
            "provenance_completeness", "load_bearing_centrality",
            "scope_of_consequence", "contradiction_strength", "uncertainty",
        ):
            value = getattr(self, name)
            if not math.isfinite(value) or not 0 <= value <= 1:
                raise TruthPressureError(f"{name} must be finite and within [0, 1]")
        if self.source_count < 0:
            raise TruthPressureError("source_count cannot be negative")


@dataclass(frozen=True)
class GateResult:
    name: str
    passed: bool
    actual: float | int
    required: float | int
    reason: str


@dataclass(frozen=True)
class PressureVector:
    support: float
    impact: float
    conflict: float
    uncertainty: float

    def export(self) -> dict[str, float]:
        return asdict(self)


@dataclass(frozen=True)
class PressureResult:
    claim_id: str
    vector: PressureVector
    raw_pressure: float
    bounded_pressure: float
    foundation_pressure: float | None
    delta_vs_foundation: float | None
    state: PressureState
    cascade_authorized: bool
    gates: tuple[GateResult, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    interpretation: str
    claim_boundary: tuple[str, ...]

    def export(self) -> dict[str, Any]:
        return {
            "truth_pressure_version": "0.1.0",
            "claim_id": self.claim_id,
            "vector": self.vector.export(),
            "raw_pressure": self.raw_pressure,
            "bounded_pressure": self.bounded_pressure,
            "foundation_pressure": self.foundation_pressure,
            "delta_vs_foundation": self.delta_vs_foundation,
            "state": self.state.value,
            "cascade_authorized": self.cascade_authorized,
            "gates": [asdict(g) for g in self.gates],
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "interpretation": self.interpretation,
            "claim_boundary": list(self.claim_boundary),
        }


def _weighted_geometric_mean(values: Iterable[float], weights: Iterable[float]) -> float:
    values = tuple(values)
    weights = tuple(weights)
    total = sum(weights)
    if total <= 0:
        raise TruthPressureError("weights must have positive total")
    if any(v == 0 for v in values):
        return 0.0
    return math.exp(sum(w * math.log(v) for v, w in zip(values, weights)) / total)


def _round(value: float | None) -> float | None:
    return None if value is None else round(value, 6)


def pressure_vector(claim: ClaimEvidence, config: PressureConfig | None = None) -> PressureVector:
    config = config or PressureConfig()
    config.validate()
    claim.validate()
    support = _weighted_geometric_mean(
        (
            claim.evidence_quality,
            claim.source_independence,
            claim.reproducibility,
            claim.provenance_completeness,
        ),
        config.evidence_weights,
    )
    impact = math.sqrt(claim.load_bearing_centrality * claim.scope_of_consequence)
    return PressureVector(
        support=_round(support),
        impact=_round(impact),
        conflict=_round(claim.contradiction_strength),
        uncertainty=_round(claim.uncertainty),
    )


def scalar_pressure(vector: PressureVector, config: PressureConfig | None = None) -> tuple[float, float]:
    config = config or PressureConfig()
    config.validate()
    raw = vector.support * vector.impact * vector.conflict / (
        config.uncertainty_floor + vector.uncertainty
    )
    bounded = raw / (1.0 + raw)
    return _round(raw), _round(bounded)


def evaluate_claim(
    claim: ClaimEvidence,
    *,
    foundation: ClaimEvidence | None = None,
    config: PressureConfig | None = None,
) -> PressureResult:
    config = config or PressureConfig()
    config.validate()
    claim.validate()

    vector = pressure_vector(claim, config)
    raw, bounded = scalar_pressure(vector, config)

    foundation_pressure = None
    delta = None
    if foundation is not None:
        foundation.validate()
        f_vector = pressure_vector(foundation, config)
        _, foundation_pressure = scalar_pressure(f_vector, config)
        delta = _round(bounded - foundation_pressure)

    gates = (
        GateResult("support", vector.support >= config.minimum_support, vector.support, config.minimum_support, "Evidence support must clear the minimum gate."),
        GateResult("provenance", claim.provenance_completeness >= config.minimum_provenance, claim.provenance_completeness, config.minimum_provenance, "The evidence chain must be inspectable."),
        GateResult("independence", claim.source_independence >= config.minimum_independence, claim.source_independence, config.minimum_independence, "Corroboration must not be purely circular."),
        GateResult("reproducibility", claim.reproducibility >= config.minimum_reproducibility, claim.reproducibility, config.minimum_reproducibility, "The result must have a meaningful replication path."),
        GateResult("source_count", claim.source_count >= config.minimum_source_count, claim.source_count, config.minimum_source_count, "At least the configured number of sources is required."),
        GateResult("conflict", vector.conflict >= config.minimum_conflict, vector.conflict, config.minimum_conflict, "A Cascade candidate must materially challenge the foundation."),
    )

    evidence_gate_names = {"support", "provenance", "independence", "reproducibility", "source_count"}
    evidence_gates_pass = all(g.passed for g in gates if g.name in evidence_gate_names)
    all_gates_pass = all(g.passed for g in gates)
    blockers = [f"{g.name} gate failed: {g.actual} < {g.required}" for g in gates if not g.passed]
    warnings: list[str] = []

    if claim.uncertainty == 0:
        warnings.append("uncertainty is zero; the positive denominator floor prevents infinity")
    if foundation is None:
        warnings.append("no foundation comparator supplied; Cascade authorization is unavailable")

    if vector.impact >= 0.75 and not evidence_gates_pass:
        state = PressureState.HELD_FRONTIER
        interpretation = (
            "The claim may be consequential, but its evidence gates do not permit promotion. "
            "Preserve it as a frontier claim without a numeric sentinel such as 999 or infinity."
        )
    elif bounded < config.challenge_threshold:
        state = PressureState.OBSERVE
        interpretation = "The claim currently exerts low evidence-weighted revision pressure."
    elif not evidence_gates_pass:
        state = PressureState.INSUFFICIENT
        interpretation = "The scalar pressure is not actionable because one or more evidence-quality gates failed."
    elif foundation is None:
        state = PressureState.REVIEW_PRIORITY
        interpretation = "The claim merits review, but cannot become a Cascade candidate without comparison against the current foundation."
    elif (
        bounded >= config.cascade_threshold
        and delta is not None
        and delta >= config.delta_margin
        and all_gates_pass
    ):
        state = PressureState.CASCADE_CANDIDATE
        interpretation = (
            "The claim clears the evidence, conflict, absolute-pressure, and relative-margin gates. "
            "This authorizes structured review for a possible Cascade; it does not automatically rewrite the foundation."
        )
    elif bounded >= config.challenge_threshold:
        state = PressureState.CHALLENGE
        interpretation = "The claim meaningfully challenges the foundation but does not clear every Cascade gate."
    else:
        state = PressureState.OBSERVE
        interpretation = "The claim should remain under observation."

    if state in {PressureState.OBSERVE, PressureState.REVIEW_PRIORITY} and evidence_gates_pass:
        blockers = [b for b in blockers if not b.startswith("conflict gate failed")]

    return PressureResult(
        claim_id=claim.claim_id,
        vector=vector,
        raw_pressure=raw,
        bounded_pressure=bounded,
        foundation_pressure=_round(foundation_pressure),
        delta_vs_foundation=_round(delta),
        state=state,
        cascade_authorized=state == PressureState.CASCADE_CANDIDATE,
        gates=gates,
        blockers=tuple(sorted(set(blockers))),
        warnings=tuple(sorted(set(warnings))),
        interpretation=interpretation,
        claim_boundary=(
            "Truth Pressure is not the probability that a claim is true.",
            "Structural importance cannot substitute for evidence.",
            "Conviction is not an input to the canonical metric.",
            "A Cascade candidate authorizes review, not automatic replacement.",
            "The default thresholds are synthetic calibration defaults, not universal constants.",
            "Zero uncertainty does not produce infinity.",
            "FRONTIER is a maturity state, not the numeric value 999.",
        ),
    )


def compare_claims(challenger: ClaimEvidence, foundation: ClaimEvidence, config: PressureConfig | None = None) -> dict[str, Any]:
    return evaluate_claim(challenger, foundation=foundation, config=config).export()
