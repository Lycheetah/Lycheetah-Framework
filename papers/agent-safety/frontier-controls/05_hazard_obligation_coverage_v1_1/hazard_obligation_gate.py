#!/usr/bin/env python3
"""
Lycheetah Hazard Obligation Coverage Gate v1.1

Purpose
-------
Close the "fresh but incomplete evidence" gap.

The caller does NOT supply the list of safety checks. Instead, a protected policy
for the effect class defines mandatory obligation groups. Every group must be
satisfied at admission and again at finality.

Each group is OR over allowed controls; policy is AND over groups.

    SAFE(policy, action, E)
      iff  forall group g in policy:
              exists obligation o in g:
                  predicate(o, action, E) = true

This is ordinary closed-world checklist / hazard-derived safety-requirement
enforcement. Novelty is not claimed. The Lycheetah contribution in this packet
is composition with exact action identity, authority generation, resource
reservation, policy-version binding, finality recheck, and durable outbox intent.

Concrete use case
-----------------
Production deployment of artifact A.

Example mandatory hazard-control groups:
  G_TESTS      : required CI PASS for A
  G_SECURITY   : security scan PASS for A
  G_REVERSIBLE : rollback plan PASS for A OR blue/green reversibility PASS for A
  G_CANARY     : canary health PASS for A

A model cannot omit G_SECURITY from its request, because the request never
chooses the policy obligations.

Limits
------
Completeness is relative to the declared policy. Unknown/omitted hazards in the
policy itself remain unknown/omitted.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
from typing import Iterable


VALID_STATUS = {"PASS", "FAIL", "UNKNOWN"}


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
        raw = json.dumps({
            "principal": self.principal,
            "tool": self.tool,
            "operation": self.operation,
            "object_id": self.object_id,
            "destination": self.destination,
            "arguments": self.arguments,
            "effect_id": self.effect_id,
        }, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return sha256(raw).hexdigest()


@dataclass(frozen=True)
class Obligation:
    group_id: str
    obligation_id: str
    hazard_id: str
    evidence_key: str
    required_status: str = "PASS"
    bind_subject_to_action_object: bool = True

    def __post_init__(self):
        if self.required_status not in VALID_STATUS:
            raise ValueError("invalid required status")


@dataclass(frozen=True)
class GateDecision:
    state: str
    reason: str
    effect_id: str | None = None
    group_id: str | None = None
    policy_version: int | None = None
    generation: int | None = None
    spent: int | None = None
    reserved: int | None = None
    committed_pending: int | None = None
    limit: int | None = None
    audit_sequence: int | None = None


class HazardObligationGate:
    def __init__(self, db_path: str | Path):
        self.db_path = str(db_path)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def connect(self):
        con = sqlite3.connect(self.db_path, timeout=30, isolation_level=None)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA journal_mode=WAL")
        con.execute("PRAGMA synchronous=FULL")
        con.execute("PRAGMA foreign_keys=ON")
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
                status TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS policies(
                effect_class TEXT NOT NULL,
                version INTEGER NOT NULL,
                active INTEGER NOT NULL CHECK(active IN (0,1)),
                PRIMARY KEY(effect_class, version)
            );

            CREATE TABLE IF NOT EXISTS obligations(
                effect_class TEXT NOT NULL,
                policy_version INTEGER NOT NULL,
                group_id TEXT NOT NULL,
                obligation_id TEXT NOT NULL,
                hazard_id TEXT NOT NULL,
                evidence_key TEXT NOT NULL,
                required_status TEXT NOT NULL,
                bind_subject_to_action_object INTEGER NOT NULL CHECK(bind_subject_to_action_object IN (0,1)),
                PRIMARY KEY(effect_class, policy_version, obligation_id),
                FOREIGN KEY(effect_class, policy_version)
                  REFERENCES policies(effect_class, version)
            );

            CREATE TABLE IF NOT EXISTS attempts(
                effect_id TEXT PRIMARY KEY,
                principal TEXT NOT NULL,
                scope_key TEXT NOT NULL,
                account_id TEXT NOT NULL,
                effect_class TEXT NOT NULL,
                policy_version INTEGER NOT NULL,
                generation INTEGER NOT NULL,
                action_hash TEXT NOT NULL,
                action_object_id TEXT NOT NULL,
                max_cost INTEGER NOT NULL CHECK(max_cost >= 0),
                state TEXT NOT NULL
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
                effect_class TEXT,
                policy_version INTEGER,
                group_id TEXT,
                principal TEXT,
                scope_key TEXT,
                account_id TEXT,
                generation INTEGER,
                detail TEXT NOT NULL
            );
            """)

    def _audit(self, con, kind, *, effect_id=None, effect_class=None,
               policy_version=None, group_id=None, principal=None,
               scope_key=None, account_id=None, generation=None, detail=""):
        cur = con.execute(
            "INSERT INTO audit(kind,effect_id,effect_class,policy_version,group_id,"
            "principal,scope_key,account_id,generation,detail)"
            " VALUES(?,?,?,?,?,?,?,?,?,?)",
            (kind,effect_id,effect_class,policy_version,group_id,principal,
             scope_key,account_id,generation,detail),
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
                raise ValueError("account exists with different budget")
            con.execute("COMMIT")

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
            "limit": limit_,
            "spent": spent,
            "reserved": reserved,
            "committed_pending": committed,
            "pressure": spent + reserved + committed,
            "available": limit_ - spent - reserved - committed,
        }

    def invariant_holds(self, account_id: str):
        s = self.snapshot(account_id)
        return (
            min(s["spent"],s["reserved"],s["committed_pending"]) >= 0
            and s["pressure"] <= s["limit"]
        )

    def _decision(self, state, reason, account_id, *, effect_id=None,
                  group_id=None, policy_version=None, generation=None,
                  audit_sequence=None):
        s = self.snapshot(account_id)
        return GateDecision(
            state=state,reason=reason,effect_id=effect_id,group_id=group_id,
            policy_version=policy_version,generation=generation,
            spent=s["spent"],reserved=s["reserved"],
            committed_pending=s["committed_pending"],limit=s["limit"],
            audit_sequence=audit_sequence,
        )

    def activate_authority(self, principal: str, scope_key: str):
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
            con.execute("COMMIT")
        return generation

    def revoke_authority(self, principal: str, scope_key: str):
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
            for p in pending:
                con.execute(
                    "UPDATE accounts SET reserved=reserved-? WHERE account_id=?",
                    (int(p["max_cost"]),p["account_id"]),
                )
                con.execute(
                    "UPDATE attempts SET state='CANCELLED' WHERE effect_id=?",
                    (p["effect_id"],),
                )
            con.execute("COMMIT")
        return generation

    def put_evidence(self, evidence_key: str, subject_hash: str, status: str):
        if status not in VALID_STATUS:
            raise ValueError("invalid status")
        with self.connect() as con:
            con.execute("BEGIN IMMEDIATE")
            row = con.execute(
                "SELECT version FROM evidence WHERE evidence_key=?",
                (evidence_key,),
            ).fetchone()
            version = 1 if row is None else int(row["version"]) + 1
            con.execute(
                "INSERT INTO evidence(evidence_key,version,subject_hash,status)"
                " VALUES(?,?,?,?)"
                " ON CONFLICT(evidence_key) DO UPDATE SET"
                " version=excluded.version,subject_hash=excluded.subject_hash,"
                " status=excluded.status",
                (evidence_key,version,subject_hash,status),
            )
            con.execute("COMMIT")
        return version

    def install_policy(self, effect_class: str, version: int,
                       obligations: Iterable[Obligation]):
        obligations = tuple(obligations)
        if not obligations:
            raise ValueError("policy requires at least one obligation")
        groups = {o.group_id for o in obligations}
        if not groups:
            raise ValueError("policy requires groups")
        with self.connect() as con:
            con.execute("BEGIN IMMEDIATE")
            con.execute(
                "UPDATE policies SET active=0 WHERE effect_class=?",
                (effect_class,),
            )
            con.execute(
                "INSERT INTO policies(effect_class,version,active) VALUES(?,?,1)",
                (effect_class,version),
            )
            for o in obligations:
                con.execute(
                    "INSERT INTO obligations(effect_class,policy_version,group_id,"
                    "obligation_id,hazard_id,evidence_key,required_status,"
                    "bind_subject_to_action_object) VALUES(?,?,?,?,?,?,?,?)",
                    (
                        effect_class,version,o.group_id,o.obligation_id,o.hazard_id,
                        o.evidence_key,o.required_status,
                        int(o.bind_subject_to_action_object),
                    ),
                )
            self._audit(
                con,"POLICY_INSTALL",effect_class=effect_class,
                policy_version=version,
                detail=f"groups={len(groups)};obligations={len(obligations)}"
            )
            con.execute("COMMIT")

    def active_policy_version(self, con, effect_class: str):
        row = con.execute(
            "SELECT version FROM policies WHERE effect_class=? AND active=1",
            (effect_class,),
        ).fetchone()
        return None if row is None else int(row["version"])

    def _obligation_rows(self, con, effect_class: str, version: int):
        return con.execute(
            "SELECT * FROM obligations WHERE effect_class=? AND policy_version=?"
            " ORDER BY group_id,obligation_id",
            (effect_class,version),
        ).fetchall()

    @staticmethod
    def _obligation_true(row, evidence_row, action_object_id):
        if evidence_row is None:
            return False
        if evidence_row["status"] != row["required_status"]:
            return False
        if row["bind_subject_to_action_object"]:
            return evidence_row["subject_hash"] == action_object_id
        return True

    def _evaluate_policy(self, con, effect_class: str, version: int,
                         action_object_id: str):
        obligations = self._obligation_rows(con,effect_class,version)
        if not obligations:
            return False, "NO_POLICY_OBLIGATIONS", None, {}

        groups = {}
        detail = {}
        for o in obligations:
            groups.setdefault(o["group_id"], []).append(o)

        for group_id, rows in groups.items():
            satisfied = False
            observed = []
            for row in rows:
                ev = con.execute(
                    "SELECT * FROM evidence WHERE evidence_key=?",
                    (row["evidence_key"],),
                ).fetchone()
                ok = self._obligation_true(row,ev,action_object_id)
                observed.append({
                    "obligation_id":row["obligation_id"],
                    "hazard_id":row["hazard_id"],
                    "evidence_key":row["evidence_key"],
                    "satisfied":ok,
                    "current_status":None if ev is None else ev["status"],
                    "current_subject":None if ev is None else ev["subject_hash"],
                })
                satisfied = satisfied or ok
            detail[group_id] = observed
            if not satisfied:
                return False, "UNSATISFIED_GROUP", group_id, detail
        return True, "ALL_GROUPS_SATISFIED", None, detail

    def admit(self, principal: str, scope_key: str, account_id: str,
              effect_class: str, action: Action, max_cost: int):
        with self.connect() as con:
            con.execute("BEGIN IMMEDIATE")

            existing = con.execute(
                "SELECT * FROM attempts WHERE effect_id=?", (action.effect_id,)
            ).fetchone()
            if existing is not None:
                seq = self._audit(
                    con,"ADMIT_IDEMPOTENT",effect_id=action.effect_id,
                    effect_class=existing["effect_class"],
                    policy_version=int(existing["policy_version"]),
                    account_id=existing["account_id"],
                    generation=int(existing["generation"]),
                    detail=f"existing state={existing['state']}"
                )
                state = existing["state"]
                con.execute("COMMIT")
                return self._decision(
                    state,"existing-attempt",existing["account_id"],
                    effect_id=action.effect_id,
                    policy_version=int(existing["policy_version"]),
                    generation=int(existing["generation"]),
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
                    effect_class=effect_class,principal=principal,
                    scope_key=scope_key,account_id=account_id,
                    detail="authority inactive"
                )
                con.execute("COMMIT")
                return self._decision(
                    "DENY","authority-inactive",account_id,
                    effect_id=action.effect_id,audit_sequence=seq
                )

            version = self.active_policy_version(con,effect_class)
            if version is None:
                seq = self._audit(
                    con,"ADMIT_DENY",effect_id=action.effect_id,
                    effect_class=effect_class,account_id=account_id,
                    detail="no active policy"
                )
                con.execute("COMMIT")
                return self._decision(
                    "DENY","no-active-policy",account_id,
                    effect_id=action.effect_id,audit_sequence=seq
                )

            ok,reason,bad_group,_ = self._evaluate_policy(
                con,effect_class,version,action.object_id
            )
            if not ok:
                seq = self._audit(
                    con,"OBLIGATION_DENY",effect_id=action.effect_id,
                    effect_class=effect_class,policy_version=version,
                    group_id=bad_group,account_id=account_id,
                    detail="mandatory hazard-control group unsatisfied at admission"
                )
                con.execute("COMMIT")
                return self._decision(
                    "DENY","mandatory-obligation-unsatisfied",account_id,
                    effect_id=action.effect_id,group_id=bad_group,
                    policy_version=version,audit_sequence=seq
                )

            account = con.execute(
                "SELECT * FROM accounts WHERE account_id=?", (account_id,)
            ).fetchone()
            if account is None:
                con.execute("ROLLBACK")
                raise KeyError(account_id)
            pressure = (
                int(account["spent"])+int(account["reserved"])
                +int(account["committed_pending"])
            )
            if pressure + max_cost > int(account["budget_limit"]):
                seq = self._audit(
                    con,"ADMIT_DENY",effect_id=action.effect_id,
                    effect_class=effect_class,policy_version=version,
                    account_id=account_id,detail="insufficient capacity"
                )
                con.execute("COMMIT")
                return self._decision(
                    "DENY","insufficient-capacity",account_id,
                    effect_id=action.effect_id,policy_version=version,
                    audit_sequence=seq
                )

            generation = int(auth["generation"])
            con.execute(
                "INSERT INTO attempts(effect_id,principal,scope_key,account_id,"
                "effect_class,policy_version,generation,action_hash,"
                "action_object_id,max_cost,state)"
                " VALUES(?,?,?,?,?,?,?,?,?,?,'RESERVED')",
                (
                    action.effect_id,principal,scope_key,account_id,effect_class,
                    version,generation,action.action_hash,action.object_id,max_cost,
                ),
            )
            con.execute(
                "UPDATE accounts SET reserved=reserved+? WHERE account_id=?",
                (max_cost,account_id),
            )
            seq = self._audit(
                con,"ADMIT_RESERVED",effect_id=action.effect_id,
                effect_class=effect_class,policy_version=version,
                principal=principal,scope_key=scope_key,account_id=account_id,
                generation=generation,
                detail="all mandatory groups satisfied; resource reserved"
            )
            con.execute("COMMIT")
        return self._decision(
            "RESERVED","closed-world-policy-satisfied",account_id,
            effect_id=action.effect_id,policy_version=version,
            generation=generation,audit_sequence=seq
        )

    def commit(self, effect_id: str, action: Action, payload: dict):
        with self.connect() as con:
            con.execute("BEGIN IMMEDIATE")
            attempt = con.execute(
                "SELECT * FROM attempts WHERE effect_id=?", (effect_id,)
            ).fetchone()
            if attempt is None:
                con.execute("ROLLBACK")
                raise KeyError(effect_id)

            account_id = attempt["account_id"]
            version = int(attempt["policy_version"])
            generation = int(attempt["generation"])
            max_cost = int(attempt["max_cost"])
            effect_class = attempt["effect_class"]

            if attempt["action_hash"] != action.action_hash:
                seq = self._audit(
                    con,"COMMIT_DENY",effect_id=effect_id,
                    effect_class=effect_class,policy_version=version,
                    account_id=account_id,generation=generation,
                    detail="action substitution"
                )
                con.execute("COMMIT")
                return self._decision(
                    "DENY","action-substitution",account_id,effect_id=effect_id,
                    policy_version=version,generation=generation,
                    audit_sequence=seq
                )

            if attempt["state"] == "COMMITTED":
                seq = self._audit(
                    con,"COMMIT_IDEMPOTENT",effect_id=effect_id,
                    effect_class=effect_class,policy_version=version,
                    account_id=account_id,generation=generation,
                    detail="already committed"
                )
                con.execute("COMMIT")
                return self._decision(
                    "COMMITTED","existing-finality",account_id,effect_id=effect_id,
                    policy_version=version,generation=generation,
                    audit_sequence=seq
                )

            if attempt["state"] in ("CANCELLED","POLICY_STALE","OBLIGATION_STALE"):
                seq = self._audit(
                    con,"COMMIT_DENY",effect_id=effect_id,
                    effect_class=effect_class,policy_version=version,
                    account_id=account_id,generation=generation,
                    detail=f"attempt state={attempt['state']}"
                )
                con.execute("COMMIT")
                return self._decision(
                    "DENY",attempt["state"].lower(),account_id,effect_id=effect_id,
                    policy_version=version,generation=generation,
                    audit_sequence=seq
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
                    effect_class=effect_class,policy_version=version,
                    account_id=account_id,generation=generation,
                    detail="authority not live at finality"
                )
                con.execute("COMMIT")
                return self._decision(
                    "DENY","authority-not-live-at-finality",account_id,
                    effect_id=effect_id,policy_version=version,generation=generation,
                    audit_sequence=seq
                )

            active_version = self.active_policy_version(con,effect_class)
            if active_version != version:
                con.execute(
                    "UPDATE accounts SET reserved=reserved-? WHERE account_id=?",
                    (max_cost,account_id),
                )
                con.execute(
                    "UPDATE attempts SET state='POLICY_STALE' WHERE effect_id=?",
                    (effect_id,),
                )
                seq = self._audit(
                    con,"POLICY_STALE",effect_id=effect_id,
                    effect_class=effect_class,policy_version=version,
                    account_id=account_id,generation=generation,
                    detail=f"active_version={active_version}"
                )
                con.execute("COMMIT")
                return self._decision(
                    "DENY","policy-version-changed",account_id,effect_id=effect_id,
                    policy_version=version,generation=generation,
                    audit_sequence=seq
                )

            ok,reason,bad_group,_ = self._evaluate_policy(
                con,effect_class,version,attempt["action_object_id"]
            )
            if not ok:
                con.execute(
                    "UPDATE accounts SET reserved=reserved-? WHERE account_id=?",
                    (max_cost,account_id),
                )
                con.execute(
                    "UPDATE attempts SET state='OBLIGATION_STALE' WHERE effect_id=?",
                    (effect_id,),
                )
                seq = self._audit(
                    con,"OBLIGATION_STALE",effect_id=effect_id,
                    effect_class=effect_class,policy_version=version,
                    group_id=bad_group,account_id=account_id,generation=generation,
                    detail="mandatory hazard-control group unsatisfied at finality"
                )
                con.execute("COMMIT")
                return self._decision(
                    "DENY","mandatory-obligation-unsatisfied-at-finality",
                    account_id,effect_id=effect_id,group_id=bad_group,
                    policy_version=version,generation=generation,
                    audit_sequence=seq
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
                effect_class=effect_class,policy_version=version,
                account_id=account_id,generation=generation,
                detail="all mandatory hazard-control groups satisfied at finality"
            )
            con.execute("COMMIT")

        return self._decision(
            "COMMITTED","hazard-obligations-covered-at-finality",account_id,
            effect_id=effect_id,policy_version=version,generation=generation,
            audit_sequence=seq
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


class PresentedEvidenceBaseline:
    """Weak baseline: caller presents any subset of passing checks.

    If every presented item passes and at least one item exists, it allows.
    It has no protected knowledge of omitted mandatory obligations.
    """
    @staticmethod
    def allow(presented_statuses: Iterable[str]):
        statuses = tuple(presented_statuses)
        return bool(statuses) and all(x == "PASS" for x in statuses)


class ConventionalChecklistOracle:
    """Independent closed-world conventional checklist.

    Mandatory groups:
      tests = T
      security = S
      reversible = R or B
      canary = C
    """
    @staticmethod
    def allow(T,S,R,B,C):
        return bool(T and S and C and (R or B))
