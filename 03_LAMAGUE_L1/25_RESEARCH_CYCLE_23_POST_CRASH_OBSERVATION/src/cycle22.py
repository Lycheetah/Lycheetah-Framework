"""Cycle22: actual namespaced publisher kills itself after first file commit.
Only runs inside a caller-provided disposable test directory. Linux-specific.
"""
import os,base64,hashlib,json
from pathlib import Path
from demo_cycle12 import create_case
from authority20 import build_binding,classify
from authjournal15 import append,digest
from witness21 import adjudicate
import cycle13

def experiment(base:Path, fault='publisher_after_first_commit'):
    base=Path(base);base.parent.chmod(0o755);base.mkdir(mode=0o755,parents=True,exist_ok=False)
    jail,data,plan,grant,pub=create_case(base)
    bind=build_binding(plan,grant)
    jk,wk=os.urandom(32),os.urandom(32)
    journal=base/'journal';journal.mkdir()
    state=base/'witness';state.mkdir(mode=0o700)
    append(journal,jk,digest(bind),'INTENT',{'expected_count':len(data)})
    def check(action='ANCHOR'):
        req={'action':action,'plan':plan,'grant':grant,'binding':bind,
             'journal':base64.b64encode((journal/'journal.jsonl').read_bytes()).decode()}
        return adjudicate(req,state,jk,wk,pub)
    first=check()
    result=cycle13.execute(plan,grant,pub,base/'ledger.db',jail,fault=fault)
    current=check('CHECK')
    ledger=cycle13.ledger_state(base/'ledger.db',grant['grant'])
    obs=classify(bind,jail/'published',journal_stage='INTENT',checkpoint_state='MATCH' if current['state']=='MATCH' else current['state'],ledger_state=ledger)
    return {'execution':result['status'],'execution_error':result['error'],'witness_anchor':first['state'],
            'witness_post_check':current['state'],'ledger':ledger,'recovery':obs,
            'source_preserved':all((jail/'source'/rel).read_bytes()==content for rel,content in data.items()),
            'auto_retry':False,'test_only':True}
if __name__=='__main__':
    import tempfile
    with tempfile.TemporaryDirectory(prefix='c22-') as tmp:
        print(json.dumps(experiment(Path(tmp)/'case'),indent=2))
