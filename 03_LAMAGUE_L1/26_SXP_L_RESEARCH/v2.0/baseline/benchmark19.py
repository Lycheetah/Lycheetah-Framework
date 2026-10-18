"""Synthetic controlled comparison: explicit viewpoint vs naive outer binding.
This is not a human experiment, nor a comparison against a real NLP parser.
"""
import csv
from pathlib import Path
from reference19 import parse_native, SOURCE_FRAME,CURRENT_FRAME
from oracle19 import read

FIELDS=['case','frame','outer_speaker','prior_speaker','inner','expected_mi','expected_ti','independent_agrees','naive_outer_correct','status']
rows=[]
# 40 pairs (80 scenarios): three transitive verbs, varied subjects/objects/other named actors.
roles=[('mi','ti'),('ti','mi'),('mi','mi'),('ti','ti'),('mi','gonape sela dimotu'),('gonape sela dimotu','ti'),('ti','gonape sela dimotu'),('gonape sela dimotu','mi')]
verbs=['liva','luma','rava']
for j in range(40):
    subj,obj=roles[j%len(roles)];verb=verbs[(j//len(roles))%3]
    for frame in (SOURCE_FRAME,CURRENT_FRAME):
        src=f'people maka nara sela\nmaka > nara : mi liva ti devora\nnara > maka : mi kelunaro gonape taba dimotu bakumo {frame} {subj} {verb} {obj} devora tesavo devora\n'
        r=parse_native(src);o=read(src)[0];b=r['bindings'][0]
        agrees=o['bound_mi']==b['bound_mi'] and o['bound_ti']==b['bound_ti']
        expected=('maka','nara') if frame==SOURCE_FRAME else ('nara','maka')
        assert (b['bound_mi'],b['bound_ti'])==expected and agrees
        rows.append({'case':j+1,'frame':frame,'outer_speaker':'nara','prior_speaker':'maka',
          'inner':f'{subj} {verb} {obj}','expected_mi':b['bound_mi'],'expected_ti':b['bound_ti'],
          'independent_agrees':agrees,'naive_outer_correct':(b['bound_mi']=='nara' and b['bound_ti']=='maka'),
          'status':'synthetic_fixture'})
assert len(rows)==80
out=Path(__file__).parent/'VIEWPOINT_BENCHMARK_v1.9.csv'
with out.open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(rows)
print('cases=',len(rows),'independent_agreed=',sum(r['independent_agrees'] for r in rows),
  'naive_outer_correct=',sum(r['naive_outer_correct'] for r in rows))
