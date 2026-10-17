#!/usr/bin/env python3
"""Generate frozen policy inputs; execute true OPA only when installed.
If OPA is absent, never mislabel Python result as a Rego execution.
"""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from isolated_controller import conventional_policy_decision

BASE={'requested_outcome':'COPY_SELECTED_FILES','source_effect':'PRESERVE',
'destination_effect':'CREATE_ONLY_IF_ABSENT','overwrite_policy':'FORBID',
'source_deletion_policy':'FORBID','plan_digest_valid':True,
'approval_signature_valid':True,'approval_nonce_fresh':True,
'root_identity_valid':True,'worker_uid':65534,'worker_chrooted':True,
'worker_privileged_fds':False}
EDITS={'move':('requested_outcome','MOVE'), 'delete_source':('source_effect','DELETE'),
'overwrite_destination':('destination_effect','OVERWRITE'),
'overwrite_authorized':('overwrite_policy','ALLOW'), 'delete_authorized':('source_deletion_policy','ALLOW'),
'invalid_plan':('plan_digest_valid',False),'bad_signature':('approval_signature_valid',False),
'replayed_nonce':('approval_nonce_fresh',False),'root_mismatch':('root_identity_valid',False),
'root_worker':('worker_uid',0),'no_chroot':('worker_chrooted',False),
'inherited_privileged_fd':('worker_privileged_fds',True)}

def cases():
    res=[{'id':'valid','input':BASE.copy(),'expected':True}]
    for name,(key,bad) in EDITS.items():
        c=BASE.copy();c[key]=bad
        res.append({'id':name,'input':c,'expected':False})
    for key in BASE:
        c=BASE.copy();del c[key]
        res.append({'id':'missing_'+key,'input':c,'expected':False})
    return res

def run():
    fixtures=cases()
    local=[{'id':c['id'],'expected':c['expected'],
             'python_policy':conventional_policy_decision(c['input'])} for c in fixtures]
    assert all(r['expected']==r['python_policy'] for r in local)
    opa=shutil.which('opa');checked=None; version=None
    if opa:
        policy=Path(__file__).resolve().parents[1]/'policy'/'effect_gate.rego'
        version=subprocess.run([opa,'version'],text=True,capture_output=True,timeout=10)
        version=version.stdout.splitlines()[0] if version.returncode==0 and version.stdout else 'UNKNOWN'
        check=subprocess.run([opa,'check',str(policy)],text=True,capture_output=True,timeout=15)
        if check.returncode!=0:raise RuntimeError('OPA policy failed check: '+check.stderr)
        checked=[]
        with tempfile.TemporaryDirectory() as td:
            inp=Path(td)/'case.json'
            for fixture in fixtures:
                inp.write_text(json.dumps(fixture['input']))
                p=subprocess.run([opa,'eval','--format=raw','--data',str(policy),'--input',str(inp),
                       'data.cycle11.effect_gate.allow'],text=True,capture_output=True,timeout=15)
                if p.returncode!=0:raise RuntimeError('OPA error '+p.stderr)
                val=p.stdout.strip()
                if val not in ('true','false'):raise RuntimeError('unexpected OPA output '+val)
                actual=val=='true'
                if actual!=fixture['expected']:raise AssertionError('OPA disagreement on '+fixture['id'])
                checked.append({'id':fixture['id'],'opa_allow':actual})
    return {'fixture_count':len(fixtures),'fixture_inputs':fixtures,
            'python_policy_comparisons':local,'python_policy_all_match':True,
            'opa_binary_available':opa is not None,
            'opa_version':version,'opa_executed_cases':checked,
            'opa_status':'EXECUTED_AND_MATCHED' if opa else 'NOT_EXECUTED_NO_OPA_BINARY',
            'notes':'Python code is an independent literal policy comparator, NOT Rego. True Rego evaluation requires installed OPA.'}

if __name__=='__main__':print(json.dumps(run(),indent=2))
