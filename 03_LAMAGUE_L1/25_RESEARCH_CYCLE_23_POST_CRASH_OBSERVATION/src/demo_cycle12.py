#!/usr/bin/env python3
"""Reproducible sample; generates only synthetic files under a fresh temp jail."""
import json
from pathlib import Path
import tempfile
from cryptography.hazmat.primitives import serialization

import bridge_v0_2 as bridge
import execution_boundary as auth
from cycle12 import prepare_world,execute,ledger_state,prerequisites

def create_case(base):
    jail=base/'jail'
    data={'sample.txt':b'approved specimen','notes/research.txt':b'approved research'}
    prepare_world(jail,data)
    plan=bridge.build_plan(bridge.demo_packet(jail/'source',jail/'published'))
    private=auth.Ed25519PrivateKey.generate()
    pub=private.public_key().public_bytes(encoding=serialization.Encoding.Raw,format=serialization.PublicFormat.Raw)
    grant=auth.sign_grant(auth.draft_grant(plan,signer_id='SYNTHETIC-NO-HUMAN'),private)
    return jail,data,plan,grant,{'SYNTHETIC-NO-HUMAN':pub}

def run():
    with tempfile.TemporaryDirectory(prefix='cycle12-synthetic-') as tmp:
        b=Path(tmp)
        jail,data,plan,grant,keys=create_case(b)
        rec=execute(plan,grant,keys,b/'replays.sqlite3',jail,extra=True)
        try:
            execute(plan,grant,keys,b/'replays.sqlite3',jail)
            replay='UNEXPECTED_ACCEPT'
        except Exception as e:replay=type(e).__name__+': '+str(e)
        return {'environment':prerequisites(),'status':rec['status'],
                'os_observations':[{k:v for k,v in x.items() if k!='child_report'} for x in rec['observations']],
                'probes':{x['role']:x['child_report']['probes'] for x in rec['observations']},
                'approved_outputs_correct':all((jail/'published'/rel).read_bytes()==payload for rel,payload in data.items()),
                'sources_preserved':all((jail/'source'/rel).read_bytes()==payload for rel,payload in data.items()),
                'extra_work_file_present':(jail/'work/UNAPPROVED.txt').exists(),
                'extra_published':(jail/'published/UNAPPROVED.txt').exists(),
                'replay_rejected':'already consumed' in replay,
                'ledger_state':ledger_state(b/'replays.sqlite3',grant['grant']),
                'receipt_sha256':rec['receipt_sha256'],
                'limitation':'Trusted Python child, disposable jail, seccomp deny-list and chroot; not a production sandbox'}
if __name__=='__main__':print(json.dumps(run(),indent=2))
