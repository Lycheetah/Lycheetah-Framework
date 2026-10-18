import unittest
from collections import Counter
from run_scenarios import main

class ComparisonTests(unittest.TestCase):
    def setUp(self):
        self.rows=main()

    def test_all_twenty_cases_agree_with_matched_conventional_rules(self):
        self.assertEqual(len(self.rows),20)
        self.assertTrue(all(r['governed']==r['conventional_matched'] for r in self.rows))

    def test_naive_baseline_difference_is_disclosed(self):
        self.assertEqual(Counter(r['naive_signed_quorum'] for r in self.rows),
                         Counter({'CONFIRMED':13,'REVIEW':6,'CONFLICT':1}))
        self.assertEqual(Counter(r['governed'] for r in self.rows),
                         Counter({'CONFIRMED':6,'REVIEW':13,'CONFLICT':1}))

    def test_genuine_dispute_causes_review_not_block(self):
        row=next(r for r in self.rows if r['case']=='challenge-active')
        self.assertEqual((row['naive_signed_quorum'],row['governed']),('CONFIRMED','REVIEW'))

    def test_false_world_is_still_confirmed(self):
        row=next(r for r in self.rows if r['case']=='false-independent-world')
        self.assertEqual((row['governed'],row['world_true']),('CONFIRMED',False))

    def test_hidden_shared_source_still_confirms(self):
        row=next(r for r in self.rows if r['case']=='hidden-shared-source')
        self.assertEqual((row['governed'],row['world_true']),('CONFIRMED',False))

    def test_auditor_challenge_avoids_global_shutdown(self):
        row=next(r for r in self.rows if r['case']=='unaffected-witnesses')
        self.assertEqual(row['governed'],'CONFIRMED')

    def test_source_patch_requires_new_witness_version(self):
        row=next(r for r in self.rows if r['case']=='stale-registry-witness')
        self.assertEqual(row['governed'],'REVIEW')

    def test_missing_trusted_anchor_refuses_confirmation(self):
        row=next(r for r in self.rows if r['case']=='no-trusted-checkpoint')
        self.assertEqual(row['governed'],'REVIEW')

if __name__=='__main__': unittest.main()
