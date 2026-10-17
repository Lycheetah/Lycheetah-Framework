#!/usr/bin/env python3
"""Signed synthetic two-file workflow, runnable only with rootless namespaces."""
import json, os, tempfile
from pathlib import Path
import cycle13
from demo_cycle12 import create_case

def run():
    with tempfile.TemporaryDirectory(prefix='lamague-c13-demo-') as tmp:
        b=Path(tmp);os.chmod(b,0o755) # unprivileged host IDs need path traversal
        jail,data,plan,grant,keys=create_case(b)
        result=cycle13.execute(plan,grant,keys,b/'ledger.db',jail,extra=True)
        return {'status':result['status'],'error':result['error'],
                'observations':[x['observed'] for x in result['observations']],
                'source_preserved':all((jail/'source'/rel).read_bytes()==raw for rel,raw in data.items()),
                'approved_outputs_verified':all((jail/'published'/rel).read_bytes()==raw for rel,raw in data.items()),
                'unapproved_output_excluded':not (jail/'published/UNAPPROVED.txt').exists(),
                'replay_state':cycle13.ledger_state(b/'ledger.db',grant['grant'])}
if __name__=='__main__':print(json.dumps(run(),indent=2))
