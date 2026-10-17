"""Cycle17 local UID-separated journal-head witness, research only.
Witness service owns private checkpoint and key. Requests carry complete journal bytes
and Ed25519 signed plan authorization; service validates chain and approval each time.
"""
import os, json, hmac, hashlib, socket, struct, stat, base64, tempfile, pathlib
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from authjournal15 import canon, digest

MAX_REQ=2500000
class Denied(Exception): pass

def signed_message(plan, nonce):
    return canon({'domain':'LAMAGUE-WITNESS-C17-v1','plan':plan,'nonce':nonce})

def validate_records(raw, plan, journal_key):
    if len(raw)>2_000_000 or not raw.endswith(b'\n'):raise Denied('journal malformed')
    lines=raw.splitlines();prev='0'*64;kind=('INTENT','STAGED','PUBLISHED')
    if not 1<=len(lines)<=3:raise Denied('unexpected event count')
    ph=digest(plan)
    for i,line in enumerate(lines):
        try:e=json.loads(line);ev=e['event'];mac=e['mac']
        except (ValueError,KeyError,TypeError) as ex:raise Denied('invalid record') from ex
        if set(e)!={'event','mac'} or set(ev)!={'seq','prev','plan','kind','data'} or type(ev['seq']) is not int or ev['seq']!=i or ev['prev']!=prev or ev['plan']!=ph or ev['kind']!=kind[i]:raise Denied('invalid journal chain')
        if not isinstance(mac,str) or not hmac.compare_digest(mac,hmac.new(journal_key,canon(ev),hashlib.sha256).hexdigest()):raise Denied('invalid journal mac')
        prev=digest(e)
    return {'count':len(lines),'last_hash':prev}

def recv_obj(sock):
    hdr=sock.recv(4)
    if len(hdr)!=4:raise Denied('header missing')
    size=struct.unpack('!I',hdr)[0]
    if size>MAX_REQ:raise Denied('oversize')
    data=b''
    while len(data)<size:
        chunk=sock.recv(min(65536,size-len(data)))
        if not chunk:raise Denied('truncated')
        data+=chunk
    return json.loads(data)

def send_obj(sock,obj):
    raw=canon(obj);sock.sendall(struct.pack('!I',len(raw))+raw)

def read_anchor(witness_dir,key):
    p=pathlib.Path(witness_dir)/'checkpoint.json'
    try:fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW)
    except FileNotFoundError:return None
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):raise Denied('anchor type')
        raw=os.read(fd,8193)
    finally:os.close(fd)
    if len(raw)>8192:raise Denied('anchor size')
    try:obj=json.loads(raw);b=obj['body'];tag=obj['mac']
    except (ValueError,KeyError,TypeError) as ex:raise Denied('anchor invalid') from ex
    if set(obj)!={'body','mac'} or set(b)!={'plan','nonce','count','last_hash'} or not isinstance(tag,str) or not hmac.compare_digest(tag,hmac.new(key,canon(b),hashlib.sha256).hexdigest()):raise Denied('anchor tampered')
    return b

def save_anchor(root,key,body):
    p=pathlib.Path(root);entry={'body':body,'mac':hmac.new(key,canon(body),hashlib.sha256).hexdigest()}
    fd,path=tempfile.mkstemp(prefix='.checkpoint-',dir=root)
    try:
        os.fchmod(fd,0o600)
        with os.fdopen(fd,'wb') as f:f.write(canon(entry));f.flush();os.fsync(f.fileno())
        os.replace(path,p/'checkpoint.json')
        dirfd=os.open(root,os.O_RDONLY|os.O_DIRECTORY)
        try:os.fsync(dirfd)
        finally:os.close(dirfd)
    finally:
        if os.path.exists(path):os.unlink(path)

def decide(request,witness_dir,journal_key,witness_key,public_key):
    if set(request)!={'action','plan','nonce','signature','journal'}:raise Denied('request shape')
    plan=request['plan'];nonce=request['nonce']
    if not isinstance(plan,dict) or not isinstance(nonce,str) or len(nonce)<16:raise Denied('invalid authority scope')
    try:
        public_key.verify(bytes.fromhex(request['signature']),signed_message(plan,nonce))
        raw=base64.b64decode(request['journal'],validate=True)
    except Exception as ex:raise Denied('signature/journal encoding invalid') from ex
    head=validate_records(raw,plan,journal_key)
    previous=read_anchor(witness_dir,witness_key)
    body={'plan':digest(plan),'nonce':nonce,**head}
    if previous:
        if (previous['plan'],previous['nonce'])!=(body['plan'],nonce):raise Denied('other operation already anchored')
        if head['count']<previous['count']:return {'state':'ROLLBACK_DETECTED','authorized':False}
        lines=raw.splitlines();old=json.loads(lines[previous['count']-1])
        if digest(old)!=previous['last_hash']:return {'state':'FORK_DETECTED','authorized':False}
    if request['action']=='CHECK':
        state='NO_ANCHOR' if previous is None else ('MATCH' if previous==body else 'UNANCHORED_TAIL')
        return {'state':state,'authorized':False}
    if request['action']!='ANCHOR':raise Denied('unknown action')
    if not previous or previous!=body:save_anchor(witness_dir,witness_key,body)
    return {'state':'ANCHORED','authorized':True,'count':head['count']}

def serve_once(sock,witness_dir,journal_key,witness_key,pubkey):
    try:
        req=recv_obj(sock);resp=decide(req,witness_dir,journal_key,witness_key,pubkey)
    except Exception as e:resp={'state':'DENIED','authorized':False,'reason':str(e)}
    send_obj(sock,resp)

def isolated_roundtrip(req,witness_dir,journal_key,witness_key,public_bytes,uid=65534):
    """Fork one-shot witness. Privilege-drop child when root. Parent cannot access its private rootless dir.
    This is a local permissions test, not host-independent isolation.
    """
    parent,child=socket.socketpair()
    pid=os.fork()
    if pid==0:
        try:
            parent.close()
            if os.geteuid()==0:
                os.setgroups([]);os.setgid(uid);os.setuid(uid)
            pub=Ed25519PublicKey.from_public_bytes(public_bytes)
            serve_once(child,witness_dir,journal_key,witness_key,pub)
        finally:os._exit(0)
    child.close()
    try:send_obj(parent,req);answer=recv_obj(parent)
    finally:parent.close();os.waitpid(pid,0)
    return answer
