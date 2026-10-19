"""Earned Light Forge III -- Human Reconfirmation Bridge, research-only.

No real identity provider, WebAuthn, agent, or external side effect is integrated.
Only an independent approval authority can sign a response. The private signer
MUST remain out of agent runtime and out of any untrusted content ingestion.

A verified receipt authorizes only one exact action. SQLite challenge claims
are single-use within this process/deployment, but this is NOT distributed
atomicity with provider side effects or a production revocation service.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass, replace
import hashlib
import json
import secrets
import sqlite3
from pathlib import Path
from typing import Any, Callable, Sequence
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.exceptions import InvalidSignature
from earned_authority import EarnedAuthorityGate, Grant, OriginProof, Request, Decision, canonical, digest

BRIDGE_SCHEMA = 'lycheetah.earned-light.review.v0.3'
INTENT_SCHEMA = 'lycheetah.earned-light.review-intent.v0.3'
RECOVERABLE = frozenset({'FIELD_PROOF_MISSING', 'ORIGIN_DISALLOWED'})
MAX_REVIEW_BYTES = 8192
MAX_TTL = 300

class ReviewError(PermissionError):
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)

@dataclass(frozen=True)
class ReviewIntent:
    """Proof that a trusted human UI explicitly opened an action for review.

    This attests a *review initiation*, NOT consent to run the action.
    """
    schema: str
    issuer: str
    intent_nonce: str
    principal: str
    grant_id: str
    request_digest: str
    issued_at: int
    expires_at: int
    signature: str

    def payload(self) -> dict[str, Any]:
        data=asdict(self)
        data.pop('signature')
        return data

@dataclass(frozen=True)
class ReviewChallenge:
    challenge_id: str
    request_digest: str
    display_digest: str
    principal: str
    grant_id: str
    issued_at: int
    expires_at: int
    reason: str
    display: str

@dataclass(frozen=True)
class ReviewReceipt:
    schema: str
    issuer: str
    challenge_id: str
    request_digest: str
    display_digest: str
    principal: str
    grant_id: str
    action: str
    issued_at: int
    expires_at: int
    signature: str

    def payload(self) -> dict[str, Any]:
        data = asdict(self)
        data.pop('signature')
        return data


def review_display(r: Request, denial_reason: str) -> str:
    """No model-written prose; include the COMPLETE exact action, ASCII escaped.

    A real trusted UI needs a reviewable high-assurance rendering and
    accessibility/user study. JSON ASCII encoding avoids bidi/control display
    spoofing in this prototype; it does not stop users being misled by content.
    """
    payload = asdict(r)
    if len(canonical(payload)) > MAX_REVIEW_BYTES:
        raise ReviewError('REVIEW_TOO_LARGE')
    action = json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=True, allow_nan=False)
    return ('REVIEW AN EXACT CONSEQUENTIAL ACTION\n'
            'Warning: values may originate in untrusted data.\n'
            f'Denial: {denial_reason}\n'
            'No action will run without an independent, authenticated approval.\n'
            'EXACT ACTION (JSON escaped; no omitted fields):\n' + action + '\n')

class ReviewStore:
    """Persistent research ledger: single-use claim in SQLite BEGIN IMMEDIATE."""
    def __init__(self, path: str | Path):
        self.path = str(path)
        with self._db() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS challenge(
                    challenge_id TEXT PRIMARY KEY,
                    intent_nonce TEXT NOT NULL UNIQUE,
                    request_digest TEXT NOT NULL,
                    display_digest TEXT NOT NULL,
                    display_text TEXT NOT NULL,
                    principal TEXT NOT NULL,
                    grant_id TEXT NOT NULL,
                    denial_code TEXT NOT NULL,
                    issued_at INTEGER NOT NULL,
                    expires_at INTEGER NOT NULL,
                    status TEXT NOT NULL CHECK (status IN ('PENDING','APPROVED','DENIED','CONSUMED')),
                    receipt_signature TEXT
                );
                CREATE TABLE IF NOT EXISTS events(
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    challenge_id TEXT NOT NULL, code TEXT NOT NULL,
                    ts INTEGER NOT NULL
                );
            ''')

    def _db(self):
        db=sqlite3.connect(self.path, isolation_level=None, timeout=10)
        db.row_factory=sqlite3.Row
        return db

    def register(self, ch: ReviewChallenge, intent_nonce: str):
        try:
            with self._db() as db:
                db.execute('BEGIN IMMEDIATE')
                db.execute('INSERT INTO challenge VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
                           (ch.challenge_id, intent_nonce, ch.request_digest,
                            ch.display_digest, ch.display, ch.principal,
                            ch.grant_id, ch.reason, ch.issued_at,
                            ch.expires_at, 'PENDING', None))
                db.execute('INSERT INTO events(challenge_id,code,ts) VALUES (?,?,?)',
                           (ch.challenge_id, 'CHALLENGE_CREATED', ch.issued_at))
                db.commit()
        except sqlite3.IntegrityError:
            raise ReviewError('REVIEW_INTENT_REPLAY') from None

    def fetch(self, cid: str):
        with self._db() as db:
            row=db.execute('SELECT * FROM challenge WHERE challenge_id=?',(cid,)).fetchone()
        return dict(row) if row else None

    def record_review(self, receipt: ReviewReceipt, *, now: int) -> None:
        with self._db() as db:
            db.execute('BEGIN IMMEDIATE')
            row=db.execute('SELECT * FROM challenge WHERE challenge_id=?',(receipt.challenge_id,)).fetchone()
            if row is None or row['status'] != 'PENDING':
                raise ReviewError('CHALLENGE_NOT_PENDING')
            if now < row['issued_at'] or now >= row['expires_at']:
                raise ReviewError('CHALLENGE_EXPIRED')
            if (receipt.request_digest != row['request_digest'] or
                receipt.display_digest != row['display_digest'] or
                receipt.principal != row['principal'] or
                receipt.grant_id != row['grant_id']):
                raise ReviewError('REVIEW_BINDING_MISMATCH')
            status='APPROVED' if receipt.action == 'approve' else 'DENIED'
            db.execute('UPDATE challenge SET status=?,receipt_signature=? WHERE challenge_id=?',
                       (status, receipt.signature, receipt.challenge_id))
            db.execute('INSERT INTO events(challenge_id,code,ts) VALUES (?,?,?)',
                       (receipt.challenge_id, 'HUMAN_'+status, now))
            db.commit()

    def consume(self, receipt: ReviewReceipt, *, now: int) -> None:
        with self._db() as db:
            db.execute('BEGIN IMMEDIATE')
            row=db.execute('SELECT * FROM challenge WHERE challenge_id=?',(receipt.challenge_id,)).fetchone()
            if row is None:
                raise ReviewError('CHALLENGE_UNKNOWN')
            if now < row['issued_at'] or now >= row['expires_at']:
                raise ReviewError('CHALLENGE_EXPIRED')
            if row['status'] != 'APPROVED':
                raise ReviewError('CHALLENGE_NOT_APPROVED')
            if (row['receipt_signature'] != receipt.signature or
                row['request_digest'] != receipt.request_digest or
                row['display_digest'] != receipt.display_digest or
                row['principal'] != receipt.principal or
                row['grant_id'] != receipt.grant_id):
                raise ReviewError('RECORDED_APPROVAL_MISMATCH')
            db.execute("UPDATE challenge SET status='CONSUMED' WHERE challenge_id=?", (receipt.challenge_id,))
            db.execute('INSERT INTO events(challenge_id,code,ts) VALUES (?,?,?)',
                       (receipt.challenge_id, 'CLAIM_CONSUMED', now))
            db.commit()

class HumanReconfirmationBridge:
    def __init__(self, gate: EarnedAuthorityGate, store: ReviewStore,
                 approval_keys: dict[str, Ed25519PublicKey],
                 initiation_keys: dict[str, Ed25519PublicKey]):
        self.gate=gate
        self.store=store
        self.approval_keys=approval_keys.copy()
        self.initiation_keys=initiation_keys.copy()

    def _check_intent(self, r: Request, g: Grant, intent: ReviewIntent | None, *, now: int) -> None:
        if not isinstance(intent, ReviewIntent) or intent.schema != INTENT_SCHEMA:
            raise ReviewError('REVIEW_INTENT_REQUIRED')
        pub=self.initiation_keys.get(intent.issuer)
        if pub is None:
            raise ReviewError('REVIEW_INTENT_ISSUER_UNKNOWN')
        try:
            if len(intent.signature) != 128:
                raise ValueError('bad length')
            pub.verify(bytes.fromhex(intent.signature),canonical(intent.payload()))
        except (InvalidSignature,ValueError):
            raise ReviewError('REVIEW_INTENT_SIGNATURE_INVALID') from None
        if (intent.request_digest != digest(asdict(r)) or
            intent.grant_id != g.grant_id or intent.principal != g.principal or
            not intent.intent_nonce):
            raise ReviewError('REVIEW_INTENT_BINDING_MISMATCH')
        if now < intent.issued_at or now >= intent.expires_at:
            raise ReviewError('REVIEW_INTENT_EXPIRED')

    def begin(self, r: Request, g: Grant | None, proofs: Sequence[OriginProof], *,
              intent: ReviewIntent | None = None, now: int, ttl: int = 90) -> ReviewChallenge:
        decision=self.gate.evaluate(r,g,proofs,now=now)
        if decision.code not in RECOVERABLE:
            raise ReviewError('NOT_RECONFIRMABLE:' + decision.code)
        if g is None or not self.gate.check_grant(r,g,now=now).allowed:
            raise ReviewError('GRANT_INVALID')
        self._check_intent(r,g,intent,now=now)
        if not 1 <= ttl <= MAX_TTL:
            raise ReviewError('INVALID_TTL')
        assert intent is not None
        expiry=min(now + ttl,g.expires_at,intent.expires_at)
        if expiry <= now:
            raise ReviewError('CHALLENGE_EXPIRED')
        display=review_display(r,decision.code)
        challenge=ReviewChallenge(secrets.token_hex(24), digest(asdict(r)),
                                  hashlib.sha256(display.encode('utf-8')).hexdigest(),
                                  g.principal,g.grant_id,now,expiry,decision.code,display)
        self.store.register(challenge,intent.intent_nonce)
        return challenge

    def verify(self, r: Request, g: Grant | None, proofs: Sequence[OriginProof],
               receipt: ReviewReceipt, *, now: int) -> Decision:
        if not isinstance(receipt,ReviewReceipt) or receipt.schema != BRIDGE_SCHEMA or receipt.action != 'approve':
            raise ReviewError('RECEIPT_INVALID')
        pub=self.approval_keys.get(receipt.issuer)
        if pub is None:
            raise ReviewError('RECEIPT_ISSUER_UNKNOWN')
        try:
            if len(receipt.signature) != 128:
                raise ValueError('signature size')
            pub.verify(bytes.fromhex(receipt.signature),canonical(receipt.payload()))
        except (InvalidSignature,ValueError):
            raise ReviewError('RECEIPT_SIGNATURE_INVALID') from None
        dec=self.gate.evaluate(r,g,proofs,now=now)
        if dec.code not in RECOVERABLE:
            raise ReviewError('NOT_RECONFIRMABLE:' + dec.code)
        if g is None or not self.gate.check_grant(r,g,now=now).allowed:
            raise ReviewError('GRANT_INVALID')
        stored=self.store.fetch(receipt.challenge_id)
        if stored is None:
            raise ReviewError('CHALLENGE_UNKNOWN')
        if (receipt.request_digest != digest(asdict(r)) or
            receipt.request_digest != stored['request_digest'] or
            receipt.grant_id != g.grant_id or
            receipt.principal != g.principal or
            receipt.display_digest != stored['display_digest'] or
            receipt.action != 'approve'):
            raise ReviewError('RECEIPT_BINDING_MISMATCH')
        # Re-render from current, complete action. Prevent review-card substitution.
        display=review_display(r,stored['denial_code'])
        if hashlib.sha256(display.encode('utf-8')).hexdigest() != receipt.display_digest:
            raise ReviewError('DISPLAY_BINDING_MISMATCH')
        if now < receipt.issued_at or now >= receipt.expires_at or now >= stored['expires_at']:
            raise ReviewError('RECEIPT_EXPIRED')
        if receipt.issued_at < stored['issued_at'] or receipt.expires_at != stored['expires_at']:
            raise ReviewError('RECEIPT_TIME_MISMATCH')
        if stored['status'] != 'APPROVED' or stored['receipt_signature'] != receipt.signature:
            raise ReviewError('RECEIPT_NOT_RECORDED')
        return Decision(True,'EAC_RECONFIRMED',g.grant_id,digest(asdict(r)),(receipt.challenge_id,))

    def execute(self, r: Request, g: Grant | None, proofs: Sequence[OriginProof],
                receipt: ReviewReceipt, *, now: int, effect: Callable[[],Any]) -> Any:
        """At-most-once CLAIM, not guaranteed exactly-once downstream effect.

        The check->consume/revocation transition is NOT globally atomic.
        Production needs a transactional provider outbox/idempotency key and
        persistent revocation under the same trusted effect boundary.
        """
        self.verify(r,g,proofs,receipt,now=now)
        self.store.consume(receipt,now=now)
        return effect()

class TrustedReviewAuthority:
    """TEST-ONLY STAND-IN for separate authenticated approval service.

    The `authenticated_principal` argument represents an already-verified
    identity session, NOT authentication performed by this code. NEVER expose
    approve() as an agent callable or claim it proves a human viewed the action.
    """
    def __init__(self, issuer: str, private_key: Ed25519PrivateKey, store: ReviewStore):
        self.issuer=issuer
        self._key=private_key
        self.store=store

    def start_review(self, r: Request, g: Grant, *, authenticated_principal: str,
                     now: int, ttl: int = 120) -> ReviewIntent:
        """MOCK signed event from independently authenticated trusted UI click.

        Caller may NEVER be an AI tool: `authenticated_principal` is a test-only
        stand-in for an established, protected real login session.
        """
        if authenticated_principal != g.principal:
            raise ReviewError('PRINCIPAL_NOT_AUTHENTICATED')
        if ttl < 1 or ttl > MAX_TTL:
            raise ReviewError('INVALID_TTL')
        it=ReviewIntent(INTENT_SCHEMA,self.issuer,secrets.token_hex(24),
                        authenticated_principal,g.grant_id,digest(asdict(r)),
                        now,min(now+ttl,g.expires_at),'')
        return replace(it,signature=self._key.sign(canonical(it.payload())).hex())

    def trusted_review_text(self, challenge_id: str) -> str:
        """Trusted UI must render server-sealed text, never agent-supplied Markdown."""
        stored = self.store.fetch(challenge_id)
        if stored is None:
            raise ReviewError('CHALLENGE_UNKNOWN')
        sealed = stored['display_text']
        if hashlib.sha256(sealed.encode('utf-8')).hexdigest() != stored['display_digest']:
            raise ReviewError('SEALED_DISPLAY_CORRUPTED')
        return sealed

    def decide(self, ch: ReviewChallenge, *, authenticated_principal: str,
               observed_display_digest: str, approved: bool, now: int) -> ReviewReceipt:
        stored=self.store.fetch(ch.challenge_id)
        if stored is None or stored['status'] != 'PENDING':
            raise ReviewError('CHALLENGE_NOT_PENDING')
        if now < stored['issued_at'] or now >= stored['expires_at']:
            raise ReviewError('CHALLENGE_EXPIRED')
        if authenticated_principal != stored['principal']:
            raise ReviewError('PRINCIPAL_NOT_AUTHENTICATED')
        # A real UI MUST obtain the full display from this trusted store;
        # passing only the expected hash is not proof it rendered correctly.
        sealed_text = stored['display_text']
        if (hashlib.sha256(sealed_text.encode('utf-8')).hexdigest() != stored['display_digest'] or
            ch.display != sealed_text or
            observed_display_digest != stored['display_digest'] or
            ch.display_digest != stored['display_digest'] or
            ch.request_digest != stored['request_digest'] or
            ch.grant_id != stored['grant_id']):
            raise ReviewError('DISPLAY_BINDING_MISMATCH')
        receipt=ReviewReceipt(BRIDGE_SCHEMA,self.issuer,ch.challenge_id,
                             stored['request_digest'],stored['display_digest'],
                             authenticated_principal,stored['grant_id'],
                             'approve' if approved else 'deny',now,stored['expires_at'],'')
        receipt=replace(receipt,signature=self._key.sign(canonical(receipt.payload())).hex())
        self.store.record_review(receipt,now=now)
        return receipt
