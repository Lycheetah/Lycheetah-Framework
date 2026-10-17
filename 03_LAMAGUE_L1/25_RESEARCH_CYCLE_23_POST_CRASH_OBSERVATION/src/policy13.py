"""Conventional Python + optional direct OPA comparison, equal input and gates."""
import copy,json,shutil,subprocess,tempfile
from pathlib import Path

BASE={'requested_outcome':'COPY_SELECTED_FILES','source_effect':'PRESERVE',
 'destination_effect':'CREATE_ONLY_IF_ABSENT','overwrite_policy':'FORBID',
 'source_deletion_policy':'FORBID','plan_integrity_verified':True,
 'signed_grant_verified':True,'grant_nonce_reserved':True,
 'worker':{'host_euid':65534},'publisher':{'host_euid':65533}}
for role in ('worker','publisher'):
    BASE[role].update({key:True for key in ('cap_eff_zero','no_new_privs','root_fd_matches',
                              'namespace_fd_proof','userns_diff','mountns_diff',
                              'netns_diff','uid_map_single_host_uid')})
    BASE[role]['seccomp_mode']=2

def decision(d):
    if not isinstance(d,dict):return False
    for key,value in BASE.items():
        if key in ('worker','publisher'):continue
        got=d.get(key)
        if (type(got) is not type(value)) or got!=value:return False
    for role,expected in (('worker',65534),('publisher',65533)):
        v=d.get(role)
        if not isinstance(v,dict) or v.get('host_euid')!=expected:return False
        if any(v.get(k) is not True for k in ('cap_eff_zero','no_new_privs','root_fd_matches',
                             'namespace_fd_proof','userns_diff','mountns_diff',
                             'netns_diff','uid_map_single_host_uid')):return False
        if v.get('seccomp_mode')!=2:return False
    return True

def cases():
    items=[{'id':'valid','input':copy.deepcopy(BASE),'expected':True}]
    for field,datum in BASE.items():
        if isinstance(datum,dict):
            for key,value in datum.items():
                for kind in ('wrong','missing'):
                    v=copy.deepcopy(BASE)
                    if kind=='missing':del v[field][key]
                    else:v[field][key]=False if isinstance(value,bool) else 0 if isinstance(value,int) else 'BAD'
                    items.append({'id':f'{kind}_{field}.{key}','input':v,'expected':False})
        else:
            for kind in ('wrong','missing'):
                v=copy.deepcopy(BASE)
                if kind=='missing':del v[field]
                else:v[field]=False if isinstance(datum,bool) else 'BAD'
                items.append({'id':f'{kind}_{field}','input':v,'expected':False})
    # All false/missing variants are conventionally denied; nothing LAMAGUE-specific here.
    for field in ('plan_integrity_verified','signed_grant_verified','grant_nonce_reserved'):
        v=copy.deepcopy(BASE);v[field]=1
        items.append({'id':'type_confusion_'+field,'input':v,'expected':False})
    return items

def run():
    fixtures=cases()
    own=[{'id':c['id'],'expected':c['expected'],'python_allow':decision(c['input'])} for c in fixtures]
    assert all(x['expected']==x['python_allow'] for x in own)
    report={'count':len(own),'python_passed':len(own),'opa_status':'NOT_RUN_BINARY_UNAVAILABLE',
            'opa_result_count':0,'opa_version':None,
            'scope':'structured-policy parity, not equivalent complete system security'}
    exe=shutil.which('opa')
    if exe:
        policy=Path(__file__).resolve().parents[1]/'policy/namespace_boundary.rego'
        v=subprocess.run([exe,'version'],capture_output=True,text=True,check=True,timeout=10)
        subprocess.run([exe,'check',str(policy)],capture_output=True,text=True,check=True,timeout=10)
        with tempfile.TemporaryDirectory() as tmp:
            inp=Path(tmp)/'input.json'
            for c in fixtures:
                inp.write_text(json.dumps(c['input']))
                r=subprocess.run([exe,'eval','--format','raw','--data',str(policy),
                                  '--input',str(inp),'data.cycle13.namespace_boundary.allow'],
                                 capture_output=True,text=True,check=True,timeout=10)
                if r.stdout.strip() not in ('true','false'):raise RuntimeError('not boolean: '+r.stdout)
                if (r.stdout.strip()=='true')!=c['expected']:raise AssertionError(c['id'])
        report.update(opa_status='OPA_EXECUTED_ALL_MATCH',opa_result_count=len(fixtures),
                      opa_version=v.stdout.splitlines()[0])
    return report
if __name__=='__main__':print(json.dumps(run(),indent=2))
