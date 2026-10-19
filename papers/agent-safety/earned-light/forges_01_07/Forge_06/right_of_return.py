"""Earned Light Forge VI: offline Right-of-Return reference experiment.

No live external effects. A simulated provider commits local writes and notification
records. The controller is distinct from the provider database.  There is no
atomic transaction between them; uncertainty must be reconciled, not guessed.

This is an experimental protocol, not an authorization / cryptography library.
"""
from __future__ import annotations
import hashlib, hmac, json, secrets, sqlite3, time
from dataclasses import dataclass
from contextlib import contextmanager
from pathlib import Path
from typing import Optional


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False)


def digest(obj):
    return hashlib.sha256(canonical(obj).encode()).hexdigest()


class ReturnError(Exception): pass
class Rejected(ReturnError): pass
class Conflict(ReturnError): pass
class UnknownEffect(ReturnError): pass


@dataclass(frozen=True)
class OperatorRequest:
    action: str
    delegation: str
    nonce: str
    expires: int
    mac: str


def sign_operator_request(secret: bytes, action: str, delegation: str, *, nonce: str, expires: int):
    payload = dict(action=action, delegation=delegation, nonce=nonce, expires=expires)
    sig = hmac.new(secret, canonical(payload).encode(), hashlib.sha256).hexdigest()
    return OperatorRequest(**payload, mac=sig)


@contextmanager
def db(path):
    con = sqlite3.connect(str(path), isolation_level=None, timeout=5)
    try:
        con.row_factory = sqlite3.Row
        con.execute('PRAGMA journal_mode=WAL')
        con.execute('PRAGMA busy_timeout=5000')
        yield con
        if con.in_transaction: con.commit()
    except BaseException:
        if con.in_transaction: con.rollback()
        raise
    finally:
        con.close()


