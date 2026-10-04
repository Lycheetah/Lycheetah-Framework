#!/usr/bin/env python3
"""
Lycheetah Dependency-Scoped Evidence Finality Gate v1.0

Concrete invariant:
    evidence required by an effect is re-evaluated inside the SAME serialized
    transaction that performs authority revalidation, resource transition, and
    durable outbox creation.

Two requirement modes:
    EXACT:
        The exact admitted evidence revision/value/status/subject must survive.
    SUBJECT_STATUS:
        The current evidence may have a newer revision, but it must still
        satisfy the declared semantic predicate:
            subject_hash == required_subject_hash
            status == required_status

This avoids two bad extremes:
    - admission-only evidence, which can become stale before effect finality;
    - global freshness epochs, which can block safe work after unrelated changes.

Conventional roots:
    optimistic concurrency / versioned state, policy enforcement at the protected
    boundary, and dependency-scoped runtime validation. Novelty is not claimed.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
import sqlite3
from typing import Iterable

@dataclass(frozen=True)
class Action:
    principal: str
    tool: str
    operation: str
    object_id: str
    destination: str
    arguments: dict
    effect_id: str

    @property
    def action_hash(self) -> str:
        body = {
            "principal": self.principal,
            "tool": self.tool,
            "operation": self.operation,
            "object_id": self.object_id,
            "destination": self.destination,
            "arguments": self.arguments,
            "effect_id": self.effect_id,
        }
        raw = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return __import__("hashlib").sha256(raw).hexdigest()



VALID_STATUSES = {"PASS", "FAIL", "UNKNOWN"}
VALID_MODES = {"EXACT", "SUBJECT_STATUS"}


@dataclass(frozen=True)
class EvidenceRequirement:
    evidence_key: str
    mode: str
    required_status: str | None = None
    required_subject_hash: str | None = None

    def __post_init__(self):
        if self.mode not in VALID_MODES:
            raise ValueError("unknown evidence mode")
        if self.mode == "SUBJECT_STATUS":
            if self.required_status not in VALID_STATUSES:
                raise ValueError("SUBJECT_STATUS requires a valid required_status")
            if not self.required_subject_hash:
                raise ValueError("SUBJECT_STATUS requires required_subject_hash")


@dataclass(frozen=True)
class FinalityDecision:
    state: str
    reason: str
    effect_id: str | None = None
    evidence_key: str | None = None
    generation: int | None = None
    limit: int | None = None
    spent: int | None = None
    reserved: int | None = None
    committed_pending: int | None = None
    audit_sequence: int | None = None


class EvidenceFinalityGate:
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
                committed_pending INTEGER NOT NULL DEFAULT 0
                    CHECK(committed_pending >= 0)
            );

            CREATE TABLE IF NOT EXISTS evidence(
                evidence_key TEXT PRIMARY KEY,
                version INTEGER NOT NULL,
                subject_hash TEXT NOT NULL,
                value_hash TEXT NOT NULL,
                status TEXT NOT NULL,
                updated_by TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS evidence_meta(
                key TEXT PRIMARY KEY,
                value INTEGER NOT NULL
            );
            INSERT OR IGNORE INTO evidence_meta(key,value)
                VALUES('global_epoch',0);

            CREATE TABLE IF NOT EXISTS attempts(
                effect_id TEXT PRIMARY KEY,
                principal TEXT NOT NULL,
                scope_key TEXT NOT NULL,
                account_id TEXT NOT NULL,
                generation INTEGER NOT NULL,
                action_hash TEXT NOT NULL,
                max_cost INTEGER NOT NULL CHECK(max_cost >= 0),
                state TEXT NOT NULL,
                admitted_global_evidence_epoch INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS attempt_evidence(
                effect_id TEXT NOT NULL,
                evidence_key TEXT NOT NULL,
                mode TEXT NOT NULL,
                admitted_version INTEGER NOT NULL,
                admitted_subject_hash TEXT NOT NULL,
                admitted_value_hash TEXT NOT NULL,
                admitted_status TEXT NOT NULL,
                required_subject_hash TEXT,
                required_status TEXT,
                PRIMARY KEY(effect_id,evidence_key),
                FOREIGN KEY(effect_id) REFERENCES attempts(effect_id)
            );

            CREATE TABLE IF NOT EXISTS outbox(
                effect_id TEXT PRIMARY KEY,
                action_hash TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                state TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS audit(
                sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                kind TEXT NOT NULL,
                effect_id TEXT,
                evidence_key TEXT,
                principal TEXT,
                scope_key TEXT,
                account_id TEXT,
                generation INTEGER,
                detail TEXT NOT NULL
            );
            """)

    def _audit(self, con, kind, *, effect_id=None, evidence_key=None,
               principal=None, scope_key=None, account_id=None,
               generation=None, detail=""):
        cur = con.execute(
            "INSERT INTO audit(kind,effect_id,evidence_key,principal,scope_key,"
            "account_id,generation,detail) VALUES(?,?,?,?,?,?,?,?)",
            (kind,effect_id,evidence_key,principal,scope_key,
             account_id,generation,detail),
        )
        return int(cur.lastrowid)

    def create_account(self, account_id: str, budget_limit: int):
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
                    (account_id,budget_limit),
                )
            elif int(row["budget_limit"]) != budget_limit:
                con.execute("ROLLBACK")
                raise ValueError("account exists with different limit")
            con.execute("COMMIT")

    def activate(self, principal: str, scope_key: str):
        with self.connect() as con:
            con.execute("BEGIN IMMEDIATE")
            row = con.execute(
                "SELECT generation FROM authorities WHERE principal=? AND scope_key=?",
                (principal,scope_key),
            ).fetchone()
            generation = 1 if row is None else int(row["generation"]) + 1
            con.execute(
                "INSERT INTO authorities(principal,scope_key,generation,active)"
                " VALUES(?,?,?,1)"
                " ON CONFLICT(principal,scope_key) DO UPDATE SET"
                " generation=excluded.generation,active=1",
                (principal,scope_key,generation),
            )
            seq = self._audit(
                con,"ACTIVATE",principal=principal,scope_key=scope_key,
                generation=generation,detail="authority active"
            )
            con.execute("COMMIT")
        return FinalityDecision(
            "ACTIVE","authority-activated",generation=generation,
            audit_sequence=seq
        )

    def revoke(self, principal: str, scope_key: str):
        with self.connect() as con:
            con.execute("BEGIN IMMEDIATE")
            row = con.execute(
                "SELECT generation FROM authorities WHERE principal=? AND scope_key=?",
                (principal,scope_key),
            ).fetchone()
            generation = 1 if row is None else int(row["generation"]) + 1
            if row is None:
                con.execute(
                    "INSERT INTO authorities(principal,scope_key,generation,active)"
                    " VALUES(?,?,?,0)", (principal,scope_key,generation)
                )
            else:
                con.execute(
                    "UPDATE authorities SET generation=?,active=0"
                    " WHERE principal=? AND scope_key=?",
                    (generation,principal,scope_key),
                )

            pending = con.execute(
                "SELECT effect_id,account_id,max_cost FROM attempts"
                " WHERE principal=? AND scope_key=? AND state='RESERVED'",
                (principal,scope_key),
            ).fetchall()
            for row2 in pending:
                con.execute(
                    "UPDATE accounts SET reserved=reserved-? WHERE account_id=?",
                    (int(row2["max_cost"]),row2["account_id"]),
                )
                con.execute(
                    "UPDATE attempts SET state='CANCELLED' WHERE effect_id=?",
                    (row2["effect_id"],),
                )
            seq = self._audit(
                con,"REVOKE",principal=principal,scope_key=scope_key,
                generation=generation,
                detail=f"revoked; cancelled={len(pending)}"
            )
            con.execute("COMMIT")
        return FinalityDecision(
            "REVOKED","authority-revoked",generation=generation,
            audit_sequence=seq
        )

    def put_evidence(self, evidence_key: str, subject_hash: str,
                     value_hash: str, status: str, updated_by="trusted-controller"):
        if status not in VALID_STATUSES:
            raise ValueError("invalid evidence status")
        with self.connect() as con:
            con.execute("BEGIN IMMEDIATE")
            row = con.execute(
                "SELECT version FROM evidence WHERE evidence_key=?",
                (evidence_key,),
            ).fetchone()
            version = 1 if row is None else int(row["version"]) + 1
            con.execute(
                "INSERT INTO evidence(evidence_key,version,subject_hash,value_hash,"
                "status,updated_by) VALUES(?,?,?,?,?,?)"
                " ON CONFLICT(evidence_key) DO UPDATE SET"
                " version=excluded.version,subject_hash=excluded.subject_hash,"
                " value_hash=excluded.value_hash,status=excluded.status,"
                " updated_by=excluded.updated_by",
                (evidence_key,version,subject_hash,value_hash,status,updated_by),
            )
            con.execute(
                "UPDATE evidence_meta SET value=value+1 WHERE key='global_epoch'"
            )
            epoch = int(con.execute(
                "SELECT value FROM evidence_meta WHERE key='global_epoch'"
            ).fetchone()[0])
            seq = self._audit(
                con,"EVIDENCE_UPDATE",evidence_key=evidence_key,
                detail=f"version={version};status={status};epoch={epoch}"
            )
            con.execute("COMMIT")
        return {
            "evidence_key": evidence_key,
            "version": version,
            "subject_hash": subject_hash,
            "value_hash": value_hash,
            "status": status,
            "global_epoch": epoch,
            "audit_sequence": seq,
        }

    def evidence_snapshot(self, evidence_key: str):
        with self.connect() as con:
            row = con.execute(
                "SELECT * FROM evidence WHERE evidence_key=?", (evidence_key,)
            ).fetchone()
        return dict(row) if row else None

    def global_evidence_epoch(self):
        with self.connect() as con:
            return int(con.execute(
                "SELECT value FROM evidence_meta WHERE key='global_epoch'"
            ).fetchone()[0])

    def snapshot(self, account_id: str):
        with self.connect() as con:
            row = con.execute(
                "SELECT * FROM accounts WHERE account_id=?", (account_id,)
            ).fetchone()
        if row is None:
            raise KeyError(account_id)
        spent = int(row["spent"])
        reserved = int(row["reserved"])
        committed = int(row["committed_pending"])
        limit_ = int(row["budget_limit"])
        return {
            "limit":limit_,"spent":spent,"reserved":reserved,
            "committed_pending":committed,
            "pressure":spent+reserved+committed,
            "available":limit_-spent-reserved-committed,
        }

    def invariant_holds(self, account_id: str):
        s = self.snapshot(account_id)
        return min(s["spent"],s["reserved"],s["committed_pending"]) >= 0 \
            and s["pressure"] <= s["limit"]

    @staticmethod
    def _requirement_satisfied(requirement: EvidenceRequirement, row):
        if row is None:
            return False
        if requirement.mode == "EXACT":
            # Admission snapshots are checked separately at finality.
            return row["status"] == "PASS"
        return (
            row["subject_hash"] == requirement.required_subject_hash
            and row["status"] == requirement.required_status
        )

    def _decision(self, state, reason, account_id, effect_id=None,
                  evidence_key=None, generation=None, audit_sequence=None):
        s = self.snapshot(account_id)
        return FinalityDecision(
            state,reason,effect_id=effect_id,evidence_key=evidence_key,
            generation=generation,limit=s["limit"],spent=s["spent"],
            reserved=s["reserved"],committed_pending=s["committed_pending"],
            audit_sequence=audit_sequence
        )

    def admit(self, principal: str, scope_key: str, account_id: str,
              action: Action, max_cost: int,
              requirements: Iterable[EvidenceRequirement]):
        reqs = tuple(requirements)
        if not reqs:
            raise ValueError("at least one evidence requirement is required")
        with self.connect() as con:
            con.execute("BEGIN IMMEDIATE")

            existing = con.execute(
                "SELECT * FROM attempts WHERE effect_id=?", (action.effect_id,)
            ).fetchone()
            if existing is not None:
                seq = self._audit(
                    con,"ADMIT_IDEMPOTENT",effect_id=action.effect_id,
                    account_id=existing["account_id"],
                    generation=int(existing["generation"]),
                    detail=f"existing state={existing['state']}"
                )
                state = existing["state"]
                con.execute("COMMIT")
                return self._decision(
                    state,"existing-attempt",existing["account_id"],
                    action.effect_id,generation=int(existing["generation"]),
                    audit_sequence=seq
                )

            auth = con.execute(
                "SELECT generation,active FROM authorities"
                " WHERE principal=? AND scope_key=?",
                (principal,scope_key),
            ).fetchone()
            if auth is None or not auth["active"]:
                seq = self._audit(
                    con,"ADMIT_DENY",effect_id=action.effect_id,
                    principal=principal,scope_key=scope_key,account_id=account_id,
                    detail="authority inactive"
                )
                con.execute("COMMIT")
                return self._decision(
                    "DENY","authority-inactive",account_id,action.effect_id,
                    audit_sequence=seq
                )

            account = con.execute(
                "SELECT * FROM accounts WHERE account_id=?", (account_id,)
            ).fetchone()
            if account is None:
                con.execute("ROLLBACK")
                raise KeyError(account_id)
            pressure = int(account["spent"])+int(account["reserved"])+int(account["committed_pending"])
            if pressure + max_cost > int(account["budget_limit"]):
                seq = self._audit(
                    con,"ADMIT_DENY",effect_id=action.effect_id,
                    account_id=account_id,detail="insufficient capacity"
                )
                con.execute("COMMIT")
                return self._decision(
                    "DENY","insufficient-capacity",account_id,action.effect_id,
                    audit_sequence=seq
                )

            evidence_rows = []
            for req in reqs:
                row = con.execute(
                    "SELECT * FROM evidence WHERE evidence_key=?",
                    (req.evidence_key,),
                ).fetchone()
                if not self._requirement_satisfied(req,row):
                    seq = self._audit(
                        con,"ADMIT_DENY",effect_id=action.effect_id,
                        evidence_key=req.evidence_key,account_id=account_id,
                        detail="evidence predicate not satisfied at admission"
                    )
                    con.execute("COMMIT")
                    return self._decision(
                        "DENY","evidence-not-satisfied",account_id,
                        action.effect_id,req.evidence_key,audit_sequence=seq
                    )
                evidence_rows.append((req,row))

            epoch = int(con.execute(
                "SELECT value FROM evidence_meta WHERE key='global_epoch'"
            ).fetchone()[0])
            generation = int(auth["generation"])
            con.execute(
                "INSERT INTO attempts(effect_id,principal,scope_key,account_id,"
                "generation,action_hash,max_cost,state,admitted_global_evidence_epoch)"
                " VALUES(?,?,?,?,?,?,?,'RESERVED',?)",
                (action.effect_id,principal,scope_key,account_id,generation,
                 action.action_hash,max_cost,epoch),
            )
            for req,row in evidence_rows:
                con.execute(
                    "INSERT INTO attempt_evidence(effect_id,evidence_key,mode,"
                    "admitted_version,admitted_subject_hash,admitted_value_hash,"
                    "admitted_status,required_subject_hash,required_status)"
                    " VALUES(?,?,?,?,?,?,?,?,?)",
                    (
                        action.effect_id,req.evidence_key,req.mode,
                        int(row["version"]),row["subject_hash"],row["value_hash"],
                        row["status"],req.required_subject_hash,req.required_status,
                    ),
                )
            con.execute(
                "UPDATE accounts SET reserved=reserved+? WHERE account_id=?",
                (max_cost,account_id),
            )
            seq = self._audit(
                con,"ADMIT_RESERVED",effect_id=action.effect_id,
                principal=principal,scope_key=scope_key,account_id=account_id,
                generation=generation,
                detail=f"bound evidence={len(evidence_rows)};epoch={epoch}"
            )
            con.execute("COMMIT")
        return self._decision(
            "RESERVED","admitted-with-evidence",account_id,action.effect_id,
            generation=generation,audit_sequence=seq
        )

    @staticmethod
    def _witness_still_valid(witness, current):
        if current is None:
            return False
        if witness["mode"] == "EXACT":
            return (
                int(current["version"]) == int(witness["admitted_version"])
                and current["subject_hash"] == witness["admitted_subject_hash"]
                and current["value_hash"] == witness["admitted_value_hash"]
                and current["status"] == witness["admitted_status"]
            )
        return (
            current["subject_hash"] == witness["required_subject_hash"]
            and current["status"] == witness["required_status"]
        )

    def commit(self, effect_id: str, action: Action, payload: dict):
        """One transaction re-checks authority + dependency evidence + resource,
        then creates the durable outbox.
        """
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
            generation = int(attempt["generation"])

            if attempt["action_hash"] != action.action_hash:
                seq = self._audit(
                    con,"COMMIT_DENY",effect_id=effect_id,account_id=account_id,
                    generation=generation,detail="action substitution"
                )
                con.execute("COMMIT")
                return self._decision(
                    "DENY","action-substitution",account_id,effect_id,
                    generation=generation,audit_sequence=seq
                )

            if attempt["state"] == "COMMITTED":
                seq = self._audit(
                    con,"COMMIT_IDEMPOTENT",effect_id=effect_id,
                    account_id=account_id,generation=generation,
                    detail="already final"
                )
                con.execute("COMMIT")
                return self._decision(
                    "COMMITTED","existing-finality",account_id,effect_id,
                    generation=generation,audit_sequence=seq
                )
            if attempt["state"] in ("CANCELLED","STALE_EVIDENCE"):
                seq = self._audit(
                    con,"COMMIT_DENY",effect_id=effect_id,
                    account_id=account_id,generation=generation,
                    detail=f"attempt state={attempt['state']}"
                )
                con.execute("COMMIT")
                return self._decision(
                    "DENY",attempt["state"].lower(),account_id,effect_id,
                    generation=generation,audit_sequence=seq
                )

            auth = con.execute(
                "SELECT generation,active FROM authorities"
                " WHERE principal=? AND scope_key=?",
                (attempt["principal"],attempt["scope_key"]),
            ).fetchone()
            if auth is None or not auth["active"] or int(auth["generation"]) != generation:
                con.execute(
                    "UPDATE accounts SET reserved=reserved-? WHERE account_id=?",
                    (max_cost,account_id),
                )
                con.execute(
                    "UPDATE attempts SET state='CANCELLED' WHERE effect_id=?",
                    (effect_id,),
                )
                seq = self._audit(
                    con,"COMMIT_DENY",effect_id=effect_id,
                    account_id=account_id,generation=generation,
                    detail="authority not live at finality"
                )
                con.execute("COMMIT")
                return self._decision(
                    "DENY","authority-not-live-at-finality",
                    account_id,effect_id,generation=generation,audit_sequence=seq
                )

            witnesses = con.execute(
                "SELECT * FROM attempt_evidence WHERE effect_id=?"
                " ORDER BY evidence_key", (effect_id,)
            ).fetchall()
            for witness in witnesses:
                current = con.execute(
                    "SELECT * FROM evidence WHERE evidence_key=?",
                    (witness["evidence_key"],),
                ).fetchone()
                if not self._witness_still_valid(witness,current):
                    con.execute(
                        "UPDATE accounts SET reserved=reserved-? WHERE account_id=?",
                        (max_cost,account_id),
                    )
                    con.execute(
                        "UPDATE attempts SET state='STALE_EVIDENCE' WHERE effect_id=?",
                        (effect_id,),
                    )
                    seq = self._audit(
                        con,"EVIDENCE_STALE",effect_id=effect_id,
                        evidence_key=witness["evidence_key"],
                        account_id=account_id,generation=generation,
                        detail=(
                            f"mode={witness['mode']};"
                            f"admitted_v={witness['admitted_version']};"
                            f"current_v={None if current is None else current['version']}"
                        )
                    )
                    con.execute("COMMIT")
                    return self._decision(
                        "DENY","evidence-stale-at-finality",
                        account_id,effect_id,witness["evidence_key"],
                        generation,audit_sequence=seq
                    )

            con.execute(
                "UPDATE accounts SET reserved=reserved-?,"
                " committed_pending=committed_pending+? WHERE account_id=?",
                (max_cost,max_cost,account_id),
            )
            con.execute(
                "UPDATE attempts SET state='COMMITTED' WHERE effect_id=?",
                (effect_id,),
            )
            con.execute(
                "INSERT INTO outbox(effect_id,action_hash,payload_json,state)"
                " VALUES(?,?,?,'PENDING')",
                (effect_id,action.action_hash,json.dumps(payload,sort_keys=True)),
            )
            seq = self._audit(
                con,"FINALITY_COMMIT",effect_id=effect_id,
                principal=attempt["principal"],scope_key=attempt["scope_key"],
                account_id=account_id,generation=generation,
                detail=f"evidence_rechecked={len(witnesses)}"
            )
            con.execute("COMMIT")
        return self._decision(
            "COMMITTED","evidence-fresh-at-finality",
            account_id,effect_id,generation=generation,audit_sequence=seq
        )

    def outbox_row(self,effect_id):
        with self.connect() as con:
            row = con.execute(
                "SELECT * FROM outbox WHERE effect_id=?", (effect_id,)
            ).fetchone()
        return dict(row) if row else None

    def audit(self):
        with self.connect() as con:
            return [dict(r) for r in con.execute(
                "SELECT * FROM audit ORDER BY sequence"
            ).fetchall()]


