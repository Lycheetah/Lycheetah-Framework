"""Earned Trust C008 — crash-observable dispatch outbox on the C007 SQLite authority.

RESEARCH LAB ONLY. Does not commit real remote effects or solve distributed atomicity.
The C007 source is copied byte-for-byte as upstream_dispatch_fence.py. This file
adds an outbox in that very same database and makes send reservation atomic with
all C007 predicates. No imported software from actual Lycheetah Framework.
"""
from __future__ import annotations

import hmac
import json
import sqlite3
from pathlib import Path
from typing import Any

from upstream_dispatch_fence import Fence, Decision, _ClosingConnection, digest, mac, canonical


class CrashSafeAuthority(Fence):
    def __init__(self, db, *, provider_receipt_key: bytes, **kwargs):
        if not isinstance(provider_receipt_key, bytes) or len(provider_receipt_key)<32:
            raise ValueError('trusted provider receipt key required')
        self.provider_receipt_key=provider_receipt_key
        super().__init__(db, **kwargs)
        with self._db() as c:
            c.execute('PRAGMA journal_mode=WAL')
            c.execute('PRAGMA synchronous=FULL')
            c.executescript('''
                CREATE TABLE IF NOT EXISTS outbox(
                    effect_id TEXT PRIMARY KEY REFERENCES effects(effect_id),
                    state TEXT NOT NULL CHECK(state IN ('PENDING','SENDING','UNKNOWN','ACKED','FAILED','CANCELLED')),
                    attempt INTEGER NOT NULL DEFAULT 0 CHECK(attempt BETWEEN 0 AND 1),
                    provider_key TEXT NOT NULL UNIQUE,
                    receipt TEXT,
                    reserve_audit_seq INTEGER);
            ''')

    def _db(self):
        c = super()._db()
        c.execute('PRAGMA foreign_keys=ON')
        c.execute('PRAGMA synchronous=FULL')
        return c

    @staticmethod
    def _state_consistent(c) -> bool:
        """Detect materialized-state edits inconsistent with the local audit sequence.

        This is NOT an external anchor: privileged rewriting of both data and all
        hashes remains possible. Detects ordinary single-table tampering.
        """
        try:
            history={}
            for row in c.execute("SELECT seq,kind,detail FROM audit ORDER BY seq"):
                if row['kind'] not in ('OUTBOX_ENQUEUED','SEND_RESERVED','DELIVERY_OUTCOME_UNKNOWN','PROVIDER_RECONCILED'):
                    continue
                event=json.loads(row['detail'])
                eid=event['effect_id']
                history.setdefault(eid,[]).append((row['seq'],row['kind']))
            for row in c.execute("""SELECT o.*,e.status AS effect_status,e.dispatch_seq
                                    FROM outbox o LEFT JOIN effects e ON e.effect_id=o.effect_id"""):
                eid=row['effect_id']; state=row['state']; effect=row['effect_status']
                if effect is None or row['provider_key'] != eid:
                    return False
                allowed={'PENDING':'PREPARED','SENDING':'DISPATCHING',
                         'UNKNOWN':'UNKNOWN','ACKED':'SUCCEEDED',
                         'FAILED':'FAILED','CANCELLED':'CANCELLED'}
                if allowed.get(state)!=effect:
                    return False
                events=history.get(eid,[])
                kinds=[x[1] for x in events]
                reservations=[x[0] for x in events if x[1]=='SEND_RESERVED']
                if kinds.count('OUTBOX_ENQUEUED')!=1:
                    return False
                if state=='PENDING':
                    if row['attempt']!=0 or reservations or row['reserve_audit_seq'] is not None or row['dispatch_seq'] is not None:
                        return False
                else:
                    if row['attempt']!=1 or len(reservations)!=1 or row['reserve_audit_seq']!=reservations[0] or row['dispatch_seq']!=reservations[0]:
                        return False
                if state=='UNKNOWN' and 'DELIVERY_OUTCOME_UNKNOWN' not in kinds:
                    return False
                if state in ('ACKED','FAILED') and 'PROVIDER_RECONCILED' not in kinds:
                    return False
            for eid,events in history.items():
                if not c.execute('SELECT 1 FROM outbox WHERE effect_id=?',(eid,)).fetchone():
                    return False
            return True
        except (ValueError,TypeError,KeyError,sqlite3.Error):
            return False

    def verify_state_consistency(self) -> bool:
        with self._db() as c:
            return self._verify_audit_conn(c) and self._state_consistent(c)

    def enqueue(self, effect_id: str) -> bool:
        """Durably make a PREPARED effect eligible for later reservation."""
        with self._db() as c:
            c.execute('BEGIN IMMEDIATE')
            if not self._verify_audit_conn(c) or not self._state_consistent(c):
                c.execute('ROLLBACK'); return False
            e=c.execute('SELECT status FROM effects WHERE effect_id=?',(effect_id,)).fetchone()
            if e is None or e['status']!='PREPARED':
                c.execute('ROLLBACK'); return False
            try:
                c.execute("INSERT INTO outbox(effect_id,state,provider_key) VALUES(?,'PENDING',?)",
                          (effect_id, effect_id))
            except sqlite3.IntegrityError:
                c.execute('ROLLBACK'); return False
            self._append(c,'OUTBOX_ENQUEUED',{'effect_id':effect_id})
            c.execute('COMMIT'); return True

    def reserve_send(self, effect_id: str, action: dict, witness: dict, now: int) -> Decision:
        """Atomic local linearization: validate C007 invariants and claim outbox.

        This returns permission to *attempt* an external send. A crash after this
        commit must be treated as uncertain and must not silently resend.
        """
        with self._db() as c:
            c.execute('BEGIN IMMEDIATE')
            if not self._verify_audit_conn(c):
                c.execute('ROLLBACK'); return Decision(False,'audit-corrupted','REVIEW')
            if not self._state_consistent(c):
                c.execute('ROLLBACK'); return Decision(False,'state-inconsistent','REVIEW')
            cfg=c.execute('SELECT graph_digest FROM config WHERE id=1').fetchone()
            if cfg is None or cfg['graph_digest']!=self.graph_digest:
                c.execute('ROLLBACK'); return Decision(False,'graph-configuration-mismatch','REVIEW')
            e=c.execute('SELECT * FROM effects WHERE effect_id=?',(effect_id,)).fetchone()
            o=c.execute('SELECT * FROM outbox WHERE effect_id=?',(effect_id,)).fetchone()
            if not e or not o:
                c.execute('ROLLBACK'); return Decision(False,'missing-effect-or-outbox','MISSING')
            if e['status']!='PREPARED' or o['state']!='PENDING' or o['attempt']!=0:
                c.execute('ROLLBACK'); return Decision(False,'already-reserved-or-resolved',o['state'])
            if not isinstance(witness,dict) or set(witness)!={'body','seal'} or not isinstance(witness['body'],dict):
                c.execute('ROLLBACK'); return Decision(False,'missing-witness','PENDING')
            body=witness['body']
            try:
                valid_seal=isinstance(witness['seal'],str) and hmac.compare_digest(mac(self.fence_key,body),witness['seal'])
                exact_action=digest(action)==e['action_hash']
            except (ValueError,TypeError,OverflowError):
                valid_seal=False; exact_action=False
            if not valid_seal:
                c.execute('ROLLBACK'); return Decision(False,'bad-witness-seal','PENDING')
            if body.get('effect_id')!=effect_id or body.get('action_hash')!=e['action_hash'] or not exact_action:
                c.execute('ROLLBACK'); return Decision(False,'action-substitution','PENDING')
            m=self._head(c)
            if body.get('governance_head')!=m['head'] or body.get('governance_revision')!=m['rev']:
                c.execute('ROLLBACK'); return Decision(False,'stale-governance','PENDING')
            if body.get('authority_epoch')!=self._epoch(c,e['actor']):
                c.execute('ROLLBACK'); return Decision(False,'revoked','PENDING')
            approval=c.execute('SELECT * FROM approvals WHERE approval_id=?',(e['approval_id'],)).fetchone()
            if approval is None or approval['epoch']!=self._epoch(c,e['actor']) or now>=approval['expires']:
                c.execute('ROLLBACK'); return Decision(False,'approval-invalid','PENDING')
            dependencies=json.loads(e['dep_json'])
            if any(c.execute('SELECT 1 FROM disputes WHERE source=?',(sid,)).fetchone() for sid in dependencies):
                c.execute('ROLLBACK'); return Decision(False,'source-challenged','PENDING')
            req=json.loads(e['req_json'])
            seen=body.get('evidence')
            if not isinstance(seen,dict) or set(seen)!=set(req):
                c.execute('ROLLBACK'); return Decision(False,'evidence-binding-invalid','PENDING')
            for key,revision in req.items():
                row=c.execute('SELECT * FROM evidence WHERE key=?',(key,)).fetchone()
                if (row is None or row['revision']!=revision or row['status']!='PASS'
                    or row['subject']!=action.get('subject') or
                    seen[key]!={'revision':row['revision'],'status':row['status'],'subject':row['subject']}):
                    c.execute('ROLLBACK'); return Decision(False,'evidence-stale','PENDING')
            c.execute("UPDATE effects SET status='DISPATCHING' WHERE effect_id=?",(effect_id,))
            seq=self._append(c,'SEND_RESERVED',{'effect_id':effect_id,'head':m['head']})
            c.execute('UPDATE effects SET dispatch_seq=? WHERE effect_id=?',(seq,effect_id))
            c.execute("UPDATE outbox SET state='SENDING',attempt=1,reserve_audit_seq=? WHERE effect_id=?",(seq,effect_id))
            c.execute('COMMIT')
            return Decision(True,'send-reserved-not-provider-confirmed','SENDING',seq)

    def recover(self) -> int:
        """Startup recovery: IN_FLIGHT becomes UNKNOWN; never automatic replay."""
        with self._db() as c:
            c.execute('BEGIN IMMEDIATE')
            if not self._verify_audit_conn(c) or not self._state_consistent(c):
                c.execute('ROLLBACK'); raise RuntimeError('audit-or-state-corrupted')
            ids=[r['effect_id'] for r in c.execute("SELECT effect_id FROM outbox WHERE state='SENDING' ORDER BY effect_id")]
            for eid in ids:
                c.execute("UPDATE outbox SET state='UNKNOWN' WHERE effect_id=?",(eid,))
                c.execute("UPDATE effects SET status='UNKNOWN' WHERE effect_id=? AND status='DISPATCHING'",(eid,))
                self._append(c,'DELIVERY_OUTCOME_UNKNOWN',{'effect_id':eid})
            c.execute('COMMIT'); return len(ids)

    def acknowledge(self, effect_id: str, result: dict) -> bool:
        """Only supply result from a trustworthy provider observation in this lab."""
        if not isinstance(result,dict) or result.get('effect_id')!=effect_id or result.get('outcome') not in ('SUCCEEDED','FAILED'):
            return False
        if not set(result).issubset({'effect_id','outcome','action_hash','signature','created'}) or not {'effect_id','outcome','action_hash','signature'}.issubset(result):
            return False
        body={k:result[k] for k in ('effect_id','outcome','action_hash')}
        if not isinstance(result['signature'],str) or not hmac.compare_digest(mac(self.provider_receipt_key,body),result['signature']):
            return False
        with self._db() as c:
            c.execute('BEGIN IMMEDIATE')
            if not self._verify_audit_conn(c) or not self._state_consistent(c):
                c.execute('ROLLBACK'); return False
            o=c.execute('SELECT state FROM outbox WHERE effect_id=?',(effect_id,)).fetchone()
            e=c.execute('SELECT action_hash FROM effects WHERE effect_id=?',(effect_id,)).fetchone()
            if not o or not e or e['action_hash']!=body['action_hash'] or o['state'] not in ('SENDING','UNKNOWN'):
                c.execute('ROLLBACK'); return False
            new='ACKED' if result['outcome']=='SUCCEEDED' else 'FAILED'
            c.execute('UPDATE outbox SET state=?,receipt=? WHERE effect_id=?',(new,canonical(result).decode(),effect_id))
            c.execute('UPDATE effects SET status=?,result_json=? WHERE effect_id=?',
                      (result['outcome'],canonical(result).decode(),effect_id))
            self._append(c,'PROVIDER_RECONCILED',{'effect_id':effect_id,'outcome':result['outcome']})
            c.execute('COMMIT'); return True

    def state_pair(self, effect_id):
        with self._db() as c:
            e=c.execute('SELECT status FROM effects WHERE effect_id=?',(effect_id,)).fetchone()
            o=c.execute('SELECT * FROM outbox WHERE effect_id=?',(effect_id,)).fetchone()
            return {'effect':e['status'] if e else None,'outbox':dict(o) if o else None}


