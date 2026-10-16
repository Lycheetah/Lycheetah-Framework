import unittest
from run_probe import CANDIDATES, evaluate, PUBLIC_CASES, VALUE_CASES

class ProbeTests(unittest.TestCase):
    def test_reference_and_valid_alternative_pass_contract(self):
        for name in ("reference", "iterative_valid_alternative"):
            with self.subTest(name=name):
                self.assertTrue(evaluate(CANDIDATES[name][0], VALUE_CASES, include_errors=True)["accepted"])

    def test_public_suite_accepts_multiple_known_defects(self):
        accepted_defects = [
            name for name, (fn, is_valid) in CANDIDATES.items()
            if not is_valid and evaluate(fn, PUBLIC_CASES)["accepted"]
        ]
        self.assertGreaterEqual(len(accepted_defects), 3)

    def test_contract_suite_rejects_all_planted_defects(self):
        for name, (fn, is_valid) in CANDIDATES.items():
            if not is_valid:
                with self.subTest(name=name):
                    self.assertFalse(evaluate(fn, VALUE_CASES, include_errors=True)["accepted"])

    def test_contract_suite_does_not_reject_valid_alternative(self):
        self.assertTrue(evaluate(CANDIDATES["iterative_valid_alternative"][0], VALUE_CASES, include_errors=True)["accepted"])

    def test_probe_counts_match_actual_checks(self):
        for name, (fn, _label) in CANDIDATES.items():
            with self.subTest(name=name):
                self.assertEqual(evaluate(fn, VALUE_CASES, include_errors=True)["checks"], 19)
                self.assertEqual(evaluate(fn, PUBLIC_CASES)["checks"], 3)

if __name__ == "__main__":
    unittest.main()
