from __future__ import annotations

from typing import Any

from lamague_temporal.bridge import analyze_dict, BridgeError
from .model import NativeProgram, NativeCompileResult, SourceStatement
from .parser import VERSION


class NativeCompileError(ValueError):
    pass


PROVENANCE = {
    "observe": "OBSERVED",
    "declare": "DECLARED",
    "calculate": "CALCULATED",
    "infer": "INFERRED",
}


def _require_pos(stmt: SourceStatement, count: int, form: str) -> None:
    if len(stmt.positional) != count:
        raise NativeCompileError(
            f"statement {stmt.index}: expected {form}"
        )


def _allowed_options(stmt: SourceStatement, allowed: set[str]) -> None:
    extra = set(stmt.options) - allowed
    if extra:
        raise NativeCompileError(
            f"statement {stmt.index}: unsupported option(s): "
            + ", ".join(sorted(extra))
        )


def _number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise NativeCompileError(f"{label} must be numeric")
    return float(value)


def _bool_or_none(value: Any, label: str):
    if value not in {True, False, None}:
        raise NativeCompileError(
            f"{label} must be true, false, or null"
        )
    return value


def compile_program(program: NativeProgram) -> NativeCompileResult:
    boundary = {
        "discrepancy_threshold": 0.30,
        "critical_threshold": 0.70,
        "recovery_horizon": 3.0,
        "minimum_invariant_preservation": 0.95,
    }
    evidence: list[dict[str, Any]] = []
    unknowns: list[dict[str, Any]] = []
    conflicts: list[dict[str, Any]] = []
    drift_specs: dict[str, dict[str, float]] = {}
    intents_raw: list[tuple[SourceStatement, str, float, float]] = []
    actions: list[dict[str, Any]] = []
    invariants: list[dict[str, Any]] = []
    preserve_targets: list[str] = []
    blocked: list[str] = []
    warnings = list(program.warnings)
    analyze_count = 0

    for stmt in program.statements:
        key = stmt.keyword
        if key in {"packet", "observability"}:
            continue

        if key == "boundary":
            _require_pos(
                stmt,
                0,
                "boundary discrepancy=... critical=... min_invariant=...;",
            )
            _allowed_options(
                stmt, {"discrepancy", "critical", "min_invariant"}
            )
            if "discrepancy" in stmt.options:
                boundary["discrepancy_threshold"] = _number(
                    stmt.options["discrepancy"], "boundary discrepancy"
                )
            if "critical" in stmt.options:
                boundary["critical_threshold"] = _number(
                    stmt.options["critical"], "boundary critical"
                )
            if "min_invariant" in stmt.options:
                boundary["minimum_invariant_preservation"] = _number(
                    stmt.options["min_invariant"],
                    "boundary min_invariant",
                )
            continue

        if key == "recover":
            _require_pos(stmt, 0, "recover horizon=...;")
            _allowed_options(stmt, {"horizon"})
            if "horizon" not in stmt.options:
                raise NativeCompileError(
                    f"statement {stmt.index}: recover requires horizon"
                )
            boundary["recovery_horizon"] = _number(
                stmt.options["horizon"], "recovery horizon"
            )
            continue

        if key in PROVENANCE:
            _require_pos(
                stmt, 1, f"{key} BRANCH_ID key=... value=...;"
            )
            _allowed_options(
                stmt,
                {"key", "value", "unit", "operator", "source", "at"},
            )
            if "key" not in stmt.options or "value" not in stmt.options:
                raise NativeCompileError(
                    f"statement {stmt.index}: {key} requires key and value"
                )
            evidence.append({
                "branch_id": stmt.positional[0],
                "key": str(stmt.options["key"]),
                "provenance": PROVENANCE[key],
                "value": stmt.options["value"],
                "unit": str(stmt.options.get("unit", "")),
                "operator": str(stmt.options.get("operator", "")),
                "source_ref": str(stmt.options.get("source", "")),
                "timestamp": (
                    None
                    if "at" not in stmt.options
                    else _number(stmt.options["at"], f"{key} timestamp")
                ),
            })
            continue

        if key == "unknown":
            _require_pos(
                stmt,
                1,
                "unknown KEY expected=... source=... protected=true;",
            )
            _allowed_options(stmt, {"expected", "source", "protected"})
            protected = stmt.options.get("protected", True)
            if not isinstance(protected, bool):
                raise NativeCompileError(
                    f"statement {stmt.index}: protected must be boolean"
                )
            unknowns.append({
                "key": stmt.positional[0],
                "expected_type": str(stmt.options.get("expected", "")),
                "source_ref": str(stmt.options.get("source", "")),
                "protected": protected,
            })
            continue

        if key == "conflict":
            _require_pos(
                stmt,
                1,
                "conflict ID branches=a,b dimensions=VALUE,UNIT "
                "status=UNRESOLVED;",
            )
            _allowed_options(stmt, {"branches", "dimensions", "status"})
            branches = stmt.options.get("branches")
            if not isinstance(branches, str) or not branches:
                raise NativeCompileError(
                    f"statement {stmt.index}: conflict requires branches=a,b"
                )
            dims = stmt.options.get("dimensions", "")
            status = str(stmt.options.get("status", "UNRESOLVED"))
            conflicts.append({
                "conflict_id": stmt.positional[0],
                "branch_ids": [x for x in branches.split(",") if x],
                "dimensions": [x for x in str(dims).split(",") if x],
                "status": status,
            })
            continue

        if key == "drift":
            _require_pos(stmt, 1, "drift KEY scale=... weight=...;")
            _allowed_options(stmt, {"scale", "weight"})
            name = stmt.positional[0]
            if name in drift_specs:
                raise NativeCompileError(
                    f"statement {stmt.index}: duplicate drift dimension {name!r}"
                )
            drift_specs[name] = {
                "scale": _number(
                    stmt.options.get("scale", 1.0), "drift scale"
                ),
                "weight": _number(
                    stmt.options.get("weight", 1.0), "drift weight"
                ),
            }
            if drift_specs[name]["scale"] <= 0:
                raise NativeCompileError(
                    f"statement {stmt.index}: drift scale must be positive"
                )
            if drift_specs[name]["weight"] < 0:
                raise NativeCompileError(
                    f"statement {stmt.index}: drift weight cannot be negative"
                )
            continue

        if key == "intent":
            _require_pos(stmt, 1, "intent KEY at=... value=...;")
            _allowed_options(stmt, {"at", "value"})
            if "at" not in stmt.options or "value" not in stmt.options:
                raise NativeCompileError(
                    f"statement {stmt.index}: intent requires at and value"
                )
            intents_raw.append((
                stmt,
                stmt.positional[0],
                _number(stmt.options["at"], "intent timestamp"),
                _number(stmt.options["value"], "intent value"),
            ))
            continue

        if key == "action":
            _require_pos(
                stmt, 1, "action KEY at=... value=... source=...;"
            )
            _allowed_options(stmt, {"at", "value", "source"})
            if "at" not in stmt.options or "value" not in stmt.options:
                raise NativeCompileError(
                    f"statement {stmt.index}: action requires at and value"
                )
            actions.append({
                "timestamp": _number(
                    stmt.options["at"], "action timestamp"
                ),
                "key": stmt.positional[0],
                "value": _number(stmt.options["value"], "action value"),
                "source_ref": str(stmt.options.get("source", "")),
            })
            continue

        if key == "invariant":
            _require_pos(
                stmt,
                1,
                "invariant NAME at=... preserved=true|false|null "
                "weight=... source=...;",
            )
            _allowed_options(
                stmt, {"at", "preserved", "weight", "source"}
            )
            if "at" not in stmt.options or "preserved" not in stmt.options:
                raise NativeCompileError(
                    f"statement {stmt.index}: invariant requires at and preserved"
                )
            invariants.append({
                "timestamp": _number(
                    stmt.options["at"], "invariant timestamp"
                ),
                "name": stmt.positional[0],
                "preserved": _bool_or_none(
                    stmt.options["preserved"], "invariant preserved"
                ),
                "weight": _number(
                    stmt.options.get("weight", 1.0), "invariant weight"
                ),
                "source_ref": str(stmt.options.get("source", "")),
            })
            continue

        if key == "preserve":
            _require_pos(stmt, 1, "preserve TARGET;")
            _allowed_options(stmt, set())
            preserve_targets.append(stmt.positional[0])
            continue

        if key == "block":
            _require_pos(stmt, 1, "block OPERATION;")
            _allowed_options(stmt, set())
            blocked.append(stmt.positional[0])
            continue

        if key == "analyze":
            _require_pos(stmt, 0, "analyze;")
            _allowed_options(stmt, set())
            analyze_count += 1
            continue

        raise NativeCompileError(
            f"statement {stmt.index}: unhandled keyword {key!r}"
        )

    if analyze_count > 1:
        raise NativeCompileError("analyze may appear at most once")

    intents: list[dict[str, Any]] = []
    for stmt, name, timestamp, value in intents_raw:
        if name not in drift_specs:
            raise NativeCompileError(
                f"statement {stmt.index}: intent {name!r} has no matching "
                f"`drift {name} ...;` declaration"
            )
        spec = drift_specs[name]
        intents.append({
            "timestamp": timestamp,
            "key": name,
            "value": value,
            "scale": spec["scale"],
            "weight": spec["weight"],
        })

    evidence_ids = {x["branch_id"] for x in evidence}
    unknown_keys = {x["key"] for x in unknowns}
    invariant_names = {x["name"] for x in invariants}
    valid_preserve = evidence_ids | unknown_keys | invariant_names
    missing_preserve = sorted(set(preserve_targets) - valid_preserve)
    if missing_preserve:
        raise NativeCompileError(
            "preserve references unknown target(s): "
            + ", ".join(missing_preserve)
        )

    packet = {
        "packet_id": program.packet_id,
        "observability_class": program.observability_class,
        "evidence": evidence,
        "unknowns": unknowns,
        "conflicts": conflicts,
        "intents": intents,
        "actions": actions,
        "invariants": invariants,
        "boundary": boundary,
        "blocked_operations": blocked,
    }
    try:
        analysis = analyze_dict(packet)
    except BridgeError as exc:
        raise NativeCompileError(str(exc)) from exc

    return NativeCompileResult(
        native_version=VERSION,
        source_hash=program.source_hash,
        ast=program.to_dict(),
        temporal_packet=packet,
        preserved_targets=tuple(preserve_targets),
        analysis=analysis,
        warnings=tuple(warnings),
        limitations=(
            "native syntax does not prove truth or physical validity",
            "low observable drift does not prove honesty, alignment, or sovereignty",
            "unknown values are not inferred",
            "conflict branches are preserved without automatic winner selection",
            "symbolic and mythic layers cannot override executable semantics",
        ),
    )
