
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lamague_codec import (  # noqa: E402
    CodecError,
    build_codebook,
    canonical_json,
    classify,
    critical_hash,
    decode,
    encode,
    full_hash,
    safety_violations,
    validate_packet,
)


def load_packets():
    return [
        json.loads(line)
        for line in (ROOT / "corpus" / "packets.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class CodecTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packets = load_packets()
        split = json.loads((ROOT / "corpus" / "split.json").read_text(encoding="utf-8"))
        train_ids = set(split["training"])
        cls.train = [packet for packet in cls.packets if packet["id"] in train_ids]
        cls.codebook = build_codebook(cls.train, max_entries=20)

    def test_corpus_count(self):
        self.assertEqual(len(self.packets), 36)

    def test_split_count(self):
        self.assertEqual(len(self.train), 24)
        self.assertEqual(len(self.packets) - len(self.train), 12)

    def test_codebook_count(self):
        self.assertEqual(len(self.codebook["entries"]), 20)

    def test_all_reference_packets_are_safe(self):
        for packet in self.packets:
            self.assertEqual(safety_violations(packet), [])

    def test_plain_roundtrip_all(self):
        for packet in self.packets:
            self.assertEqual(canonical_json(decode(encode(packet))), canonical_json(packet))

    def test_dictionary_roundtrip_all(self):
        for packet in self.packets:
            source = encode(packet, self.codebook)
            decoded = decode(source, self.codebook)
            self.assertEqual(canonical_json(decoded), canonical_json(packet))

    def test_hashes_preserved(self):
        for packet in self.packets:
            decoded = decode(encode(packet, self.codebook), self.codebook)
            self.assertEqual(full_hash(decoded), full_hash(packet))
            self.assertEqual(critical_hash(decoded), critical_hash(packet))

    def test_dictionary_source_requires_codebook(self):
        with self.assertRaises(CodecError):
            decode(encode(self.packets[0], self.codebook))

    def test_invalid_prefix_rejected(self):
        with self.assertRaises(CodecError):
            decode("BAD{}")

    def test_missing_field_rejected(self):
        packet = copy.deepcopy(self.packets[0])
        del packet["purpose"]
        with self.assertRaises(CodecError):
            validate_packet(packet)

    def test_unknown_field_rejected(self):
        packet = copy.deepcopy(self.packets[0])
        packet["mystery"] = True
        with self.assertRaises(CodecError):
            validate_packet(packet)

    def test_invalid_operation_rejected(self):
        packet = copy.deepcopy(self.packets[0])
        packet["operations"].append("∇cas")
        with self.assertRaises(CodecError):
            validate_packet(packet)

    def test_out_of_range_dictionary_reference_rejected(self):
        source = encode(self.packets[0], self.codebook)
        body = json.loads(source[3:])
        body["p"] = 999999
        with self.assertRaises(CodecError):
            decode("L1D" + json.dumps(body, separators=(",", ":")), self.codebook)

    def test_exact_classification(self):
        result = classify(self.packets[0], copy.deepcopy(self.packets[0]))
        self.assertEqual(result["classification"], "EXACT_EQUIVALENT")

    def test_safe_extension_is_partial(self):
        candidate = copy.deepcopy(self.packets[0])
        candidate["evidence"].append(
            {"id": "extra", "text": "Additional evidence.", "provenance": "source://extra"}
        )
        result = classify(self.packets[0], candidate)
        self.assertEqual(result["classification"], "PARTIAL_EQUIVALENT")

    def test_unknown_loss_is_unsafe(self):
        candidate = copy.deepcopy(self.packets[0])
        candidate["unknowns"] = []
        result = classify(self.packets[0], candidate)
        self.assertEqual(result["classification"], "UNSAFE_COLLAPSE")

    def test_invariant_change_is_divergent(self):
        candidate = copy.deepcopy(self.packets[0])
        candidate["invariants"][0]["text"] += " Changed."
        result = classify(self.packets[0], candidate)
        self.assertEqual(result["classification"], "DIVERGENT")

    def test_guard_removal_is_unsafe(self):
        candidate = copy.deepcopy(self.packets[0])
        candidate["operations"] = [op for op in candidate["operations"] if op != "G"]
        result = classify(self.packets[0], candidate)
        self.assertEqual(result["classification"], "UNSAFE_COLLAPSE")

    def test_plain_codec_is_smaller_than_minified_json_for_all_packets(self):
        for packet in self.packets:
            self.assertLess(len(encode(packet).encode("utf-8")), len(canonical_json(packet).encode("utf-8")))


if __name__ == "__main__":
    unittest.main(verbosity=2)
