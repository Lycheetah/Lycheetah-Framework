"""Source-equivalent policy parser/schema parity matrix.

Not an import of the upstream package. Parser behavior intentionally mirrors the
inspected TextRule.from_dict / AssurancePolicy.from_dict contracts.
"""
from __future__ import annotations
import copy, json, math, re
from pathlib import Path
from typing import Any, Mapping
import jsonschema
ROOT=Path(__file__).resolve().parent
SCHEMA=json.loads((ROOT/'policy.schema.json').read_text())
VALIDATOR=jsonschema.Draft202012Validator(SCHEMA)
STRICT_SCHEMA=json.loads((ROOT/'policy.schema.strict-candidate.json').read_text())
STRICT_VALIDATOR=jsonschema.Draft202012Validator(STRICT_SCHEMA)
class PolicyError(ValueError): pass

def base_policy():
 return {'id':'test.policy','version':'1','description':'Fixture policy','text':{'rules':[{'id':'customer.test-rule','pattern':'foo','title':'Test rule','description':'Fixture','phases':['input','output'],'requested_disposition':'REVIEW','claim_status':'SCAFFOLD','deterministic':False,'severity':'MEDIUM','status_basis':'','ignore_case':True}]},'tools':{'require_approval_for_side_effects':True,'denied':['shell'],'review':[],'allowlist':[],'blocked_scopes':['production.shell']},'privacy':{'capture_content':False,'capture_arguments':False,'capture_evidence_spans':False,'sensitive_argument_keys':['token']}}
def mapping(x,path):
 if not isinstance(x,Mapping): raise PolicyError(f'{path} must be object')
 return x
def reject_unknown(d,allowed,path):
 if set(d)-allowed: raise PolicyError(f'{path} contains unknown fields')
def boolean(x,path):
 if type(x) is not bool: raise PolicyError(f'{path} must be boolean')
 return x
def number(x,path):
 if isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(float(x)): raise PolicyError(f'{path} must be finite number')
 return float(x)
def integer(x,path):
 if isinstance(x,bool) or not isinstance(x,int): raise PolicyError(f'{path} must be integer')
 return x
def strings(x,path):
 if not isinstance(x,(list,tuple)) or any(not isinstance(i,str) or not i for i in x) or len(x)!=len(set(x)): raise PolicyError(f'{path} must be unique non-empty strings')
 return tuple(x)
def parse_rule(data):
 data=mapping(data,'text rule'); allowed={'id','pattern','title','description','phases','requested_disposition','claim_status','deterministic','severity','status_basis','ignore_case'}; reject_unknown(data,allowed,'text rule')
 if 'id' not in data or 'pattern' not in data: raise PolicyError('text rule requires id and pattern')
 phases=strings(data.get('phases',['input','output']),'text rule.phases')
 rid=str(data['id']); pat=str(data['pattern']); title=str(data.get('title',data['id'])); desc=str(data.get('description','Policy text rule matched')); basis=str(data.get('status_basis',''))
 if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._:-]{2,127}',rid): raise PolicyError('invalid text rule id')
 if not pat: raise PolicyError('pattern must be non-empty')
 if len(pat)>4096: raise PolicyError('pattern too long')
 if not phases or any(p not in ('input','output') for p in phases): raise PolicyError('invalid phase')
 det=boolean(data.get('deterministic',False),'deterministic'); ign=boolean(data.get('ignore_case',True),'ignore_case')
 try: re.compile(pat,re.IGNORECASE if ign else 0)
 except re.error: raise PolicyError('invalid regex')
 status=data.get('claim_status','SCAFFOLD')
 if status not in ('ACTIVE','SCAFFOLD','CONJECTURE'): raise PolicyError('invalid claim status')
 if status=='ACTIVE' and not basis.strip(): raise PolicyError('ACTIVE rule requires status_basis')
 if data.get('requested_disposition','REVIEW') not in ('ALLOW','REVIEW','BLOCK'): raise PolicyError('invalid disposition')
 if data.get('severity','MEDIUM') not in ('INFO','LOW','MEDIUM','HIGH','CRITICAL'): raise PolicyError('invalid severity')
 return {'id':rid,'pattern':pat,'title':title,'description':desc,'status_basis':basis}
def parse_policy(data):
 data=mapping(data,'policy'); reject_unknown(data,{'id','version','description','text','tools','privacy'},'policy')
 if 'id' not in data or 'version' not in data: raise PolicyError('policy requires id/version')
 if not isinstance(data['id'],str) or not isinstance(data['version'],str): raise PolicyError('policy id/version string')
 if 'description' in data and not isinstance(data['description'],str): raise PolicyError('description string')
 if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._:-]{2,127}',data['id']): raise PolicyError('invalid policy id')
 text=mapping(data.get('text',{}),'text'); tools=mapping(data.get('tools',{}),'tools'); privacy=mapping(data.get('privacy',{}),'privacy')
 reject_unknown(text,{'manipulation_review_threshold','aura_review_below_percent','max_text_characters','rules'},'text'); reject_unknown(tools,{'require_approval_for_side_effects','denied','review','allowlist','blocked_scopes'},'tools'); reject_unknown(privacy,{'capture_content','capture_arguments','capture_evidence_spans','sensitive_argument_keys'},'privacy')
 number(text.get('manipulation_review_threshold',.25),'threshold'); aura=number(text.get('aura_review_below_percent',70),'aura');
 if not 0<=aura<=100: raise PolicyError('aura range')
 mt=integer(text.get('max_text_characters',20000),'max_text_characters')
 if not 1<=mt<=2000000: raise PolicyError('max_text_characters range')
 for k in ('require_approval_for_side_effects',): boolean(tools.get(k,True),k)
 for k in ('capture_content','capture_arguments','capture_evidence_spans'): boolean(privacy.get(k,False),k)
 for k,default in [('denied',['shell','shell.*','shell_*','exec','exec.*','exec_*','subprocess*','database.drop*','identity.delete*']),('review',[]),('allowlist',[]),('blocked_scopes',['production.shell','identity.admin','secrets.*'])]: strings(tools.get(k,default),k)
 for k,default in [('sensitive_argument_keys',['password','passwd','secret','token','authorization','api_key','apikey','cookie','private_key','credential'])]: strings(privacy.get(k,default),k)
 rules=text.get('rules',[])
 if not isinstance(rules,list): raise PolicyError('rules must be array')
 parsed=[parse_rule(r) for r in rules]
 if len({r['id'] for r in parsed})!=len(parsed): raise PolicyError('rule ids must be unique')
 return True
