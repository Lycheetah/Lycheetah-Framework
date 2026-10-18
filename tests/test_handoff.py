"""Tests for Lycheetah Cross-Seat Task & Context Capsule (`lycheetah.handoff`).

Claim coverage:
  [ACTIVE] Task capsule creation, validation, and JSON serialization round-trip
  [ACTIVE] ASCII terminal card rendering with negative constraints and boundaries
  [ACTIVE] Clean execution completion and verification pass
  [ACTIVE] Adversarial rejection: protected path breach (e.g. README.md modified)
  [ACTIVE] Adversarial rejection: scope expansion (files modified outside target_paths)
  [ACTIVE] Adversarial rejection: task digest mutation / post-issuance tampering
  [ACTIVE] Adversarial rejection: missing execution result or unexecuted status
  [ACTIVE] Seamless integration with CompactionShield and AgentStatePacket
  [ACTIVE] CLI entry point `lycheetah-handoff` commands: create, inspect, complete, verify
"""

from __future__ import annotations

import json
from dataclasses import replace
import pytest

from lycheetah.cli import handoff_cli
from lycheetah.compaction import CodecError, CompactionShield
from lycheetah.handoff import (
    HANDOFF_SCHEMA_VERSION,
    HandoffCapsule,
    HandoffError,
    create_capsule,
    verify_handoff,
)


@pytest.mark.active
def test_create_capsule_defaults():
    capsule = create_capsule(purpose="Implement sealed handoff tool")
    assert capsule.schema == HANDOFF_SCHEMA_VERSION
    assert capsule.issuer == "Mac"
    assert capsule.recipient == "Aetheron"
    assert capsule.scope == "code:write"
    assert capsule.risk == "MEDIUM"
    assert capsule.status == "PROPOSED"
    assert capsule.purpose == "Implement sealed handoff tool"
    assert capsule.capsule_id.startswith("ho-")
    assert len(capsule.task_digest()) == 64


@pytest.mark.active
def test_create_capsule_validation_errors():
    with pytest.raises(HandoffError, match="risk must be one of"):
        create_capsule(purpose="Invalid risk", risk="ULTRA_HIGH")

    with pytest.raises(HandoffError, match="purpose cannot be empty"):
        create_capsule(purpose="   ")

    with pytest.raises(HandoffError, match="capsule_id cannot be empty"):
        HandoffCapsule(
            capsule_id="",
            created_at="2026-10-18T00:00:00Z",
            issuer="Mac",
            recipient="Aetheron",
            scope="code:write",
            purpose="Valid purpose",
            risk="LOW",
            target_paths=(),
            protected_paths=(),
            invariants=(),
            recovery=(),
            unknowns=(),
        )


@pytest.mark.active
def test_capsule_serialization_roundtrip():
    capsule = create_capsule(
        purpose="Refactor core assurance engine",
        issuer="Mac",
        recipient="Sol",
        scope="code:refactor",
        risk="HIGH",
        target_paths=["lycheetah/assurance/runtime.py"],
        protected_paths=["README.md", "pyproject.toml"],
        invariants=["Zero regression on existing test suite", "Ed25519 signature preserved"],
        recovery=["git checkout HEAD -- lycheetah/assurance/"],
        unknowns=["Will audit chain need re-keying?"],
        authority_id="mac-auth-01",
    )

    data = capsule.to_dict()
    assert data["schema"] == HANDOFF_SCHEMA_VERSION
    assert data["status"] == "PROPOSED"
    assert data["task_digest"] == capsule.task_digest()
    assert len(data["invariants"]) == 2
    assert len(data["protected_paths"]) == 2

    restored = HandoffCapsule.from_dict(data)
    assert restored.capsule_id == capsule.capsule_id
    assert restored.purpose == capsule.purpose
    assert restored.task_digest() == capsule.task_digest()
    assert restored.target_paths == capsule.target_paths
    assert restored.protected_paths == capsule.protected_paths
    assert restored.authority_id == "mac-auth-01"


@pytest.mark.active
def test_capsule_render_card():
    capsule = create_capsule(
        purpose="Build handoff CLI interface with visual cards",
        issuer="Mac",
        recipient="Aetheron",
        target_paths=["lycheetah/cli.py"],
        protected_paths=["README.md"],
        invariants=["README must never be touched"],
        recovery=["git reset --hard HEAD"],
    )

    card = capsule.render_card()
    assert "LYCHEETAH HANDOFF CAPSULE" in card
    assert "From: Mac ──► To: Aetheron" in card
    assert "PURPOSE" in card
    assert "Build handoff CLI interface with visual cards" in card
    assert "PROTECTED PATHS (HANDS OFF)" in card
    assert "✖ README.md" in card
    assert "NON-NEGOTIABLE INVARIANTS" in card
    assert "README must never be touched" in card
    assert "RECOVERY / ROLLBACK PATH" in card
    assert "Task Digest:" in card


