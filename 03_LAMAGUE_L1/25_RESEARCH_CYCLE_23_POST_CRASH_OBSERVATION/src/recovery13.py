#!/usr/bin/env python3
"""Inspection-only recovery for a STOPPED disposable Cycle13 operation.

Never retries, deletes, repairs, or publishes. Intended for a quiescent test jail.
No independent process-quiescence proof; production recovery requires a lock/fence.
"""
from __future__ import annotations
import json, os, sqlite3, stat
from pathlib import Path
from contextlib import closing
import bridge_v0_2 as bridge
import execution_boundary as auth
from cycle13 import _read_checked, Refused


def inspect_published(plan:dict, jail:Path):
    root=jail/'published'
    expected={a['destination_relative']:(a['source_sha256'],a['source_bytes']) for a in plan['actions']}
    found=set(); suspicious=[]
    for parent,dirs,files in os.walk(root,followlinks=False):
        for name in dirs+files:
            path=Path(parent)/name
            rel=path.relative_to(root).as_posix()
            st=os.lstat(path)
            if stat.S_ISLNK(st.st_mode):suspicious.append('SYMLINK:'+rel)
            elif stat.S_ISREG(st.st_mode):
                found.add(rel)
                if rel not in expected:suspicious.append('EXTRA:'+rel)
            elif not stat.S_ISDIR(st.st_mode):suspicious.append('OTHER:'+rel)
    matched=[];missing=[];changed=[]
    for rel,(sha,size) in expected.items():
        if rel not in found:
            missing.append(rel)
            continue
        try:
            _read_checked(root,rel,sha,size)
            matched.append(rel)
        except Exception:
            changed.append(rel)
    if suspicious or changed:classification='INCONSISTENT_QUARANTINE'
    elif len(matched)==len(expected):classification='OUTPUTS_PRESENT_RECEIPT_MISSING'
    elif matched:classification='PARTIAL_VERIFIED_REQUIRES_OPERATOR'
    else:classification='ABORTED_BEFORE_PUBLICATION'
    return {'classification':classification,'verified_published':sorted(matched),
            'missing':sorted(missing),'changed':sorted(changed),'suspicious':sorted(suspicious)}


def reconcile(plan:dict,envelope:dict,trusted_keys:dict,db:Path,jail:Path):
    bridge.verify_plan_integrity(plan)
    grant=auth.verify_grant(plan,envelope,trusted_keys)
    if Path(plan['source_root']).resolve()!=jail/'source' or Path(plan['destination_root']).resolve()!=jail/'published':
        raise Refused('recovery target differs from approved plan')
    # Signed roots safeguard against substituting an unrelated jail.
    if auth.root_fingerprints(plan)!=grant['roots']:
        raise Refused('root identity changed: refuse recovery')
    with closing(sqlite3.connect(db,timeout=5,isolation_level=None)) as con:
        con.execute('PRAGMA synchronous=FULL')
        con.execute('BEGIN IMMEDIATE')
        row=con.execute('SELECT plan_sha256,state,receipt_json FROM executions WHERE signer=? AND nonce=?',
                        (grant['signer_id'],grant['nonce'])).fetchone()
        if row is None or row[0]!=plan['plan_sha256']:
            con.execute('ROLLBACK');raise Refused('reservation missing or mismatched')
        if row[1]!='IN_PROGRESS':
            con.execute('COMMIT')
            return {'classification':'ALREADY_TERMINAL','ledger_state':row[1],
                    'changed':False,'mutation':'NONE','no_retry':True}
        result=inspect_published(plan,jail)
        result.update({'plan_sha256':plan['plan_sha256'],'nonce':grant['nonce'],
                       'source':'filesystem inspection, not proof of original operation',
                       'mutation':'LEDGER_STATE_ONLY','no_retry':True,
                       'limitations':['requires a quiescent disposable jail',
                          'does not prove original worker/publisher identity',
                          'no crash-consistent multi-file atomicity',
                          'signed grant expiry can block delayed recovery']})
        result['recovery_sha256']=bridge.digest_obj(result)
        state='RECOVERED_'+result['classification']
        con.execute('UPDATE executions SET state=?,receipt_json=? WHERE signer=? AND nonce=? AND state=?',
                    (state,json.dumps(result,sort_keys=True),grant['signer_id'],grant['nonce'],'IN_PROGRESS'))
        con.execute('COMMIT')
        return result
