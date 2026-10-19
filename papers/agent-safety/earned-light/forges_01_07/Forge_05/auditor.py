"""Independent verifier: requires a trusted pre-export snapshot / task oracle."""
from __future__ import annotations
import hashlib, json, subprocess, sys, tempfile
from pathlib import Path
from fixture import oracle, source, digest
from exporter import export_bundle

SECTION_FILES={k:k+'.json' for k in ('documents','policies','decisions','dependencies')}

def local_manifest_status(folder):
    folder=Path(folder); manifest_path=folder/'manifest.json'
    if not manifest_path.is_file(): return 'none'
    try:
        manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
        files=manifest['files']
        if set(files)!={'documents.json','policies.json','decisions.json','dependencies.json','state.json'}:
            return 'invalid'
        for filename,v in files.items():
            raw=(folder/filename).read_bytes()
            if hashlib.sha256(raw).hexdigest()!=v['sha256']:return 'mismatch'
            data=json.loads(raw)
            if (len(data) if isinstance(data,list) else 1)!=v['records']:return 'mismatch'
        return 'match'
    except (OSError,KeyError,TypeError,ValueError,json.JSONDecodeError):return 'invalid'

def audit(folder, reference, result):
    folder=Path(folder)
    # Trusted external snapshot: not a self-generated claim from the export we are checking.
    issues=[]; total=0; matched=0
    for section,expected in reference['fingerprints'].items():
        try:
            present={r['id']:digest(r) for r in json.loads((folder/SECTION_FILES[section]).read_text(encoding='utf-8'))}
        except (OSError,TypeError,ValueError,KeyError,json.JSONDecodeError):present={}
        for rid,fingerprint in expected.items():
            total+=1
            if present.get(rid)==fingerprint:matched+=1
            else:issues.append('missing_or_modified:'+section+'/'+rid)
        for rid in set(present)-set(expected):issues.append('unexpected:'+section+'/'+rid)
    manifest=local_manifest_status(folder)
    continuity_pass=0
    output=result.get('output',{}) if result.get('ok') else {}
    for task in reference['tasks']:
        actual=(output.get('queries',{}).get(task['topic']) if task['task']=='query'
                else output.get('case_history',{}).get(task['id']))
        if actual==task['expected']: continuity_pass+=1
        else: issues.append('failed_task:'+(task.get('topic') or task.get('id')))
    rev_ok=(output.get('revision')==reference['revision'])
    if not rev_ok:issues.append('revision_mismatch')
    deps=output.get('dependencies',[])
    connector_claims_portable=bool(result.get('ok')) and all(d.get('portable') for d in deps if d.get('required_for_effects'))
    # Also verify against independent dependency reference; missing dependencies never imply readiness.
    required_ref=[did for did,dhash in reference['fingerprints']['dependencies'].items() if did=='DEPEND-CRM']
    connector_claims_portable=connector_claims_portable and all(any(d.get('id')==required for d in deps) for required in required_ref)
    if manifest in ('mismatch','invalid'):issues.append('manifest_'+manifest)
    full_continuity=(continuity_pass==len(reference['tasks']) and matched==total and rev_ok)
    # Read-only operation is only a simulated task, no real business operation is undertaken.
    return {'manifest_status':manifest,'records_verified':matched,'records_expected':total,
            'tasks_passed':continuity_pass,'tasks_expected':len(reference['tasks']),
            'reference_revision_match':rev_ok,
            'synthetic_readonly_continuity':full_continuity,
            'connector_claims_portable':connector_claims_portable and full_continuity,
            'externally_verified_effects_continuity':False,  # No live connector exercise performed.
            'issues':issues}

def run_trial(profile='portable',variant='clean',root=None):
    with tempfile.TemporaryDirectory(prefix='earned-light-exit-') if root is None else _external_root(root) as tmp:
        root=Path(tmp); source_side=root/'source_only'; transfer=root/'transfer'; target=root/'target_without_source'
        source_side.mkdir();transfer.mkdir();target.mkdir()
        ref=oracle(source())
        (source_side/'trusted_reference.json').write_text(json.dumps(ref,indent=2,sort_keys=True),encoding='utf-8')
        export_bundle(transfer,profile,variant)
        # Importer receives only transfer path, is executed with isolated Python flags and cwd.
        command=[sys.executable,'-I',str(Path(__file__).with_name('target_importer.py')),str(transfer)]
        proc=subprocess.run(command, cwd=target, capture_output=True,text=True,timeout=10,check=False)
        if proc.stdout:
            result=json.loads(proc.stdout)
        else:result={'ok':False,'error':proc.stderr[:500]}
        checked=audit(transfer,ref,result)
        return {'profile':profile,'variant':variant,'target_process_success':result.get('ok',False),**checked}

class _external_root:
    def __init__(self,where):self.where=where
    def __enter__(self):return self.where
    def __exit__(self,*args):return False

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--profile',choices=('portable','conventional','proprietary'),default='portable')
    parser.add_argument('--variant',choices=('clean','omitted_policy','omitted_decision','stale','no_provenance','dependency_loss','tamper_after_manifest','forge_manifest'),default='clean')
    args=parser.parse_args()
    print(json.dumps(run_trial(args.profile,args.variant),indent=2,sort_keys=True))
