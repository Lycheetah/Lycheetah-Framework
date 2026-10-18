"""Transport/contract integration without pretending to run a real language model."""
import json
import unittest
from hybrid_gateway import ProviderConfig
from probe_live_model import run_suite


class LiveProbeTransportTests(unittest.TestCase):
    def config(self):
        return ProviderConfig('fixture-model', base_url='http://127.0.0.1:11434/v1')

    def fake(self,url,payload,config):
        task=json.loads(payload['messages'][1]['content'])
        sid=task['source_id']
        if sid in ('positive','distractor'):
            candidates=[{
                'subject':'refunds','predicate':'window_days','scope':'in_store',
                'value':'14','valid_from':'2026-10-01T00:00:00Z','valid_until':None,
                'evidence_quote':'Refunds allowed within 14 days.','supersedes':[],
            }]
        else:
            candidates=[]
        return {'choices':[{'message':{'content':json.dumps({'claims':candidates})}}]}

    def test_inference_path_with_deterministic_fixture_only(self):
        report=run_suite(self.config(), self.fake)
        self.assertEqual(report['total'],4)
        self.assertEqual(report['contract_conformant'],4)
        self.assertEqual([c['received'] for c in report['cases']],[1,0,0,1])
        self.assertTrue(report['inference_request_attempted'])
        self.assertEqual(report['transport_mode'],'fixture')
        self.assertTrue(report['base_url_redacted'])
        self.assertNotIn('source_text', report)

    def test_provider_hallucinates_negated_example(self):
        def bad(url,payload,config):
            sid=json.loads(payload['messages'][1]['content'])['source_id']
            if sid=='example-only':
                candidate={
                    'subject':'refunds','predicate':'window_days','scope':'in_store',
                    'value':'60','valid_from':'2026-10-01T00:00:00Z','valid_until':None,
                    'evidence_quote':'Refunds allowed within 60 days.','supersedes':[],
                }
                return {'choices':[{'message':{'content':json.dumps({'claims':[candidate]})}}]}
            return self.fake(url,payload,config)
        report=run_suite(self.config(), bad)
        self.assertEqual(report['contract_conformant'],3)
        row=next(c for c in report['cases'] if c['case_id']=='example-only')
        self.assertEqual(row['disposition'],'REVIEW_UNEXPECTED')
        self.assertEqual(row['unexpected'],1)

    def test_model_omits_known_policy(self):
        def empty(url,payload,config):
            return {'choices':[{'message':{'content':'{"claims":[]}'}}]}
        report=run_suite(self.config(),empty)
        self.assertEqual(report['contract_conformant'],2)
        self.assertEqual([r['disposition'] for r in report['cases']],
            ['REVIEW_MISSING','READY_FOR_REVIEW','READY_FOR_REVIEW','REVIEW_MISSING'])

    def test_invalid_json_is_not_counted_as_correct_abstention(self):
        def broken(url,payload,config):
            return {'choices':[{'message':{'content':'not-json'}}]}
        report=run_suite(self.config(),broken)
        self.assertEqual(report['contract_conformant'],0)
        self.assertTrue(all(r['disposition']=='EXTRACTION_REJECTED' for r in report['cases']))

if __name__=='__main__': unittest.main()
