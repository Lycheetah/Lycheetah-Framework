import unittest
from harness import Decision, evaluate, scenarios, run

class HarnessTests(unittest.TestCase):
    def setUp(self):
        self.cases = {s.id: s for s in scenarios()}

    def test_clean_patch_is_accepted_by_both(self):
        r = evaluate(self.cases["S01_clean_patch"])
        self.assertEqual(r.baseline, Decision.ACCEPT.value)
        self.assertEqual(r.closed_loop, Decision.ACCEPT.value)

    def test_task_noop_green_tests_is_caught_by_candidate(self):
        r = evaluate(self.cases["S03_green_no_effect"])
        self.assertEqual(r.baseline, Decision.ACCEPT.value)
        self.assertEqual(r.closed_loop, Decision.BLOCK.value)

    def test_shared_conventional_gates_are_preserved(self):
        for case_id in ("S07_stale_test_evidence", "S08_workspace_escape", "S09_revoked_approval", "S10_runner_unavailable"):
            with self.subTest(case_id=case_id):
                r = evaluate(self.cases[case_id])
                self.assertEqual(r.baseline, Decision.BLOCK.value)
                self.assertEqual(r.closed_loop, Decision.BLOCK.value)

    def test_false_sensor_is_not_magically_fixed(self):
        r = evaluate(self.cases["S05_unseen_semantic_regression"])
        self.assertEqual(r.baseline, Decision.ACCEPT.value)
        self.assertEqual(r.closed_loop, Decision.ACCEPT.value)

    def test_ambiguous_or_out_of_contract_work_goes_to_review(self):
        for case_id in ("S06_valid_multi_file", "S12_unmachineable_goal"):
            with self.subTest(case_id=case_id):
                self.assertEqual(evaluate(self.cases[case_id]).closed_loop, Decision.REVIEW.value)

    def test_complete_contract_allows_valid_multi_file_change(self):
        r = evaluate(self.cases["S13_valid_multi_file_declared"])
        self.assertEqual(r.baseline, Decision.ACCEPT.value)
        self.assertEqual(r.closed_loop, Decision.ACCEPT.value)

    def test_false_alarm_can_block_valid_work(self):
        r = evaluate(self.cases["S14_sensor_false_alarm"])
        self.assertEqual(r.ground_truth, "valid")
        self.assertEqual(r.closed_loop, Decision.BLOCK.value)

    def test_metrics_show_both_gain_and_cost(self):
        report = run()
        self.assertLess(report["candidate"]["invalid_cases_auto_accepted"], report["baseline"]["invalid_cases_auto_accepted"])
        self.assertGreater(report["candidate"]["valid_cases_sent_to_review"], 0)
        self.assertIn("S05_unseen_semantic_regression", report["candidate"]["all_invalid_auto_accept_ids"])

if __name__ == "__main__":
    unittest.main(verbosity=2)
