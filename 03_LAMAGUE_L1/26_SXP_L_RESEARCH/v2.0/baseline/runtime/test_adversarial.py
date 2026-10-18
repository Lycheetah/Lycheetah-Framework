import unittest
from adversarial_eval import run

class BenchmarkFixtureTests(unittest.TestCase):
    def test_all_hand_labeled_reference_cases(self):
        summary, rows=run()
        self.assertEqual(summary['cases'],28)
        self.assertEqual(summary['gate_correct'],28)
        self.assertEqual(summary['gate_false_allow'],0)
        self.assertEqual(summary['gate_false_deny'],0)
    def test_toy_keyword_has_both_error_types(self):
        summary,_=run()
        self.assertGreater(summary['keyword_false_allow'],0)
        self.assertGreater(summary['keyword_false_deny'],0)

if __name__=='__main__':unittest.main()
