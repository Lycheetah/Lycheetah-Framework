"""SXP-L v1.1 regression, independently checked signatures and adversarial tests."""
import copy
import random
import unittest
from discourse11 import parse_expression, render_expression, interpret, QUOTE, RELATION
from oracle11 import parse as independent_parse, OracleReject
from consent import SPEECH_ROOTS, ACTION_ROOTS
from sovereignty import ACTS
from spoken import SPELL, is_literal_name
from sxpl_v03 import SXPError


def named(s):
 if is_literal_name(s):return f'gonape {s} dimotu'
 return 'pulako '+' '.join(SPELL[ch] for ch in s)+' sanuti'


def speech(root,actor,action,resource):
 return f'mi {root} {actor} bakumo {action} {named(resource)} tesavo devora'


def quote(src,actor='ti'):
 return f'mi kavira {actor} bakumo {src} tesavo devora'


def relation(left,right,root='kasora'):
 return f'mi {root} bakumo {left} tesavo bakumo {right} tesavo devora'


def ast_signature(doc):
 n=doc['node']
 if n['kind']=='attributed_quote':
  i=n['quoted_ast']['node']
  if i['kind']=='legacy_v09':
   i=i['content']['node']
  if i['kind']=='legacy_v08':
   i=i['content']['node']
  return n
 return n

class Discourse11Tests(unittest.TestCase):
 def assert_canonical(self,s):
  d=parse_expression(s)
  self.assertEqual(render_expression(d),s)
  self.assertEqual(parse_expression(render_expression(d)),d)
  self.assertFalse(interpret(d)['authorizes'])
  return d

 def test_quote_grant_is_not_grant(self):
  grant=speech('periva','ti','tavona','darafa')
  s=quote(grant)
  d=self.assert_canonical(s)
  self.assertEqual(d['node']['kind'],'attributed_quote')
  self.assertEqual(d['node']['quoted_words'],grant)
  self.assertEqual(d['node']['attribution_status'],'unverified_report')
  self.assertEqual(interpret(d)['quoted_mi_refers_to'],'ti')
  self.assertEqual(independent_parse(s)[:3],('quote','mi','ti'))

 def test_contrast_causal_claim_not_verified(self):
  grant=speech('periva','ti','tavona','darafa')
  refuse=speech('resama','ti','tavona','darafa')
  for root in RELATION:
   with self.subTest(root=root):
    s=relation(grant,refuse,root)
    d=self.assert_canonical(s)
    self.assertEqual(independent_parse(s)[2],RELATION[root])
    self.assertEqual(interpret(d)['relation_is_fact'],False)

 def test_legacy_v10_survives(self):
  for root in [*ACTS,*SPEECH_ROOTS]:
   person='mi' if root=='domera' else 'ti'
   s=speech(root,person,'tavona','darafa')
   d=self.assert_canonical(s)
   self.assertEqual(d['node']['kind'],'legacy_v10')

 def test_quote_name_and_spelling(self):
  for source in ('mi','ti',named('nara'),named('agent_7')):
   s=quote(speech('tinora','ti','mesara','draft_17'),source)
   self.assert_canonical(s)
   self.assertEqual(independent_parse(s)[2],
     ('nara' if 'nara' in source else 'agent_7' if 'pulako' in source else source))

 def test_name_collision_in_quote_does_not_execute(self):
  q=quote(speech('periva','ti','rekova','darafa'))
  for changed in (q.replace('kavira','tinora'),
                  q.replace('ti bakumo mi','ti bakumo devora mi'),
                  q+' mi periva ti',
                  q.replace('tesavo devora','devora',1)):
   with self.subTest(changed=changed):
    with self.assertRaises(SXPError):parse_expression(changed)

 def test_malformed_nested_frames(self):
  inner=speech('periva','ti','mesara','darafa')
  good=quote(inner)
  for bad in (good.replace(' bakumo mi periva',' mi periva'),
              good.replace(' gonape darafa dimotu',' gonape darafa sanuti'),
              good.replace(' tesavo devora tesavo devora',' devora tesavo devora'),
              good.replace('bakumo mi periva','bakumo kavira mi periva'),
              good.replace(' gonape darafa dimotu',' darafa'),
              good+' tesavo',
              good.replace('mi kavira','ti kavira')):
   with self.subTest(bad=bad):
    with self.assertRaises(SXPError):parse_expression(bad)

 def test_opaque_text_tamper(self):
  base=quote(speech('periva','ti','tavona','darafa'))
  d=parse_expression(base)
  for change in ('status','authorizes','words','source','embedded'):
   obj=copy.deepcopy(d)
   if change=='status':obj['node']['attribution_status']='verified'
   elif change=='authorizes':obj['node']['authorizes']=True
   elif change=='words':obj['node']['quoted_words']=obj['node']['quoted_words'].replace('periva','tinora')
   elif change=='source':obj['node']['source']='invalid_name!'
   else:obj['node']['quoted_ast']['node']['kind']='verified_grant'
   with self.subTest(change=change):
    with self.assertRaises((SXPError,ValueError,TypeError)):render_expression(obj)

 def test_relation_false_causality(self):
  s=relation(speech('tinora','ti','tavona','darafa'),speech('periva','ti','tavona','darafa'),'borema')
  d=self.assert_canonical(s)
  self.assertEqual(d['node']['relation_status'],'speaker_supplied_not_verified')
  self.assertFalse(interpret(d)['relation_is_fact'])

 def test_generated_independent_oracle(self):
  rng=random.Random(111111)
  acts=list(ACTS)+list(SPEECH_ROOTS)
  actions=list(ACTION_ROOTS)
  subjects=['mi','ti',named('nara'),named('agent_7')]
  resources=['darafa','agent_7','nara','draft_17']
  for ix in range(2500):
   root=rng.choice(acts)
   actor='mi' if root=='domera' else rng.choice(subjects)
   inner=speech(root,actor,rng.choice(actions),rng.choice(resources))
   if ix%4 == 0:
    s=quote(inner,rng.choice(subjects))
   else:
    r2=rng.choice(acts)
    actor2='mi' if r2=='domera' else rng.choice(subjects)
    other=speech(r2,actor2,rng.choice(actions),rng.choice(resources))
    s=relation(inner,other,rng.choice(list(RELATION)))
   doc=self.assert_canonical(s)
   oracle=independent_parse(s)
   self.assertIn(oracle[0],('quote','relation'))
   self.assertEqual(doc['node']['kind'], 'attributed_quote' if oracle[0]=='quote' else 'speaker_relation')
   self.assertFalse(oracle[-1])
   if oracle[0]=='quote':
    self.assertEqual(doc['node']['source'],oracle[2])
    self.assertEqual(oracle[3][1],('grant_report' if root=='periva' else SPEECH_ROOTS.get(root,ACTS.get(root))))
   else:
    self.assertEqual(doc['node']['relation'],oracle[2])

 def test_independent_oracle_rejects_bad(self):
  for s in ('mi kavira ti bakumo mi periva ti devora tesavo devora',
            'mi kasora bakumo mi liva ti devora tesavo devora',
            'mi borema bakumo mi liva ti devora tesavo bakumo mi periva ti devora tesavo devora'):
   with self.assertRaises(OracleReject):independent_parse(s)

if __name__=='__main__':unittest.main()
