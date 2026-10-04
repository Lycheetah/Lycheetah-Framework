#!/usr/bin/env python3
"""
Lycheetah Atomic Resource + Authority Finality Gate v0.9

Combines, in one durable serialization boundary:
  - authority generation,
  - resource reservation,
  - exact action/effect binding,
  - local finality acceptance,
  - durable outbox insertion.

The remote relay remains asynchronous. That is the established transactional
outbox pattern: local state + an outbox record commit atomically; an idempotent
relay/provider handles at-least-once delivery.

This is conventional transactional/fencing engineering composed around the
Lycheetah control vocabulary. Novelty is not claimed.

Resource pressure:
    P = spent + reserved + committed_pending <= budget

State meanings:
    RESERVED   : budget held, effect not final.
    COMMITTED  : local finality accepted; outbox exists; maximum exposure held.
    SETTLED    : provider receipt reconciled; actual spend charged.
    NO_EFFECT  : provider certifies no effect; committed exposure released.
    CANCELLED  : revocation won before local finality; reservation released.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import sqlite3
from typing import Optional

from pathlib import Path as _SupportPath
import sys as _support_sys
_support_sys.path.insert(0, str(_SupportPath(__file__).resolve().parents[1]))
from research_support import Action  # noqa: E402


@dataclass(frozen=True)
class AtomicDecision:
    state: str
    reason: str
    effect_id: str | None = None
    generation: int | None = None
    limit: int | None = None
    spent: int | None = None
    reserved: int | None = None
    committed_pending: int | None = None
    actual_cost: int | None = None
    audit_sequence: int | None = None


class AtomicFinalityGate:
    def __init__(self, db_path: str | Path):
        self.db_path = str(db_path)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def connect(self):
        con = sqlite3.connect(self.db_path, timeout=30, isolation_level=None)
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

            CREATE TABLE IF NOT EXISTS accounts(
                account_id TEXT PRIMARY KEY,
                budget_limit INTEGER NOT NULL CHECK(budget_limit >= 0),
                spent INTEGER NOT NULL DEFAULT 0 CHECK(spent >= 0),
                reserved INTEGER NOT NULL DEFAULT 0 CHECK(reserved >= 0),
                committed_pending INTEGER NOT NULL DEFAULT 0 CHECK(committed_pending >= 0)
            );

            CREATE TABLE IF NOT EXISTS attempts(
                effect_id TEXT PRIMARY KEY,
                principal TEXT NOT NULL,
                scope_key TEXT NOT NULL,
                account_id TEXT NOT NULL,
                generation INTEGER NOT NULL,
                action_hash TEXT NOT NULL,
                max_cost INTEGER NOT NULL CHECK(max_cost >= 0),
                actual_cost INTEGER,
                state TEXT NOT NULL,
                FOREIGN KEY(account_id) REFERENCES accounts(account_id)
            );

            CREATE TABLE IF NOT EXISTS outbox(
                effect_id TEXT PRIMARY KEY,
                action_hash TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                state TEXT NOT NULL,
                receipt TEXT,
                relay_attempts INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY(effect_id) REFERENCES attempts(effect_id)
            );

            CREATE TABLE IF NOT EXISTS audit(
                sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                kind TEXT NOT NULL,
                effect_id TEXT,
                principal TEXT,
                scope_key TEXT,
                account_id TEXT,
                generation INTEGER,
                amount INTEGER,
                detail TEXT NOT NULL
            );
            """)

    def _audit(self, con, kind, *, effect_id=None, principal=None,
               scope_key=None, account_id=None, generation=None,
               amount=None, detail=""):
        cur = con.execute(
            "INSERT INTO audit(kind,effect_id,principal,scope_key,account_id,"
            "generation,amount,detail) VALUES(?,?,?,?,?,?,?,?)",
            (kind, effect_id, principal, scope_key, account_id,
             generation, amount, detail),
        )
        return int(cur.lastrowid)

    def create_account(self, account_id: str, budget_limit: int):
        if budget_limit < 0:
            raise ValueError("budget_limit must be nonnegative")
        with self.connect() as con:
            con.execute("BEGIN IMMEDIATE")
            row = con.execute(
                "SELECT budget_limit FROM accounts WHERE account_id=?",
                (account_id,),
            ).fetchone()
            if row is None:
                con.execute(
                    "INSERT INTO accounts(account_id,budget_limit,spent,reserved,"
                    "committed_pending) VALUES(?,?,0,0,0)",
                    (account_id, budget_limit),
                )
                self._audit(
                    con, "ACCOUNT_CREATE", account_id=account_id,
                    amount=budget_limit, detail="budget account created"
                )
            elif int(row["budget_limit"]) != budget_limit:
                con.execute("ROLLBACK")
                raise ValueError("account exists with different budget")
            con.execute("COMMIT")

    def activate(self, principal: str, scope_key: str):
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
                " generation=excluded.generation,active=1",
                (principal, scope_key, generation),
            )
            seq = self._audit(
                con, "ACTIVATE", principal=principal, scope_key=scope_key,
                generation=generation, detail="authority active"
            )
            con.execute("COMMIT")
        return AtomicDecision(
            "ACTIVE", "authority-activated", generation=generation,
            audit_sequence=seq
        )

    def revoke(self, principal: str, scope_key: str):
        """Revocation and cancellation of not-yet-final attempts are atomic."""
        with self.connect() as con:
            con.execute("BEGIN IMMEDIATE")
            row = con.execute(
                "SELECT generation FROM authorities WHERE principal=? AND scope_key=?",
                (principal, scope_key),
            ).fetchone()
            generation = 1 if row is None else int(row["generation"]) + 1
            if row is None:
                con.execute(
                    "INSERT INTO authorities(principal,scope_key,generation,active)"
                    " VALUES(?,?,?,0)",
                    (principal, scope_key, generation),
                )
            else:
                con.execute(
                    "UPDATE authorities SET generation=?,active=0"
                    " WHERE principal=? AND scope_key=?",
                    (generation, principal, scope_key),
                )

            pending = con.execute(
                "SELECT effect_id,account_id,max_cost FROM attempts"
                " WHERE principal=? AND scope_key=? AND state='RESERVED'",
                (principal, scope_key),
            ).fetchall()
            released = 0
            for attempt in pending:
                max_cost = int(attempt["max_cost"])
                con.execute(
                    "UPDATE accounts SET reserved=reserved-? WHERE account_id=?",
                    (max_cost, attempt["account_id"]),
                )
                con.execute(
                    "UPDATE attempts SET state='CANCELLED' WHERE effect_id=?",
                    (attempt["effect_id"],),
                )
                released += max_cost
                self._audit(
                    con, "CANCEL_RESERVED", effect_id=attempt["effect_id"],
                    principal=principal, scope_key=scope_key,
                    account_id=attempt["account_id"], generation=generation,
                    amount=max_cost, detail="revocation won before finality"
                )

            seq = self._audit(
                con, "REVOKE", principal=principal, scope_key=scope_key,
                generation=generation, amount=released,
                detail=f"authority revoked; released reserved={released}"
            )
            con.execute("COMMIT")
        return AtomicDecision(
            "REVOKED", "authority-revoked", generation=generation,
            reserved=released, audit_sequence=seq
        )

    def snapshot(self, account_id: str):
        with self.connect() as con:
            row = con.execute(
                "SELECT * FROM accounts WHERE account_id=?", (account_id,)
            ).fetchone()
        if row is None:
            raise KeyError(account_id)
        return {
            "limit": int(row["budget_limit"]),
            "spent": int(row["spent"]),
            "reserved": int(row["reserved"]),
            "committed_pending": int(row["committed_pending"]),
            "pressure": (
                int(row["spent"]) + int(row["reserved"])
                + int(row["committed_pending"])
            ),
            "available": (
                int(row["budget_limit"]) - int(row["spent"])
                - int(row["reserved"]) - int(row["committed_pending"])
            ),
        }

    def invariant_holds(self, account_id: str):
        s = self.snapshot(account_id)
        return (
            s["spent"] >= 0 and s["reserved"] >= 0
            and s["committed_pending"] >= 0
            and s["pressure"] <= s["limit"]
        )

    def _decision_from_account(self, state, reason, account_id,
                               effect_id=None, generation=None,
                               actual_cost=None, audit_sequence=None):
        s = self.snapshot(account_id)
        return AtomicDecision(
            state, reason, effect_id=effect_id, generation=generation,
            limit=s["limit"], spent=s["spent"], reserved=s["reserved"],
            committed_pending=s["committed_pending"],
            actual_cost=actual_cost, audit_sequence=audit_sequence
        )

    def admit(self, principal: str, scope_key: str, account_id: str,
              action: Action, max_cost: int):
        if max_cost < 0:
            raise ValueError("max_cost must be nonnegative")
        with self.connect() as con:
            con.execute("BEGIN IMMEDIATE")

            # Stable effect identity is inspected before current authority. A retry
            # of a previously cancelled/committed/settled effect reports that
            # durable state rather than pretending it is a brand-new admission.
            existing = con.execute(
                "SELECT * FROM attempts WHERE effect_id=?", (action.effect_id,)
            ).fetchone()
            if existing is not None:
                if (
                    existing["action_hash"] != action.action_hash
                    or existing["account_id"] != account_id
                    or int(existing["max_cost"]) != max_cost
                ):
                    seq = self._audit(
                        con, "ADMIT_DENY", effect_id=action.effect_id,
                        principal=principal, scope_key=scope_key,
                        account_id=account_id, amount=max_cost,
                        detail="effect id conflict"
                    )
                    con.execute("COMMIT")
                    return self._decision_from_account(
                        "DENY", "effect-id-conflict", account_id,
                        action.effect_id, audit_sequence=seq
                    )
                seq = self._audit(
                    con, "ADMIT_IDEMPOTENT", effect_id=action.effect_id,
                    principal=principal, scope_key=scope_key,
                    account_id=account_id, generation=int(existing["generation"]),
                    amount=int(existing["max_cost"]),
                    detail=f"existing state={existing['state']}"
                )
                state = existing["state"]
                con.execute("COMMIT")
                return self._decision_from_account(
                    state, "existing-attempt", account_id, action.effect_id,
                    generation=int(existing["generation"]),
                    actual_cost=existing["actual_cost"], audit_sequence=seq
                )

            auth = con.execute(
                "SELECT generation,active FROM authorities"
                " WHERE principal=? AND scope_key=?",
                (principal, scope_key),
            ).fetchone()
            if auth is None or not auth["active"]:
                seq = self._audit(
                    con, "ADMIT_DENY", effect_id=action.effect_id,
                    principal=principal, scope_key=scope_key,
                    account_id=account_id, detail="authority inactive"
                )
                con.execute("COMMIT")
                return self._decision_from_account(
                    "DENY", "authority-inactive", account_id,
                    action.effect_id, audit_sequence=seq
                )

            account = con.execute(
                "SELECT * FROM accounts WHERE account_id=?", (account_id,)
            ).fetchone()
            if account is None:
                con.execute("ROLLBACK")
                raise KeyError(account_id)

            pressure = (
                int(account["spent"]) + int(account["reserved"])
                + int(account["committed_pending"])
            )
            if pressure + max_cost > int(account["budget_limit"]):
                seq = self._audit(
                    con, "ADMIT_DENY", effect_id=action.effect_id,
                    principal=principal, scope_key=scope_key,
                    account_id=account_id, generation=int(auth["generation"]),
                    amount=max_cost, detail="insufficient shared capacity"
                )
                con.execute("COMMIT")
                return self._decision_from_account(
                    "DENY", "insufficient-capacity", account_id,
                    action.effect_id, generation=int(auth["generation"]),
                    audit_sequence=seq
                )

            generation = int(auth["generation"])
            con.execute(
                "INSERT INTO attempts(effect_id,principal,scope_key,account_id,"
                "generation,action_hash,max_cost,actual_cost,state)"
                " VALUES(?,?,?,?,?,?,?,NULL,'RESERVED')",
                (
                    action.effect_id, principal, scope_key, account_id,
                    generation, action.action_hash, max_cost,
                ),
            )
            con.execute(
                "UPDATE accounts SET reserved=reserved+? WHERE account_id=?",
                (max_cost, account_id),
            )
            seq = self._audit(
                con, "ADMIT_RESERVED", effect_id=action.effect_id,
                principal=principal, scope_key=scope_key,
                account_id=account_id, generation=generation, amount=max_cost,
                detail="authority generation captured and capacity reserved"
            )
            con.execute("COMMIT")
        return self._decision_from_account(
            "RESERVED", "admitted-and-reserved", account_id,
            action.effect_id, generation=generation, audit_sequence=seq
        )

    def commit(self, effect_id: str, action: Action, payload: dict):
        """Atomic local finality point: generation check + resource transition + outbox."""
        with self.connect() as con:
            con.execute("BEGIN IMMEDIATE")
            attempt = con.execute(
                "SELECT * FROM attempts WHERE effect_id=?", (effect_id,)
            ).fetchone()
            if attempt is None:
                con.execute("ROLLBACK")
                raise KeyError(effect_id)

            account_id = attempt["account_id"]
            generation = int(attempt["generation"])
            max_cost = int(attempt["max_cost"])

            if attempt["action_hash"] != action.action_hash:
                seq = self._audit(
                    con, "COMMIT_DENY", effect_id=effect_id,
                    principal=attempt["principal"], scope_key=attempt["scope_key"],
                    account_id=account_id, generation=generation,
                    detail="action substitution"
                )
                con.execute("COMMIT")
                return self._decision_from_account(
                    "DENY", "action-substitution", account_id,
                    effect_id, generation, audit_sequence=seq
                )

            if attempt["state"] in ("COMMITTED", "SETTLED", "NO_EFFECT"):
                seq = self._audit(
                    con, "COMMIT_IDEMPOTENT", effect_id=effect_id,
                    principal=attempt["principal"], scope_key=attempt["scope_key"],
                    account_id=account_id, generation=generation,
                    detail=f"already {attempt['state']}"
                )
                con.execute("COMMIT")
                return self._decision_from_account(
                    attempt["state"], "existing-finality", account_id,
                    effect_id, generation, attempt["actual_cost"], seq
                )

            if attempt["state"] == "CANCELLED":
                seq = self._audit(
                    con, "COMMIT_DENY", effect_id=effect_id,
                    principal=attempt["principal"], scope_key=attempt["scope_key"],
                    account_id=account_id, generation=generation,
                    detail="attempt cancelled"
                )
                con.execute("COMMIT")
                return self._decision_from_account(
                    "DENY", "attempt-cancelled", account_id,
                    effect_id, generation, audit_sequence=seq
                )

            auth = con.execute(
                "SELECT generation,active FROM authorities"
                " WHERE principal=? AND scope_key=?",
                (attempt["principal"], attempt["scope_key"]),
            ).fetchone()
            if (
                auth is None
                or not auth["active"]
                or int(auth["generation"]) != generation
            ):
                # If revocation/regrant changed generation but did not proactively
                # cancel this row for any reason, fail closed and release reservation.
                con.execute(
                    "UPDATE accounts SET reserved=reserved-? WHERE account_id=?",
                    (max_cost, account_id),
                )
                con.execute(
                    "UPDATE attempts SET state='CANCELLED' WHERE effect_id=?",
                    (effect_id,),
                )
                seq = self._audit(
                    con, "COMMIT_DENY", effect_id=effect_id,
                    principal=attempt["principal"], scope_key=attempt["scope_key"],
                    account_id=account_id,
                    generation=None if auth is None else int(auth["generation"]),
                    amount=max_cost, detail="authority stale/inactive at finality"
                )
                con.execute("COMMIT")
                return self._decision_from_account(
                    "DENY", "authority-not-live-at-finality", account_id,
                    effect_id, generation, audit_sequence=seq
                )

            # One transaction moves the budget from pre-finality RESERVED to
            # accepted-but-unreconciled COMMITTED_PENDING and creates the outbox.
            con.execute(
                "UPDATE accounts SET reserved=reserved-?,"
                " committed_pending=committed_pending+? WHERE account_id=?",
                (max_cost, max_cost, account_id),
            )
            con.execute(
                "UPDATE attempts SET state='COMMITTED' WHERE effect_id=?",
                (effect_id,),
            )
            con.execute(
                "INSERT INTO outbox(effect_id,action_hash,payload_json,state,"
                "receipt,relay_attempts) VALUES(?,?,?,'PENDING',NULL,0)",
                (
                    effect_id, action.action_hash,
                    json.dumps(payload, sort_keys=True),
                ),
            )
            seq = self._audit(
                con, "FINALITY_COMMIT", effect_id=effect_id,
                principal=attempt["principal"], scope_key=attempt["scope_key"],
                account_id=account_id, generation=generation, amount=max_cost,
                detail="authority+resource+outbox committed atomically"
            )
            con.execute("COMMIT")
        return self._decision_from_account(
            "COMMITTED", "local-finality-accepted", account_id,
            effect_id, generation, audit_sequence=seq
        )

    def outbox_row(self, effect_id: str):
        with self.connect() as con:
            row = con.execute(
                "SELECT * FROM outbox WHERE effect_id=?", (effect_id,)
            ).fetchone()
        return dict(row) if row else None

    def settle_receipt(self, effect_id: str, receipt: str, actual_cost: int):
        if actual_cost < 0:
            raise ValueError("actual_cost must be nonnegative")
        with self.connect() as con:
            con.execute("BEGIN IMMEDIATE")
            attempt = con.execute(
                "SELECT * FROM attempts WHERE effect_id=?", (effect_id,)
            ).fetchone()
            if attempt is None:
                con.execute("ROLLBACK")
                raise KeyError(effect_id)
            account_id = attempt["account_id"]
            max_cost = int(attempt["max_cost"])

            if attempt["state"] == "SETTLED":
                if int(attempt["actual_cost"]) != actual_cost:
                    seq = self._audit(
                        con, "SETTLE_DENY", effect_id=effect_id,
                        account_id=account_id, amount=actual_cost,
                        detail="conflicting settlement"
                    )
                    con.execute("COMMIT")
                    return self._decision_from_account(
                        "DENY", "conflicting-settlement", account_id,
                        effect_id, actual_cost=int(attempt["actual_cost"]),
                        audit_sequence=seq
                    )
                seq = self._audit(
                    con, "SETTLE_IDEMPOTENT", effect_id=effect_id,
                    account_id=account_id, amount=actual_cost,
                    detail="already settled"
                )
                con.execute("COMMIT")
                return self._decision_from_account(
                    "SETTLED", "already-settled", account_id,
                    effect_id, actual_cost=actual_cost, audit_sequence=seq
                )

            if attempt["state"] != "COMMITTED":
                seq = self._audit(
                    con, "SETTLE_DENY", effect_id=effect_id,
                    account_id=account_id, amount=actual_cost,
                    detail=f"invalid state={attempt['state']}"
                )
                con.execute("COMMIT")
                return self._decision_from_account(
                    "DENY", "not-committed", account_id,
                    effect_id, audit_sequence=seq
                )

            if actual_cost > max_cost:
                seq = self._audit(
                    con, "SETTLE_INDETERMINATE", effect_id=effect_id,
                    account_id=account_id, amount=actual_cost,
                    detail=f"actual exceeds committed maximum {max_cost}"
                )
                con.execute("COMMIT")
                return self._decision_from_account(
                    "INDETERMINATE", "provider-cost-exceeds-maximum",
                    account_id, effect_id, actual_cost=actual_cost,
                    audit_sequence=seq
                )

            con.execute(
                "UPDATE accounts SET committed_pending=committed_pending-?,"
                " spent=spent+? WHERE account_id=?",
                (max_cost, actual_cost, account_id),
            )
            con.execute(
                "UPDATE attempts SET state='SETTLED',actual_cost=? WHERE effect_id=?",
                (actual_cost, effect_id),
            )
            con.execute(
                "UPDATE outbox SET state='DELIVERED',receipt=? WHERE effect_id=?",
                (receipt, effect_id),
            )
            seq = self._audit(
                con, "SETTLE", effect_id=effect_id, account_id=account_id,
                amount=actual_cost, detail=f"unused exposure={max_cost-actual_cost}"
            )
            con.execute("COMMIT")
        return self._decision_from_account(
            "SETTLED", "provider-receipt-settled", account_id,
            effect_id, actual_cost=actual_cost, audit_sequence=seq
        )

    def certify_no_effect(self, effect_id: str, certificate: str):
        with self.connect() as con:
            con.execute("BEGIN IMMEDIATE")
            attempt = con.execute(
                "SELECT * FROM attempts WHERE effect_id=?", (effect_id,)
            ).fetchone()
            if attempt is None:
                con.execute("ROLLBACK")
                raise KeyError(effect_id)
            account_id = attempt["account_id"]
            max_cost = int(attempt["max_cost"])
            if attempt["state"] == "NO_EFFECT":
                seq = self._audit(
                    con, "NO_EFFECT_IDEMPOTENT", effect_id=effect_id,
                    account_id=account_id, detail="already certified"
                )
                con.execute("COMMIT")
                return self._decision_from_account(
                    "NO_EFFECT", "already-certified", account_id,
                    effect_id, audit_sequence=seq
                )
            if attempt["state"] != "COMMITTED":
                seq = self._audit(
                    con, "NO_EFFECT_DENY", effect_id=effect_id,
                    account_id=account_id,
                    detail=f"invalid state={attempt['state']}"
                )
                con.execute("COMMIT")
                return self._decision_from_account(
                    "DENY", "not-committed", account_id,
                    effect_id, audit_sequence=seq
                )

            con.execute(
                "UPDATE accounts SET committed_pending=committed_pending-?"
                " WHERE account_id=?",
                (max_cost, account_id),
            )
            con.execute(
                "UPDATE attempts SET state='NO_EFFECT' WHERE effect_id=?",
                (effect_id,),
            )
            con.execute(
                "UPDATE outbox SET state='NO_EFFECT',receipt=? WHERE effect_id=?",
                (certificate, effect_id),
            )
            seq = self._audit(
                con, "NO_EFFECT", effect_id=effect_id, account_id=account_id,
                amount=max_cost, detail="committed exposure released"
            )
            con.execute("COMMIT")
        return self._decision_from_account(
            "NO_EFFECT", "provider-certified-no-effect",
            account_id, effect_id, audit_sequence=seq
        )

    def mark_relay_attempt(self, effect_id: str):
        with self.connect() as con:
            con.execute("BEGIN IMMEDIATE")
            con.execute(
                "UPDATE outbox SET relay_attempts=relay_attempts+1 WHERE effect_id=?",
                (effect_id,),
            )
            con.execute("COMMIT")

    def audit(self):
        with self.connect() as con:
            return [dict(r) for r in con.execute(
                "SELECT * FROM audit ORDER BY sequence"
            ).fetchall()]


