"""Re-run the published earlier cycles, without rewriting them or hiding native failures."""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
import zipfile

EXPECTED_SYNTHETIC={1:20,2:29,3:50,4:38,5:42,6:59,7:47}
NATIVE_CANDIDATE_TESTS={4:{'test_framework_bridge_candidate'},5:{'test_real_framework_bridge_candidate'}}

def run(folder,modules):
    cp=subprocess.run([sys.executable,'-m','unittest','-q',*modules],cwd=folder,capture_output=True,text=True,timeout=120)
    match=re.search(r'Ran (\d+) tests?',cp.stderr)
    return {'exit_code':cp.returncode,'test_methods':int(match.group(1)) if match else None,
            'tail':cp.stderr[-360:]}

def main(zip_path):
    report=[]
    with tempfile.TemporaryDirectory() as root:
        with zipfile.ZipFile(zip_path) as z:
            z.extractall(root)
        for idx,expected in EXPECTED_SYNTHETIC.items():
            folder=Path(root)/f'earned_trust_cycle_{idx:03d}'
            tests=sorted(p.stem for p in folder.glob('test_*.py'))
            default=run(folder,tests)
            selected=[t for t in tests if t not in NATIVE_CANDIDATE_TESTS.get(idx,set())]
            bounded=run(folder,selected) if idx in NATIVE_CANDIDATE_TESTS else default
            if bounded['exit_code']!=0 or bounded['test_methods']!=expected:
                raise RuntimeError(f'Cycle {idx} unexpected synthetic result: {bounded}')
            report.append({'cycle':idx,'default_selection':default,
                           'synthetic_selected':bounded,
                           'real_framework_test_modules_excluded':sorted(NATIVE_CANDIDATE_TESTS.get(idx,set()))})
    totals=sum(r['synthetic_selected']['test_methods'] for r in report)
    output={'historical_zip':Path(zip_path).name,'cycles_checked':7,
            'selected_synthetic_tests_passed':totals,
            'default_modules_with_import_errors':[4,5],
            'real_framework_integration':'NOT_EXECUTED',
            'raw':report}
    Path(__file__).with_name('historical_recheck_results.json').write_text(json.dumps(output,indent=2)+'\n')
    print(f'Historical synthetic checks: {totals}/{totals} passed')
    print('Default selection: C004 and C005 fail on missing native lycheetah package; see JSON')

if __name__=='__main__':
    if len(sys.argv)!=2:raise SystemExit('usage: run_historical_recheck.py prior_7_cycles.zip')
    main(sys.argv[1])
