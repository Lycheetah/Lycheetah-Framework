import unittest
from baseline_fixture import TextRule as LegacyRule
from policy_parser_candidate import TextRule as CandidateRule, PolicyError as CandidatePolicyError

BASE = {"id": "customer.rule-01", "pattern": r"\bhello\b"}
BAD_VALUES = [None, True, 17, 3.5, ["ordinary"], {"ordinary": "value"}]
FIELDS = ("id", "pattern", "title", "description")

class PolicyParserContractTests(unittest.TestCase):
    def test_candidate_rejects_wrong_types_for_all_text_fields(self):
        for field in FIELDS:
            for value in BAD_VALUES:
                with self.subTest(field=field, value=repr(value)):
                    data = dict(BASE)
                    data[field] = value
                    with self.assertRaises(CandidatePolicyError):
                        CandidateRule.from_dict(data)

    def test_baseline_coerces_numeric_id_and_pattern(self):
        id_rule = LegacyRule.from_dict({"id": 123, "pattern": "x"})
        pattern_rule = LegacyRule.from_dict({"id": "test.rule", "pattern": 123})
        self.assertEqual(id_rule.rule_id, "123")
        self.assertEqual(pattern_rule.pattern, "123")

    def test_baseline_coerces_non_string_title_and_description(self):
        rule = LegacyRule.from_dict({"id": "test.rule", "pattern": "x", "title": False, "description": ["oops"]})
        self.assertEqual(rule.title, "False")
        self.assertEqual(rule.description, "['oops']")

    def test_candidate_preserves_valid_strings(self):
        source = {"id": "test.rule", "pattern": r"\bhello\b", "title": "Hello", "description": "Test rule"}
        rule = CandidateRule.from_dict(source)
        self.assertEqual((rule.rule_id, rule.pattern, rule.title, rule.description), ("test.rule", r"\bhello\b", "Hello", "Test rule"))

    def test_candidate_preserves_defaults(self):
        rule = CandidateRule.from_dict({"id": "test.rule", "pattern": "x"})
        self.assertEqual(rule.title, "test.rule")
        self.assertEqual(rule.description, "Policy text rule matched")

    def test_candidate_rejects_missing_required_fields(self):
        for source in ({"id": "test.rule"}, {"pattern": "x"}):
            with self.subTest(source=source), self.assertRaises(CandidatePolicyError):
                CandidateRule.from_dict(source)

    def test_candidate_rejects_unknown_fields(self):
        with self.assertRaises(CandidatePolicyError):
            CandidateRule.from_dict({**BASE, "typo": "unexpected"})

if __name__ == "__main__":
    unittest.main(verbosity=2)
