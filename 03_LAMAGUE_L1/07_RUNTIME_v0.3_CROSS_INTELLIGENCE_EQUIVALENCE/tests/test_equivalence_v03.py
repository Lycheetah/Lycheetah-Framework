from __future__ import annotations

import json
import unittest
from pathlib import Path
import tempfile

from lamague_runtime import (
    ChallengeCase,
    ChallengePack,
    ConsensusStatus,
    CrossIntelligenceConsensus,
    CrossIntelligenceEquivalenceHarness,
    DecoderPacket,
    EquivalenceClass,
    PacketValidationError,
    extract_json_object,
    validate_text,
)


def base_packet(**overrides):
    data = dict(
        case_id="T01",
        decoder_id="REFERENCE",
        purpose="preserve accountable meaning",
        claim="the result is context-limited",
        operation_path=["O", "E", "U", "P", "Y"],
        invariants=["uncertainty remains visible", "lineage remains recoverable"],
        unknowns=["method reliability"],
        authority=["human authorises publication"],
        participants=["human", "AI"],
        affected_parties=["future reader"],
        evidence=["trace"],
        provenance=["source"],
        dissent=[],
        value_ledger=[],
        consequences=["limited result published"],
        consequence_horizon="immediate",
        recovery=["revise later"],
    )
    data.update(overrides)
    return DecoderPacket(**data)


class DecoderPacketTests(unittest.TestCase):
    def test_hash_ignores_decoder_identity(self):
        a = base_packet(decoder_id="A")
        b = base_packet(decoder_id="B")
        self.assertEqual(a.semantic_hash(), b.semantic_hash())

    def test_hash_normalizes_case_and_whitespace(self):
        a = base_packet(purpose="Preserve accountable meaning")
        b = base_packet(purpose="  preserve   accountable meaning ")
        self.assertEqual(a.semantic_hash(), b.semantic_hash())

    def test_hash_changes_when_unknown_lost(self):
        a = base_packet()
        b = base_packet(unknowns=[])
        self.assertNotEqual(a.semantic_hash(), b.semantic_hash())

    def test_critical_hash_ignores_evidence_surface(self):
        a = base_packet(evidence=["trace"])
        b = base_packet(evidence=["trace", "replication"])
        self.assertEqual(a.critical_hash(), b.critical_hash())

    def test_from_dict_requires_core_fields(self):
        with self.assertRaises(ValueError):
            DecoderPacket.from_dict({"case_id": "x"})


class EquivalenceTests(unittest.TestCase):
    def setUp(self):
        self.h = CrossIntelligenceEquivalenceHarness()
        self.ref = base_packet()

    def test_exact_equivalent(self):
        cand = base_packet(decoder_id="CAND")
        report = self.h.compare(self.ref, cand)
        self.assertEqual(report.classification, EquivalenceClass.EXACT_EQUIVALENT)

    def test_invariant_equivalent_when_only_evidence_expands(self):
        cand = base_packet(
            decoder_id="CAND",
            evidence=["trace", "replication"],
        )
        report = self.h.compare(self.ref, cand)
        self.assertEqual(report.classification, EquivalenceClass.INVARIANT_EQUIVALENT)

    def test_partial_when_unknowns_expand_safely(self):
        cand = base_packet(
            decoder_id="CAND",
            unknowns=["method reliability", "human learnability"],
        )
        report = self.h.compare(self.ref, cand)
        self.assertEqual(report.classification, EquivalenceClass.PARTIAL_EQUIVALENT)

    def test_unknown_loss_is_unsafe_collapse(self):
        cand = base_packet(decoder_id="CAND", unknowns=[])
        report = self.h.compare(self.ref, cand)
        self.assertEqual(report.classification, EquivalenceClass.UNSAFE_COLLAPSE)
        self.assertIn("unknowns", report.unsafe_losses)

    def test_authority_loss_is_unsafe_collapse(self):
        cand = base_packet(decoder_id="CAND", authority=[])
        report = self.h.compare(self.ref, cand)
        self.assertEqual(report.classification, EquivalenceClass.UNSAFE_COLLAPSE)

    def test_participant_loss_is_unsafe_collapse(self):
        cand = base_packet(decoder_id="CAND", participants=["human"])
        report = self.h.compare(self.ref, cand)
        self.assertEqual(report.classification, EquivalenceClass.UNSAFE_COLLAPSE)

    def test_affected_party_loss_is_unsafe_collapse(self):
        cand = base_packet(decoder_id="CAND", affected_parties=[])
        report = self.h.compare(self.ref, cand)
        self.assertEqual(report.classification, EquivalenceClass.UNSAFE_COLLAPSE)

    def test_purpose_change_is_divergent(self):
        cand = base_packet(decoder_id="CAND", purpose="replace accountable meaning")
        report = self.h.compare(self.ref, cand)
        self.assertEqual(report.classification, EquivalenceClass.DIVERGENT)

    def test_invariant_loss_is_divergent(self):
        cand = base_packet(
            decoder_id="CAND",
            invariants=["lineage remains recoverable"],
        )
        report = self.h.compare(self.ref, cand)
        self.assertEqual(report.classification, EquivalenceClass.DIVERGENT)

    def test_operation_path_can_differ_without_critical_loss(self):
        cand = base_packet(decoder_id="CAND", operation_path=["O", "U", "P", "Y"])
        report = self.h.compare(self.ref, cand)
        self.assertEqual(report.classification, EquivalenceClass.INVARIANT_EQUIVALENT)

    def test_dissent_erasure_is_unsafe(self):
        dissent = [{
            "parties": ["human", "AI"],
            "positions": {"human": "publish", "AI": "test"},
            "status": "UNRESOLVED",
        }]
        ref = base_packet(dissent=dissent)
        cand = base_packet(decoder_id="CAND", dissent=[])
        report = self.h.compare(ref, cand)
        self.assertEqual(report.classification, EquivalenceClass.UNSAFE_COLLAPSE)

    def test_value_flow_erasure_is_unsafe(self):
        value = [{
            "source": "human",
            "recipient": "AI",
            "kind": "artifact",
            "declared": True,
            "consent": "analysis only",
            "reversible": True,
        }]
        ref = base_packet(value_ledger=value)
        cand = base_packet(decoder_id="CAND", value_ledger=[])
        report = self.h.compare(ref, cand)
        self.assertEqual(report.classification, EquivalenceClass.UNSAFE_COLLAPSE)


