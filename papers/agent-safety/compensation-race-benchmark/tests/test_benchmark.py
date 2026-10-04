import tempfile
import unittest
from pathlib import Path

from compensation_race.benchmark import ResourceStore, run_case, run_stress


class CompensationRaceTests(unittest.TestCase):
    def test_precheck_race_overwrites_legitimate_update(self):
        r = run_case("weak_precheck_race")
        self.assertTrue(r["precheck_passed"])
        self.assertTrue(r["repair_reported_success"])
        self.assertTrue(r["overwrote_legitimate_update"])

    def test_sequential_cas_can_leave_partial_repair(self):
        r = run_case("sequential_partial")
        self.assertFalse(r["repair_reported_success"])
        self.assertEqual(r["repaired_before_failure"], ["A"])
        self.assertTrue(r["partial_repair"])

    def test_atomic_commit_fence_refuses_stale_set_without_writes(self):
        r = run_case("atomic_stale_refusal")
        self.assertFalse(r["repair_committed"])
        self.assertTrue(r["writes_zero"])

    def test_atomic_commit_fence_repairs_clean_set(self):
        r = run_case("atomic_clean")
        self.assertTrue(r["repair_committed"])
        self.assertTrue(r["both_restored"])

    def test_stress(self):
        r = run_stress(25)
        self.assertEqual(r["weak_precheck_overwrites"], 25)
        self.assertEqual(r["sequential_partial_repairs"], 25)
        self.assertEqual(r["atomic_stale_refusals"], 25)
        self.assertEqual(r["atomic_partial_repairs"], 0)
        self.assertEqual(r["atomic_clean_successes"], 25)


if __name__ == "__main__":
    unittest.main()
