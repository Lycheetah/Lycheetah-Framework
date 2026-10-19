"""Forge IV — consent/intention semantics over the existing Lycheetah CommitFence.

Educational integration adapter, not an authorization provider or an identity service.
Fenced finality still belongs to upstream CommitFence. A trusted host MUST ensure
agents cannot call the fence or this bridge's owner methods directly.

Separate SQLite ledger vs underlying fence => NO cross-database atomicity.
We use revoke-before-change and generation-matching checks to fail closed for
new issuances *through this wrapper*. If the host exposes direct fence handles,
any claim about journal enforcement is void.
"""
from __future__ import annotations

from dataclasses import dataclass
from contextlib import contextmanager
from pathlib import Path
import hashlib
import json
import sqlite3
import threading
from typing import Any, Protocol


def _canonical(obj: dict) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False)


def _digest(obj: dict) -> str:
    return hashlib.sha256(_canonical(obj).encode("utf-8")).hexdigest()


class FencePort(Protocol):
    def revoke(self, principal: str, scope_key: str) -> Any: ...
    def activate(self, principal: str, scope_key: str) -> Any: ...
    def state(self, principal: str, scope_key: str) -> dict | None: ...
    def issue_handle(self, principal: str, scope_key: str, action: Any) -> tuple[Any, Any]: ...
    def commit(self, handle_id: str, action: Any) -> Any: ...


@dataclass(frozen=True)
class HumanIntent:
    principal: str
    scope_key: str
    purpose: str
    action_hash: str
    generation: int
    version: int
    active: bool


@dataclass(frozen=True)
class BridgeVerdict:
    allowed: bool
    reason: str
    handle: Any = None


