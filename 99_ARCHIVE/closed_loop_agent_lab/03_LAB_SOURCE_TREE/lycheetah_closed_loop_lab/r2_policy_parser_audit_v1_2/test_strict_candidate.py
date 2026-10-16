"""Tests for strict TextRule parsing; uses only Python's standard library."""
from __future__ import annotations

import unittest

from source_equivalent_baseline import PolicyError as BaselinePolicyError, TextRule as BaselineRule
from strict_candidate import PolicyError, TextRule

BASE = {"id": "customer.rule-01", "pattern": r"\bhello\b"}
BAD_VALUES = [None, True, 17, 3.5, ["x"], {"x": "y"}]
JSON_FIELDS = ("id", "pattern", "title", "description", "status_basis")


class TestStrictCandidate(unittest.TestCase):
    def test_all_json_string_fields_reject_wrong_types(self):
        for field in JSON_FIELDS:
            for bad in BAD_VALUES:
                with self.subTest(field=field, value=bad):
                    payload = dict(BASE)
                    payload[field] = bad
                    with self.assertRaises(PolicyError):
                        TextRule.from_dict(payload)

    def test_direct_constructor_rejects_wrong_types_for_all_text_fields(self):
        base = {
            "rule_id": BASE["id"],
            "pattern": BASE["pattern"],
            "title": "title",
            "description": "description",
            "status_basis": "",
        }
        for field in ("rule_id", "pattern", "title", "description", "status_basis"):
            for bad in BAD_VALUES:
                with self.subTest(field=field, value=bad):
                    payload = dict(base)
                    payload[field] = bad
                    with self.assertRaises(PolicyError):
                        TextRule(**payload)

    def test_valid_explicit_strings_round_trip(self):
        payload = {
            **BASE,
            "title": "Human-readable title",
            "description": "Valid description.",
            "status_basis": "Approved policy PR-17.",
        }
        rule = TextRule.from_dict(payload)
        self.assertEqual(rule.rule_id, payload["id"])
        self.assertEqual(rule.pattern, payload["pattern"])
        self.assertEqual(rule.title, payload["title"])
        self.assertEqual(rule.description, payload["description"])
        self.assertEqual(rule.status_basis, payload["status_basis"])

    def test_existing_missing_optional_defaults_are_preserved(self):
        rule = TextRule.from_dict(dict(BASE))
        self.assertEqual(rule.title, BASE["id"])
        self.assertEqual(rule.description, "Policy text rule matched")
        self.assertEqual(rule.status_basis, "")

    def test_source_equivalent_fixture_exposes_status_basis_coercion(self):
        self.assertEqual(BaselineRule.from_dict({**BASE, "status_basis": 22}).status_basis, "22")
        with self.assertRaises(PolicyError):
            TextRule.from_dict({**BASE, "status_basis": 22})

    def test_baseline_is_not_accidentally_used_as_candidate(self):
        # A sentinel documenting that the source-equivalent fixture deliberately
        # exhibits the behavior this candidate changes.
        self.assertEqual(BaselineRule.from_dict({**BASE, "title": False}).title, "False")
        with self.assertRaises(PolicyError):
            TextRule.from_dict({**BASE, "title": False})


if __name__ == "__main__":
    unittest.main(verbosity=2)
