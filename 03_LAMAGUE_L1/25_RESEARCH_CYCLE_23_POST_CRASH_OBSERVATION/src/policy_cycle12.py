#!/usr/bin/env python3
"""Frozen role-boundary Rego fixtures. OPA is run ONLY if installed."""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

BASE={
 'requested_outcome':'COPY_SELECTED_FILES',
 'source_effect':'PRESERVE',
 'destination_effect':'CREATE_ONLY_IF_ABSENT',
 'overwrite_policy':'FORBID',
 'source_deletion_policy':'FORBID',
 'plan_integrity_verified':True,
 'signed_grant_verified':True,
 'grant_nonce_reserved':True,
 'worker':{'euid':65534,'cap_eff_zero':True,'no_new_privs':True,'seccomp_mode':2,'root_fd_matches':True},
 'publisher':{'euid':65533,'cap_eff_zero':True,'no_new_privs':True,'seccomp_mode':2,'root_fd_matches':True},
}

def decision(v):
    """Conventional standalone Python boolean policy, not a Rego interpreter."""
    return (v.get('requested_outcome')=='COPY_SELECTED_FILES'
        and v.get('source_effect')=='PRESERVE'
        and v.get('destination_effect')=='CREATE_ONLY_IF_ABSENT'
        and v.get('overwrite_policy')=='FORBID'
        and v.get('source_deletion_policy')=='FORBID'
        and all(v.get(k) is True for k in ('plan_integrity_verified','signed_grant_verified','grant_nonce_reserved'))
        and isinstance(v.get('worker'),dict) and isinstance(v.get('publisher'),dict)
        and all(v[role].get('euid')==uid and v[role].get('cap_eff_zero') is True
          and v[role].get('no_new_privs') is True and v[role].get('seccomp_mode')==2
          and v[role].get('root_fd_matches') is True for role,uid in [('worker',65534),('publisher',65533)]))

def fixtures():
    import copy
    a=[{'id':'valid','input':copy.deepcopy(BASE),'expected':True}]
    for field,bad in [('requested_outcome','MOVE'),('source_effect','DELETE'),
      ('destination_effect','OVERWRITE'),('overwrite_policy','ALLOW'),
      ('source_deletion_policy','ALLOW'),('plan_integrity_verified',False),
      ('signed_grant_verified',False),('grant_nonce_reserved',False),
      ('worker.euid',0),('worker.cap_eff_zero',False),('worker.no_new_privs',False),
      ('worker.seccomp_mode',0),('worker.root_fd_matches',False),
      ('publisher.euid',0),('publisher.cap_eff_zero',False),('publisher.no_new_privs',False),
      ('publisher.seccomp_mode',0),('publisher.root_fd_matches',False)]:
        for variant in ('invalid','missing'):
            val=copy.deepcopy(BASE)
            if '.' in field:
                role,k=field.split('.')
                if variant=='missing':del val[role][k]
                else:val[role][k]=bad
            else:
                if variant=='missing':del val[field]
                else:val[field]=bad
            a.append({'id':variant+'_'+field,'input':val,'expected':False})
    return a

def run():
    cases=fixtures()
    py=[{'id':c['id'],'expected':c['expected'],'decision':decision(c['input'])} for c in cases]
    assert all(x['expected']==x['decision'] for x in py)
    opa=shutil.which('opa')
    out={'fixtures':len(cases),'python_results':py,'python_all_match':True,
         'opa_status':'NOT_EXECUTED_BINARY_UNAVAILABLE','opa_version':None,'opa_results':None,
         'source':'Conventional structured-data gate; no LAMAGUE-specific decision advantage tested'}
    if opa:
        policy=Path(__file__).resolve().parents[1]/'policy'/'role_boundary.rego'
        vers=subprocess.run([opa,'version'],text=True,capture_output=True,timeout=10,check=True)
        subprocess.run([opa,'check',str(policy)],text=True,capture_output=True,timeout=10,check=True)
        verdict=[]
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'input.json'
            for c in cases:
                path.write_text(json.dumps(c['input']))
                p=subprocess.run([opa,'eval','--format','raw','--data',str(policy),
                    '--input',str(path),'data.cycle12.role_boundary.allow'],
                    text=True,capture_output=True,timeout=15,check=True)
                result=p.stdout.strip()
                if result not in ('true','false'):raise RuntimeError('OPA result not boolean: '+result)
                assert (result=='true')==c['expected'],c['id']
                verdict.append({'id':c['id'],'opa_allow':result=='true'})
        out['opa_status']='EXECUTED_AND_MATCHED'
        out['opa_results']=verdict
        out['opa_version']=vers.stdout.splitlines()[0]
    return out
if __name__=='__main__':print(json.dumps(run(),indent=2))