@pytest.mark.active
def test_to_agent_state_packet_and_compaction_shield():
    capsule = create_capsule(
        purpose="Deploy signed release",
        risk="HIGH",
        target_paths=["dist/release.whl"],
        invariants=["No unsigned wheels in index"],
        recovery=["Rollback repo index"],
        unknowns=["Network latency on signing authority"],
    )
    packet = capsule.to_agent_state_packet()
    assert packet.id == capsule.capsule_id
    assert packet.purpose == capsule.purpose
    assert packet.risk == "HIGH"
    assert len(packet.invariants) == 1
    assert len(packet.recovery) == 1
    assert len(packet.unknowns) == 1

    # CompactionShield round-trip verification
    wire = CompactionShield.compact(packet)
    restored_pkt = CompactionShield.decompact(wire)
    comp_report = CompactionShield.verify_integrity(packet, restored_pkt)
    assert comp_report["is_safe"] is True


@pytest.mark.active
def test_clean_completion_and_verification():
    ref = create_capsule(
        purpose="Implement handoff tool",
        issuer="Mac",
        recipient="Aetheron",
        target_paths=["lycheetah/handoff.py", "lycheetah/cli.py"],
        protected_paths=["README.md"],
        invariants=["README remains untouched"],
        recovery=["git checkout HEAD -- lycheetah/"],
    )

    executed = ref.complete(
        completed_by="Aetheron",
        summary="Successfully implemented handoff capsule and CLI",
        modified_files=["lycheetah/handoff.py", "lycheetah/cli.py"],
        receipt_digest="sha256:11223344556677889900aabbccddeeff",
        evidence_notes="All unit and CLI tests passed cleanly",
    )

    assert executed.status == "EXECUTED"
    assert executed.result is not None
    assert executed.result.completed_by == "Aetheron"

    card = executed.render_card()
    assert "EXECUTION RESULT" in card
    assert "Completed by: Aetheron" in card
    assert "Receipt: sha256:11223344" in card

    verdict = verify_handoff(ref, executed)
    assert verdict.passed is True
    assert verdict.status == "DECLARATIONS_MATCH"
    assert verdict.details["verification_basis"] == "DECLARATIONS_ONLY"
    assert verdict.details["filesystem_observed"] is False
    assert verdict.details["issuer_authenticated"] is False
    assert len(verdict.violations) == 0
    assert verdict.details["modified_count"] == 2
    assert verdict.details["protected_checked"] == 1


@pytest.mark.active
def test_adversarial_protected_path_breach():
    ref = create_capsule(
        purpose="Refactor docs and code",
        issuer="Mac",
        recipient="Aetheron",
        target_paths=["lycheetah/handoff.py", "README.md"],  # target includes README
        protected_paths=["README.md"],  # but protected forbids README!
    )

    # Agent modified README.md
    executed = ref.complete(
        completed_by="Aetheron",
        summary="Edited README and code",
        modified_files=["lycheetah/handoff.py", "README.md"],
    )

    verdict = verify_handoff(ref, executed)
    assert verdict.passed is False
    assert verdict.status == "REJECTED_VIOLATION"
    assert any("PROTECTED PATH VIOLATION" in v for v in verdict.violations)
    assert any("README.md" in v for v in verdict.violations)


@pytest.mark.active
def test_adversarial_scope_expansion():
    ref = create_capsule(
        purpose="Scoped edit",
        issuer="Mac",
        recipient="Aetheron",
        target_paths=["lycheetah/handoff.py"],
        protected_paths=["README.md"],
    )

    # Agent modified extra_unapproved.py
    executed = ref.complete(
        completed_by="Aetheron",
        summary="Modified target and an extra unapproved file",
        modified_files=["lycheetah/handoff.py", "lycheetah/extra_unapproved.py"],
    )

    verdict = verify_handoff(ref, executed)
    assert verdict.passed is False
    assert any("SCOPE EXPANSION" in v for v in verdict.violations)
    assert any("extra_unapproved.py" in v for v in verdict.violations)


@pytest.mark.active
def test_adversarial_task_digest_mutation():
    ref = create_capsule(
        purpose="Original purpose",
        issuer="Mac",
        recipient="Aetheron",
        invariants=["Invariant A"],
    )

    executed = ref.complete(
        completed_by="Aetheron",
        summary="Finished",
    )

    # Simulate tampered executed capsule where an invariant was weakened/altered
    tampered_capsule = replace(executed, invariants=({"id": "INV-1", "text": "Altered invariant"},))

    verdict = verify_handoff(ref, tampered_capsule)
    assert verdict.passed is False
    assert any("task specification was mutated" in v for v in verdict.violations)


