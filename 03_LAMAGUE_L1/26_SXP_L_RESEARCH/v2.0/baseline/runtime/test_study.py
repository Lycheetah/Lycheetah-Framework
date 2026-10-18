import collections
import csv
import tempfile
from pathlib import Path
import unittest
from study_builder import build,write

class StudyMaterialsTests(unittest.TestCase):
 def test_balanced_semantic_acts(self):
  items=build()
  self.assertEqual(48,len(items))
  self.assertTrue(all(n==8 for n in collections.Counter(i['kind'] for i in items).values()))
 def test_study_sets_have_no_correct_label_field(self):
  with tempfile.TemporaryDirectory() as temp:
   write(Path(temp));k={}
   for name in 'ABC':
    with (Path(temp)/f'STUDY_SET_{name}.csv').open(encoding='utf8') as source:
     rows=list(csv.DictReader(source))
    self.assertEqual(48,len(rows));self.assertEqual({'sxpl':16,'english':16,'json':16},dict(collections.Counter(r['condition'] for r in rows)))
    self.assertNotIn('correct_kind',rows[0]);k[name]=[(r['trial_id'],r['condition']) for r in rows]
   self.assertTrue(all(len({next(c for n,c in k[nam] if n==item) for nam in 'ABC'})==3 for item,_ in k['A']))
 def test_all_utterances_represent_correct_kind(self):
  from sovereignty import parse_expression
  for i in build():self.assertEqual(i['kind'],parse_expression(i['sxpl'])['node']['kind'])

class MinimalPairAuditTests(unittest.TestCase):
 def test_all_minimal_pairs_distinguishable(self):
  import tempfile
  from minimal_pair_eval import evaluate
  with tempfile.TemporaryDirectory() as tmp:
   result=evaluate(Path(tmp))
   self.assertEqual(105,result['total_pairs'])
   self.assertEqual(0,result['failed'])
