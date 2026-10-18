"""SXP-L v1.0: typed reports, backward compatibility, and adversarial guards."""
import copy
import random
import unittest
from pathlib import Path
from sxpl_v03 import SXPError
from sovereignty import ACTS, parse_expression, render_expression, interpret
from consent import parse_expression as parse_old, render_expression as render_old
from spoken import SPELL,lev
from dialogue10 import parse_document,render_document
from authority_bridge import inspect,collect_reports
from authz import sign_fixture,grant_claims,revoke_claims

NAMES=('agena','darafa','rapora','nara','agent_7','draft_17')
ACTIONS=('mesara','lenova','rekova','sotira','tavona')


def name(x):
    from spoken import is_literal_name
    if is_literal_name(x):return 'gonape '+x+' dimotu'
    return 'pulako '+' '.join(SPELL[c] for c in x)+' sanuti'


def sentence(root,who='ti',action='tavona',resource='darafa'):
    return f'mi {root} {who} bakumo {action} {name(resource)} tesavo devora'


class SovereigntyTests(unittest.TestCase):
    def test_six_acts_differ(self):
        self.assertEqual(set(ACTS.values()),{parse_expression(sentence(r,'mi' if r=='domera' else 'ti'))['node']['kind'] for r in ACTS})
    def test_every_act_is_unverified_and_non_authorizing(self):
        for r in ACTS:
            with self.subTest(root=r):
                s=sentence(r,'mi' if r=='domera' else 'ti')
                doc=parse_expression(s)
                self.assertEqual(render_expression(doc),s)
                self.assertEqual(doc['node']['epistemic_status'],'unverified_utterance')
                self.assertFalse(interpret(doc)['authorizes'])
    def test_trust_and_delegation_differ(self):
        a=parse_expression(sentence('tinora'))
        b=parse_expression(sentence('dalora'))
        self.assertNotEqual(a['node']['kind'],b['node']['kind'])
    def test_refusal_and_decision_reservation_differ(self):
        a=parse_expression(sentence('resama'))
        b=parse_expression(sentence('domera','mi'))
        self.assertNotEqual(a['node']['kind'],b['node']['kind'])
    def test_no_nonself_decision_reservation(self):
        with self.assertRaises(SXPError):parse_expression(sentence('domera','ti'))
        with self.assertRaises(SXPError):parse_expression(sentence('domera',name('agena')))
    def test_no_arbitrary_verb(self):
        with self.assertRaises(SXPError):parse_expression(sentence('tinora').replace('tavona','executeeverything'))
    def test_missing_frame(self):
        with self.assertRaises(SXPError):parse_expression(sentence('tinora').replace(' tesavo',''))
    def test_extra_words(self):
        with self.assertRaises(SXPError):parse_expression(sentence('tinora').replace(' tesavo',' noka tesavo'))
    def test_unframed_name(self):
        with self.assertRaises(SXPError):parse_expression('mi tinora agena bakumo tavona gonape darafa dimotu tesavo devora')
    def test_nonself_report_spoof(self):
        with self.assertRaises(SXPError):parse_expression(sentence('tinora').replace('mi tinora','ti tinora'))
    def test_question_not_promoted_to_report(self):
        with self.assertRaises(SXPError):parse_expression(sentence('tinora').replace('devora','kevonu'))
    def test_confusable_new_words(self):
        from sovereignty import OLD_VOCAB
        for r in ACTS:
            self.assertTrue(all(lev(r,x)>1 for x in OLD_VOCAB))
        self.assertTrue(all(lev(a,b)>1 for a in ACTS for b in ACTS if a!=b))
    def test_tampered_ast(self):
        doc=parse_expression(sentence('tinora'))
        for field,malicious in [('epistemic_status','verified'),('action','unlimited'),('counterparty','*'),('resource','mi')]:
            with self.subTest(field=field):
                d=copy.deepcopy(doc);d['node'][field]=malicious
                with self.assertRaises((SXPError,TypeError,ValueError)):render_expression(d)
        d=copy.deepcopy(doc);d['node']['authorizes']=True
        with self.assertRaises(SXPError):render_expression(d)
    def test_older_sentences_survive(self):
        old=[
            'mi periva ti bakumo tavona gonape darafa dimotu tesavo devora',
            'mi revona ti bakumo tavona gonape darafa dimotu tesavo devora',
            'mi vanira bakumo fura mi satoma tesavo devora',
            'mi liva ti devora',
            'kesari ti kena bakumo gonape nara dimotu luma ti tesavo kevonu',
        ]
        for s in old:
            self.assertEqual(render_expression(parse_expression(s)),s)
            self.assertEqual(render_old(parse_old(s)),s)
            self.assertFalse(interpret(parse_expression(s))['authorizes'])
    def test_document_round_trip_and_resolved_references(self):
        path=Path(__file__).parent/'examples'/'sovereignty_is_not_permission.sxh'
        doc=parse_document(path.read_text())
        self.assertEqual(doc,parse_document(render_document(doc)))
        rs=collect_reports(doc)
        self.assertEqual('agena',rs[0]['counterparty'])
        self.assertEqual('mac',next(x for x in rs if x['kind']=='decision_reservation')['counterparty'])
    def test_unknown_participant_rejected(self):
        src=(Path(__file__).parent/'examples'/'sovereignty_is_not_permission.sxh').read_text()
        with self.assertRaises(SXPError):parse_document(src.replace('persona agena\n',''))
    def test_delegation_not_capability(self):
        req={'grantee':'agena','operation':'publish_post','resource':'darafa'}
        doc=parse_document((Path(__file__).parent/'examples'/'sovereignty_is_not_permission.sxh').read_text())
        self.assertEqual('DENY_NO_EXACT_GRANT',inspect(doc,req,[],{}, {},now=150)['policy']['code'])
    def test_transcripts_do_not_control_gate(self):
        req={'grantee':'agena','operation':'publish_post','resource':'darafa'}
        key=b'v10-demo-key-local-only-noprod';owner='owner'
        grant=grant_claims('grantx',owner,'agena','publish_post','darafa',100,200)
        events=[sign_fixture(grant,key)]
        docs=[parse_document((Path(__file__).parent/'examples'/'sovereignty_is_not_permission.sxh').read_text())]
        modified=(Path(__file__).parent/'examples'/'sovereignty_is_not_permission.sxh').read_text().replace('mi resama','mi dalora').replace('mi domera mi','mi ranova ti')
        docs.append(parse_document(modified))
        for d in docs:
            x=inspect(d,req,events,{owner:key},{owner:{'darafa'}},now=150)
            self.assertTrue(x['policy']['allowed'])
            self.assertFalse(x['execution_performed'])
        self.assertTrue(inspect(docs[0],req,events,{owner:key},{owner:{'darafa'}},now=150)['review_advised'])
        self.assertFalse(inspect(docs[1],req,events,{owner:key},{owner:{'darafa'}},now=150)['review_advised'])
        revoked=[*events,sign_fixture(revoke_claims(grant,120),key)]
        self.assertFalse(inspect(docs[0],req,revoked,{owner:key},{owner:{'darafa'}},now=150)['policy']['allowed'])
    def test_2500_generated_round_trips(self):
        rng=random.Random(10010)
        choices=tuple(ACTS)
        for _ in range(2500):
            root=rng.choice(choices)
            who='mi' if root=='domera' else rng.choice(('mi','ti',name(rng.choice(NAMES))))
            src=sentence(root,who,rng.choice(ACTIONS),rng.choice(NAMES))
            doc=parse_expression(src)
            self.assertEqual(src,render_expression(doc))
            self.assertEqual(doc,parse_expression(render_expression(doc)))

if __name__=='__main__':unittest.main()

class MalformedPolicyInputTests(unittest.TestCase):
 def test_bad_request_fails_closed_no_exception(self):
  doc=parse_document((Path(__file__).parent/'examples'/'sovereignty_is_not_permission.sxh').read_text())
  for request in (None,[],{'grantee':'agena'},'publish it'):
   self.assertEqual('DENY_INVALID_REQUEST',inspect(doc,request,[],{}, {},now=100)['policy']['code'])
