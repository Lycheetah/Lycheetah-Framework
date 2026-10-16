"""Small tests for demonstrated wire-type normalization behavior."""
import unittest
from source_equivalent_wire_fixture import (
    WireError,
    baseline_control_reference,
    baseline_finding,
    baseline_receipt_parse,
    canonical_sha256,
    strict_control_reference,
    strict_finding,
    strict_receipt_parse,
)


class TestWireTypeNormalization(unittest.TestCase):
    def test_numeric_receipt_schema_version_normalizes_to_same_digest_checked_body(self):
        body = {
            "schema_version": "0.1",
            "receipt_id": "urn:uuid:fixture",
            "issued_at": "2026-10-16T00:00:00Z",
            "runtime": {"name": "fixture"},
        }
        payload = {**body, "integrity": {"digest": canonical_sha256(body)}}
        payload["schema_version"] = 0.1
        parsed = baseline_receipt_parse(payload)
        self.assertEqual(parsed["schema_version"], "0.1")
        with self.assertRaisesRegex(WireError, "schema_version must be a string"):
            strict_receipt_parse(payload)

    def test_boolean_control_title_normalizes_to_same_string(self):
        payload = {"framework": "F", "control_id": "X-1", "title": "False"}
        mutated = {**payload, "title": False}
        self.assertEqual(baseline_control_reference(payload), baseline_control_reference(mutated))
        with self.assertRaisesRegex(WireError, "title must be a string"):
            strict_control_reference(mutated)

    def test_boolean_confidence_and_typed_evidence_normalize_to_valid_values(self):
        payload = {
            "id": "TEST:FINDING:001", "title": "False", "description": "d",
            "evaluator": "e", "confidence": 1.0, "evidence": ["17"],
        }
        mutated = {**payload, "title": False, "confidence": True, "evidence": [17]}
        baseline = baseline_finding(mutated)
        self.assertEqual(baseline, baseline_finding(payload))
        with self.assertRaises(WireError):
            strict_finding(mutated)

    def test_confidence_string_is_not_numeric_contract(self):
        payload = {
            "id": "TEST:FINDING:001", "title": "t", "description": "d",
            "evaluator": "e", "confidence": "0.5", "evidence": [],
        }
        self.assertEqual(baseline_finding(payload)["confidence"], 0.5)
        with self.assertRaisesRegex(WireError, "confidence must be a finite number"):
            strict_finding(payload)

    def test_valid_wire_records_remain_accepted(self):
        receipt_body = {
            "schema_version": "0.1", "receipt_id": "id", "issued_at": "time",
            "runtime": {"name": "fixture"},
        }
        receipt_payload = {**receipt_body, "integrity": {"digest": canonical_sha256(receipt_body)}}
        self.assertEqual(strict_receipt_parse(receipt_payload), receipt_body)
        control = {"framework": "F", "control_id": "X-1", "title": "A"}
        self.assertEqual(strict_control_reference(control), {**control, "url": ""})
        finding = {"id": "TEST:FINDING:001", "title": "t", "description": "d", "evaluator": "e", "confidence": 0.5, "evidence": ["ok"]}
        self.assertEqual(strict_finding(finding)["confidence"], 0.5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