class SimulatedIdempotentProvider:
    """Separate SQLite DB, idempotency and HMAC receipt. No network or money."""
    def __init__(self, db, *, receipt_key: bytes):
        if not isinstance(receipt_key,bytes) or len(receipt_key)<32: raise ValueError('receipt key required')
        self.receipt_key=receipt_key
        self.db=str(db)
        Path(self.db).parent.mkdir(parents=True,exist_ok=True)
        with self._db() as c:
            c.execute('PRAGMA journal_mode=WAL')
            c.execute('''CREATE TABLE IF NOT EXISTS applied (
                effect_id TEXT PRIMARY KEY,action_hash TEXT NOT NULL,
                response TEXT NOT NULL)''')

    def _db(self):
        c=sqlite3.connect(self.db,timeout=20,isolation_level=None,factory=_ClosingConnection)
        c.row_factory=sqlite3.Row
        c.execute('PRAGMA synchronous=FULL')
        c.execute('PRAGMA busy_timeout=20000')
        return c

    def apply(self,effect_id,action):
        """No second write for the same effect_id; mismatched payload rejected."""
        hashed=digest(action)
        with self._db() as c:
            c.execute('BEGIN IMMEDIATE')
            row=c.execute('SELECT * FROM applied WHERE effect_id=?',(effect_id,)).fetchone()
            if row:
                c.execute('COMMIT')
                if row['action_hash']!=hashed:
                    return {'effect_id':effect_id,'outcome':'REJECTED_MISMATCH','created':False}
                result=json.loads(row['response']);result['created']=False
                return result
            body={'effect_id':effect_id,'outcome':'SUCCEEDED','action_hash':hashed}
            result={**body,'signature':mac(self.receipt_key,body)}
            c.execute('INSERT INTO applied VALUES(?,?,?)',(effect_id,hashed,canonical(result).decode()))
            c.execute('COMMIT'); return {**result,'created':True}

    def lookup(self,effect_id):
        with self._db() as c:
            row=c.execute('SELECT response FROM applied WHERE effect_id=?',(effect_id,)).fetchone()
            return json.loads(row['response']) if row else None

    def count(self):
        with self._db() as c:
            return c.execute('SELECT count(*) FROM applied').fetchone()[0]
