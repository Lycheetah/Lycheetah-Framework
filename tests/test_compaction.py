"""Tests for lycheetah.compaction codec and context shield."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from lycheetah.compaction import (
    AgentStatePacket,
    CodecError,
    CompactionShield,
    ContextProtector,
    build_codebook,
    canonical_json,
    classify,
    critical_hash,
    decode,
    encode,
    full_hash,
    safety_violations,
    validate_codebook,
    validate_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
CORPUS_PATH = (
    REPO_ROOT
    / "03_LAMAGUE_L1"
    / "22_REVERSIBLE_COMPRESSION_v1.0"
    / "corpus"
    / "packets.jsonl"
)
SPLIT_PATH = (
    REPO_ROOT
    / "03_LAMAGUE_L1"
    / "22_REVERSIBLE_COMPRESSION_v1.0"
    / "corpus"
    / "split.json"
)


def load_corpus_packets() -> list[dict]:
    if CORPUS_PATH.exists():
        return [
            json.loads(line)
            for line in CORPUS_PATH.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    return []


@pytest.fixture(scope="module")
def corpus():
    packets = load_corpus_packets()
    assert len(packets) == 36, "Canonical corpus must contain exactly 36 packets"
    return packets


@pytest.fixture(scope="module")
def codebook(corpus):
    if SPLIT_PATH.exists():
        split = json.loads(SPLIT_PATH.read_text(encoding="utf-8"))
        train_ids = set(split.get("training", []))
        train = [p for p in corpus if p["id"] in train_ids]
    else:
        train = corpus[:24]
    return build_codebook(train, max_entries=20)


# ============================================================================
# 1. Exact Round-Trip & Hash Verification
# ============================================================================


def test_corpus_count(corpus):
    assert len(corpus) == 36


def test_plain_roundtrip_all(corpus):
    for packet in corpus:
        wire = encode(packet)
        restored = decode(wire)
        assert canonical_json(restored) == canonical_json(packet)
        assert full_hash(restored) == full_hash(packet)
        assert critical_hash(restored) == critical_hash(packet)


def test_plain_codec_compression_ratio(corpus):
    for packet in corpus:
        raw_size = len(canonical_json(packet).encode("utf-8"))
        wire_size = len(encode(packet).encode("utf-8"))
        assert wire_size < raw_size


def test_dictionary_roundtrip_all(corpus, codebook):
    validate_codebook(codebook)
    assert len(codebook["entries"]) == 20
    for packet in corpus:
        wire = encode(packet, codebook)
        assert wire.startswith("L1D")
        restored = decode(wire, codebook)
        assert canonical_json(restored) == canonical_json(packet)
        assert full_hash(restored) == full_hash(packet)
        assert critical_hash(restored) == critical_hash(packet)


def test_dictionary_source_requires_codebook(corpus, codebook):
    wire = encode(corpus[0], codebook)
    with pytest.raises(CodecError, match="L1D source requires a codebook"):
        decode(wire, None)


def test_out_of_range_dictionary_reference_rejected(corpus, codebook):
    wire = encode(corpus[0], codebook)
    body = json.loads(wire[3:])
    body["p"] = 999999
    with pytest.raises(CodecError, match="dictionary reference 999999 is out of range"):
        decode("L1D" + json.dumps(body, separators=(",", ":")), codebook)


# ============================================================================
# 2. Schema and Validation Constraints
# ============================================================================


def test_missing_required_field_rejected(corpus):
    packet = copy.deepcopy(corpus[0])
    del packet["purpose"]
    with pytest.raises(CodecError, match="missing required fields: purpose"):
        validate_packet(packet)


def test_unknown_field_rejected(corpus):
    packet = copy.deepcopy(corpus[0])
    packet["unexpected_property"] = True
    with pytest.raises(CodecError, match="unknown packet fields: unexpected_property"):
        validate_packet(packet)


def test_invalid_schema_name_rejected(corpus):
    packet = copy.deepcopy(corpus[0])
    packet["schema"] = "INVALID-SCHEMA"
    with pytest.raises(CodecError, match="schema must equal"):
        validate_packet(packet)


def test_invalid_operation_rejected(corpus):
    packet = copy.deepcopy(corpus[0])
    packet["operations"].append("9")
    with pytest.raises(CodecError, match="invalid operation '9'"):
        validate_packet(packet)


def test_invalid_wire_prefix_rejected():
    with pytest.raises(CodecError, match="source must begin with L1 or L1D"):
        decode("INVALID_WIRE_FORMAT{}")


def test_corrupt_compressed_json_rejected():
    with pytest.raises(CodecError, match="invalid compressed JSON"):
        decode("L1{broken_json")


# ============================================================================
# 3. Semantic Safety Rules & Fail-Closed Invariants
# ============================================================================


def test_all_corpus_packets_pass_safety(corpus):
    for packet in corpus:
        assert safety_violations(packet) == []


def test_protected_unknown_without_recovery_fails_closed(corpus):
    packet = copy.deepcopy(corpus[0])
    packet["unknowns"] = [
        {"id": "u1", "protected": True, "requiredFor": "DB schema sanity"}
    ]
    packet["recovery"] = []
    # Both safety_violations and encode should refuse this packet
    violations = safety_violations(packet)
    assert "PROTECTED_UNKNOWN_WITHOUT_RECOVERY" in violations
    with pytest.raises(CodecError, match="PROTECTED_UNKNOWN_WITHOUT_RECOVERY"):
        encode(packet)


def test_operations_cross_checks(corpus):
    # Unknown without U
    p1 = copy.deepcopy(corpus[0])
    p1["unknowns"] = [{"id": "u1", "protected": False, "requiredFor": "check"}]
    p1["operations"] = [op for op in p1["operations"] if op != "U"]
    assert "UNKNOWN_WITHOUT_U" in safety_violations(p1)

    # Authority without G
    p2 = copy.deepcopy(corpus[0])
    p2["authority"] = [{"id": "a1", "scope": "admin", "text": "lead"}]
    p2["operations"] = [op for op in p2["operations"] if op != "G"]
    assert "AUTHORITY_OR_AFFECTED_WITHOUT_G" in safety_violations(p2)

    # Dissent without V
    p3 = copy.deepcopy(corpus[0])
    p3["dissent"] = [{"party": "reviewer", "position": "object"}]
    p3["operations"] = [op for op in p3["operations"] if op != "V"]
    assert "DISSENT_WITHOUT_V" in safety_violations(p3)

    # Recovery without F
    p4 = copy.deepcopy(corpus[0])
    p4["recovery"] = [{"id": "r1", "text": "restore"}]
    p4["operations"] = [op for op in p4["operations"] if op != "F"]
    assert "RECOVERY_WITHOUT_FOLD" in safety_violations(p4)

    # Value flow without affected parties
    p5 = copy.deepcopy(corpus[0])
    p5["valueFlow"] = [
        {"source": "a", "recipient": "b", "consent": "REVOCABLE", "kind": "token"}
    ]
    p5["affectedParties"] = []
    assert "VALUE_FLOW_WITHOUT_AFFECTED_PARTY" in safety_violations(p5)


# ============================================================================
# 4. Classification & Tamper Detection
# ============================================================================


def test_exact_classification(corpus):
    result = classify(corpus[0], copy.deepcopy(corpus[0]))
    assert result["classification"] == "EXACT_EQUIVALENT"


def test_safe_extension_is_partial(corpus):
    candidate = copy.deepcopy(corpus[0])
    candidate["evidence"].append(
        {"id": "e_new", "text": "Extra log line", "provenance": "audit://2"}
    )
    result = classify(corpus[0], candidate)
    assert result["classification"] == "PARTIAL_EQUIVALENT"


def test_loss_of_unknown_is_unsafe(corpus):
    candidate = copy.deepcopy(corpus[0])
    candidate["unknowns"] = []
    result = classify(corpus[0], candidate)
    assert result["classification"] == "UNSAFE_COLLAPSE"


def test_invariant_text_change_is_divergent(corpus):
    candidate = copy.deepcopy(corpus[0])
    candidate["invariants"][0]["text"] += " Modified."
    result = classify(corpus[0], candidate)
    assert result["classification"] == "DIVERGENT"


# ============================================================================
# 5. High-Level Ergonomics: AgentStatePacket, Shield, and ContextProtector
# ============================================================================


def test_agent_state_packet_roundtrip(corpus):
    packet_dict = corpus[0]
    asp = AgentStatePacket.from_dict(packet_dict)
    assert asp.critical_hash == critical_hash(packet_dict)
    assert asp.full_hash == full_hash(packet_dict)

    # Wire serialization
    wire = asp.to_wire()
    restored = AgentStatePacket.from_wire(wire)
    assert restored.to_dict() == packet_dict


def test_agent_state_packet_auto_operations():
    asp = AgentStatePacket(
        id="auto-ops-test",
        purpose="Test automatic operation inference",
        claim="Auto operations work",
        invariants=[{"id": "inv1", "text": "Stay intact"}],
        unknowns=[{"id": "u1", "protected": False, "requiredFor": "testing"}],
        authority=[{"id": "a1", "scope": "test", "text": "owner"}],
        dissent=[{"party": "qa", "position": "needs more tests"}],
        recovery=[{"id": "r1", "text": "rollback"}],
        yield_desc="ready",
    )
    d = asp.to_dict()
    assert set(d["operations"]) == {"U", "G", "V", "F", "Y"}
    assert safety_violations(d) == []


def test_compaction_shield_verify_integrity(corpus):
    ref = corpus[0]
    # Exact equivalent
    verdict = CompactionShield.verify_integrity(ref, copy.deepcopy(ref))
    assert verdict["is_safe"] is True
    assert verdict["classification"] == "EXACT_EQUIVALENT"

    # Reference as critical_hash hex string
    ref_hash = critical_hash(ref)
    verdict2 = CompactionShield.verify_integrity(ref_hash, copy.deepcopy(ref))
    assert verdict2["is_safe"] is True
    assert verdict2["candidate_critical_hash"] == ref_hash

    # Mutated candidate
    bad = copy.deepcopy(ref)
    bad["invariants"][0]["text"] += " altered"
    verdict3 = CompactionShield.verify_integrity(ref_hash, bad)
    assert verdict3["is_safe"] is False
    assert verdict3["classification"] == "DIVERGENT"


def test_context_protector_workflow():
    protector = ContextProtector(
        session_id="agent-session-42",
        purpose="Migrate database cluster",
        claim="Prepared staging migration",
        risk="HIGH",
        horizon="Deployment window 2 hours",
        yield_desc="Proceed with migration script",
    )
    protector.add_invariant("inv-1", "Never drop customer tables without explicit approval")
    protector.add_participant("agent-worker")
    protector.add_affected_party("devops-team")
    protector.add_authority("auth-1", "cluster-admin", "DevOps on-call holds veto")
    protector.add_dissent("dba-peer", "Verify lock timeouts first")
    protector.add_unknown("u-1", "Exact replica lag under heavy load", protected=True)
    protector.add_evidence("ev-1", "Staging load test output", "logs/staging.log")
    protector.add_value_flow("devops-team", "agent-worker", "REVOCABLE", "cluster-creds")

    # If we try to export without recovery when protected unknowns exist -> raises CodecError
    with pytest.raises(CodecError, match="Protected unknowns are declared, but no recovery path"):
        protector.export_packet()

    # Now add recovery
    protector.add_recovery("rec-1", "Revert to pre-migration snapshot snap-2026-10-17")
    packet = protector.export_packet()
    assert packet.id == "agent-session-42"

    # Compact to wire string
    wire = protector.compact()
    assert wire.startswith("L1")

    # Decompact
    restored = CompactionShield.decompact(wire)
    assert restored.id == "agent-session-42"
    assert restored.critical_hash == protector.critical_hash

    # Test candidate summary verification: LLM dropped the recovery path
    dropped_dict = restored.to_dict()
    dropped_dict["recovery"] = []
    verdict = protector.verify_candidate_summary(dropped_dict)
    assert verdict["is_safe"] is False
    assert verdict["classification"] == "UNSAFE_COLLAPSE"


# ============================================================================
# 6. CLI Integration
# ============================================================================


def test_compact_cli_workflow(tmp_path, corpus):
    from lycheetah.cli import compact_cli

    packet_file = tmp_path / "packet.json"
    packet_file.write_text(json.dumps(corpus[0]), encoding="utf-8")
    wire_file = tmp_path / "wire.txt"
    restored_file = tmp_path / "restored.json"

    # 1. encode
    compact_cli(["encode", str(packet_file), "-o", str(wire_file)])
    assert wire_file.exists()
    assert wire_file.read_text().startswith("L1")

    # 2. decode
    compact_cli(["decode", str(wire_file), "-o", str(restored_file)])
    assert restored_file.exists()
    restored_data = json.loads(restored_file.read_text())
    assert restored_data["id"] == corpus[0]["id"]
    assert critical_hash(restored_data) == critical_hash(corpus[0])

    # 3. check
    compact_cli(["check", str(packet_file)])

    # 4. verify
    compact_cli(["verify", str(packet_file), str(restored_file)])

    # 5. build-codebook
    corpus_jsonl = tmp_path / "corpus.jsonl"
    corpus_jsonl.write_text(
        "\n".join(json.dumps(p) for p in corpus[:10]), encoding="utf-8"
    )
    codebook_file = tmp_path / "codebook.json"
    compact_cli(
        ["build-codebook", str(corpus_jsonl), "--max-entries", "10", "-o", str(codebook_file)]
    )
    assert codebook_file.exists()
    cb = json.loads(codebook_file.read_text())
    assert len(cb["entries"]) <= 10