class DurableIdempotentProvider:
    """Synthetic remote provider with durable effect-id idempotency."""

    def __init__(self, db_path: str | Path):
        self.db_path = str(db_path)
        with sqlite3.connect(self.db_path) as con:
            con.execute("""
                CREATE TABLE IF NOT EXISTS provider_effects(
                    effect_id TEXT PRIMARY KEY,
                    payload_json TEXT NOT NULL,
                    actual_cost INTEGER NOT NULL,
                    receipt TEXT NOT NULL
                )
            """)

    def send(self, effect_id: str, payload: dict, actual_cost: int):
        with sqlite3.connect(self.db_path) as con:
            row = con.execute(
                "SELECT * FROM provider_effects WHERE effect_id=?",
                (effect_id,),
            ).fetchone()
            if row is not None:
                return {"receipt": row[3], "actual_cost": int(row[2])}
            receipt = f"provider:{effect_id}"
            con.execute(
                "INSERT INTO provider_effects(effect_id,payload_json,actual_cost,receipt)"
                " VALUES(?,?,?,?)",
                (effect_id, json.dumps(payload, sort_keys=True), actual_cost, receipt),
            )
            return {"receipt": receipt, "actual_cost": actual_cost}

    def count(self):
        with sqlite3.connect(self.db_path) as con:
            return int(con.execute(
                "SELECT COUNT(*) FROM provider_effects"
            ).fetchone()[0])

    def receipt(self, effect_id):
        with sqlite3.connect(self.db_path) as con:
            row = con.execute(
                "SELECT receipt,actual_cost FROM provider_effects WHERE effect_id=?",
                (effect_id,),
            ).fetchone()
        if row is None:
            return None
        return {"receipt": row[0], "actual_cost": int(row[1])}


