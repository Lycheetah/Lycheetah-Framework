"""Cycle23: post-crash, per-file observation evidence, anchored with keyed chain.

This is NOT publisher-synchronous commit evidence. Assumes publisher quiescence,
trusted local observer, separately protected keys and witness state.
"""
import os,json,hmac,hashlib,base64,datetime
from pathlib import Path
from authjournal15 import canon,digest,syncdir
from authority20 import build_binding,verify_original_grant,file_observation,Refusal
from witness17 import save_anchor,read_anchor,Denied
from demo_cycle12 import create_case
import cycle13

class EvidenceError(Exception):pass

def _mac(key,p):return hmac.new(key,canon(p),hashlib.sha256).hexdigest()

def read_events(path,key,binding):
    p=Path(path)
    if not p.exists():return []
    raw=p.read_bytes()
    if len(raw)>1000000 or not raw.endswith(b'\n'):raise EvidenceError('bad or partial event stream')
    out=[];prev='0'*64
    for line in raw.splitlines():
        try:r=json.loads(line);body=r['body'];tag=r['mac']
        except Exception as e:raise EvidenceError('malformed event') from e
        if set(r)!={'body','mac'} or set(body)!={'sequence','previous','binding','relative','observation'}:raise EvidenceError('record shape')
        if type(body['sequence']) is not int or body['sequence']!=len(out) or body['previous']!=prev or body['binding']!=digest(binding):raise EvidenceError('record chain')
        if body['relative'] not in binding['expected'] or body['observation'] not in ('MATCH','ABSENT','MISMATCH','UNSAFE_TYPE','UNSAFE_PATH'):raise EvidenceError('invalid observation')
        if not hmac.compare_digest(tag,_mac(key,body)):raise EvidenceError('record authentication')
        prev=digest(r);out.append(body)
    return out

def observe_and_append(path,key,binding,root,relative):
    path=Path(path)
    if relative not in binding['expected']:raise EvidenceError('unapproved file')
    events=read_events(path,key,binding)
    if relative in {e['relative'] for e in events}:raise EvidenceError('duplicate per-file evidence')
    observation=file_observation(root,relative,binding['expected'][relative])
    prev='0'*64 if not events else digest(json.loads(path.read_bytes().splitlines()[-1]))
    body={'sequence':len(events),'previous':prev,'binding':digest(binding),'relative':relative,'observation':observation}
    record={'body':body,'mac':_mac(key,body)}
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_APPEND|os.O_NOFOLLOW,0o600)
    try:
        line=canon(record)+b'\n'
        while line:line=line[os.write(fd,line):]
        os.fsync(fd)
    finally:os.close(fd)
    syncdir(path.parent)
    return body

def witness_action(path,binding,plan,grant,trusted_keys,journal_key,state,witness_key,action='ANCHOR'):
    verify_original_grant(plan,grant,trusted_keys,binding,now=datetime.datetime.now(datetime.timezone.utc))
    events=read_events(path,journal_key,binding)
    if not events:raise EvidenceError('no observations')
    records=Path(path).read_bytes().splitlines()
    head={'plan':digest(binding),'nonce':grant['grant']['nonce'],'count':len(events),'last_hash':digest(json.loads(records[-1]))}
    previous=read_anchor(state,witness_key)
    if previous:
        if previous['plan']!=head['plan'] or previous['nonce']!=head['nonce']:raise EvidenceError('different operation')
        if previous['count']>head['count']:return 'ROLLBACK_DETECTED'
        if previous['count'] and digest(json.loads(records[previous['count']-1]))!=previous['last_hash']:return 'FORK_DETECTED'
    if action=='CHECK':return 'MATCH' if previous==head else 'UNANCHORED_TAIL' if previous else 'NO_ANCHOR'
    if action!='ANCHOR':raise EvidenceError('unknown action')
    if previous!=head:save_anchor(state,witness_key,head)
    return 'ANCHORED'

def experiment(base,fault='publisher_after_first_commit'):
    base=Path(base);base.parent.chmod(0o755);base.mkdir(parents=True,exist_ok=False)
    jail,data,plan,grant,pub=create_case(base);binding=build_binding(plan,grant)
    evidence_dir=base/'evidence';evidence_dir.mkdir()
    checkpoint=base/'file_witness';checkpoint.mkdir(mode=0o700)
    jk,wk=os.urandom(32),os.urandom(32)
    result=cycle13.execute(plan,grant,pub,base/'ledger.db',jail,fault=fault)
    events_path=evidence_dir/'per_file.jsonl'
    observations=[]
    for relative in binding['expected']:
        observations.append(observe_and_append(events_path,jk,binding,jail/'published',relative))
    anchored=witness_action(events_path,binding,plan,grant,pub,jk,checkpoint,wk)
    return {'execution':result['status'],'observations':{o['relative']:o['observation'] for o in observations},'witness':anchored,'check':witness_action(events_path,binding,plan,grant,pub,jk,checkpoint,wk,'CHECK'),'auto_retry':False,'evidence_type':'POST_CRASH_OBSERVATION_NOT_COMMIT_ATTESTATION'}
if __name__=='__main__':
    import tempfile
    with tempfile.TemporaryDirectory(prefix='c23-') as tmp:print(json.dumps(experiment(Path(tmp)/'case'),indent=2))
