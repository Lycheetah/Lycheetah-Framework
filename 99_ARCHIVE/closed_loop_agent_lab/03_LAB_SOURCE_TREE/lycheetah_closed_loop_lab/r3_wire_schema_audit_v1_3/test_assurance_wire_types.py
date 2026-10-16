"""Upstream regression tests for strict assurance-record wire types.

Apply with strict_assurance_wire_types_v1_3.patch to the inspected source
revision. These tests require the real lycheetah.assurance package.
"""
import json

import pytest

from lycheetah.assurance import (
    AssurancePolicy,
    AssuranceRuntime,
    ClaimStatus,
    ControlReference,
    Disposition,
    Finding,
    PolicyError,
    Severity,
)
from lycheetah.assurance.receipt import AssuranceReceipt, ReceiptError

BAD_JSON_VALUES = [None, True, 17, 3.5, ["ordinary"], {"ordinary": "value"}]


def _finding_dict():
    finding = Finding.create(
        finding_id="TEST:FINDING:001",
        title="Example finding",
        description="A valid synthetic finding.",
        severity=Severity.MEDIUM,
        requested_disposition=Disposition.REVIEW,
        claim_status=ClaimStatus.SCAFFOLD,
        deterministic=False,
        evaluator="test-evaluator/1",
        confidence=0.5,
        status_basis="Fixture-only status basis.",
        evidence=["reason=fixture"],
        controls=[ControlReference("Example Framework", "EX-1", "Example control")],
    )
    return finding.to_dict()


@pytest.mark.parametrize("field", ("framework", "control_id", "title", "url"))
@pytest.mark.parametrize("bad_value", BAD_JSON_VALUES, ids=lambda value: repr(value))
def test_control_reference_parser_rejects_non_string_fields(field, bad_value):
    payload = {"framework": "Example Framework", "control_id": "EX-1", "title": "Example", "url": ""}
    payload[field] = bad_value
    with pytest.raises((ValueError, TypeError)):
        ControlReference.from_dict(payload)


@pytest.mark.parametrize("field", ("id", "title", "description", "evaluator", "status_basis"))
@pytest.mark.parametrize("bad_value", BAD_JSON_VALUES, ids=lambda value: repr(value))
def test_finding_parser_rejects_non_string_text_fields(field, bad_value):
    payload = _finding_dict()
    payload[field] = bad_value
    with pytest.raises((ValueError, TypeError)):
        Finding.from_dict(payload)


@pytest.mark.parametrize("bad_value", [True, False, "0.5", None, [], {}, float("nan"), float("inf")])
def test_finding_parser_rejects_non_numeric_or_non_finite_confidence(bad_value):
    payload = _finding_dict()
    payload["confidence"] = bad_value
    with pytest.raises((ValueError, TypeError)):
        Finding.from_dict(payload)


@pytest.mark.parametrize("bad_value", [None, True, 17, 3.5, {"x": "y"}])
def test_finding_parser_rejects_non_string_evidence_items(bad_value):
    payload = _finding_dict()
    payload["evidence"] = [bad_value]
    with pytest.raises((ValueError, TypeError)):
        Finding.from_dict(payload)


def test_valid_finding_round_trip_preserves_types_and_defaults():
    payload = _finding_dict()
    finding = Finding.from_dict(payload)
    assert finding.finding_id == payload["id"]
    assert finding.title == payload["title"]
    assert finding.confidence == 0.5
    assert finding.evidence == ("reason=fixture",)
    assert finding.controls[0].control_id == "EX-1"


def test_receipt_rejects_non_string_schema_version_before_normalization():
    receipt = AssuranceRuntime(AssurancePolicy()).evaluate_text(
        "This is a harmless test receipt."
    )
    assert receipt.verify().valid
    payload = json.loads(receipt.to_json(indent=None))
    # Before strict parsing, 0.1 was converted to "0.1", reproducing the same
    # in-memory body and allowing this noncanonical wire representation through.
    payload["schema_version"] = 0.1
    with pytest.raises(ReceiptError, match="schema_version must be a string"):
        AssuranceReceipt.from_dict(payload)


def test_receipt_valid_wire_representation_still_verifies():
    receipt = AssuranceRuntime().evaluate_text("A regular output with no special handling.")
    restored = AssuranceReceipt.from_json(receipt.to_json(indent=None))
    assert restored.verify().valid
    assert restored.schema_version == "0.1"
