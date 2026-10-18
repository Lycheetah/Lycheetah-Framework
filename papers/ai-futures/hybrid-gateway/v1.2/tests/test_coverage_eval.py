"""Freeze the synthetic comparator's intended interpretation."""
import unittest
from run_coverage_eval import evaluate

class CoverageEvalRegression(unittest.TestCase):
    def test_synthetic_conformance_comparison(self):
        r=evaluate()
        self.assertEqual(r['case_count'],32)
        self.assertEqual(r['group_summary']['complete'], {'n':8,'legacy_accepted':8,'v05_ready':8})
        self.assertEqual(r['group_summary']['missing'], {'n':8,'legacy_accepted':8,'v05_ready':0})
        self.assertEqual(r['group_summary']['duplicate'], {'n':8,'legacy_accepted':8,'v05_ready':0})
        self.assertEqual(r['group_summary']['unexpected'], {'n':8,'legacy_accepted':0,'v05_ready':0})
