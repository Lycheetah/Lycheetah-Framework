"""Run Forge V and restored Forge IV tests against SHA-pinned upstream source."""
from __future__ import annotations
from pathlib import Path
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import zipfile

ROOT=Path(__file__).resolve().parent
UPSTREAM=ROOT/'upstream_mirror'
SOURCES={
 'papers/agent-safety/frontier-controls/research_support.py':'0f623b6614be03a2f7bf65f2a5ea3fe1b12e51e9',
 'papers/agent-safety/frontier-controls/01_commit_time_authority_v0_7/commit_fence.py':'0af8050808569a098e11fb72a9f7d6c4c15044bb'
}

def check_blob(path):
    b=path.read_bytes()
    return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()

def suite(cwd,env):
    proc=subprocess.run([sys.executable,'-W','ignore::ResourceWarning',
        '-m','unittest','discover','-s','tests','-v'],
        cwd=cwd,env=env,text=True,capture_output=True,timeout=90)
    log=proc.stdout+'\n'+proc.stderr
    m=re.search(r'Ran (\d+) tests in',log)
    return {'tests':int(m.group(1)) if m else None,'passed':proc.returncode==0,
            'exit_code':proc.returncode,'skipped':len(re.findall(r'\.\.\. skipped',log)),
            'log':log}

def main():
    actual={p:check_blob(UPSTREAM/p) for p in SOURCES}
    if actual!=SOURCES:
        raise AssertionError(f'Upstream mirror SHA mismatch {actual!r}')
    env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'}
    v=suite(ROOT,env)
    with tempfile.TemporaryDirectory() as temp:
        with zipfile.ZipFile(ROOT/'lineage/FORGE_IV_COMPLETE.zip') as z:
            z.extractall(temp)
        old=Path(temp)/'sovereign_choice_forge_iv'
        iv=suite(old,{**env,'LYCHEETAH_REPO_ROOT':str(UPSTREAM)})
    compare=subprocess.run([sys.executable,'compare_crash_window.py'],cwd=ROOT,
            text=True,capture_output=True,timeout=40)
    result={
        'date':'2026-10-18',
        'source':'Lycheetah/Lycheetah-Framework master source files fetched via GitHub connector',
        'verified_git_blob_sha1':actual,
        'forge_v':{k:x for k,x in v.items() if k!='log'},
        'forge_iv_against_real_upstream':{k:x for k,x in iv.items() if k!='log'},
        'total_tests':(v['tests'] or 0)+(iv['tests'] or 0),
        'total_passed':v['passed'] and iv['passed'] and compare.returncode==0,
        'crash_comparison':json.loads((ROOT/'comparison_results.json').read_text()) if compare.returncode==0 else None,
        'real_external_effects':False,
        'live_human_authentication':False,
        'security_certification':False,
        'known_upstream_resource_warnings':True,
    }
    (ROOT/'verification_log.txt').write_text('=== FORGE V ===\n'+v['log']+'\n=== FORGE IV UPSTREAM ===\n'+iv['log']+'\n=== COMPARE ===\n'+compare.stdout+compare.stderr)
    (ROOT/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:w for k,w in result.items() if k not in ('crash_comparison','verified_git_blob_sha1')},indent=2))
    if not result['total_passed']:
        print(v['log'][-4000:],iv['log'][-4000:],compare.stderr, file=sys.stderr)
        raise SystemExit(1)

if __name__=='__main__':main()
