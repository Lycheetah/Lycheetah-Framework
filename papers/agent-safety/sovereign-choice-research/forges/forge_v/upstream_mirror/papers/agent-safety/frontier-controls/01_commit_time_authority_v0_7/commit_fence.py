#!/usr/bin/env python3
"""
Lycheetah Commit-Time Authorization Fence v0.7

Problem:
    A permit can be valid at admission and even at a pre-dispatch recheck, then
    be revoked before the external effect becomes durable.

Mechanism:
    The protected finality sink itself serializes authority generation and
    effect commit in the same SQLite transaction.

Property within this prototype:
    If revocation is ordered before protected commit, a handle from the old
    generation cannot create a new effect.

This is generation fencing / commit-time authorization, an established
distributed-systems/security pattern. Novelty is not claimed. The packet tests
its composition with Lycheetah's exact action/effect binding.

Boundary:
    The guarantee only covers effects committed through this protected sink.
    A remote provider that does not participate in fencing/atomic finality can
    still accept an already-dispatched stale request.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import secrets
import sqlite3
from typing import Optional

from pathlib import Path as _SupportPath
import sys as _support_sys
_support_sys.path.insert(0, str(_SupportPath(__file__).resolve().parents[1]))
from research_support import Action  # noqa: E402


@dataclass(frozen=True)
class ExecutionHandle:
    handle_id: str
    principal: str
    scope_key: str
    generation: int
    action_hash: str
    effect_id: str


@dataclass(frozen=True)
class FenceDecision:
    state: str
    reason: str
    generation: int | None = None
    audit_sequence: int | None = None
    receipt: str | None = None


class CommitFence:
    """Protected authority state + finality sink in one serialized store."""

    def __init__(self, db_path: str | Path):
        self.db_path = str(db_path)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def connect(self):
        con = sqlite3.connect(self.db_path, timeout=20, isolation_level=None)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys=ON")
        con.execute("PRAGMA journal_mode=WAL")
        con.execute("PRAGMA synchronous=FULL")
        return con

    def _init_db(self):
        with self.connect() as con:
            con.executescript("""
            CREATE TABLE IF NOT EXISTS authorities(
                principal TEXT NOT NULL,
                scope_key TEXT NOT NULL,
                generation INTEGER NOT NULL,
                active INTEGER NOT NULL CHECK(active IN (0,1)),
                PRIMARY KEY(principal, scope_key)
            );

            CREATE TABLE IF NOT EXISTS handles(
                handle_id TEXT PRIMARY KEY,
                principal TEXT NOT NULL,
                scope_key TEXT NOT NULL,
                generation INTEGER NOT NULL,
                action_hash TEXT NOT NULL,
                effect_id TEXT NOT NULL,
                consumed INTEGER NOT NULL DEFAULT 0 CHECK(consumed IN (0,1))
            );

            CREATE TABLE IF NOT EXISTS effects(
                effect_id TEXT PRIMARY KEY,
                action_hash TEXT NOT NULL,
                handle_id TEXT NOT NULL,
                generation INTEGER NOT NULL,
                receipt TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS audit(
                sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                kind TEXT NOT NULL,
                principal TEXT,
                scope_key TEXT,
                generation INTEGER,
                handle_id TEXT,
                effect_id TEXT,
                detail TEXT NOT NULL
            );
            """)

    def _audit(self, con, kind: str, *, principal=None, scope_key=None,
               generation=None, handle_id=None, effect_id=None, detail=""):
        cur = con.execute(
            "INSERT INTO audit(kind,principal,scope_key,generation,handle_id,"
            "effect_id,detail) VALUES(?,?,?,?,?,?,?)",
            (kind, principal, scope_key, generation, handle_id, effect_id, detail),
        )
        return int(cur.lastrowid)

    def activate(self, principal: str, scope_key: str) -> FenceDecision:
        """Create or regrant authority. Every transition advances generation."""
        with self.connect() as con:
            con.execute("BEGIN IMMEDIATE")
            row = con.execute(
                "SELECT generation FROM authorities WHERE principal=? AND scope_key=?",
                (principal, scope_key),
            ).fetchone()
            generation = 1 if row is None else int(row["generation"]) + 1
            con.execute(
                "INSERT INTO authorities(principal,scope_key,generation,active)"
                " VALUES(?,?,?,1)"
                " ON CONFLICT(principal,scope_key) DO UPDATE SET"
                " generation=excluded.generation, active=1",
                (principal, scope_key, generation),
            )
            seq = self._audit(
                con, "ACTIVATE", principal=principal, scope_key=scope_key,
                generation=generation, detail="authority active"
            )
            con.execute("COMMIT")
        return FenceDecision("ACTIVE", "authority-activated", generation, seq)

    def revoke(self, principal: str, scope_key: str) -> FenceDecision:
        """Revocation itself advances generation, fencing all older handles."""
        with self.connect() as con:
            con.execute("BEGIN IMMEDIATE")
            row = con.execute(
                "SELECT generation FROM authorities WHERE principal=? AND scope_key=?",
                (principal, scope_key),
            ).fetchone()
            if row is None:
                generation = 1
                con.execute(
                    "INSERT INTO authorities(principal,scope_key,generation,active)"
                    " VALUES(?,?,?,0)",
                    (principal, scope_key, generation),
                )
            else:
                generation = int(row["generation"]) + 1
                con.execute(
                    "UPDATE authorities SET generation=?,active=0"
                    " WHERE principal=? AND scope_key=?",
                    (generation, principal, scope_key),
                )
            seq = self._audit(
                con, "REVOKE", principal=principal, scope_key=scope_key,
                generation=generation, detail="authority revoked"
            )
            con.execute("COMMIT")
        return FenceDecision("REVOKED", "authority-revoked", generation, seq)

    def state(self, principal: str, scope_key: str):
        with self.connect() as con:
            row = con.execute(
                "SELECT generation,active FROM authorities"
                " WHERE principal=? AND scope_key=?",
                (principal, scope_key),
            ).fetchone()
        if row is None:
            return None
        return {"generation": int(row["generation"]), "active": bool(row["active"])}

    def issue_handle(self, principal: str, scope_key: str,
                     action: Action) -> tuple[Optional[ExecutionHandle], FenceDecision]:
        with self.connect() as con:
            con.execute("BEGIN IMMEDIATE")
            row = con.execute(
                "SELECT generation,active FROM authorities"
                " WHERE principal=? AND scope_key=?",
                (principal, scope_key),
            ).fetchone()
            if row is None or not row["active"]:
                generation = None if row is None else int(row["generation"])
                seq = self._audit(
                    con, "ISSUE_DENY", principal=principal, scope_key=scope_key,
                    generation=generation, effect_id=action.effect_id,
                    detail="authority inactive"
                )
                con.execute("COMMIT")
                return None, FenceDecision(
                    "DENY", "authority-inactive", generation, seq
                )

            generation = int(row["generation"])
            handle_id = "xh-" + secrets.token_hex(16)
            con.execute(
                "INSERT INTO handles(handle_id,principal,scope_key,generation,"
                "action_hash,effect_id,consumed) VALUES(?,?,?,?,?,?,0)",
                (
                    handle_id, principal, scope_key, generation,
                    action.action_hash, action.effect_id,
                ),
            )
            seq = self._audit(
                con, "ISSUE", principal=principal, scope_key=scope_key,
                generation=generation, handle_id=handle_id,
                effect_id=action.effect_id, detail="execution handle issued"
            )
            con.execute("COMMIT")
        return ExecutionHandle(
            handle_id, principal, scope_key, generation,
            action.action_hash, action.effect_id
        ), FenceDecision("ISSUED", "execution-handle-issued", generation, seq)

    def commit(self, handle_id: str, action: Action) -> FenceDecision:
        """Linearization point for the protected external effect.

        Authority generation check, single-use consumption and effect creation
        occur under one BEGIN IMMEDIATE transaction.
        """
        with self.connect() as con:
            con.execute("BEGIN IMMEDIATE")
            handle = con.execute(
                "SELECT * FROM handles WHERE handle_id=?", (handle_id,)
            ).fetchone()
            if handle is None:
                seq = self._audit(
                    con, "COMMIT_DENY", effect_id=action.effect_id,
                    detail="unknown handle"
                )
                con.execute("COMMIT")
                return FenceDecision("DENY", "unknown-handle", None, seq)

            principal = handle["principal"]
            scope_key = handle["scope_key"]
            handle_gen = int(handle["generation"])

            # Idempotent confirmed effect lookup first.
            existing = con.execute(
                "SELECT * FROM effects WHERE effect_id=?", (action.effect_id,)
            ).fetchone()
            if existing is not None:
                if existing["action_hash"] != action.action_hash:
                    seq = self._audit(
                        con, "COMMIT_DENY", principal=principal, scope_key=scope_key,
                        generation=handle_gen, handle_id=handle_id,
                        effect_id=action.effect_id,
                        detail="effect id reused for different action"
                    )
                    con.execute("COMMIT")
                    return FenceDecision(
                        "DENY", "effect-id-reused", handle_gen, seq
                    )
                seq = self._audit(
                    con, "COMMIT_IDEMPOTENT", principal=principal,
                    scope_key=scope_key, generation=int(existing["generation"]),
                    handle_id=handle_id, effect_id=action.effect_id,
                    detail="existing confirmed effect"
                )
                con.execute("COMMIT")
                return FenceDecision(
                    "CONFIRMED", "idempotent-existing-effect",
                    int(existing["generation"]), seq, existing["receipt"]
                )

            if handle["action_hash"] != action.action_hash:
                seq = self._audit(
                    con, "COMMIT_DENY", principal=principal, scope_key=scope_key,
                    generation=handle_gen, handle_id=handle_id,
                    effect_id=action.effect_id, detail="action substitution"
                )
                con.execute("COMMIT")
                return FenceDecision(
                    "DENY", "action-substitution", handle_gen, seq
                )

            if handle["consumed"]:
                seq = self._audit(
                    con, "COMMIT_DENY", principal=principal, scope_key=scope_key,
                    generation=handle_gen, handle_id=handle_id,
                    effect_id=action.effect_id, detail="handle consumed"
                )
                con.execute("COMMIT")
                return FenceDecision(
                    "DENY", "handle-consumed", handle_gen, seq
                )

            auth = con.execute(
                "SELECT generation,active FROM authorities"
                " WHERE principal=? AND scope_key=?",
                (principal, scope_key),
            ).fetchone()
            if auth is None:
                seq = self._audit(
                    con, "COMMIT_DENY", principal=principal, scope_key=scope_key,
                    generation=None, handle_id=handle_id,
                    effect_id=action.effect_id, detail="authority missing"
                )
                con.execute("COMMIT")
                return FenceDecision("DENY", "authority-missing", None, seq)

            current_gen = int(auth["generation"])
            if not auth["active"]:
                seq = self._audit(
                    con, "COMMIT_DENY", principal=principal, scope_key=scope_key,
                    generation=current_gen, handle_id=handle_id,
                    effect_id=action.effect_id, detail="authority inactive at commit"
                )
                con.execute("COMMIT")
                return FenceDecision(
                    "DENY", "authority-inactive-at-commit", current_gen, seq
                )

            if current_gen != handle_gen:
                seq = self._audit(
                    con, "COMMIT_DENY", principal=principal, scope_key=scope_key,
                    generation=current_gen, handle_id=handle_id,
                    effect_id=action.effect_id,
                    detail=f"generation mismatch handle={handle_gen}"
                )
                con.execute("COMMIT")
                return FenceDecision(
                    "DENY", "stale-generation", current_gen, seq
                )

            receipt = f"fenced-receipt:{action.effect_id}:g{current_gen}"
            con.execute(
                "INSERT INTO effects(effect_id,action_hash,handle_id,generation,receipt)"
                " VALUES(?,?,?,?,?)",
                (
                    action.effect_id, action.action_hash, handle_id,
                    current_gen, receipt,
                ),
            )
            con.execute(
                "UPDATE handles SET consumed=1 WHERE handle_id=?", (handle_id,)
            )
            seq = self._audit(
                con, "COMMIT_EFFECT", principal=principal, scope_key=scope_key,
                generation=current_gen, handle_id=handle_id,
                effect_id=action.effect_id, detail="effect committed"
            )
            con.execute("COMMIT")
            return FenceDecision(
                "COMMITTED", "effect-committed", current_gen, seq, receipt
            )

    def effect_count(self):
        with self.connect() as con:
            return int(con.execute("SELECT COUNT(*) FROM effects").fetchone()[0])

    def audit(self):
        with self.connect() as con:
            return [dict(r) for r in con.execute(
                "SELECT * FROM audit ORDER BY sequence"
            ).fetchall()]


class PreDispatchOnlyBaseline:
    """Deliberately weaker comparison.

    It verifies a handle generation before dispatch, but the provider does not
    re-check protected authority at commit. Revocation between check and commit
    therefore cannot stop the already released request.
    """

    def __init__(self, fence: CommitFence):
        self.fence = fence
        self.released = {}

    def precheck(self, handle: ExecutionHandle, action: Action) -> bool:
        state = self.fence.state(handle.principal, handle.scope_key)
        ok = bool(
            state
            and state["active"]
            and state["generation"] == handle.generation
            and handle.action_hash == action.action_hash
        )
        if ok:
            self.released[action.effect_id] = action.action_hash
        return ok

    def remote_commit(self, action: Action) -> bool:
        # Simulates a remote provider that received the request already and has
        # no generation-fence interface.
        expected = self.released.get(action.effect_id)
        return expected == action.action_hash


class ConventionalGenerationFence:
    """Independent minimal matched conventional state machine."""
    def __init__(self):
        self.generation = 1
        self.active = True
        self.handle_generation = None
        self.consumed = False
        self.effects = 0

    def issue(self):
        if not self.active:
            return False
        self.handle_generation = self.generation
        self.consumed = False
        return True

    def revoke(self):
        self.generation += 1
        self.active = False

    def regrant(self):
        self.generation += 1
        self.active = True

    def commit(self):
        if self.handle_generation is None:
            return False
        # Stable effect identity is idempotent across retries and re-issued
        # handles. This baseline models "new external effect", not mere success.
        if self.effects > 0:
            return False
        if self.consumed:
            return False
        if not self.active or self.handle_generation != self.generation:
            return False
        self.consumed = True
        self.effects += 1
        return True
