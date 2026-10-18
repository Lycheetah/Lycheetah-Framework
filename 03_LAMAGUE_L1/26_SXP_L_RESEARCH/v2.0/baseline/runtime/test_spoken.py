"""SXP-L 0.7 deterministic spoken-script tests; no human/audio evidence."""
from __future__ import annotations
import random
import unittest
from pathlib import Path
from sxpl_v03 import parse as canonical_parse,SXPError
from compact import hear_compact,speak_compact
from spoken import (speak_spoken,hear_spoken,syllables,ipa,confusable_pairs,
                    WORDS,SPELL,UNSPELL,FRAMES,lev)
from conversation_v07 import parse_document,render_document,upgrade_v06
from conversation_v06 import parse_document as parse_v06

ROOT=Path(__file__).parent

class SpokenTests(unittest.TestCase):
    def failcode(self,code,fn,*args):
        with self.assertRaises(SXPError) as ctx:fn(*args)
        self.assertEqual(ctx.exception.code,code)

    def same(self,compact):
        spoken=speak_spoken(compact)
        recovered=hear_spoken(spoken)
        self.assertEqual(canonical_parse(recovered),canonical_parse(hear_compact(compact)))
        self.assertEqual(spoken,speak_spoken(speak_compact(recovered)))
        for token in spoken.split():ipa(token)
        return spoken

    def test_foundation(self):
        cases={
          'mi liva ti.':'mi liva ti devora',
          'mi fela loma @nara.':'mi fela loma gonape nara dimotu devora',
          'mi hira ( fura mi rava @nara ).':
             'mi hira bakumo fura mi rava gonape nara dimotu tesavo devora',
          'qira ti kena ( @nara luma ti )?':
             'kesari ti kena bakumo gonape nara dimotu luma ti tesavo kevonu',
          'mi noka kena ( @nara noka luma mi ).':
             'mi noka kena bakumo gonape nara dimotu noka luma mi tesavo devora',
        }
        for compact,expected in cases.items():self.assertEqual(self.same(compact),expected)

    def test_names_are_not_verbs(self):
        v=self.same('@liva liva @fera.')
        self.assertIn('gonape liva dimotu liva gonape fera dimotu',v)
        self.assertEqual(canonical_parse(hear_spoken(v))['clause']['roles']['actor']['value'],'liva')

    def test_machine_id_spelling_reversible(self):
        for name in ['person_2','mac','asha','x9','v07_test','a','nara9','_invalid']:
            compact=f'mi liva @{name}.'
            if name.startswith('_'):
                self.failcode('E_COMPACT_LEX',speak_spoken,compact)
                continue
            v=self.same(compact)
            if name in {'person_2','mac','asha','x9','v07_test','nara9'}:
                self.assertIn(FRAMES['spell_open'],v)
            if name in {'a'}:self.assertIn(FRAMES['name_open'],v)
        self.assertEqual(len(SPELL),37)
        self.assertEqual(len(set(SPELL.values())),37)
        self.assertEqual({v:k for k,v in SPELL.items()},UNSPELL)

    def test_scope_negation_preserved(self):
        a=canonical_parse(hear_spoken(self.same('mi noka kena ( @nara luma mi ).')))
        b=canonical_parse(hear_spoken(self.same('mi kena ( @nara noka luma mi ).')))
        self.assertNotEqual(a,b)
        self.assertEqual(a['clause']['polarity'],'negative')
        self.assertEqual(b['clause']['roles']['proposition']['value']['polarity'],'negative')

    def test_optional_time_moods_modals(self):
        for c in [
          'qira mura fura mi noka hira ( pana ti nela mi )?',
          'dira mira pana @nara rava mi.',
          'mi fela afela.',
          'mi hira ( mi vela ( fura ti rava mi ) ).',
        ]:
            self.same(c)

    def test_quote_refuses_loss(self):
        self.failcode('E_SPOKEN_QUOTE',speak_spoken,
                      'mi fera ( mi diva ti lo "our future" ).')

    def test_invalid_frames_and_words(self):
        self.failcode('E_SPOKEN_FRAME',hear_spoken,'mi liva gonape nara devora')
        self.failcode('E_SPOKEN_FRAME',hear_spoken,'mi liva dimotu devora')
        self.failcode('E_SPOKEN_FRAME',hear_spoken,'mi liva pulako ba de')
        self.failcode('E_SPOKEN_SPELL',hear_spoken,'mi liva pulako beda sanuti devora')
        self.failcode('E_SPOKEN_SPELL',hear_spoken,'mi liva pulako mu sanuti devora')
        self.failcode('E_SPOKEN_WORD',hear_spoken,'mi invented ti devora')
        self.failcode('E_COMPACT_PUNCT',hear_spoken,'mi liva ti kevonu')
        self.failcode('E_COMPACT_PUNCT',hear_spoken,'kesari mi liva ti devora')
        self.failcode('E_SPOKEN_LEX',hear_spoken,'mi liva @nara devora')
        self.failcode('E_SPOKEN_LEX',hear_spoken,'mi liva ti.')
        self.failcode('E_SPOKEN_LEX',hear_spoken,'mi liva ti Devora')
        self.failcode('E_SPOKEN_LIMIT',hear_spoken,'a'*36001)

    def test_phonemes_and_morphotactics(self):
        for w in WORDS|set(SPELL.values()):
            self.assertGreaterEqual(len(syllables(w)),1,w)
            self.assertTrue(ipa(w),w)
        self.assertEqual(syllables('afela'),('a','fe','la'))
        self.assertEqual(ipa('liva'),'ˈli.va')
        self.assertEqual(ipa('nara'),'ˈna.ɾa')
        self.failcode('E_PHONE_SHAPE',syllables,'ash')
        self.failcode('E_PHONE_CHAR',syllables,'qira')

    def test_collision_audit_exposes_known_pairs(self):
        pairs={(a,b) for a,b,_ in confusable_pairs()}
        self.assertIn(('loma','luma'),pairs)
        self.assertIn(('mi','ti'),pairs)
        self.assertEqual(lev('loma','luma'),1)
        self.assertGreaterEqual(lev(FRAMES['name_open'],FRAMES['name_close']),2)

    def test_conversation_with_fallback(self):
        text=(ROOT/'examples/first_spoken_dialogue.sxh').read_text()
        d=parse_document(text)
        self.assertEqual((len(d['participants']),len(d['turns'])),(3,3))
        norm=render_document(d)
        self.assertEqual(parse_document(norm),d)
        self.assertIn('lina a1 ^ ',norm)
        self.assertIn('lina a2 ~ ',norm)
        before=parse_v06((ROOT/'examples/conversation_v06.sxh').read_text())
        after=upgrade_v06(before)
        self.assertEqual(after,dict(before,schema='0.7.0'))
        self.assertEqual(parse_document(render_document(after)),after)

    def test_generated_3600_semantic_roundtrips(self):
        rng=random.Random(71017)
        names=['@mac','@nara','@nara9','@person_2','@liva','mi','ti']
        transitive=['liva','luma','rava','nela','siva','ariva','mora','diva']
        feelings=['loma','afela','yora','fera','sada','hira']
        attitudes=['kena','vela','hira','fera']
        def gen(depth=0):
            out=[]
            if rng.random()<.2:out.append(rng.choice(['qira','dira']))
            if rng.random()<.23:out.append(rng.choice(['mira','mura']))
            if rng.random()<.3:out.append(rng.choice(['pana','fura']))
            out.append(rng.choice(names))
            if rng.random()<.3:out.append('noka')
            cat=rng.choice(['trans','feel','att']) if depth<4 else rng.choice(['trans','feel'])
            if cat=='trans':out += [rng.choice(transitive),rng.choice(names)]
            elif cat=='feel':
                out+=['fela',rng.choice(feelings)]
                if rng.random()<.45:out.append(rng.choice(names))
            else:out += [rng.choice(attitudes),'(',*gen(depth+1),')']
            return out
        for i in range(3600):
            tokens=gen()
            written=' '.join(tokens)+('?' if tokens[0]=='qira' else '.')
            try:self.same(written)
            except Exception as e:raise AssertionError(f'case {i}: {written} {e}') from e

if __name__=='__main__':unittest.main(verbosity=2)
