"""Lycheetah Forge III: intent-versioned commit fence, LOCAL synthetic reference.

NOT a production agent/tool guard. Trusted caller separation, identity proof, actual
provider finality, semantic consent, external anchoring, and security review are
out of scope. All effects below are rows in the same SQLite database.

The core distinction is that intent changes are *authority events* rather than
negative scores for the person. Commit and validity check are one transaction.
"""
from __future__ import annotations
from dataclasses import dataclass
from contextlib import closing
from pathlib import Path
from typing import Callable
import hashlib
import hmac
import json
import sqlite3
import time

HIGH_IMPACT = frozenset({"send_email", "publish_post", "transfer_money", "repo_write"})
LOW_IMPACT = frozenset({"prepare_draft", "read_document"})
KNOWN_OPS = HIGH_IMPACT | LOW_IMPACT


def canonical(value: dict) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


@dataclass(frozen=True)
class Action:
    owner: str
    agent: str
    operation: str
    resource: str
    effect_id: str
    payload: str

    def body(self) -> dict:
        return {"owner": self.owner, "agent": self.agent, "operation": self.operation,
                "resource": self.resource, "effect_id": self.effect_id, "payload": self.payload}

    def digest(self) -> str:
        return hashlib.sha256(canonical(self.body()).encode()).hexdigest()


@dataclass(frozen=True)
class Verdict:
    state: str
    reason: str
    sequence: int
    receipt: str = ""

    @property
    def committed(self) -> bool:
        return self.state == "COMMITTED"


