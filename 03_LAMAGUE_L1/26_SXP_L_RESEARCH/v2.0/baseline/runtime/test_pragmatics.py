"""Deterministic new v0.8 tests; synthetic property probes are not user studies."""
import random
import unittest
from pathlib import Path
from sxpl_v03 import SXPError
from pragmatics import parse_expression,render_expression,explain_risk,_proposition
from dialogue08 import parse_document,render_document,summarize,fingerprint

HERE=Path(__file__).parent

class PragmaticsTests(unittest.TestCase):
    def code(self,code,fn,*args):
        with self.assertRaises(SXPError) as caught:fn(*args)
        self.assertEqual(caught.exception.code,code)
    def rt(self,s):
        a=parse_expression(s)
        b=render_expression(a)
        self.assertEqual(parse_expression(b),a)
        self.assertEqual(render_expression(parse_expression(b)),b)
        return a['node']

    def test_baseline_v07_is_still_a_proposition(self):
        for s in ['mi liva ti devora',
                  'mi fela loma gonape nara dimotu devora',
                  'mi hira bakumo fura mi rava gonape nara dimotu tesavo devora',
                  'mi noka kena bakumo gonape nara dimotu luma mi tesavo devora']:
            self.assertEqual(self.rt(s)['kind'],'proposition')

    def test_legacy_questions_and_inert_directives(self):
        cases=['kesari ti kena bakumo gonape nara dimotu luma ti tesavo kevonu',
               'dutami mopaku pana gonape nara dimotu rava mi devora']
        for s in cases:
            self.assertEqual(self.rt(s)['kind'],'proposition')

    def test_stay_can_take_past_present_future_and_negation(self):
        for s in ['mi satoma devora','nura mi noka satoma devora','pana mi satoma devora',
                  'fura ti noka satoma devora','fura gonape nara dimotu satoma devora']:
            node=self.rt(s)
            self.assertEqual(node['kind'],'proposition')
            self.assertEqual(node['content']['clause']['op'],'USR:stay')

    def test_four_distinct_future_attitudes(self):
        kinds=[]
        for word in ['vanira','nivara','hira','fera','vela','kena']:
            node=self.rt(f'mi {word} bakumo fura mi satoma tesavo devora')
            self.assertEqual(node['kind'],'attitude_report')
            kinds.append(node['stance'])
        self.assertEqual(len(set(kinds)),6)

    def test_promise_is_different_from_intention_and_desire(self):
        promise=self.rt('mi pamisa bakumo fura mi satoma tesavo devora')
        desire=self.rt('mi vanira bakumo fura mi satoma tesavo devora')
        intention=self.rt('mi nivara bakumo fura mi satoma tesavo devora')
        self.assertEqual(promise['kind'],'promise_report')
        self.assertEqual((desire['kind'],intention['kind']),('attitude_report','attitude_report'))
        self.assertNotEqual(desire['stance'],intention['stance'])

    def test_inability_is_not_a_promise(self):
        cap=self.rt('mi noka kapera bakumo mi pamisa bakumo fura mi satoma tesavo tesavo devora')
        self.assertEqual(cap['kind'],'capacity_report')
        self.assertEqual(cap['polarity'],'negative')
        self.assertEqual(cap['candidate_promise']['kind'],'promise_report')
        self.assertIn('not performed',explain_risk({'node':cap}))

    def test_declining_promise_is_not_inability(self):
        declined=self.rt('mi noka pamisa bakumo fura mi satoma tesavo devora')
        cannot=self.rt('mi noka kapera bakumo mi pamisa bakumo fura mi satoma tesavo tesavo devora')
        self.assertEqual((declined['kind'],cannot['kind']),('promise_report','capacity_report'))
        self.assertNotEqual(declined,cannot)

    def test_future_promise_scope_validation(self):
        self.code('E_V08_PROMISE',parse_expression,'mi pamisa bakumo mi satoma tesavo devora')
        self.code('E_V08_PROMISE',parse_expression,'mi pamisa bakumo fura ti satoma tesavo devora')
        self.code('E_V08_PROMISE',parse_expression,'mi pamisa bakumo pana mi satoma tesavo devora')

    def test_capacity_must_have_positive_embedded_promise(self):
        self.code('E_V08_SCOPE',parse_expression,
                  'mi kapera bakumo mi vanira bakumo fura mi satoma tesavo tesavo devora')
        self.code('E_V08_SCOPE',parse_expression,
                  'mi kapera bakumo ti pamisa bakumo fura ti satoma tesavo tesavo devora')
        self.code('E_V08_SCOPE',parse_expression,
                  'mi kapera bakumo mi noka pamisa bakumo fura mi satoma tesavo tesavo devora')

    def test_conditional_does_not_assert_branches(self):
        n=self.rt('sivane bakumo fura mi satoma tesavo tanaro bakumo fura ti satoma tesavo devora')
        self.assertEqual(n['kind'],'conditional')
        self.assertEqual(n['interpretation'],'speaker_reported_conditional')
        self.assertIn('neither branch',explain_risk({'node':n}))

    def test_malformed_conditionals_fail(self):
        self.code('E_V08_CONDITIONAL',parse_expression,
                  'sivane bakumo fura mi satoma tesavo fura ti satoma devora')
        self.code('E_V08_FRAME',parse_expression,
                  'sivane bakumo fura mi satoma tanaro bakumo fura ti satoma tesavo devora')

    def test_invalid_end_and_inner_punctuation(self):
        self.code('E_V08_END',parse_expression,'mi liva ti kevonu')
        self.code('E_V08_END',parse_expression,'mi liva ti devora mi liva ti devora')
        self.code('E_SPOKEN_LEX',parse_expression,'mi liva ti.')

    def test_quoted_opaque_context_refused(self):
        self.code('E_SPOKEN_LEX',parse_expression,'mi fera bakumo mi diva ti lo "our future" tesavo devora')

    def test_dialogue_example_and_fingerprint(self):
        d=parse_document((HERE/'examples/promise_and_repair.sxh').read_text())
        self.assertEqual(summarize(d)['utterances'],8)
        self.assertEqual(summarize(d)['repairs'],1)
        self.assertEqual(summarize(d)['provenance_claims'],3)
        self.assertEqual(parse_document(render_document(d)),d)
        self.assertEqual(fingerprint(d),fingerprint(parse_document(render_document(d))))

    def test_dialogue_uncertain_provenance_not_verified(self):
        d=parse_document((HERE/'examples/promise_and_repair.sxh').read_text())
        provenance=[e for t in d['turns'] for e in t['events'] if e['kind']=='provenance']
        self.assertTrue(all(not e['verified'] for e in provenance))
        self.assertTrue(all('claimed_by' in e for e in provenance))

    def test_cross_speaker_promise_spoof_rejected(self):
        base='diala 0.8\npersona mac\npersona asha\ntura mac to asha\nlina a1 ^ '
        self.code('E_V08_PROMISOR',parse_document,
                  base+'ti pamisa bakumo fura ti satoma tesavo devora\nenda\n')
        self.code('E_V08_UNBOUND_YOU',parse_document,
                  'diala 0.8\npersona mac\ntura mac to none\nlina a1 ^ ti satoma devora\nenda\n')

    def test_repair_requires_same_speaker(self):
        base='diala 0.8\npersona mac\npersona asha\n'
        s=(base+'tura mac to asha\nlina a1 ^ mi liva ti devora\nenda\n'
           'tura asha to mac\nlina b1 ^ mi liva ti devora\nrepara a1 b1\nenda\n')
        self.code('E_V08_REPAIR',parse_document,s)

    def test_repair_requires_forward_order(self):
        s=('diala 0.8\npersona mac\ntura mac to none\n'
           'lina a1 ^ mi satoma devora\nlina a2 ^ fura mi satoma devora\nrepara a2 a1\nenda\n')
        self.code('E_V08_REPAIR',parse_document,s)

    def test_disallowed_sources_cannot_claim_verified(self):
        s=('diala 0.8\npersona mac\ntura mac to none\n'
           'lina a1 ^ mi satoma devora\nevida a1 verified\nenda\n')
        self.code('E_V08_PROVENANCE',parse_document,s)

    def test_links_do_not_claim_entailment(self):
        d=parse_document((HERE/'examples/promise_and_repair.sxh').read_text())
        links=[e for t in d['turns'] for e in t['events'] if e['kind']=='link']
        self.assertTrue(all(e['epistemic_status']=='speaker_supplied_link' for e in links))

    def test_generated_2500_round_trips(self):
        rng=random.Random(81017)
        def actor():return rng.choice(['mi','ti','gonape nara dimotu','pulako fe de sanuti'])
        def prop():
            base=rng.choice(['satoma','liva','rava','luma'])
            a=actor()
            return (rng.choice(['fura ','pana ','','nura '])+a+
                    (' noka' if rng.random()<0.3 else '')+' '+base+
                    ((' '+actor()) if base!='satoma' else ''))
        for i in range(2500):
            cat=rng.choice(['base','attitude','conditional','promise','capacity'])
            if cat=='base':s=prop()+' devora'
            elif cat=='attitude':s=rng.choice(['mi','ti'])+' '+rng.choice(['vanira','nivara','hira','fera'])+' bakumo '+prop()+' tesavo devora'
            elif cat=='conditional':s='sivane bakumo '+prop()+' tesavo tanaro bakumo '+prop()+' tesavo devora'
            elif cat=='promise':
                a=rng.choice(['mi','ti'])
                s=a+' pamisa bakumo fura '+a+' satoma tesavo devora'
            else:
                a=rng.choice(['mi','ti'])
                s=a+' noka kapera bakumo '+a+' pamisa bakumo fura '+a+' satoma tesavo tesavo devora'
            try:self.rt(s)
            except Exception as e:raise AssertionError(f'case {i}, {s}, {e!r}') from e

if __name__=='__main__':unittest.main(verbosity=2)
