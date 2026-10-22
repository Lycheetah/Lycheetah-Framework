"""What the compaction shield detects, what it cannot, and where its two paths agree."""

from dataclasses import replace

import pytest

from lycheetah.compaction import AgentStatePacket, CompactionShield, ContextProtector
from lycheetah.compaction.codec import classify

U1 = {"id": "U1", "protected": True, "requiredFor": "cutover"}
U2 = {"id": "U2", "protected": False, "requiredFor": "reporting"}
E1 = {"id": "E1", "text": "Plan reviewed", "provenance": "reviewer"}
E2 = {"id": "E2", "text": "Backup taken", "provenance": "operator"}


def _packet(**changes):
    packet = AgentStatePacket(
        id="drift-packet",
        purpose="Migrate a synthetic ledger",
        claim="Dry run only",
        risk="CRITICAL",
        evidence=[dict(E1), dict(E2)],
        unknowns=[dict(U1)],
        invariants=[{"id": "I1", "text": "no deletes"}, {"id": "I2", "text": "no writes"}],
        authority=[{"id": "A1", "scope": "db:write", "text": "Owner approval"}],
        participants=["worker", "reviewer"],
        affected_parties=["customers"],
        dissent=[{"party": "reviewer", "position": "wait for backup"}],
        recovery=[{"id": "R1", "text": "Restore the snapshot"}],
        horizon="this week",
        yield_desc="halt",
    )
    return replace(packet, **changes)


def _protector():
    live = ContextProtector("drift-live", "Migrate a synthetic ledger", "Dry run only", risk="HIGH")
    live.add_invariant("I1", "no deletes").add_unknown("U1", "cutover")
    live.add_recovery("R1", "Restore the snapshot").add_authority("A1", "db:write", "Owner")
    live.add_participant("worker").add_affected_party("customers")
    live.add_evidence("E1", "Plan reviewed", "reviewer")
    return live


def _verdict(reference, candidate):
    result = CompactionShield.verify_integrity(reference, candidate)
    return result["classification"], result["is_safe"]


def test_export_does_not_share_state_with_the_live_accumulator():
    live = _protector()
    snapshot = live.export_packet()
    snapshot.evidence[0]["text"] = "forged"
    snapshot.unknowns.append(dict(U2))
    snapshot.authority.clear()
    assert live.evidence[0]["text"] == "Plan reviewed"
    assert len(live.unknowns) == len(live.authority) == 1

    fresh = live.export_packet()
    kept = fresh.to_dict()
    live.evidence[0]["text"] = "changed later"
    live.unknowns[0]["protected"] = False
    live.add_dissent("auditor", "object")
    assert fresh.to_dict() == kept


@pytest.mark.parametrize(
    "changes, field",
    [
        ({"risk": "LOW"}, "risk"),
        ({"evidence": []}, "evidence"),
        ({"evidence": [{"id": "E1", "text": "All tests passed", "provenance": "invented"}]}, "evidence"),
        ({"evidence": [dict(E2), dict(E1)]}, "evidence"),
        ({"yield_desc": "proceed"}, "yield"),
        ({"horizon": "indefinite"}, "horizon"),
        ({"id": "another-packet"}, "id"),
    ],
    ids=["risk_down", "evidence_dropped", "evidence_invented", "evidence_reordered", "yield",
         "horizon", "id"],
)
def test_noncritical_drift_stays_partial_but_is_named(changes, field):
    result = CompactionShield.verify_integrity(_packet(), _packet(**changes))
    assert (result["classification"], result["is_safe"]) == ("PARTIAL_EQUIVALENT", True)
    assert result["changed_fields"] == [field]


