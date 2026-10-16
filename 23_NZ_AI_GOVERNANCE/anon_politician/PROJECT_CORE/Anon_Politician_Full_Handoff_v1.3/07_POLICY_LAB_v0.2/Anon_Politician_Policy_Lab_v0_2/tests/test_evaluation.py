import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'evaluation'))
from prepare_blind_pack import prepare
from aggregate_reviews import aggregate, DIMENSIONS

class EvaluationTests(unittest.TestCase):
    def raw(self):
        methods=[]
        for mid in ['ordinary_baseline','structured_ledger','anon_politician']:
            methods.append({'method_id':mid,'label':mid,'analysis_text':f'Analysis produced for {mid}.'})
        return {'experiment_id':'T1','case_id':'C1','policy_question':'Test question','source_packet_sha256':'abc','source_cutoff':'2026-10-16','reference_context':{'known_facts':['fact']},'methods':methods}

    def test_blind_mapping_covers_three_arms_without_disclosing_ids_in_pack(self):
        pack,key=prepare(self.raw(),seed=10)
        self.assertEqual({c['candidate_id'] for c in pack['candidates']},{'A','B','C'})
        self.assertNotIn('method_id', str(pack))
        self.assertEqual(set(key['mapping']),{'A','B','C'})
        self.assertEqual(len(set(key['mapping'].values())),3)

    def test_prepare_rejects_missing_output(self):
        data=self.raw();data['methods'][0]['analysis_text']='PASTE FROZEN ARM A OUTPUT HERE'
        with self.assertRaises(ValueError): prepare(data,seed=1)

    def test_aggregate_has_profiles_but_no_total_or_winner(self):
        review={'experiment_id':'T1','blind_pack_id':'APB-123','case_id':'C1','reviewer_id':'r1','candidates':[]}
        for cid in 'ABC':
            review['candidates'].append({'candidate_id':cid,'ratings':{dim:{'score':'2','note':'Checked'} for dim in DIMENSIONS},'critical_flags':[]})
        out=aggregate([review],{'mapping':{'A':'ordinary_baseline','B':'structured_ledger','C':'anon_politician'}})
        self.assertIn('dimensions',out['methods_or_aliases']['ordinary_baseline'])
        self.assertNotIn('total_score', str(out))
        self.assertEqual(out['reporting_rule'], "Dimension profiles only. No composite total or overall winner is calculated. Reviewers' critical issue flags must be investigated separately; do not average away material errors.")

    def test_critical_flags_are_not_averaged_away(self):
        review={'experiment_id':'T1','blind_pack_id':'APB-123','case_id':'C1','reviewer_id':'r1','candidates':[{'candidate_id':'A','ratings':{},'critical_flags':[{'code':'material_factual_error','label':'Material factual error'}]}]}
        out=aggregate([review])
        self.assertEqual(len(out['methods_or_aliases']['A']['critical_flags']),1)

    def test_mapping_key_must_match_blind_pack(self):
        review={'experiment_id':'T1','blind_pack_id':'APB-111','case_id':'C1','reviewer_id':'r1','candidates':[]}
        with self.assertRaises(ValueError): aggregate([review],{'blind_pack_id':'APB-222','mapping':{'A':'ordinary_baseline','B':'structured_ledger','C':'anon_politician'}})

if __name__=='__main__': unittest.main()
