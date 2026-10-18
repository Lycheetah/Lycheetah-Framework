import copy,random,unittest
from pathlib import Path
from repair18 import parse_native, verify_bundle, ROOT_CLARIFY, ROOT_CORRECT, to_studio
from independent_reader18 import read as restricted_read
from runtime.spoken import syllables,lev
from runtime.sxpl_v03 import SXPError
from runtime.continuity13 import turn_id

EXAMPLE=Path(__file__).parent.joinpath('examples/three_turns.sxp18').read_text()

def rejected(s):
    with unittest.TestCase().assertRaises(SXPError):parse_native(s)

class Repair18Tests(unittest.TestCase):
    def test_example(self):
        result=parse_native(EXAMPLE)
        self.assertEqual([t['kind'] for t in result['meaning18']['turns']],
            ['ordinary_utterance','clarification_request','self_correction'])
        self.assertEqual(result['meaning18']['turns'][0]['utterance'],'mi liva ti devora')
        self.assertEqual(len(result['meaning18']['semantic_loss_if_legacy_only']),2)
    def test_new_roots_are_pronounceable(self):
        for root in (ROOT_CLARIFY,ROOT_CORRECT):self.assertEqual(''.join(syllables(root)),root)
        self.assertGreater(lev(ROOT_CLARIFY,ROOT_CORRECT),1)
    def test_native_is_canonical_and_reversible(self):
        r=parse_native(EXAMPLE)
        self.assertEqual(r['native'],EXAMPLE)
        self.assertEqual(verify_bundle(r['native'],r['studio17'],r['legacy_sxh'],r['studio17_sidecar'],r['meaning18']),r)
    def test_old_format_does_not_preserve_repair(self):
        r=parse_native(EXAMPLE)
        self.assertNotIn(ROOT_CLARIFY,r['legacy_sxh'])
        self.assertNotIn(ROOT_CORRECT,r['legacy_sxh'])
        self.assertIn('repira',r['legacy_sxh'])
        self.assertIn('clarification_request',str(r['meaning18']))
    def test_clarification_is_not_an_assertion(self):
        r=parse_native(EXAMPLE)
        self.assertFalse(r['meaning18']['turns'][1]['embedded_is_asserted'])
        self.assertFalse(r['meaning18']['authorizes'])
    def test_correction_does_not_erase_history(self):
        r=parse_native(EXAMPLE)
        self.assertEqual(len(r['meaning18']['turns']),3)
        self.assertIn('mi liva ti devora',r['legacy_sxh'])
        self.assertEqual(r['studio17_sidecar']['turns'][0]['corrected_by'],3)
    def test_immutable_liva(self):
        rejected(EXAMPLE.replace('liva','jiva'))
    def test_unknown_refs_fail(self):
        rejected(EXAMPLE.replace('gonape taba','gonape tabe'))
        rejected(EXAMPLE.replace('gonape taba','gonape zzzz'))
    def test_no_future_refs(self):
        rejected('people maka nara\nmaka > nara : mi kelunaro gonape tabe dimotu bakumo mi liva ti devora tesavo devora')
    def test_clarification_ownership(self):
        rejected('people maka nara\nmaka > nara : mi liva ti devora\nmaka > nara : mi kelunaro gonape taba dimotu bakumo mi luma ti devora tesavo devora')
    def test_correction_ownership(self):
        rejected('people maka nara\nmaka > nara : mi liva ti devora\nnara > maka : mi remakivo gonape taba dimotu bakumo mi luma ti devora tesavo devora')
    def test_clarification_viewpoint_explicit(self):
        rejected(EXAMPLE.replace('gonape maka dimotu luma gonape nara dimotu','mi luma ti'))
    def test_correction_fork_rejected(self):
        rejected(EXAMPLE+'maka > nara : mi remakivo gonape taba dimotu bakumo mi luma ti devora tesavo devora\n')
    def test_unstructured_marker_rejected(self):
        rejected(EXAMPLE.replace('mi kelunaro gonape taba dimotu bakumo','mi kelunaro'))
        rejected(EXAMPLE.replace('tesavo devora','devora'))
    def test_noncanonical_spacing_fails(self):
        rejected(EXAMPLE.replace('mi liva','mi  liva'))
    def test_quote_does_not_grant(self):
        txt='people maka nara\nmaka > nara : mi periva ti bakumo tavona gonape darafa dimotu tesavo devora\n'
        # v1.8 still subject to inherited syntax rules; any accepted utterance is not a host capability.
        try:r=parse_native(txt)
        except SXPError:return
        self.assertIs(r['meaning18']['authorizes'],False)
    def test_tamper_each_artifact(self):
        r=parse_native(EXAMPLE)
        with self.assertRaises(SXPError): verify_bundle(r['native'].replace('liva','luma'),r['studio17'],r['legacy_sxh'],r['studio17_sidecar'],r['meaning18'])
        with self.assertRaises(SXPError): verify_bundle(r['native'],r['studio17']+' ',r['legacy_sxh'],r['studio17_sidecar'],r['meaning18'])
        with self.assertRaises(SXPError): verify_bundle(r['native'],r['studio17'],r['legacy_sxh']+' ',r['studio17_sidecar'],r['meaning18'])
        s=copy.deepcopy(r['studio17_sidecar']);s['authorizes']=True
        with self.assertRaises(SXPError): verify_bundle(r['native'],r['studio17'],r['legacy_sxh'],s,r['meaning18'])
        s=copy.deepcopy(r['meaning18']);s['turns'][1]['kind']='ordinary_utterance'
        with self.assertRaises(SXPError): verify_bundle(r['native'],r['studio17'],r['legacy_sxh'],r['studio17_sidecar'],s)
    def test_ambiguous_pronoun_not_guessed(self):
        src='people maka nara sela vera\nmaka > nara : mi liva sivena devora\n'
        r=parse_native(src)
        self.assertEqual(r['reference_status'][0]['reference']['status'],'ambiguous')
    def test_restricted_reader(self):
        r=parse_native(EXAMPLE)
        check=restricted_read(r['native'])
        for left,right in zip(check,r['meaning18']['turns']):
            self.assertEqual(left[0],right['kind'])
            self.assertEqual(left[1],right.get('target_index'))
    def test_generated_700(self):
        rng=random.Random(180018)
        for n in range(700):
            count=rng.randint(2,12)
            people=['maka','nara','sela','vera'][:rng.randint(2,4)]
            lines=['people '+' '.join(people)];speakers=[];audiences=[];corrected=set()
            for idx in range(1,count+1):
                speaker=rng.choice(people);audience=rng.choice([p for p in people if p!=speaker])
                choices=[('ordinary_utterance',None)]
                diff=[j for j,p in enumerate(speakers,1) if p!=speaker]
                same=[j for j,p in enumerate(speakers,1) if p==speaker and j not in corrected]
                if diff:choices.append(('clarification_request',rng.choice(diff)))
                if same:choices.append(('self_correction',rng.choice(same)))
                act,target=rng.choice(choices)
                leaf=f'mi {rng.choice(["liva","luma","rava"])} ti devora'
                if act=='ordinary_utterance':phrase=leaf
                else:
                    if act=='clarification_request':
                        audience=speakers[target-1]
                        leaf=f'gonape {speakers[target-1]} dimotu luma gonape {people[0]} dimotu devora'
                    else:
                        # The original addressee is needed to keep 'ti' referentially stable.
                        audience=audiences[target-1]

                    root=ROOT_CLARIFY if act=='clarification_request' else ROOT_CORRECT
                    phrase=f'mi {root} gonape {turn_id(target)} dimotu bakumo {leaf} tesavo devora'
                    if act=='self_correction':corrected.add(target)
                lines.append(f'{speaker} > {audience} : {phrase}');speakers.append(speaker);audiences.append(audience)
            source='\n'.join(lines)+'\n'
            got=parse_native(source)
            self.assertEqual(got['native'],source)
            self.assertEqual(verify_bundle(got['native'],got['studio17'],got['legacy_sxh'],got['studio17_sidecar'],got['meaning18']),got)
            ref=restricted_read(source)
            self.assertEqual([r[0] for r in ref],[r['kind'] for r in got['meaning18']['turns']])
    def test_bounded(self):
        rejected('')
        rejected(EXAMPLE*150)

if __name__=='__main__':unittest.main()
