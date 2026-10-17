#!/usr/bin/env python3
"""Small constructed matrix. Expected outcomes predetermined by harness author."""
import json,os,subprocess,sys,tempfile
from pathlib import Path
import cycle13,recovery13
from demo_cycle12 import create_case


def sample(scenario):
    with tempfile.TemporaryDirectory(prefix='lamague13-matrix-') as d:
        b=Path(d);os.chmod(b,0o755)
        jail,contents,plan,grant,keys=create_case(b)
        db=b/'ledger.db'
        if scenario in ('normal','extra_output','poison','symlink_output','deny_observation'):
            kw={'extra':scenario=='extra_output','poison':scenario=='poison',
                'symlink':scenario=='symlink_output'}
            if scenario=='deny_observation':kw['inspector']=lambda *args:{'accepted':False}
            r=cycle13.execute(plan,grant,keys,db,jail,**kw)
            return {'scenario':scenario,'result':r['status'],
                    'published_file_count':sum(p.is_file() for p in (jail/'published').rglob('*')),
                    'originals_intact':all((jail/'source'/rel).read_bytes()==raw for rel,raw in contents.items())}
        payload=b/'req.json'
        payload.write_text(json.dumps({'plan':plan,'grant':grant,'keys':{k:v.hex() for k,v in keys.items()},
                     'fault':'hard_after_reservation' if scenario=='crash_after_reservation' else 'hard_after_publish'}))
        code='''import json,sys
from pathlib import Path
import cycle13
b=Path(sys.argv[1]);r=json.loads((b/'req.json').read_text())
cycle13.execute(r['plan'],r['grant'],{k:bytes.fromhex(v) for k,v in r['keys'].items()},
    b/'ledger.db',b/'jail',fault=r['fault'])'''
        p=subprocess.run([sys.executable,'-c',code,str(b)],capture_output=True,text=True,timeout=30)
        if scenario=='crash_after_publish_plus_corruption':
            (jail/'published/sample.txt').write_bytes(b'corrupted')
        rec=recovery13.reconcile(plan,grant,keys,db,jail)
        return {'scenario':scenario,'child_exit':p.returncode,
                'recovery_classification':rec['classification'],'auto_retry':False,
                'originals_intact':all((jail/'source'/rel).read_bytes()==raw for rel,raw in contents.items())}

def run():
    names=['normal','extra_output','poison','symlink_output','deny_observation',
           'crash_after_reservation','crash_after_publish','crash_after_publish_plus_corruption']
    results=[sample(n) for n in names]
    expected=['COMPLETED_VERIFIED','COMPLETED_VERIFIED','FAILED_OR_PARTIAL',
              'FAILED_OR_PARTIAL','FAILED_OR_PARTIAL',
              'ABORTED_BEFORE_PUBLICATION','OUTPUTS_PRESENT_RECEIPT_MISSING',
              'INCONSISTENT_QUARANTINE']
    actual=[x['result'] if 'result' in x else x['recovery_classification'] for x in results]
    assert actual==expected,list(zip(actual,expected))
    assert all(x['originals_intact'] for x in results)
    return {'scenarios':len(results),'matched_expected':len(results),'results':results,
            'limitations':'constructed scenarios and trusted synthetic code, not statistical deployment evidence'}
if __name__=='__main__':print(json.dumps(run(),indent=2))