@pytest.mark.parametrize(
    "changes, classification, fields",
    [
        ({"authority": []}, "UNSAFE_COLLAPSE", ["authority"]),
        ({"dissent": []}, "UNSAFE_COLLAPSE", ["dissent"]),
        ({"participants": ["worker"]}, "UNSAFE_COLLAPSE", ["participants"]),
        ({"unknowns": [{**U1, "protected": False}]}, "UNSAFE_COLLAPSE", ["unknown_protection"]),
        ({"unknowns": [{**U1, "id": "U9"}]}, "UNSAFE_COLLAPSE", ["unknown_protection"]),
        (
            {"authority": [{"id": "A1", "scope": "db:admin", "text": "Owner approval"}]},
            "DIVERGENT",
            None,
        ),
        ({"claim": "Live run"}, "DIVERGENT", None),
        ({"participants": ["reviewer", "worker"]}, "DIVERGENT", None),
        (
            {"invariants": [{"id": "I2", "text": "no writes"}, {"id": "I1", "text": "no deletes"}]},
            "DIVERGENT",
            None,
        ),
    ],
    ids=["authority_dropped", "dissent_dropped", "participant_dropped", "unknown_unprotected",
         "protected_unknown_swapped", "authority_altered", "claim_altered",
         "participants_reordered", "invariants_reordered"],
)
def test_missing_altered_and_reordered_critical_context_is_not_safe(changes, classification, fields):
    result = CompactionShield.verify_integrity(_packet(), _packet(**changes))
    assert (result["classification"], result["is_safe"]) == (classification, False)
    assert result.get("fields") == fields


def test_unprotected_unknown_beside_a_protected_one_is_not_a_collapse():
    mixed = _packet(unknowns=[dict(U1), dict(U2)])
    assert _verdict(mixed, replace(mixed, horizon="next week")) == ("PARTIAL_EQUIVALENT", True)
    added = _packet(unknowns=[dict(U1), dict(U2)])
    assert _verdict(_packet(), added) == ("DIVERGENT", False)
    weakened = replace(mixed, unknowns=[{**U1, "protected": False}, dict(U2)])
    assert CompactionShield.verify_integrity(mixed, weakened)["fields"] == ["unknown_protection"]


def test_both_reference_paths_refuse_a_candidate_that_breaks_a_packet_rule():
    broken = _packet(operations=["Y"])
    candidate = replace(broken, risk="LOW")
    by_packet = CompactionShield.verify_integrity(broken, candidate)
    by_digest = CompactionShield.verify_integrity(broken.critical_hash, candidate)
    for result in (by_packet, by_digest):
        assert (result["classification"], result["is_safe"]) == ("UNSAFE_COLLAPSE", False)
        assert "UNKNOWN_WITHOUT_U" in result["violations"]
    inherited = classify(broken.to_dict(), broken.to_dict())
    assert inherited["classification"] == "UNSAFE_COLLAPSE"
    assert "reference" in inherited["reason"]
    assert _verdict(_packet(), _packet()) == ("EXACT_EQUIVALENT", True)


def test_a_stale_snapshot_passes_unless_a_critical_field_moved_on():
    live = _protector()
    stale = live.export_packet()
    live.set_risk("CRITICAL")
    result = live.verify_candidate_summary(stale)
    assert (result["classification"], result["is_safe"]) == ("PARTIAL_EQUIVALENT", True)
    assert result["changed_fields"] == ["risk"]
    live.add_authority("A2", "db:admin", "Second approver")
    result = live.verify_candidate_summary(stale)
    assert (result["classification"], result["is_safe"]) == ("UNSAFE_COLLAPSE", False)
    assert result["fields"] == ["authority"]


def test_digest_reference_names_what_it_cannot_see():
    reference = _packet()
    result = CompactionShield.verify_integrity(
        reference.critical_hash, _packet(risk="LOW", evidence=[])
    )
    assert (result["classification"], result["is_safe"]) == ("PARTIAL_EQUIVALENT", True)
    assert {"risk", "evidence", "horizon", "yield"} <= set(result["unchecked_fields"])


@pytest.mark.parametrize(
    "spoil",
    [str.upper, lambda digest: "z" * 64, lambda digest: digest + "\n", lambda digest: digest[:63]],
    ids=["uppercase", "not_hex", "trailing_newline", "short"],
)
def test_malformed_digest_reference_is_undecodable(spoil):
    reference = _packet()
    assert _verdict(spoil(reference.critical_hash), reference) == ("UNDECODABLE", False)