class ChoiceFence:
    """The host is responsible for isolating trusted owner calls from agents."""
    def __init__(self, db_path: str | Path, *, key: bytes, clock: Callable[[], int] | None = None):
        if not isinstance(key, bytes) or len(key) < 16:
            raise ValueError("key must be bytes of at least 16 characters")
        self.path = str(db_path)
        self.key = key
        self.clock = clock or (lambda: int(time.time()))
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        # :memory: is one connection per call; use a shared database file for this design.
        if self.path == ":memory:":
            raise ValueError("Use a dedicated SQLite file for atomic cross-connection testing")
        with closing(self.connect()) as cx:
            cx.executescript("""
                CREATE TABLE IF NOT EXISTS owner_intents (
                  owner TEXT PRIMARY KEY, version INTEGER NOT NULL CHECK(version >= 1));
                CREATE TABLE IF NOT EXISTS tickets (
                  ticket_id TEXT PRIMARY KEY, owner TEXT NOT NULL, version INTEGER NOT NULL,
                  action_hash TEXT NOT NULL, effect_id TEXT NOT NULL,
                  expires_at INTEGER NOT NULL, approved INTEGER NOT NULL,
                  revoked INTEGER NOT NULL DEFAULT 0, consumed INTEGER NOT NULL DEFAULT 0);
                CREATE TABLE IF NOT EXISTS local_effects (
                  effect_id TEXT PRIMARY KEY, ticket_id TEXT NOT NULL UNIQUE,
                  action_hash TEXT NOT NULL, receipt TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS audit (
                  seq INTEGER PRIMARY KEY AUTOINCREMENT,
                  kind TEXT NOT NULL, detail TEXT NOT NULL,
                  previous TEXT NOT NULL, digest TEXT NOT NULL, mac TEXT NOT NULL);
            """)

    def connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.path, isolation_level=None, timeout=15)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA journal_mode=WAL")
        db.execute("PRAGMA busy_timeout=15000")
        db.execute("PRAGMA synchronous=FULL")
        return db

    @staticmethod
    def validate_string(value: str, field: str) -> None:
        if not isinstance(value, str) or not value.strip() or len(value) > 256:
            raise ValueError(f"Invalid {field}")

    def now(self) -> int:
        now = self.clock()
        if type(now) is not int or now < 0:
            raise ValueError("Only a trusted host may supply a valid clock")
        return now

    def _audit(self, cx: sqlite3.Connection, kind: str, detail: dict) -> tuple[int, str]:
        row = cx.execute("SELECT digest FROM audit ORDER BY seq DESC LIMIT 1").fetchone()
        previous = row[0] if row else "GENESIS"
        data = canonical(detail)
        digest = hashlib.sha256((previous + "|" + kind + "|" + data).encode()).hexdigest()
        mac = hmac.new(self.key, digest.encode(), hashlib.sha256).hexdigest()
        cur = cx.execute("INSERT INTO audit(kind,detail,previous,digest,mac) VALUES (?,?,?,?,?)",
                         (kind, data, previous, digest, mac))
        return int(cur.lastrowid), digest

    def register(self, owner: str) -> None:
        """Trusted-owner API. No external authentication happens here."""
        self.validate_string(owner, "owner")
        with closing(self.connect()) as cx:
            cx.execute("BEGIN IMMEDIATE")
            cx.execute("INSERT OR IGNORE INTO owner_intents(owner,version) VALUES (?,1)", (owner,))
            self._audit(cx, "REGISTER", {"owner": owner})
            cx.execute("COMMIT")

    def revise(self, owner: str, *, reason: str = "prefer_not_to_say") -> int:
        """Invalidate all old-version tickets. No moral judgement or productivity score."""
        self.validate_string(owner, "owner")
        with closing(self.connect()) as cx:
            cx.execute("BEGIN IMMEDIATE")
            row = cx.execute("SELECT version FROM owner_intents WHERE owner=?", (owner,)).fetchone()
            if row is None:
                raise ValueError("owner unknown")
            next_version = int(row[0]) + 1
            cx.execute("UPDATE owner_intents SET version=? WHERE owner=?", (next_version, owner))
            self._audit(cx, "REVISE", {"owner": owner, "version": next_version,
                       "reason_hash": hashlib.sha256(reason.encode()).hexdigest()})
            cx.execute("COMMIT")
            return next_version

    def issue(self, ticket_id: str, action: Action, *, expires_at: int,
              explicit_human_approval: bool) -> int:
        """Trusted-owner API. 'explicit_human_approval' is a simulated assertion,
        NOT proof a person ever saw the action; production must authenticate it.
        """
        self.validate_string(ticket_id, "ticket_id")
        for f, v in action.body().items():
            self.validate_string(v, f)
        if action.operation not in KNOWN_OPS:
            raise ValueError("unknown operation")
        if type(expires_at) is not int or expires_at <= self.now():
            raise ValueError("ticket expiry must be in the future")
        if type(explicit_human_approval) is not bool:
            raise ValueError("approval must be boolean")
        if action.operation in HIGH_IMPACT and not explicit_human_approval:
            raise ValueError("high-impact action needs explicitly asserted approval")
        with closing(self.connect()) as cx:
            cx.execute("BEGIN IMMEDIATE")
            row = cx.execute("SELECT version FROM owner_intents WHERE owner=?", (action.owner,)).fetchone()
            if row is None:
                raise ValueError("owner unknown")
            version = int(row[0])
            cx.execute("""INSERT INTO tickets(ticket_id, owner, version, action_hash,
                        effect_id, expires_at, approved) VALUES (?,?,?,?,?,?,?)""",
                       (ticket_id, action.owner, version, action.digest(), action.effect_id,
                        expires_at, int(explicit_human_approval)))
            self._audit(cx, "ISSUE", {"ticket": ticket_id, "owner": action.owner,
                        "intent_version": version, "action_hash": action.digest(),
                        "expires_at": expires_at, "approved": explicit_human_approval})
            cx.execute("COMMIT")
            return version

    def revoke(self, owner: str, ticket_id: str) -> bool:
        """Trusted-owner API. Called before finality, this prevents local commit."""
        with closing(self.connect()) as cx:
            cx.execute("BEGIN IMMEDIATE")
            cur = cx.execute("UPDATE tickets SET revoked=1 WHERE ticket_id=? AND owner=? AND revoked=0",
                             (ticket_id, owner))
            self._audit(cx, "REVOKE", {"owner": owner, "ticket": ticket_id, "changed": cur.rowcount == 1})
            cx.execute("COMMIT")
            return cur.rowcount == 1

    def _gate(self, cx: sqlite3.Connection, ticket_id: str, action: Action, now: int) -> str:
        row = cx.execute("""SELECT t.owner,t.version,t.action_hash,t.effect_id,t.expires_at,
                        t.approved,t.revoked,t.consumed,o.version AS current_version
                        FROM tickets t JOIN owner_intents o ON o.owner=t.owner
                        WHERE t.ticket_id=?""", (ticket_id,)).fetchone()
        if row is None:
            return "unknown_ticket"
        if action.operation not in KNOWN_OPS:
            return "unknown_operation"
        if row[0] != action.owner:
            return "wrong_owner"
        if row[6]:
            return "revoked"
        if row[1] != row[8]:
            return "stale_intent"
        if now >= row[4]:
            return "expired"
        if row[7]:
            return "replayed"
        if row[3] != action.effect_id or not hmac.compare_digest(row[2], action.digest()):
            return "action_substitution"
        if action.operation in HIGH_IMPACT and not row[5]:
            return "approval_required"
        if cx.execute("SELECT 1 FROM local_effects WHERE effect_id=?", (action.effect_id,)).fetchone():
            return "effect_already_exists"
        return "allowed"

    def precheck(self, ticket_id: str, action: Action) -> str:
        """Deliberately insufficient by itself: no reservation of finality."""
        with closing(self.connect()) as cx:
            return self._gate(cx, ticket_id, action, self.now())

    def commit(self, ticket_id: str, action: Action) -> Verdict:
        """For LOCAL effect only, fence check + durable effect under one lock."""
        with closing(self.connect()) as cx:
            cx.execute("BEGIN IMMEDIATE")
            reason = self._gate(cx, ticket_id, action, self.now())
            if reason != "allowed":
                seq, digest = self._audit(cx, "DENY", {"ticket": ticket_id,
                              "effect": action.effect_id, "reason": reason})
                cx.execute("COMMIT")
                return Verdict("DENIED", reason, seq, digest)
            # Local finality: effect and ticket consumption share this transaction.
            receipt = "local:" + action.effect_id + ":" + action.digest()
            cx.execute("""INSERT INTO local_effects(effect_id,ticket_id,action_hash,receipt)
                         VALUES (?,?,?,?)""", (action.effect_id, ticket_id, action.digest(), receipt))
            cx.execute("UPDATE tickets SET consumed=1 WHERE ticket_id=?", (ticket_id,))
            seq, digest = self._audit(cx, "COMMIT", {"ticket": ticket_id,
                          "effect": action.effect_id, "action_hash": action.digest()})
            cx.execute("COMMIT")
            return Verdict("COMMITTED", "local_effect_committed", seq, receipt)

    def effect_count(self) -> int:
        with closing(self.connect()) as cx:
            return int(cx.execute("SELECT COUNT(*) FROM local_effects").fetchone()[0])

    def audit_ok(self) -> bool:
        with closing(self.connect()) as cx:
            previous = "GENESIS"
            for row in cx.execute("SELECT kind,detail,previous,digest,mac FROM audit ORDER BY seq"):
                expected = hashlib.sha256((previous + "|" + row[0] + "|" + row[1]).encode()).hexdigest()
                signed = hmac.new(self.key, expected.encode(), hashlib.sha256).hexdigest()
                if row[2] != previous or not hmac.compare_digest(expected, row[3]) or not hmac.compare_digest(signed, row[4]):
                    return False
                previous = row[3]
            return True


class PreDispatchOnlyBaseline:
    """Toy conventional TOCTOU anti-pattern: permission checked at release,
    remote sink cannot re-check authority or action payload at finality.
    This is NOT an actual competitor or the Lycheetah upstream fence.
    """
    def __init__(self, fence: ChoiceFence):
        self.fence = fence
        self.released: set[str] = set()
        self.events: list[dict] = []

    def predispatch(self, ticket: str, action: Action) -> bool:
        ok = self.fence.precheck(ticket, action) == "allowed"
        if ok:
            self.released.add(ticket)
        return ok

    def remote_commit(self, ticket: str, action: Action) -> bool:
        if ticket not in self.released:
            return False
        # The remote provider already accepted the request. There is no finality fence.
        self.events.append({"ticket": ticket, "action": action.body()})
        return True
