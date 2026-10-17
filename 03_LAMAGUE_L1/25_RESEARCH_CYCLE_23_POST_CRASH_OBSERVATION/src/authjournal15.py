"""Cycle15: authenticated crash journal bound to a plan digest. Research-only POSIX prototype."""
import hashlib,hmac,json,os,fcntl,contextlib,stat
from pathlib import Path

class Refused(Exception): pass

def canon(obj):return json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()
def digest(obj):return hashlib.sha256(canon(obj)).hexdigest()

def syncdir(root):
    fd=os.open(root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    try:os.fsync(fd)
    finally:os.close(fd)

@contextlib.contextmanager
def exclusive(root):
    root=Path(root); root.mkdir(parents=True,exist_ok=True)
    fd=os.open(root/'.lock',os.O_RDWR|os.O_CREAT|os.O_NOFOLLOW,0o600)
    try:
        try:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError as ex:raise Refused('concurrent publication') from ex
        yield
    finally:fcntl.flock(fd,fcntl.LOCK_UN);os.close(fd)

def read_chain(root,key,plan_digest):
    path=Path(root)/'journal.jsonl'
    if not path.exists():return []
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):raise Refused('invalid journal type')
        with os.fdopen(fd,'rb',closefd=False) as f:raw=f.read(2_000_000+1)
    finally:os.close(fd)
    if len(raw)>2_000_000 or not raw.endswith(b'\n'):raise Refused('truncated or oversized journal')
    prev='0'*64; output=[]
    for line in raw.splitlines():
        try:entry=json.loads(line); event=entry['event']; tag=entry['mac']
        except (KeyError,ValueError,TypeError) as ex:raise Refused('bad journal record') from ex
        if set(entry)!={'event','mac'} or not isinstance(event,dict):raise Refused('bad record shape')
        if set(event)!={'seq','prev','plan','kind','data'} or event['seq']!=len(output) or type(event['seq']) is not int or event['prev']!=prev or event['plan']!=plan_digest:raise Refused('journal sequence/binding mismatch')
        expected=hmac.new(key,canon(event),hashlib.sha256).hexdigest()
        if not isinstance(tag,str) or not hmac.compare_digest(tag,expected):raise Refused('journal authentication failed')
        if event['kind'] not in ('INTENT','STAGED','PUBLISHED'):raise Refused('unknown transition')
        if event['kind']!=('INTENT','STAGED','PUBLISHED')[min(len(output),2)]:raise Refused('transition order')
        prev=digest(entry);output.append(event)
    return output

def append(root,key,plan_digest,kind,data):
    events=read_chain(root,key,plan_digest)
    if len(events)>=3:raise Refused('already complete')
    if kind!=('INTENT','STAGED','PUBLISHED')[len(events)]:raise Refused('wrong transition')
    path=Path(root)/'journal.jsonl'
    prev='0'*64 if not events else None
    if events:
        # Regenerate previous record hash from raw journal tail, avoiding hidden mutable state.
        raw=path.read_bytes().splitlines()[-1];prev=hashlib.sha256(canon(json.loads(raw))).hexdigest()
    event={'seq':len(events),'prev':prev,'plan':plan_digest,'kind':kind,'data':data}
    entry={'event':event,'mac':hmac.new(key,canon(event),hashlib.sha256).hexdigest()}
    fd=os.open(path,os.O_WRONLY|os.O_APPEND|os.O_CREAT|os.O_NOFOLLOW,0o600)
    try:
        raw=canon(entry)+b'\n'
        while raw:
            n=os.write(fd,raw)
            if n<=0:raise OSError('write failed')
            raw=raw[n:]
        os.fsync(fd)
    finally:os.close(fd)
    syncdir(root)

def file_state(path,expected,nbytes):
    try:fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
    except FileNotFoundError:return 'ABSENT'
    except OSError:return 'INVALID'
    try:
        st=os.fstat(fd)
        if not stat.S_ISREG(st.st_mode) or st.st_size!=nbytes:return 'MISMATCH'
        sha=hashlib.sha256()
        while True:
            block=os.read(fd,65536)
            if not block:break
            sha.update(block)
        return 'MATCH' if sha.hexdigest()==expected else 'MISMATCH'
    finally:os.close(fd)

def inspect(root,key,plan,locked=False):
    if not locked:
        with exclusive(root):return inspect(root,key,plan,True)
    plan_hash=digest(plan);events=read_chain(root,key,plan_hash)
    if not events:return {'status':'NO_INTENT','retry_allowed':False}
    info=events[0]['data'];expected=info.get('sha256');nbytes=info.get('bytes')
    if info.get('target')!='result.bin' or not isinstance(expected,str) or len(expected)!=64 or type(nbytes) is not int or nbytes<0:raise Refused('invalid intent content')
    for e in events[1:]:
        if e['data']!={'sha256':expected}:raise Refused('inconsistent journal data')
    staged=file_state(Path(root)/'.stage.bin',expected,nbytes)
    output=file_state(Path(root)/'result.bin',expected,nbytes)
    if 'INVALID' in (staged,output) or 'MISMATCH' in (staged,output):state='QUARANTINE_INCONSISTENT'
    elif output=='MATCH':state='VERIFIED_PUBLISHED' if events[-1]['kind']=='PUBLISHED' else 'PUBLISHED_RECEIPT_MISSING'
    elif staged=='MATCH':state='STAGED_NOT_PUBLISHED'
    else:state='INTENT_ONLY'
    return {'status':state,'retry_allowed':False,'plan_digest':plan_hash,'events':len(events),'stage':staged,'published':output}

def publish(root,key,plan,payload,failpoint=None):
    """Fixed one-file publication. Caller supplies a previously validated authorization context.
    Not an authorization verifier or a sandbox; never put key within worker reach.
    """
    root=Path(root)
    if not isinstance(key,bytes) or len(key)<32:raise Refused('weak/missing secret')
    if not isinstance(plan,dict) or plan.get('action')!='COPY' or plan.get('output')!='result.bin' or plan.get('sha256')!=hashlib.sha256(payload).hexdigest() or plan.get('bytes')!=len(payload):raise Refused('plan/payload mismatch')
    with exclusive(root):
        if (root/'journal.jsonl').exists() or (root/'.stage.bin').exists() or (root/'result.bin').exists():raise Refused('operation already started')
        ph=digest(plan);d={'target':'result.bin','sha256':plan['sha256'],'bytes':len(payload)}
        append(root,key,ph,'INTENT',d)
        if failpoint=='intent':os._exit(41)
        fd=os.open(root/'.stage.bin',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
        try:
            view=memoryview(payload)
            while view:
                n=os.write(fd,view)
                if n<=0:raise OSError('short write')
                view=view[n:]
            os.fsync(fd)
        finally:os.close(fd)
        syncdir(root);append(root,key,ph,'STAGED',{'sha256':plan['sha256']})
        if failpoint=='staged':os._exit(42)
        os.link(root/'.stage.bin',root/'result.bin',follow_symlinks=False)
        syncdir(root)
        if failpoint=='link':os._exit(43)
        append(root,key,ph,'PUBLISHED',{'sha256':plan['sha256']})
        if failpoint=='published':os._exit(44)
        return inspect(root,key,plan,True)
