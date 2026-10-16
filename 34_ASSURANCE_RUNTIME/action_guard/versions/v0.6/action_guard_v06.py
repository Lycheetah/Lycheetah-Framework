"""Lycheetah Action Guard v0.6 — durable single-use action authorization ledger.

Research prototype only. Standard library; SQLite-backed durable state; no live provider.
The local ledger cannot make a remote effect atomic. Provider-specific conditional
execution and outcome reconciliation remain mandatory.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import sqlite3
from pathlib import Path
from typing import Any, Literal

Outcome = Literal["success", "failure", "unknown"]


def canonical_action(action: dict[str, Any]) -> str:
    return json.dumps(action, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def action_digest(action: dict[str, Any]) -> str:
    return sha256(canonical_action(action).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class Decision:
    allowed: bool
    reason: str
    effect_id: str | None = None
    status: str | None = None
    action: dict[str, Any] | None = None


class _ClosingConnection(sqlite3.Connection):
    """Connection context manager that also closes the descriptor on exit."""
    def __exit__(self, exc_type, exc, tb):
        try:
            return super().__exit__(exc_type, exc, tb)
        finally:
            self.close()


class PersistentActionGuard:
    """SQLite ledger with single-use approvals and fail-closed dispatch claims.

    Semantic boundary: a successful PREPARED -> DISPATCHING transaction is the local
    authorization linearization point. A later revocation blocks still-PREPARED work,
    but cannot guarantee cancellation of a remote request already in DISPATCHING.
    """

    def __init__(self, db_path: str | Path):
        self.db_path = str(db_path)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as c:
            c.execute("PRAGMA journal_mode=WAL")
            c.executescript("""
                CREATE TABLE IF NOT EXISTS authority (
                    actor TEXT PRIMARY KEY,
                    epoch INTEGER NOT NULL CHECK(epoch >= 0)
                );
                CREATE TABLE IF NOT EXISTS approvals (
                    approval_id TEXT PRIMARY KEY,
                    actor TEXT NOT NULL,
                    approver_id TEXT NOT NULL,
                    action_hash TEXT NOT NULL,
                    scope TEXT NOT NULL,
                    issued_at INTEGER NOT NULL,
                    expires_at INTEGER NOT NULL,
                    authority_epoch INTEGER NOT NULL
                );
                CREATE TABLE IF NOT EXISTS effects (
                    effect_id TEXT PRIMARY KEY,
                    approval_id TEXT NOT NULL UNIQUE REFERENCES approvals(approval_id),
                    actor TEXT NOT NULL,
                    action_json TEXT NOT NULL,
                    action_hash TEXT NOT NULL,
                    scope TEXT NOT NULL,
                    status TEXT NOT NULL CHECK(status IN
                      ('PREPARED','DISPATCHING','SUCCEEDED','FAILED','UNKNOWN','CANCELLED')),
                    created_at INTEGER NOT NULL,
                    updated_at INTEGER NOT NULL,
                    result_json TEXT,
                    reason TEXT
                );
                CREATE TABLE IF NOT EXISTS audit (
                    seq INTEGER PRIMARY KEY AUTOINCREMENT,
                    at INTEGER NOT NULL,
                    actor TEXT NOT NULL,
                    approval_id TEXT,
                    effect_id TEXT,
                    event TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    details_json TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS effects_status_idx ON effects(status);
                CREATE INDEX IF NOT EXISTS audit_effect_idx ON audit(effect_id, seq);
            """)

    def _connect(self) -> sqlite3.Connection:
        c = sqlite3.connect(self.db_path, timeout=15, isolation_level=None, factory=_ClosingConnection)
        c.row_factory = sqlite3.Row
        c.execute("PRAGMA foreign_keys=ON")
        c.execute("PRAGMA busy_timeout=15000")
        return c

    @staticmethod
    def _audit(c: sqlite3.Connection, at: int, actor: str, approval_id: str | None,
               effect_id: str | None, event: str, reason: str,
               details: dict[str, Any] | None = None) -> None:
        c.execute("INSERT INTO audit(at,actor,approval_id,effect_id,event,reason,details_json) VALUES(?,?,?,?,?,?,?)",
                  (at, actor, approval_id, effect_id, event, reason,
                   json.dumps(details or {}, sort_keys=True, separators=(",", ":"))))

    @staticmethod
    def _authority_epoch(c: sqlite3.Connection, actor: str) -> int:
        row = c.execute("SELECT epoch FROM authority WHERE actor=?", (actor,)).fetchone()
        return int(row["epoch"]) if row else 0

    @staticmethod
    def _validate(c: sqlite3.Connection, approval_id: str, actor: str,
                  action: dict[str, Any], scope: str, now: int) -> tuple[bool, str, sqlite3.Row | None]:
        a = c.execute("SELECT * FROM approvals WHERE approval_id=?", (approval_id,)).fetchone()
        if a is None: return False, "missing_approval", None
        if a["actor"] != actor: return False, "actor_mismatch", a
        if a["action_hash"] != action_digest(action): return False, "action_mismatch", a
        if a["scope"] != scope: return False, "scope_mismatch", a
        if now < a["issued_at"]: return False, "not_yet_valid", a
        if now >= a["expires_at"]: return False, "expired", a
        if a["authority_epoch"] != PersistentActionGuard._authority_epoch(c, actor):
            return False, "revoked", a
        return True, "allowed", a

    def issue_approval(self, approval_id: str, actor: str, approver_id: str,
                       action: dict[str, Any], scope: str, issued_at: int,
                       expires_at: int) -> Decision:
        """Record approval by a distinct approver identity for an executor principal."""
        if not approval_id or not actor or not approver_id or not scope or expires_at <= issued_at:
            return Decision(False, "invalid_approval")
        # Ensure action is canonical JSON before writing durable authorization.
        try: digest = action_digest(action)
        except (TypeError, ValueError): return Decision(False, "invalid_action")
        with self._connect() as c:
            c.execute("BEGIN IMMEDIATE")
            epoch = self._authority_epoch(c, actor)
            try:
                c.execute("INSERT INTO approvals VALUES(?,?,?,?,?,?,?,?)",
                          (approval_id, actor, approver_id, digest, scope, issued_at, expires_at, epoch))
            except sqlite3.IntegrityError:
                c.execute("ROLLBACK")
                return Decision(False, "approval_id_exists")
            self._audit(c, issued_at, actor, approval_id, None, "APPROVAL_ISSUED", "allowed",
                        {"approver_id": approver_id, "action_hash": digest, "scope": scope, "epoch": epoch, "expires_at": expires_at})
            c.execute("COMMIT")
        return Decision(True, "approval_issued")

    def revoke_all(self, actor: str, now: int) -> int:
        with self._connect() as c:
            c.execute("BEGIN IMMEDIATE")
            c.execute("INSERT OR IGNORE INTO authority(actor,epoch) VALUES(?,0)", (actor,))
            c.execute("UPDATE authority SET epoch=epoch+1 WHERE actor=?", (actor,))
            epoch = self._authority_epoch(c, actor)
            self._audit(c, now, actor, None, None, "AUTHORITY_REVOKED", "epoch_incremented", {"epoch": epoch})
            c.execute("COMMIT")
        return epoch

    def prepare_effect(self, effect_id: str, approval_id: str, actor: str,
                       action: dict[str, Any], scope: str, now: int) -> Decision:
        if not effect_id:
            return Decision(False, "invalid_effect_id")
        try: action_json = canonical_action(action); digest = action_digest(action)
        except (TypeError, ValueError): return Decision(False, "invalid_action")
        with self._connect() as c:
            c.execute("BEGIN IMMEDIATE")
            valid, reason, a = self._validate(c, approval_id, actor, action, scope, now)
            if not valid:
                self._audit(c, now, actor, approval_id, effect_id, "PREPARE_DENIED", reason)
                c.execute("COMMIT")
                return Decision(False, reason)
            try:
                c.execute("INSERT INTO effects(effect_id,approval_id,actor,action_json,action_hash,scope,status,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?)",
                          (effect_id, approval_id, actor, action_json, digest, scope, "PREPARED", now, now))
            except sqlite3.IntegrityError:
                c.execute("ROLLBACK")
                # Distinguish reused approval from duplicate effect identifier.
                with self._connect() as check:
                    row = check.execute("SELECT effect_id FROM effects WHERE approval_id=?", (approval_id,)).fetchone()
                    return Decision(False, "approval_already_consumed" if row else "effect_id_exists")
            self._audit(c, now, actor, approval_id, effect_id, "EFFECT_PREPARED", "allowed", {"action_hash": digest})
            c.execute("COMMIT")
        return Decision(True, "prepared", effect_id, "PREPARED", action)

    def claim_dispatch(self, effect_id: str, now: int,
                       current_action: dict[str, Any]) -> Decision:
        """Re-check authority and trusted live state immediately before dispatch claim.

        current_action must come from the provider adapter, not from the model/user.
        The provider must still enforce a conditional write (e.g. expected head SHA).
        """
        with self._connect() as c:
            c.execute("BEGIN IMMEDIATE")
            e = c.execute("SELECT * FROM effects WHERE effect_id=?", (effect_id,)).fetchone()
            if e is None:
                c.execute("COMMIT")
                return Decision(False, "missing_effect", effect_id)
            if e["status"] != "PREPARED":
                self._audit(c, now, e["actor"], e["approval_id"], effect_id,
                            "DISPATCH_CLAIM_DENIED", "effect_not_prepared", {"status": e["status"]})
                c.execute("COMMIT")
                return Decision(False, "effect_not_prepared", effect_id, e["status"])
            intended = json.loads(e["action_json"])
            if action_digest(current_action) != e["action_hash"]:
                c.execute("UPDATE effects SET status='CANCELLED',updated_at=?,reason=? WHERE effect_id=?",
                          (now, "live_state_mismatch", effect_id))
                self._audit(c, now, e["actor"], e["approval_id"], effect_id,
                            "EFFECT_CANCELLED", "live_state_mismatch",
                            {"approved_hash": e["action_hash"], "observed_hash": action_digest(current_action)})
                c.execute("COMMIT")
                return Decision(False, "live_state_mismatch", effect_id, "CANCELLED")
            valid, reason, _ = self._validate(c, e["approval_id"], e["actor"], intended, e["scope"], now)
            if not valid:
                c.execute("UPDATE effects SET status='CANCELLED',updated_at=?,reason=? WHERE effect_id=?",
                          (now, reason, effect_id))
                self._audit(c, now, e["actor"], e["approval_id"], effect_id,
                            "EFFECT_CANCELLED", reason)
                c.execute("COMMIT")
                return Decision(False, reason, effect_id, "CANCELLED")
            c.execute("UPDATE effects SET status='DISPATCHING',updated_at=? WHERE effect_id=? AND status='PREPARED'",
                      (now, effect_id))
            self._audit(c, now, e["actor"], e["approval_id"], effect_id,
                        "DISPATCH_CLAIMED", "authorized", {"action_hash": e["action_hash"]})
            c.execute("COMMIT")
        return Decision(True, "dispatch_claimed", effect_id, "DISPATCHING", intended)

    def record_result(self, effect_id: str, now: int, outcome: Outcome,
                      details: dict[str, Any] | None = None) -> Decision:
        mapping = {"success": "SUCCEEDED", "failure": "FAILED", "unknown": "UNKNOWN"}
        if outcome not in mapping:
            return Decision(False, "invalid_outcome", effect_id)
        status = mapping[outcome]
        payload = json.dumps(details or {}, sort_keys=True, separators=(",", ":"))
        with self._connect() as c:
            c.execute("BEGIN IMMEDIATE")
            e = c.execute("SELECT * FROM effects WHERE effect_id=?", (effect_id,)).fetchone()
            if e is None:
                c.execute("COMMIT")
                return Decision(False, "missing_effect", effect_id)
            if e["status"] != "DISPATCHING":
                c.execute("COMMIT")
                return Decision(False, "effect_not_dispatching", effect_id, e["status"])
            c.execute("UPDATE effects SET status=?,updated_at=?,result_json=?,reason=? WHERE effect_id=?",
                      (status, now, payload, outcome, effect_id))
            self._audit(c, now, e["actor"], e["approval_id"], effect_id,
                        "PROVIDER_RESULT", outcome, details)
            c.execute("COMMIT")
        return Decision(True, "result_recorded", effect_id, status)

    def reconcile_effect(self, effect_id: str, now: int, outcome: Literal["success", "failure"],
                         evidence: dict[str, Any]) -> Decision:
        """Resolve UNKNOWN/DISPATCHING only after an external authoritative read.

        This method records a caller-supplied reconciliation result; it cannot verify
        the evidence itself. Production callers must authenticate provider responses,
        retain request/merge identifiers, and fail closed if state is ambiguous.
        """
        if outcome not in ("success", "failure"):
            return Decision(False, "reconciliation_requires_definitive_outcome", effect_id)
        if not isinstance(evidence, dict) or not evidence:
            return Decision(False, "reconciliation_evidence_required", effect_id)
        status = "SUCCEEDED" if outcome == "success" else "FAILED"
        payload = json.dumps(evidence, sort_keys=True, separators=(",", ":"))
        with self._connect() as c:
            c.execute("BEGIN IMMEDIATE")
            e = c.execute("SELECT * FROM effects WHERE effect_id=?", (effect_id,)).fetchone()
            if e is None:
                c.execute("COMMIT")
                return Decision(False, "missing_effect", effect_id)
            if e["status"] not in ("DISPATCHING", "UNKNOWN"):
                c.execute("COMMIT")
                return Decision(False, "effect_not_reconcilable", effect_id, e["status"])
            c.execute("UPDATE effects SET status=?,updated_at=?,result_json=?,reason=? WHERE effect_id=?",
                      (status, now, payload, "reconciled_" + outcome, effect_id))
            self._audit(c, now, e["actor"], e["approval_id"], effect_id,
                        "PROVIDER_RECONCILED", outcome, evidence)
            c.execute("COMMIT")
        return Decision(True, "reconciled", effect_id, status)

    def get_effect(self, effect_id: str) -> dict[str, Any] | None:
        with self._connect() as c:
            row = c.execute("SELECT * FROM effects WHERE effect_id=?", (effect_id,)).fetchone()
            if row is None: return None
            result = dict(row)
            result["action"] = json.loads(result.pop("action_json"))
            result["result"] = json.loads(result.pop("result_json")) if result.get("result_json") else None
            return result

    def audit_events(self, effect_id: str | None = None) -> list[dict[str, Any]]:
        with self._connect() as c:
            if effect_id is None:
                rows = c.execute("SELECT * FROM audit ORDER BY seq").fetchall()
            else:
                rows = c.execute("SELECT * FROM audit WHERE effect_id=? ORDER BY seq", (effect_id,)).fetchall()
            out = []
            for row in rows:
                d = dict(row); d["details"] = json.loads(d.pop("details_json")); out.append(d)
            return out


class FakeMergeProvider:
    """Test-only conditional, idempotent provider. Never calls GitHub."""
    def __init__(self):
        self.current_pr: dict[tuple[str, int], dict[str, Any]] = {}
        self.outcomes: dict[str, dict[str, Any]] = {}
        self.calls = 0

    def seed_pr(self, repo: str, number: int, head_sha: str, base_sha: str, *, open: bool = True) -> None:
        self.current_pr[(repo, number)] = {"head_sha": head_sha, "base_sha": base_sha, "open": open, "merged": False}

    @staticmethod
    def state_action(repo: str, number: int, state: dict[str, Any]) -> dict[str, Any]:
        return {"tool": "github.merge", "repo": repo, "pull_request": number,
                "head_sha": state["head_sha"], "base_sha": state["base_sha"],
                "merge_method": "squash"}

    def read_action(self, repo: str, number: int) -> dict[str, Any]:
        state = self.current_pr[(repo, number)]
        return self.state_action(repo, number, state)

    def merge(self, action: dict[str, Any], idempotency_key: str) -> dict[str, Any]:
        # Same key returns the same durable mock-provider result and creates no second effect.
        if idempotency_key in self.outcomes:
            return dict(self.outcomes[idempotency_key])
        self.calls += 1
        key = (action["repo"], int(action["pull_request"]))
        pr = self.current_pr.get(key)
        if pr is None or not pr["open"] or pr["merged"]:
            result = {"status": "failure", "reason": "pr_not_mergeable"}
        elif pr["head_sha"] != action["head_sha"] or pr["base_sha"] != action["base_sha"]:
            result = {"status": "failure", "reason": "stale_sha"}
        else:
            pr["merged"] = True
            result = {"status": "success", "merge_commit": "mock-merge-" + action["head_sha"]}
        self.outcomes[idempotency_key] = result
        return dict(result)
