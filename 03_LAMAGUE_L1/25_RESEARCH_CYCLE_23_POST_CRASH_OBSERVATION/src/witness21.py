"""Cycle 21 original-grant-aware persistent witness reference, LOCAL research only.
Unlike Cycle 18, authorization uses the original execution grant, not a second signature.
The journal remains an HMAC-authenticated account of events, not proof that events happened.
"""
import os,sys, socket,struct,json,base64,hashlib,hmac,argparse,pathlib,stat,datetime
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from witness17 import validate_records,read_anchor,save_anchor,recv_obj,send_obj,Denied
from witness18 import read_secret,peer_uid
from authority20 import verify_original_grant,build_binding,Refusal
from authjournal15 import canon,digest


def adjudicate(req, state, journal_key, witness_key, trusted_keys, now=None):
    if not isinstance(req,dict) or set(req)!={'action','plan','grant','binding','journal'}:raise Denied('request shape')
    if req['action'] not in ('CHECK','ANCHOR'):raise Denied('unknown action')
    plan,grant,binding=req['plan'],req['grant'],req['binding']
    try:
        # Caller cannot omit expiry verification through this service.
        verdict=verify_original_grant(plan,grant,trusted_keys,binding,now=now or datetime.datetime.now(datetime.timezone.utc))
    except Refusal as exc:raise Denied('original grant refused: '+str(exc)) from exc
    try:raw=base64.b64decode(req['journal'],validate=True)
    except Exception as exc:raise Denied('journal encoding') from exc
    head=validate_records(raw,binding,journal_key)
    nonce=verdict['nonce']; previous=read_anchor(state,witness_key)
    body={'plan':digest(binding),'nonce':nonce,**head}
    if previous:
        if previous['plan']!=body['plan'] or previous['nonce']!=nonce:raise Denied('operation mismatch')
        if previous['count']>head['count']:return {'state':'ROLLBACK_DETECTED','authorized':False}
        if digest(json.loads(raw.splitlines()[previous['count']-1]))!=previous['last_hash']:
            return {'state':'FORK_DETECTED','authorized':False}
    if req['action']=='CHECK':
        return {'state':('NO_ANCHOR' if previous is None else 'MATCH' if previous==body else 'UNANCHORED_TAIL'),'authorized':False}
    if previous!=body:save_anchor(state,witness_key,body)
    return {'state':'ANCHORED','authorized':True,'count':head['count'],'original_grant_verified':True}


def serve(sockpath,state,keys,uid):
    for p in (state,keys):
        x=os.stat(p)
        if x.st_uid!=os.geteuid() or not stat.S_ISDIR(x.st_mode) or x.st_mode&0o077:raise Denied('private directory permissions')
    jk=read_secret(pathlib.Path(keys)/'journal.key',32)
    wk=read_secret(pathlib.Path(keys)/'witness.key',32)
    trusted={'SYNTHETIC-NO-HUMAN':read_secret(pathlib.Path(keys)/'grant.pub',32)}
    if pathlib.Path(sockpath).exists():raise Denied('socket exists')
    s=socket.socket(socket.AF_UNIX);s.bind(sockpath);os.chmod(sockpath,0o600);s.listen(4)
    try:
        while True:
            conn,_=s.accept()
            with conn:
                conn.settimeout(3)
                try:
                    if peer_uid(conn)!=uid:raise Denied('peer uid denied')
                    req=recv_obj(conn)
                    resp=adjudicate(req,state,jk,wk,trusted)
                except Exception as exc:resp={'state':'DENIED','authorized':False,'reason':str(exc)[:140]}
                try:send_obj(conn,resp)
                except (OSError,ConnectionError):pass
    finally:s.close();pathlib.Path(sockpath).unlink(missing_ok=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--socket',required=True);p.add_argument('--state',required=True);p.add_argument('--keys',required=True);p.add_argument('--uid',type=int,required=True)
    a=p.parse_args();serve(a.socket,a.state,a.keys,a.uid)
