"""Risk binding at the sovereign permit boundary, with synthetic consensus.

These checks isolate admission/ledger behaviour. They do not authenticate a
human or validate the truth of a numerical consensus verdict.
"""

from __future__ import annotations

from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
import sqlite3

import pytest

from lycheetah.compaction import AgentStatePacket, CompactionShield
from lycheetah.consensus import DeliberationVerdict
from lycheetah.sovereign_harness import (
    SovereignExecutionHarness,
    SovereignExecutionPermit,
)

ISSUED = 1_700_000_000


def _scenario(root: Path, risk: str = "HIGH", with_authority: bool = False) -> dict:
    verdict = DeliberationVerdict(
        converged=True,
        obstruction_free=True,
        byzantine_safe=True,
        rounds_run=1,
        healthy_agents=["worker"],
        quarantined_agents=[],
        final_drift=0.0,
        consensus_vector=[1.0, 0.0],
        partition_count=1,
        inconsistent_edges=[],
        consensus_digest="a" * 64,
        audit_trail=["Synthetic fixture isolates the risk-admission boundary."],
    )
    packet = AgentStatePacket(
        id="risk-binding-packet",
        purpose="Read a synthetic status with a pinned declared risk",
        claim="The approved read has no external side effect",
        risk=risk,
        invariants=[{"id": "I1", "text": "read_only"}],
        authority=(
            [{"id": "reviewer", "scope": "exec:read", "text": "Declared test grant"}]
            if with_authority else []
        ),
        recovery=[{"id": "R1", "text": "No external mutation to reverse"}],
    )
    action = {"tool": "metrics.read", "target": "synthetic", "side_effect": False}
    harness = SovereignExecutionHarness(root)
    permit = harness.issue_permit(
        permit_id="risk-permit",
        actor="worker",
        authority_id="reviewer" if with_authority else None,
        allowed_scopes=("exec:read",),
        bound_scope="exec:read",
        state_version="synthetic-v1",
        action=action,
        consensus_verdict=verdict,
        reference_packet=packet,
        issued_at=ISSUED,
        ttl_seconds=300,
    )
    calls = []

    def execute():
        calls.append("called")
        return {"status": "success", "value": "synthetic"}

    return {
        "harness": harness, "permit": permit, "packet": packet,
        "verdict": verdict, "action": action, "calls": calls, "executor": execute,
    }


def _evaluate(case: dict, *, reference=None, candidate=None, permit=None):
    return case["harness"].evaluate_and_execute(
        permit=permit if permit is not None else case["permit"],
        consensus=case["verdict"],
        reference_packet=reference if reference is not None else case["packet"],
        candidate_packet=candidate if candidate is not None else case["packet"],
        live_action=case["action"],
        live_scope="exec:read",
        current_state_version="synthetic-v1",
        executor=case["executor"],
        now=ISSUED + 10,
    )


def _assert_denied(case: dict, receipt, reason: str):
    assert receipt.accepted is False
    assert receipt.provider_called is False
    assert receipt.stop_reason == reason
    assert case["calls"] == []
    assert case["harness"].nonce_store.get_permit_record("risk-permit")["status"] == "ISSUED"


def test_candidate_risk_downgrade_cannot_waive_authority(tmp_path):
    """Regression: v1 executes this read after HIGH is downgraded to LOW."""
    case = _scenario(tmp_path)
    candidate = replace(case["packet"], risk="LOW")
    assert candidate.critical_hash == case["packet"].critical_hash
    assert CompactionShield.verify_integrity(case["packet"], candidate)["is_safe"] is True
    _assert_denied(case, _evaluate(case, candidate=candidate), "CANDIDATE_RISK_MISMATCH")


@pytest.mark.parametrize("reference_risk,candidate_risk", [("LOW", "HIGH"), ("LOW", "LOW")])
def test_reference_substitution_cannot_rebind_risk(tmp_path, reference_risk, candidate_risk):
    case = _scenario(tmp_path)
    reference = replace(case["packet"], risk=reference_risk)
    candidate = replace(case["packet"], risk=candidate_risk)
    _assert_denied(
        case, _evaluate(case, reference=reference, candidate=candidate),
        "REFERENCE_RISK_MISMATCH",
    )


def test_changed_permit_risk_without_rehash_is_tampering(tmp_path):
    case = _scenario(tmp_path)
    altered = replace(case["permit"], bound_risk="LOW")
    _assert_denied(case, _evaluate(case, permit=altered), "PERMIT_DIGEST_TAMPERED")


def test_rehashed_risk_change_does_not_match_registered_permit(tmp_path):
    case = _scenario(tmp_path)
    altered = replace(case["permit"], bound_risk="LOW")
    altered = replace(altered, permit_digest=altered.compute_digest())
    low_packet = replace(case["packet"], risk="LOW")
    _assert_denied(
        case, _evaluate(case, reference=low_packet, candidate=low_packet, permit=altered),
        "PERMIT_LEDGER_DIGEST_MISMATCH",
    )


@pytest.mark.parametrize("risk", [None, "", "low", "UNSPECIFIED", True, ["LOW"]])
def test_invalid_or_unbound_risk_refused_at_each_boundary(tmp_path, risk):
    case = _scenario(tmp_path)
    invalid = replace(case["permit"], bound_risk=risk)
    reason = "PERMIT_RISK_UNBOUND" if risk is None else "PERMIT_RISK_INVALID"
    with pytest.raises(ValueError, match=reason):
        case["harness"].nonce_store.register_permit(invalid)
    assert case["harness"].nonce_store.claim_single_use(invalid, ISSUED + 10) == (False, reason)
    _assert_denied(case, _evaluate(case, permit=invalid), reason)


