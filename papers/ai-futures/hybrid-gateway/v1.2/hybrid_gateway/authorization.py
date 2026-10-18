"""Cycle 9: explicit *operator-key* authority for whole-batch SQLite admission.

HMAC-SHA256 verifies control of a trusted key, NOT that a human read the source,
NOT a person's identity, and NOT defense against a compromised signing service.
Keys are never stored in the ledger. The signature covers an exact audited batch,
ledger head, plan, source, registry, commit timestamp and short validity period.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
from datetime import datetime, timezone, timedelta
import hashlib
import hmac
import re
import secrets
from typing import Mapping
from .core import canonical_digest, json_bytes, utc
from .coverage import AuditedBatch, ExtractionPlan

PURPOSE = 'lycheetah.hybrid-gateway.batch-admit.v1'
MAX_TTL_SECONDS = 600


def batch_digest(batch: AuditedBatch) -> str:
    if not isinstance(batch, AuditedBatch):
        raise TypeError('expected audited batch')
    return canonical_digest(json_bytes({
        'receipt': asdict(batch.receipt),
        'stages': [asdict(stage) for stage in batch.stages]}))


@dataclass(frozen=True)
class SignedBatchApproval:
    purpose: str
    key_id: str
    nonce: str
    issued_at: str
    expires_at: str
    recorded_at: str
    source_digest: str
    ledger_id: str
    plan_fingerprint: str
    registry_fingerprint: str
    ledger_head_at_stage: str | None
    batch_digest: str
    signature: str

    def unsigned_payload(self) -> dict:
        return {k: v for k, v in asdict(self).items() if k != 'signature'}


class ReviewKeyring:
    """Operator-supplied keys; no automatic reviewer identity assertion."""
    def __init__(self, keys: Mapping[str, bytes]):
        if not isinstance(keys, Mapping) or not keys:
            raise ValueError('nonempty operator keyring required')
        result = {}
        for key_id, secret in keys.items():
            if not isinstance(key_id, str) or not re.fullmatch(r'[a-zA-Z0-9._-]{1,80}', key_id):
                raise ValueError('invalid key id')
            if not isinstance(secret, bytes) or len(secret) < 32:
                raise ValueError('HMAC key must be at least 32 bytes')
            result[key_id] = secret
        self._keys = result

    def get(self, key_id):
        return self._keys.get(key_id)


def issue_approval(batch: AuditedBatch, plan: ExtractionPlan, *,
                   key_id: str, secret: bytes, recorded_at: str, ledger_id: str,
                   ttl_seconds: int = 300, now: datetime | None = None,
                   nonce: str | None = None) -> SignedBatchApproval:
    """Call only from a separate trusted reviewer/approval service.

    `now` and `nonce` are testing hooks; never expose them to an LLM.
    """
    ReviewKeyring({key_id: secret})
    if not isinstance(ledger_id,str) or not re.fullmatch('[0-9a-f]{48}',ledger_id):
        raise ValueError('approval requires persistent ledger identity')
    if type(ttl_seconds) is not int or not 1 <= ttl_seconds <= MAX_TTL_SECONDS:
        raise ValueError('invalid bounded approval TTL')
    if batch.receipt.disposition != 'READY_FOR_REVIEW':
        raise ValueError('cannot sign incomplete extraction')
    if not isinstance(plan, ExtractionPlan):
        raise TypeError('expected extraction plan')
    if (batch.receipt.source_id != plan.source_id or
        batch.receipt.plan_fingerprint != plan.fingerprint or
        batch.receipt.registry_fingerprint != plan.registry_fingerprint or
        batch.receipt.source_digest != plan.source_digest):
        raise ValueError('batch does not match operator plan')
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError('clock must have timezone')
    now = now.astimezone(timezone.utc)
    issued = now.isoformat(timespec='seconds').replace('+00:00', 'Z')
    expires = (now + timedelta(seconds=ttl_seconds)).isoformat(timespec='seconds').replace('+00:00','Z')
    nonce = nonce or secrets.token_hex(24)
    if not isinstance(nonce, str) or not re.fullmatch('[0-9a-f]{48}', nonce):
        raise ValueError('invalid nonce')
    parts = dict(purpose=PURPOSE, key_id=key_id, nonce=nonce,
        issued_at=issued, expires_at=expires, recorded_at=utc(recorded_at),
        source_digest=plan.source_digest, ledger_id=ledger_id, plan_fingerprint=plan.fingerprint,
        registry_fingerprint=plan.registry_fingerprint,
        ledger_head_at_stage=batch.receipt.ledger_head_at_stage,
        batch_digest=batch_digest(batch))
    signature = hmac.new(secret, json_bytes(parts), hashlib.sha256).hexdigest()
    return SignedBatchApproval(**parts, signature=signature)


def verify_approval(approval: SignedBatchApproval, *, batch: AuditedBatch,
                    plan: ExtractionPlan, keyring: ReviewKeyring,
                    recorded_at: str, ledger_id: str, now: datetime | None = None) -> bool:
    if not isinstance(approval, SignedBatchApproval) or not isinstance(keyring, ReviewKeyring):
        return False
    try:
        secret = keyring.get(approval.key_id)
        if secret is None or approval.purpose != PURPOSE:
            return False
        if (approval.recorded_at != utc(recorded_at) or
            approval.source_digest != plan.source_digest or
            approval.ledger_id != ledger_id or
            approval.plan_fingerprint != plan.fingerprint or
            approval.registry_fingerprint != plan.registry_fingerprint or
            approval.ledger_head_at_stage != batch.receipt.ledger_head_at_stage or
            approval.batch_digest != batch_digest(batch)):
            return False
        if not re.fullmatch('[0-9a-f]{48}', approval.nonce):
            return False
        if not re.fullmatch('[0-9a-f]{64}', approval.signature):
            return False
        issued = datetime.fromisoformat(utc(approval.issued_at).replace('Z', '+00:00'))
        expires = datetime.fromisoformat(utc(approval.expires_at).replace('Z', '+00:00'))
        now = now or datetime.now(timezone.utc)
        if now.tzinfo is None or now.utcoffset() is None:
            return False
        now = now.astimezone(timezone.utc)
        if not (issued <= now < expires and 0 < (expires - issued).total_seconds() <= MAX_TTL_SECONDS):
            return False
        mac = hmac.new(secret, json_bytes(approval.unsigned_payload()), hashlib.sha256).hexdigest()
        return hmac.compare_digest(mac, approval.signature)
    except (ValueError, TypeError, OverflowError, AttributeError):
        return False
