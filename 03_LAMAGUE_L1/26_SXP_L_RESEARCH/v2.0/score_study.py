"""Offline scorer for v2.0 pilot CSVs. Avoids claiming statistical significance.

Design: missing and 'unsure' are scored incorrect for an intent-to-test accuracy
rate; an additional attempted-only rate is reported, without suppressing abstentions.
Source form strings are not trusted. Every case/cohort/condition checked to allocation.
"""
from __future__ import annotations
import argparse,csv,json
from collections import defaultdict
from pathlib import Path
from build_study import ROOT,CONDS,COHORTS,OPTIONS
COLS=['version','cohort','case_id','condition','block','question_type','answer_code','elapsed_ms']

class StudyError(ValueError):pass

def read_key(path=ROOT/'researcher'/'ANSWER_KEY_DO_NOT_SHARE.json'):
 data=json.loads(Path(path).read_text(encoding='utf8'))
 if len(data)!=32 or len(set(i['id'] for i in data))!=32:raise StudyError('invalid researcher key')
 return {x['id']:x for x in data}

def parse_csv(path,key=None):
 key=key or read_key()
 with open(path,encoding='utf-8-sig',newline='') as f:
  reader=csv.DictReader(f)
  if reader.fieldnames!=COLS:raise StudyError('unexpected CSV columns')
  data=list(reader)
 if len(data)!=32:raise StudyError('expected 32 case records; export may be truncated')
 seen=set();cohort=None;out=[]
 for row in data:
  if any(x is None for x in row.values()):raise StudyError('missing column')
  case=row['case_id']
  if case not in key or case in seen:raise StudyError('unknown or repeated case ID')
  seen.add(case)
  if row['cohort'] not in COHORTS:raise StudyError('unknown cohort')
  cohort=cohort or row['cohort']
  if row['cohort']!=cohort:raise StudyError('mixed cohorts')
  k=key[case]
  cond=CONDS[(int(case[1:])-1+COHORTS.index(cohort))%4]
  if (row['version']!='2.0' or row['condition']!=cond or
      row['block']!=str(k['block']) or row['question_type']!=k['question_type']):
   raise StudyError(f'allocation mismatch: {case}')
  a=row['answer_code']
  if a and a not in OPTIONS[k['question_type']]:raise StudyError(f'invalid answer value: {case}')
  try:ms=int(row['elapsed_ms'])
  except Exception as e:raise StudyError('non-integer time') from e
  if ms<0 or ms>7*24*3600*1000:raise StudyError('implausible elapsed time')
  out.append({'case_id':case,'condition':cond,'type':k['question_type'],'attempted':a not in ('','unsure'),
      'answered':bool(a),'uncertain':a=='unsure','correct':a==k['answer'],'elapsed_ms':ms})
 if set(key)!=seen:raise StudyError('case set mismatch')
 return {'cohort':cohort,'rows':out}

def summarize(parsed):
 arms={}
 for cond in CONDS:
  r=[x for x in parsed['rows'] if x['condition']==cond]
  attempted=sum(x['attempted'] for x in r);correct=sum(x['correct'] for x in r)
  arms[cond]={'n':len(r),'correct':correct,'accuracy_all':round(correct/len(r),3),
      'attempted':attempted,'accuracy_attempted':round(correct/attempted,3) if attempted else None,
      'unsure':sum(x['uncertain'] for x in r),'missing':sum(not x['answered'] for x in r),
      'elapsed_ms_total':sum(x['elapsed_ms'] for x in r)}
 return {'study':'SXP-L v2.0 pre-registered exploratory pilot', 'cohort':parsed['cohort'],
     'caution':'Descriptive per-session scores. No human data unless input file comes from a consenting participant. No significance test or causal claim.',
     'arms':arms}

def main():
 a=argparse.ArgumentParser();a.add_argument('csv',nargs='+');a.add_argument('--key',default=str(ROOT/'researcher'/'ANSWER_KEY_DO_NOT_SHARE.json'))
 o=a.parse_args();key=read_key(o.key)
 for p in o.csv:
  try:print(json.dumps({'file':Path(p).name,**summarize(parse_csv(p,key))},indent=2))
  except StudyError as e:raise SystemExit(f'Invalid export ({p}): {e}')

if __name__=='__main__':main()
