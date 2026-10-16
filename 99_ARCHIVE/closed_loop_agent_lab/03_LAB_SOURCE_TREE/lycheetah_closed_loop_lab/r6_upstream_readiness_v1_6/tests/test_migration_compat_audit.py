"""Offline tests for the read-only compatibility preflight's wire guards."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("migration_compat", ROOT / "scan_migration_compat.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def test_valid_minimal_policy_has_no_wire_issues():
    data = {"id": "test.policy", "version": "1", "text": {"rules": [{"id": "test.rule", "pattern": "example"}]}}
    assert MODULE.policy_wire_issues(data) == []


def test_non_string_rule_id_and_pattern_are_reported():
    data = {"id": "test.policy", "version": "1", "text": {"rules": [{"id": True, "pattern": 12}]}}
    issues = MODULE.policy_wire_issues(data)
    assert "text.rules[0].id must be a string" in issues
    assert "text.rules[0].pattern must be a string" in issues


def test_optional_rule_text_fields_are_checked_when_present():
    data = {"id": "test.policy", "version": "1", "text": {"rules": [{"id": "test.rule", "pattern": "x", "title": False}]}}
    assert "text.rules[0].title must be a string" in MODULE.policy_wire_issues(data)


def test_receipt_rejects_normalizable_schema_version():
    assert "schema_version must be a string" in MODULE.receipt_wire_issues({"schema_version": 0.1})


def test_receipt_policy_digest_has_strict_wire_shape():
    issues = MODULE.receipt_wire_issues({"schema_version": "0.1", "policy": {"sha256": "not-a-hash"}})
    assert "policy.sha256 must be 64 lowercase hexadecimal characters" in issues


def test_receipt_finding_confidence_excludes_booleans():
    data = {"schema_version": "0.1", "findings": [{"confidence": True, "evidence": [], "controls": []}]}
    assert "findings[0].confidence must be a finite number" in MODULE.receipt_wire_issues(data)


def test_receipt_control_reference_rejects_unknown_keys():
    data = {"schema_version": "0.1", "findings": [{"id": "test.id", "title": "t", "description": "d", "evaluator": "e", "confidence": 0.5, "evidence": [], "controls": [{"framework": "f", "control_id": "c", "title": "t", "extra": 1}]}]}
    assert "findings[0].controls[0].extra is unknown" in MODULE.receipt_wire_issues(data)


def _valid_policy_record():
    return {
        "id": "test.policy", "version": "1", "description": "Fixture",
        "text": {"manipulation_review_threshold": 0.25, "aura_review_below_percent": 70.0, "max_text_characters": 20000, "rules": []},
        "tools": {"require_approval_for_side_effects": True, "denied": ["shell"], "review": [], "allowlist": [], "blocked_scopes": ["secrets.*"]},
        "privacy": {"capture_content": False, "capture_arguments": False, "capture_evidence_spans": False, "sensitive_argument_keys": ["password"]},
    }


def _valid_receipt_record():
    return {
        "schema_version": "0.1", "receipt_id": "receipt-001", "issued_at": "2026-10-16T00:00:00Z",
        "runtime": {}, "policy": {"id": "test.policy", "version": "1", "sha256": "a" * 64},
        "event": {"event_id": "evt-1", "phase": "tool", "subject": {"name": "lookup", "sha256": "b" * 64}, "replayable": True},
        "decision": "ALLOW", "findings": [{"id": "test.finding", "title": "Fixture", "description": "Synthetic", "severity": "INFO", "requested_disposition": "ALLOW", "effective_disposition": "ALLOW", "claim_status": "ACTIVE", "deterministic": True, "evaluator": "test", "confidence": 1.0, "evidence": [], "controls": []}],
        "metrics": {}, "limitations": [], "lineage": {"trace_id": "trace-1", "previous_receipt_sha256": None},
        "integrity": {"algorithm": "sha256", "canonicalization": "lycheetah-json-v1", "digest": "c" * 64, "seal": None},
    }


def test_candidate_policy_schema_accepts_representative_valid_record():
    import jsonschema
    schema = MODULE.POLICY_CANDIDATE
    jsonschema.Draft202012Validator(schema).validate(_valid_policy_record())


def test_candidate_policy_schema_rejects_active_rule_without_basis():
    import jsonschema
    payload = _valid_policy_record()
    payload["text"]["rules"] = [{"id": "test.rule", "pattern": "example", "claim_status": "ACTIVE"}]
    try:
        jsonschema.Draft202012Validator(MODULE.POLICY_CANDIDATE).validate(payload)
    except jsonschema.ValidationError:
        return
    raise AssertionError("candidate schema accepted ACTIVE rule without status_basis")


def test_candidate_receipt_schema_accepts_representative_wire_record():
    import jsonschema
    jsonschema.Draft202012Validator(MODULE.RECEIPT_CANDIDATE).validate(_valid_receipt_record())


def test_candidate_receipt_schema_rejects_unknown_control_extension():
    import jsonschema
    payload = _valid_receipt_record()
    payload["findings"][0]["controls"] = [{"framework": "f", "control_id": "id", "title": "t", "extension": 1}]
    try:
        jsonschema.Draft202012Validator(MODULE.RECEIPT_CANDIDATE).validate(payload)
    except jsonschema.ValidationError:
        return
    raise AssertionError("candidate schema accepted unknown control property")


def test_receipt_guard_rejects_explicit_null_cap_reason():
    data = {"schema_version": "0.1", "findings": [{"cap_reason": None, "evidence": [], "controls": []}]}
    assert "findings[0].cap_reason must be a string when present" in MODULE.receipt_wire_issues(data)
