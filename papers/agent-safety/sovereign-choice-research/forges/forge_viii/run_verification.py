"""Reproduce Forge VIII, unpacking its nested lineage into a temporary directory."""
from __future__ import annotations
import hashlib,json,re,shutil,subprocess,sys,tempfile,zipfile
from pathlib import Path
root=Path(__file__).resolve().parent

def execute(args,cwd=root,timeout=120):
    p=subprocess.run(args,cwd=cwd,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=timeout)
    result={'return_code':p.returncode,'ok':p.returncode==0,'combined_output_tail':(p.stdout+p.stderr)[-1200:]}
    numbers=re.findall(r'Ran (\d+) tests? in',p.stdout+p.stderr)
    result['tests']=int(numbers[-1]) if numbers else 0
    return result,p

def verify():
    new,testproc=execute([sys.executable,'-m','unittest','discover','-s','tests','-v'])
    raw=json.loads((root/'results'/'benchmark.json').read_text())
    current=subprocess.run([sys.executable,'src/sovereignty_surface.py'],cwd=root,check=True,capture_output=True,text=True)
    fixture_equal=raw==json.loads(current.stdout)
    previous=json.loads((root/'results'/'preference_revision.json').read_text())
    traj=subprocess.run([sys.executable,'src/trajectory.py'],cwd=root,check=True,capture_output=True,text=True)
    trajectory_equal=previous==json.loads(traj.stdout)
    ui=(root/'prototype'/'sovereignty_surface_lab.html').read_text(encoding='utf-8')
    offline=not any(key in ui for key in ['fetch(','XMLHttpRequest','http://','https://','<script src=','<link rel="stylesheet" href='])
    scripts_valid=None
    js_python_parity=None
    if shutil.which('node'):
        with tempfile.TemporaryDirectory() as tmp:
            script=re.search(r'<script>(.*?)</script>',ui,re.S).group(1)
            js=Path(tmp)/'ui.js';js.write_text(script,encoding='utf-8')
            syntax,_=execute(['node','--check',str(js)])
            scripts_valid=syntax['ok']
        parity,_=execute(['node','results/ui_parity_check.cjs'])
        js_python_parity=parity['ok']
    with tempfile.TemporaryDirectory() as tmp:
        zpath=root/'lineage'/'FORGE_VII_COMPLETE.zip'
        with zipfile.ZipFile(zpath) as z:
            if z.testzip() is not None:raise ValueError('broken lineage archive')
            z.extractall(tmp)
        upstream=Path(tmp)/'sovereign_choice_forge_vii'
        historical,runproc=execute([sys.executable,'run_verification.py'],cwd=upstream,timeout=240)
        try:
            h=json.loads(runproc.stdout)
            historical['tests']=int(h['combined_tests'])
            historical['baseline_parity']=bool(h['baseline_parity'])
            historical['source_integrity']=bool(h['lineage']['source_integrity'])
            historical['all_passed']=bool(h['all_passed'])
        except Exception as exc:
            historical['parse_error']=str(exc)
    hashes={}
    if (root/'MANIFEST_SHA256.json').exists():
        manifest=json.loads((root/'MANIFEST_SHA256.json').read_text())
        for name,expected in manifest.items():
            hashes[name]=hashlib.sha256((root/name).read_bytes()).hexdigest()==expected
    passed=all([new['ok'],new['tests']==32,fixture_equal,trajectory_equal,offline,
                scripts_valid is not False,js_python_parity is not False,historical['ok'],historical.get('tests')==110,
                historical.get('baseline_parity'),historical.get('source_integrity'),
                historical.get('all_passed'),all(hashes.values())])
    report={'schema':'lycheetah.forge-viii.verification.v1','status':'SYNTHETIC_LOCAL_NOT_DEPLOYED',
            'all_passed':passed,'new_tests':new['tests'],'prior_tests':historical.get('tests',0),
            'combined_tests':new['tests']+historical.get('tests',0),
            'fixture_equal':fixture_equal,'trajectory_equal':trajectory_equal,
            'matched_usage_pairs':raw['matched_usage_pairs'],
            'different_surface_verdicts':raw['different_surface_verdicts'],
            'negative_control_pairs':raw['pairs']-raw['different_surface_verdicts'],
            'ui_offline':offline,'ui_js_syntax':scripts_valid,'js_python_parity':js_python_parity,
            'sha256_manifest_verified':all(hashes.values()),
            'historical_tests':historical,'local_tests':new,
            'limits':['All graph edges and preferences are fictional fixtures.',
                      'No study with real people, model outputs, or deployed tools.',
                      'No individual free-will measure or clinical conclusion.',
                      'No demonstrated advantage over a strong conventional baseline.']}
    print(json.dumps(report,indent=2,ensure_ascii=False))
    if not passed:raise SystemExit(1)
    return report

if __name__=='__main__':verify()
