"""Cycle19 synthetic glue of signed Cycle13 execution + persistent Cycle18 witness.
Research demonstration only; test controller provisions all keys. Not production security.
"""
import os,sys,json,subprocess,tempfile,time,socket,hashlib,base64,signal
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
import cycle13
import execution_boundary as auth
from demo_cycle12 import create_case
from witness17 import signed_message,send_obj,recv_obj
from authjournal15 import append,digest,inspect,read_chain

WITNESS_UID=65532

def sign_request(plan,nonce,raw,private,action='ANCHOR'):
    return {'action':action,'plan':plan,'nonce':nonce,'signature':private.sign(signed_message(plan,nonce)).hex(),
            'journal':base64.b64encode(raw).decode()}

def witness_call(sock_path,req):
    with socket.socket(socket.AF_UNIX) as s:
        s.settimeout(3);s.connect(str(sock_path));send_obj(s,req);return recv_obj(s)

def setup_witness(base,client_uid):
    state=base/'state';keys=base/'keys';sockdir=base/'sockets'
    for x in [state,keys]:
        x.mkdir(mode=0o700);os.chown(x,WITNESS_UID,WITNESS_UID);os.chmod(x,0o700)
    sockdir.mkdir(mode=0o755);os.chown(sockdir,WITNESS_UID,WITNESS_UID);os.chmod(sockdir,0o755)
    jk=os.urandom(32);wk=os.urandom(32);priv=Ed25519PrivateKey.generate()
    pub=priv.public_key().public_bytes(encoding=serialization.Encoding.Raw,format=serialization.PublicFormat.Raw)
    for name,data in [('journal.key',jk),('witness.key',wk),('signer.pub',pub)]:
        path=keys/name;path.write_bytes(data);os.chown(path,WITNESS_UID,WITNESS_UID);os.chmod(path,0o600)
    sock=sockdir/'w.sock'
    def drop():
        os.setgroups([]);os.setgid(WITNESS_UID);os.setuid(WITNESS_UID)
    p=subprocess.Popen([sys.executable,'-u',str(Path(__file__).with_name('witness18.py')),
        '--socket',str(sock),'--state',str(state),'--keys',str(keys),'--client-uid',str(client_uid)],
        preexec_fn=drop,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    for _ in range(200):
        if sock.exists():break
        if p.poll() is not None:raise RuntimeError('witness startup refused: '+p.stderr.read().decode())
        time.sleep(.015)
    if not sock.exists():raise RuntimeError('witness startup timed out')
    # Socket is 0600 owned by witness, explicitly allow designated local client UID access;
    # authorization additionally requires SO_PEERCRED identity matching.
    os.chmod(sock,0o666)
    return p,sock,jk,priv

def run_integrated(base:Path,failpoint=None):
    base=Path(base);base.mkdir(parents=True,exist_ok=False);os.chmod(base,0o755)
    jail,data,plan,grant,keys=create_case(base)
    nonce=grant['grant']['nonce']
    auth.verify_grant(plan,grant,keys)
    wp,sock,jk,signer=setup_witness(base,os.geteuid())
    journal=base/'journal';journal.mkdir()
    binding={'protocol':'C19-LINK-v1','plan_sha256':plan['plan_sha256'],
             'grant_nonce':nonce,'grant_signature':grant['signature_ed25519_b64'],
             'expected':{rel:hashlib.sha256(content).hexdigest() for rel,content in data.items()}}
    ph=digest(binding)
    (base/'binding.json').write_text(json.dumps(binding,sort_keys=True))
    with (base/'binding.json').open('rb') as f:os.fsync(f.fileno())
    def anchor():
        req=sign_request(binding,nonce,(journal/'journal.jsonl').read_bytes(),signer)
        r=witness_call(sock,req)
        if r.get('state')!='ANCHORED' or not r.get('authorized'):raise RuntimeError('witness refusal '+str(r))
        return r
    try:
        append(journal,jk,ph,'INTENT',{'grant_checked':True,'files':len(data)})
        anchor()
        if failpoint=='after_intent':os._exit(81)
        # C13 actually runs rootless namespaced worker and publisher; signed grant consumed in its ledger.
        result=cycle13.execute(plan,grant,keys,base/'nonce_ledger.db',jail,extra=True)
        if result['status']!='COMPLETED_VERIFIED':raise RuntimeError('Cycle13 failure: '+str(result['error']))
        if failpoint=='after_execution':os._exit(82)
        for rel,payload in data.items():
            if (jail/'source'/rel).read_bytes()!=payload or (jail/'published'/rel).read_bytes()!=payload:
                raise RuntimeError('published/source verification failed')
        append(journal,jk,ph,'STAGED',{'result':'verified_both_files'})
        anchor()
        if failpoint=='after_staged':os._exit(83)
        append(journal,jk,ph,'PUBLISHED',{'result':'published_both_files'})
        anchor()
        return {'status':'VERIFIED','witness': 'ANCHORED_3','signed_grant_checked':True,
                'nonce_consumed':cycle13.ledger_state(base/'nonce_ledger.db',grant['grant']),
                'sources_preserved':True,'published_files':len(data),'unapproved_output_excluded':not (jail/'published'/'UNAPPROVED.txt').exists(),
                'limitations':'single test controller provisions credentials; two independent signature domains; crash post-execution precedes journal reconciliation'}
    finally:
        wp.terminate()
        try:wp.wait(timeout=2)
        except subprocess.TimeoutExpired:wp.kill();wp.wait()

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--base',required=True);p.add_argument('--failpoint',default=None)
    opts=p.parse_args();print(json.dumps(run_integrated(Path(opts.base),opts.failpoint),indent=2))
