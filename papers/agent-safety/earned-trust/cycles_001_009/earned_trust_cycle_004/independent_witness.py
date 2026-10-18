"""Cycle 004 -- two-domain outcome witness, *synthetic local reference only*.

The observer DB is intentionally distinct from the provider DB.  The test harness,
not the model or the provider, supplies world observations. Different keys and
files are not proof of independent operators or truth in a real deployment.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import sqlite3
import hmac
import hashlib
import json
import sys

# Byte-identical Cycle 003 reference implementation is bundled beside this file.
# It remains a synthetic reference, not part of Lycheetah's installed package.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from authenticated_provider import (
    SignedSQLiteProvider, TrustedIssuer, hash_obj, seal, verify_artifact, valid_action,
    PROOF_FIELDS, decode_wire,
)

OBS_FIELDS = frozenset({
    "schema", "source_id", "effect_id", "token_sha256", "action_sha256",
    "status", "correctness", "revision", "observed_at",
})


@dataclass(frozen=True)
class Reconciliation:
    result: str
    reason: str
    provider_authenticated: bool
    independent_observation_authenticated: bool
    def to_dict(self) -> dict[str, Any]:
        return vars(self).copy()


class IndependentObserver:
    """Observer-side signing capability and independent local fixture state.

    This module is a *lab oracle* only: the caller writes observations; it does
    not secretly see remote payments or verify independent source provenance.
    """
    def __init__(self, db_path: str | Path, *, secret: bytes, source_id: str = "external-observer-A",
                 key_id: str = "external-observer-key-A"):
        if len(secret) < 32:
            raise ValueError("observer key must contain 32+ bytes")
        if not source_id or not key_id or source_id == "local-provider":
            raise ValueError("observer identity cannot be local-provider")
        self.db_path = str(db_path)
        self.secret, self.source_id, self.key_id = secret, source_id, key_id
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS observations (
                effect_id TEXT PRIMARY KEY, token_sha TEXT NOT NULL, action_sha TEXT NOT NULL,
                status TEXT NOT NULL, correctness TEXT NOT NULL, revision INTEGER NOT NULL,
                observed_at INTEGER NOT NULL)""")

    def observe(self, *, effect_id: str, token_sha256: str, action_sha256: str,
                status: str, correctness: str, observed_at: int) -> dict[str, Any]:
        """Trusted lab-only oracle update (not available to an untrusted agent)."""
        if not effect_id or len(token_sha256) != 64 or len(action_sha256) != 64:
            raise ValueError("bad identity hash")
        if status not in {"COMMITTED", "NOT_COMMITTED", "UNKNOWN"}:
            raise ValueError("bad observed status")
        if correctness not in {"TRUE", "FALSE", "UNKNOWN"}:
            raise ValueError("bad outcome correctness")
        if type(observed_at) is not int or observed_at < 0:
            raise ValueError("bad observation time")
        with sqlite3.connect(self.db_path, isolation_level=None) as db:
            db.execute("BEGIN IMMEDIATE")
            prior = db.execute("SELECT revision,observed_at FROM observations WHERE effect_id=?", (effect_id,)).fetchone()
            if prior is not None and observed_at <= prior[1]:
                db.execute("ROLLBACK")
                raise ValueError("non-monotonic time for observation")
            revision = 1 if prior is None else prior[0]+1
            db.execute("""INSERT INTO observations VALUES(?,?,?,?,?,?,?)
                         ON CONFLICT(effect_id) DO UPDATE SET
                         token_sha=excluded.token_sha, action_sha=excluded.action_sha,
                         status=excluded.status, correctness=excluded.correctness,
                         revision=excluded.revision, observed_at=excluded.observed_at""",
                       (effect_id, token_sha256, action_sha256, status, correctness, revision, observed_at))
            db.execute("COMMIT")
        return self.current(effect_id)

    def current(self, effect_id: str) -> dict[str, Any] | None:
        with sqlite3.connect(self.db_path) as db:
            row = db.execute("SELECT * FROM observations WHERE effect_id=?", (effect_id,)).fetchone()
        if row is None:
            return None
        _, token_sha, action_sha, status, correctness, revision, observed_at = row
        body = {"schema": "earned-trust.external-observation.v1", "source_id": self.source_id,
                "effect_id": effect_id, "token_sha256": token_sha, "action_sha256": action_sha,
                "status": status, "correctness": correctness,
                "revision": revision, "observed_at": observed_at}
        return seal(self.secret, "earned-trust.observation.v1", self.key_id, body)

    def verify(self, witness: Any) -> bool:
        if not verify_artifact(witness, self.secret, "earned-trust.observation.v1",
                               self.key_id, OBS_FIELDS):
            return False
        b = witness["body"]
        return (b["schema"] == "earned-trust.external-observation.v1"
                and b["source_id"] == self.source_id
                and b["status"] in {"COMMITTED", "NOT_COMMITTED", "UNKNOWN"}
                and b["correctness"] in {"TRUE", "FALSE", "UNKNOWN"}
                and type(b["revision"]) is int and b["revision"] > 0
                and type(b["observed_at"]) is int and b["observed_at"] >= 0)


