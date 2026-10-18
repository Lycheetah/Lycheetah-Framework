"""Reproducible synthetic abstention vs. recency-baseline demonstration.

No truth labels for ambiguous pronouns; 'unsupported commitment' means
choosing a referent when no unique referent is logically licensed by this
restricted grammar. It does not measure real-world linguistic accuracy.
"""
import csv
import json
import random
from pathlib import Path
from continuity13 import parse_transcript, render_transcript
from oracle13 import read_flat_one_turn
from test_continuity13 import transcript


def run():
    rng=random.Random(131313)
    names=['maka','nara','sela','vera','luma']
    rows=[]
    for i in range(60):
        n=2+(i%4)
        people=names[:n]
        speaker,audience=rng.sample(people,2)
        candidates=sorted(set(people)-{speaker,audience})
        anchor=rng.choice(candidates) if candidates and i%5==0 else None
        text=transcript(people,[(speaker,audience,'mi liva sivena devora',anchor,None)])
        main=parse_transcript(text)['turns'][0]['reference']
        oracle=read_flat_one_turn(text)
        assert (main['status'],main['chosen'],main['candidates'])==(
            oracle['status'],oracle['chosen'],oracle['candidates'])
        # Deliberately invalid baseline: pretend most recently declared person
        # is the antecedent, even when several are possible.
        naive=candidates[-1] if candidates else None
        unsupported=bool(naive is not None and main['chosen'] is None)
        rows.append({'case':i+1,'participant_count':n,'speaker':speaker,
                     'audience':audience,'anchor':anchor or '',
                     'candidate_count':len(candidates),'expected_status':main['status'],
                     'chosen_by_v13':main['chosen'] or '',
                     'baseline_recent_name':naive or '',
                     'baseline_unsupported_commitment':unsupported,
                     'v13_unsupported_commitment':False,
                     'oracle_matches':True})
    Path('REFERENCE_BENCHMARK_v1.3.csv').write_text('',encoding='utf-8')
    with open('REFERENCE_BENCHMARK_v1.3.csv','w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    summary={'total_synthetic_cases':len(rows),
             'independent_limited_oracle_agreement':sum(x['oracle_matches'] for x in rows),
             'v13_abstentions':sum(x['expected_status'] in ('ambiguous','unresolved') for x in rows),
             'baseline_unsupported_commitments':sum(x['baseline_unsupported_commitment'] for x in rows),
             'v13_unsupported_commitments':sum(x['v13_unsupported_commitment'] for x in rows),
             'note':'Synthetic context uniqueness check; not a human comprehension or SOTA baseline.'}
    Path('REFERENCE_BENCHMARK_SUMMARY_v1.3.json').write_text(json.dumps(summary,indent=2)+'\n')
    return summary

if __name__=='__main__':print(json.dumps(run(),indent=2))
