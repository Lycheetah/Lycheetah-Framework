"""SXP-L v0.9 reference permission gate (NO external execution).

Trusted host-supplied *signed capability events*, not language expressions,
are the only possible grant authority. Exact action/resource matching. Fail
closed on malformed or ambiguous attestations. HMAC here is for reproducible
research fixtures, NOT production identity, storage, or key management.
"""
from __future__ import annotations
import hashlib
import hmac
import json
import re
from typing import Any

ID = re.compile(r'[a-z][a-z0-9_]{0,39}\Z')
OPERATIONS = frozenset({'send_email','read_file','delete_file','schedule_event','publish_post'})
HIGH_IMPACT = frozenset({'send_email','delete_file','publish_post','schedule_event'})
BASE = frozenset({'version','kind','grant_id','issuer','grantee','operation','resource','not_before'})
GRANT_FIELDS = BASE | {'expires_at','approval'}
REVOKE_FIELDS = BASE


def canonical(item: dict) -> bytes:
    return json.dumps(item,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode('ascii')


def _valid_id(value):
    return isinstance(value,str) and ID.fullmatch(value) is not None


def _valid_event_shape(event):
    if not isinstance(event,dict) or set(event)!={'claims','mac'} or not isinstance(event['claims'],dict):
        return False
    c=event['claims']
    fields=GRANT_FIELDS if c.get('kind')=='grant' else REVOKE_FIELDS if c.get('kind')=='revoke' else set()
    if set(c)!=fields:return False
    if type(c.get('version')) is not int or c['version']!=1:return False
    if not all(_valid_id(c.get(k)) for k in ('grant_id','issuer','grantee','resource')):return False
    if not isinstance(c.get('operation'),str) or c['operation'] not in OPERATIONS:return False
    if type(c.get('not_before')) is not int or c['not_before']<0:return False
    if c['kind']=='grant':
        if type(c.get('expires_at')) is not int or c['expires_at']<=c['not_before']:return False
        # A short-lived, explicitly approved grant required for high-impact actions.
        if c['expires_at']-c['not_before']>86400:return False
        if not isinstance(c['approval'],str) or c['approval'] not in ('ordinary','human_confirmed'):return False
        if c['operation'] in HIGH_IMPACT and c['approval']!='human_confirmed':return False
    mac=event['mac']
    return isinstance(mac,str) and re.fullmatch(r'[a-f0-9]{64}',mac) is not None


def sign_fixture(claims: dict,key:bytes)->dict:
    """FOR TESTS ONLY: a trusted host is presumed to control the private key."""
    if not isinstance(key,bytes) or len(key)<16:
        raise ValueError('test key must have at least 16 bytes')
    temp={'claims':claims.copy(),'mac':'0'*64}
    if not _valid_event_shape(temp):raise ValueError('invalid event structure')
    return {'claims':claims.copy(),'mac':hmac.new(key,canonical(claims),hashlib.sha256).hexdigest()}


def _verify(event,keys,ownership)->bool:
    if not _valid_event_shape(event):return False
    c=event['claims'];key=keys.get(c['issuer'])
    if not isinstance(key,bytes) or len(key)<16:return False
    resources=ownership.get(c['issuer'],set())
    if not isinstance(resources,(set,frozenset,list,tuple)) or c['resource'] not in resources:return False
    expected=hmac.new(key,canonical(c),hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected,event['mac'])


def decision(request:dict,events:list, keys:dict, ownership:dict, *, now:int)->dict:
    """Deterministic reference gate. Returns a decision; NEVER calls a tool.

    Request and now must be supplied by trusted runtime, not extracted from
    unverified SXP-L words. revocation events are durable for this evaluation;
    the caller must persist and supply the full revocation log each time.
    """
    def deny(code,detail=''):
        return {'allowed':False,'code':code,'detail':detail,'matched_grant':None}
    if (not isinstance(request,dict) or set(request)!={'grantee','operation','resource'} or
        not _valid_id(request.get('grantee')) or not _valid_id(request.get('resource')) or
        not isinstance(request.get('operation'),str) or request.get('operation') not in OPERATIONS):
        return deny('DENY_INVALID_REQUEST')
    if type(now) is not int or now<0:return deny('DENY_INVALID_TIME')
    if not isinstance(events,list) or len(events)>256:return deny('DENY_INVALID_EVIDENCE','event list')
    if not isinstance(keys,dict) or not isinstance(ownership,dict):return deny('DENY_INVALID_TRUST_CONFIG')
    # Fail closed if even one supplied purported permission event is malformed.
    if any(not _verify(e,keys,ownership) for e in events):
        return deny('DENY_UNVERIFIED_EVIDENCE')
    grants=[e['claims'] for e in events if e['claims']['kind']=='grant']
    revocations=[e['claims'] for e in events if e['claims']['kind']=='revoke']
    if len({g['grant_id'] for g in grants})!=len(grants):
        return deny('DENY_DUPLICATE_GRANT_ID')
    if len({(r['issuer'],r['grant_id']) for r in revocations})!=len(revocations):
        return deny('DENY_DUPLICATE_REVOCATION')
    for r in revocations:
        match=[g for g in grants if g['grant_id']==r['grant_id']]
        if match and any(any(g[k]!=r[k] for k in ('issuer','grantee','operation','resource')) for g in match):
            return deny('DENY_REVOCATION_SCOPE_MISMATCH')
    scoped=[g for g in grants if all(g[k]==request[k] for k in ('grantee','operation','resource'))]
    if not scoped:return deny('DENY_NO_EXACT_GRANT')
    live=[g for g in scoped if g['not_before']<=now<g['expires_at']]
    if not live:return deny('DENY_NO_LIVE_GRANT')
    for grant in live:
        revoked=any(r['grant_id']==grant['grant_id'] and
                    r['issuer']==grant['issuer'] and r['not_before']<=now
                    for r in revocations)
        if not revoked:
            return {'allowed':True,'code':'ALLOW_VERIFIED_EXACT_SCOPE',
                    'detail':'Test gate: valid signed grant; no execution performed.',
                    'matched_grant':grant['grant_id']}
    return deny('DENY_REVOKED')


def grant_claims(grant_id,issuer,grantee,operation,resource,start,expiry,approval='human_confirmed'):
    return {'version':1,'kind':'grant','grant_id':grant_id,'issuer':issuer,
            'grantee':grantee,'operation':operation,'resource':resource,
            'not_before':start,'expires_at':expiry,'approval':approval}


def revoke_claims(grant:dict, at:int)->dict:
    return {k:grant[k] for k in BASE if k not in ('not_before','kind')}|{'not_before':at,'kind':'revoke'}


def receipt(req,events,result,now):
    """Content fingerprint, not a tamper-proof audit trail."""
    payload={'request':req,'events':events,'decision':result,'at':now}
    return {'decision':result, 'sha256':hashlib.sha256(b'SXP-L-v0.9-receipt\0'+canonical(payload)).hexdigest(),
            'integrity_claim':'local deterministic fingerprint only'}


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description='SXP-L offline fixture authorization demo, NO tool execution')
    p.add_argument('--demo',action='store_true');a=p.parse_args()
    if a.demo:
        key=b'local-fixture-key-not-for-production'
        g=grant_claims('granta','owner','agena','send_email','darafa',100,200)
        signed=sign_fixture(g,key)
        request={'grantee':'agena','operation':'send_email','resource':'darafa'}
        keys={'owner':key};ownership={'owner':{'darafa'}}
        for title,records,when in [('No evidence',[],150),('Attested grant',[signed],150),
                                    ('Expired',[signed],201),('Revoked',[signed,sign_fixture(revoke_claims(g,160),key)],170)]:
            print(title, ':', json.dumps(decision(request,records,keys,ownership,now=when)))