class ConsensusTests(unittest.TestCase):
    def setUp(self):
        self.c = CrossIntelligenceConsensus()
        self.ref = base_packet()

    def test_safe_consensus(self):
        candidates = [
            base_packet(decoder_id="A"),
            base_packet(decoder_id="B"),
        ]
        report = self.c.evaluate(self.ref, candidates)
        self.assertEqual(report.status, ConsensusStatus.SAFE_CONSENSUS)

    def test_safe_majority_with_dissent(self):
        candidates = [
            base_packet(decoder_id="A"),
            base_packet(decoder_id="B", evidence=["trace", "replication"]),
            base_packet(decoder_id="C", unknowns=[]),
        ]
        report = self.c.evaluate(self.ref, candidates)
        self.assertEqual(report.status, ConsensusStatus.SAFE_MAJORITY_WITH_DISSENT)
        self.assertEqual(report.unsafe_decoders, ["C"])

    def test_split(self):
        candidates = [
            base_packet(decoder_id="A"),
            base_packet(decoder_id="B", unknowns=[]),
        ]
        report = self.c.evaluate(self.ref, candidates)
        self.assertEqual(report.status, ConsensusStatus.SPLIT)

    def test_no_safe_consensus(self):
        candidates = [
            base_packet(decoder_id="A", unknowns=[]),
            base_packet(decoder_id="B", purpose="different"),
        ]
        report = self.c.evaluate(self.ref, candidates)
        self.assertEqual(report.status, ConsensusStatus.NO_SAFE_CONSENSUS)

    def test_clusters_include_reference(self):
        candidates = [base_packet(decoder_id="A")]
        report = self.c.evaluate(self.ref, candidates)
        self.assertEqual(report.clusters[0].decoder_ids, ["A", "REFERENCE"])


class PacketValidationTests(unittest.TestCase):
    def test_extract_plain_json(self):
        data = extract_json_object(json.dumps(base_packet().to_dict()))
        self.assertEqual(data["case_id"], "T01")

    def test_extract_fenced_json(self):
        text = "```json\n" + json.dumps(base_packet().to_dict()) + "\n```"
        packet = validate_text(text)
        self.assertEqual(packet.case_id, "T01")

    def test_invalid_json_rejected(self):
        with self.assertRaises(PacketValidationError):
            validate_text("not-json")


class ChallengePackTests(unittest.TestCase):
    def test_round_trip(self):
        case = ChallengeCase(
            case_id="T01",
            title="test",
            source_expression="O -> Y",
            source_text="observe and yield",
            instructions="decode",
            reference_packet=base_packet(),
        )
        with tempfile.TemporaryDirectory() as td:
            pack = ChallengePack([case])
            path = pack.write(td)
            loaded = ChallengePack.load(path)
            self.assertEqual(loaded.cases[0].case_id, "T01")
            self.assertEqual(
                loaded.cases[0].reference_packet.semantic_hash(),
                case.reference_packet.semantic_hash(),
            )


if __name__ == "__main__":
    unittest.main()