CASES={
 'rule_id_boolean':lambda p:p['text']['rules'][0].update(id=True),
 'rule_pattern_boolean':lambda p:p['text']['rules'][0].update(pattern=True),
 'rule_title_boolean':lambda p:p['text']['rules'][0].update(title=False),
 'rule_description_integer':lambda p:p['text']['rules'][0].update(description=7),
 'rule_status_basis_integer':lambda p:p['text']['rules'][0].update(status_basis=4),
 'rule_pattern_too_long':lambda p:p['text']['rules'][0].update(pattern='a'*4097),
 'active_rule_missing_basis':lambda p:p['text']['rules'][0].update(claim_status='ACTIVE',deterministic=True,status_basis=''),
 'active_rule_blank_basis':lambda p:p['text']['rules'][0].update(claim_status='ACTIVE',deterministic=True,status_basis='   '),
 'duplicate_rule_ids':lambda p:p['text']['rules'].append(copy.deepcopy(p['text']['rules'][0])),
 'empty_tool_allowlist_item':lambda p:p['tools'].update(allowlist=['']),
 'threshold_boolean':lambda p:p['text'].update(manipulation_review_threshold=True),
 'unknown_text_rule_key':lambda p:p['text']['rules'][0].update(extension='x'),
 'wrong_deterministic_type':lambda p:p['text']['rules'][0].update(deterministic='false'),
 'wrong_phases_type':lambda p:p['text']['rules'][0].update(phases=['tool']),
 'max_text_as_float':lambda p:p['text'].update(max_text_characters=20.0),
 'duplicate_allowlist':lambda p:p['tools'].update(allowlist=['x','x']),
 'bad_regex':lambda p:p['text']['rules'][0].update(pattern='['),
 'rule_id_integer':lambda p:p['text']['rules'][0].update(id=123),
 'policy_description_integer':lambda p:p.update(description=7),
 'valid_minimal_policy':lambda p:p.update(text={'rules':[]},tools={},privacy={}),
}
def strict_type_gate(p):
 # Proposed type gate before the source-equivalent parser; semantic validation still follows.
 q=copy.deepcopy(p)
 try:
  for rule in q.get('text',{}).get('rules',[]):
   for field in ('id','pattern'):
    if field in rule and not isinstance(rule[field],str): raise PolicyError(f'text rule {field} must be a string')
   for field in ('title','description','status_basis'):
    if field in rule and not isinstance(rule[field],str): raise PolicyError(f'text rule {field} must be a string')
  parse_policy(q)
  return True,''
 except Exception as e: return False,f'{type(e).__name__}: {e}'
def run():
 rows=[]
 for name,mutate in CASES.items():
  p=base_policy(); mutate(p)
  schema_ok=not list(VALIDATOR.iter_errors(p))
  try: parse_policy(p); parser_ok=True; err=''
  except Exception as e: parser_ok=False; err=f'{type(e).__name__}: {e}'
  strict_ok,strict_err=strict_type_gate(p)
  candidate_schema_ok=not list(STRICT_VALIDATOR.iter_errors(p))
  rows.append({'case':name,'schema_accepts':schema_ok,'source_equivalent_parser_accepts':parser_ok,'strict_candidate_schema_accepts':candidate_schema_ok,'proposed_strict_parser_accepts':strict_ok,'schema_parser_parity':schema_ok==parser_ok,'candidate_contract_parity':candidate_schema_ok==strict_ok,'parser_note':err,'strict_parser_note':strict_err})
 return rows
if __name__=='__main__':
 rows=run(); print(json.dumps({'count':len(rows),'current_schema_accepts':sum(r['schema_accepts'] for r in rows),'source_equivalent_parser_accepts':sum(r['source_equivalent_parser_accepts'] for r in rows),'current_parity_cases':sum(r['schema_parser_parity'] for r in rows),'strict_candidate_schema_accepts':sum(r['strict_candidate_schema_accepts'] for r in rows),'proposed_strict_parser_accepts':sum(r['proposed_strict_parser_accepts'] for r in rows),'candidate_contract_parity_cases':sum(r['candidate_contract_parity'] for r in rows),'current_mismatches':[r for r in rows if not r['schema_parser_parity']],'candidate_mismatches':[r for r in rows if not r['candidate_contract_parity']],'results':rows},indent=2))
