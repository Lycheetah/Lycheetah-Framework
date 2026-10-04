#!/usr/bin/env python3
"""
Lycheetah Shared Resource Commitment Ledger v0.8

A durable, multi-broker resource reservation ledger.

Invariant:
    spent(account) + reserved(account) <= limit(account)

The invariant is protected by serializing reserve/settle/release mutations in
one SQLite database using BEGIN IMMEDIATE.

This is conventional transactional accounting, not a novel algorithm. The
Lycheetah-specific role is composition with effect finality: unresolved external
effects keep their maximum charge reserved until reconciliation, preventing
retry/cross-broker overspend.

Boundary:
- one SQLite database is the serialization authority;
- all brokers must use it;
- external providers must not exceed the reserved upper bound if a real-world
  spend bound is claimed;
- distributed replicas/partitions are not covered.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sqlite3
from typing import Optional


ACTIVE_STATES = ("RESERVED", "UNKNOWN")


@dataclass(frozen=True)
class BudgetDecision:
    state: str
    reason: str
    account_id: str
    effect_id: str | None = None
    reserved: int = 0
    spent: int = 0
    limit: int = 0
    reservation_max: int | None = None
    actual_cost: int | None = None
    audit_sequence: int | None = None


class SharedResourceLedger:
    def __init__(self, db_path: str | Path):
        self.db_path = str(db_path)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def connect(self):
        con = sqlite3.connect(self.db_path, timeout=30, isolation_level=None)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA journal_mode=WAL")
        con.execute("PRAGMA synchronous=FULL")
        return con

    def _init_db(self):
        with self.connect() as con:
            con.executescript("""
            CREATE TABLE IF NOT EXISTS accounts(
                account_id TEXT PRIMARY KEY,
                budget_limit INTEGER NOT NULL CHECK(budget_limit >= 0),
                spent INTEGER NOT NULL DEFAULT 0 CHECK(spent >= 0),
                reserved INTEGER NOT NULL DEFAULT 0 CHECK(reserved >= 0),
                generation INTEGER NOT NULL DEFAULT 1 CHECK(generation >= 1)
            );

            CREATE TABLE IF NOT EXISTS reservations(
                effect_id TEXT PRIMARY KEY,
                account_id TEXT NOT NULL,
                broker_id TEXT NOT NULL,
                max_cost INTEGER NOT NULL CHECK(max_cost >= 0),
                actual_cost INTEGER,
                state TEXT NOT NULL,
                generation INTEGER NOT NULL,
                FOREIGN KEY(account_id) REFERENCES accounts(account_id)
            );

            CREATE TABLE IF NOT EXISTS audit(
                sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                kind TEXT NOT NULL,
                account_id TEXT NOT NULL,
                effect_id TEXT,
                broker_id TEXT,
                amount INTEGER,
                detail TEXT NOT NULL
            );
            """)

    def _audit(self, con, kind, account_id, effect_id=None, broker_id=None,
               amount=None, detail=""):
        cur = con.execute(
            "INSERT INTO audit(kind,account_id,effect_id,broker_id,amount,detail)"
            " VALUES(?,?,?,?,?,?)",
            (kind, account_id, effect_id, broker_id, amount, detail),
        )
        return int(cur.lastrowid)

    def create_account(self, account_id: str, budget_limit: int):
        if budget_limit < 0:
            raise ValueError("budget_limit must be nonnegative")
        with self.connect() as con:
            con.execute("BEGIN IMMEDIATE")
            existing = con.execute(
                "SELECT * FROM accounts WHERE account_id=?", (account_id,)
            ).fetchone()
            if existing is None:
                con.execute(
                    "INSERT INTO accounts(account_id,budget_limit,spent,reserved,generation)"
                    " VALUES(?,?,0,0,1)",
                    (account_id, budget_limit),
                )
                self._audit(
                    con, "ACCOUNT_CREATE", account_id, amount=budget_limit,
                    detail="resource account created"
                )
            elif int(existing["budget_limit"]) != budget_limit:
                con.execute("ROLLBACK")
                raise ValueError("account exists with different budget")
            con.execute("COMMIT")

    def snapshot(self, account_id: str):
        with self.connect() as con:
            row = con.execute(
                "SELECT * FROM accounts WHERE account_id=?", (account_id,)
            ).fetchone()
        if row is None:
            raise KeyError(account_id)
        return {
            "account_id": account_id,
            "limit": int(row["budget_limit"]),
            "spent": int(row["spent"]),
            "reserved": int(row["reserved"]),
            "available": (
                int(row["budget_limit"])
                - int(row["spent"])
                - int(row["reserved"])
            ),
            "generation": int(row["generation"]),
        }

    def _decision(self, state, reason, account_id, effect_id=None,
                  reservation_max=None, actual_cost=None, audit_sequence=None):
        s = self.snapshot(account_id)
        return BudgetDecision(
            state=state, reason=reason, account_id=account_id,
            effect_id=effect_id, reserved=s["reserved"], spent=s["spent"],
            limit=s["limit"], reservation_max=reservation_max,
            actual_cost=actual_cost, audit_sequence=audit_sequence,
        )

    def reserve(self, account_id: str, broker_id: str,
                effect_id: str, max_cost: int) -> BudgetDecision:
        if max_cost < 0:
            raise ValueError("max_cost must be nonnegative")
        with self.connect() as con:
            con.execute("BEGIN IMMEDIATE")
            account = con.execute(
                "SELECT * FROM accounts WHERE account_id=?", (account_id,)
            ).fetchone()
            if account is None:
                con.execute("ROLLBACK")
                raise KeyError(account_id)

            existing = con.execute(
                "SELECT * FROM reservations WHERE effect_id=?", (effect_id,)
            ).fetchone()
            if existing is not None:
                if (
                    existing["account_id"] != account_id
                    or int(existing["max_cost"]) != max_cost
                ):
                    seq = self._audit(
                        con, "RESERVE_DENY", account_id, effect_id, broker_id,
                        max_cost, "effect id reused with conflicting reservation"
                    )
                    con.execute("COMMIT")
                    return self._decision(
                        "DENY", "effect-id-conflict", account_id, effect_id,
                        reservation_max=max_cost, audit_sequence=seq
                    )
                seq = self._audit(
                    con, "RESERVE_IDEMPOTENT", account_id, effect_id, broker_id,
                    max_cost, f"existing state={existing['state']}"
                )
                con.execute("COMMIT")
                return self._decision(
                    existing["state"], "existing-reservation", account_id,
                    effect_id, reservation_max=int(existing["max_cost"]),
                    actual_cost=existing["actual_cost"], audit_sequence=seq
                )

            limit_ = int(account["budget_limit"])
            spent = int(account["spent"])
            reserved = int(account["reserved"])
            if spent + reserved + max_cost > limit_:
                seq = self._audit(
                    con, "RESERVE_DENY", account_id, effect_id, broker_id,
                    max_cost, "insufficient shared capacity"
                )
                con.execute("COMMIT")
                return self._decision(
                    "DENY", "insufficient-capacity", account_id, effect_id,
                    reservation_max=max_cost, audit_sequence=seq
                )

            generation = int(account["generation"])
            con.execute(
                "INSERT INTO reservations(effect_id,account_id,broker_id,max_cost,"
                "actual_cost,state,generation) VALUES(?,?,?,?,NULL,'RESERVED',?)",
                (effect_id, account_id, broker_id, max_cost, generation),
            )
            con.execute(
                "UPDATE accounts SET reserved=reserved+? WHERE account_id=?",
                (max_cost, account_id),
            )
            seq = self._audit(
                con, "RESERVE", account_id, effect_id, broker_id, max_cost,
                "maximum cost reserved"
            )
            con.execute("COMMIT")
        return self._decision(
            "RESERVED", "capacity-reserved", account_id, effect_id,
            reservation_max=max_cost, audit_sequence=seq
        )

    def mark_unknown(self, effect_id: str) -> BudgetDecision:
        with self.connect() as con:
            con.execute("BEGIN IMMEDIATE")
            row = con.execute(
                "SELECT * FROM reservations WHERE effect_id=?", (effect_id,)
            ).fetchone()
            if row is None:
                con.execute("ROLLBACK")
                raise KeyError(effect_id)
            account_id = row["account_id"]
            if row["state"] == "SETTLED":
                seq = self._audit(
                    con, "UNKNOWN_IGNORED", account_id, effect_id, row["broker_id"],
                    row["max_cost"], "already settled"
                )
                con.execute("COMMIT")
                return self._decision(
                    "SETTLED", "already-settled", account_id, effect_id,
                    reservation_max=int(row["max_cost"]),
                    actual_cost=int(row["actual_cost"]), audit_sequence=seq
                )
            if row["state"] == "RELEASED":
                seq = self._audit(
                    con, "UNKNOWN_DENY", account_id, effect_id, row["broker_id"],
                    row["max_cost"], "already released"
                )
                con.execute("COMMIT")
                return self._decision(
                    "DENY", "already-released", account_id, effect_id,
                    reservation_max=int(row["max_cost"]), audit_sequence=seq
                )
            con.execute(
                "UPDATE reservations SET state='UNKNOWN' WHERE effect_id=?",
                (effect_id,),
            )
            seq = self._audit(
                con, "UNKNOWN", account_id, effect_id, row["broker_id"],
                row["max_cost"], "outcome unresolved; capacity retained"
            )
            con.execute("COMMIT")
        return self._decision(
            "UNKNOWN", "capacity-retained-pending-reconciliation",
            account_id, effect_id, reservation_max=int(row["max_cost"]),
            audit_sequence=seq
        )

    def settle(self, effect_id: str, actual_cost: int) -> BudgetDecision:
        if actual_cost < 0:
            raise ValueError("actual_cost must be nonnegative")
        with self.connect() as con:
            con.execute("BEGIN IMMEDIATE")
            row = con.execute(
                "SELECT * FROM reservations WHERE effect_id=?", (effect_id,)
            ).fetchone()
            if row is None:
                con.execute("ROLLBACK")
                raise KeyError(effect_id)
            account_id = row["account_id"]
            max_cost = int(row["max_cost"])

            if row["state"] == "SETTLED":
                if int(row["actual_cost"]) != actual_cost:
                    seq = self._audit(
                        con, "SETTLE_DENY", account_id, effect_id, row["broker_id"],
                        actual_cost, "conflicting settlement"
                    )
                    con.execute("COMMIT")
                    return self._decision(
                        "DENY", "conflicting-settlement", account_id, effect_id,
                        reservation_max=max_cost,
                        actual_cost=int(row["actual_cost"]), audit_sequence=seq
                    )
                seq = self._audit(
                    con, "SETTLE_IDEMPOTENT", account_id, effect_id,
                    row["broker_id"], actual_cost, "already settled"
                )
                con.execute("COMMIT")
                return self._decision(
                    "SETTLED", "already-settled", account_id, effect_id,
                    reservation_max=max_cost, actual_cost=actual_cost,
                    audit_sequence=seq
                )

            if row["state"] == "RELEASED":
                seq = self._audit(
                    con, "SETTLE_DENY", account_id, effect_id, row["broker_id"],
                    actual_cost, "reservation already released"
                )
                con.execute("COMMIT")
                return self._decision(
                    "DENY", "already-released", account_id, effect_id,
                    reservation_max=max_cost, audit_sequence=seq
                )

            if actual_cost > max_cost:
                # Do not mutate counters. A real provider exceeding the bound is
                # an assumption failure that requires separate incident handling.
                seq = self._audit(
                    con, "SETTLE_INDETERMINATE", account_id, effect_id,
                    row["broker_id"], actual_cost,
                    f"provider cost exceeds reserved upper bound {max_cost}"
                )
                con.execute("COMMIT")
                return self._decision(
                    "INDETERMINATE", "actual-cost-exceeds-reservation",
                    account_id, effect_id, reservation_max=max_cost,
                    actual_cost=actual_cost, audit_sequence=seq
                )

            con.execute(
                "UPDATE accounts SET reserved=reserved-?, spent=spent+?"
                " WHERE account_id=?",
                (max_cost, actual_cost, account_id),
            )
            con.execute(
                "UPDATE reservations SET state='SETTLED',actual_cost=?"
                " WHERE effect_id=?",
                (actual_cost, effect_id),
            )
            seq = self._audit(
                con, "SETTLE", account_id, effect_id, row["broker_id"],
                actual_cost, f"released unused={max_cost-actual_cost}"
            )
            con.execute("COMMIT")
        return self._decision(
            "SETTLED", "effect-settled", account_id, effect_id,
            reservation_max=max_cost, actual_cost=actual_cost,
            audit_sequence=seq
        )

    def release_no_effect(self, effect_id: str) -> BudgetDecision:
        with self.connect() as con:
            con.execute("BEGIN IMMEDIATE")
            row = con.execute(
                "SELECT * FROM reservations WHERE effect_id=?", (effect_id,)
            ).fetchone()
            if row is None:
                con.execute("ROLLBACK")
                raise KeyError(effect_id)
            account_id = row["account_id"]
            max_cost = int(row["max_cost"])

            if row["state"] == "RELEASED":
                seq = self._audit(
                    con, "RELEASE_IDEMPOTENT", account_id, effect_id,
                    row["broker_id"], max_cost, "already released"
                )
                con.execute("COMMIT")
                return self._decision(
                    "RELEASED", "already-released", account_id, effect_id,
                    reservation_max=max_cost, audit_sequence=seq
                )
            if row["state"] == "SETTLED":
                seq = self._audit(
                    con, "RELEASE_DENY", account_id, effect_id,
                    row["broker_id"], max_cost, "already settled"
                )
                con.execute("COMMIT")
                return self._decision(
                    "DENY", "already-settled", account_id, effect_id,
                    reservation_max=max_cost,
                    actual_cost=int(row["actual_cost"]), audit_sequence=seq
                )

            con.execute(
                "UPDATE accounts SET reserved=reserved-? WHERE account_id=?",
                (max_cost, account_id),
            )
            con.execute(
                "UPDATE reservations SET state='RELEASED' WHERE effect_id=?",
                (effect_id,),
            )
            seq = self._audit(
                con, "RELEASE", account_id, effect_id, row["broker_id"],
                max_cost, "provider certified no effect"
            )
            con.execute("COMMIT")
        return self._decision(
            "RELEASED", "no-effect-capacity-released",
            account_id, effect_id, reservation_max=max_cost,
            audit_sequence=seq
        )

    def invariant_holds(self, account_id: str) -> bool:
        s = self.snapshot(account_id)
        return (
            s["spent"] >= 0
            and s["reserved"] >= 0
            and s["spent"] + s["reserved"] <= s["limit"]
        )

    def reservation(self, effect_id: str):
        with self.connect() as con:
            row = con.execute(
                "SELECT * FROM reservations WHERE effect_id=?", (effect_id,)
            ).fetchone()
        return dict(row) if row else None

    def audit(self, account_id: str):
        with self.connect() as con:
            return [
                dict(row) for row in con.execute(
                    "SELECT * FROM audit WHERE account_id=? ORDER BY sequence",
                    (account_id,),
                ).fetchall()
            ]


class InstanceLocalBudget:
    """Deliberately weak current-style baseline: one ledger per broker."""

    def __init__(self, budget_limit: int):
        self.limit = budget_limit
        self.spent = 0
        self.reserved = 0
        self.effects = {}

    def reserve(self, effect_id: str, max_cost: int):
        if effect_id in self.effects:
            return True
        if self.spent + self.reserved + max_cost > self.limit:
            return False
        self.effects[effect_id] = ["RESERVED", max_cost, None]
        self.reserved += max_cost
        return True

    def settle(self, effect_id: str, actual_cost: int):
        state, max_cost, _ = self.effects[effect_id]
        if state == "SETTLED":
            return True
        if actual_cost > max_cost:
            return False
        self.reserved -= max_cost
        self.spent += actual_cost
        self.effects[effect_id] = ["SETTLED", max_cost, actual_cost]
        return True


class ConventionalReservationOracle:
    """Independent single-account state machine for bounded trace checks."""

    def __init__(self, limit=2):
        self.limit = limit
        self.spent = 0
        self.reserved = 0
        self.effects = {}

    def reserve(self, effect_id, amount=1):
        if effect_id in self.effects:
            return self.effects[effect_id][0]
        if self.spent + self.reserved + amount > self.limit:
            return "DENY"
        self.effects[effect_id] = ["RESERVED", amount, None]
        self.reserved += amount
        return "RESERVED"

    def unknown(self, effect_id):
        if effect_id not in self.effects:
            return "MISSING"
        state, amount, actual = self.effects[effect_id]
        if state == "SETTLED":
            return "SETTLED"
        if state == "RELEASED":
            return "DENY"
        self.effects[effect_id][0] = "UNKNOWN"
        return "UNKNOWN"

    def settle(self, effect_id, actual=1):
        if effect_id not in self.effects:
            return "MISSING"
        state, amount, old_actual = self.effects[effect_id]
        if state == "SETTLED":
            return "SETTLED" if old_actual == actual else "DENY"
        if state == "RELEASED":
            return "DENY"
        if actual > amount:
            return "INDETERMINATE"
        self.reserved -= amount
        self.spent += actual
        self.effects[effect_id] = ["SETTLED", amount, actual]
        return "SETTLED"

    def release(self, effect_id):
        if effect_id not in self.effects:
            return "MISSING"
        state, amount, actual = self.effects[effect_id]
        if state == "RELEASED":
            return "RELEASED"
        if state == "SETTLED":
            return "DENY"
        self.reserved -= amount
        self.effects[effect_id][0] = "RELEASED"
        return "RELEASED"
