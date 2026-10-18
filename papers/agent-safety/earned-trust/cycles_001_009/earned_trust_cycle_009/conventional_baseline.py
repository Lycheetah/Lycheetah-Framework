"""Independent conventional HMAC + SQLite idempotency reference.

Not part of Lycheetah; compares only the provider authorization/idempotency layer,
not evidence governance, human review, or the agent-facing socket.
"""
from __future__ import annotations
import hashlib,hmac,json,sqlite3,time
from pathlib import Path

def wire(v):return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def sign(key,payload):return hmac.new(key,wire(payload),hashlib.sha256).hexdigest()

class ConventionalProvider:
    def __init__(self,path,issuer_key):
        self.key=issuer_key;self.path=str(path)
        with sqlite3.connect(self.path) as db:
            db.execute('CREATE TABLE IF NOT EXISTS applied(effect TEXT PRIMARY KEY, payload_hash TEXT NOT NULL, dispatch INTEGER NOT NULL)')
    def apply(self,action,token,now=None):
        now=int(time.time()) if now is None else now
        if not isinstance(token,dict) or set(token)!={'body','signature'}:return 'DENIED'
        body=token['body']
        if not isinstance(body,dict):return 'DENIED'
        if not isinstance(token['signature'],str) or not hmac.compare_digest(sign(self.key,body),token['signature']):return 'DENIED'
        try:
            if (set(body)!={'v','issuer','kid','effect_id','action_hash','dispatch_seq','issued_at','expires_at'}
                or body['v']!=1 or body['issuer']!='trusted-gateway' or body['kid']!='gateway-v1'
                or not body['effect_id'] or type(body['dispatch_seq']) is not int or body['dispatch_seq']<1
                or type(body['issued_at']) is not int or type(body['expires_at']) is not int
                or body['issued_at']>now or now>=body['expires_at'] or not 1<=body['expires_at']-body['issued_at']<=60
                or set(action)!={'subject','tool','refund_cents'} or action['tool']!='refund.create'
                or not isinstance(action['subject'],str) or not action['subject']
                or type(action['refund_cents']) is not int or not 1<=action['refund_cents']<=100_000
                or hashlib.sha256(wire(action)).hexdigest()!=body['action_hash']):return 'DENIED'
        except (KeyError,ValueError,TypeError):return 'DENIED'
        with sqlite3.connect(self.path,timeout=20,isolation_level=None) as db:
            db.execute('BEGIN IMMEDIATE')
            old=db.execute('SELECT payload_hash,dispatch FROM applied WHERE effect=?',(body['effect_id'],)).fetchone()
            if old:
                db.execute('COMMIT')
                return 'REPLAY' if old==(body['action_hash'],body['dispatch_seq']) else 'DENIED'
            db.execute('INSERT INTO applied VALUES(?,?,?)',(body['effect_id'],body['action_hash'],body['dispatch_seq']))
            db.execute('COMMIT')
        return 'COMMITTED'
