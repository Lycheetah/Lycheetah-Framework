"""Cycle 11: signed, privacy-minimized, append-only local review-decision journal.

A journal signature proves control of a configured local HMAC key, not that a
particular person reviewed evidence. Hash chains require an externally retained
head to detect deletion/replacement of an entire local database.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import hmac
import json
import re
import secrets
import sqlite3

from .authorization import ReviewKeyring, batch_digest
from .core import canonical_digest, json_bytes

PURPOSE = 'lycheetah.hybrid-gateway.review-decision.v1'
DIGEST_PATTERN = re.compile(r'sha256:[0-9a-f]{64}\Z')


@dataclass(frozen=True)
class ReviewJournalAuthority:
    """Trusted server-side witness; never create from untrusted HTTP parameters."""
    key_id: str
    secret: bytes
    ledger_id: str
    presentation_digest: str
    batch_fingerprint: str

    def __post_init__(self):
        ReviewKeyring({self.key_id: self.secret})
        if not isinstance(self.ledger_id, str) or not re.fullmatch('[0-9a-f]{48}',self.ledger_id):
            raise ValueError('invalid ledger identity')
        for digest in (self.presentation_digest, self.batch_fingerprint):
            if not isinstance(digest,str) or not DIGEST_PATTERN.fullmatch(digest):
                raise ValueError('invalid journal digest')


@dataclass(frozen=True)
class ReviewDecisionRecord:
    purpose: str
    seq: int
    prior_hash: str | None
    action: str
    reason_code: str
    key_id: str
    nonce: str
    ledger_id: str
    batch_digest: str
    plan_fingerprint: str
    source_digest: str
    registry_fingerprint: str
    presentation_digest: str
    ledger_head_at_stage: str | None
    knowledge_event_hash: str | None
    decided_at: str
    signature: str
    entry_hash: str

    def unsigned(self) -> dict:
        return {k: v for k,v in asdict(self).items() if k not in ('signature','entry_hash')}


def initialize_schema(conn: sqlite3.Connection):
    conn.execute('''CREATE TABLE IF NOT EXISTS review_decisions
        (seq INTEGER PRIMARY KEY, batch_digest TEXT NOT NULL UNIQUE,
         entry_hash TEXT NOT NULL UNIQUE, payload TEXT NOT NULL)''')


def _last_record(conn):
    row=conn.execute('SELECT seq,payload FROM review_decisions ORDER BY seq DESC LIMIT 1').fetchone()
    return None if row is None else ReviewDecisionRecord(**json.loads(row['payload']))


def append_decision(conn, *, authority: ReviewJournalAuthority, batch, plan,
                    action: str, reason_code: str, event_hash: str | None,
                    ledger_id: str):
    """Call only inside an active BEGIN IMMEDIATE transaction. Never commits itself."""
    if not conn.in_transaction:
        raise ValueError('journal append requires caller transaction')
    if not isinstance(authority,ReviewJournalAuthority) or authority.ledger_id != ledger_id:
        raise ValueError('journal authority/ledger mismatch')
    actual_batch_digest=batch_digest(batch)
    if not hmac.compare_digest(authority.batch_fingerprint, actual_batch_digest):
        raise ValueError('journal authority/batch mismatch')
    receipt=batch.receipt
    if (receipt.plan_fingerprint != plan.fingerprint or
        receipt.registry_fingerprint != plan.registry_fingerprint or
        receipt.source_digest != plan.source_digest or
        receipt.source_id != plan.source_id):
        raise ValueError('journal plan/receipt mismatch')
    if action not in ('APPROVED','REJECTED'):
        raise ValueError('invalid decision')
    if action == 'APPROVED' and (reason_code!='WHOLE_BATCH_APPROVED' or not event_hash):
        raise ValueError('approved decision needs knowledge event')
    if action == 'REJECTED' and (reason_code!='WHOLE_BATCH_REJECTED' or event_hash is not None):
        raise ValueError('rejected decision cannot reference knowledge event')
    if event_hash is not None and not DIGEST_PATTERN.fullmatch(event_hash):
        raise ValueError('invalid knowledge event digest')
    previous=_last_record(conn)
    # Do not extend a locally tampered journal merely because its final digest parses.
    audit=audit_decisions(conn,ledger_id=ledger_id,
                          keyring=ReviewKeyring({authority.key_id:authority.secret}))
    if audit['invalid_entries']:
        raise ValueError('cannot extend an unverifiable local decision journal')
    parts=dict(purpose=PURPOSE, seq=1 if previous is None else previous.seq+1,
        prior_hash=None if previous is None else previous.entry_hash,
        action=action,reason_code=reason_code,key_id=authority.key_id,
        nonce=secrets.token_hex(24),ledger_id=ledger_id,
        batch_digest=actual_batch_digest,plan_fingerprint=plan.fingerprint,
        source_digest=plan.source_digest,registry_fingerprint=plan.registry_fingerprint,
        presentation_digest=authority.presentation_digest,
        ledger_head_at_stage=receipt.ledger_head_at_stage,
        knowledge_event_hash=event_hash,
        decided_at=datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z'))
    signature=hmac.new(authority.secret,json_bytes(parts),hashlib.sha256).hexdigest()
    entry_hash=canonical_digest(json_bytes({**parts,'signature':signature}))
    record=ReviewDecisionRecord(**parts,signature=signature,entry_hash=entry_hash)
    conn.execute('INSERT INTO review_decisions(seq,batch_digest,entry_hash,payload) VALUES (?,?,?,?)',
                 (record.seq, record.batch_digest,record.entry_hash,json_bytes(asdict(record)).decode('utf8')))
    return record


def audit_decisions(conn, *, ledger_id: str, keyring: ReviewKeyring,
                    expected_head: str | None = None) -> dict:
    """Recalculate each local MAC + chain and match approved entries to commits."""
    if not isinstance(keyring,ReviewKeyring):
        raise TypeError('keyring required')
    rows=conn.execute('SELECT seq,batch_digest,entry_hash,payload FROM review_decisions ORDER BY seq').fetchall()
    prev=None
    bad=[]
    approvals=0
    rejections=0
    events={x['hash']:x for x in
            (json.loads(r['payload']) for r in conn.execute('SELECT payload FROM events'))}
    approved_hashes=set()
    for index,row in enumerate(rows,1):
        try:
            d=json.loads(row['payload'])
            rec=ReviewDecisionRecord(**d)
            secret=keyring.get(rec.key_id)
            if (rec.seq!=index or rec.seq!=row['seq'] or rec.prior_hash!=prev
                or rec.purpose!=PURPOSE or rec.ledger_id!=ledger_id
                or rec.batch_digest!=row['batch_digest'] or rec.entry_hash!=row['entry_hash']
                or not DIGEST_PATTERN.fullmatch(rec.presentation_digest)
                or not re.fullmatch('[0-9a-f]{48}',rec.nonce) or secret is None):
                raise ValueError('journal identity or chain mismatch')
            sig=hmac.new(secret,json_bytes(rec.unsigned()),hashlib.sha256).hexdigest()
            if not hmac.compare_digest(sig,rec.signature):
                raise ValueError('MAC mismatch')
            if canonical_digest(json_bytes({**rec.unsigned(),'signature':rec.signature})) != rec.entry_hash:
                raise ValueError('entry hash mismatch')
            if rec.action=='APPROVED':
                evt=events.get(rec.knowledge_event_hash)
                used=conn.execute('SELECT batch_digest FROM used_approvals WHERE event_hash=?',
                                  (rec.knowledge_event_hash,)).fetchone()
                if (rec.reason_code!='WHOLE_BATCH_APPROVED' or evt is None or
                    evt['kind']!='BATCH_ADMIT' or evt['prev_hash']!=rec.ledger_head_at_stage or
                    used is None or used['batch_digest']!=rec.batch_digest or
                    rec.knowledge_event_hash in approved_hashes):
                    raise ValueError('approved event/permit mismatch')
                approvals+=1
                approved_hashes.add(rec.knowledge_event_hash)
            elif rec.action=='REJECTED':
                if rec.knowledge_event_hash is not None or rec.reason_code!='WHOLE_BATCH_REJECTED':
                    raise ValueError('rejection cannot admit knowledge')
                rejections+=1
            else: raise ValueError('unknown decision kind')
        except (ValueError,TypeError,KeyError,AttributeError):
            bad.append(row['seq'])
        # Continue auditing remaining records, but never silently mark an invalid
        # predecessor as trusted; it makes later records invalid too.
        if index in bad:
            prev='INVALID_PREDECESSOR'
        else:
            prev=rec.entry_hash
    head=rows[-1]['entry_hash'] if rows else None
    if expected_head is not None and head!=expected_head:
        bad.append('external_head_mismatch')
    return {'total':len(rows),'verified_approvals':approvals,'verified_rejections':rejections,
            'invalid_entries':tuple(bad),'journal_head':head,
            'limitations':'Local signatures and integrity only; retain head externally to detect truncation or replacement'}