class SimulatedProvider:
    """A provider with durable operation IDs. Trust and service reachability are assumed."""
    def __init__(self, path):
        self.path = path
        with db(path) as c:
            c.execute('CREATE TABLE IF NOT EXISTS records (key TEXT PRIMARY KEY, value TEXT, version INTEGER NOT NULL, last_op TEXT)')
            c.execute('CREATE TABLE IF NOT EXISTS operations (op_id TEXT PRIMARY KEY, request_hash TEXT NOT NULL, kind TEXT NOT NULL, key TEXT NOT NULL, before_json TEXT, after_json TEXT, before_version INTEGER, after_version INTEGER, before_last_op TEXT, status TEXT NOT NULL)')
            c.execute('CREATE TABLE IF NOT EXISTS outbound (op_id TEXT PRIMARY KEY, destination TEXT NOT NULL, message TEXT NOT NULL)')
            c.execute('CREATE TABLE IF NOT EXISTS compensations (comp_id TEXT PRIMARY KEY, op_id TEXT NOT NULL, status TEXT NOT NULL, reason TEXT)')

    def seed(self, key, value):
        with db(self.path) as c:
            c.execute('BEGIN IMMEDIATE')
            if c.execute('SELECT key FROM records WHERE key=?', (key,)).fetchone():
                raise Conflict('seed key exists')
            c.execute('INSERT INTO records VALUES (?,?,?,?)', (key, canonical(value), 0, 'seed'))
            c.execute('COMMIT')

    def current(self, key):
        with db(self.path) as c:
            r = c.execute('SELECT * FROM records WHERE key=?', (key,)).fetchone()
        if r is None: return None
        return dict(key=r['key'], value=json.loads(r['value']), version=r['version'], last_op=r['last_op'])

    def receipt(self, op_id):
        with db(self.path) as c:
            r = c.execute('SELECT * FROM operations WHERE op_id=?', (op_id,)).fetchone()
            if not r: return None
            return dict(r)

    def apply(self, op_id, kind, key, value, expected_version=None):
        if kind not in ('write', 'notify'):
            raise Rejected('unrecognized kind')
        request_hash = digest(dict(kind=kind, key=key, value=value, expected_version=expected_version))
        with db(self.path) as c:
            c.execute('BEGIN IMMEDIATE')
            old = c.execute('SELECT * FROM operations WHERE op_id=?', (op_id,)).fetchone()
            if old:
                if old['request_hash'] != request_hash:
                    raise Conflict('idempotency key reused for different request')
                c.execute('COMMIT')
                return dict(old)
            if kind == 'notify':
                if not isinstance(value, dict) or not isinstance(value.get('message'), str):
                    raise Rejected('notification must contain message')
                c.execute('INSERT INTO outbound VALUES (?,?,?)', (op_id, key, value['message']))
                before, after, bv, av, blo = None, canonical(value), None, None, None
            else:
                record = c.execute('SELECT * FROM records WHERE key=?', (key,)).fetchone()
                actual_version = record['version'] if record else None
                if expected_version != actual_version:
                    raise Conflict('write precondition changed')
                before = record['value'] if record else None
                bv = actual_version
                blo = record['last_op'] if record else None
                av = (actual_version + 1) if actual_version is not None else 0
                after = canonical(value)
                c.execute('INSERT INTO records(key,value,version,last_op) VALUES(?,?,?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value,version=excluded.version,last_op=excluded.last_op', (key, after, av, op_id))
            c.execute('INSERT INTO operations VALUES (?,?,?,?,?,?,?,?,?,?)', (op_id, request_hash, kind, key, before, after, bv, av, blo, 'committed'))
            c.execute('COMMIT')
        return self.receipt(op_id)

    def human_write(self, key, value):
        """Simulates a nondelegated human modification between action and return."""
        op_id='human:'+secrets.token_hex(8)
        record=self.current(key)
        self.apply(op_id, 'write', key, value, record['version'] if record else None)
        return op_id

    def compensate(self, op_id, comp_id):
        with db(self.path) as c:
            c.execute('BEGIN IMMEDIATE')
            old = c.execute('SELECT * FROM compensations WHERE comp_id=?', (comp_id,)).fetchone()
            if old:
                if old['op_id'] != op_id: raise Conflict('compensation key collision')
                c.execute('COMMIT')
                return dict(old)
            original = c.execute('SELECT * FROM operations WHERE op_id=?', (op_id,)).fetchone()
            if not original: raise UnknownEffect('original operation not observable')
            if original['kind'] != 'write':
                result = ('irreversible', 'notification already emitted')
            else:
                actual = c.execute('SELECT * FROM records WHERE key=?', (original['key'],)).fetchone()
                # optimistic check avoids overwriting another actor's work
                if not actual or actual['last_op'] != op_id or actual['version'] < original['after_version'] or actual['value'] != original['after_json']:
                    result = ('conflict', 'provider value changed after original action')
                elif original['before_version'] is None:
                    c.execute('DELETE FROM records WHERE key=?', (original['key'],))
                    result = ('restored', 'record creation undone')
                else:
                    c.execute('UPDATE records SET value=?,version=?,last_op=? WHERE key=?', (original['before_json'], actual['version']+1, original['before_last_op'], original['key']))
                    result = ('restored', 'previous value restored with a new revision')
            c.execute('INSERT INTO compensations VALUES (?,?,?,?)', (comp_id, op_id, *result))
            c.execute('COMMIT')
            return dict(comp_id=comp_id, op_id=op_id, status=result[0], reason=result[1])


