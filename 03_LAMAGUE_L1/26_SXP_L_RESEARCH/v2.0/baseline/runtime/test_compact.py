"""Deterministic property tests of the bounded SXP-L v0.6 register (not human studies)."""
from __future__ import annotations
import random
import unittest
from pathlib import Path
from compact import hear_compact,speak_compact,meaning_equal
from conversation_v06 import parse_document,render_document,upgrade_v05
from dialogue import parse_document as parse_v05
from roots import speak_roots
from sxpl_v03 import parse as parse_clause,SXPError

ROOT=Path(__file__).parent

class CompactTests(unittest.TestCase):
    def reject(self,code,source):
        with self.assertRaises(SXPError) as x: hear_compact(source)
        self.assertEqual(x.exception.code,code)

    def test_examples_and_scope(self):
        examples={
            'mi liva ti.':'sa nu love ka mi ta ti en',
            'mi fela loma @nara.':'sa nu feel ka mi ta nara fe longing en',
            'mi hira ( fura mi rava @nara ).':'sa nu hope ka mi pr [ sa fu reconnect ka mi ta nara en ] en',
            'mi noka kena ( @nara luma mi ).':'sa no nu know ka mi pr [ sa nu miss ka nara ta mi en ] en',
            'mi noka kena ( @nara noka luma mi ).':'sa no nu know ka mi pr [ sa no nu miss ka nara ta mi en ] en',
            'mi fera ( mi diva ti lo "our future" ).':'sa nu fear ka mi pr [ sa nu differ ka mi ta ti lo "our future" en ] en',
            'qira ti kena ( @nara luma ti )?':'qu nu know ka ti pr [ sa nu miss ka nara ta ti en ] en',
        }
        for short,long in examples.items():
            self.assertEqual(parse_clause(hear_compact(short)),parse_clause(long))
            self.assertEqual(parse_clause(hear_compact(speak_compact(long))),parse_clause(long))
        a=parse_clause(hear_compact('mi noka kena ( @nara luma mi ).'))['clause']
        b=parse_clause(hear_compact('mi noka kena ( @nara noka luma mi ).'))['clause']
        self.assertEqual(a['polarity'],b['polarity'])
        self.assertNotEqual(a['roles']['proposition']['value']['polarity'],
                            b['roles']['proposition']['value']['polarity'])

    def test_confusable_roots_and_names(self):
        src='@liva liva @fera.'
        c=hear_compact(src)
        self.assertEqual(parse_clause(c)['clause']['roles']['actor']['value'],'liva')
        self.assertEqual(parse_clause(c)['clause']['roles']['target']['value'],'fera')
        self.assertEqual(speak_compact(c),src)
        self.reject('E_COMPACT_ENTITY','liva liva @fera.')
        self.reject('E_COMPACT_ENTITY','mi liva liva.')
        self.reject('E_COMPACT_ROOT','mi invented ti.')
        self.reject('E_COMPACT_LEX','mi liva @person-2.')

    def test_fail_closed_scope_and_punctuation(self):
        self.reject('E_COMPACT_PUNCT','mi liva ti?')
        self.reject('E_COMPACT_PUNCT','qira mi liva ti.')
        self.reject('E_COMPACT_TRAILING','mi liva ti. mi liva ti.')
        self.reject('E_COMPACT_LEX','mi liva ti!')
        self.reject('E_COMPACT_ENTITY','mi liva you.')
        self.reject('E_COMPACT_EXPECT','mi hira ti.')
        self.reject('E_COMPACT_FEELING','mi fela lava.')
        self.reject('E_COMPACT_CONTEXT','mi diva ti lo future.')
        self.reject('E_COMPACT_ROOT','mi noka noka liva ti.')
        self.reject('E_COMPACT_DEPTH','mi hira ( mi hira ( mi hira ( mi hira ( mi hira ( mi hira ( mi hira ( mi hira ( mi hira ( mi liva ti ) ) ) ) ) ) ) ) ).')
        for s in ('','mi liva ti. '*6000):
            with self.assertRaises(SXPError):hear_compact(s)

    def test_modal_time_negation_and_quotes(self):
        # Quoted context round-trips, including embedded quotes and escaped newlines.
        quoted=r'qira mura fura mi noka hira ( pana ti nela mi lo "speaker said \"no\"" )?'
        self.assertEqual(speak_compact(hear_compact(quoted)),quoted)
        text='qira mura fura mi noka hira ( pana ti nela mi lo "notes\\ninside" )?'
        c=hear_compact(text)
        self.assertEqual(speak_compact(c),text)
        self.assertEqual(parse_clause(c)['clause']['modality'],'obligation')
        self.assertEqual(parse_clause(c)['clause']['time'],'future')
        self.assertEqual(parse_clause(c)['clause']['polarity'],'negative')
        with self.assertRaises(SXPError) as x:speak_compact('sa see ka mi ta ti se "source" en')
        self.assertEqual(x.exception.code,'E_COMPACT_UNSUPPORTED')

    def test_dialogue_parity_with_v05(self):
        text=(ROOT/'examples/conversation_v06.sxh').read_text()
        out=parse_document(text)
        self.assertEqual(parse_document(render_document(out)),out)
        self.assertEqual((len(out['participants']),len(out['turns'])),(3,3))
        events=out['turns'][0]['events']
        self.assertEqual(events[0]['resolved']['clause']['roles']['actor']['value'],'mac')
        self.assertEqual(events[0]['resolved']['clause']['roles']['target']['value'],'asha')
        self.assertEqual(events[2]['relation'],'but')
        self.assertEqual(events[2]['by'],'mac')
        neg1=out['turns'][2]['events'][0]['resolved']['clause']
        neg2=out['turns'][2]['events'][1]['resolved']['clause']
        self.assertEqual(neg1['roles']['proposition']['value']['polarity'],'positive')
        self.assertEqual(neg2['roles']['proposition']['value']['polarity'],'negative')
        # v0.5 AST upgraded to v0.6 retains content (schema renamed only).
        old=parse_v05((ROOT/'examples/v05_reference.sxh').read_text())
        upgraded=upgrade_v05(old)
        copy_old=dict(old,schema='0.6.0')
        self.assertEqual(upgraded,copy_old)
        self.assertEqual(parse_document(render_document(upgraded)),upgraded)

    def test_unsupported_fallback_exact(self):
        full=speak_roots('sa nu see ka mi ta ti se "witness report" en')
        doc='\n'.join(['diala 0.6','persona ada','persona bea','tura ada to bea',
                       f'lina x1 | {full}','enda',''])
        obj=parse_document(doc)
        normalized=render_document(obj)
        self.assertIn('lina x1 | ',normalized)
        self.assertNotIn('lina x1 ~ ',normalized)
        self.assertEqual(obj,parse_document(normalized))

    def test_generated_2400_roundtrips(self):
        rng=random.Random(60617)
        people=['@ada','@bea','@cai','mi','ti']
        feelings=['loma','afela','yora','fera','sada','hira']
        transitive=['liva','luma','rava','nela','siva','ariva','mora','diva']
        attitude=['hira','vela','kena','fera']
        def gen(depth):
            seg=[]
            if rng.random()<.18:seg.append(rng.choice(['qira','dira']))
            if rng.random()<.18:seg.append(rng.choice(['mira','mura']))
            if rng.random()<.24:seg.append(rng.choice(['pana','fura']))
            seg.append(rng.choice(people))
            if rng.random()<.3:seg.append('noka')
            cat=rng.choice(['trans','feel','att']) if depth<4 else rng.choice(['trans','feel'])
            if cat=='trans':seg.extend([rng.choice(transitive),rng.choice(people)])
            elif cat=='feel':
                seg.extend(['fela',rng.choice(feelings)])
                if rng.random()<.5:seg.append(rng.choice(people))
            else:seg.extend([rng.choice(attitude),'(',*gen(depth+1),')'])
            if rng.random()<.3:seg.extend(['lo',rng.choice(['"future"','"a\\nb"','"love"','"noka"'])])
            return seg
        for i in range(2400):
            tokens=gen(0)
            short=' '.join(tokens)+('?' if tokens[0]=='qira' else '.')
            try:
                canonical=hear_compact(short)
                new=speak_compact(canonical)
                self.assertEqual(parse_clause(canonical),parse_clause(hear_compact(new)))
                self.assertEqual(new,short)
            except Exception as e:
                raise AssertionError(f'generated case {i}: {short}: {e}') from e

if __name__=='__main__':unittest.main(verbosity=2)
