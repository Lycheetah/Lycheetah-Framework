#!/usr/bin/env python3
"""Cycle 11: signed authorization -> staged copy worker -> audited publisher.

Narrow local experiment. Requires root to use chroot + drop to UID 65534,
which is NOT a production sandbox. Tested only on disposable directory trees.
Trusted publisher remains privileged, and no kernel MAC/network sandbox is set.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import sqlite3
import stat
import subprocess
import sys
import tempfile

from bridge_v0_2 import BridgeError, digest_obj, verify_plan_integrity
from execution_boundary import verify_grant, root_fingerprints, open_root, open_parent, O_REG
from standard_fd_baseline import copy_one as conventional_copy_one

WORKER_UID=65534


def available() -> dict:
    """Only test mechanisms this program actually needs; do not infer broad sandboxing."""
    return {'posix': os.name=='posix', 'root_euid':os.geteuid()==0,
            'chroot_api':hasattr(os,'chroot'), 'uid_drop_api':hasattr(os,'setgroups') and hasattr(os,'setuid'),
            'usable':os.name=='posix' and os.geteuid()==0 and hasattr(os,'chroot') and hasattr(os,'setuid')}


def require_environment():
    if not available()['usable']:
        raise BridgeError('chroot + credential drop unavailable; fail closed')


def reserve(db, grant, plan):
    with sqlite3.connect(db, timeout=5, isolation_level=None) as con:
        con.execute('PRAGMA synchronous=FULL')
        con.execute('CREATE TABLE IF NOT EXISTS executions (signer TEXT, nonce TEXT, plan_sha256 TEXT, state TEXT, receipt_json TEXT, PRIMARY KEY(signer,nonce))')
        try:
            con.execute('BEGIN IMMEDIATE')
            con.execute('INSERT INTO executions VALUES (?,?,?,\'IN_PROGRESS\',NULL)',(grant['signer_id'],grant['nonce'],plan['plan_sha256']))
            con.execute('COMMIT')
        except sqlite3.IntegrityError as ex:
            con.execute('ROLLBACK')
            raise BridgeError('approval already consumed; replay denied') from ex


def _relative_parts(rel: str):
    p=PurePosixPath(rel)
    if p.is_absolute() or not p.parts or any(x in ('','..','.') for x in rel.split('/')):
        raise BridgeError('invalid relative path')
    return p.parts


def _root_read(root: str, rel: str, expected_hash: str, expected_size: int) -> bytes:
    rootfd=open_root(root)
    try:
        parent=open_parent(rootfd,rel)
        try:
            fd=os.open(PurePosixPath(rel).name,O_REG,dir_fd=parent)
            try:
                if not stat.S_ISREG(os.fstat(fd).st_mode):
                    raise BridgeError('input not a regular file')
                out=bytearray()
                while True:
                    buf=os.read(fd,min(262144,expected_size+1-len(out)))
                    if not buf:break
                    out.extend(buf)
                    if len(out)>expected_size: raise BridgeError('input exceeds approval')
                if len(out)!=expected_size or hashlib.sha256(out).hexdigest()!=expected_hash:
                    raise BridgeError('input differs from approved plan')
                return bytes(out)
            finally:os.close(fd)
        finally:os.close(parent)
    finally:os.close(rootfd)


def _prepare_jail(jail: Path, plan: dict):
    jail.mkdir(mode=0o755)
    # root owns all non-writable paths; worker has only /output writable.
    os.chmod(jail,0o755)
    src=jail/'source'; out=jail/'output'
    src.mkdir(mode=0o755);out.mkdir(mode=0o700)
    os.chown(out,WORKER_UID,WORKER_UID)
    seen_sources=set()
    for a in plan['actions']:
        sr=a['source_relative']; dr=a['destination_relative']
        if sr not in seen_sources:
            payload=_root_read(plan['source_root'],sr,a['source_sha256'],a['source_bytes'])
            filename=src.joinpath(*_relative_parts(sr))
            filename.parent.mkdir(parents=True,exist_ok=True)
            filename.write_bytes(payload)
            os.chmod(filename,0o444)
            seen_sources.add(sr)
        p=out.joinpath(*_relative_parts(dr)).parent
        p.mkdir(parents=True,exist_ok=True)
        os.chown(p,WORKER_UID,WORKER_UID)
        os.chmod(p,0o700)
    for folder in [src,*src.rglob('*')]:
        if folder.is_dir():
            os.chmod(folder,0o555)
    return src,out


def policy_facts(plan: dict, *, signature_valid=True, nonce_fresh=True,
                 root_valid=True, worker_uid=WORKER_UID, chrooted=True, privileged_fds=False) -> dict:
    c=plan['effect_contract']
    return {'requested_outcome':c['requested_outcome'],'source_effect':c['source_effect'],
            'destination_effect':c['destination_effect'], 'overwrite_policy':c['overwrite_policy'],
            'source_deletion_policy':c['source_deletion_policy'],
            'plan_digest_valid':True,'approval_signature_valid':signature_valid,
            'approval_nonce_fresh':nonce_fresh,'root_identity_valid':root_valid,
            'worker_uid':worker_uid,'worker_chrooted':chrooted,'worker_privileged_fds':privileged_fds}


def conventional_policy_decision(facts: dict) -> bool:
    """Independent literal Python counterpart of policy/effect_gate.rego, NOT OPA execution."""
    return (facts.get('requested_outcome')=='COPY_SELECTED_FILES'
        and facts.get('source_effect')=='PRESERVE'
        and facts.get('destination_effect')=='CREATE_ONLY_IF_ABSENT'
        and facts.get('overwrite_policy')=='FORBID'
        and facts.get('source_deletion_policy')=='FORBID'
        and all(facts.get(k) is True for k in ('plan_digest_valid','approval_signature_valid','approval_nonce_fresh','root_identity_valid'))
        and facts.get('worker_uid')==WORKER_UID and facts.get('worker_chrooted') is True
        and facts.get('worker_privileged_fds') is False)


def run_worker(jail: Path, plan: dict, *, probe=False, inject_extraneous=False, tamper_approved=False, symlink_approved=False, worker_script=None) -> dict:
    manifest={'jail':str(jail),'actions':[{'source_rel':a['source_relative'],
              'destination_rel':a['destination_relative'],'sha256':a['source_sha256'],
              'size':a['source_bytes']} for a in plan['actions']],
              'probe':probe,'inject_extraneous':inject_extraneous,'tamper_approved':tamper_approved,'symlink_approved':symlink_approved}
    entry=Path(worker_script) if worker_script else Path(__file__).with_name('worker_entry.py')
    try:
        proc=subprocess.run([sys.executable,'-I',str(entry)],input=json.dumps(manifest),
                   text=True,capture_output=True,timeout=12,close_fds=True,check=False)
    except subprocess.TimeoutExpired as e:
        raise BridgeError('worker timed out; outcome indeterminate') from e
    try:
        result=json.loads(proc.stdout)
    except ValueError as e:
        raise BridgeError(f'worker did not return JSON; exit={proc.returncode}') from e
    if proc.returncode!=0 or 'fatal' in result:
        raise BridgeError('worker failed: '+str(result.get('fatal','nonzero exit')))
    if result.get('worker_uid')!=WORKER_UID or result.get('worker_gid')!=WORKER_UID:
        raise BridgeError('worker did not attest to expected effective credentials')
    # Reported credentials are verified by the worker code, but self-report alone
    # is NOT an independent OS attestation against a malicious worker.
    return result


def execute_isolated(plan, envelope, keys, db: Path, *, probe=False,
                     inject_extraneous=False, tamper_approved=False, symlink_approved=False, require_fn=require_environment):
    require_fn()  # fail closed, do not automatically fall back to privileged execution
    verify_plan_integrity(plan)
    grant=verify_grant(plan,envelope,keys)
    if not conventional_policy_decision(policy_facts(plan)):
        raise BridgeError('policy refused operation')
    reserve(db,grant,plan)
    actions=[]; worker=None; error=None
    try:
        with tempfile.TemporaryDirectory(prefix='cycle11-jail-') as temp:
            jail=Path(temp)/'jail'
            _prepare_jail(jail,plan)
            worker=run_worker(jail,plan,probe=probe,inject_extraneous=inject_extraneous,
                   tamper_approved=tamper_approved,symlink_approved=symlink_approved)
            # Worker may generate unapproved files. They are NEVER published.
            outcomes=worker['actions']
            if len(outcomes)!=len(plan['actions']) or any(x['status']!='COPIED' for x in outcomes):
                raise BridgeError('isolated worker did not complete approved set')
            if root_fingerprints(plan)!=grant['roots']:
                raise BridgeError('original roots changed before publishing')
            for a in plan['actions']:
                rel=a['destination_relative']; srel=a['source_relative']
                # Explicitly recheck original source, refusing a changed request.
                _root_read(plan['source_root'],srel,a['source_sha256'],a['source_bytes'])
                # Conventional hardened file-descriptor publisher; separately privileged.
                result=conventional_copy_one(jail/'output',Path(plan['destination_root']),
                                rel,a['source_sha256'],a['source_bytes'])
                actions.append({'destination_relative':rel,'status':result})
                if result!='VERIFIED': raise BridgeError('trusted publisher failed: '+result)
            if root_fingerprints(plan)!=grant['roots']:
                raise BridgeError('root namespace changed after publishing; side effects may persist')
    except BaseException as exc:
        error=f'{type(exc).__name__}: {exc}'
    receipt={'status':'COMPLETED_VERIFIED' if error is None else 'FAILED_OR_PARTIAL',
             'plan_sha256':plan['plan_sha256'],'approval_nonce':grant['nonce'],
             'actions':actions,'worker':worker,'error':error,
             'limitations':'chroot+UID/DAC only; privileged publisher not isolated; no network, mount or whole-host confinement guarantee'}
    receipt['receipt_sha256']=digest_obj(receipt)
    with sqlite3.connect(db,timeout=5,isolation_level=None) as con:
        con.execute('UPDATE executions SET state=?, receipt_json=? WHERE signer=? AND nonce=? AND state=\'IN_PROGRESS\'',
            (receipt['status'],json.dumps(receipt,sort_keys=True),grant['signer_id'],grant['nonce']))
    return receipt
