"""Earned Trust Cycle 002: SQLite-conditional REFUND LAB, not an external provider.

A single trusted SQLite transaction validates current policy, approval, source record,
exact action and effect identity, then inserts the effect. No network or actual payments.
This laboratory models a capability real providers MAY NOT expose.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Literal
import json
import sqlite3


def canonical(value: dict) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value: dict) -> str:
    return sha256(canonical(value).encode()).hexdigest()


@dataclass(frozen=True)
class Intent:
    effect_id: str
    approval_id: str
    actor: str
    subject: str
    amount_cents: int
    scope: str = "refund:create"
    expected_version: int | None = None

    def payload(self) -> dict:
        return {"actor": self.actor, "subject": self.subject,
                "amount_cents": self.amount_cents, "scope": self.scope}


@dataclass(frozen=True)
class Result:
    code: str
    committed: bool
    replay: bool = False
    state_version: int | None = None


class LostResponse(ConnectionError):
    """Raised AFTER a committed write to model an uncertain external response."""


class ConditionalRefundProvider:
    """Trusted single-DB simulated processor. This is NOT a production payment API."""

    def __init__(self, db_path: str | Path):
        self.path = str(db_path)
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS principals(actor TEXT PRIMARY KEY, epoch INT NOT NULL);
                CREATE TABLE IF NOT EXISTS grants(
                    approval_id TEXT PRIMARY KEY, actor TEXT NOT NULL, approver TEXT NOT NULL,
                    scope TEXT NOT NULL, payload_hash TEXT NOT NULL,
                    issued_at INT NOT NULL, expires_at INT NOT NULL, epoch INT NOT NULL);
                CREATE TABLE IF NOT EXISTS subjects(
                    subject TEXT PRIMARY KEY, eligible INT NOT NULL, version INT NOT NULL,
                    evidence_status TEXT NOT NULL, recorded_truth INT NOT NULL);
                CREATE TABLE IF NOT EXISTS rules(id INT PRIMARY KEY CHECK(id=1), maximum INT NOT NULL, version INT NOT NULL);
                CREATE TABLE IF NOT EXISTS effects(
                    effect_id TEXT PRIMARY KEY, approval_id TEXT NOT NULL, payload_hash TEXT NOT NULL,
                    amount_cents INT NOT NULL, subject TEXT NOT NULL,
                    commit_version INT NOT NULL, status TEXT NOT NULL,
                    UNIQUE(approval_id));
                INSERT OR IGNORE INTO rules(id,maximum,version) VALUES(1,5000,1);
            """)

    def _connect(self):
        connection = sqlite3.connect(self.path, isolation_level=None, timeout=15.0)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA busy_timeout=15000")
        return connection

    def seed(self, intent: Intent, *, now: int = 100, expires_at: int = 200,
             eligible: bool = True, recorded_truth: bool = True):
        """Fixture creation: source is treated as authoritative, truth is separate oracle."""
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute("INSERT OR REPLACE INTO principals VALUES(?,0)", (intent.actor,))
            db.execute("INSERT OR REPLACE INTO subjects VALUES(?,?,?,?,?)",
                       (intent.subject, int(eligible), 1, "PASS", int(recorded_truth)))
            db.execute("INSERT OR REPLACE INTO grants VALUES(?,?,?,?,?,?,?,?)",
                       (intent.approval_id, intent.actor, "trusted-human-reviewer", intent.scope,
                        digest(intent.payload()), now, expires_at, 0))
            db.execute("COMMIT")

    def change(self, *, subject: str | None = None, eligible: bool | None = None,
               truth: bool | None = None, evidence_status: str | None = None,
               maximum: int | None = None, actor: str | None = None,
               revoke: bool = False):
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            if subject is not None and any(x is not None for x in (eligible, truth, evidence_status)):
                current = db.execute("SELECT * FROM subjects WHERE subject=?", (subject,)).fetchone()
                if current is None:
                    raise ValueError("unknown subject")
                db.execute("UPDATE subjects SET eligible=?, recorded_truth=?, evidence_status=?,version=version+1 WHERE subject=?",
                           (int(eligible) if eligible is not None else current["eligible"],
                            int(truth) if truth is not None else current["recorded_truth"],
                            evidence_status if evidence_status is not None else current["evidence_status"], subject))
            if maximum is not None:
                db.execute("UPDATE rules SET maximum=?,version=version+1 WHERE id=1", (maximum,))
            if revoke:
                if actor is None:
                    raise ValueError("actor required to revoke")
                db.execute("UPDATE principals SET epoch=epoch+1 WHERE actor=?", (actor,))
            db.execute("COMMIT")

    def _check(self, db: sqlite3.Connection, intent: Intent, *, now: int) -> Result:
        # Historical successful effect is readable after a later revocation: NO second write.
        previous = db.execute("SELECT * FROM effects WHERE effect_id=?", (intent.effect_id,)).fetchone()
        if previous is not None:
            if previous["payload_hash"] == digest(intent.payload()) and previous["approval_id"] == intent.approval_id:
                return Result("IDEMPOTENT_REPLAY", False, True, previous["commit_version"])
            return Result("EFFECT_ID_CONFLICT", False)
        if not isinstance(intent.amount_cents, int) or isinstance(intent.amount_cents, bool) or intent.amount_cents <= 0:
            return Result("INVALID_AMOUNT", False)
        grant = db.execute("SELECT * FROM grants WHERE approval_id=?", (intent.approval_id,)).fetchone()
        if grant is None or grant["actor"] != intent.actor or grant["scope"] != intent.scope or grant["payload_hash"] != digest(intent.payload()):
            return Result("INVALID_GRANT_OR_PAYLOAD", False)
        principal = db.execute("SELECT epoch FROM principals WHERE actor=?", (intent.actor,)).fetchone()
        if principal is None or principal["epoch"] != grant["epoch"]:
            return Result("REVOKED", False)
        if not (grant["issued_at"] <= now < grant["expires_at"]):
            return Result("EXPIRED_OR_EARLY", False)
        record = db.execute("SELECT * FROM subjects WHERE subject=?", (intent.subject,)).fetchone()
        if record is None or not record["eligible"] or record["evidence_status"] != "PASS":
            return Result("EVIDENCE_NOT_PASS", False)
        if intent.expected_version is not None and record["version"] != intent.expected_version:
            return Result("SUBJECT_VERSION_CHANGED", False)
        rule = db.execute("SELECT * FROM rules WHERE id=1").fetchone()
        if intent.amount_cents > rule["maximum"]:
            return Result("POLICY_LIMIT", False)
        consumed = db.execute("SELECT effect_id FROM effects WHERE approval_id=?", (intent.approval_id,)).fetchone()
        if consumed is not None:
            return Result("GRANT_ALREADY_USED", False)
        return Result("READY", False, False, record["version"])

    def preview(self, intent: Intent, *, now: int = 110) -> Result:
        with self._connect() as db:
            return self._check(db, intent, now=now)

    def commit(self, intent: Intent, *, now: int = 110, lose_response: bool = False) -> Result:
        """Check and INSERT under the same SQLite write transaction (linearization)."""
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            result = self._check(db, intent, now=now)
            if result.code != "READY":
                db.execute("COMMIT")
                return result
            db.execute("INSERT INTO effects VALUES(?,?,?,?,?,?,?)",
                       (intent.effect_id, intent.approval_id, digest(intent.payload()),
                        intent.amount_cents, intent.subject, result.state_version, "COMMITTED"))
            db.execute("COMMIT")
        if lose_response:
            raise LostResponse("commit succeeded; response was lost")
        return Result("COMMITTED", True, False, result.state_version)

    def effect_count(self) -> int:
        with self._connect() as db:
            return db.execute("SELECT count(*) FROM effects").fetchone()[0]

    def reconcile(self, intent: Intent) -> Result:
        """Authoritative read, distinguishing no effect / committed effect / id collision."""
        with self._connect() as db:
            r = db.execute("SELECT * FROM effects WHERE effect_id=?", (intent.effect_id,)).fetchone()
            if r is None:
                return Result("NOT_FOUND", False)
            if r["payload_hash"] != digest(intent.payload()) or r["approval_id"] != intent.approval_id:
                return Result("EFFECT_ID_CONFLICT", False)
            return Result("RECONCILED_COMMITTED", False, True, r["commit_version"])

    def recorded_truth_for(self, subject: str) -> bool:
        """Independent experiment oracle; inaccessible to the policy check."""
        with self._connect() as db:
            row = db.execute("SELECT recorded_truth FROM subjects WHERE subject=?", (subject,)).fetchone()
            return bool(row[0])
