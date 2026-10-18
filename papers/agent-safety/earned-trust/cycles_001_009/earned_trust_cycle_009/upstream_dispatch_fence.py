"""Earned Trust C007: SQLite-serialized authority/evidence/challenge/dispatch lab.

Synthetic reference controller, NOT a production broker or a replacement for
Lycheetah's actual FinalityGate / PersistentActionGuard. It only guarantees a
local ordering among cooperating clients using THIS SQLite database.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


def canonical(obj: object) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()


def digest(obj: object) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()


def mac(key: bytes, obj: object) -> str:
    return hmac.new(key, canonical(obj), hashlib.sha256).hexdigest()


@dataclass(frozen=True)
class Decision:
    allowed: bool
    reason: str
    state: str
    audit_seq: int | None = None


class _ClosingConnection(sqlite3.Connection):
    def __exit__(self, exc_type, exc, tb):
        try:
            return super().__exit__(exc_type, exc, tb)
        finally:
            self.close()


class Fence:
    """Permission/dispatch *claim* ordered with governance in one SQLite DB.

    All operations that change protected authorization state MUST enter through
    this broker and this database. External changes outside it are invisible.
    """
    def __init__(self, db: str | Path, *, approval_key: bytes, auditor_key: bytes,
                 reviewer_keys: Mapping[str, tuple[str, bytes]], fence_key: bytes,
                 source_parents: Mapping[str, tuple[str, ...]]):
        self.db = str(db)
        Path(self.db).parent.mkdir(parents=True, exist_ok=True)
        self.approval_key = approval_key
        self.auditor_key = auditor_key
        self.reviewers = dict(reviewer_keys)
        self.fence_key = fence_key
        self.parents = {name: tuple(parents) for name, parents in source_parents.items()}
        if not self.parents or any(not isinstance(name, str) or not name for name in self.parents):
            raise ValueError("trusted source graph required")
        visited, active = set(), set()
        def dfs(name):
            if name not in self.parents: raise ValueError("unregistered source ancestry")
            if name in active: raise ValueError("source graph cycle")
            if name in visited: return
            active.add(name)
            for parent in self.parents[name]: dfs(parent)
            active.remove(name);visited.add(name)
        for name in self.parents: dfs(name)
        self.graph_digest = digest(self.parents)
        if any(len(k) < 32 for k in [approval_key, auditor_key, fence_key]):
            raise ValueError("keys must be 32+ bytes")
        if len({org for org, key in self.reviewers.values()}) < 2:
            raise ValueError("need separate reviewing organizations")
        if any(len(key) < 32 for org, key in self.reviewers.values()):
            raise ValueError("reviewer key too short")
        with self._db() as c:
            c.executescript("""
                CREATE TABLE IF NOT EXISTS meta (id INTEGER PRIMARY KEY CHECK(id=1), rev INTEGER NOT NULL, head TEXT NOT NULL);
                INSERT OR IGNORE INTO meta VALUES(1,0,'GENESIS');
                CREATE TABLE IF NOT EXISTS epochs(actor TEXT PRIMARY KEY,epoch INTEGER NOT NULL);
                CREATE TABLE IF NOT EXISTS approvals (
                    approval_id TEXT PRIMARY KEY,actor TEXT NOT NULL,scope TEXT NOT NULL,action_hash TEXT NOT NULL,
                    expires INTEGER NOT NULL,epoch INTEGER NOT NULL);
                CREATE TABLE IF NOT EXISTS evidence (key TEXT PRIMARY KEY,revision INTEGER NOT NULL,
                    status TEXT NOT NULL,subject TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS disputes(source TEXT PRIMARY KEY,opened_seq INTEGER NOT NULL);
                CREATE TABLE IF NOT EXISTS used_nonces(nonce TEXT PRIMARY KEY);
                CREATE TABLE IF NOT EXISTS effects (
                    effect_id TEXT PRIMARY KEY,approval_id TEXT NOT NULL UNIQUE,action_hash TEXT NOT NULL,
                    actor TEXT NOT NULL,scope TEXT NOT NULL,dep_json TEXT NOT NULL,req_json TEXT NOT NULL,
                    status TEXT NOT NULL CHECK(status IN ('PREPARED','DISPATCHING','UNKNOWN','SUCCEEDED','FAILED')),
                    dispatch_seq INTEGER,result_json TEXT);
                CREATE TABLE IF NOT EXISTS audit (
                    seq INTEGER PRIMARY KEY AUTOINCREMENT,kind TEXT NOT NULL,detail TEXT NOT NULL,
                    prev_hash TEXT NOT NULL,hash TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS config (id INTEGER PRIMARY KEY CHECK(id=1), graph_digest TEXT NOT NULL);
            """)
            existing=c.execute('SELECT graph_digest FROM config WHERE id=1').fetchone()
            if existing is None:
                c.execute('INSERT INTO config VALUES(1,?)',(self.graph_digest,))
            elif existing['graph_digest'] != self.graph_digest:
                raise ValueError('source graph differs from database-bound version')

    def _db(self) -> sqlite3.Connection:
        c = sqlite3.connect(self.db, timeout=20, isolation_level=None, factory=_ClosingConnection)
        c.row_factory = sqlite3.Row
        c.execute("PRAGMA busy_timeout=20000")
        return c

    @staticmethod
    def _head(c):
        return c.execute("SELECT rev,head FROM meta WHERE id=1").fetchone()

    @staticmethod
    def _epoch(c, actor):
        r = c.execute("SELECT epoch FROM epochs WHERE actor=?", (actor,)).fetchone()
        return 0 if r is None else r['epoch']

    @staticmethod
    def _append(c,kind,detail):
        prev = c.execute("SELECT hash FROM audit ORDER BY seq DESC LIMIT 1").fetchone()
        last = prev['hash'] if prev else 'AUDIT_GENESIS'
        cur = c.execute("INSERT INTO audit(kind,detail,prev_hash,hash) VALUES(?,?,?,?)",
                        (kind,canonical(detail).decode(),last,''))
        seq = cur.lastrowid
        rowhash = digest({'seq':seq,'kind':kind,'detail':detail,'prev':last})
        c.execute("UPDATE audit SET hash=? WHERE seq=?",(rowhash,seq))
        return seq

    @staticmethod
    def _verify_audit_conn(c):
        expected_prev='AUDIT_GENESIS'
        rows=c.execute("SELECT * FROM audit ORDER BY seq").fetchall()
        for index,r in enumerate(rows,1):
            if r['seq'] != index or r['prev_hash'] != expected_prev:
                return False
            try:
                expected=digest({'seq':r['seq'],'kind':r['kind'],
                                 'detail':json.loads(r['detail']),'prev':expected_prev})
            except (ValueError, TypeError):
                return False
            if not hmac.compare_digest(r['hash'],expected):
                return False
            expected_prev=r['hash']
        return True

    def verify_audit(self):
        with self._db() as c:
            return self._verify_audit_conn(c)

    def _closure(self, ids):
        all_ids=set()
        def visit(sid):
            if sid not in self.parents: raise ValueError('unknown source')
            if sid in all_ids:return
            all_ids.add(sid)
            for upstream in self.parents[sid]:visit(upstream)
        for sid in ids:visit(sid)
        return sorted(all_ids)

    def governance_head(self):
        with self._db() as c:
            r=self._head(c)
            return {'revision':r['rev'],'head':r['head']}

    def _advance_head(self,c,kind,body):
        row=self._head(c)
        newrev=row['rev']+1
        newhead=digest({'previous':row['head'],'revision':newrev,'kind':kind,'body':body})
        c.execute("UPDATE meta SET rev=?,head=? WHERE id=1",(newrev,newhead))
        return newrev,newhead

    def approval_body(self,approval_id,actor,action,scope,expires):
        return {'approval_id':approval_id,'actor':actor,'action_hash':digest(action),
                'scope':scope,'expires':expires}

    def sign_approval(self,body):
        """Only fixture support; real issuer must own the separate approval key."""
        return mac(self.approval_key,body)

    def approve(self,body,signature):
        if not isinstance(signature,str) or not hmac.compare_digest(signature,mac(self.approval_key,body)):
            return False
        if set(body) != {'approval_id','actor','action_hash','scope','expires'}:
            return False
        if type(body['expires']) is not int or body['expires']<1:
            return False
        with self._db() as c:
            c.execute('BEGIN IMMEDIATE')
            if not self._verify_audit_conn(c):
                c.execute('ROLLBACK'); return False
            try:
                c.execute("INSERT INTO approvals VALUES(?,?,?,?,?,?)",(
                    body['approval_id'],body['actor'],body['scope'],body['action_hash'],
                    body['expires'],self._epoch(c,body['actor'])))
            except sqlite3.IntegrityError:
                c.execute('ROLLBACK');return False
            self._append(c,'APPROVED',body)
            c.execute('COMMIT')
        return True

    def prepare(self,effect_id,approval_id,action,scope,dependencies,requirements):
        if not effect_id or not isinstance(dependencies,(tuple,list)) or not dependencies:
            return False
        if not isinstance(requirements,dict) or not requirements:
            return False
        if any(not isinstance(x,str) or not x for x in dependencies):
            return False
        try:
            resolved_dependencies=self._closure(dependencies)
        except ValueError:
            return False
        with self._db() as c:
            c.execute('BEGIN IMMEDIATE')
            a=c.execute("SELECT * FROM approvals WHERE approval_id=?",(approval_id,)).fetchone()
            if (a is None or a['scope']!=scope or a['action_hash']!=digest(action)
                    or a['epoch']!=self._epoch(c,a['actor'])):
                c.execute('ROLLBACK');return False
            for key,expected in requirements.items():
                record=c.execute('SELECT * FROM evidence WHERE key=?',(key,)).fetchone()
                if (not record or record['status']!='PASS' or record['revision'] != expected
                        or record['subject'] != action.get('subject')):
                    c.execute('ROLLBACK');return False
            try:
                c.execute("INSERT INTO effects VALUES(?,?,?,?,?,?,?,?,NULL,NULL)",(
                    effect_id,approval_id,digest(action),a['actor'],scope,
                    canonical(resolved_dependencies).decode(),canonical(requirements).decode(),
                    'PREPARED'))
            except sqlite3.IntegrityError:
                c.execute('ROLLBACK');return False
            self._append(c,'PREPARED',{'effect_id':effect_id,'approval_id':approval_id})
            c.execute('COMMIT');return True

    def update_evidence(self,key,revision,status,subject):
        if status not in {'PASS','FAIL'} or type(revision) is not int or revision<1:
            return False
        with self._db() as c:
            c.execute('BEGIN IMMEDIATE')
            r=c.execute('SELECT revision FROM evidence WHERE key=?',(key,)).fetchone()
            if r and revision<=r['revision']:
                c.execute('ROLLBACK');return False
            c.execute("INSERT INTO evidence VALUES(?,?,?,?) ON CONFLICT(key) DO UPDATE SET revision=excluded.revision,status=excluded.status,subject=excluded.subject",(key,revision,status,subject))
            self._append(c,'EVIDENCE_UPDATED',{'key':key,'revision':revision,'status':status,'subject':subject})
            c.execute('COMMIT')
        return True

    def challenge_body(self,source,nonce):
        return {'kind':'CHALLENGE','source':source,'nonce':nonce}

    def sign_challenge(self,body):
        return mac(self.auditor_key,body)

    def challenge(self,body,signature):
        if set(body)!={'kind','source','nonce'} or body['kind']!='CHALLENGE' or body['source'] not in self.parents or not body['nonce']:
            return False
        if not isinstance(signature,str) or not hmac.compare_digest(signature,mac(self.auditor_key,body)):
            return False
        with self._db() as c:
            c.execute('BEGIN IMMEDIATE')
            if c.execute('SELECT 1 FROM used_nonces WHERE nonce=?',(body['nonce'],)).fetchone():
                c.execute('ROLLBACK');return False
            if c.execute('SELECT 1 FROM disputes WHERE source=?',(body['source'],)).fetchone():
                c.execute('ROLLBACK');return False
            c.execute('INSERT INTO used_nonces VALUES(?)',(body['nonce'],))
            seq=self._append(c,'CHALLENGE',body)
            c.execute('INSERT INTO disputes VALUES(?,?)',(body['source'],seq))
            self._advance_head(c,'CHALLENGE',body)
            c.execute('COMMIT')
        return True

    def resolution_body(self,source,nonce):
        return {'kind':'RESOLVE','source':source,'nonce':nonce}

    def sign_resolution(self,body,reviewer):
        return {'reviewer':reviewer,'mac':mac(self.reviewers[reviewer][1],body)}

    def resolve(self,body,signatures):
        if set(body)!={'kind','source','nonce'} or body['kind']!='RESOLVE' or body['source'] not in self.parents:
            return False
        if not isinstance(signatures,(list,tuple)) or len(signatures)<2:
            return False
        orgs=set(); names=set()
        for sig in signatures:
            if not isinstance(sig,dict) or set(sig)!={'reviewer','mac'}:
                return False
            rid=sig['reviewer']
            if rid not in self.reviewers or rid in names:
                return False
            org,key=self.reviewers[rid]
            if not isinstance(sig['mac'],str) or not hmac.compare_digest(sig['mac'],mac(key,body)):
                return False
            names.add(rid);orgs.add(org)
        if len(orgs)<2:
            return False
        with self._db() as c:
            c.execute('BEGIN IMMEDIATE')
            if c.execute('SELECT 1 FROM used_nonces WHERE nonce=?',(body['nonce'],)).fetchone():
                c.execute('ROLLBACK');return False
            if not c.execute('SELECT 1 FROM disputes WHERE source=?',(body['source'],)).fetchone():
                c.execute('ROLLBACK');return False
            c.execute('INSERT INTO used_nonces VALUES(?)',(body['nonce'],))
            c.execute('DELETE FROM disputes WHERE source=?',(body['source'],))
            self._append(c,'RESOLVE',body)
            self._advance_head(c,'RESOLVE',body)
            c.execute('COMMIT');return True

    def revoke(self,actor):
        with self._db() as c:
            c.execute('BEGIN IMMEDIATE')
            epoch=self._epoch(c,actor)+1
            c.execute('INSERT INTO epochs VALUES(?,?) ON CONFLICT(actor) DO UPDATE SET epoch=excluded.epoch',(actor,epoch))
            seq=self._append(c,'REVOKE',{'actor':actor,'epoch':epoch})
            c.execute('COMMIT')
            return seq

    def witness(self,effect_id):
        """Sealed short-lived *local snapshot*, not a provider-signed observation."""
        with self._db() as c:
            e=c.execute('SELECT * FROM effects WHERE effect_id=?',(effect_id,)).fetchone()
            if e is None or e['status'] != 'PREPARED':
                return None
            m=self._head(c)
            req=json.loads(e['req_json'])
            current={}
            for key in req:
                row=c.execute('SELECT * FROM evidence WHERE key=?',(key,)).fetchone()
                if row is None:
                    return None
                current[key]={'revision':row['revision'],'status':row['status'],'subject':row['subject']}
            body={'schema':'ET-C007-WITNESS','effect_id':effect_id,'action_hash':e['action_hash'],
                  'governance_head':m['head'],'governance_revision':m['rev'],
                  'authority_epoch':self._epoch(c,e['actor']), 'evidence':current}
            return {'body':body,'seal':mac(self.fence_key,body)}

    def claim(self,effect_id,action,witness,now):
        """The last locally serialized permission check, NOT remote effect commit."""
        with self._db() as c:
            c.execute('BEGIN IMMEDIATE')
            if not self._verify_audit_conn(c):
                c.execute('ROLLBACK');return Decision(False,'audit-corrupted','REVIEW')
            config=c.execute('SELECT graph_digest FROM config WHERE id=1').fetchone()
            if config is None or config['graph_digest']!=self.graph_digest:
                c.execute('ROLLBACK');return Decision(False,'graph-configuration-mismatch','REVIEW')
            e=c.execute('SELECT * FROM effects WHERE effect_id=?',(effect_id,)).fetchone()
            if e is None:
                c.execute('ROLLBACK');return Decision(False,'missing-effect','MISSING')
            status=e['status']
            if status!='PREPARED':
                c.execute('ROLLBACK');return Decision(False,'effect-already-claimed',status)
            if not isinstance(witness,dict) or set(witness)!={'body','seal'} or not isinstance(witness['body'],dict):
                c.execute('ROLLBACK');return Decision(False,'missing-witness',status)
            body=witness['body']
            if not isinstance(witness['seal'],str) or not hmac.compare_digest(mac(self.fence_key,body),witness['seal']):
                c.execute('ROLLBACK');return Decision(False,'bad-witness-seal',status)
            if body.get('effect_id')!=effect_id or body.get('action_hash')!=e['action_hash'] or digest(action)!=e['action_hash']:
                c.execute('ROLLBACK');return Decision(False,'action-substitution',status)
            m=self._head(c)
            if body.get('governance_head')!=m['head'] or body.get('governance_revision')!=m['rev']:
                c.execute('ROLLBACK');return Decision(False,'stale-governance',status)
            if body.get('authority_epoch')!=self._epoch(c,e['actor']):
                c.execute('ROLLBACK');return Decision(False,'revoked',status)
            approval=c.execute('SELECT * FROM approvals WHERE approval_id=?',(e['approval_id'],)).fetchone()
            if approval is None or approval['epoch']!=self._epoch(c,e['actor']) or now>=approval['expires']:
                c.execute('ROLLBACK');return Decision(False,'approval-invalid',status)
            dep=json.loads(e['dep_json'])
            if any(c.execute('SELECT 1 FROM disputes WHERE source=?',(sid,)).fetchone() for sid in dep):
                c.execute('ROLLBACK');return Decision(False,'source-challenged',status)
            req=json.loads(e['req_json'])
            seen=body.get('evidence')
            if not isinstance(seen,dict) or set(seen)!=set(req):
                c.execute('ROLLBACK');return Decision(False,'evidence-binding-invalid',status)
            for key,wanted_revision in req.items():
                record=c.execute('SELECT * FROM evidence WHERE key=?',(key,)).fetchone()
                if (record is None or record['revision']!=wanted_revision or record['status']!='PASS'
                    or record['subject']!=action.get('subject')
                    or seen[key]!={'revision':record['revision'],'status':record['status'],'subject':record['subject']}):
                    c.execute('ROLLBACK');return Decision(False,'evidence-stale',status)
            c.execute("UPDATE effects SET status='DISPATCHING' WHERE effect_id=? AND status='PREPARED'",(effect_id,))
            seq=self._append(c,'DISPATCH_CLAIMED',{'effect_id':effect_id,'governance_revision':m['rev']})
            c.execute('UPDATE effects SET dispatch_seq=? WHERE effect_id=?',(seq,effect_id))
            c.execute('COMMIT');return Decision(True,'locally-dispatchable','DISPATCHING',seq)

    def result(self,effect_id,outcome,details=None):
        if outcome not in {'SUCCEEDED','FAILED','UNKNOWN'}:
            return False
        with self._db() as c:
            c.execute('BEGIN IMMEDIATE')
            e=c.execute('SELECT status FROM effects WHERE effect_id=?',(effect_id,)).fetchone()
            if e is None or e['status']!='DISPATCHING':
                c.execute('ROLLBACK');return False
            c.execute('UPDATE effects SET status=?,result_json=? WHERE effect_id=?',
                      (outcome,canonical(details or {}).decode(),effect_id))
            self._append(c,'RESULT',{'effect_id':effect_id,'outcome':outcome})
            c.execute('COMMIT');return True

    def state(self,effect_id):
        with self._db() as c:
            e=c.execute('SELECT * FROM effects WHERE effect_id=?',(effect_id,)).fetchone()
            return dict(e) if e else None

    def audit_events(self):
        with self._db() as c:
            return [dict(x) for x in c.execute('SELECT * FROM audit ORDER BY seq')]