@pytest.mark.parametrize("field,value", [("bound_risk", "LOW"), ("bound_scope", "other")])
def test_direct_store_claim_checks_actual_payload(tmp_path, field, value):
    case = _scenario(tmp_path)
    changed = replace(case["permit"], **{field: value})
    assert case["harness"].nonce_store.claim_single_use(changed, ISSUED + 10) == (
        False, "PERMIT_DIGEST_TAMPERED",
    )
    assert case["harness"].nonce_store.get_permit_record("risk-permit")["status"] == "ISSUED"


def test_legacy_digest_shape_preserved_but_execution_refused(tmp_path):
    case = _scenario(tmp_path)
    legacy = replace(case["permit"], bound_risk=None)
    old_payload = case["permit"].to_dict()
    old_payload.pop("permit_digest")
    old_payload.pop("bound_risk")
    old_payload["schema"] = "lycheetah.sovereign_harness.v1"
    old_bytes = json.dumps(
        old_payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
    ).encode("utf-8")
    old_digest = sha256(old_bytes).hexdigest()
    legacy = replace(legacy, permit_digest=old_digest)
    assert legacy.compute_digest() == old_digest
    assert legacy.to_dict() == {**old_payload, "permit_digest": old_digest}
    _assert_denied(case, _evaluate(case, permit=legacy), "PERMIT_RISK_UNBOUND")


def test_existing_sqlite_schema_and_row_survive_reopening(tmp_path):
    case = _scenario(tmp_path)
    db_path = tmp_path / "ledger" / "sovereign_permits.sqlite3"
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            "INSERT INTO sovereign_permits VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ("historic-v1", "old-digest", "old-actor", None, "exec:read", "v0", "hash",
             100, 200, "ISSUED", None),
        )
        old_columns = connection.execute("PRAGMA table_info(sovereign_permits)").fetchall()
        old_row = connection.execute(
            "SELECT * FROM sovereign_permits WHERE permit_id = 'historic-v1'",
        ).fetchone()
    reopened = SovereignExecutionHarness(tmp_path)
    assert reopened.nonce_store.get_permit_record("historic-v1")["permit_digest"] == "old-digest"
    with sqlite3.connect(db_path) as connection:
        assert connection.execute("PRAGMA table_info(sovereign_permits)").fetchall() == old_columns
        assert connection.execute(
            "SELECT * FROM sovereign_permits WHERE permit_id = 'historic-v1'",
        ).fetchone() == old_row
    case["harness"] = reopened
    _assert_denied(
        case, _evaluate(case, candidate=replace(case["packet"], risk="LOW")),
        "CANDIDATE_RISK_MISMATCH",
    )


@pytest.mark.parametrize("risk", ["LOW", "MEDIUM", "HIGH", "CRITICAL"])
def test_valid_risk_bound_permit_still_executes_once(tmp_path, risk):
    case = _scenario(tmp_path, risk=risk, with_authority=True)
    assert case["permit"].to_dict()["schema"] == "lycheetah.sovereign_permit.v2"
    assert case["permit"].bound_risk == risk
    receipt = _evaluate(case, candidate=case["packet"].to_wire())
    assert receipt.accepted is True
    assert receipt.provider_called is True
    assert receipt.compaction_summary["reference_risk"] == risk
    assert receipt.compaction_summary["bound_risk"] == risk
    assert case["calls"] == ["called"]
    replay = _evaluate(case)
    assert replay.accepted is False
    assert replay.stop_reason == "PERMIT_REPLAYED"
    assert case["calls"] == ["called"]


@pytest.mark.parametrize("risk", ["LOW", "MEDIUM"])
def test_bound_lower_risk_read_can_execute_without_declared_authority(tmp_path, risk):
    case = _scenario(tmp_path, risk=risk)
    assert _evaluate(case).accepted is True
    assert case["calls"] == ["called"]


@pytest.mark.parametrize("risk", ["HIGH", "CRITICAL"])
def test_bound_high_risk_still_requires_authority(tmp_path, risk):
    case = _scenario(tmp_path, risk=risk)
    _assert_denied(case, _evaluate(case), "HUMAN_AUTHORITY_REQUIRED")


def test_low_level_issuance_requires_explicit_bound_risk(tmp_path):
    case = _scenario(tmp_path)
    args = {
        "permit_id": "direct", "actor": "worker", "authority_id": None,
        "allowed_scopes": ("exec:read",), "bound_scope": "exec:read",
        "state_version": "v1", "action": case["action"],
        "consensus_digest": "a" * 64,
        "compaction_critical_hash": case["packet"].critical_hash,
        "bound_packet_id": case["packet"].id,
    }
    with pytest.raises(TypeError, match="bound_risk"):
        SovereignExecutionPermit.issue(**args)
    with pytest.raises(ValueError, match="bound_risk"):
        SovereignExecutionPermit.issue(**args, bound_risk="low")
    assert SovereignExecutionPermit.issue(**args, bound_risk="HIGH").bound_risk == "HIGH"
