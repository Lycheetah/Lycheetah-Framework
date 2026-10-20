"""Lycheetah Action Guard — durable single-use action authorization ledger.

SQLite-backed durable state providing single-use approvals, fail-closed dispatch claims,
authority epochs, and hash-chained audit trails.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any, Literal

Outcome = Literal["success", "failure", "unknown"]
AUDIT_GENESIS = sha256(b"lycheetah-action-guard-audit-chain-v1").hexdigest()


def canonical_action(action: dict[str, Any]) -> str:
    """Serialize an action dictionary to deterministic, canonical JSON."""
    return json.dumps(
        action, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    )


def action_digest(action: dict[str, Any]) -> str:
    """Return the SHA-256 hex digest of a canonical action dictionary."""
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
    """SQLite ledger with single-use approvals, authority epochs, and fail-closed dispatch claims.

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
                    details_json TEXT NOT NULL,
                    prev_hash TEXT,
                    event_hash TEXT
                );
                CREATE INDEX IF NOT EXISTS effects_status_idx ON effects(status);
                CREATE INDEX IF NOT EXISTS audit_effect_idx ON audit(effect_id, seq);
            """)
            audit_columns = {
                row["name"] for row in c.execute("PRAGMA table_info(audit)").fetchall()
            }
            legacy_audit = "prev_hash" not in audit_columns or "event_hash" not in audit_columns
            if "prev_hash" not in audit_columns:
                c.execute("ALTER TABLE audit ADD COLUMN prev_hash TEXT")
            if "event_hash" not in audit_columns:
                c.execute("ALTER TABLE audit ADD COLUMN event_hash TEXT")
            if legacy_audit:
                self._rebuild_legacy_audit_chain(c)

    def _connect(self) -> sqlite3.Connection:
        c = sqlite3.connect(
            self.db_path, timeout=15, isolation_level=None, factory=_ClosingConnection
        )
        c.row_factory = sqlite3.Row
        c.execute("PRAGMA foreign_keys=ON")
        c.execute("PRAGMA busy_timeout=15000")
        return c

    @staticmethod
    def _audit_hash(
        seq: int,
        at: int,
        actor: str,
        approval_id: str | None,
        effect_id: str | None,
        event: str,
        reason: str,
        details_json: str,
        prev_hash: str,
    ) -> str:
        payload = {
            "seq": seq,
            "at": at,
            "actor": actor,
            "approval_id": approval_id,
            "effect_id": effect_id,
            "event": event,
            "reason": reason,
            "details_json": details_json,
            "prev_hash": prev_hash,
            "format": "lycheetah-action-guard-audit-event-v1",
        }
        wire = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return sha256(wire.encode("utf-8")).hexdigest()

    @classmethod
    def _rebuild_legacy_audit_chain(cls, c: sqlite3.Connection) -> None:
        prev = AUDIT_GENESIS
        rows = c.execute("SELECT * FROM audit ORDER BY seq").fetchall()
        for row in rows:
            h = cls._audit_hash(
                row["seq"],
                row["at"],
                row["actor"],
                row["approval_id"],
                row["effect_id"],
                row["event"],
                row["reason"],
                row["details_json"],
                prev,
            )
            c.execute(
                "UPDATE audit SET prev_hash=?,event_hash=? WHERE seq=?", (prev, h, row["seq"])
            )
            prev = h

    @classmethod
    def _audit(
        cls,
        c: sqlite3.Connection,
        at: int,
        actor: str,
        approval_id: str | None,
        effect_id: str | None,
        event: str,
        reason: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        details_json = json.dumps(
            details or {}, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        )
        previous = c.execute("SELECT event_hash FROM audit ORDER BY seq DESC LIMIT 1").fetchone()
        prev_hash = previous["event_hash"] if previous and previous["event_hash"] else AUDIT_GENESIS
        cur = c.execute(
            "INSERT INTO audit("
            "at,actor,approval_id,effect_id,event,reason,details_json,prev_hash,event_hash) "
            "VALUES(?,?,?,?,?,?,?,?,?)",
            (at, actor, approval_id, effect_id, event, reason, details_json, prev_hash, ""),
        )
        if cur.lastrowid is None:
            raise RuntimeError("audit INSERT did not return a row id")
        seq = cur.lastrowid
        event_hash = cls._audit_hash(
            seq, at, actor, approval_id, effect_id, event, reason, details_json, prev_hash
        )
        c.execute("UPDATE audit SET event_hash=? WHERE seq=?", (event_hash, seq))

    @classmethod
    def _verify_audit_chain(
        cls, c: sqlite3.Connection, expected_anchor: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        rows = c.execute("SELECT * FROM audit ORDER BY seq").fetchall()
        prev_hash = AUDIT_GENESIS
        previous_seq = None
        first_bad_seq = None
        reason = "ok"
        for row in rows:
            seq = int(row["seq"])
            if previous_seq is None and seq != 1:
                first_bad_seq, reason = seq, "sequence_gap_from_genesis"
                break
            if previous_seq is not None and seq != previous_seq + 1:
                first_bad_seq, reason = seq, "sequence_gap"
                break
            if row["prev_hash"] != prev_hash:
                first_bad_seq, reason = seq, "previous_hash_mismatch"
                break
            expected = cls._audit_hash(
                seq,
                row["at"],
                row["actor"],
                row["approval_id"],
                row["effect_id"],
                row["event"],
                row["reason"],
                row["details_json"],
                row["prev_hash"],
            )
            if row["event_hash"] != expected:
                first_bad_seq, reason = seq, "event_hash_mismatch"
                break
            prev_hash = row["event_hash"]
            previous_seq = seq
        root_hash = prev_hash
        count = len(rows)
        last_seq = int(rows[-1]["seq"]) if rows else None
        valid = first_bad_seq is None
        if valid and expected_anchor is not None:
            anchor_seq = expected_anchor.get("last_seq")
            prefix = [
                r for r in rows if anchor_seq is not None and int(r["seq"]) <= int(anchor_seq)
            ]
            prefix_count = len(prefix)
            prefix_last_seq = int(prefix[-1]["seq"]) if prefix else None
            prefix_root = prefix[-1]["event_hash"] if prefix else AUDIT_GENESIS
            if (
                expected_anchor.get("event_count") != prefix_count
                or expected_anchor.get("last_seq") != prefix_last_seq
                or expected_anchor.get("root_hash") != prefix_root
            ) and not (
                expected_anchor.get("event_count") == 0
                and expected_anchor.get("last_seq") is None
                and expected_anchor.get("root_hash") == AUDIT_GENESIS
                and prefix_count == 0
            ):
                valid, reason = False, "external_anchor_mismatch"
        return {
            "valid": valid,
            "reason": reason,
            "event_count": count,
            "first_bad_seq": first_bad_seq,
            "last_seq": last_seq,
            "root_hash": root_hash,
        }

    def verify_audit_chain(self, expected_anchor: dict[str, Any] | None = None) -> dict[str, Any]:
        """Verify internal event integrity; optionally compare with a separately stored anchor."""
        with self._connect() as c:
            return self._verify_audit_chain(c, expected_anchor)

    def audit_anchor(self) -> dict[str, Any]:
        """Return a checkpoint only when the current internal chain is consistent."""
        status = self.verify_audit_chain()
        if not status["valid"]:
            raise RuntimeError(
                "audit_chain_invalid: refusing to mint a checkpoint from suspect history"
            )
        return {
            "event_count": status["event_count"],
            "last_seq": status["last_seq"],
            "root_hash": status["root_hash"],
        }

    @classmethod
    def _verify_state_consistency(cls, c: sqlite3.Connection) -> dict[str, Any]:
        """Cross-check mutable materialized tables against the checkpointed event journal."""
        try:
            events = c.execute("SELECT * FROM audit ORDER BY seq").fetchall()
            approval_events: dict[str, dict[str, Any]] = {}
            revocation_epochs: dict[str, int] = {}
            expected_effects: dict[str, dict[str, Any]] = {}

            for row in events:
                event = row["event"]
                actor = row["actor"]
                approval_id = row["approval_id"]
                effect_id = row["effect_id"]
                details = json.loads(row["details_json"])
                if event == "APPROVAL_ISSUED":
                    if not approval_id or approval_id in approval_events:
                        return {
                            "valid": False,
                            "reason": "approval_event_duplicate_or_missing_id",
                            "reference": approval_id,
                        }
                    try:
                        approval_epoch = int(details["epoch"])
                        if approval_epoch != revocation_epochs.get(actor, 0):
                            return {
                                "valid": False,
                                "reason": "approval_epoch_does_not_match_prior_revocations",
                                "reference": approval_id,
                            }
                        approval_events[approval_id] = {
                            "actor": actor,
                            "approver_id": details["approver_id"],
                            "action_hash": details["action_hash"],
                            "scope": details["scope"],
                            "issued_at": int(row["at"]),
                            "expires_at": int(details["expires_at"]),
                            "authority_epoch": approval_epoch,
                        }
                    except (KeyError, TypeError, ValueError):
                        return {
                            "valid": False,
                            "reason": "approval_event_malformed",
                            "reference": approval_id,
                        }
                elif event == "AUTHORITY_REVOKED":
                    try:
                        epoch = int(details["epoch"])
                    except (KeyError, TypeError, ValueError):
                        return {
                            "valid": False,
                            "reason": "revocation_event_malformed",
                            "reference": actor,
                        }
                    expected_epoch = revocation_epochs.get(actor, 0) + 1
                    if epoch != expected_epoch:
                        return {
                            "valid": False,
                            "reason": "revocation_epoch_sequence_mismatch",
                            "reference": actor,
                        }
                    revocation_epochs[actor] = epoch
                elif event == "EFFECT_PREPARED":
                    if not effect_id or effect_id in expected_effects:
                        return {
                            "valid": False,
                            "reason": "effect_prepare_event_duplicate_or_missing_id",
                            "reference": effect_id,
                        }
                    approval = approval_events.get(approval_id or "")
                    if approval is None:
                        return {
                            "valid": False,
                            "reason": "effect_references_missing_approval",
                            "reference": effect_id,
                        }
                    action_hash = details.get("action_hash")
                    expected_effects[effect_id] = {
                        "approval_id": approval_id,
                        "actor": actor,
                        "action_hash": action_hash,
                        "scope": approval["scope"],
                        "created_at": int(row["at"]),
                        "updated_at": int(row["at"]),
                        "status": "PREPARED",
                        "reason": None,
                        "result_json": None,
                    }
                elif event == "DISPATCH_CLAIMED":
                    eff = expected_effects.get(effect_id or "")
                    if eff is None or eff["status"] != "PREPARED":
                        return {
                            "valid": False,
                            "reason": "illegal_dispatch_claim_transition",
                            "reference": effect_id,
                        }
                    eff["status"], eff["updated_at"] = "DISPATCHING", int(row["at"])
                elif event == "EFFECT_CANCELLED":
                    eff = expected_effects.get(effect_id or "")
                    if eff is None or eff["status"] != "PREPARED":
                        return {
                            "valid": False,
                            "reason": "illegal_effect_cancel_transition",
                            "reference": effect_id,
                        }
                    eff["status"], eff["updated_at"], eff["reason"] = (
                        "CANCELLED",
                        int(row["at"]),
                        row["reason"],
                    )
                elif event == "PROVIDER_RESULT":
                    eff = expected_effects.get(effect_id or "")
                    outcome = row["reason"]
                    status = {
                        "success": "SUCCEEDED",
                        "failure": "FAILED",
                        "unknown": "UNKNOWN",
                    }.get(outcome)
                    if eff is None or eff["status"] != "DISPATCHING" or status is None:
                        return {
                            "valid": False,
                            "reason": "illegal_provider_result_transition",
                            "reference": effect_id,
                        }
                    eff["status"], eff["updated_at"], eff["reason"] = (
                        status,
                        int(row["at"]),
                        outcome,
                    )
                    eff["result_json"] = row["details_json"]
                elif event == "PROVIDER_RECONCILED":
                    eff = expected_effects.get(effect_id or "")
                    outcome = row["reason"]
                    status = {"success": "SUCCEEDED", "failure": "FAILED"}.get(outcome)
                    if (
                        eff is None
                        or eff["status"] not in ("DISPATCHING", "UNKNOWN")
                        or status is None
                    ):
                        return {
                            "valid": False,
                            "reason": "illegal_reconciliation_transition",
                            "reference": effect_id,
                        }
                    eff["status"], eff["updated_at"] = status, int(row["at"])
                    eff["reason"], eff["result_json"] = "reconciled_" + outcome, row["details_json"]

            approval_rows = {
                row["approval_id"]: dict(row)
                for row in c.execute("SELECT * FROM approvals").fetchall()
            }
            if set(approval_rows) != set(approval_events):
                return {"valid": False, "reason": "approval_table_event_set_mismatch"}
            for aid, expected in approval_events.items():
                actual = approval_rows[aid]
                if any(actual[field] != value for field, value in expected.items()):
                    return {
                        "valid": False,
                        "reason": "approval_table_event_mismatch",
                        "reference": aid,
                    }

            authority_rows = {
                row["actor"]: int(row["epoch"])
                for row in c.execute("SELECT actor,epoch FROM authority").fetchall()
            }
            for actor in set(authority_rows) | set(revocation_epochs):
                actual_epoch = authority_rows.get(actor, 0)
                expected_epoch = revocation_epochs.get(actor, 0)
                if actual_epoch != expected_epoch:
                    return {
                        "valid": False,
                        "reason": "authority_table_event_mismatch",
                        "reference": actor,
                    }

            effect_rows = {
                row["effect_id"]: dict(row) for row in c.execute("SELECT * FROM effects").fetchall()
            }
            if set(effect_rows) != set(expected_effects):
                return {"valid": False, "reason": "effect_table_event_set_mismatch"}
            for eid, expected in expected_effects.items():
                actual = effect_rows[eid]
                try:
                    action = json.loads(actual["action_json"])
                    action_wire = canonical_action(action)
                    digest = action_digest(action)
                except (TypeError, ValueError, json.JSONDecodeError):
                    return {"valid": False, "reason": "effect_action_malformed", "reference": eid}
                if (
                    action_wire != actual["action_json"]
                    or digest != actual["action_hash"]
                    or digest != expected["action_hash"]
                    or actual["actor"] != expected["actor"]
                    or actual["approval_id"] != expected["approval_id"]
                    or actual["scope"] != expected["scope"]
                    or actual["created_at"] != expected["created_at"]
                    or actual["updated_at"] != expected["updated_at"]
                    or actual["status"] != expected["status"]
                    or actual["reason"] != expected["reason"]
                ):
                    return {
                        "valid": False,
                        "reason": "effect_table_event_mismatch",
                        "reference": eid,
                    }
                try:
                    actual_result = (
                        json.loads(actual["result_json"])
                        if actual["result_json"] is not None
                        else None
                    )
                    expected_result = (
                        json.loads(expected["result_json"])
                        if expected["result_json"] is not None
                        else None
                    )
                except (TypeError, json.JSONDecodeError):
                    return {
                        "valid": False,
                        "reason": "effect_result_json_malformed",
                        "reference": eid,
                    }
                if actual_result != expected_result:
                    return {
                        "valid": False,
                        "reason": "effect_result_event_mismatch",
                        "reference": eid,
                    }
                approval = approval_events.get(actual["approval_id"])
                if approval is None or approval["action_hash"] != digest:
                    return {
                        "valid": False,
                        "reason": "effect_approval_binding_mismatch",
                        "reference": eid,
                    }
            return {
                "valid": True,
                "reason": "ok",
                "approval_count": len(approval_rows),
                "effect_count": len(effect_rows),
                "actor_count": len(set(authority_rows) | set(revocation_epochs)),
            }
        except Exception as exc:
            return {
                "valid": False,
                "reason": "state_consistency_check_error",
                "error_type": type(exc).__name__,
            }

    def verify_state_consistency(self) -> dict[str, Any]:
        """Check operational tables against the audit journal without mutating state."""
        with self._connect() as c:
            return self._verify_state_consistency(c)

    @staticmethod
    def _authority_epoch(c: sqlite3.Connection, actor: str) -> int:
        row = c.execute("SELECT epoch FROM authority WHERE actor=?", (actor,)).fetchone()
        return int(row["epoch"]) if row else 0

    @staticmethod
    def _validate(
        c: sqlite3.Connection,
        approval_id: str,
        actor: str,
        action: dict[str, Any],
        scope: str,
        now: int,
    ) -> tuple[bool, str, sqlite3.Row | None]:
        a = c.execute("SELECT * FROM approvals WHERE approval_id=?", (approval_id,)).fetchone()
        if a is None:
            return False, "missing_approval", None
        if a["actor"] != actor:
            return False, "actor_mismatch", a
        if a["action_hash"] != action_digest(action):
            return False, "action_mismatch", a
        if a["scope"] != scope:
            return False, "scope_mismatch", a
        if now < a["issued_at"]:
            return False, "not_yet_valid", a
        if now >= a["expires_at"]:
            return False, "expired", a
        if a["authority_epoch"] != PersistentActionGuard._authority_epoch(c, actor):
            return False, "revoked", a
        return True, "allowed", a

    def issue_approval(
        self,
        approval_id: str,
        actor: str,
        approver_id: str,
        action: dict[str, Any],
        scope: str,
        issued_at: int,
        expires_at: int,
    ) -> Decision:
        """Record approval by a distinct approver identity for an executor principal."""
        if not approval_id or not actor or not approver_id or not scope or expires_at <= issued_at:
            return Decision(False, "invalid_approval")
        try:
            digest = action_digest(action)
        except (TypeError, ValueError):
            return Decision(False, "invalid_action")
        with self._connect() as c:
            c.execute("BEGIN IMMEDIATE")
            epoch = self._authority_epoch(c, actor)
            try:
                c.execute(
                    "INSERT INTO approvals VALUES(?,?,?,?,?,?,?,?)",
                    (
                        approval_id,
                        actor,
                        approver_id,
                        digest,
                        scope,
                        issued_at,
                        expires_at,
                        epoch,
                    ),
                )
            except sqlite3.IntegrityError:
                c.execute("ROLLBACK")
                return Decision(False, "approval_id_exists")
            self._audit(
                c,
                issued_at,
                actor,
                approval_id,
                None,
                "APPROVAL_ISSUED",
                "allowed",
                {
                    "approver_id": approver_id,
                    "action_hash": digest,
                    "scope": scope,
                    "epoch": epoch,
                    "expires_at": expires_at,
                },
            )
            c.execute("COMMIT")
        return Decision(True, "approval_issued")

    def revoke_all(self, actor: str, now: int) -> int:
        """Revoke all pending approvals for an actor by bumping authority epoch."""
        with self._connect() as c:
            c.execute("BEGIN IMMEDIATE")
            c.execute("INSERT OR IGNORE INTO authority(actor,epoch) VALUES(?,0)", (actor,))
            c.execute("UPDATE authority SET epoch=epoch+1 WHERE actor=?", (actor,))
            epoch = self._authority_epoch(c, actor)
            self._audit(
                c,
                now,
                actor,
                None,
                None,
                "AUTHORITY_REVOKED",
                "epoch_incremented",
                {"epoch": epoch},
            )
            c.execute("COMMIT")
        return epoch

    def prepare_effect(
        self,
        effect_id: str,
        approval_id: str,
        actor: str,
        action: dict[str, Any],
        scope: str,
        now: int,
    ) -> Decision:
        """Prepare an authorized effect bound to a single-use approval."""
        if not effect_id:
            return Decision(False, "invalid_effect_id")
        try:
            action_json = canonical_action(action)
            digest = action_digest(action)
        except (TypeError, ValueError):
            return Decision(False, "invalid_action")
        with self._connect() as c:
            c.execute("BEGIN IMMEDIATE")
            valid, reason, _ = self._validate(c, approval_id, actor, action, scope, now)
            if not valid:
                self._audit(c, now, actor, approval_id, effect_id, "PREPARE_DENIED", reason)
                c.execute("COMMIT")
                return Decision(False, reason)
            try:
                c.execute(
                    "INSERT INTO effects("
                    "effect_id,approval_id,actor,action_json,action_hash,scope,"
                    "status,created_at,updated_at) "
                    "VALUES(?,?,?,?,?,?,?,?,?)",
                    (
                        effect_id,
                        approval_id,
                        actor,
                        action_json,
                        digest,
                        scope,
                        "PREPARED",
                        now,
                        now,
                    ),
                )
            except sqlite3.IntegrityError:
                c.execute("ROLLBACK")
                with self._connect() as check:
                    row = check.execute(
                        "SELECT effect_id FROM effects WHERE approval_id=?", (approval_id,)
                    ).fetchone()
                    return Decision(
                        False, "approval_already_consumed" if row else "effect_id_exists"
                    )
            self._audit(
                c,
                now,
                actor,
                approval_id,
                effect_id,
                "EFFECT_PREPARED",
                "allowed",
                {"action_hash": digest},
            )
            c.execute("COMMIT")
        return Decision(True, "prepared", effect_id, "PREPARED", action)

    def claim_dispatch(
        self,
        effect_id: str,
        now: int,
        current_action: dict[str, Any],
        expected_audit_anchor: dict[str, Any] | None = None,
        require_exact_audit_anchor: bool = False,
    ) -> Decision:
        """Linearization point: claim dispatch right before executing an effect."""
        if expected_audit_anchor is None:
            return Decision(False, "trusted_audit_anchor_required", effect_id)
        with self._connect() as c:
            c.execute("BEGIN IMMEDIATE")
            integrity = self._verify_audit_chain(c, expected_audit_anchor)
            if not integrity["valid"]:
                c.execute("ROLLBACK")
                return Decision(False, "audit_chain_invalid", effect_id)
            if require_exact_audit_anchor and expected_audit_anchor is not None:
                current_anchor = {
                    "event_count": integrity["event_count"],
                    "last_seq": integrity["last_seq"],
                    "root_hash": integrity["root_hash"],
                }
                if current_anchor != expected_audit_anchor:
                    c.execute("ROLLBACK")
                    return Decision(False, "audit_checkpoint_stale", effect_id)
            consistency = self._verify_state_consistency(c)
            if not consistency["valid"]:
                c.execute("ROLLBACK")
                return Decision(False, "ledger_state_inconsistent", effect_id)
            e = c.execute("SELECT * FROM effects WHERE effect_id=?", (effect_id,)).fetchone()
            if e is None:
                c.execute("COMMIT")
                return Decision(False, "missing_effect", effect_id)
            if e["status"] != "PREPARED":
                self._audit(
                    c,
                    now,
                    e["actor"],
                    e["approval_id"],
                    effect_id,
                    "DISPATCH_CLAIM_DENIED",
                    "effect_not_prepared",
                    {"status": e["status"]},
                )
                c.execute("COMMIT")
                return Decision(False, "effect_not_prepared", effect_id, e["status"])
            intended = json.loads(e["action_json"])
            if action_digest(current_action) != e["action_hash"]:
                c.execute(
                    "UPDATE effects SET status='CANCELLED',updated_at=?,reason=? WHERE effect_id=?",
                    (now, "live_state_mismatch", effect_id),
                )
                self._audit(
                    c,
                    now,
                    e["actor"],
                    e["approval_id"],
                    effect_id,
                    "EFFECT_CANCELLED",
                    "live_state_mismatch",
                    {
                        "approved_hash": e["action_hash"],
                        "observed_hash": action_digest(current_action),
                    },
                )
                c.execute("COMMIT")
                return Decision(False, "live_state_mismatch", effect_id, "CANCELLED")
            valid, reason, _ = self._validate(
                c, e["approval_id"], e["actor"], intended, e["scope"], now
            )
            if not valid:
                c.execute(
                    "UPDATE effects SET status='CANCELLED',updated_at=?,reason=? WHERE effect_id=?",
                    (now, reason, effect_id),
                )
                self._audit(
                    c, now, e["actor"], e["approval_id"], effect_id, "EFFECT_CANCELLED", reason
                )
                c.execute("COMMIT")
                return Decision(False, reason, effect_id, "CANCELLED")
            c.execute(
                "UPDATE effects SET status='DISPATCHING',updated_at=? "
                "WHERE effect_id=? AND status='PREPARED'",
                (now, effect_id),
            )
            self._audit(
                c,
                now,
                e["actor"],
                e["approval_id"],
                effect_id,
                "DISPATCH_CLAIMED",
                "authorized",
                {"action_hash": e["action_hash"]},
            )
            c.execute("COMMIT")
        return Decision(True, "dispatch_claimed", effect_id, "DISPATCHING", intended)

    def record_result(
        self,
        effect_id: str,
        now: int,
        outcome: Outcome,
        details: dict[str, Any] | None = None,
    ) -> Decision:
        """Record the terminal or intermediate outcome of a dispatched effect."""
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
            c.execute(
                "UPDATE effects SET status=?,updated_at=?,result_json=?,reason=? WHERE effect_id=?",
                (status, now, payload, outcome, effect_id),
            )
            self._audit(
                c, now, e["actor"], e["approval_id"], effect_id, "PROVIDER_RESULT", outcome, details
            )
            c.execute("COMMIT")
        return Decision(True, "result_recorded", effect_id, status)

    def reconcile_effect(
        self,
        effect_id: str,
        now: int,
        outcome: Literal["success", "failure"],
        evidence: dict[str, Any],
    ) -> Decision:
        """Resolve UNKNOWN/DISPATCHING only after an external authoritative read."""
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
            c.execute(
                "UPDATE effects SET status=?,updated_at=?,result_json=?,reason=? WHERE effect_id=?",
                (status, now, payload, "reconciled_" + outcome, effect_id),
            )
            self._audit(
                c,
                now,
                e["actor"],
                e["approval_id"],
                effect_id,
                "PROVIDER_RECONCILED",
                outcome,
                evidence,
            )
            c.execute("COMMIT")
        return Decision(True, "reconciled", effect_id, status)

    def get_approval(self, approval_id: str) -> dict[str, Any] | None:
        """Read recorded approval metadata; this does not authenticate its issuer."""
        with self._connect() as c:
            row = c.execute(
                "SELECT * FROM approvals WHERE approval_id=?", (approval_id,)
            ).fetchone()
            return dict(row) if row is not None else None

    def get_effect(self, effect_id: str) -> dict[str, Any] | None:
        """Fetch effect record with deserialized action and result objects."""
        with self._connect() as c:
            row = c.execute("SELECT * FROM effects WHERE effect_id=?", (effect_id,)).fetchone()
            if row is None:
                return None
            result = dict(row)
            result["action"] = json.loads(result.pop("action_json"))
            result["result"] = (
                json.loads(result.pop("result_json")) if result.get("result_json") else None
            )
            return result

    def audit_events(self, effect_id: str | None = None) -> list[dict[str, Any]]:
        """Fetch raw audit events in order, optionally filtered by effect_id."""
        with self._connect() as c:
            if effect_id is None:
                rows = c.execute("SELECT * FROM audit ORDER BY seq").fetchall()
            else:
                rows = c.execute(
                    "SELECT * FROM audit WHERE effect_id=? ORDER BY seq", (effect_id,)
                ).fetchall()
            out = []
            for row in rows:
                d = dict(row)
                d["details"] = json.loads(d.pop("details_json"))
                out.append(d)
            return out

    def audit_chain_events_after(self, last_seq: int | None) -> list[dict[str, Any]]:
        """Return wire-format hash-chain events after a checkpoint sequence."""
        cutoff = 0 if last_seq is None else int(last_seq)
        fields = (
            "seq",
            "at",
            "actor",
            "approval_id",
            "effect_id",
            "event",
            "reason",
            "details_json",
            "prev_hash",
            "event_hash",
        )
        with self._connect() as c:
            rows = c.execute(
                "SELECT " + ",".join(fields) + " FROM audit WHERE seq>? ORDER BY seq",
                (cutoff,),
            ).fetchall()
            return [{field: row[field] for field in fields} for row in rows]
