"""Reproducible local suites; extracts historical lineage into a temporary directory.

Requires cryptography. Does not call any network API, email tool or GitHub write.
"""
from __future__ import annotations
import os,sys,subprocess,tempfile,zipfile,hashlib,json,datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parent
MIRROR=ROOT/'upstream_mirror'/'papers'/'agent-safety'/'frontier-controls'
SOURCES={
    'research_support.py':'0f623b6614be03a2f7bf65f2a5ea3fe1b12e51e9',
    '01_commit_time_authority_v0_7/commit_fence.py':'0af8050808569a098e11fb72a9f7d6c4c15044bb',
}

def run_unittests(cwd:Path, *,environment=None):
    env=os.environ.copy()
    env['PYTHONDONTWRITEBYTECODE']='1'
    env['PYTHONWARNINGS']='ignore::ResourceWarning'
    env.update(environment or {})
    proc=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],
                        cwd=cwd,env=env,encoding='utf-8',errors='replace',
                        capture_output=True,timeout=60)
    import re
    log=proc.stdout+proc.stderr
    m=re.search(r'Ran (\d+) tests? in',log)
    tests=int(m.group(1)) if m else None
    skipped=re.search(r'skipped=(\d+)',log)
    return {'tests':tests,'exit_code':proc.returncode,
            'skipped':int(skipped.group(1)) if skipped else 0,
            'tail':log[-650:]}

def verify_source_hashes():
    res={}
    for rel,expected in SOURCES.items():
        data=(MIRROR/rel).read_bytes()
        actual=hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()
        res[rel]={'expected_git_blob':expected,'actual_git_blob':actual,'matches':expected==actual}
        if actual!=expected:raise RuntimeError(f'upstream copy mismatch: {rel}')
    return res

def main():
    results={'schema':'lycheetah.forge-vi.verification.v1','date_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
             'source_integrity':verify_source_hashes(),
             'forge_vi':run_unittests(ROOT)}
    with tempfile.TemporaryDirectory() as temp:
        work=Path(temp)
        with zipfile.ZipFile(ROOT/'lineage'/'FORGE_V_COMPLETE.zip') as zv: zv.extractall(work)
        v=work/'sovereign_choice_forge_v'
        results['forge_v_regression']=run_unittests(v)
        with zipfile.ZipFile(v/'lineage'/'FORGE_IV_COMPLETE.zip') as zi:zi.extractall(work)
        iv=work/'sovereign_choice_forge_iv'
        results['forge_iv_regression']=run_unittests(iv,environment={'LYCHEETAH_REPO_ROOT':str(ROOT/'upstream_mirror')})
    suites=[results[x] for x in ['forge_vi','forge_v_regression','forge_iv_regression']]
    results['total_tests']=sum(r['tests'] or 0 for r in suites)
    results['all_passed']=all(r['exit_code']==0 and r['skipped']==0 and r['tests'] is not None for r in suites)
    results['external_effects']=False
    results['human_authentication_proven']=False
    results['production_security_claim']=False
    print(json.dumps(results,indent=2))
    if not results['all_passed']:sys.exit(1)
if __name__=='__main__':main()
