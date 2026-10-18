"""SXP-L v1.0 deterministic minimal pairs, not a human comprehension benchmark."""
from __future__ import annotations
import csv
import json
from itertools import combinations
from pathlib import Path
from sovereignty import ACTS,parse_expression,interpret
from consent import ACTION_ROOTS
from authz import decision

WORDS={**ACTS,'periva':'grant_report'}


def sample(root,action):
 who='mi' if root=='domera' else 'ti'
 return f'mi {root} {who} bakumo {action} gonape darafa dimotu tesavo devora'


def evaluate(out_dir:Path):
 rows=[]
 for a,b in combinations(WORDS,2):
  for action in ACTION_ROOTS:
   a_txt,b_txt=sample(a,action),sample(b,action)
   a_node,b_node=parse_expression(a_txt)['node'],parse_expression(b_txt)['node']
   a_kind=a_node['kind'] if a_node['kind']!='legacy_v09' else a_node['content']['node']['kind']
   b_kind=b_node['kind'] if b_node['kind']!='legacy_v09' else b_node['content']['node']['kind']
   req={'grantee':'agena','operation':ACTION_ROOTS[action],'resource':'darafa'}
   result=decision(req,[],{}, {},now=100)
   yes=(a_kind!=b_kind and not result['allowed'] and
        not interpret(parse_expression(a_txt))['authorizes'] and
        not interpret(parse_expression(b_txt))['authorizes'])
   rows.append({'item':len(rows)+1,'act_a':a_kind,'act_b':b_kind,'action':ACTION_ROOTS[action],
                'sentence_a':a_txt,'sentence_b':b_txt,
                'distinct_ast_kinds':str(a_kind!=b_kind).lower(),
                'text_alone_authorizes':str(result['allowed']).lower(),
                'pass':str(yes).lower()})
 out_dir.mkdir(parents=True,exist_ok=True)
 with (out_dir/'MINIMAL_PAIR_AUDIT_v1.0.csv').open('w',newline='',encoding='utf8') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 summary={'total_pairs':len(rows),'passed':sum(r['pass']=='true' for r in rows),
          'failed':sum(r['pass']!='true' for r in rows),
          'method':'seven semantic roots by five supported action types',
          'claim_limit':'Same-parser AST distinction and empty-authority policy fixtures; no independent semantic understanding or human comprehension test.'}
 (out_dir/'MINIMAL_PAIR_SUMMARY_v1.0.json').write_text(json.dumps(summary,indent=2)+'\n')
 return summary

if __name__=='__main__':print(json.dumps(evaluate(Path(__file__).parent),indent=2))
