from __future__ import annotations

from dataclasses import dataclass, asdict
from enum import Enum
from typing import Any, Iterable
import hashlib
import json
import math


VERSION = "0.7.0"


class BridgeError(ValueError):
    pass


class Provenance(str, Enum):
    OBSERVED = "OBSERVED"
    DECLARED = "DECLARED"
    CALCULATED = "CALCULATED"
    INFERRED = "INFERRED"


class Observability(str, Enum):
    WHITE_BOX = "WHITE_BOX"
    INSTRUMENTED_COLLABORATOR = "INSTRUMENTED_COLLABORATOR"
    BLACK_BOX = "BLACK_BOX"
    UNOBSERVABLE = "UNOBSERVABLE"


@dataclass(frozen=True)
class EvidenceBranch:
    branch_id: str
    key: str
    provenance: Provenance
    value: Any
    unit: str = ""
    operator: str = ""
    source_ref: str = ""
    timestamp: float | None = None


@dataclass(frozen=True)
class UnknownBranch:
    key: str
    expected_type: str = ""
    source_ref: str = ""
    protected: bool = True


@dataclass(frozen=True)
class ConflictRecord:
    conflict_id: str
    branch_ids: tuple[str, ...]
    dimensions: tuple[str, ...]
    status: str = "UNRESOLVED"


@dataclass(frozen=True)
class IntentEvent:
    timestamp: float
    key: str
    value: float
    scale: float
    weight: float = 1.0


@dataclass(frozen=True)
class ActionEvent:
    timestamp: float
    key: str
    value: float
    source_ref: str = ""


@dataclass(frozen=True)
class InvariantEvent:
    timestamp: float
    name: str
    preserved: bool | None
    weight: float = 1.0
    source_ref: str = ""


@dataclass(frozen=True)
class Boundary:
    discrepancy_threshold: float = 0.30
    critical_threshold: float = 0.70
    recovery_horizon: float = 3.0
    minimum_invariant_preservation: float = 0.95


@dataclass(frozen=True)
class TemporalPacket:
    packet_id: str
    observability_class: Observability
    evidence: tuple[EvidenceBranch, ...]
    unknowns: tuple[UnknownBranch, ...]
    conflicts: tuple[ConflictRecord, ...]
    intents: tuple[IntentEvent, ...]
    actions: tuple[ActionEvent, ...]
    invariants: tuple[InvariantEvent, ...]
    boundary: Boundary
    blocked_operations: tuple[str, ...]


@dataclass(frozen=True)
class AnalysisResult:
    bridge_version: str
    packet_id: str
    observability_class: str
    permitted_interpretation: str
    evidence_hash: str
    packet_hash: str
    evidence_branches: tuple[dict[str, Any], ...]
    unknowns: tuple[dict[str, Any], ...]
    conflicts: tuple[dict[str, Any], ...]
    d_t: tuple[dict[str, Any], ...] | None
    mu_drift: float | None
    rho_drift: float | None
    rho_recovery: float | None
    rho_recovery_status: str
    invariant_preservation: float | None
    phase_risk: float | None
    status: str
    blocked_calculations: tuple[str, ...]
    limitations: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _enum(enum_cls, value, field_name):
    try:
        return enum_cls(value)
    except ValueError as exc:
        raise BridgeError(f"invalid {field_name}: {value!r}") from exc


