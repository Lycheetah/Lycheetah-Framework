"""Bounded and adversarial tests for v1.3 textual conversational reference."""
import copy
import random
import unittest
from pathlib import Path

from sxpl_v03 import SXPError
from continuity13 import (parse_transcript, render_transcript,
                          interpret_transcript, turn_id)
from discourse12 import parse_expression as parse12

PARTICIPANTS=['maka','nara','sela','vera','luma']


def transcript(names, entries):
    lines=[f'norava gonape {n} dimotu' for n in names]
    for who,to,speech,anchor,reply in entries:
        lines.append(f'taviro gonape {who} dimotu gonape {to} dimotu')
        if anchor:lines.append(f'rasufe gonape {anchor} dimotu')
        if reply:lines.append(f'repira gonape {reply} dimotu')
        lines.extend([speech,'tevaro'])
    return '\n'.join(lines)+'\n'


class TestContinuity13(unittest.TestCase):
    def test_12_turn_dialogue(self):
        text=Path('examples/continuity_12_turns.sxh').read_text()
        doc=parse_transcript(text)
        self.assertEqual(render_transcript(doc),text)
        self.assertEqual(len(doc['turns']),12)
        self.assertEqual([x['reference']['status'] for x in doc['turns'] if 'sivena' in x['utterance']],
                         ['explicit_anchor','ambiguous','explicit_anchor','ambiguous','explicit_anchor'])
        self.assertEqual(doc['turns'][5]['reply_to'],turn_id(1))
        self.assertEqual(doc['turns'][10]['reply_to'],turn_id(10))
        self.assertFalse(doc['authorizes'])
        self.assertFalse(doc['identity_claims_authenticated'])

    def test_existing_phrase_unchanged(self):
        a=transcript(['maka','nara'], [('maka','nara','mi liva ti devora',None,None)])
        r=parse_transcript(a)['turns'][0]
        self.assertEqual(r['reference']['expanded'],'mi liva ti devora')
        self.assertEqual(r['roles'],{'mi':'maka','ti':'nara','scope':'outer_utterance_only'})
        with self.assertRaises(SXPError):
            parse_transcript(a.replace('mi liva ti','mi jiva ti'))

    def test_zero_candidates_unresolved(self):
        a=transcript(['maka','nara'], [('maka','nara','mi liva sivena devora',None,None)])
        ref=parse_transcript(a)['turns'][0]['reference']
        self.assertEqual(ref['status'],'unresolved')
        self.assertEqual(ref['candidates'],[])
        self.assertIsNone(ref['expression_ast'])

    def test_unique_candidate(self):
        a=transcript(['maka','nara','sela'], [('maka','nara','mi liva sivena devora',None,None)])
        ref=parse_transcript(a)['turns'][0]['reference']
        self.assertEqual(ref['chosen'],'sela')
        self.assertEqual(ref['status'],'unique_candidate')
        self.assertEqual(ref['expanded'],'mi liva gonape sela dimotu devora')
        self.assertEqual(ref['expression_ast'],parse12(ref['expanded']))

    def test_ambiguous_abstention(self):
        a=transcript(['maka','nara','sela','vera'], [('maka','nara','mi liva sivena devora',None,None)])
        r=parse_transcript(a)['turns'][0]['reference']
        self.assertEqual(r['status'],'ambiguous')
        self.assertEqual(r['candidates'],['sela','vera'])
        self.assertIsNone(r['chosen'])
        self.assertIsNone(r['expanded'])
        self.assertIsNone(r['expression_ast'])

    def test_scoped_anchor(self):
        a=transcript(['maka','nara','sela','vera'], [
            ('maka','nara','mi liva sivena devora','vera',None),
            ('maka','nara','mi liva sivena devora',None,None)])
        x,y=[t['reference'] for t in parse_transcript(a)['turns']]
        self.assertEqual(x['status'],'explicit_anchor')
        self.assertEqual(x['chosen'],'vera')
        self.assertEqual(y['status'],'ambiguous')

    def test_invalid_anchor_and_orphan(self):
        for anchor,speech in [('maka','mi liva sivena devora'),
                              ('missing','mi liva sivena devora'),
                              ('sela','mi liva ti devora')]:
            a=transcript(['maka','nara','sela'],[('maka','nara',speech,anchor,None)])
            with self.subTest(anchor=anchor), self.assertRaises(SXPError):parse_transcript(a)

    def test_reply_to_previous_only(self):
        base=[('maka','nara','mi liva ti devora',None,None)]
        good=transcript(['maka','nara'],base+[('nara','maka','mi liva ti devora',None,turn_id(1))])
        self.assertEqual(parse_transcript(good)['turns'][1]['reply_to'],turn_id(1))
        for bad in [turn_id(2),'tazi','maka']:
            with self.subTest(bad=bad),self.assertRaises(SXPError):
                parse_transcript(transcript(['maka','nara'],base+[('nara','maka','mi liva ti devora',None,bad)]))

    def test_invalid_noncanonical_or_unparsed_ambiguity(self):
        # Ambiguity must not become a loophole for otherwise nonsensical clauses.
        for utterance in ['mi liva sivena', 'mi gibberish sivena devora',
                          'mi liva gonape sivena dimotu devora',
                          'mi liva sivena devora devora']:
            a=transcript(['maka','nara','sela','vera'], [('maka','nara',utterance,None,None)])
            with self.subTest(utterance=utterance),self.assertRaises(SXPError):parse_transcript(a)

    def test_reject_duplicate_participant_and_bad_roles(self):
        a=transcript(['maka','nara'], [('maka','nara','mi liva ti devora',None,None)])
        for bad in [a.replace('norava gonape nara dimotu','norava gonape maka dimotu'),
                    a.replace('taviro gonape maka dimotu gonape nara dimotu',
                              'taviro gonape maka dimotu gonape maka dimotu'),
                    a.replace('taviro gonape maka dimotu','taviro gonape sela dimotu'),
                    a.replace('tevaro','tevaro tevaro')]:
            with self.assertRaises(SXPError):parse_transcript(bad)

    def test_tampered_ast_rejected(self):
        a=transcript(['maka','nara','sela','vera'], [('maka','nara','mi liva sivena devora',None,None)])
        obj=parse_transcript(a)
        updates=[('authorizes',True),('identity_claims_authenticated',True)]
        for key,value in updates:
            bad=copy.deepcopy(obj);bad[key]=value
            with self.assertRaises(SXPError):render_transcript(bad)
        for key,value in [('chosen','sela'),('status','unique_candidate'),('candidates',['sela'])]:
            bad=copy.deepcopy(obj);bad['turns'][0]['reference'][key]=value
            with self.assertRaises(SXPError):render_transcript(bad)

    def test_reported_permission_inert(self):
        sentence='mi periva ti bakumo tavona gonape darafa dimotu tesavo devora'
        a=transcript(['maka','nara'], [('maka','nara',sentence,None,None)])
        obj=parse_transcript(a)
        self.assertFalse(obj['turns'][0]['authorizes'])
        self.assertFalse(interpret_transcript(obj)[0]['authorizes'])
        self.assertFalse(interpret_transcript(obj)[0]['identity_authenticated'])

    def test_seeded_1200_generated_contexts(self):
        rng=random.Random(131313)
        for index in range(1200):
            count=rng.randrange(2,6)
            people=PARTICIPANTS[:count]
            speaker,audience=rng.sample(people,2)
            remaining=sorted(set(people)-{speaker,audience})
            anchor=(rng.choice(remaining) if remaining and index%5==0 else None)
            text=transcript(people,[(speaker,audience,'mi liva sivena devora',anchor,None)])
            obj=parse_transcript(text)
            self.assertEqual(render_transcript(obj),text)
            row=obj['turns'][0]['reference']
            if anchor:
                self.assertEqual((row['status'],row['chosen']),('explicit_anchor',anchor))
            elif len(remaining)==1:
                self.assertEqual((row['status'],row['chosen']),('unique_candidate',remaining[0]))
            elif len(remaining)==0:
                self.assertEqual((row['status'],row['chosen']),('unresolved',None))
            else:
                self.assertEqual((row['status'],row['chosen']),('ambiguous',None))
            if len(remaining)!=1 and anchor is None:self.assertIsNone(row['expression_ast'])

    def test_third_person_in_reported_scope_rejected(self):
        quoted='mi nimareko gonape nara dimotu bakumo mi liva sivena devora tesavo devora'
        a=transcript(['maka','nara','sela'], [('maka','nara',quoted,None,None)])
        # v1.2 binds the embedded first person to the *reported source*, not
        # necessarily the current turn speaker. v1.3 refuses to flatten scopes.
        with self.assertRaises(SXPError):parse_transcript(a)

    def test_bounds(self):
        a=transcript(['maka','nara'], [('maka','nara','mi liva ti devora',None,None)])
        with self.assertRaises(SXPError):parse_transcript(a*1000)
        with self.assertRaises(SXPError):parse_transcript('')

if __name__=='__main__':unittest.main()
