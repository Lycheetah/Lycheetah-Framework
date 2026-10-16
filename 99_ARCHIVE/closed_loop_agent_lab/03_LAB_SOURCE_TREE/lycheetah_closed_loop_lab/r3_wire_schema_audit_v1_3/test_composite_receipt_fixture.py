import unittest
from composite_receipt_fixture import (
    WireError,
    baseline_parse_and_verify,
    finalize_receipt,
    mutate,
    strict_parse_and_verify,
    valid_receipt_body,
)

CASES = [
    "schema_version_number",
    "control_title_boolean",
    "finding_title_boolean",
    "confidence_boolean",
    "evidence_integer",
]

class TestCompositeReceiptWireMutation(unittest.TestCase):
    def test_well_typed_receipt_verifies(self):
        payload = finalize_receipt(valid_receipt_body())
        normalized, valid = baseline_parse_and_verify(payload)
        self.assertTrue(valid)
        self.assertEqual(normalized, valid_receipt_body())

    def test_mutations_normalize_to_same_digest_but_strict_parser_rejects(self):
        original = finalize_receipt(valid_receipt_body())
        expected, original_valid = baseline_parse_and_verify(original)
        self.assertTrue(original_valid)
        for case in CASES:
            with self.subTest(case=case):
                mutated = mutate(original, case)
                baseline_normalized, baseline_valid = baseline_parse_and_verify(mutated)
                self.assertTrue(baseline_valid, case)
                self.assertEqual(baseline_normalized, expected, case)
                with self.assertRaises(WireError):
                    strict_parse_and_verify(mutated)

if __name__ == "__main__":
    unittest.main()
