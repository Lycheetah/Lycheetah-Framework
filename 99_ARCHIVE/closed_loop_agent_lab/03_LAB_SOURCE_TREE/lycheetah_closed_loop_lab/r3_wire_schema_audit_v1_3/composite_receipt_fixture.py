"""Receipt-shaped source-equivalent fixture for wire-type normalization.

Mirrors the inspected normalization behavior in ControlReference.from_dict,
Finding.from_dict and AssuranceReceipt.from_dict/body_dict. Not an import of the
upstream package and not a substitute for its real tests.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from source_equivalent_wire_fixture import WireError, canonical_sha256


def _control_to_body(raw: Mapping[str, Any]) -> dict[str, str]:
    # Mirrors ControlReference.from_dict(... str(...)) then ControlReference.to_dict().
    output = {
        "framework": str(raw["framework"]),
        "control_id": str(raw["control_id"]),
        "title": str(raw["title"]),
    }
    url = str(raw.get("url", ""))
    if url:
        output["url"] = url
    return output


def _finding_to_body(raw: Mapping[str, Any]) -> dict[str, Any]:
    # Mirrors the string/float coercions in Finding.from_dict and the resulting to_dict.
    out: dict[str, Any] = {
        "id": str(raw["id"]),
        "title": str(raw["title"]),
        "description": str(raw["description"]),
        "severity": raw["severity"],
        "requested_disposition": raw["requested_disposition"],
        "effective_disposition": raw["effective_disposition"],
        "claim_status": raw["claim_status"],
        "deterministic": raw["deterministic"],
        "evaluator": str(raw["evaluator"]),
        "confidence": float(raw.get("confidence", 1.0)),
        "evidence": [str(item) for item in raw.get("evidence", [])],
        "controls": [_control_to_body(item) for item in raw.get("controls", [])],
    }
    status_basis = str(raw.get("status_basis", ""))
    if status_basis:
        out["status_basis"] = status_basis
    if raw.get("cap_reason"):
        out["cap_reason"] = raw["cap_reason"]
    return out


def _strict_finding_to_body(raw: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(raw, Mapping):
        raise WireError("finding must be an object")
    for field in ("id", "title", "description", "evaluator"):
        if not isinstance(raw.get(field), str):
            raise WireError(f"finding {field} must be a string")
    if "status_basis" in raw and not isinstance(raw["status_basis"], str):
        raise WireError("finding status_basis must be a string")
    confidence = raw.get("confidence", 1.0)
    import math
    if isinstance(confidence, bool) or not isinstance(confidence, (int, float)) or not math.isfinite(float(confidence)):
        raise WireError("finding confidence must be a finite number")
    if not isinstance(raw.get("evidence", []), list) or any(not isinstance(item, str) for item in raw.get("evidence", [])):
        raise WireError("finding evidence must be an array of strings")
    controls = raw.get("controls", [])
    if not isinstance(controls, list):
        raise WireError("finding controls must be an array")
    normalized_controls = []
    for control in controls:
        if not isinstance(control, Mapping):
            raise WireError("control reference must be an object")
        for field in ("framework", "control_id", "title"):
            if not isinstance(control.get(field), str):
                raise WireError(f"control reference {field} must be a string")
        if "url" in control and not isinstance(control["url"], str):
            raise WireError("control reference url must be a string")
        normalized_controls.append(_control_to_body(control))
    out = {
        "id": raw["id"],
        "title": raw["title"],
        "description": raw["description"],
        "severity": raw["severity"],
        "requested_disposition": raw["requested_disposition"],
        "effective_disposition": raw["effective_disposition"],
        "claim_status": raw["claim_status"],
        "deterministic": raw["deterministic"],
        "evaluator": raw["evaluator"],
        "confidence": float(confidence),
        "evidence": list(raw.get("evidence", [])),
        "controls": normalized_controls,
    }
    if raw.get("status_basis", ""):
        out["status_basis"] = raw["status_basis"]
    if raw.get("cap_reason"):
        if not isinstance(raw["cap_reason"], str):
            raise WireError("finding cap_reason must be a string or null")
        out["cap_reason"] = raw["cap_reason"]
    return out


def valid_receipt_body() -> dict[str, Any]:
    return {
        "schema_version": "0.1",
        "receipt_id": "urn:uuid:fixture-0001",
        "issued_at": "2026-10-16T00:00:00Z",
        "runtime": {"name": "fixture-runtime", "status": "SCAFFOLD"},
        "policy": {"id": "fixture.policy", "version": "1", "sha256": "a" * 64},
        "event": {"phase": "output", "replayable": False},
        "decision": "ALLOW",
        "findings": [
            {
                "id": "TEST:FINDING:001",
                "title": "False",
                "description": "Fixture finding",
                "severity": "MEDIUM",
                "requested_disposition": "ALLOW",
                "effective_disposition": "ALLOW",
                "claim_status": "ACTIVE",
                "deterministic": True,
                "evaluator": "test/1",
                "confidence": 1.0,
                "evidence": ["17"],
                "controls": [{"framework": "Fixture", "control_id": "CTRL-1", "title": "False"}],
                "status_basis": "Fixture-only basis",
            }
        ],
        "metrics": {},
        "limitations": ["fixture-only"],
        "lineage": {"trace_id": "trace-fixture", "previous_receipt_sha256": None},
    }


def finalize_receipt(body: Mapping[str, Any]) -> dict[str, Any]:
    payload = deepcopy(dict(body))
    payload["integrity"] = {
        "algorithm": "sha256",
        "canonicalization": "lycheetah-json-v1",
        "digest": canonical_sha256(body),
        "seal": None,
    }
    return payload


def baseline_parse_and_verify(payload: Mapping[str, Any]) -> tuple[dict[str, Any], bool]:
    body: dict[str, Any] = {
        "schema_version": str(payload["schema_version"]),
        "receipt_id": str(payload["receipt_id"]),
        "issued_at": str(payload["issued_at"]),
        "runtime": deepcopy(payload["runtime"]),
        "policy": deepcopy(payload["policy"]),
        "event": deepcopy(payload["event"]),
        "decision": payload["decision"],
        "findings": [_finding_to_body(item) for item in payload["findings"]],
        "metrics": deepcopy(payload["metrics"]),
        "limitations": [str(item) for item in payload["limitations"]],
        "lineage": deepcopy(payload["lineage"]),
    }
    return body, canonical_sha256(body) == payload["integrity"]["digest"]


def strict_parse_and_verify(payload: Mapping[str, Any]) -> tuple[dict[str, Any], bool]:
    if not isinstance(payload.get("schema_version"), str):
        raise WireError("schema_version must be a string")
    if not isinstance(payload.get("receipt_id"), str) or not isinstance(payload.get("issued_at"), str):
        raise WireError("receipt_id and issued_at must be strings")
    body = {
        "schema_version": payload["schema_version"],
        "receipt_id": payload["receipt_id"],
        "issued_at": payload["issued_at"],
        "runtime": deepcopy(payload["runtime"]),
        "policy": deepcopy(payload["policy"]),
        "event": deepcopy(payload["event"]),
        "decision": payload["decision"],
        "findings": [_strict_finding_to_body(item) for item in payload["findings"]],
        "metrics": deepcopy(payload["metrics"]),
        "limitations": list(payload["limitations"]),
        "lineage": deepcopy(payload["lineage"]),
    }
    return body, canonical_sha256(body) == payload["integrity"]["digest"]


def mutate(payload: Mapping[str, Any], case: str) -> dict[str, Any]:
    out = deepcopy(dict(payload))
    if case == "schema_version_number":
        out["schema_version"] = 0.1
    elif case == "control_title_boolean":
        out["findings"][0]["controls"][0]["title"] = False
    elif case == "finding_title_boolean":
        out["findings"][0]["title"] = False
    elif case == "confidence_boolean":
        out["findings"][0]["confidence"] = True
    elif case == "evidence_integer":
        out["findings"][0]["evidence"][0] = 17
    else:
        raise ValueError(f"unknown mutation case: {case}")
    return out
