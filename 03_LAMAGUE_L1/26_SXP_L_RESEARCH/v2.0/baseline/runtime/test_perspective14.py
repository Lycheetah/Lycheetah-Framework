"""Bounded v1.4 tests: scopes, referents, mutation resistance and legacy parity."""
import copy
import random
import unittest
from pathlib import Path
from sxpl_v03 import SXPError
from perspective14 import (parse_transcript, render_transcript, interpret_transcript,
                           compatibility_check, MAX_DEPTH)

PEOPLE=['maka','nara','sela','vera','luma']

def make_text(people, turns):
    lines=[f'norava gonape {p} dimotu' for p in people]
    for turn in turns:
        speaker,audience,frames,leaf,anchor,reply=turn
        lines.append(f'taviro gonape {speaker} dimotu gonape {audience} dimotu')
        if anchor: lines.append(f'rasufe gonape {anchor} dimotu')
        if reply:lines.append(f'repira gonape {reply} dimotu')
        for root,holder,who in frames:
            lines.append(f'{root} gonape {holder} dimotu gonape {who} dimotu')
        lines.extend([leaf,'tevaro'])
    return '\n'.join(lines)+'\n'

class Perspective14Tests(unittest.TestCase):
    def test_demo_8_turns(self):
        data=Path('examples/nested_perspectives_8_turns.sxh').read_text()
        doc=parse_transcript(data)
        self.assertEqual(len(doc['turns']),8)
        self.assertEqual(parse_transcript(render_transcript(doc)),doc)
        self.assertFalse(doc['authorizes'])
        for x in interpret_transcript(doc):
            self.assertFalse(x['proposition_accepted_as_fact'])
            self.assertFalse(x['speech_authenticated'])
            self.assertFalse(x['authorizes'])

    def test_existing_liva(self):
        x=make_text(['maka','nara'],[('maka','nara',[],'mi liva ti devora',None,None)])
        doc=parse_transcript(x)
        self.assertEqual(doc['turns'][0]['leaf_roles']['mi'],'maka')
        self.assertEqual(doc['turns'][0]['leaf_roles']['ti'],'nara')
        self.assertTrue(compatibility_check(x))
        with self.assertRaises(SXPError):parse_transcript(x.replace('mi liva ti','mi jiva ti'))

    def test_nested_scope_shifts_first_and_second_person(self):
        txt=make_text(PEOPLE[:4],[('maka','nara',[
            ('naveriko','nara','maka'),('belareko','sela','vera')],
            'mi liva ti devora',None,None)])
        t=parse_transcript(txt)['turns'][0]
        self.assertEqual(t['speaker'],'maka')
        self.assertEqual(t['leaf_roles']['mi'],'sela')
        self.assertEqual(t['leaf_roles']['ti'],'vera')
        self.assertEqual([f['kind'] for f in t['frames']],['reported_speech','belief'])
        self.assertEqual(t['reference']['expanded'],'mi liva ti devora')
        self.assertEqual(render_transcript(parse_transcript(txt)),txt)

    def test_uncertainty_is_not_negation(self):
        txt=make_text(PEOPLE[:4],[('maka','nara',[
            ('nesaluko','maka','nara'),('belareko','nara','maka')],
            'gonape sela dimotu liva gonape vera dimotu devora',None,None)])
        t=parse_transcript(txt)['turns'][0]
        self.assertEqual(t['frames'][0]['kind'],'not_know_whether')
        self.assertEqual(t['frames'][1]['kind'],'belief')
        self.assertFalse(t['frames'][0]['authorizes'])
        self.assertEqual(t['leaf_roles']['mi'],'nara')
        self.assertEqual(t['leaf_roles']['ti'],'maka')

    def test_ambiguous_third_person_uses_local_frame(self):
        frames=[('belareko','sela','maka')]
        txt=make_text(PEOPLE[:4],[('maka','nara',frames,'mi liva sivena devora',None,None)])
        r=parse_transcript(txt)['turns'][0]['reference']
        self.assertEqual(r['status'],'ambiguous')
        self.assertEqual(r['candidates'],['nara','vera'])
        self.assertIsNone(r['chosen'])
        self.assertIsNone(r['expression_ast'])
        good=make_text(PEOPLE[:4],[('maka','nara',frames,'mi liva sivena devora','vera',None)])
        resolved=parse_transcript(good)['turns'][0]
        self.assertEqual(resolved['reference']['chosen'],'vera')
        self.assertEqual(resolved['reference']['status'],'explicit_anchor')
        self.assertEqual(resolved['leaf_roles']['mi'],'sela')

    def test_anchor_cannot_use_inner_holder_or_addressee(self):
        for x in ['maka','sela']:
            bad=make_text(PEOPLE[:4],[('maka','nara',[('belareko','sela','maka')],
                       'mi liva sivena devora',x,None)])
            with self.subTest(anchor=x),self.assertRaises(SXPError):parse_transcript(bad)

    def test_no_nested_pronoun_smuggling_inside_leaf(self):
        bad=make_text(PEOPLE[:4],[('maka','nara',[('naveriko','nara','maka')],
          'mi nimareko gonape sela dimotu bakumo mi liva sivena devora tesavo devora',None,None)])
        with self.assertRaises(SXPError):parse_transcript(bad)

    def test_frame_names_must_be_declared_distinct(self):
        for holder,audience in [('sela','sela'),('missing','nara'),('maka','missing')]:
            text=make_text(PEOPLE[:4],[('maka','nara',[('belareko',holder,audience)],
                       'mi liva ti devora',None,None)])
            with self.subTest(holder=holder,audience=audience),self.assertRaises(SXPError):parse_transcript(text)

    def test_malformed_frame_cannot_fallback_to_legacy(self):
        base=make_text(['maka','nara'],[('maka','nara',[('belareko','nara','maka')],
                       'mi liva ti devora',None,None)])
        for changed in [base.replace('belareko gonape nara dimotu gonape maka dimotu', 'belareko nara'),
                        base.replace('tevaro','tevaro tevaro'),
                        base.replace('belareko', 'unexpected'),
                        base.replace('mi liva ti devora','mi liva ti')]:
            with self.assertRaises(SXPError):parse_transcript(changed)

    def test_limits(self):
        text=make_text(['maka','nara'],[('maka','nara',
                 [('belareko','nara','maka')]*(MAX_DEPTH+1),'mi liva ti devora',None,None)])
        with self.assertRaises(SXPError):parse_transcript(text)
        with self.assertRaises(SXPError):parse_transcript('')

    def test_tampering_rejected(self):
        src=make_text(PEOPLE[:4],[('maka','nara',[('naveriko','nara','maka'),('belareko','sela','vera')],
                       'mi liva ti devora',None,None)])
        doc=parse_transcript(src)
        modifications=[lambda d:d.update(authorizes=True),
                       lambda d:d['turns'][0]['frames'][1].update(holder='maka'),
                       lambda d:d['turns'][0]['frames'][0].update(evidence='verified'),
                       lambda d:d['turns'][0]['leaf_roles'].update(mi='maka'),
                       lambda d:d['turns'][0]['reference'].update(status='verified')]
        for fn in modifications:
            bad=copy.deepcopy(doc);fn(bad)
            with self.assertRaises(SXPError):render_transcript(bad)

    def test_legacy_12_turn_compatibility(self):
        src=Path('examples/continuity_12_turns.sxh').read_text()
        self.assertTrue(compatibility_check(src))
        doc=parse_transcript(src)
        self.assertEqual(render_transcript(doc),src)
        self.assertTrue(all(not x['frames'] for x in doc['turns']))

    def test_seeded_1800_nested_frames(self):
        rng=random.Random(141414)
        for k in range(1800):
            count=rng.randrange(2,6);people=PEOPLE[:count]
            speaker,audience=rng.sample(people,2)
            depth=rng.randrange(0,5)
            frames=[]
            for _ in range(depth):
                holder,to=rng.sample(people,2)
                frames.append((rng.choice(tuple(['naveriko','belareko','nesaluko'])),holder,to))
            leaf=rng.choice(['mi liva ti devora','mi fela loma ti devora',
                     'gonape '+speaker+' dimotu liva ti devora'])
            src=make_text(people,[(speaker,audience,frames,leaf,None,None)])
            doc=parse_transcript(src)
            self.assertEqual(render_transcript(doc),src)
            local=(frames[-1][1],frames[-1][2]) if frames else (speaker,audience)
            self.assertEqual((doc['turns'][0]['leaf_roles']['mi'],doc['turns'][0]['leaf_roles']['ti']),local)

if __name__=='__main__':unittest.main()