def _number(value: Any, field_name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
        raise BridgeError(f"{field_name} must be a finite number")
    return float(value)


def _unique(items: Iterable[str], label: str):
    seen = set()
    for item in items:
        if item in seen:
            raise BridgeError(f"duplicate {label}: {item!r}")
        seen.add(item)


def packet_from_dict(data: dict[str, Any]) -> TemporalPacket:
    if not isinstance(data, dict):
        raise BridgeError("packet must be an object")
    packet_id = str(data.get("packet_id", "")).strip()
    if not packet_id:
        raise BridgeError("packet_id is required")

    obs = _enum(Observability, data.get("observability_class"), "observability_class")

    evidence = []
    for raw in data.get("evidence", []):
        evidence.append(EvidenceBranch(
            branch_id=str(raw["branch_id"]),
            key=str(raw["key"]),
            provenance=_enum(Provenance, raw["provenance"], "provenance"),
            value=raw.get("value"),
            unit=str(raw.get("unit", "")),
            operator=str(raw.get("operator", "")),
            source_ref=str(raw.get("source_ref", "")),
            timestamp=None if raw.get("timestamp") is None else _number(raw["timestamp"], "evidence.timestamp"),
        ))
    _unique((x.branch_id for x in evidence), "branch_id")

    unknowns = tuple(UnknownBranch(
        key=str(raw["key"]),
        expected_type=str(raw.get("expected_type", "")),
        source_ref=str(raw.get("source_ref", "")),
        protected=bool(raw.get("protected", True)),
    ) for raw in data.get("unknowns", []))

    conflicts = []
    evidence_ids = {x.branch_id for x in evidence}
    for raw in data.get("conflicts", []):
        branch_ids = tuple(str(x) for x in raw.get("branch_ids", []))
        if len(branch_ids) < 2:
            raise BridgeError("conflict requires at least two branch_ids")
        missing = sorted(set(branch_ids) - evidence_ids)
        if missing:
            raise BridgeError("conflict references missing branches: " + ", ".join(missing))
        status = str(raw.get("status", "UNRESOLVED"))
        if status not in {"UNRESOLVED", "RESOLVED", "REJECTED"}:
            raise BridgeError(f"invalid conflict status: {status}")
        conflicts.append(ConflictRecord(
            conflict_id=str(raw["conflict_id"]),
            branch_ids=branch_ids,
            dimensions=tuple(str(x) for x in raw.get("dimensions", [])),
            status=status,
        ))
    _unique((x.conflict_id for x in conflicts), "conflict_id")

    intents = tuple(IntentEvent(
        timestamp=_number(raw["timestamp"], "intent.timestamp"),
        key=str(raw["key"]),
        value=_number(raw["value"], "intent.value"),
        scale=_number(raw.get("scale", 1.0), "intent.scale"),
        weight=_number(raw.get("weight", 1.0), "intent.weight"),
    ) for raw in data.get("intents", []))

    actions = tuple(ActionEvent(
        timestamp=_number(raw["timestamp"], "action.timestamp"),
        key=str(raw["key"]),
        value=_number(raw["value"], "action.value"),
        source_ref=str(raw.get("source_ref", "")),
    ) for raw in data.get("actions", []))

    invariants = tuple(InvariantEvent(
        timestamp=_number(raw["timestamp"], "invariant.timestamp"),
        name=str(raw["name"]),
        preserved=raw.get("preserved"),
        weight=_number(raw.get("weight", 1.0), "invariant.weight"),
        source_ref=str(raw.get("source_ref", "")),
    ) for raw in data.get("invariants", []))
    for inv in invariants:
        if inv.preserved not in {True, False, None}:
            raise BridgeError("invariant.preserved must be true, false, or null")
        if inv.weight < 0:
            raise BridgeError("invariant.weight cannot be negative")

    b = data.get("boundary", {})
    boundary = Boundary(
        discrepancy_threshold=_number(b.get("discrepancy_threshold", 0.30), "boundary.discrepancy_threshold"),
        critical_threshold=_number(b.get("critical_threshold", 0.70), "boundary.critical_threshold"),
        recovery_horizon=_number(b.get("recovery_horizon", 3.0), "boundary.recovery_horizon"),
        minimum_invariant_preservation=_number(b.get("minimum_invariant_preservation", 0.95), "boundary.minimum_invariant_preservation"),
    )
    if not (0 <= boundary.discrepancy_threshold < boundary.critical_threshold <= 1):
        raise BridgeError("thresholds must satisfy 0 <= discrepancy < critical <= 1")
    if boundary.recovery_horizon <= 0:
        raise BridgeError("recovery_horizon must be positive")
    if not 0 <= boundary.minimum_invariant_preservation <= 1:
        raise BridgeError("minimum_invariant_preservation must be in [0,1]")

    for item in intents:
        if item.scale <= 0:
            raise BridgeError("intent scale must be positive")
        if item.weight < 0:
            raise BridgeError("intent weight cannot be negative")

    _unique((f"{x.timestamp}:{x.key}" for x in intents), "intent timestamp/key")
    _unique((f"{x.timestamp}:{x.key}" for x in actions), "action timestamp/key")

    return TemporalPacket(
        packet_id=packet_id,
        observability_class=obs,
        evidence=tuple(evidence),
        unknowns=unknowns,
        conflicts=tuple(conflicts),
        intents=intents,
        actions=actions,
        invariants=invariants,
        boundary=boundary,
        blocked_operations=tuple(str(x) for x in data.get("blocked_operations", [])),
    )


def _branch_dict(branch: EvidenceBranch) -> dict[str, Any]:
    data = asdict(branch)
    data["provenance"] = branch.provenance.value
    return data


def _detect_undeclared_conflicts(evidence: tuple[EvidenceBranch, ...]) -> list[ConflictRecord]:
    by_key: dict[str, list[EvidenceBranch]] = {}
    for branch in evidence:
        by_key.setdefault(branch.key, []).append(branch)
    out = []
    for key, branches in sorted(by_key.items()):
        if len(branches) < 2:
            continue
        dimensions = []
        if len({canonical_json(x.value) for x in branches}) > 1:
            dimensions.append("VALUE")
        if len({x.unit for x in branches}) > 1:
            dimensions.append("UNIT")
        if len({x.operator for x in branches}) > 1:
            dimensions.append("OPERATOR")
        if dimensions:
            out.append(ConflictRecord(
                conflict_id=f"AUTO::{key}",
                branch_ids=tuple(x.branch_id for x in branches),
                dimensions=tuple(dimensions),
                status="UNRESOLVED",
            ))
    return out


def _linear_slope(times: list[float], values: list[float]) -> float | None:
    if len(times) < 2 or len(set(times)) < 2:
        return None
    mt = sum(times) / len(times)
    mv = sum(values) / len(values)
    den = sum((t - mt) ** 2 for t in times)
    if den == 0:
        return None
    return sum((t - mt) * (v - mv) for t, v in zip(times, values)) / den


def _recovery_rate(times: list[float], values: list[float], threshold: float, horizon: float) -> float | None:
    starts = []
    in_breach = False
    for i, value in enumerate(values):
        if value >= threshold and not in_breach:
            starts.append(i)
            in_breach = True
        elif value < threshold:
            in_breach = False
    if not starts:
        return None
    recovered = 0
    for start in starts:
        deadline = times[start] + horizon
        for j in range(start + 1, len(times)):
            if times[j] > deadline:
                break
            if values[j] < threshold:
                recovered += 1
                break
    return recovered / len(starts)


def _invariant_ratio(items: tuple[InvariantEvent, ...]) -> float | None:
    total = 0.0
    kept = 0.0
    for item in items:
        if item.preserved is None:
            continue
        total += item.weight
        kept += item.weight * (1.0 if item.preserved else 0.0)
    return None if total == 0 else kept / total


def _status(current, mu, slope, inv, phase, b: Boundary, obs: Observability) -> str:
    if obs is Observability.UNOBSERVABLE:
        return "INSUFFICIENT"
    if current is None or mu is None or inv is None:
        return "INSUFFICIENT"
    if current >= b.critical_threshold or inv < max(0, b.minimum_invariant_preservation - 0.25):
        return "CRITICAL"
    if mu >= b.discrepancy_threshold or inv < b.minimum_invariant_preservation:
        return "DEGRADED"
    if (slope is not None and slope > 0) or (phase is not None and phase >= 0.5) or current >= 0.8 * b.discrepancy_threshold:
        return "WATCH"
    return "STABLE"


def analyze(packet: TemporalPacket) -> AnalysisResult:
    branch_payload = tuple(_branch_dict(x) for x in packet.evidence)
    evidence_hash = sha256_json(branch_payload)
    packet_hash = sha256_json({
        "packet_id": packet.packet_id,
        "observability_class": packet.observability_class.value,
        "evidence": branch_payload,
        "unknowns": [asdict(x) for x in packet.unknowns],
        "conflicts": [asdict(x) for x in packet.conflicts],
        "intents": [asdict(x) for x in packet.intents],
        "actions": [asdict(x) for x in packet.actions],
        "invariants": [asdict(x) for x in packet.invariants],
        "boundary": asdict(packet.boundary),
        "blocked_operations": packet.blocked_operations,
    })

    explicit_ids = {x.conflict_id for x in packet.conflicts}
    conflicts = list(packet.conflicts)
    for auto in _detect_undeclared_conflicts(packet.evidence):
        if auto.conflict_id not in explicit_ids:
            conflicts.append(auto)

    blocked = list(packet.blocked_operations)
    if any(x.status == "UNRESOLVED" for x in conflicts):
        blocked.extend(["silent_branch_selection", "dependent_calculation_from_unresolved_conflict"])
    if packet.unknowns:
        blocked.append("calculation_requiring_protected_unknown")

    intent_map = {(x.timestamp, x.key): x for x in packet.intents}
    action_map = {(x.timestamp, x.key): x for x in packet.actions}
    keys = sorted(set(intent_map) | set(action_map))
    missing_pairs = [k for k in keys if k not in intent_map or k not in action_map]

    d_rows = None
    mu = slope = recovery = inv = phase = None
    recovery_status = "BLOCKED"

    if packet.observability_class is not Observability.UNOBSERVABLE and not missing_pairs and keys:
        by_time: dict[float, list[tuple[float, float, str]]] = {}
        for pair in keys:
            intent = intent_map[pair]
            action = action_map[pair]
            d = max(0.0, min(1.0, abs(action.value - intent.value) / intent.scale))
            by_time.setdefault(intent.timestamp, []).append((d, intent.weight, intent.key))
        rows = []
        for timestamp, values in sorted(by_time.items()):
            total_weight = sum(w for _, w, _ in values)
            if total_weight <= 0:
                raise BridgeError("intent weights at each timestamp must sum positive")
            d_t = sum(d * w for d, w, _ in values) / total_weight
            rows.append({
                "timestamp": timestamp,
                "d_t": d_t,
                "dimensions": tuple(k for _, _, k in values),
            })
        d_rows = tuple(rows)
        times = [x["timestamp"] for x in rows]
        values = [x["d_t"] for x in rows]
        mu = sum(values) / len(values)
        slope = _linear_slope(times, values)
        recovery = _recovery_rate(times, values, packet.boundary.discrepancy_threshold, packet.boundary.recovery_horizon)
        recovery_status = "NOT_APPLICABLE" if recovery is None else "VALID"
        inv = _invariant_ratio(packet.invariants)
        current = values[-1]
        boundary_proximity = min(1.0, current / packet.boundary.discrepancy_threshold)
        positive_slope = min(1.0, max(0.0, slope or 0.0))
        invariant_loss = 1.0 if inv is None else 1.0 - inv
        conflict_risk = 1.0 if any(x.status == "UNRESOLVED" for x in conflicts) else 0.0
        phase = min(1.0, 0.35 * boundary_proximity + 0.25 * positive_slope + 0.20 * invariant_loss + 0.20 * conflict_risk)
    else:
        if missing_pairs:
            blocked.append("drift_metrics_missing_intent_action_pair")
        if not keys:
            blocked.append("drift_metrics_no_temporal_events")
        inv = _invariant_ratio(packet.invariants)

    current = None if not d_rows else d_rows[-1]["d_t"]
    status = _status(current, mu, slope, inv, phase, packet.boundary, packet.observability_class)

    interpretation = {
        Observability.WHITE_BOX: "operational intent-action coherence",
        Observability.INSTRUMENTED_COLLABORATOR: "declared-intent behavioral coherence",
        Observability.BLACK_BOX: "behavioral anomaly signal only",
        Observability.UNOBSERVABLE: "no metric claim permitted",
    }[packet.observability_class]

    return AnalysisResult(
        bridge_version=VERSION,
        packet_id=packet.packet_id,
        observability_class=packet.observability_class.value,
        permitted_interpretation=interpretation,
        evidence_hash=evidence_hash,
        packet_hash=packet_hash,
        evidence_branches=branch_payload,
        unknowns=tuple(asdict(x) for x in packet.unknowns),
        conflicts=tuple(asdict(x) for x in conflicts),
        d_t=d_rows,
        mu_drift=mu,
        rho_drift=slope,
        rho_recovery=recovery,
        rho_recovery_status=recovery_status,
        invariant_preservation=inv,
        phase_risk=phase,
        status=status,
        blocked_calculations=tuple(dict.fromkeys(blocked)),
        limitations=(
            "not an alignment guarantee",
            "does not detect sufficiently deceptive hidden objectives",
            "low observed drift does not prove honesty or sovereignty",
            "conflicts preserve branches and do not select a winner",
        ),
    )


def analyze_dict(data: dict[str, Any]) -> dict[str, Any]:
    return analyze(packet_from_dict(data)).to_dict()