class OutboxRelay:
    def __init__(self, gate: AtomicFinalityGate, provider: DurableIdempotentProvider):
        self.gate = gate
        self.provider = provider

    def deliver(self, effect_id: str, actual_cost: int,
                crash_after_provider=False):
        row = self.gate.outbox_row(effect_id)
        if row is None:
            return {"state": "MISSING"}
        if row["state"] == "DELIVERED":
            return {"state": "DELIVERED", "receipt": row["receipt"]}
        if row["state"] == "NO_EFFECT":
            return {"state": "NO_EFFECT", "receipt": row["receipt"]}

        self.gate.mark_relay_attempt(effect_id)
        payload = json.loads(row["payload_json"])
        result = self.provider.send(effect_id, payload, actual_cost)
        if crash_after_provider:
            # Simulate process death after remote accept but before local receipt write.
            return {"state": "CRASHED_AFTER_PROVIDER"}

        d = self.gate.settle_receipt(
            effect_id, result["receipt"], result["actual_cost"]
        )
        return {"state": d.state, "decision": d.__dict__}


class NaiveDualWrite:
    """Weak comparison demonstrating the classic dual-write anomalies."""
    def __init__(self):
        self.local_final = set()
        self.outbox = set()
        self.remote_effects = 0

    def commit_local_then_crash(self, effect_id):
        self.local_final.add(effect_id)
        # Crash before durable outbox insert.
        return

    def send_remote_then_crash(self, effect_id):
        # Non-idempotent remote.
        self.remote_effects += 1
        # Crash before recording final state.
        return

    def retry_remote(self, effect_id):
        self.remote_effects += 1