@pytest.mark.active
def test_verification_rejects_unexecuted_or_missing_result():
    ref = create_capsule(purpose="Test missing result")
    verdict = verify_handoff(ref, ref)
    assert verdict.passed is False
    assert verdict.status == "REJECTED_NO_RESULT"


@pytest.mark.active
def test_cli_e2e_workflow(tmp_path, capsys):
    ref_file = tmp_path / "task_ref.json"
    exec_file = tmp_path / "task_exec.json"

    # 1. CLI create
    handoff_cli(
        [
            "create",
            "--purpose",
            "Build CLI handoff suite",
            "--from",
            "Mac",
            "--to",
            "Aetheron",
            "--target",
            "lycheetah/cli.py",
            "lycheetah/handoff.py",
            "--protect",
            "README.md",
            "--invariant",
            "README untouched",
            "--recovery",
            "git checkout HEAD",
            "-o",
            str(ref_file),
        ]
    )
    assert ref_file.exists()

    # 2. CLI inspect (card)
    handoff_cli(["inspect", str(ref_file)])
    card_out = capsys.readouterr().out
    assert "LYCHEETAH HANDOFF CAPSULE" in card_out
    assert "Build CLI handoff suite" in card_out

    # 3. CLI inspect (--json)
    handoff_cli(["inspect", str(ref_file), "--json"])
    json_out = capsys.readouterr().out
    data = json.loads(json_out)
    assert data["purpose"] == "Build CLI handoff suite"

    # 4. CLI complete
    handoff_cli(
        [
            "complete",
            str(ref_file),
            "--by",
            "Aetheron",
            "--summary",
            "Completed implementation cleanly",
            "--modified",
            "lycheetah/cli.py",
            "lycheetah/handoff.py",
            "--receipt",
            "sha256:fedcba9876543210",
            "-o",
            str(exec_file),
        ]
    )
    assert exec_file.exists()

    # 5. CLI verify (clean pass)
    handoff_cli(["verify", str(ref_file), str(exec_file)])
    verify_out = capsys.readouterr().out
    assert "Verdict:   PASS [DECLARATIONS_MATCH]" in verify_out
    assert "Reported declarations match the reference" in verify_out
    assert "filesystem effects and issuer identity unverified" in verify_out

    # 6. CLI verify with --json
    handoff_cli(["verify", str(ref_file), str(exec_file), "--json"])
    verdict_json = json.loads(capsys.readouterr().out)
    assert verdict_json["passed"] is True
    assert verdict_json["status"] == "DECLARATIONS_MATCH"


@pytest.mark.active
def test_cli_verify_failure_exit(tmp_path):
    ref_file = tmp_path / "task_ref.json"
    breach_file = tmp_path / "task_breach.json"

    # Create reference
    handoff_cli(
        [
            "create",
            "--purpose",
            "Sensitive change",
            "--protect",
            "README.md",
            "-o",
            str(ref_file),
        ]
    )

    # Complete with protected path breach
    handoff_cli(
        [
            "complete",
            str(ref_file),
            "--by",
            "Aetheron",
            "--summary",
            "Accidentally touched README",
            "--modified",
            "README.md",
            "-o",
            str(breach_file),
        ]
    )

    # CLI verify must exit with code 1
    with pytest.raises(SystemExit) as exc_info:
        handoff_cli(["verify", str(ref_file), str(breach_file)])
    assert exc_info.value.code == 1


@pytest.mark.parametrize("reported", ["./README.md", "././README.md", "README.md/child"])
def test_protected_path_aliases_are_rejected(reported):
    ref = create_capsule(
        purpose="Audit declared paths", protected_paths=["README.md"], target_paths=["README.md"]
    )
    done = ref.complete(
        completed_by=ref.recipient, summary="Synthetic report", modified_files=[reported]
    )
    verdict = verify_handoff(ref, done)
    assert verdict.passed is False
    assert any("PROTECTED PATH VIOLATION" in v for v in verdict.violations)


@pytest.mark.parametrize("protected", ["private", "private/", "./private"])
def test_protected_directory_children_are_rejected(protected):
    ref = create_capsule(
        purpose="Audit directory protection", protected_paths=[protected], target_paths=["private/"]
    )
    done = ref.complete(
        completed_by=ref.recipient,
        summary="Synthetic report",
        modified_files=["private/nested/data.txt"],
    )
    assert any("PROTECTED PATH VIOLATION" in v for v in verify_handoff(ref, done).violations)


def test_targets_cover_components_without_accepting_sibling_prefixes():
    ref = create_capsule(purpose="Scoped subtree", target_paths=["src/"])
    good = ref.complete(
        completed_by=ref.recipient, summary="Synthetic report", modified_files=["./src/module.py"]
    )
    bad = ref.complete(
        completed_by=ref.recipient,
        summary="Synthetic report",
        modified_files=["src_other/module.py"],
    )
    assert verify_handoff(ref, good).passed is True
    assert verify_handoff(ref, bad).passed is False


