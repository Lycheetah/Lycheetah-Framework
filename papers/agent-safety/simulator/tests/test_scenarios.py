import unittest

from safety_sim.scenarios import run_experiments


class ScriptedExperimentTests(unittest.TestCase):
    def test_matched_baselines_and_expected_counterexamples(self):
        report = run_experiments()
        self.assertEqual(report["cases_per_arm"], 19)
        self.assertTrue(report["all_expected_outcomes_met"])
        self.assertTrue(report["matched_outcomes_equivalent"])
        for arm, rows in report["arms"].items():
            for row in rows:
                with self.subTest(arm=arm, case=row["case"]):
                    self.assertTrue(row["met_expected_outcome"], row)
            limits = {row["case"]: row for row in rows if row["counterexample"]}
            self.assertEqual(limits["inflight-after-revoke"]["observation"]["effect_count"], 1)
            self.assertEqual(limits["permitted-harm"]["observation"]["simulated_harm_markers"], 1)
            uncertain = next(row for row in rows if row["case"] == "receipt-absent")
            self.assertEqual(uncertain["observation"]["reserved"], 1)


if __name__ == "__main__":
    unittest.main()
