#!/usr/bin/env python3
"""Cycle13 controlled namespace workflow. NOT a general sandbox or service.

Requires root, x86_64 Linux, /proc; no real user files. The signed destination
is the disposable jail's /published directory, writable only to publisher UID.
The OS observation is a gate before GO, not cryptographic attestation.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import selectors
import sqlite3
import stat
import socket
from array import array
import subprocess
import sys
import shutil
import tempfile
from contextlib import closing

import bridge_v0_2 as bridge
import execution_boundary as auth
import isolated_controller as old
from linux_guard import supported

WORKER=65534;PUBLISHER=65533

class Refused(Exception):pass

def prerequisites():
    return {'root':os.geteuid()==0,'linux_x86_64':supported(),
            'proc_status':Path('/proc/self/status').exists(),
            'chroot':hasattr(os,'chroot'),'setgroups':hasattr(os,'setgroups'),
            'unshare':shutil.which('unshare') is not None,
            'all':supported() and shutil.which('unshare') is not None and Path('/proc/self/status').exists() and hasattr(os,'chroot') and hasattr(os,'setgroups')}

def require():
    if not prerequisites()['all']:raise Refused('required controls unavailable; fail closed')

def _safe_rel(rel:str):
    if not isinstance(rel,str) or not rel or rel.startswith('/') or any(x in ('','..','.') for x in rel.split('/')):
        raise Refused('noncanonical relative path')
    return rel

def prepare_world(jail:Path, contents:dict[str,bytes]):
    """Only synthetic fixtures; never point at user-owned existing paths."""
    if jail.exists():raise Refused('jail already exists; do not alter')
    jail.mkdir(mode=0o755)
    for d,uid,mode in [('source',0,0o755),('work',WORKER,0o700),
                       ('verified',0,0o755),('published',PUBLISHER,0o700)]:
        x=jail/d;x.mkdir(mode=0o700);os.chown(x,uid,uid if uid else 0);os.chmod(x,mode)
    for rel,content in contents.items():
        _safe_rel(rel)
        file=jail/'source'/rel
        file.parent.mkdir(parents=True,exist_ok=True)
        file.write_bytes(content);os.chmod(file,0o444)
        for label,uid in [('work',WORKER),('verified',0),('published',PUBLISHER)]:
            par=jail/label/rel
            par.parent.mkdir(parents=True,exist_ok=True)
            cur=jail/label
            for segment in rel.split('/')[:-1]:
                cur=cur/segment
                os.chown(cur,uid,uid if uid else 0)
                os.chmod(cur,0o700 if uid else 0o755)
    for p in [jail/'source',*(jail/'source').rglob('*')]:
        if p.is_dir():os.chmod(p,0o555)
    return jail

def observation(pid:int,expected_uid:int,jail:Path,proof_root:bool,proof_ns:dict):
    """Controller reads kernel proc status, namespace inodes and host UID map."""
    status={}
    proc=Path('/proc')/str(pid)
    for line in (proc/'status').read_text().splitlines():
        if ':' in line:
            k,v=line.split(':',1);status[k]=v.strip()
    uid=[int(v) for v in status['Uid'].split()]
    gid=[int(v) for v in status['Gid'].split()]
    names=('user','mnt','net')
    # /proc/<pid>/ns/* is ptrace-gated and inaccessible in this container.
    # Kernel-backed namespace descriptors are passed by the trusted child.
    child_ns=proof_ns
    controller_ns={name:(Path('/proc/self/ns')/name).stat().st_ino for name in names}
    ns_diff={name:child_ns[name]!=controller_ns[name] for name in names}
    mapping=(proc/'uid_map').read_text().strip().split()
    mapping_valid=len(mapping)==3 and list(map(int,mapping))==[0,expected_uid,1]
    info={'pid':pid,'host_uid_fields':uid,'host_gid_fields':gid,
          'cap_eff':status.get('CapEff'),'no_new_privs':status.get('NoNewPrivs'),
          'seccomp':status.get('Seccomp'),'chroot_root_inode_via_scm_rights':proof_root,
          'namespace_inodes':child_ns,'different_from_controller':ns_diff,
          'uid_map':mapping,'uid_map_valid':mapping_valid,
          'proc_root_status':'UNAVAILABLE_AFTER_UID_DROP',
          'independent_fd_audit':'NOT_PERFORMED',
          'namespace_evidence':'TRUSTED_CHILD_SCM_RIGHTS_FDS_NOT_INDEPENDENT_PROC_NS_INSPECTION'}
    info['accepted']=(uid==[expected_uid]*4 and gid==[expected_uid]*4 and
          status.get('CapEff')=='0000000000000000' and status.get('NoNewPrivs')=='1'
          and status.get('Seccomp')=='2' and proof_root and
          mapping_valid and all(ns_diff.values()))
    return info

def _line_with_timeout(p,seconds):
    sel=selectors.DefaultSelector()
    try:
        sel.register(p.stdout,selectors.EVENT_READ)
        if not sel.select(seconds):raise Refused('child did not reach observation barrier')
        line=p.stdout.readline()
        if not line:raise Refused('child exited before observation: '+p.stderr.read(500))
        return line
    finally:sel.close()

def run_role(jail:Path, role:str, actions:list, *, extra=False, poison=False, symlink=False, crash_after_first_commit=False, inspector=observation):
    require()
    uid=WORKER if role=='worker' else PUBLISHER
    script=Path(__file__).with_name('role_child13.py')
    ref=Path(__file__).resolve().parents[1]/'reference'
    startup='import runpy,sys;sys.path.insert(0,sys.argv[1]);sys.path.insert(0,sys.argv[2]);runpy.run_path(sys.argv[3],run_name="__main__")'
    cmd=['unshare','-Urnm','--',sys.executable,'-u','-I','-c',startup,str(script.parent),str(ref),str(script)]
    parent_socket,child_socket=socket.socketpair(socket.AF_UNIX,socket.SOCK_STREAM)
    parent_socket.settimeout(6)
    env={**os.environ,'CYCLE13_PROOF_FD':str(child_socket.fileno())}
    def drop_host_identity():
        os.setgroups([]);os.setgid(uid);os.setuid(uid)
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE,text=True,bufsize=1,close_fds=True,
                       env=env,pass_fds=(child_socket.fileno(),),preexec_fn=drop_host_identity)
    child_socket.close()
    try:
        p.stdin.write(json.dumps({'jail':str(jail),'role':role,'actions':actions,
                     'inject_extra':extra,'poison':poison,'symlink':symlink,
                     'crash_after_first_commit':crash_after_first_commit})+'\n');p.stdin.flush()
        marker,controls,_,_=parent_socket.recvmsg(1,socket.CMSG_SPACE(4*array('i',[0]).itemsize))
        proof_fds=[]
        for level,ctype,payload in controls:
            if level==socket.SOL_SOCKET and ctype==socket.SCM_RIGHTS:
                numbers=array('i');numbers.frombytes(payload[:len(payload)//numbers.itemsize*numbers.itemsize]);proof_fds.extend(numbers)
        proof_root=False
        proof_ns={}
        try:
            if len(proof_fds)==4:
                got=os.fstat(proof_fds[0]);expected=jail.stat()
                proof_root=((got.st_dev,got.st_ino)==(expected.st_dev,expected.st_ino))
                proof_ns={name:os.fstat(fd).st_ino for name,fd in zip(('user','mnt','net'),proof_fds[1:])}
        finally:
            for fd in proof_fds:os.close(fd)
        if marker!=b'N' or not proof_root or len(proof_ns)!=3:
            p.wait(timeout=5)
            raise Refused('OS inode proof rejected; '+p.stderr.read(1000)+' '+p.stdout.read(1000))
        ready=json.loads(_line_with_timeout(p,6))
        if ready!={'ready':role}:raise Refused('role failed readiness: '+str(ready))
        observed=inspector(p.pid,uid,jail,proof_root,proof_ns)
        if not observed.get('accepted'):raise Refused('kernel-backed gate refused; fail closed')
        p.stdin.write('GO\n');p.stdin.flush();p.stdin.close()
        if p.wait(timeout=12)!=0:
            raise Refused('role failed: '+p.stdout.read(1000)+' '+p.stderr.read(1000))
        out=json.loads(p.stdout.readline())
        if 'fatal' in out or out.get('status')!='COMPLETED':
            raise Refused('child rejected: '+str(out))
        return {'observed':observed,'child_report':out}
    except BaseException:
        if p.poll() is None:
            p.kill()
            p.wait(timeout=5)
        raise
    finally:
        parent_socket.close()
        for f in (p.stdin,p.stdout,p.stderr):
            if f is not None and not f.closed:f.close()

def _read_checked(root:Path,rel:str,sha:str,size:int)->bytes:
    # Same fd-anchored no-follow read as Cycle11, with size/hash verification.
    return old._root_read(str(root),_safe_rel(rel),sha,size)

def stage_verified(jail:Path, actions:list):
    for a in actions:
        data=_read_checked(jail/'work',a['relative'],a['sha256'],a['size'])
        path=jail/'verified'/a['relative']
        fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o444)
        try:
            view=memoryview(data)
            while view:
                n=os.write(fd,view)
                if n<=0:raise Refused('short staging write')
                view=view[n:]
            os.fsync(fd)
        finally:os.close(fd)
        os.chmod(path,0o444)

def reserve_once(db:Path,grant,plan):
    with closing(sqlite3.connect(db,timeout=5,isolation_level=None)) as con:
        con.execute('PRAGMA synchronous=FULL')
        con.execute('CREATE TABLE IF NOT EXISTS executions (signer TEXT, nonce TEXT, plan_sha256 TEXT, state TEXT, receipt_json TEXT, PRIMARY KEY(signer,nonce))')
        try:
            con.execute('BEGIN IMMEDIATE')
            con.execute("INSERT INTO executions VALUES (?,?,?,'IN_PROGRESS',NULL)",
                (grant['signer_id'],grant['nonce'],plan['plan_sha256']))
            con.execute('COMMIT')
        except sqlite3.IntegrityError as e:
            con.execute('ROLLBACK')
            raise Refused('approval already consumed; replay denied') from e


def ledger_state(db:Path,grant:dict):
    with closing(sqlite3.connect(db)) as con:
        return con.execute('SELECT state FROM executions WHERE signer=? AND nonce=?',
                           (grant['signer_id'],grant['nonce'])).fetchone()[0]

def execute(plan, envelope, trusted_keys, db:Path, jail:Path, *,
            extra=False,poison=False,symlink=False,fault=None,inspector=observation):
    require()
    # Signing roots must be precisely the jail source and publisher-owned target.
    if Path(plan['source_root']).resolve()!=jail/'source' or Path(plan['destination_root']).resolve()!=jail/'published':
        raise Refused('approved destination is not the disposable publisher root')
    bridge.verify_plan_integrity(plan)
    grant=auth.verify_grant(plan,envelope,trusted_keys)
    reserve_once(db,grant,plan) # approval consumed BEFORE worker starts
    if fault=='hard_after_reservation':os._exit(73)  # only run this fault in a separate test process
    observed=[]; published=[]; error=None
    actions=[{'relative':a['destination_relative'],'source_relative':a['source_relative'],
              'sha256':a['source_sha256'],'size':a['source_bytes']} for a in plan['actions']]
    if any(a['relative']!=a['source_relative'] for a in actions):
        error='different source/destination names not in limited Cycle12 worker'
    else:
        try:
            if fault=='after_reservation':raise Refused('injected abort after nonce reservation')
            wr=run_role(jail,'worker',actions,extra=extra,poison=poison,symlink=symlink,inspector=inspector)
            observed.append({'role':'worker',**wr})
            if not old.conventional_policy_decision(old.policy_facts(plan,worker_uid=wr['observed']['host_uid_fields'][0],
                         chrooted=wr['observed']['accepted'],privileged_fds=False)):
                raise Refused('policy refused trusted observed facts')
            if fault=='after_worker':raise Refused('injected abort after worker')
            stage_verified(jail,actions)
            for a in actions:
                _read_checked(jail/'source',a['source_relative'],a['sha256'],a['size'])
            if auth.root_fingerprints(plan)!=grant['roots']:
                raise Refused('root identity changed before publisher')
            if fault=='before_publisher':raise Refused('injected abort before publisher')
            pub=run_role(jail,'publisher',actions,crash_after_first_commit=(fault=='publisher_after_first_commit'),inspector=inspector)
            observed.append({'role':'publisher',**pub})
            if fault=='hard_after_publish':os._exit(74)  # intentionally lose final receipt
            for a in actions:
                _read_checked(jail/'published',a['relative'],a['sha256'],a['size'])
                published.append(a['relative'])
            if auth.root_fingerprints(plan)!=grant['roots']:
                raise Refused('root identity changed after publication; effects may persist')
        except BaseException as e:error=f'{type(e).__name__}: {e}'
    state='COMPLETED_VERIFIED' if error is None else 'FAILED_OR_PARTIAL'
    receipt={'status':state,'plan_sha256':plan['plan_sha256'],'nonce':grant['nonce'],
             'published':published,'observations':observed,'error':error,
             'synthetic':True,'human_approval':False,'fd_audit_limitation':'No independent post-drop /proc fd inspection; programmatically closed proof socket and used close_fds',
             'security_boundary':'rootless user/mount/net namespaces + host UID/DAC + chroot + partial seccomp; not mature sandbox'}
    receipt['receipt_sha256']=bridge.digest_obj(receipt)
    with closing(sqlite3.connect(db,timeout=5,isolation_level=None)) as con:
        con.execute('UPDATE executions SET state=?,receipt_json=? WHERE signer=? AND nonce=? AND state=\'IN_PROGRESS\'',
                    (state,json.dumps(receipt,sort_keys=True),grant['signer_id'],grant['nonce']))
    return receipt
