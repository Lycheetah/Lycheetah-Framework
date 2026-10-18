"""SXP-L 1.9 new binder regression; no human-study outcomes."""
import copy,random,unittest
from pathlib import Path
from reference19 import parse_native,expand19,verify_bundle,NEW,SOURCE_FRAME,CURRENT_FRAME,write_bundle
from oracle19 import read
from runtime.sxpl_v03 import SXPError
from runtime.continuity13 import turn_id
from runtime.spoken import syllables,lev
from repair18 import parse_native as parse18

BASE=Path(__file__).parent
EXAMPLE=(BASE/'examples/contrasting_viewpoints.sxp19').read_text()
OLD=(BASE/'examples/explicit_v18_fallback.sxp18').read_text()
def not_allowed(source):
    with unittest.TestCase().assertRaises(SXPError):parse_native(source)

class NaturalReference19(unittest.TestCase):
    def test_example_binds_two_viewpoints(self):
        r=parse_native(EXAMPLE)
        self.assertEqual(r['expanded_v18'],OLD)
        b=r['bindings']
        self.assertEqual(len(b),2)
        self.assertEqual((b[0]['bound_mi'],b[0]['bound_ti']),('maka','nara'))
        self.assertEqual((b[1]['bound_mi'],b[1]['bound_ti']),('nara','maka'))
        self.assertTrue(all(x['proposed_not_asserted'] for x in b))
        self.assertEqual(read(EXAMPLE)[0]['subject'],'maka')
        self.assertEqual(read(EXAMPLE)[1]['subject'],'nara')
    def test_historical_explicit_fallback(self):
        self.assertEqual(parse_native(OLD)['expanded_v18'],OLD)
        self.assertFalse(parse_native(OLD)['bindings'])
        self.assertEqual(parse_native(OLD)['legacy_sxh'],parse18(OLD)['legacy_sxh'])
    def test_original_phrase_untouched(self):
        self.assertIn('mi liva ti devora',parse_native(EXAMPLE)['native'])
        not_allowed(EXAMPLE.replace('mi liva ti devora','mi jiva ti devora'))
    def test_reversible_record(self):
        d=parse_native(EXAMPLE)
        self.assertEqual(verify_bundle(d['native'],d['expanded_v18'],d['meaning19'],d['legacy_sxh'],d['meaning18'],d['studio17'],d['studio17_sidecar']),d)
    def test_legacy_cannot_recover_binder_choice(self):
        d=parse_native(EXAMPLE)
        self.assertNotIn(SOURCE_FRAME,d['expanded_v18'])
        self.assertNotIn(CURRENT_FRAME,d['legacy_sxh'])
        self.assertIn('loss', 'loss' )
        self.assertIn('cannot be recovered',d['meaning19']['loss_if_expanded_only'])
    def test_new_words_shape(self):
        self.assertEqual(''.join(syllables(SOURCE_FRAME)),SOURCE_FRAME)
        self.assertEqual(''.join(syllables(CURRENT_FRAME)),CURRENT_FRAME)
        self.assertGreater(lev(SOURCE_FRAME,CURRENT_FRAME),1)
    def test_corrector_ownership_inherited(self):
        not_allowed(EXAMPLE.replace('maka > nara : mi remakivo','nara > maka : mi remakivo'))
    def test_unknown_and_forward_references(self):
        not_allowed(EXAMPLE.replace('kelunaro gonape taba','kelunaro gonape tani'))
        not_allowed(EXAMPLE.replace('kelunaro gonape taba','kelunaro gonape tabe'))
    def test_wrong_clarification_audience(self):
        not_allowed(EXAMPLE.replace('nara > maka : mi kelunaro','nara > sela : mi kelunaro'))
    def test_missing_binder(self):
        not_allowed(EXAMPLE.replace('soraviko mi luma','mi luma'))
    def test_nested_scope_rejected(self):
        not_allowed(EXAMPLE.replace('soraviko mi luma ti devora','soraviko mi hira bakumo mi luma ti devora tesavo devora'))
    def test_outside_binder_rejected(self):
        not_allowed(EXAMPLE.replace('mi liva ti devora','soraviko mi liva ti devora'))
    def test_third_person_not_guessed(self):
        not_allowed(EXAMPLE.replace('soraviko mi luma ti devora','soraviko mi luma sivena devora'))
    def test_bad_names_rejected(self):
        not_allowed(EXAMPLE.replace('soraviko mi luma ti devora','soraviko mi luma gonape ghost dimotu devora'))
    def test_attacker_controlled_sidecar(self):
        r=parse_native(EXAMPLE)
        fake=copy.deepcopy(r['meaning19']);fake['bindings'][0]['bound_mi']='nara'
        with self.assertRaises(SXPError):verify_bundle(r['native'],r['expanded_v18'],fake,r['legacy_sxh'],r['meaning18'],r['studio17'],r['studio17_sidecar'])
        with self.assertRaises(SXPError):verify_bundle(r['native'],r['expanded_v18']+' ',r['meaning19'],r['legacy_sxh'],r['meaning18'],r['studio17'],r['studio17_sidecar'])
    def test_word_order_matters(self):
        r=EXAMPLE.replace('soraviko mi luma ti devora','soraviko ti luma mi devora')
        d=parse_native(r)
        self.assertIn('gonape nara dimotu luma gonape maka dimotu',d['expanded_v18'])
    def test_named_subject_and_mixed_roles(self):
        r=EXAMPLE.replace('soraviko mi luma ti devora','soraviko gonape sela dimotu luma ti devora')
        d=parse_native(r)
        self.assertIn('gonape sela dimotu luma gonape nara dimotu',d['expanded_v18'])
    def test_source_correction_history(self):
        r=parse_native(EXAMPLE)
        self.assertEqual(r['studio17_sidecar']['turns'][0]['corrected_by'],4)
        self.assertFalse(r['meaning19']['authorizes'])
    def test_oracle_cross_reads_400_seeded(self):
        rng=random.Random(190019)
        names=['maka','nara','sela','vera']
        accepted=0
        for _ in range(400):
            n=rng.randint(2,4); people=names[:n]
            lines=['people '+' '.join(people)]
            roles=[]
            for i in range(1,rng.randint(2,7)):
                speaker=rng.choice(people)
                audience=rng.choice([p for p in people if p!=speaker])
                eligible=[j for j,(prior_speaker,_) in enumerate(roles,1) if prior_speaker != speaker]
                if not eligible or rng.random()<0.35:
                    word=rng.choice(('liva','luma','rava'))
                    text=f'mi {word} ti devora'
                else:
                    target=rng.choice(eligible);audience=roles[target-1][0]
                    word=rng.choice(('liva','luma','rava'))
                    frame=rng.choice((SOURCE_FRAME,CURRENT_FRAME))
                    actor=rng.choice(('mi','ti'))
                    obj=rng.choice(('mi','ti'))
                    text=f'mi kelunaro gonape {turn_id(target)} dimotu bakumo {frame} {actor} {word} {obj} devora tesavo devora'
                lines.append(f'{speaker} > {audience} : {text}')
                roles.append((speaker,audience))
            src='\n'.join(lines)+'\n'
            main=parse_native(src)
            accepted+=1
            independent=read(src)
            self.assertEqual(len(independent),len(main['bindings']))
            for a,b in zip(independent,main['bindings']):
                self.assertEqual((a['turn'],a['reference_turn'],a['frame'],a['bound_mi'],a['bound_ti']),
                                 (b['turn'],b['reference_turn'],b['frame'],b['bound_mi'],b['bound_ti']))
            self.assertEqual(expand19(src)[0],main['expanded_v18'])
            self.assertFalse(main['meaning19']['authorizes'])
        self.assertEqual(accepted,400)
    def test_inherited_old_example(self):
        old=(BASE/'examples/three_turns.sxp18').read_text()
        self.assertEqual(parse_native(old)['expanded_v18'],old)
    def test_canonical_spacing(self):
        not_allowed(EXAMPLE.replace('soraviko mi luma','soraviko  mi luma'))
    def test_filename_write(self):
        import tempfile
        with tempfile.TemporaryDirectory() as path:
            r=write_bundle(EXAMPLE,Path(path))
            self.assertEqual(Path(path,'conversation.sxp19').read_text(),EXAMPLE)
            self.assertEqual(Path(path,'conversation.sxpl19.json').is_file(),True)
if __name__=='__main__':unittest.main()
