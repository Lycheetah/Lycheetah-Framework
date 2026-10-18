import unittest
from run_scenarios import generate

class MatchedControls(unittest.TestCase):
    def test_matched_conventional_same_scenarios(self):
        p=generate()
        self.assertEqual(p['totals']['matched_control_disagreements'],0)
    def test_naive_quorum_overconfirms(self):
        p=generate()['totals']
        self.assertGreater(p['naive_confirmed'],p['provenance_confirmed'])
    def test_deliberately_false_independent_consensus_still_confirmed(self):
        p=generate()['cases']
        x=next(x for x in p if x['name']=='two-sources-agree-on-false-evidence')
        self.assertFalse(x['ground_truth_correct'])
        self.assertEqual(x['provenance_gate'],'CONFIRMED')
    def test_disagreement_is_not_automatic_block(self):
        p=generate()['cases']
        x=next(x for x in p if x['name']=='recorded-negative-evidence')
        self.assertEqual(x['provenance_gate'],'CONFLICT')

if __name__=='__main__':unittest.main()