class ConventionalAtomicOracle:
    """Independent pure state machine used for bounded trace comparison."""
    def __init__(self, budget=1):
        self.budget = budget
        self.spent = 0
        self.reserved = 0
        self.committed = 0
        self.generation = 1
        self.active = True
        self.attempts = {}
        self.outbox = set()

    def admit(self, eid, cost=1):
        if eid in self.attempts:
            return self.attempts[eid]["state"]
        if not self.active:
            return "DENY"
        if self.spent + self.reserved + self.committed + cost > self.budget:
            return "DENY"
        self.attempts[eid] = {
            "state": "RESERVED", "generation": self.generation, "cost": cost
        }
        self.reserved += cost
        return "RESERVED"

    def revoke(self):
        self.generation += 1
        self.active = False
        for eid, row in self.attempts.items():
            if row["state"] == "RESERVED":
                self.reserved -= row["cost"]
                row["state"] = "CANCELLED"

    def regrant(self):
        self.generation += 1
        self.active = True

    def commit(self, eid):
        row = self.attempts.get(eid)
        if row is None:
            return "MISSING"
        if row["state"] in ("COMMITTED", "SETTLED", "NO_EFFECT"):
            return row["state"]
        if row["state"] == "CANCELLED":
            return "DENY"
        if not self.active or row["generation"] != self.generation:
            self.reserved -= row["cost"]
            row["state"] = "CANCELLED"
            return "DENY"
        self.reserved -= row["cost"]
        self.committed += row["cost"]
        row["state"] = "COMMITTED"
        self.outbox.add(eid)
        return "COMMITTED"

    def settle(self, eid, actual=1):
        row = self.attempts.get(eid)
        if row is None:
            return "MISSING"
        if row["state"] == "SETTLED":
            return "SETTLED"
        if row["state"] != "COMMITTED":
            return "DENY"
        if actual > row["cost"]:
            return "INDETERMINATE"
        self.committed -= row["cost"]
        self.spent += actual
        row["state"] = "SETTLED"
        return "SETTLED"
