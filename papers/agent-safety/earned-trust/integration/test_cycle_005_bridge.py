"""Native bridge tests check the decision boundary as well as the label."""
from pathlib import Path
import tempfile
import unittest

from cycle_005_bridge import run_real_framework_path


class CorrectedCycle005(unittest.TestCase):
    def run_case(self, **options):
        with tempfile.TemporaryDirectory() as home:
            return run_real_framework_path(Path(home), **options)

    def test_distinct_sources_reach_provenance_confirmation(self):
        result = self.run_case()
        self.assertEqual(result["boundary"], "provenance")
        self.assertEqual(result["decision"], "CONFIRMED")
        self.assertEqual(result["guard_status"], "SUCCEEDED")
        self.assertTrue(result["provider_proof_ok"])

    def test_common_origin_refused_at_provenance_not_an_earlier_error(self):
        result = self.run_case(common_origin=True)
        self.assertEqual(result["boundary"], "provenance")
        self.assertEqual(result["decision"], "REVIEW")
        self.assertEqual(result["guard_status"], "SUCCEEDED")
        self.assertTrue(result["provider_proof_ok"])

    def test_stale_evidence_refused_before_dispatch(self):
        result = self.run_case(stale_before_finality=True)
        self.assertEqual(result["boundary"], "finality")
        self.assertEqual(result["decision"], "REVIEW")
        self.assertEqual(result["guard_status"], "PREPARED")

    def test_authenticated_independent_sources_can_confirm_a_false_fact(self):
        result = self.run_case(wrong_world_fact=True)
        self.assertEqual(result["boundary"], "provenance")
        self.assertEqual(result["decision"], "CONFIRMED")
        self.assertFalse(result["ground_truth_correct"])

    def test_wrong_provider_approval_still_refused(self):
        result = self.run_case(provider_approval_id="a1")
        self.assertEqual(result["boundary"], "provider")
        self.assertEqual(result["reason"], "GRANT_MISMATCH")
        self.assertEqual(result["decision"], "REVIEW")


if __name__ == "__main__":
    unittest.main()
