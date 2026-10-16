"""Scoped source-equivalent fixtures for Assurance deserialization coercions.

These fixtures reproduce specific normalization expressions in the inspected
upstream methods. They are not imports of the whole Lycheetah package.
"""
from __future__ import annotations
import hashlib
import json
import math
from typing import Any, Mapping


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


class WireError(ValueError):
    pass


def baseline_receipt_parse(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Mirror from_dict's schema_version=str(...) followed by verify-style hashing."""
    body = {key: value for key, value in payload.items() if key != "integrity"}
    body["schema_version"] = str(payload["schema_version"])
    expected = canonical_sha256(body)
    if expected != payload["integrity"]["digest"]:
        raise WireError("receipt body digest mismatch")
    return body


def strict_receipt_parse(payload: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(payload.get("schema_version"), str):
        raise WireError("schema_version must be a string")
    return baseline_receipt_parse(payload)


def baseline_control_reference(payload: Mapping[str, Any]) -> dict[str, str]:
    return {
        "framework": str(payload["framework"]),
        "control_id": str(payload["control_id"]),
        "title": str(payload["title"]),
        "url": str(payload.get("url", "")),
    }


def strict_control_reference(payload: Mapping[str, Any]) -> dict[str, str]:
    for field in ("framework", "control_id", "title", "url"):
        if field in payload and not isinstance(payload[field], str):
            raise WireError(f"control reference {field} must be a string")
    for field in ("framework", "control_id", "title"):
        if field not in payload:
            raise WireError(f"control reference missing required field: {field}")
    return baseline_control_reference(payload)


def baseline_finding(payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "id": str(payload["id"]),
        "title": str(payload["title"]),
        "description": str(payload["description"]),
        "evaluator": str(payload["evaluator"]),
        "confidence": float(payload.get("confidence", 1.0)),
        "status_basis": str(payload.get("status_basis", "")),
        "evidence": tuple(str(item) for item in payload.get("evidence", [])),
    }


def strict_finding(payload: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, Mapping):
        raise WireError("finding must be an object")
    for field in ("id", "title", "description", "evaluator"):
        if not isinstance(payload.get(field), str):
            raise WireError(f"finding {field} must be a string")
    if "status_basis" in payload and not isinstance(payload["status_basis"], str):
        raise WireError("finding status_basis must be a string")
    confidence = payload.get("confidence", 1.0)
    if isinstance(confidence, bool) or not isinstance(confidence, (int, float)) or not math.isfinite(float(confidence)):
        raise WireError("finding confidence must be a finite number")
    evidence = payload.get("evidence", [])
    if not isinstance(evidence, list) or any(not isinstance(item, str) for item in evidence):
        raise WireError("finding evidence must be an array of strings")
    return baseline_finding(payload)
