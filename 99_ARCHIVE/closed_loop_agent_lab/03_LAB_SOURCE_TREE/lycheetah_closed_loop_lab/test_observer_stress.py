import unittest
from observer_stress import evaluate, generate_grid

class ObserverStressTests(unittest.TestCase):
    def test_perfect_sensor_no_unknowns_accepts_only_valid_tasks(self):
        r = evaluate(0.2, 1.0, 1.0, unknown_valid=0.0, unknown_invalid=0.0, n=1000)
        self.assertEqual(r["candidate"]["invalid_auto_accept_expected"], 0)
        self.assertEqual(r["candidate"]["valid_auto_accept_expected"], 800)
        self.assertEqual(r["candidate"]["valid_block_expected"], 0)
        self.assertEqual(r["candidate"]["total_review_expected"], 0)

    def test_useless_sensor_reproduces_baseline_auto_accepts(self):
        r = evaluate(0.2, 0.0, 1.0, unknown_valid=0.0, unknown_invalid=0.0, n=1000)
        self.assertEqual(r["candidate"]["invalid_auto_accept_expected"], 200)
        self.assertEqual(r["baseline"]["invalid_auto_accept_expected"], 200)

    def test_false_alarm_cost_appears_in_valid_block_metric(self):
        r = evaluate(0.2, 0.8, 0.8, unknown_valid=0.1, unknown_invalid=0.1, n=1000)
        self.assertAlmostEqual(r["candidate"]["valid_block_expected"], 80)
        self.assertAlmostEqual(r["candidate"]["valid_review_expected"], 80)

    def test_invalid_probability_combinations_rejected(self):
        with self.assertRaises(ValueError):
            evaluate(0.2, 0.99, 0.02, unknown_valid=0.02, unknown_invalid=0.02)
        with self.assertRaises(ValueError):
            evaluate(0.2, 0.5, 0.99, unknown_valid=0.02, unknown_invalid=0.02)

    def test_grid_is_complete_and_expected_counts_conserve_mass(self):
        grid = generate_grid()
        self.assertEqual(len(grid), 3 * 6 * 4)
        for r in grid:
            self.assertAlmostEqual(
                r["candidate"]["invalid_auto_accept_expected"] +
                r["candidate"]["invalid_block_expected"] +
                r["candidate"]["invalid_review_expected"],
                r["ground_truth_invalid_expected"],
            )
            self.assertAlmostEqual(
                r["candidate"]["valid_auto_accept_expected"] +
                r["candidate"]["valid_block_expected"] +
                r["candidate"]["valid_review_expected"],
                r["ground_truth_valid_expected"],
            )

if __name__ == "__main__":
    unittest.main(verbosity=2)
