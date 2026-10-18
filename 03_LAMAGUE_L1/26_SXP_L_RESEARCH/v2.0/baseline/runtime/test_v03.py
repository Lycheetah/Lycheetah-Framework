import unittest,random,sys
from sxpl_v03 import parse,render,fingerprint,SXPError

EXAMPLES=[
 'sa nu feel ka self fe longing ta person_2 en',
 'sa nu love ka self ta person_2 re loves en',
 'sa nu know ka self pr [ sa nu understand ka person_2 ta self en ] no en',
 'sa no nu know ka self pr [ sa nu understand ka person_2 lo "how much I want to see them" en ] en',
 'sa nu believe ka self pr [ sa ma fu reconnect ka self ta person_2 en ] co 0.45 en',
]
# v0.3 negation must be before time; keep a correct nested example only.
EXAMPLES[2]='sa no nu know ka self pr [ sa nu understand ka person_2 ta self en ] en'
class Tests(unittest.TestCase):
 def test_samples(self):
  for s in EXAMPLES:
   with self.subTest(s=s):
    a=parse(s);self.assertEqual(parse(render(a)),a);self.assertEqual(fingerprint(a),fingerprint(parse(render(a))))
 def test_generated(self):
  rng=random.Random(401)
  for _ in range(3000):
   depth=rng.randint(0,6)
   s='sa nu see ka self ta person_2 en'
   for j in range(depth):
    s=f'sa nu believe ka speaker_{j} pr [ {s} ] co 0.{rng.randint(100000,999999)} en'
   self.assertEqual(parse(render(parse(s))),parse(s))
 def test_reject(self):
  bad=['sa nu feel ka self fe "longing" en','sa nu believe pr sa nu X en en',
       'sa nu believe pr [ sa nu X en en', 'sa nu feel fe unavailable en',
       'sa nu see ka self ka me en','sa nu see co 1.001 en',
       'sa nu see ta "x" pr [ sa nu believe pr [ sa nu X en ] en ] en ]',
       'sa nu X en junk','sa nu X pr [ sa nu X en ] pr [ sa nu X en ] en',
       'sa nu X pr [ sa nu X en ]','sa nu X fe fear re bogus en']
  for s in bad:
   with self.subTest(s=s):
    with self.assertRaises(SXPError):parse(s)
 def test_depth(self):
  s='sa nu X en'
  for _ in range(10):s=f'sa nu X pr [ {s} ] en'
  with self.assertRaises(SXPError):parse(s)
if __name__=='__main__':unittest.main()