def test_empty_targets_permit_no_reported_file_modification():
    ref = create_capsule(purpose="No write targets")
    done = ref.complete(
        completed_by=ref.recipient, summary="Synthetic report", modified_files=["undeclared.txt"]
    )
    assert verify_handoff(ref, done).passed is False


def test_completion_recipient_must_match():
    ref = create_capsule(purpose="A task for one receiving seat")
    done = ref.complete(completed_by="another-seat", summary="Synthetic report")
    assert any("recipient mismatch" in v for v in verify_handoff(ref, done).violations)


def test_serialized_digest_is_checked_before_accepting_a_capsule():
    data = create_capsule(purpose="Original task").to_dict()
    data["purpose"] = "Changed task"
    with pytest.raises(HandoffError, match="task_digest"):
        HandoffCapsule.from_dict(data)


@pytest.mark.parametrize(
    "field,value",
    [
        ("purpose", None),
        ("risk", []),
        ("status", "UNKNOWN"),
        ("target_paths", "src/module.py"),
        ("invariants", [{"id": "I1", "text": None}]),
        ("result", []),
        ("created_at", "yesterday"),
    ],
)
def test_malformed_capsule_fields_fail_visibly(field, value):
    data = create_capsule(purpose="Valid task").to_dict()
    data[field] = value
    with pytest.raises(HandoffError):
        HandoffCapsule.from_dict(data)


@pytest.mark.parametrize(
    "path",
    [
        "../README.md",
        "src/../README.md",
        "/tmp/file",
        "C:/file",
        "src\\file",
        ".",
        "",
        "src/*",
        "src/\x1b",
    ],
)
def test_unsafe_or_ambiguous_paths_are_rejected(path):
    with pytest.raises(HandoffError):
        create_capsule(purpose="Reject invalid path", target_paths=[path])


@pytest.mark.parametrize(
    "name", ["target_paths", "protected_paths", "invariants", "recovery", "unknowns"]
)
def test_a_string_is_not_accepted_as_a_sequence_of_entries(name):
    with pytest.raises(HandoffError):
        create_capsule(purpose="Reject accidental character lists", **{name: "not-a-list"})


def test_unknowns_do_not_invent_recovery_or_human_authority():
    capsule = create_capsule(purpose="An unresolved dependency", unknowns=["Is backup available?"])
    packet = capsule.to_agent_state_packet()
    assert packet.recovery == []
    assert packet.authority == []
    assert "Is backup available?" in packet.claim
    with pytest.raises(CodecError, match="PROTECTED_UNKNOWN_WITHOUT_RECOVERY"):
        CompactionShield.compact(packet)


def test_unknown_wording_survives_the_packet_roundtrip():
    question = "Does the restore identity still have access?"
    capsule = create_capsule(
        purpose="Retain the actual question",
        unknowns=[question],
        recovery=["Stop before changes if the dependency is unresolved"],
    )
    packet = capsule.to_agent_state_packet()
    restored = CompactionShield.decompact(CompactionShield.compact(packet))
    assert question in restored.claim
    assert restored.claim == packet.claim


def test_nested_task_records_are_immutable_and_serialization_copies_them():
    capsule = create_capsule(purpose="Keep the reference stable", invariants=["Keep scope"])
    with pytest.raises(TypeError):
        capsule.invariants[0]["text"] = "Weakened"
    data = capsule.to_dict()
    data["invariants"][0]["text"] = "Weakened outside"
    assert capsule.invariants[0]["text"] == "Keep scope"


def test_completion_before_creation_is_rejected():
    ref = create_capsule(purpose="Time order", created_at="2026-10-18T12:00:00Z")
    done = ref.complete(
        completed_by=ref.recipient, summary="Synthetic report", now="2026-10-18T11:00:00Z"
    )
    assert any("precedes" in v for v in verify_handoff(ref, done).violations)


def test_an_existing_completion_cannot_be_silently_replaced():
    ref = create_capsule(purpose="Immutable completion")
    done = ref.complete(completed_by=ref.recipient, summary="First report")
    with pytest.raises(HandoffError, match="already exists"):
        done.complete(completed_by=ref.recipient, summary="Replacement report")


def test_cli_refuses_to_overwrite_an_existing_reference(tmp_path, capsys):
    output = tmp_path / "reference.json"
    output.write_text("preserve these existing bytes")
    with pytest.raises(SystemExit) as error:
        handoff_cli(["create", "--purpose", "New task", "-o", str(output)])
    assert error.value.code == 1
    assert output.read_text() == "preserve these existing bytes"
    assert "Error:" in capsys.readouterr().err
