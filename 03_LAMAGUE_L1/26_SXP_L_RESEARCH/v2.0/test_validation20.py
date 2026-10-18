import csv,io,json,re,tempfile,unittest
from collections import Counter
from pathlib import Path
from build_study import ROOT,CONDS,COHORTS,BLOCKS,OPTIONS,make_cases,participant_html,create
from score_study import COLS,parse_csv,summarize,StudyError
from sys import path
path.insert(0,str(ROOT/'baseline'))
path.insert(0,str(ROOT/'baseline'/'runtime'))
from reference19 import parse_native
from oracle19 import read

CASES=make_cases()

def write_csv(path,cohort,choose):
 with open(path,'w',newline='',encoding='utf8') as f:
  w=csv.DictWriter(f,fieldnames=COLS);w.writeheader()
  for c in CASES:
   condition=CONDS[(int(c['id'][1:])-1+COHORTS.index(cohort))%4]
   w.writerow({'version':'2.0','cohort':cohort,'case_id':c['id'],'condition':condition,
     'block':c['block'],'question_type':c['question_type'],
     'answer_code':choose(c),'elapsed_ms':1234})

class Validation20(unittest.TestCase):
 def test_case_count(self):self.assertEqual(len(CASES),32)
 def test_all_cases_parse(self):
  for c in CASES:
   with self.subTest(case=c['id']):
    r=parse_native(c['compact']+'\n')
    self.assertEqual(r['expanded_v18'].strip(),c['expanded'])
    if c['semantic_status']=='proposal':
     rr=read(c['compact']+'\n')[0]
     self.assertEqual((rr['subject'],rr['object'],rr['verb']),
        (c['semantic_subject'],c['semantic_object'],c['verb']))
    else:self.assertFalse(r['bindings'])
 def test_four_cohorts_counterbalanced(self):
  for coh in COHORTS:
   exposed=[CONDS[(int(c['id'][1:])-1+COHORTS.index(coh))%4] for c in CASES]
   self.assertEqual(Counter(exposed),Counter({c:8 for c in CONDS}))
   for block in range(8):
    self.assertEqual(set(exposed[block*4:block*4+4]),set(CONDS))
   for cond in CONDS:
    q=Counter(c['question_type'] for c,v in zip(CASES,exposed) if v==cond)
    self.assertEqual(q,Counter({'subject':2,'object':2,'status':4}))
 def test_every_case_rotates_through_arms(self):
  for case in CASES:
   self.assertEqual(set(CONDS[(int(case['id'][1:])-1+COHORTS.index(x))%4] for x in COHORTS),set(CONDS))
 def test_html_does_not_embed_other_arms(self):
  # For the compact condition, unique English full gloss and unique JSON objects
  # should not appear as stimulus data. Avoid confusing generic tutorial text with case payloads.
  for cohort in COHORTS:
   html=participant_html(CASES,cohort)
   self.assertNotIn('ANSWER_KEY_DO_NOT_SHARE',html)
   self.assertNotIn('"answer":',html)
   self.assertEqual(html.count('const cohort='),1)
   for c in CASES:
    cond=CONDS[(int(c['id'][1:])-1+COHORTS.index(cohort))%4]
    self.assertIn(json.dumps(c[cond],ensure_ascii=False).replace('<','\\u003c'),html)
    if cond!='english':self.assertNotIn(c['english'],html)
 def test_scoring_perfect_synthetic(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'synthetic.csv';write_csv(p,'B',lambda c:c['answer'])
   r=summarize(parse_csv(p))
   self.assertTrue(all(a['correct']==8 for a in r['arms'].values()))
 def test_scoring_all_unsure(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'synthetic.csv';write_csv(p,'A',lambda c:'unsure')
   r=summarize(parse_csv(p))
   self.assertTrue(all(a['correct']==0 and a['unsure']==8 for a in r['arms'].values()))
 def test_wrong_cohort_rejected(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'synthetic.csv';write_csv(p,'C',lambda c:c['answer'])
   s=p.read_text().replace(',C,',',A,')
   p.write_text(s)
   with self.assertRaises(StudyError):parse_csv(p)
 def test_duplicate_case_rejected(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'synthetic.csv';write_csv(p,'A',lambda c:c['answer'])
   s=p.read_text();lines=s.splitlines();lines[-1]=lines[-2];p.write_text('\n'.join(lines)+'\n')
   with self.assertRaises(StudyError):parse_csv(p)
 def test_no_grant_as_correct_status(self):
  self.assertNotIn('grant',{c['answer'] for c in CASES})
 def test_original_love_expression(self):
  self.assertIn('mi liva ti devora',CASES[0]['compact'])
 def test_allocated_json_matches_key(self):
  for c in CASES:
   j=json.loads(c['json']);last=j['turns'][-1]
   if c['semantic_status']=='proposal':
    p=last['embedded_proposition'];self.assertEqual((p['subject'],p['object']),(c['semantic_subject'],c['semantic_object']))
   else:self.assertEqual(last['statement']['status'],'reported_utterance')

if __name__=='__main__':unittest.main()
