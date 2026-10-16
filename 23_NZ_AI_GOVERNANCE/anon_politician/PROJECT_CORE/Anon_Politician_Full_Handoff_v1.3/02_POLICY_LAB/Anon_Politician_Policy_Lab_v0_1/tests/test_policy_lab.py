import unittest
from src.policy_lab import Claim, EvidenceItem, review_queue, validate_packet, packet_summary

class PolicyLabTests(unittest.TestCase):
    def test_transitive_review_queue_preserves_dependants(self):
        claims = [
            Claim('F1', 'Base assumption', 'factual'),
            Claim('T1', 'Theory depends on F1', 'assumption', depends_on=['F1']),
            Claim('E1', 'Proposal detail depends on T1', 'assumption', depends_on=['T1']),
            Claim('X1', 'Unrelated', 'value'),
        ]
        self.assertEqual(review_queue('F1', claims), ['E1', 'T1'])
        self.assertEqual([c.status for c in claims], ['proposed'] * 4)

    def test_unknown_claim_is_reported(self):
        self.assertRaises(KeyError, review_queue, 'missing', [])

    def test_fact_requires_source(self):
        e = EvidenceItem('E1', 'Something happened', 'fact')
        self.assertTrue(any('source URL' in x for x in e.validate()))

    def test_forecast_requires_limitations(self):
        e = EvidenceItem('E1', 'Projected effect', 'forecast', source_url='https://example.org')
        self.assertTrue(any('limitations' in x for x in e.validate()))

    def test_open_voluntary_sample_not_auto_representative(self):
        packet = {'case_id':'X','title':'Y','policy_question':'Q','decision_owner':'Human','last_updated':'2026-10-16',
                  'authority_mode':'advisory','evidence':[],'claims':[],
                  'public_input':{'sample_type':'open_voluntary','representative_claim':True}}
        self.assertTrue(any('cannot be labelled representative' in x for x in validate_packet(packet)))

    def test_ai_cannot_be_decision_owner(self):
        packet = {'case_id':'X','title':'Y','policy_question':'Q','decision_owner':'AI','last_updated':'2026-10-16',
                  'authority_mode':'advisory','evidence':[],'claims':[],'decision_status':'adopted_by_ai'}
        self.assertTrue(any('AI cannot be the accountable decision-maker' in x for x in validate_packet(packet)))

    def test_summary_does_not_generate_recommendation(self):
        s = packet_summary({'case_id':'X','title':'Y','claims':[],'evidence':[]})
        self.assertIsNone(s['policy_recommendation'])
        self.assertIn('does not evaluate', s['warning'])

    def test_dependency_cycles_terminate(self):
        claims = [Claim('A','a','assumption',depends_on=['B']), Claim('B','b','assumption',depends_on=['A'])]
        self.assertEqual(review_queue('A', claims), ['B'])

if __name__ == '__main__': unittest.main()
