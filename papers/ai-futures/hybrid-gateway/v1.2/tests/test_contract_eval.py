import unittest
from run_contract_eval import evaluate

class ContractEvaluationTests(unittest.TestCase):
    def test_all_cases_are_accounted_for(self):
        report = evaluate()
        names = [r['case'] for r in report['cases']]
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(report['total_cases'], 33)
        self.assertEqual(sum(r['expected_operator_authorized'] for r in report['cases']), 9)

    def test_reference_contract_matches_all_author_defined_labels(self):
        report = evaluate()
        self.assertTrue(all(r['expected_operator_authorized'] == r['contracted_v0_4']
                            for r in report['cases']))
        self.assertGreater(report['metrics']['lexical_baseline']['false_positive'], 0)
        self.assertGreater(report['metrics']['narrow_regex_baseline']['false_positive'], 0)
        self.assertGreater(report['metrics']['narrow_regex_baseline']['false_negative'], 0)

if __name__ == '__main__':
    unittest.main()
