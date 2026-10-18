"""Four real-Framework tests; intentionally fail at import if checkout is unavailable."""
import tempfile
from pathlib import Path
import unittest
from framework_bridge_candidate import run_simulated_refund

class RealFrameworkBridgeCandidate(unittest.TestCase):
    def _run(self,**kwargs):
        with tempfile.TemporaryDirectory() as tmp:
            return run_simulated_refund(Path(tmp),**kwargs)
    def test_legitimate_receipt_and_observation(self):
        self.assertEqual(self._run()['result'],'CONFIRMED')
    def test_stale_evidence_before_finality(self):
        v=self._run(stale_before_finality=True)
        self.assertEqual(v['result'],'REVIEW')
        self.assertEqual(v['guard_status'],'PREPARED')
    def test_changed_provider_condition_after_guard_dispatch(self):
        v=self._run(stale_after_dispatch=True)
        self.assertEqual(v['result'],'REVIEW')
        self.assertEqual(v['guard_status'],'FAILED')
    def test_signed_own_record_disagrees_with_lab_oracle(self):
        self.assertEqual(self._run(false_world_fact=True)['result'],'CONFLICT')
