"""Needs the actual repo checkout. DO NOT fake these imports."""
import tempfile
from pathlib import Path
import unittest
from real_framework_bridge_candidate import run_real_framework_path

class IntegrationAgainstRealFramework(unittest.TestCase):
    def run_case(self,**opts):
        with tempfile.TemporaryDirectory() as td:
            return run_real_framework_path(Path(td),**opts)
    def test_normal_two_origins(self):
        v=self.run_case();self.assertEqual(v['decision'],'CONFIRMED');self.assertEqual(v['guard_status'],'SUCCEEDED')
    def test_common_origin_with_two_signers(self):
        self.assertEqual(self.run_case(common_origin=True)['decision'],'REVIEW')
    def test_stale_evidence_aborts_before_dispatch(self):
        v=self.run_case(stale_before_finality=True);self.assertEqual(v['decision'],'REVIEW');self.assertEqual(v['guard_status'],'PREPARED')
    def test_even_distinct_origins_cannot_validate_ground_truth(self):
        v=self.run_case(wrong_world_fact=True);self.assertEqual(v['decision'],'CONFIRMED');self.assertFalse(v['ground_truth_correct'])
