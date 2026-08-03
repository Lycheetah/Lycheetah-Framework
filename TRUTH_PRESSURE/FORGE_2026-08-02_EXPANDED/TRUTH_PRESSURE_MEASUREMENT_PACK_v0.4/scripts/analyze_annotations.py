#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json,math,statistics
from pathlib import Path
from itertools import combinations

COMPONENTS=('E','P','S')

def rankdata(values):
    order=sorted(range(len(values)),key=lambda i:values[i])
    ranks=[0.0]*len(values);i=0
    while i<len(order):
        j=i
        while j+1<len(order) and values[order[j+1]]==values[order[i]]:j+=1
        r=(i+j+2)/2
        for k in range(i,j+1):ranks[order[k]]=r
        i=j+1
    return ranks

def pearson(a,b):
    if len(a)<2:return None
    ma,mb=statistics.mean(a),statistics.mean(b)
    num=sum((x-ma)*(y-mb) for x,y in zip(a,b))
    da=sum((x-ma)**2 for x in a);db=sum((y-mb)**2 for y in b)
    return None if da==0 or db==0 else num/math.sqrt(da*db)

def spearman(a,b):return pearson(rankdata(a),rankdata(b))

def interval_alpha(matrix):
    # Equal-rater, complete-data squared-distance alpha.
    observed=[]
    for row in matrix:
        observed.extend((a-b)**2 for a,b in combinations(row,2))
    flat=[x for row in matrix for x in row]
    expected=[(a-b)**2 for a,b in combinations(flat,2)]
    do=statistics.mean(observed) if observed else 0
    de=statistics.mean(expected) if expected else 0
    return 1.0 if de==0 and do==0 else (None if de==0 else 1-do/de)

def load_key(path):
    data=json.loads(Path(path).read_text())
    return {m['item_code']:m['case_id'] for items in data['raters'].values() for m in items}

def load_ratings(paths,key):
    by_case={}
    for rater_index,p in enumerate(paths):
        with Path(p).open(encoding='utf-8-sig',newline='') as f:
            for row in csv.DictReader(f):
                code=row['item_code'].strip()
                if code not in key:raise ValueError(f'Unknown item_code {code} in {p}')
                case=key[code]
                rec={'rater':rater_index,'ambiguity':row['ambiguity_flag_yes_no'].strip().lower()}
                if rec['ambiguity'] not in ('yes','no'):raise ValueError(f'Invalid ambiguity flag for {code}')
                for c in COMPONENTS:
                    score=int(row[f'{c}_score_0_4']);conf=int(row[f'{c}_confidence_1_3'])
                    if not 0<=score<=4:raise ValueError(f'{code} {c} score out of range')
                    if not 1<=conf<=3:raise ValueError(f'{code} {c} confidence out of range')
                    rec[c]=score;rec[f'{c}_conf']=conf
                rec['reason']=row['brief_reason'].strip()
                if not rec['reason']:raise ValueError(f'Missing reason for {code}')
                by_case.setdefault(case,[]).append(rec)
    expected=len(paths)
    for case,rows in by_case.items():
        if len(rows)!=expected:raise ValueError(f'{case} has {len(rows)} ratings, expected {expected}')
    return by_case

def load_engine(path):
    if not path:return {}
    out={}
    for line in Path(path).read_text().splitlines():
        if not line.strip():continue
        row=json.loads(line);r=row['result']['components']
        out[row['id']]={'E':r['evidence'],'P':r['explanatoryPower'],'S':r['strain']}
    return out

def component_report(component,by_case,engine):
    cases=sorted(by_case)
    matrix=[[r[component] for r in sorted(by_case[c],key=lambda x:x['rater'])] for c in cases]
    pair_exact=[];pair_within=[];pair_spearman=[]
    nraters=len(matrix[0])
    for a,b in combinations(range(nraters),2):
        va=[row[a] for row in matrix];vb=[row[b] for row in matrix]
        pair_exact.append(sum(x==y for x,y in zip(va,vb))/len(va))
        pair_within.append(sum(abs(x-y)<=1 for x,y in zip(va,vb))/len(va))
        pair_spearman.append(spearman(va,vb))
    means=[statistics.mean(row)/4 for row in matrix]
    result={
      'alpha_interval_squared':interval_alpha(matrix),
      'mean_pair_exact_agreement':statistics.mean(pair_exact),
      'mean_pair_within_one_agreement':statistics.mean(pair_within),
      'pairwise_spearman':pair_spearman,
      'mean_confidence':statistics.mean(r[f'{component}_conf'] for c in cases for r in by_case[c]),
    }
    common=[c for c in cases if c in engine]
    if common:
        human=[statistics.mean(r[component] for r in by_case[c])/4 for c in common]
        machine=[engine[c][component] for c in common]
        disagreements=sorted(({'case_id':c,'human_mean':h,'engine':m,'absolute_error':abs(h-m)} for c,h,m in zip(common,human,machine)),key=lambda x:x['absolute_error'],reverse=True)
        result['engine_correspondence']={
          'spearman':spearman(human,machine),
          'mean_absolute_error':statistics.mean(abs(h-m) for h,m in zip(human,machine)),
          'largest_disagreements':disagreements[:8],
        }
    return result

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--key',required=True)
    ap.add_argument('--ratings',nargs='+',required=True)
    ap.add_argument('--engine-results')
    ap.add_argument('--output',required=True)
    args=ap.parse_args()
    key=load_key(args.key);ratings=load_ratings(args.ratings,key);engine=load_engine(args.engine_results)
    report={
      'protocol':'TP-MEASURE-0.4',
      'cases':len(ratings),'raters':len(args.ratings),
      'ambiguity_rate':statistics.mean(r['ambiguity']=='yes' for rows in ratings.values() for r in rows),
      'components':{c:component_report(c,ratings,engine) for c in COMPONENTS},
      'boundary':'Construct agreement and engine correspondence do not establish factual truth or universal validity.'
    }
    Path(args.output).write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
