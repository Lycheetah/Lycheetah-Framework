"""Clean-room Forge VII validation, automatically rerunning preserved Forge VI lineage.

No external effects or network calls. Requires python3 and cryptography for the
already-existing historical Forge VI suite. A missing requirement fails visibly.
"""
from __future__ import annotations
import hashlib, json, re, subprocess, sys, tempfile, zipfile, os
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def run(cmd,cwd=None,env=None,timeout=90):
    p=subprocess.run(cmd,cwd=cwd or ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                     timeout=timeout, text=True,encoding='utf-8',errors='replace')
    num=re.findall(r'Ran (\d+) tests? in',p.stdout)
    return {'success':p.returncode==0,'exit_code':p.returncode,'test_count':int(num[-1]) if num else 0,
            'output_tail':p.stdout[-1200:], '_full_text':p.stdout}

def verify():
    local=run([sys.executable,'-m','unittest','discover','-s','tests','-v'])
    # Directly compare displayed example data against benchmark result JSON.
    env=dict(os.environ, PYTHONPATH=str(ROOT/'src'), PYTHONDONTWRITEBYTECODE='1')
    make=run([sys.executable,'src/self_displacement.py'],env=env)
    data=json.loads(subprocess.run([sys.executable,'src/self_displacement.py'], cwd=ROOT,
                env=env,check=True,capture_output=True,text=True).stdout)
    expected=json.loads((ROOT/'results'/'fixture_results.json').read_text())
    fixture_match=data==expected
    archive=ROOT/'lineage'/'FORGE_VI_COMPLETE.zip'
    lineage={'success':False,'test_count':0,'output_tail':''}
    with tempfile.TemporaryDirectory() as tmp:
        with zipfile.ZipFile(archive) as z:
            if z.testzip() is not None:raise ValueError('corrupt lineage zip')
            z.extractall(tmp)
        historical=Path(tmp)/'sovereign_choice_forge_vi'
        if not (historical/'run_verification.py').exists():raise FileNotFoundError('Forge VI root missing')
        hist=run([sys.executable,'run_verification.py'],cwd=historical,timeout=120)
        lineage={'success':hist['success'],'test_count':0,'output_tail':hist['output_tail']}
        try:
            m=re.search(r'\{\s*"schema"\s*:\s*"lycheetah.forge-vi.verification.v1".*',hist['_full_text'],flags=re.S)
            if m:
                h=json.loads(m.group(0));lineage['test_count']=h.get('total_tests',0)
                lineage['source_integrity']=all(x['matches'] for x in h.get('source_integrity',{}).values())
        except Exception:pass
    html=(ROOT/'prototype'/'self_displacement_lab.html').read_text(encoding='utf-8')
    html_checks={'contains_18_fixtures':html.count('"prompt":')==18,
                 'scripted_only': 'SCRIPTED FIXTURE ONLY' in html,
                 'offline': not any(x in html for x in ('https://','http://','fetch(','XMLHttpRequest')),
                 'policy_rules_present':all(x in html for x in ('exit_everywhere','retention','sovereign','standard'))}
    manifest=ROOT/'MANIFEST_SHA256.json'
    hash_results={}
    if manifest.exists():
        index=json.loads(manifest.read_text())
        for rel,h in index.items():
            blob=(ROOT/rel).read_bytes();hash_results[rel]=hashlib.sha256(blob).hexdigest()==h
    good=all([local['success'],make['success'],fixture_match,lineage['success'],lineage['test_count']==87,
              lineage.get('source_integrity',False), all(html_checks.values()),all(hash_results.values())])
    result={'status':'LOCAL_RESEARCH_NOT_DEPLOYED','all_passed':good,
            'forge_vii_tests':local['test_count'],'prior_lineage_tests':lineage['test_count'],
            'combined_tests':local['test_count']+lineage['test_count'],
            'baseline_parity':data['policies']['standard']['acceptable']==data['policies']['sovereign']['acceptable']==18,
            'fixture_results':data['policies'],'fixture_snapshot_matches':fixture_match,
            'lineage':lineage,'html_checks':html_checks,'manifest_verified':all(hash_results.values()),
            'limitations':['Scripted policy fixtures, not AI model behavior','No real user participants',
                           'No production security or external authorization guarantee']}
    print(json.dumps(result,indent=2,ensure_ascii=False))
    if not good:sys.exit(1)
if __name__=='__main__':verify()