class ReturnController:
    """Tracks delegation, dispatch, revocation, reconciliation and return.

    Dispatch is reserved in controller before provider execution. A revocation
    blocks *new* dispatch, but cannot atomically stop an already dispatched call.
    """
    def __init__(self, path, provider: SimulatedProvider, operator_secret: bytes, *, clock=None):
        self.path, self.provider, self.secret = path, provider, operator_secret
        self.clock = clock if clock is not None else lambda: int(time.time())
        with db(path) as c:
            c.execute('CREATE TABLE IF NOT EXISTS delegations (id TEXT PRIMARY KEY, active INTEGER NOT NULL, epoch INTEGER NOT NULL, scope TEXT NOT NULL)')
            c.execute('CREATE TABLE IF NOT EXISTS intents (op_id TEXT PRIMARY KEY, delegation TEXT NOT NULL, epoch INTEGER NOT NULL, kind TEXT NOT NULL, key TEXT NOT NULL, value_json TEXT NOT NULL, expected_version INTEGER, status TEXT NOT NULL, provider_receipt_hash TEXT, compensation_status TEXT, compensation_reason TEXT)')
            c.execute('CREATE TABLE IF NOT EXISTS operator_nonces (nonce TEXT PRIMARY KEY, action TEXT NOT NULL, delegation TEXT NOT NULL)')

    def grant(self, delegation, allowed_kinds):
        if not allowed_kinds or set(allowed_kinds) - {'write', 'notify'}: raise Rejected('invalid kinds')
        with db(self.path) as c:
            c.execute('INSERT INTO delegations VALUES (?,?,?,?)', (delegation, 1, 0, canonical(sorted(set(allowed_kinds)))))

    def verify_operator(self, request: OperatorRequest, action: str, delegation: str, con):
        expected = sign_operator_request(self.secret, request.action, request.delegation, nonce=request.nonce, expires=request.expires)
        if not hmac.compare_digest(expected.mac, request.mac): raise Rejected('invalid operator authenticator')
        if request.action != action or request.delegation != delegation: raise Rejected('operator request context mismatch')
        if request.expires < self.clock(): raise Rejected('operator request expired')
        try:
            con.execute('INSERT INTO operator_nonces VALUES (?,?,?)', (request.nonce, action, delegation))
        except sqlite3.IntegrityError:
            raise Rejected('operator request replayed')

    def propose(self, delegation, op_id, kind, key, value, expected_version=None):
        if kind not in ('write','notify'): raise Rejected('invalid action')
        with db(self.path) as c:
            c.execute('BEGIN IMMEDIATE')
            grant=c.execute('SELECT * FROM delegations WHERE id=?', (delegation,)).fetchone()
            if not grant or not grant['active'] or kind not in json.loads(grant['scope']): raise Rejected('no active permission')
            c.execute('INSERT INTO intents VALUES (?,?,?,?,?,?,?,?,?,?,?)', (op_id,delegation,grant['epoch'],kind,key,canonical(value),expected_version,'proposed',None,None,None))
            c.execute('COMMIT')

    def dispatch(self, op_id, *, simulate_lost_ack=False, after_reservation=None):
        with db(self.path) as c:
            c.execute('BEGIN IMMEDIATE')
            intent=c.execute('SELECT * FROM intents WHERE op_id=?',(op_id,)).fetchone()
            if not intent or intent['status'] != 'proposed': raise Rejected('not a dispatchable proposal')
            grant=c.execute('SELECT * FROM delegations WHERE id=?',(intent['delegation'],)).fetchone()
            if not grant or not grant['active'] or grant['epoch'] != intent['epoch']:
                c.execute('UPDATE intents SET status=? WHERE op_id=?',('blocked',op_id))
                c.execute('COMMIT')
                return 'blocked'
            c.execute('UPDATE intents SET status=? WHERE op_id=?',('dispatched',op_id))
            c.execute('COMMIT')
        # Deliberate non-atomic boundary; a revocation may happen right here.
        if after_reservation is not None: after_reservation()
        try:
            receipt=self.provider.apply(op_id,intent['kind'],intent['key'],json.loads(intent['value_json']),intent['expected_version'])
        except ReturnError:
            # No safe inference: provider might have applied before a lost response.
            with db(self.path) as c: c.execute('UPDATE intents SET status=? WHERE op_id=?',('uncertain',op_id))
            raise
        if simulate_lost_ack:
            with db(self.path) as c: c.execute('UPDATE intents SET status=? WHERE op_id=?',('uncertain',op_id))
            return 'uncertain'
        with db(self.path) as c:
            c.execute('UPDATE intents SET status=?,provider_receipt_hash=? WHERE op_id=?',('confirmed',digest(receipt),op_id))
        return 'confirmed'

    def revoke(self, delegation, request):
        with db(self.path) as c:
            c.execute('BEGIN IMMEDIATE')
            self.verify_operator(request,'revoke',delegation,c)
            r=c.execute('SELECT * FROM delegations WHERE id=?',(delegation,)).fetchone()
            if not r: raise Rejected('unknown delegation')
            c.execute('UPDATE delegations SET active=0,epoch=epoch+1 WHERE id=?',(delegation,))
            c.execute('COMMIT')

    def reconcile(self, delegation):
        """Queries the simulated provider; no external independent witness exists."""
        outcomes=[]
        with db(self.path) as c:
            rows=c.execute('SELECT * FROM intents WHERE delegation=? ORDER BY rowid',(delegation,)).fetchall()
            for row in rows:
                if row['status'] not in ('dispatched','uncertain'): continue
                try:
                    receipt=self.provider.receipt(row['op_id'])
                except (OSError, TimeoutError, sqlite3.OperationalError):
                    outcomes.append((row['op_id'],'provider_unavailable'))
                    continue
                if receipt:
                    c.execute('UPDATE intents SET status=?,provider_receipt_hash=? WHERE op_id=?',('confirmed',digest(receipt),row['op_id']))
                    outcomes.append((row['op_id'],'confirmed'))
                else:
                    # A missing receipt does not prove the side effect did not occur.
                    outcomes.append((row['op_id'],'unresolved'))
        return outcomes

    def return_to_human(self, delegation, request):
        """Owner-authorized, repeatable reconciliation/compensation attempt.

        Returns per-action results, not a single misleading 'all restored' flag.
        """
        with db(self.path) as c:
            c.execute('BEGIN IMMEDIATE')
            self.verify_operator(request,'return',delegation,c)
            grant=c.execute('SELECT active FROM delegations WHERE id=?',(delegation,)).fetchone()
            if not grant or grant['active']: raise Rejected('must revoke first')
            c.execute('COMMIT')
        self.reconcile(delegation)
        with db(self.path) as c:
            rows=c.execute('SELECT * FROM intents WHERE delegation=? ORDER BY rowid DESC',(delegation,)).fetchall()
        reports=[]
        for item in rows:
            state=item['status']
            if state in ('proposed','blocked'):
                status='no_effect_dispatched'
            elif state in ('dispatched','uncertain'):
                status='unresolved_effect'
            else:
                comp_id='return:'+item['op_id']
                try:
                    comp=self.provider.compensate(item['op_id'],comp_id)
                    status=comp['status']
                    with db(self.path) as c:
                        c.execute('UPDATE intents SET compensation_status=?,compensation_reason=? WHERE op_id=?',(status,comp['reason'],item['op_id']))
                except (UnknownEffect, OSError, TimeoutError, sqlite3.OperationalError):
                    status='unresolved_effect'
            reports.append(dict(op_id=item['op_id'],kind=item['kind'],status=status))
        return reports

    def view(self, delegation):
        with db(self.path) as c:
            return [dict(r) for r in c.execute('SELECT * FROM intents WHERE delegation=? ORDER BY rowid',(delegation,))]


class SnapshotBaseline:
    """Intentionally weak control: naive snapshot overwrite, exposing lost updates."""
    @staticmethod
    def undo(provider, key, original):
        provider.human_write(key, original)
        return provider.current(key)


class ConventionalSagaBaseline:
    """Strong conventional comparison: supplied operation log and CAS compensation.

    Reverses in reverse order using the same provider implementation. Does not
    pretend conventional sagas are incapable of reconciliation or safe rollback.
    The difference Forge VI explores is operator-driven revocation/review, not
    superior compensation mathematics.
    """
    @staticmethod
    def compensate_all(provider, operation_ids):
        out=[]
        for op_id in reversed(operation_ids):
            try:
                r=provider.compensate(op_id,'saga:'+op_id)
                out.append(dict(op_id=op_id,status=r['status']))
            except UnknownEffect:
                out.append(dict(op_id=op_id,status='unresolved_effect'))
        return out
