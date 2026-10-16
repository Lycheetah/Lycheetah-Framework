import json
import unittest
from pathlib import Path
from src.policy_lab import validate_packet, review_queue, Claim

ROOT = Path(__file__).resolve().parents[1]

class CasePacketTests(unittest.TestCase):
    def setUp(self):
        self.packet = json.loads((ROOT / 'case_study' / 'policy_packet_template.json').read_text())

    def test_case_packet_has_no_validation_errors(self):
        self.assertEqual(validate_packet(self.packet), [])

    def test_review_queue_tracks_downstream_hypotheses(self):
        claims = [Claim(**c) for c in self.packet['claims']]
        affected = review_queue('F-GOV-02', claims)
        self.assertIn('H-INCIDENCE-01', affected)
        self.assertIn('H-DELIVERY-01', affected)

    def test_open_voluntary_input_is_not_consensus_by_default(self):
        self.packet['public_input'] = {'sample_type':'open_voluntary','representative_claim':True}
        self.assertTrue(any('cannot be labelled representative' in e for e in validate_packet(self.packet)))

if __name__ == '__main__': unittest.main()
