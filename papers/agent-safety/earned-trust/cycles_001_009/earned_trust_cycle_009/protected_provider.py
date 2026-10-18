"""Earned Trust C009 — loopback-only capability-gated synthetic effect provider.

NO production security claim. HMAC keys and SQLite are held by the *trusted* service.
The untrusted agent may reach HTTP /v1/execute but may not read keys or DB.
Provider applies one exact JSON action per effect ID under SQLite BEGIN IMMEDIATE.
The authorization issuer is an assumed trusted gateway; compromised issuer
can authorize an unauthorized action. This is NOT a complete security sandbox.
"""
from __future__ import annotations
import hmac
import json
import sqlite3
import time
from dataclasses import dataclass
from hashlib import sha256
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from upstream_dispatch_fence import canonical, digest, mac, _ClosingConnection


def strict_json(raw: bytes) -> Any:
    def unique(pairs):
        obj={}
        for k,v in pairs:
            if k in obj: raise ValueError('duplicate JSON field')
            obj[k]=v
        return obj
    return json.loads(raw.decode('utf8'),object_pairs_hook=unique,parse_constant=lambda s: (_ for _ in ()).throw(ValueError('non-finite number')))


class CapabilityIssuer:
    """Only a trusted gateway may possess these keys. Never expose mint() to an agent."""
    def __init__(self,key:bytes,kid='gateway-v1'):
        if not isinstance(key,bytes) or len(key)<32: raise ValueError('32+ byte key required')
        if not kid: raise ValueError('kid required')
        self.key=key;self.kid=kid

    def mint(self,effect_id:str,action:dict,dispatch_seq:int, *, now:int|None=None,ttl:int=20)->dict:
        if type(ttl) is not int or not 1 <= ttl <= 60:raise ValueError('ttl 1..60')
        if not isinstance(effect_id,str) or not effect_id:raise ValueError('effect id')
        if type(dispatch_seq) is not int or dispatch_seq<1:raise ValueError('dispatch seq')
        now=int(time.time()) if now is None else now
        body={'v':1,'issuer':'trusted-gateway','kid':self.kid,'effect_id':effect_id,
              'action_hash':digest(action),'dispatch_seq':dispatch_seq,
              'issued_at':now,'expires_at':now+ttl}
        return {'body':body,'signature':mac(self.key,body)}


@dataclass(frozen=True)
class ProviderResult:
    status:int
    payload:dict