class OutcomeVerifier:
    """Read-only reconciliation of signed LOCAL provider receipt and observer claim.

    Trust assumptions: separate keys, authorized observer, uncompromised verifier,
    freshness from direct observer current() lookup; no external-world truth proof.
    """
    def __init__(self, provider: SignedSQLiteProvider, observer: IndependentObserver):
        if provider.provider_secret == observer.secret or provider.authority_secret == observer.secret:
            raise ValueError("observer signer must use a distinct key")
        self.provider, self.observer = provider, observer

    def reconcile(self, *, effect_id: str, token: dict[str, Any], action: dict[str, Any],
                  supplied_witness: dict[str, Any] | None = None) -> Reconciliation:
        # Original signed provider record is fetched by ID, not trusted as caller input.
        if not valid_action(action) or not isinstance(effect_id, str) or not effect_id:
            return Reconciliation("REVIEW", "invalid-subject", False, False)
        try:
            proof = self.provider.lookup(effect_id)
        except (ValueError, TypeError, UnicodeError, sqlite3.DatabaseError):
            return Reconciliation("REVIEW", "provider-read-invalid", False, False)
        if proof is None:
            return Reconciliation("UNKNOWN", "no-provider-commit-receipt", False, False)
        if not self.provider.verify_proof(proof, token=token, action=action):
            return Reconciliation("REVIEW", "invalid-provider-proof", False, False)
        try:
            stored_valid = self.provider.verify_stored_effect(effect_id, token=token)
            audit_valid = self.provider.verify_audit().get("valid") is True
        except (ValueError, TypeError, UnicodeError, sqlite3.DatabaseError):
            return Reconciliation("REVIEW", "provider-consistency-unavailable", True, False)
        if not stored_valid:
            return Reconciliation("REVIEW", "provider-ledger-inconsistent", True, False)
        # Protect against locally detectable truncation or reordering.
        if not audit_valid:
            return Reconciliation("REVIEW", "provider-audit-invalid", True, False)
        try:
            witness = supplied_witness if supplied_witness is not None else self.observer.current(effect_id)
        except (ValueError, TypeError, UnicodeError, sqlite3.DatabaseError):
            return Reconciliation("REVIEW", "observer-read-invalid", True, False)
        if witness is None:
            return Reconciliation("REVIEW", "independent-observation-missing", True, False)
        if not self.observer.verify(witness):
            return Reconciliation("REVIEW", "observer-auth-invalid", True, False)
        try:
            current = self.observer.current(effect_id)
        except (ValueError, TypeError, UnicodeError, sqlite3.DatabaseError):
            return Reconciliation("REVIEW", "observer-read-invalid", True, True)
        if current is None or current != witness:
            return Reconciliation("REVIEW", "observer-evidence-not-current", True, True)
        p, o = proof["body"], witness["body"]
        if (o["effect_id"] != effect_id or o["token_sha256"] != p["token_sha256"]
                or o["action_sha256"] != p["action_sha256"]):
            return Reconciliation("CONFLICT", "cross-source-action-disagreement", True, True)
        if o["status"] != "COMMITTED":
            return Reconciliation("CONFLICT" if o["status"] == "NOT_COMMITTED" else "REVIEW",
                                  "observer-does-not-confirm-effect", True, True)
        if o["correctness"] == "FALSE":
            return Reconciliation("CONFLICT", "observer-reports-harmful-or-incorrect-effect", True, True)
        if o["correctness"] != "TRUE":
            return Reconciliation("REVIEW", "observer-correctness-unknown", True, True)
        return Reconciliation("CONFIRMED", "two-local-claims-agree", True, True)
