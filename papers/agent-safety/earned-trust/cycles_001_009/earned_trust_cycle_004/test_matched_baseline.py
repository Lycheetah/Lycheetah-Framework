"""Check that matched conventional checks perform equivalently on labelled lab matrix."""
import unittest
from run_scenarios import case

class MatchedControls(unittest.TestCase):
    def test_legitimate(self):
        r=case('legitimate'); self.assertEqual(r['two_record'],r['conventional_matched'])
    def test_false_provider_claim(self):
        r=case('false',actual_truth=False,observer_correctness='FALSE')
        self.assertEqual(r['two_record'],r['conventional_matched'])
    def test_correlated_false_evidence(self):
        r=case('correlated',actual_truth=False,observer_correctness='TRUE')
        self.assertEqual(r['two_record'],r['conventional_matched'])
    def test_observer_missing(self):
        r=case('missing',missing_observer=True)
        self.assertEqual(r['two_record'],r['conventional_matched'])
    def test_outdated_observation(self):
        r=case('stale',stale_observer=True)
        self.assertEqual(r['two_record'],r['conventional_matched'])
    def test_cross_source_mismatch(self):
        r=case('wrong',wrong_observer_action=True)
        self.assertEqual(r['two_record'],r['conventional_matched'])
    def test_corrupt_record(self):
        r=case('broken',corrupted_provider=True)
        self.assertEqual(r['two_record'],r['conventional_matched'])
    def test_missing_provider(self):
        r=case('not-committed',missing_provider=True)
        self.assertEqual(r['two_record'],r['conventional_matched'])

if __name__=='__main__':unittest.main()