class ProtectedProvider:
    def __init__(self,path:str|Path, *, capability_keys:dict[str,bytes], receipt_key:bytes,
                 allowed_tool='refund.create'):
        if not isinstance(receipt_key,bytes) or len(receipt_key)<32:raise ValueError('receipt key required')
        if not capability_keys or any(len(k)<32 for k in capability_keys.values()):
            raise ValueError('trusted signing keys required')
        self.db=str(path);self.keys=dict(capability_keys);self.receipt_key=receipt_key
        self.allowed_tool=allowed_tool
        Path(self.db).parent.mkdir(parents=True,exist_ok=True)
        with self._db() as c:
            c.execute('PRAGMA journal_mode=WAL')
            c.execute('''CREATE TABLE IF NOT EXISTS applied(
               effect_id TEXT PRIMARY KEY, action_hash TEXT NOT NULL,
               dispatch_seq INTEGER NOT NULL, result_json TEXT NOT NULL)''')

    def _db(self):
        c=sqlite3.connect(self.db,timeout=15,isolation_level=None,factory=_ClosingConnection)
        c.row_factory=sqlite3.Row
        c.execute('PRAGMA busy_timeout=15000')
        c.execute('PRAGMA synchronous=FULL')
        return c

    def apply(self,action:dict, capability:dict, now:int|None=None)->ProviderResult:
        now=int(time.time()) if now is None else now
        if not isinstance(capability,dict) or set(capability)!={'body','signature'} or not isinstance(capability['body'],dict):
            return ProviderResult(401,{'error':'missing-capability'})
        body=capability['body']
        expected={'v','issuer','kid','effect_id','action_hash','dispatch_seq','issued_at','expires_at'}
        if set(body)!=expected or body.get('v')!=1 or body.get('issuer')!='trusted-gateway':
            return ProviderResult(401,{'error':'invalid-capability-format'})
        eid=body.get('effect_id');kid=body.get('kid'); key=self.keys.get(kid) if isinstance(kid,str) else None
        if not key or not isinstance(capability['signature'],str) or not hmac.compare_digest(mac(key,body),capability['signature']):
            return ProviderResult(401,{'error':'invalid-capability-signature'})
        if not isinstance(eid,str) or not eid or type(body.get('dispatch_seq')) is not int or body['dispatch_seq']<1:
            return ProviderResult(401,{'error':'invalid-action-binding'})
        if (type(body.get('issued_at')) is not int or type(body.get('expires_at')) is not int
            or body['issued_at']>now or now>=body['expires_at']
            or not 1<=body['expires_at']-body['issued_at']<=60):
            return ProviderResult(401,{'error':'expired-or-invalid-capability'})
        if not isinstance(action,dict) or set(action)!={'subject','refund_cents','tool'}:
            return ProviderResult(400,{'error':'invalid-action-shape'})
        if (not isinstance(action['subject'],str) or not action['subject'] or
            type(action['refund_cents']) is not int or not 1<=action['refund_cents']<=100_000 or
            action['tool']!=self.allowed_tool):
            return ProviderResult(403,{'error':'provider-action-policy'})
        try:
            hashed=digest(action)
        except (TypeError,ValueError,OverflowError):
            return ProviderResult(400,{'error':'invalid-action'})
        if not isinstance(body['action_hash'],str) or not hmac.compare_digest(hashed,body['action_hash']):
            return ProviderResult(403,{'error':'action-substitution'})
        with self._db() as c:
            c.execute('BEGIN IMMEDIATE')
            row=c.execute('SELECT * FROM applied WHERE effect_id=?',(eid,)).fetchone()
            if row:
                c.execute('COMMIT')
                if row['action_hash']!=hashed or row['dispatch_seq']!=body['dispatch_seq']:
                    return ProviderResult(409,{'error':'replay-mismatch'})
                out=json.loads(row['result_json']);return ProviderResult(200,{**out,'created':False})
            resp={'effect_id':eid,'action_hash':hashed,'outcome':'SUCCEEDED'}
            signed={**resp,'signature':mac(self.receipt_key,resp)}
            c.execute('INSERT INTO applied VALUES(?,?,?,?)',(eid,hashed,body['dispatch_seq'],canonical(signed).decode()))
            c.execute('COMMIT')
            return ProviderResult(201,{**signed,'created':True})

    def lookup(self,effect_id):
        with self._db() as c:
            row=c.execute('SELECT result_json FROM applied WHERE effect_id=?',(effect_id,)).fetchone()
            return json.loads(row['result_json']) if row else None

    def count(self):
        with self._db() as c:
            return c.execute('SELECT count(*) FROM applied').fetchone()[0]

    def revoke_signer(self,kid:str):
        self.keys.pop(kid,None)


def serve(provider:ProtectedProvider, host='127.0.0.1', port=0):
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            if self.path!='/v1/execute':return self._reply(404,{'error':'not-found'})
            if 'Transfer-Encoding' in self.headers:return self._reply(400,{'error':'unsupported-encoding'})
            try:
                n=int(self.headers.get('Content-Length','-1'))
                if n<0 or n>16_384:return self._reply(413,{'error':'size-limit'})
                req=strict_json(self.rfile.read(n))
                if not isinstance(req,dict) or set(req)!={'action','capability'}:
                    return self._reply(400,{'error':'invalid-request'})
                answer=provider.apply(req['action'],req['capability'])
                return self._reply(answer.status,answer.payload)
            except (ValueError,TypeError,UnicodeError,json.JSONDecodeError):
                return self._reply(400,{'error':'invalid-json'})
        def do_GET(self):return self._reply(405,{'error':'post-required'})
        def _reply(self,status,obj):
            data=canonical(obj)
            self.send_response(status);self.send_header('Content-Type','application/json')
            self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
        def log_message(self,*args):pass
    return ThreadingHTTPServer((host,port),Handler)
