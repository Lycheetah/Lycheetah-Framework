#!/usr/bin/env python3
"""Cycle13 rootless user/mount/net namespace worker; trusted synthetic process.

The parent sends a manifest line; this child drops privileges and installs a
limited seccomp filter, then announces READY. Only after parent reads kernel
/proc facts will it send GO. It never runs user supplied executable code.
"""
import hashlib
import json
import os
from pathlib import Path
import socket
import sys
import stat
from array import array

from linux_guard import install
import ctypes
from standard_fd_baseline import copy_one

WORKER=65534
PUBLISHER=65533

def probe(role):
    results={}
    for name, fn in {
      'network_socket': lambda:socket.socket(socket.AF_INET,socket.SOCK_STREAM),
      'process_fork': lambda:os.fork(),
      'execve':lambda:os.execve('/missing', ['/missing'],{}),
      'write_source':lambda:os.open('/source/notes/research.txt',os.O_WRONLY|os.O_TRUNC),
      'write_other_role':lambda:os.open('/published/nope',os.O_WRONLY|os.O_CREAT,0o600) if role=='worker' else os.open('/work/nope',os.O_WRONLY|os.O_CREAT,0o600),
      'escape_root':lambda:os.open('/../../outside',os.O_WRONLY|os.O_CREAT,0o600),
    }.items():
        try:
            fd=fn()
            if isinstance(fd,socket.socket):fd.close()
            elif isinstance(fd,int):
                if name=='process_fork':
                    if fd==0:os._exit(200)
                    os.waitpid(fd,0)
                else:os.close(fd)
            results[name]='UNEXPECTED_ALLOWED'
        except OSError as e:results[name]='DENIED_ERRNO_'+str(e.errno)
    return results

def strip_namespace_caps():
    """Drop effective, permitted and inheritable caps in user namespace.
    This is not a general-purpose sandbox setup.
    """
    libc=ctypes.CDLL(None,use_errno=True)
    class Header(ctypes.Structure):
        _fields_=[('version',ctypes.c_uint32),('pid',ctypes.c_int)]
    class CapData(ctypes.Structure):
        _fields_=[('effective',ctypes.c_uint32),('permitted',ctypes.c_uint32),('inheritable',ctypes.c_uint32)]
    hdr=Header(0x20080522,0)
    vals=(CapData*2)()
    if libc.capset(ctypes.byref(hdr),ctypes.byref(vals))!=0:
        raise OSError(ctypes.get_errno(),'capset failed')
    st=dict(line.split(':',1) for line in open('/proc/self/status') if ':' in line) if os.path.exists('/proc/self/status') else {}
    # /proc may not be mounted inside chroot; independent host process verifies.
    return True

def run():
    req=json.loads(sys.stdin.readline())
    jail=Path(req['jail'])
    role=req['role']
    if role not in ('worker','publisher') or not jail.is_absolute():
        raise ValueError('invalid role/jail')
    uid=WORKER if role=='worker' else PUBLISHER
    # Python source/library modules were loaded before chroot. These routines
    # are trusted. Arbitrary imported code is outside this threat model.
    # Preexec host already dropped to the correct host UID/GID. unshare -Urnm
    # maps only that host identity to uid 0 inside a private user namespace.
    # No other UIDs mapped: setuid(65534) inside namespace is impossible.
    if os.geteuid()!=0:raise RuntimeError('namespace root mapping absent')
    ns_fds=[os.open('/proc/self/ns/'+n,os.O_RDONLY|os.O_CLOEXEC) for n in ('user','mnt','net')]
    os.chroot(str(jail));os.chdir('/')
    strip_namespace_caps()
    # supported() requires euid 0; a controller has already checked that.
    from linux_guard import install_after_drop
    install_after_drop()
    proof_fd=int(os.environ.pop('CYCLE13_PROOF_FD'))
    proof_socket=socket.socket(fileno=proof_fd)
    root_fd=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_CLOEXEC)
    try:
        proof_socket.sendmsg([b'N'],[(socket.SOL_SOCKET,socket.SCM_RIGHTS,array('i',[root_fd,*ns_fds]))])
    finally:
        os.close(root_fd)
        for ns_fd in ns_fds:os.close(ns_fd)
        proof_socket.close()
    print(json.dumps({'ready':role}),flush=True)
    if sys.stdin.readline().strip()!='GO':
        return {'status':'ABORTED_BEFORE_ACTION'}
    source, destination=('/source','/work') if role=='worker' else ('/verified','/published')
    result=[]
    for action in req['actions']:
        rel=action['relative']
        status=copy_one(Path(source),Path(destination),rel,action['sha256'],action['size'])
        result.append({'relative':rel,'status':status})
        if role=='publisher' and req.get('crash_after_first_commit') and len(result)==1 and status=='VERIFIED':
            os._exit(92)  # test-only real abrupt termination after the first file commit
        if status!='VERIFIED':break
    if role=='worker' and req.get('inject_extra'):
        Path('/work/UNAPPROVED.txt').write_bytes(b'not in signed plan')
    if role=='worker' and req.get('poison') and result and result[0]['status']=='VERIFIED':
        (Path('/work')/result[0]['relative']).write_bytes(b'poisoned')
    if role=='worker' and req.get('symlink') and result and result[0]['status']=='VERIFIED':
        p=Path('/work')/result[0]['relative'];p.unlink();p.symlink_to('/source/'+result[0]['relative'])
    return {'status':'COMPLETED' if len(result)==len(req['actions']) and all(r['status']=='VERIFIED' for r in result) else 'FAILED',
            'actions':result,'probes':probe(role)}
if __name__=='__main__':
    try:
        res=run();print(json.dumps(res,sort_keys=True),flush=True)
    except BaseException as e:
        print(json.dumps({'fatal':f'{type(e).__name__}: {e}'}),flush=True);sys.exit(1)
