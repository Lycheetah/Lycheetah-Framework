"""Independent small v1.1 reading oracle.

Deliberately does NOT import discourse11, the v1.0 parser, or its renderer.
Its COVERAGE IS LIMITED to quoted/linked short v0.9/v1.0 action reports
plus the sentence `mi liva ti devora`. It is NOT an independent full grammar.
Returns semantic signatures so tests can check more than text round trips.
"""
from __future__ import annotations
import re

Q='kavira'; R={'kasora':'contrast_report','borema':'causal_claim_report'}
REPORTS={
 'periva':'grant_report','pekora':'permission_request',
 'nelora':'denial_report','revona':'revocation_report',
 'tinora':'trust_report','dalora':'delegation_proposal',
 'resama':'delegation_refusal','esaloma':'explanation_request',
 'ranova':'recommendation_request','domera':'decision_reservation'
}
ACTIONS={'mesara':'send_email','lenova':'read_file','rekova':'delete_file',
         'sotira':'schedule_event','tavona':'publish_post'}
SYMBOLS='abcdefghijklmnopqrstuvwxyz0123456789_'
CODES=[c+v for c in 'bdfgkmnp' for v in 'aeiou']
SPELLING=dict(zip(CODES,SYMBOLS))
ID=re.compile(r'[a-z][a-z0-9_]{0,39}\Z')
LEX=re.compile(r'[a-z]+\Z')

class OracleReject(ValueError):pass
class OracleUnsupported(OracleReject):pass

def _fail(message):raise OracleReject(message)

def lex(text):
 if not isinstance(text,str) or not text or len(text)>36000: _fail('lex input')
 if not re.fullmatch(r'[a-z]+(?:\s+[a-z]+)*',text):_fail('lex format')
 words=text.split()
 if len(words)>4096:_fail('size')
 return words

def entity(words,i,resource=False):
 if i>=len(words):_fail('entity truncation')
 if words[i] in ('mi','ti') and not resource:return words[i],i+1
 if words[i]=='gonape' and i+2<len(words) and words[i+2]=='dimotu':
  item=words[i+1]; j=i+3
 elif words[i]=='pulako':
  j=i+1; pieces=[]
  while j<len(words) and words[j]!='sanuti':
   if words[j] not in SPELLING:_fail('spell code')
   pieces.append(SPELLING[words[j]]);j+=1
  if j==len(words):_fail('spell frame')
  item=''.join(pieces);j+=1
 else:_fail('entity framing')
 if not ID.fullmatch(item) or item in ('mi','ti','none'):_fail('invalid entity')
 return item,j

def frame(words,start):
 if start>=len(words) or words[start]!='bakumo':_fail('frame open')
 depth=1;i=start+1;data=[]
 while i<len(words):
  w=words[i];i+=1
  if w=='bakumo':depth+=1
  if w=='tesavo':
   depth-=1
   if depth==0:
    if not data:_fail('empty frame')
    return data,i
  data.append(w)
 _fail('frame close')

def act(words):
 if words==['mi','liva','ti','devora']:return ('love','mi','ti')
 if len(words)<7 or words[:1]!=['mi'] or words[-1]!='devora' or words[1] not in REPORTS:
  raise OracleUnsupported('not in limited oracle subset')
 role,i=entity(words,2)
 if i>=len(words) or words[i]!='bakumo':_fail('task frame')
 i+=1
 if i>=len(words) or words[i] not in ACTIONS:_fail('action')
 action=ACTIONS[words[i]]
 resource,i=entity(words,i+1,resource=True)
 if words[i:]!=['tesavo','devora']:_fail('trailing task')
 if words[1]=='domera' and role!='mi':_fail('reservation role')
 return ('act',REPORTS[words[1]],'mi',role,action,resource)

def parse(text):
 words=lex(text)
 if len(words)<5 or words[0]!='mi' or words[-1]!='devora':_fail('outer frame')
 if words[1]==Q:
  source,i=entity(words,2)
  inside,i=frame(words,i)
  if words[i:]!=['devora']:_fail('after quote')
  return ('quote','mi',source,act(inside),'unverified_attribution',False)
 if words[1] in R:
  left,i=frame(words,2)
  right,i=frame(words,i)
  if words[i:]!=['devora']:_fail('after relation')
  return ('relation','mi',R[words[1]],act(left),act(right),'speaker_supplied',False)
 raise OracleUnsupported('outside oracle subset')
