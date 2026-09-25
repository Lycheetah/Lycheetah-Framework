"""Executable contract for evidence-capped enforcement."""

import itertools

import pytest

from lycheetah.assurance import (
    AssuranceEvent,
    ClaimStatus,
    Disposition,
    Finding,
    Phase,
    Severity,
    capped_disposition,
)
from lycheetah.assurance.jsonutil import CanonicalJSONError, sha256_json


@pytest.mark.parametrize(
    "status,deterministic,requested,expected",
    [
        (status, deterministic, requested, expected)
        for status, deterministic, requested, expected in (
            (ClaimStatus.ACTIVE, True, Disposition.ALLOW, Disposition.ALLOW),
            (ClaimStatus.ACTIVE, True, Disposition.REVIEW, Disposition.REVIEW),
            (ClaimStatus.ACTIVE, True, Disposition.BLOCK, Disposition.BLOCK),
            (ClaimStatus.ACTIVE, False, Disposition.ALLOW, Disposition.ALLOW),
            (ClaimStatus.ACTIVE, False, Disposition.REVIEW, Disposition.REVIEW),
            (ClaimStatus.ACTIVE, False, Disposition.BLOCK, Disposition.REVIEW),
            (ClaimStatus.SCAFFOLD, True, Disposition.ALLOW, Disposition.ALLOW),
            (ClaimStatus.SCAFFOLD, True, Disposition.REVIEW, Disposition.REVIEW),
            (ClaimStatus.SCAFFOLD, True, Disposition.BLOCK, Disposition.REVIEW),
            (ClaimStatus.SCAFFOLD, False, Disposition.ALLOW, Disposition.ALLOW),
            (ClaimStatus.SCAFFOLD, False, Disposition.REVIEW, Disposition.REVIEW),
            (ClaimStatus.SCAFFOLD, False, Disposition.BLOCK, Disposition.REVIEW),
            (ClaimStatus.CONJECTURE, True, Disposition.ALLOW, Disposition.ALLOW),
            (ClaimStatus.CONJECTURE, True, Disposition.REVIEW, Disposition.ALLOW),
            (ClaimStatus.CONJECTURE, True, Disposition.BLOCK, Disposition.ALLOW),
            (ClaimStatus.CONJECTURE, False, Disposition.ALLOW, Disposition.ALLOW),
            (ClaimStatus.CONJECTURE, False, Disposition.REVIEW, Disposition.ALLOW),
            (ClaimStatus.CONJECTURE, False, Disposition.BLOCK, Disposition.ALLOW),
        )
    ],
)
def test_evidence_cap_matrix(status, deterministic, requested, expected):
    effective, _ = capped_disposition(requested, status, deterministic)
    assert effective == expected


def test_cap_reason_is_recorded_when_authority_is_downgraded():
    finding = Finding.create(
        finding_id="TEST:CAP:001",
        title="Experimental detector",
        description="Synthetic finding",
        severity=Severity.HIGH,
        requested_disposition=Disposition.BLOCK,
        claim_status=ClaimStatus.SCAFFOLD,
        deterministic=True,
        evaluator="test",
    )
    assert finding.effective_disposition == Disposition.REVIEW
    assert "capped" in finding.cap_reason
    assert finding.to_dict()["cap_reason"] == finding.cap_reason


def test_event_rejects_non_json_argument_values():
    with pytest.raises(CanonicalJSONError):
        AssuranceEvent(
            phase=Phase.TOOL,
            tool_name="demo",
            tool_arguments={"bad": object()},
        )


def test_event_rejects_non_finite_numbers():
    with pytest.raises(CanonicalJSONError):
        AssuranceEvent(
            phase=Phase.TOOL,
            tool_name="demo",
            tool_arguments={"bad": float("nan")},
        )


@pytest.mark.parametrize(
    "kwargs",
    [
        {"phase": Phase.OUTPUT, "content": 7},
        {"phase": Phase.TOOL, "tool_name": "demo", "tool_arguments": []},
        {"phase": Phase.TOOL, "tool_name": "demo", "side_effect": "false"},
        {"phase": Phase.TOOL, "tool_name": "demo", "human_approved": "yes"},
        {"phase": Phase.OUTPUT, "content": "text", "tool_name": "demo"},
    ],
)
def test_event_rejects_ambiguous_typed_values(kwargs):
    with pytest.raises((TypeError, ValueError)):
        AssuranceEvent(**kwargs)


def test_canonical_hash_is_key_order_independent():
    assert sha256_json({"a": 1, "b": 2}) == sha256_json({"b": 2, "a": 1})


def test_all_cap_combinations_have_a_defined_result():
    combinations = itertools.product(ClaimStatus, (False, True), Disposition)
    assert len([capped_disposition(requested, status, deterministic) for status, deterministic, requested in combinations]) == 18
