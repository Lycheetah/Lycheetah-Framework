"""Rerun the self-authored unit tests of all research cycles without mutating them."""
from pathlib import Path
import json
import subprocess
import sys
import re

root=Path(__file__).resolve().parent.parent
names={
    '001':['test_earned_trust_probe'],
    '002':['test_transactional_provider','test_binding_contract'],
    '003':['test_authenticated_provider'],
    '004':['test_independent_witness','test_matched_baseline'],
    '005':['test_provenance_gate','test_baseline_consistency'],
    '006':['test_governed_registry','test_baseline_comparison'],
}
results={}
for cycle,modules in names.items():
    cwd=root/('earned_trust_cycle_'+cycle)
    cmd=[sys.executable,'-m','unittest','-q',*modules]
    try:
        p=subprocess.run(cmd,cwd=cwd,capture_output=True,text=True,timeout=45)
        raw=p.stdout+'\n'+p.stderr
        matches=re.findall(r'Ran (\d+) tests?',raw)
        tests=int(matches[-1]) if matches else None
        results[cycle]={"return_code":p.returncode,"tests":tests,"passed":p.returncode==0,
                        "tail":raw[-1500:]}
    except Exception as exc:
        results[cycle]={"passed":False,"error":type(exc).__name__+': '+str(exc)}
print(json.dumps(results,indent=2))
if any(not row.get('passed') for row in results.values()):
    raise SystemExit(1)
