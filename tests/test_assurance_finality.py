from dataclasses import dataclass

from lycheetah.assurance.finality import (
    AdmissionWitness,
    EvidenceMode,
    EvidenceRecord,
    EvidenceRequirement,
    FinalityGate,
    MappingEvidenceStore,
)
from lycheetah.assurance.models import AssuranceEvent, Disposition, Phase


@dataclass(frozen=True)
class Verification:
    valid: bool


class FakeReceipt:
    counter = 0

    def __init__(self, decision, policy):
        FakeReceipt.counter += 1
        self.decision = decision
        self.policy = policy
        self.digest = f"{FakeReceipt.counter:064x}"
        self._valid = True

    def verify(self):
        return Verification(self._valid)


class FakeRuntime:
    def __init__(self):
        self.decision = Disposition.ALLOW
        self.policy = {
            "id": "test.policy",
            "version": "1",
            "sha256": "a" * 64,
        }

    def evaluate(self, event):
        return FakeReceipt(self.decision, dict(self.policy))


def event(effect_id="evt-1", amount=5):
    return AssuranceEvent(
        phase=Phase.TOOL,
        event_id=effect_id,
        trace_id="trace-1",
        tool_name="deploy.promote",
        tool_arguments={"artifact": "A", "amount": amount},
        scopes=("production.deploy",),
        side_effect=True,
        human_approved=True,
    )


def record(version="1", subject="A", value="tests-1", status="PASS"):
    return EvidenceRecord("ci-required", version, subject, value, status)


def gate_with(record_value=None):
    runtime = FakeRuntime()
    store = MappingEvidenceStore([record_value or record()])
    return runtime, store, FinalityGate(runtime, store)


REQ = EvidenceRequirement(
    "ci-required",
    EvidenceMode.SUBJECT_STATUS,
    required_status="PASS",
    required_subject_hash="A",
)


def test_fresh_dependency_can_finalize():
    runtime, store, gate = gate_with()
    admitted = gate.admit(event(), [REQ])
    assert admitted.disposition == Disposition.ALLOW
    assert admitted.ready_for_finality is True
    final = gate.finalize(admitted.witness, event())
    assert final.disposition == Disposition.ALLOW
    assert final.ready is True


def test_missing_evidence_routes_to_review_at_admission():
    runtime = FakeRuntime()
    gate = FinalityGate(runtime, MappingEvidenceStore())
    result = gate.admit(event(), [REQ])
    assert result.disposition == Disposition.REVIEW
    assert result.witness is None


def test_status_change_after_admission_routes_to_review():
    runtime, store, gate = gate_with()
    admitted = gate.admit(event(), [REQ])
    store.put(record(version="2", value="tests-2", status="FAIL"))
    final = gate.finalize(admitted.witness, event())
    assert final.disposition == Disposition.REVIEW
    assert final.reason == "evidence-predicate-false-at-finality"
    assert final.ready is False


def test_new_equivalent_subject_status_receipt_remains_usable():
    runtime, store, gate = gate_with()
    admitted = gate.admit(event(), [REQ])
    store.put(record(version="2", value="tests-2", status="PASS"))
    final = gate.finalize(admitted.witness, event())
    assert final.disposition == Disposition.ALLOW
    assert final.ready is True


def test_exact_mode_rejects_newer_even_still_pass():
    runtime, store, gate = gate_with()
    exact = EvidenceRequirement("ci-required", EvidenceMode.EXACT, "PASS", "A")
    admitted = gate.admit(event(), [exact])
    store.put(record(version="2", value="tests-2", status="PASS"))
    final = gate.finalize(admitted.witness, event())
    assert final.disposition == Disposition.REVIEW
    assert final.reason == "exact-evidence-changed-after-admission"


def test_wrong_subject_after_admission_routes_to_review():
    runtime, store, gate = gate_with()
    admitted = gate.admit(event(), [REQ])
    store.put(record(version="2", subject="B", value="tests-b", status="PASS"))
    final = gate.finalize(admitted.witness, event())
    assert final.disposition == Disposition.REVIEW
    assert final.evidence_key == "ci-required"


