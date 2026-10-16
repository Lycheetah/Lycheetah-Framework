import json
import unittest
from pathlib import Path
from policy_contract_parity import (
    ROOT, VALIDATOR, STRICT_VALIDATOR, CASES, base_policy, parse_policy,
    strict_type_gate,
)

class TestPolicyContractParity(unittest.TestCase):
    def test_good_baseline_validates_and_parses(self):
        policy=base_policy()
        self.assertFalse(list(VALIDATOR.iter_errors(policy)))
        self.assertFalse(list(STRICT_VALIDATOR.iter_errors(policy)))
        self.assertTrue(parse_policy(policy))
        self.assertTrue(strict_type_gate(policy)[0])

    def test_wire_type_coercions_are_blocked_by_candidate(self):
        for name in ('rule_id_boolean','rule_pattern_boolean','rule_title_boolean','rule_description_integer','rule_status_basis_integer','rule_id_integer'):
            with self.subTest(case=name):
                policy=base_policy(); CASES[name](policy)
                self.assertTrue(strict_type_gate(policy)[0] is False)
                self.assertTrue(list(STRICT_VALIDATOR.iter_errors(policy)))

    def test_candidate_encodes_pattern_limit_and_active_basis(self):
        for name in ('rule_pattern_too_long','active_rule_missing_basis','active_rule_blank_basis'):
            with self.subTest(case=name):
                policy=base_policy(); CASES[name](policy)
                self.assertTrue(list(STRICT_VALIDATOR.iter_errors(policy)))
                self.assertFalse(strict_type_gate(policy)[0])

    def test_semantic_checks_remain_parser_responsibility(self):
        for name in ('duplicate_rule_ids','bad_regex'):
            with self.subTest(case=name):
                policy=base_policy(); CASES[name](policy)
                self.assertFalse(list(STRICT_VALIDATOR.iter_errors(policy)))
                self.assertFalse(strict_type_gate(policy)[0])

    def test_candidate_results_are_machine_readable_and_complete(self):
        data=json.loads((ROOT/'results.json').read_text())
        self.assertEqual(data['count'],20)
        self.assertEqual(len(data['results']),20)
        self.assertEqual(data['candidate_contract_parity_cases'],17)

if __name__=='__main__': unittest.main(verbosity=2)
