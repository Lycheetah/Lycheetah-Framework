"""v0.9: text-only permission reports are never authenticated authorization."""
from __future__ import annotations
import random
import unittest
from sxpl_v03 import SXPError
from consent import (parse_expression,render_expression,interpret,
                     SPEECH_ROOTS,ACTION_ROOTS)
from spoken import SPELL,lev,WORDS,confusable_pairs
from pragmatics import ACT_ROOTS,NEW_PREDICATES,CONDITIONAL
from dialogue09 import parse_document,render_document
from pathlib import Path


class ConsentLanguageTests(unittest.TestCase):
    def setUp(self):
        self.phrases={
            'grant':'mi periva gonape agena dimotu bakumo mesara gonape darafa dimotu tesavo devora',
            'request':'mi pekora ti bakumo lenova gonape rapora dimotu tesavo devora',
            'deny':'mi nelora gonape agena dimotu bakumo rekova gonape darafa dimotu tesavo devora',
            'revoke':'mi revona gonape agena dimotu bakumo mesara gonape darafa dimotu tesavo devora',
        }
    def test_each_speech_act(self):
        for name,src in self.phrases.items():
            with self.subTest(name=name):
                d=parse_expression(src);self.assertEqual(src,render_expression(d))
                self.assertFalse(interpret(d)['authorizes'])
    def test_distinguish_request_and_grant(self):
        self.assertNotEqual(parse_expression(self.phrases['request'])['node']['kind'],
                            parse_expression(self.phrases['grant'])['node']['kind'])
    def test_explicit_unverified_provenance(self):
        for src in self.phrases.values():
            self.assertEqual(parse_expression(src)['node']['epistemic_status'],'unverified_utterance')
    def test_spoof_another_speaker(self):
        with self.assertRaises(SXPError):parse_expression(self.phrases['grant'].replace('mi periva','ti periva'))
    def test_missing_frame(self):
        with self.assertRaises(SXPError):parse_expression(self.phrases['grant'].replace(' tesavo',''))
    def test_unknown_action(self):
        with self.assertRaises(SXPError):parse_expression(self.phrases['grant'].replace(' mesara ',' tunova '))
    def test_resource_must_be_named(self):
        with self.assertRaises(SXPError):parse_expression(self.phrases['grant'].replace('gonape darafa dimotu','ti'))
    def test_unknown_grantee(self):
        with self.assertRaises(SXPError):parse_expression(self.phrases['grant'].replace('gonape agena dimotu','wildcard'))
    def test_old_promise_retained(self):
        text='mi pamisa bakumo fura mi satoma tesavo devora'
        d=parse_expression(text)
        self.assertEqual(d['node']['kind'],'legacy_v08')
        self.assertEqual(render_expression(d),text)
        self.assertFalse(interpret(d)['authorizes'])
    def test_old_question_retained(self):
        text='kesari ti kena bakumo gonape nara dimotu luma ti tesavo kevonu'
        d=parse_expression(text)
        self.assertEqual(render_expression(d),text)
    def test_new_roots_not_one_edit_collision(self):
        roots=set(SPEECH_ROOTS)|set(ACTION_ROOTS)
        existing=set(WORDS)|set(ACT_ROOTS)|set(NEW_PREDICATES)|set(CONDITIONAL)
        for r in roots:
            for x in existing:
                self.assertGreater(lev(r,x),1,(r,x))
        self.assertEqual([],confusable_pairs(1,roots))
    def test_bad_ast_must_fail(self):
        d=parse_expression(self.phrases['grant'])
        d['node']['epistemic_status']='verified'
        with self.assertRaises(SXPError):render_expression(d)
    def test_two_thousand_generated_roundtrips(self):
        rng=random.Random(909)
        names=['agena','darafa','rapora','nara','mora','sora']
        for _ in range(2000):
            root=rng.choice(list(SPEECH_ROOTS))
            action=rng.choice(list(ACTION_ROOTS))
            a=rng.choice(names);b=rng.choice(names)
            sentence=f'mi {root} gonape {a} dimotu bakumo {action} gonape {b} dimotu tesavo devora'
            self.assertEqual(sentence,render_expression(parse_expression(sentence)))
    def test_spelled_identifiers(self):
        def spell(x):return 'pulako '+' '.join(SPELL[c] for c in x)+' sanuti'
        phrase=f'mi periva {spell("agent_7")} bakumo mesara {spell("draft_17")} tesavo devora'
        doc=parse_expression(phrase)
        self.assertEqual(doc['node']['grantee'],'agent_7')
        self.assertEqual(doc['node']['resource'],'draft_17')
        self.assertEqual(phrase,render_expression(doc))
    def test_dialogue_roundtrip(self):
        src=(Path(__file__).parent/'examples'/'consent_not_execution.sxh').read_text()
        doc=parse_document(src)
        self.assertEqual(4,len(doc['turns']))
        self.assertEqual(doc,parse_document(render_document(doc)))
    def test_dialogue_unbound_grantee_rejected(self):
        src=(Path(__file__).parent/'examples'/'consent_not_execution.sxh').read_text()
        src=src.replace('persona agena\n','')
        with self.assertRaises(SXPError):parse_document(src)
    def test_dialogue_only_textual_permission(self):
        src=(Path(__file__).parent/'examples'/'consent_not_execution.sxh').read_text()
        doc=parse_document(src)
        self.assertTrue(all(evt['parsed']['node'].get('epistemic_status')!='verified'
                for t in doc['turns'] for evt in t['events'] if evt['kind']=='utterance'))

if __name__=='__main__':unittest.main()
