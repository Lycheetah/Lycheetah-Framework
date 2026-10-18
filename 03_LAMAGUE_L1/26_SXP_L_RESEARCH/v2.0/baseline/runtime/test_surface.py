import unittest,random
from sxpl_v03 import parse,SXPError
from surface import hear,speak,meaning_equal
class SurfaceTests(unittest.TestCase):
 def test_examples(self):
  samples=[
   'sa nu feel ka self fe longing ta person_2 en',
   'sa no nu know ka self pr [ sa nu understand ka person_2 ta self en ] en',
   'qu ma fu reconnect ka self ta person_2 en',
   'sa nu believe ka self pr [ sa ma fu reconnect ka self ta person_2 en ] co 0.45 en',
   'sa nu love ka self ta "A person with a quote: \\"yes\\"" re loves en',
  ]
  for s in samples:
   with self.subTest(s=s):self.assertTrue(meaning_equal(s,hear(speak(s))))
 def test_3000_generated_nested(self):
  rng=random.Random(20261017)
  for _ in range(3000):
   s='sa nu see ka self ta person_2 en'
   for j in range(rng.randint(0,6)):
    s=f'sa nu believe ka speaker_{j} pr [ {s} ] co 0.{rng.randint(100000,999999)} en'
   self.assertEqual(parse(s),parse(hear(speak(s))))
 def test_registry_failures(self):
  for s in ['sava nu feel ami self ena','sa nura see ena','sava nura see en','sava nura see ena extra']:
   with self.subTest(s=s):
    with self.assertRaises(SXPError):hear(s)
 def test_reserved_collision(self):
  s='sa nu see ka sava ta nura lo "nami sava nura" en'
  self.assertTrue(meaning_equal(s,hear(speak(s))))
  with self.assertRaises(SXPError):hear('sava nura see ena')
 def test_substantive_distinction(self):
  a='sa no nu know ka self pr [ sa nu understand ka person_2 ta self en ] en'
  b='sa nu know ka self pr [ sa no nu understand ka person_2 ta self en ] en'
  self.assertNotEqual(speak(a),speak(b))
  self.assertFalse(meaning_equal(hear(speak(a)),hear(speak(b))))
if __name__=='__main__':unittest.main()
