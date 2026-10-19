"""Compare against a strong conventional open-JSON baseline, not just lock-in strawman."""
import csv, json
from pathlib import Path
from auditor import run_trial

def main():
    profiles=('proprietary','conventional','portable')
    variants=('clean','omitted_policy','omitted_decision','stale','no_provenance','dependency_loss','tamper_after_manifest','forge_manifest')
    results=[run_trial(profile,variant) for variant in variants for profile in profiles]
    folder=Path(__file__).with_name('results');folder.mkdir(exist_ok=True)
    (folder/'comparisons.json').write_text(json.dumps(results,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    keys=['profile','variant','manifest_status','records_verified','records_expected','tasks_passed','tasks_expected','reference_revision_match','synthetic_readonly_continuity','connector_claims_portable','externally_verified_effects_continuity']
    with (folder/'comparisons.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows({k:r[k] for k in keys} for r in results)
    print('Ran',len(results),'deterministic offline trials')
    for v in variants:
        print(v,':', ' | '.join(f"{r['profile']} {r['tasks_passed']}/{r['tasks_expected']} {r['records_verified']}/{r['records_expected']} manifest={r['manifest_status']}" for r in results if r['variant']==v))
if __name__=='__main__':main()
