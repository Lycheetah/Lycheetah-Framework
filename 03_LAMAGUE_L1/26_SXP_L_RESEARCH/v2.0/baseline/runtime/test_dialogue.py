"""Unit and deterministic generative checks for the bounded v0.5 dialogue grammar."""
from pathlib import Path
import json
import random
import unittest
from dialogue import parse_document,render_document,canonical_bytes,fingerprint,resolve_pronouns
from surface import speak,hear
from roots import speak_roots, hear_roots
from sxpl_v03 import parse as clause_parse, render as clause_render, SXPError
ROOT=Path(__file__).resolve().parent


def doc(lines,people=('ada','bea')):
    return '\n'.join(['diala 0.5',*(f'persona {p}' for p in people),*lines])+'\n'


def line(identifier,source):
    return 'lina '+identifier+' | '+speak(source)


class DialogueTests(unittest.TestCase):
    def assert_code(self,code,text):
        with self.assertRaises(SXPError) as ctx:parse_document(text)
        self.assertEqual(ctx.exception.code,code)

    def test_real_dialogue(self):
        original=(ROOT/'examples'/'first_dialogue.sxh').read_text()
        ast=parse_document(original)
        self.assertEqual((len(ast['participants']),len(ast['turns'])),(3,3))
        self.assertEqual(ast,parse_document(render_document(ast)))
        self.assertEqual(fingerprint(ast),fingerprint(parse_document(render_document(ast))))
        a=ast['turns'][0]['events'][0]
        self.assertEqual(a['resolved']['clause']['roles']['actor']['value'],'mac')
        self.assertEqual(a['resolved']['clause']['roles']['proposition']['value']['roles']['target']['value'],'mac')
        b=ast['turns'][1]['events'][0]
        self.assertEqual(b['resolved']['clause']['roles']['actor']['value'],'mac') # ti = addressed participant
        neg1=ast['turns'][2]['events'][0]['resolved']['clause']
        neg2=ast['turns'][2]['events'][1]['resolved']['clause']
        self.assertEqual(neg1['polarity'],'negative')
        self.assertEqual(neg1['roles']['proposition']['value']['polarity'],'positive')
        self.assertEqual(neg2['polarity'],'negative')
        self.assertEqual(neg2['roles']['proposition']['value']['polarity'],'negative')

    def test_quoted_pronouns_not_resolved(self):
        src='sa nu remember ka mi ta "mi" lo "ti" en'
        x=parse_document(doc(['tura ada to bea',line('x1',src),'enda']))
        roles=x['turns'][0]['events'][0]['resolved']['clause']['roles']
        self.assertEqual(roles['actor']['value'],'ada')
        self.assertEqual(roles['target'],{'type':'string','value':'mi'})
        self.assertEqual(roles['context'],{'type':'string','value':'ti'})

    def test_distinct_emotion_and_nested_claim(self):
        lines=['tura ada to bea',line('x1','sa nu feel ka mi fe longing ta bea en'),
               line('x2','sa nu believe ka mi pr [ sa nu arrive ka ti ta mi en ] en'),
               'kora and x1 x2','enda']
        out=parse_document(doc(lines))
        ev=out['turns'][0]['events']
        self.assertEqual(ev[0]['resolved']['clause']['roles']['feeling']['value'],'longing')
        self.assertEqual(ev[1]['resolved']['clause']['roles']['proposition']['value']['roles']['actor']['value'],'bea')
        self.assertEqual(ev[2]['by'],'ada')

    def test_invalid_references_and_structure(self):
        base=['tura ada to bea',line('x1','sa nu feel ka mi fe longing en'),'enda']
        self.assert_code('E_DIALOG_DUP_PERSONA',doc(['persona ada',*base]))
        self.assert_code('E_DIALOG_UNKNOWN_PERSONA',doc(['tura ada to nobody',line('x1','sa nu see ka mi en'),'enda']))
        self.assert_code('E_DIALOG_DUP_LINE',doc(['tura ada to bea',line('x1','sa nu see ka mi en'),line('x1','sa nu see ka mi en'),'enda']))
        self.assert_code('E_DIALOG_UNBOUND_LINK',doc(['tura ada to bea',line('x1','sa nu see ka mi en'),'kora but x1 x2','enda']))
        self.assert_code('E_DIALOG_UNBOUND_LINK',doc(['tura ada to bea',line('x1','sa nu see ka mi en'),'kora but x1 x1','enda']))
        self.assert_code('E_DIALOG_RELATION',doc(['tura ada to bea',line('x1','sa nu see ka mi en'),'kora proof x1 x1','enda']))
        self.assert_code('E_DIALOG_NO_TURN',doc([line('x1','sa nu see ka mi en')]))
        self.assert_code('E_DIALOG_UNCLOSED_TURN',doc(['tura ada to bea',line('x1','sa nu see ka mi en')]))
        self.assert_code('E_DIALOG_EMPTY_TURN',doc(['tura ada to bea','enda']))
        self.assert_code('E_DIALOG_ID',doc(['persona mi',*base]))
        self.assert_code('E_DIALOG_ID',doc(['persona none',*base]))
        self.assert_code('E_UNBOUND_YOU',doc(['tura ada to none',line('x1','sa nu see ka ti en'),'enda']))
        self.assert_code('E_UNBOUND_PARTICIPANT',doc(['tura ada to bea',line('x1','sa nu see ka unknown_actor en'),'enda']))
        self.assert_code('E_ROOT_PREDICATE',doc(['tura ada to bea','lina x1 | sava nura see ena','enda']))

    def test_roots_are_roundtrippable_and_noncolliding(self):
        cases = [
            'sa nu believe ka mi pr [ sa nu miss ka bea ta mi en ] en',
            'sa nu feel ka mi fe longing ta bea en',
            'sa nu see ka mi ta vela lo "luma" en',
            'sa nu remember ka mi ta "believe" en',
            'sa nu see ka believe ta hope lo longing en',
            'sa nu believe ka mi ta "quoted with \\"escaped\\" value" en',
        ]
        for s in cases:
            self.assertEqual(clause_parse(s),clause_parse(hear_roots(speak_roots(s))))
        self.assertIn('lami',speak_roots(cases[0]))
        collision=speak_roots('sa nu see ka believe ta hope lo longing en')
        self.assertIn('ami nami believe',collision)
        self.assertIn('tavi nami hope',collision)
        self.assertIn('lori nami longing',collision)
        with self.assertRaises(SXPError) as ctx:
            hear_roots('sava nura lami siva ami lami vela ena')
        self.assertEqual(ctx.exception.code,'E_ROOT_POSITION')
        with self.assertRaises(SXPError) as ctx:
            hear_roots('sava nura lami nosuchroot ami nami mi ena')
        self.assertEqual(ctx.exception.code,'E_UNKNOWN_ROOT')
        with self.assertRaises(SXPError) as ctx:
            hear_roots('sava nura lami')
        self.assertEqual(ctx.exception.code,'E_ROOT_VALUE')

    def test_backcompat_surface(self):
        samples=[
            'sa nu feel ka self fe longing ta person_2 en',
            'sa no nu know ka self pr [ sa nu understand ka person_2 ta self en ] en',
            'qu ma fu reconnect ka self ta person_2 en',
        ]
        for x in samples:
            self.assertEqual(clause_parse(x),clause_parse(hear(speak(x))))

    def test_generation_1500_dialogues(self):
        """Grammar fuzzing, NOT empirical comprehension or reasoning assessment."""
        rng=random.Random(20261017)
        for i in range(1500):
            people=['ada','bea','cai']
            turns=[]
            for t in range(rng.randrange(1,5)):
                who=rng.choice(people)
                you=rng.choice([p for p in people if p!=who])
                turns.append(f'tura {who} to {you}')
                source=f'sa {rng.choice(["nu", "fu", "pa"])} {rng.choice(["hope", "feel", "see", "believe"])} ka mi ta ti en'
                turns.append(line(f'u{i}_{t}',source))
                if t:
                    turns.append(f'kora {rng.choice(["and", "but", "because"])} u{i}_{t-1} u{i}_{t}')
                turns.append('enda')
            d=parse_document(doc(turns,people))
            self.assertEqual(d,parse_document(render_document(d)))
            self.assertEqual(canonical_bytes(d),canonical_bytes(parse_document(render_document(d))))

if __name__=='__main__':unittest.main(verbosity=2)