def test_policy_change_after_admission_routes_to_review():
    runtime, store, gate = gate_with()
    admitted = gate.admit(event(), [REQ])
    runtime.policy["version"] = "2"
    runtime.policy["sha256"] = "b" * 64
    final = gate.finalize(admitted.witness, event())
    assert final.disposition == Disposition.REVIEW
    assert final.reason == "policy-changed-after-admission"


def test_underlying_runtime_review_is_propagated_at_finality():
    runtime, store, gate = gate_with()
    admitted = gate.admit(event(), [REQ])
    runtime.decision = Disposition.REVIEW
    final = gate.finalize(admitted.witness, event())
    assert final.disposition == Disposition.REVIEW
    assert final.ready is False


def test_underlying_runtime_block_is_propagated_at_finality():
    runtime, store, gate = gate_with()
    admitted = gate.admit(event(), [REQ])
    runtime.decision = Disposition.BLOCK
    final = gate.finalize(admitted.witness, event())
    assert final.disposition == Disposition.BLOCK
    assert final.ready is False


def test_action_substitution_routes_to_review():
    runtime, store, gate = gate_with()
    admitted = gate.admit(event(), [REQ])
    changed = event(amount=999)
    final = gate.finalize(admitted.witness, changed)
    assert final.disposition == Disposition.REVIEW
    assert final.reason == "event-changed-after-admission"


def test_witness_round_trip_and_tamper_detection():
    runtime, store, gate = gate_with()
    admitted = gate.admit(event(), [REQ])
    raw = admitted.witness.to_dict()
    restored = AdmissionWitness.from_dict(raw)
    assert restored.verify()
    raw["policy_version"] = "999"
    try:
        AdmissionWitness.from_dict(raw)
    except ValueError as exc:
        assert "digest mismatch" in str(exc)
    else:
        raise AssertionError("tampered witness was accepted")


def test_gate_owned_failure_does_not_invent_block():
    runtime, store, gate = gate_with()
    admitted = gate.admit(event(), [REQ])
    store.put(record(version="2", status="FAIL"))
    final = gate.finalize(admitted.witness, event())
    assert final.disposition == Disposition.REVIEW
    assert final.disposition != Disposition.BLOCK


# Integration-owned regressions, distinct from the supplied FakeRuntime suite.
def test_empty_reissued_witness_cannot_skip_required_evidence():
    from dataclasses import replace
    from lycheetah.assurance.jsonutil import sha256_json
    _, _, gate = gate_with()
    witness = gate.admit(event(), [REQ]).witness
    empty = replace(witness, evidence=())
    empty = replace(empty, digest=sha256_json(empty.body_dict()))
    result = gate.finalize(empty, event())
    assert result.disposition == Disposition.REVIEW
    assert result.ready is False
    assert result.reason == "witness-evidence-empty"


def test_wrong_key_from_provider_cannot_satisfy_dependency():
    class WrongKeyProvider:
        def get_evidence(self, key):
            return EvidenceRecord("unrelated", "1", "A", "tests-1", "PASS")
    gate = FinalityGate(FakeRuntime(), WrongKeyProvider())
    assert gate.admit(event(), [REQ]).ready_for_finality is False


def test_malformed_record_values_are_rejected_without_string_coercion():
    import pytest
    body = record().to_dict()
    for invalid in [None, False, 12, [], {}]:
        body["status"] = invalid
        with pytest.raises(ValueError):
            EvidenceRecord.from_dict(body)


def test_finality_with_real_assurance_runtime_and_evidence_change():
    from lycheetah.assurance import AssuranceRuntime
    store = MappingEvidenceStore([record()])
    gate = FinalityGate(AssuranceRuntime(), store)
    admitted = gate.admit(event(), [REQ])
    assert admitted.ready_for_finality
    assert gate.finalize(admitted.witness, event()).ready
    store.put(record(version="2", status="FAIL"))
    assert not gate.finalize(admitted.witness, event()).ready
