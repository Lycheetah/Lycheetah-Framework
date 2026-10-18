"""Deterministic, counterbalanced human comprehension pilot materials.

No participants have been recruited or tested. CSVs measure speech-act
recognition after a shared training period. No human outcomes are claimed.
"""
from __future__ import annotations
import csv
import json
import random
from pathlib import Path
from sovereignty import ACTS, parse_expression
from consent import ACTION_ROOTS

ENGLISH_ACT={
 'trust_report':'I report that I trust {target} regarding {task}.',
 'delegation_proposal':'I propose delegating {task} to {target}.',
 'delegation_refusal':'I refuse to delegate {task} to {target}.',
 'explanation_request':'I ask {target} to explain {task}.',
 'recommendation_request':'I ask {target} for advice about {task}.',
 'decision_reservation':'I say I will keep the final decision about {task} myself.',
}
ACTION_GLOSS={'send_email':'sending the draft','read_file':'reading the file',
              'delete_file':'deleting the document','schedule_event':'scheduling the meeting',
              'publish_post':'publishing the post'}
ACTION_ROOT_BACK={v:k for k,v in ACTION_ROOTS.items()}
LABELS=sorted(ENGLISH_ACT)
JSON_FEATURES={
 'trust_report':{'attitude':'trust'},
 'delegation_proposal':{'delegation':'proposed'},
 'delegation_refusal':{'delegation':'refused'},
 'explanation_request':{'request':'explanation'},
 'recommendation_request':{'request':'recommendation'},
 'decision_reservation':{'final_decision':'reserved_by_speaker'},
}


def build(seed=1010):
 rng=random.Random(seed)
 items=[]
 kinds=list(LABELS)
 operations=list(ACTION_GLOSS)
 # Eight items per semantic act; 48 matched meanings in total.
 for kind in kinds:
  for j in range(8):
   operation=operations[(j+kinds.index(kind))%len(operations)]
   target=('ti' if j%2==0 else 'gonape agena dimotu')
   target_gloss=('you' if j%2==0 else 'Agena')
   resource='gonape '+('darafa' if j%2==0 else 'rapora')+' dimotu'
   root=next(k for k,v in ACTS.items() if v==kind)
   subject='mi' if kind=='decision_reservation' else target
   speech=f'mi {root} {subject} bakumo {ACTION_ROOT_BACK[operation]} {resource} tesavo devora'
   parsed=parse_expression(speech)['node']
   assert parsed['kind']==kind
   english=ENGLISH_ACT[kind].format(target=target_gloss,task=ACTION_GLOSS[operation])
   data={'speaker':'self_report','counterparty':'speaker' if kind=='decision_reservation' else target_gloss,
         'operation':operation,'resource':'darafa' if j%2==0 else 'rapora',
         'authenticated_authorization':False,**JSON_FEATURES[kind]}
   items.append({'id':f'{kind[:5]}_{j+1:02}', 'kind':kind,
                'sxpl':speech,'english':english,'json':json.dumps(data,separators=(',',':'))})
 rng.shuffle(items)
 return items


def write(directory:Path):
 directory.mkdir(exist_ok=True,parents=True)
 items=build()
 labels=' | '.join(LABELS)
 for offset,name in enumerate('ABC'):
  # One of three counterbalanced materials, with 16 instances per register.
  rows=[]
  for i,item in enumerate(items):
   cond=('sxpl','english','json')[(i+offset)%3]
   rows.append({'trial_id':item['id'],'condition':cond,
                'stimulus':item[cond], 'question':'Which speech act was reported?',
                'choices':labels,'response':'','confidence_1to5':'','elapsed_ms':''})
  with (directory/f'STUDY_SET_{name}.csv').open('w',newline='',encoding='utf8') as f:
   w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 with (directory/'STUDY_KEY_ORGANIZER_ONLY.csv').open('w',newline='',encoding='utf8') as f:
  w=csv.DictWriter(f,fieldnames=['trial_id','correct_kind','text_only_authorizes'])
  w.writeheader();w.writerows([{'trial_id':i['id'],'correct_kind':i['kind'],
                               'text_only_authorizes':'no'} for i in items])
 return len(items)

if __name__=='__main__':
 print('Created',write(Path(__file__).parent/'study'),'paired item concepts in 3 counterbalanced sets')
