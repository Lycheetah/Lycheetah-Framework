"""v1.4 restricted comparison against independent oracle and naïve outer-role shortcut."""
import csv
import random
from pathlib import Path
from oracle14 import read
from perspective14 import parse_transcript, render_transcript

rng=random.Random(140014);results=[]
people=['maka','nara','sela','vera','luma']
ROOTS=['naveriko','belareko','nesaluko']

def line(p):return 'gonape '+p+' dimotu'

for ix in range(90):
    pool=people[:2+ix%4] if 2+ix%4<=len(people) else people
    speaker,audience=rng.sample(pool,2)
    frames=[]
    for _ in range(ix%4):
        a,b=rng.sample(pool,2)
        frames.append((ROOTS[(ix+_)%3],a,b))
    local=(frames[-1][1],frames[-1][2]) if frames else (speaker,audience)
    third=sorted(set(pool)-set(local))
    leaf='mi liva sivena devora' if ix%3 else 'mi liva ti devora'
    anchor=third[-1] if ('sivena' in leaf and third and ix%7==0) else None
    lines=[f'norava {line(p)}' for p in pool]
    lines.append(f'taviro {line(speaker)} {line(audience)}')
    if anchor: lines.append(f'rasufe {line(anchor)}')
    lines.extend(f'{root} {line(a)} {line(b)}' for root,a,b in frames)
    lines.extend([leaf,'tevaro'])
    source='\n'.join(lines)+'\n'
    actual=parse_transcript(source)
    check=read(source)[0]
    a=actual['turns'][0]
    valid=(a['leaf_roles']['mi']==check['local_mi'] and
           a['leaf_roles']['ti']==check['local_ti'] and
           [f['kind'] for f in a['frames']]==check['frame_kinds'] and
           a['reference']['status']==check['reference_status'] and
           a['reference']['chosen']==check['referent'] and
           a['reference']['candidates']==check['candidates'] and
           render_transcript(actual)==source)
    # Deliberately naïve model binds inner leaf's first person to outer speaker.
    naive_correct=local[0]==speaker and local[1]==audience
    results.append({'case':ix+1,'frames':len(frames),'participants':len(pool),
        'reference_status':check['reference_status'],
        'oracle_agrees':valid,'outer_only_baseline_correct_roles':naive_correct})
    if not valid: raise AssertionError((ix,a,check))
with open('REFERENCE_BENCHMARK_v1.4.csv','w',newline='') as f:
    dw=csv.DictWriter(f,fieldnames=list(results[0]));dw.writeheader();dw.writerows(results)
print(f'cases={len(results)} oracle_agreements={sum(x["oracle_agrees"] for x in results)} '
    f'outer_only_right={sum(x["outer_only_baseline_correct_roles"] for x in results)} '
    f'uncertain_or_ambiguous={sum(x["reference_status"] in ("ambiguous","unresolved") for x in results)}')