class IntentAuthorityBridge:
    """Trusted-host API translating an endorsed intention into fence generations.

    The host, NOT the model, must authenticate the principal and show an exact
    action preview to the human. `grant` has no proof of genuine understanding.
    Neither the principal name nor an `action_hash` is a signature of consent.
    """
    def __init__(self, fence: FencePort, journal_path: str | Path):
        self.fence = fence
        self.path = Path(journal_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._mutex = threading.RLock()
        with self._db() as con:
            con.executescript("""
                CREATE TABLE IF NOT EXISTS intents (
                  principal TEXT NOT NULL, scope_key TEXT NOT NULL,
                  version INTEGER NOT NULL, generation INTEGER NOT NULL,
                  purpose TEXT NOT NULL, action_hash TEXT NOT NULL,
                  active INTEGER NOT NULL CHECK(active IN (0,1)),
                  PRIMARY KEY(principal, scope_key));
                CREATE TABLE IF NOT EXISTS intent_events (
                  seq INTEGER PRIMARY KEY AUTOINCREMENT,
                  principal TEXT NOT NULL, scope_key TEXT NOT NULL,
                  kind TEXT NOT NULL, version INTEGER NOT NULL,
                  generation INTEGER NOT NULL, reason_class TEXT NOT NULL,
                  action_hash TEXT NOT NULL);
            """)

    @contextmanager
    def _db(self):
        con = sqlite3.connect(str(self.path), timeout=15)
        con.row_factory = sqlite3.Row
        try:
            with con:
                yield con
        finally:
            con.close()

    @staticmethod
    def _nonempty(value: str, what: str, limit: int = 1000) -> str:
        if not isinstance(value, str) or not value.strip() or len(value) > limit:
            raise ValueError(f"invalid {what}")
        return value

    @staticmethod
    def _action_hash(action: Any) -> str:
        h = getattr(action, "action_hash", None)
        if not isinstance(h, str) or len(h) != 64 or any(x not in "0123456789abcdef" for x in h):
            raise ValueError("action must have an exact 64-character lowercase SHA-256 action_hash")
        return h

    def current(self, principal: str, scope_key: str) -> HumanIntent | None:
        with self._db() as con:
            row = con.execute("SELECT * FROM intents WHERE principal=? AND scope_key=?",
                              (principal, scope_key)).fetchone()
        if row is None:
            return None
        return HumanIntent(row["principal"], row["scope_key"], row["purpose"],
                           row["action_hash"], int(row["generation"]),
                           int(row["version"]), bool(row["active"]))

    def _log(self, con: sqlite3.Connection, *, principal: str, scope_key: str,
             kind: str, version: int, generation: int, reason_class: str,
             action_hash: str, purpose: str, active: bool):
        con.execute("""INSERT INTO intents(principal,scope_key,version,generation,purpose,
                      action_hash,active) VALUES(?,?,?,?,?,?,?)
                      ON CONFLICT(principal,scope_key) DO UPDATE SET
                      version=excluded.version,generation=excluded.generation,
                      purpose=excluded.purpose,action_hash=excluded.action_hash,
                      active=excluded.active""",
                    (principal,scope_key,version,generation,purpose,action_hash,int(active)))
        con.execute("""INSERT INTO intent_events(principal,scope_key,kind,version,
                      generation,reason_class,action_hash) VALUES(?,?,?,?,?,?,?)""",
                    (principal,scope_key,kind,version,generation,reason_class,action_hash))

    def grant(self, principal: str, scope_key: str, purpose: str, action: Any,
              *, reason_class: str = "endorsed") -> HumanIntent:
        """Trusted-host new/revised intention. Revoke old authority before regrant.

        A journal BEGIN IMMEDIATE serializes revisions between bridge processes.
        The fence and journal are NOT atomically coupled: an interrupted update
        can deny future work, but a bare upstream handle can bypass this layer.
        """
        self._nonempty(principal, "principal", 256)
        self._nonempty(scope_key, "scope_key", 256)
        self._nonempty(purpose, "purpose")
        self._nonempty(reason_class, "reason class", 64)
        action_hash = self._action_hash(action)
        with self._mutex, self._db() as con:
            con.execute("BEGIN IMMEDIATE")
            row = con.execute("SELECT version FROM intents WHERE principal=? AND scope_key=?",
                              (principal, scope_key)).fetchone()
            new_version = 1 if row is None else int(row[0]) + 1
            self.fence.revoke(principal, scope_key)
            state = self.fence.state(principal, scope_key)
            if not state or state["active"]:
                raise RuntimeError("fence failed to revoke")
            self._log(con, principal=principal, scope_key=scope_key, kind="CHANGE_PENDING",
                      version=new_version, generation=state["generation"],
                      reason_class=reason_class, action_hash=action_hash, purpose=purpose,
                      active=False)
            result = self.fence.activate(principal, scope_key)
            current_state = self.fence.state(principal, scope_key)
            if (not current_state or not current_state["active"] or
                    current_state["generation"] != result.generation):
                raise RuntimeError("new fence generation not active")
            self._log(con, principal=principal, scope_key=scope_key, kind="GRANT_ACTIVE",
                      version=new_version, generation=result.generation,
                      reason_class=reason_class, action_hash=action_hash, purpose=purpose,
                      active=True)
            return HumanIntent(principal, scope_key, purpose, action_hash,
                               result.generation, new_version, True)

    def withdraw(self, principal: str, scope_key: str) -> HumanIntent | None:
        """Trusted-user withdrawal; no personal justification is required."""
        self._nonempty(principal, "principal", 256)
        self._nonempty(scope_key, "scope_key", 256)
        with self._mutex, self._db() as con:
            con.execute("BEGIN IMMEDIATE")
            prior = con.execute("SELECT * FROM intents WHERE principal=? AND scope_key=?",
                                (principal, scope_key)).fetchone()
            result = self.fence.revoke(principal, scope_key)
            if prior is None:
                return None
            next_v = int(prior["version"]) + 1
            self._log(con, principal=principal, scope_key=scope_key, kind="WITHDRAW",
                      version=next_v, generation=result.generation,
                      reason_class="not_required", action_hash=prior["action_hash"],
                      purpose=prior["purpose"], active=False)
            return HumanIntent(principal, scope_key, prior["purpose"], prior["action_hash"],
                               result.generation, next_v, False)

    def _matched_intent(self, principal: str, scope_key: str, action: Any):
        record = self.current(principal, scope_key)
        state = self.fence.state(principal, scope_key)
        if record is None or not record.active:
            return None, "no_active_endorsement"
        if not state or not state["active"] or state["generation"] != record.generation:
            return None, "generation_not_current"
        if self._action_hash(action) != record.action_hash:
            return None, "action_not_endorsed"
        return record, "matched"

    def issue(self, principal: str, scope_key: str, action: Any) -> BridgeVerdict:
        """Issue an upstream handle only for current, exact endorsed action.

        Recheck after issuance, which closes the gap in which a concurrent
        revision can activate a *new* generation between our check and issue.
        """
        with self._mutex:
            record, reason = self._matched_intent(principal, scope_key, action)
            if record is None:
                return BridgeVerdict(False, reason)
            handle, decision = self.fence.issue_handle(principal, scope_key, action)
            if handle is None:
                return BridgeVerdict(False, getattr(decision, "reason", "upstream_denied"))
            latest, reason = self._matched_intent(principal, scope_key, action)
            if (latest is None or latest.generation != record.generation or
                    handle.generation != record.generation):
                # Issued but never released; existing handle cannot commit when
                # old generation is revoked. If another actor changed journal
                # without fencing, this integration boundary has been bypassed.
                return BridgeVerdict(False, "changed_during_issue")
            return BridgeVerdict(True, "issued", handle)

    def commit(self, handle: Any, action: Any) -> Any:
        """Defer ONLY to upstream finality; never reinterpret existing effects.

        The upstream must enforce action hash, generation and effect-id binding.
        Any remote provider is outside this model's atomic safety boundary.
        """
        return self.fence.commit(handle.handle_id, action)

    def event_history(self) -> list[dict]:
        with self._db() as con:
            return [dict(r) for r in con.execute("SELECT * FROM intent_events ORDER BY seq")]
