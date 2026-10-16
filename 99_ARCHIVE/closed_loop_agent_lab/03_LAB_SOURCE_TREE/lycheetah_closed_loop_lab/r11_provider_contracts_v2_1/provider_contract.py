"""Provider-side atomicity and idempotency reference models (stdlib only).

These are test doubles for provider contract exploration, not live-provider adapters.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import time
from pathlib import Path
from typing import Any, Callable, Mapping


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


class ConditionDenied(RuntimeError):
    pass


class IdempotencyConflict(RuntimeError):
    pass


class InjectedCrash(RuntimeError):
    pass


class ResponseLost(RuntimeError):
    """Provider committed, but the caller did not receive the response."""


class AtomicConditionalProvider:
    """Correct reference contract: predicate, idempotency key, effect and result
    are serialized in one provider-owned SQLite write transaction.

    Important: this only models a provider whose condition is authoritative in
    this same transaction domain. It does not magically lock an unrelated service.
    """

    supports_durable_idempotency = True
    supports_atomic_condition = True
    supports_lookup = True

    def __init__(self, db_path: str | Path, *, clock: Callable[[], float] = time.time):
        self.db_path = str(db_path)
        self.clock = clock
        self.drop_next_response = False
        self.crash_before_commit = False
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(self.db_path, timeout=10, isolation_level=None)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA busy_timeout=10000")
        return con

    def _init_db(self) -> None:
        con = self._connect()
        try:
            con.execute("PRAGMA journal_mode=WAL")
            con.execute("CREATE TABLE IF NOT EXISTS condition_state (key TEXT PRIMARY KEY, version TEXT NOT NULL, status TEXT NOT NULL)")
            con.execute("CREATE TABLE IF NOT EXISTS provider_effects (operation_id TEXT PRIMARY KEY, request_sha256 TEXT NOT NULL, payload_json TEXT NOT NULL, result_json TEXT NOT NULL, applied_at REAL NOT NULL)")
        finally:
            con.close()

    def set_condition(self, key: str, version: str, status: str) -> None:
        con = self._connect()
        try:
            con.execute("BEGIN IMMEDIATE")
            con.execute("INSERT INTO condition_state VALUES(?,?,?) ON CONFLICT(key) DO UPDATE SET version=excluded.version,status=excluded.status", (key, version, status))
            con.commit()
        except Exception:
            if con.in_transaction:
                con.rollback()
            raise
        finally:
            con.close()

    def get_condition(self, key: str) -> dict[str, str] | None:
        con = self._connect()
        try:
            row = con.execute("SELECT * FROM condition_state WHERE key=?", (key,)).fetchone()
            return dict(row) if row else None
        finally:
            con.close()

    def lookup(self, operation_id: str, payload: Mapping[str, Any]) -> dict[str, Any] | None:
        request_sha = digest(payload)
        con = self._connect()
        try:
            row = con.execute("SELECT * FROM provider_effects WHERE operation_id=?", (operation_id,)).fetchone()
            if row is None:
                return None
            if row["request_sha256"] != request_sha:
                raise IdempotencyConflict("operation ID already bound to a different payload")
            return {**json.loads(row["result_json"]), "replayed": True}
        finally:
            con.close()

    def execute(self, operation_id: str, payload: Mapping[str, Any], *,
                condition_key: str, required_status: str, required_version: str | None = None) -> dict[str, Any]:
        request_sha = digest(payload)
        con = self._connect()
        committed_result: dict[str, Any] | None = None
        replayed = False
        try:
            con.execute("BEGIN IMMEDIATE")
            prior = con.execute("SELECT * FROM provider_effects WHERE operation_id=?", (operation_id,)).fetchone()
            if prior is not None:
                if prior["request_sha256"] != request_sha:
                    con.rollback()
                    raise IdempotencyConflict("operation ID already bound to a different payload")
                committed_result = json.loads(prior["result_json"])
                replayed = True
                con.commit()
            else:
                current = con.execute("SELECT version,status FROM condition_state WHERE key=?", (condition_key,)).fetchone()
                if current is None or current["status"] != required_status or (required_version is not None and current["version"] != required_version):
                    con.rollback()
                    raise ConditionDenied("provider-side conditional predicate is false")
                result = {"operation_id": operation_id, "request_sha256": request_sha,
                          "accepted": True, "condition_key": condition_key,
                          "condition_version": current["version"], "condition_status": current["status"]}
                con.execute("INSERT INTO provider_effects VALUES(?,?,?,?,?)",
                            (operation_id, request_sha, canonical_bytes(payload).decode(),
                             canonical_bytes(result).decode(), float(self.clock())))
                if self.crash_before_commit:
                    self.crash_before_commit = False
                    raise InjectedCrash("crash before provider transaction commit")
                con.commit()
                committed_result = result
        except Exception:
            if con.in_transaction:
                con.rollback()
            raise
        finally:
            con.close()
        assert committed_result is not None
        if self.drop_next_response:
            self.drop_next_response = False
            raise ResponseLost("effect and idempotency record committed; response lost")
        return {**committed_result, "replayed": replayed}

    def effect_count(self, operation_id: str | None = None) -> int:
        con = self._connect()
        try:
            if operation_id is None:
                return int(con.execute("SELECT COUNT(*) FROM provider_effects").fetchone()[0])
            return int(con.execute("SELECT COUNT(*) FROM provider_effects WHERE operation_id=?", (operation_id,)).fetchone()[0])
        finally:
            con.close()


class CheckThenActProvider:
    """Negative control: separately checks external condition and later acts.

    Even with idempotency, an evidence update can occur after the check and before
    effect commit. The callback deliberately exposes that interleaving.
    """
    supports_durable_idempotency = True
    supports_atomic_condition = False
    supports_lookup = True

    def __init__(self):
        self.condition = {"version": "1", "status": "PASS"}
        self.effects: dict[str, tuple[str, dict[str, Any]]] = {}
        self.after_check: Callable[[], None] | None = None

    def set_condition(self, version: str, status: str) -> None:
        self.condition = {"version": version, "status": status}

    def lookup(self, operation_id: str, payload: Mapping[str, Any]) -> dict[str, Any] | None:
        row = self.effects.get(operation_id)
        if row is None:
            return None
        if row[0] != digest(payload):
            raise IdempotencyConflict("operation ID already bound to a different payload")
        return {**row[1], "replayed": True}

    def execute(self, operation_id: str, payload: Mapping[str, Any], *, required_status: str = "PASS") -> dict[str, Any]:
        prior = self.lookup(operation_id, payload)
        if prior is not None:
            return prior
        observed = dict(self.condition)
        if observed["status"] != required_status:
            raise ConditionDenied("predicate false at precheck")
        if self.after_check:
            self.after_check()
        result = {"operation_id": operation_id, "request_sha256": digest(payload),
                  "accepted": True, "condition_version": observed["version"],
                  "condition_status": observed["status"]}
        self.effects[operation_id] = (digest(payload), result)
        return {**result, "replayed": False}

    def effect_count(self) -> int:
        return len(self.effects)


class NonIdempotentProvider:
    """Negative control: every execute call applies a new effect; no durable lookup."""
    supports_durable_idempotency = False
    supports_atomic_condition = False
    supports_lookup = False

    def __init__(self):
        self.effects: list[dict[str, Any]] = []
        self.drop_next_response = False

    def lookup(self, operation_id: str, payload: Mapping[str, Any]) -> None:
        return None

    def execute(self, operation_id: str, payload: Mapping[str, Any]) -> dict[str, Any]:
        result = {"operation_id": operation_id, "accepted": True, "ordinal": len(self.effects) + 1}
        self.effects.append({"operation_id": operation_id, "payload": dict(payload), "result": dict(result)})
        if self.drop_next_response:
            self.drop_next_response = False
            raise ResponseLost("effect may have committed but response was lost")
        return result

    def effect_count(self) -> int:
        return len(self.effects)