class AdmissionOnlyEvidenceBaseline:
    """Weak baseline reproducing the old temporal gap."""
    def __init__(self):
        self.admitted = set()

    def admit(self,effect_id,current_predicate: bool):
        if current_predicate:
            self.admitted.add(effect_id)
            return True
        return False

    def commit(self,effect_id):
        return effect_id in self.admitted


class GlobalEpochFreshnessBaseline:
    """Safe but coarse: any evidence update invalidates every admitted action."""
    def __init__(self):
        self.epoch = 0
        self.admitted = {}

    def update(self):
        self.epoch += 1

    def admit(self,effect_id):
        self.admitted[effect_id] = self.epoch
        return True

    def commit(self,effect_id):
        return self.admitted.get(effect_id) == self.epoch


class ConventionalDependencyOracle:
    """Independent pure semantic state machine for bounded traces."""
    def __init__(self):
        self.required = {
            "version":1,"subject":"A","value":"tests-1","status":"PASS"
        }
        self.unrelated_version = 1
        self.active = True
        self.generation = 1
        self.state = None
        self.admitted = None
        self.outbox = False

    def admit(self):
        if self.state is not None:
            return self.state
        if not self.active:
            return "DENY"
        if self.required["subject"] != "A" or self.required["status"] != "PASS":
            return "DENY"
        self.state = "RESERVED"
        self.admitted = {
            "generation":self.generation,
            "required_subject":"A",
            "required_status":"PASS",
        }
        return "RESERVED"

    def required_fail(self):
        self.required["version"] += 1
        self.required["status"] = "FAIL"

    def required_equivalent_pass(self):
        self.required["version"] += 1
        self.required["value"] = f"tests-{self.required['version']}"
        self.required["status"] = "PASS"
        self.required["subject"] = "A"

    def subject_change(self):
        self.required["version"] += 1
        self.required["subject"] = "B"
        self.required["status"] = "PASS"

    def unrelated_change(self):
        self.unrelated_version += 1

    def commit(self):
        if self.state == "COMMITTED":
            return "COMMITTED"
        if self.state in ("CANCELLED","STALE_EVIDENCE"):
            return "DENY"
        if self.state is None:
            return "MISSING"
        if not self.active or self.generation != self.admitted["generation"]:
            self.state = "CANCELLED"
            return "DENY"
        if (
            self.required["subject"] != self.admitted["required_subject"]
            or self.required["status"] != self.admitted["required_status"]
        ):
            self.state = "STALE_EVIDENCE"
            return "DENY"
        self.state = "COMMITTED"
        self.outbox = True
        return "COMMITTED"
