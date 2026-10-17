#!/usr/bin/env python3
"""10 synthetic scenarios; no statistical population inference."""
import json
from pathlib import Path
import tempfile
from demo_cycle12 import create_case
import cycle12 as c

CASES=['normal','extra_unapproved','poison_worker_bytes','symlink_worker_output',
       'abort_after_reservation','abort_after_worker','abort_before_publisher',
       'destination_collision','changed_signed_source','failed_os_observation']

def run():
    cases=[]
    for name in CASES:
        with tempfile.TemporaryDirectory(prefix='cycle12-matrix-') as t:
            root=Path(t)
            jail,original,plan,envelope,keys=create_case(root)
            options={}
            if name=='extra_unapproved':options['extra']=True
            elif name=='poison_worker_bytes':options['poison']=True
            elif name=='symlink_worker_output':options['symlink']=True
            elif name.startswith('abort_'):
                options['fault']={'abort_after_reservation':'after_reservation',
                 'abort_after_worker':'after_worker','abort_before_publisher':'before_publisher'}[name]
            elif name=='destination_collision':
                (jail/'published/sample.txt').write_bytes(b'EXISTING')
            elif name=='changed_signed_source':
                (jail/'source/sample.txt').write_bytes(b'UNAPPROVED CHANGE')
            elif name=='failed_os_observation':
                def reject(pid,uid,jail,proof_root):
                    o=c.observation(pid,uid,jail,proof_root);o['accepted']=False;return o
                options['inspector']=reject
            receipt=c.execute(plan,envelope,keys,root/'ledger.db',jail,**options)
            actual={k:(jail/'published'/k).read_bytes() if (jail/'published'/k).exists() and (jail/'published'/k).is_file() else None for k in original}
            expected_success=name in ('normal','extra_unapproved')
            expected_status='COMPLETED_VERIFIED' if expected_success else 'FAILED_OR_PARTIAL'
            case={'scenario':name,'status':receipt['status'],
                  'expected_status':expected_status,
                  'all_approved_outputs_match':all(actual[k]==v for k,v in original.items()),
                  'unapproved_file_published':(jail/'published/UNAPPROVED.txt').exists(),
                  'observed_worker':any(o['role']=='worker' for o in receipt['observations']),
                  'observed_publisher':any(o['role']=='publisher' for o in receipt['observations']),
                  'error':receipt['error']}
            if receipt['status']!=expected_status:raise AssertionError(name+' unexpected decision '+str(case))
            if case['unapproved_file_published']:raise AssertionError(name+' unapproved published')
            if expected_success and not case['all_approved_outputs_match']:raise AssertionError(name+' bytes mismatch')
            if name=='destination_collision' and actual['sample.txt']!=b'EXISTING':raise AssertionError('overwrite')
            cases.append(case)
    return {'scenarios':cases,'count':len(cases),'all_expected_statuses':True,
            'note':'Synthetic fault injections. Staged publication may be partial after a late failure; no atomic multi-file guarantee.'}
if __name__=='__main__':print(json.dumps(run(),indent=2))
