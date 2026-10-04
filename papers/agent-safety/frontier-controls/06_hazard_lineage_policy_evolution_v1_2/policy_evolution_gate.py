#!/usr/bin/env python3
"""
Lycheetah Hazard Lineage + Policy Evolution Gate v1.2

Problem:
    A runtime can perfectly enforce an incomplete or accidentally weakened
    policy. Safety-relevant policy changes need change-impact analysis.

This prototype protects policy evolution with:
  1. semantic monotonicity analysis over closed-world obligation formulas;
  2. incident -> hazard -> control-group traceability;
  3. frozen regression scenarios;
  4. policy-version activation only after those checks pass.

Policy semantics:
    AND over mandatory groups.
    OR over alternative obligations within each group.

Automatic activation rule in v1.2:
    - EQUIVALENT or STRONGER policy relative to active version;
    - every HIGH/CRITICAL incident is mapped to a group in the candidate whose
      obligations trace to that incident's hazard;
    - every frozen regression fixture passes.

WEAKER or INCOMPARABLE changes are STOPPED for explicit external review.
This is intentionally conservative. Safe retirement/replacement of controls is
not automated in this prototype.

This is conventional management-of-change / safety-case maintenance machinery,
not claimed as a novel safety-analysis method.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import sqlite3
from typing import Iterable


@dataclass(frozen=True)
class Obligation:
    obligation_id: str
    hazard_id: str
    evidence_key: str


@dataclass(frozen=True)
class Group:
    group_id: str
    obligations: tuple[Obligation, ...]


@dataclass(frozen=True)
class Policy:
    policy_id: str
    version: int
    groups: tuple[Group, ...]


@dataclass(frozen=True)
class EvolutionDecision:
    state: str
    reason: str
    relation: str | None = None
    policy_id: str | None = None
    version: int | None = None
    failing_fixture: str | None = None
    incident_id: str | None = None


def policy_formula(policy: Policy, truth: dict[str, bool]) -> bool:
    """AND(groups), OR(obligations in group)."""
    return all(
        bool(group.obligations)
        and any(bool(truth.get(o.obligation_id, False)) for o in group.obligations)
        for group in policy.groups
    )


def group_map(policy: Policy):
    return {
        g.group_id: frozenset(o.obligation_id for o in g.obligations)
        for g in policy.groups
    }


def semantic_relation_structural(old: Policy, new: Policy) -> str:
    """Exact structural implication classifier for AND-of-OR formulas when
    obligation IDs are atomic booleans.

    STRONGER: new => old, but old !=> new
    WEAKER: old => new, but new !=> old
    EQUIVALENT: both
    INCOMPARABLE: neither
    """
    oldm = group_map(old)
    newm = group_map(new)
    weakening = False
    strengthening = False

    all_groups = set(oldm) | set(newm)
    for gid in all_groups:
        o = oldm.get(gid)
        n = newm.get(gid)
        if o is None and n is not None:
            # added conjunct
            strengthening = True
        elif o is not None and n is None:
            # removed conjunct
            weakening = True
        else:
            assert o is not None and n is not None
            if n == o:
                continue
            if n.issuperset(o):
                # more alternatives -> easier to satisfy
                weakening = True
            elif n.issubset(o):
                # fewer alternatives -> harder to satisfy
                strengthening = True
            else:
                # replacement/mixed alternatives
                weakening = True
                strengthening = True

    if weakening and strengthening:
        return "INCOMPARABLE"
    if weakening:
        return "WEAKER"
    if strengthening:
        return "STRONGER"
    return "EQUIVALENT"


class PolicyEvolutionGate:
    def __init__(self, db_path: str | Path):
        self.db_path = str(db_path)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def connect(self):
        con = sqlite3.connect(self.db_path, timeout=20, isolation_level=None)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA journal_mode=WAL")
        con.execute("PRAGMA synchronous=FULL")
        return con

    def _init_db(self):
        with self.connect() as con:
            con.executescript("""
            CREATE TABLE IF NOT EXISTS policies(
                policy_id TEXT NOT NULL,
                version INTEGER NOT NULL,
                policy_json TEXT NOT NULL,
                state TEXT NOT NULL,
                relation_to_previous TEXT,
                PRIMARY KEY(policy_id,version)
            );

            CREATE TABLE IF NOT EXISTS active_policy(
                policy_id TEXT PRIMARY KEY,
                version INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS incidents(
                incident_id TEXT PRIMARY KEY,
                hazard_id TEXT NOT NULL,
                severity TEXT NOT NULL,
                description TEXT NOT NULL,
                mapped_group_id TEXT,
                state TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS fixtures(
                fixture_id TEXT PRIMARY KEY,
                policy_id TEXT NOT NULL,
                truth_json TEXT NOT NULL,
                expected_allow INTEGER NOT NULL CHECK(expected_allow IN (0,1)),
                source TEXT NOT NULL,
                active INTEGER NOT NULL CHECK(active IN (0,1))
            );

            CREATE TABLE IF NOT EXISTS audit(
                sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                kind TEXT NOT NULL,
                policy_id TEXT,
                version INTEGER,
                incident_id TEXT,
                detail TEXT NOT NULL
            );
            """)

    def _audit(self, con, kind, *, policy_id=None, version=None,
               incident_id=None, detail=""):
        con.execute(
            "INSERT INTO audit(kind,policy_id,version,incident_id,detail)"
            " VALUES(?,?,?,?,?)",
            (kind,policy_id,version,incident_id,detail),
        )

    @staticmethod
    def _encode_policy(policy: Policy):
        return json.dumps({
            "policy_id": policy.policy_id,
            "version": policy.version,
            "groups": [
                {
                    "group_id": g.group_id,
                    "obligations": [
                        {
                            "obligation_id": o.obligation_id,
                            "hazard_id": o.hazard_id,
                            "evidence_key": o.evidence_key,
                        }
                        for o in g.obligations
                    ],
                }
                for g in policy.groups
            ],
        }, sort_keys=True)

    @staticmethod
    def _decode_policy(raw: str) -> Policy:
        d = json.loads(raw)
        return Policy(
            d["policy_id"], int(d["version"]),
            tuple(
                Group(
                    g["group_id"],
                    tuple(
                        Obligation(
                            o["obligation_id"], o["hazard_id"], o["evidence_key"]
                        )
                        for o in g["obligations"]
                    ),
                )
                for g in d["groups"]
            ),
        )

    def active(self, policy_id: str):
        with self.connect() as con:
            row = con.execute(
                "SELECT p.policy_json FROM active_policy a"
                " JOIN policies p ON p.policy_id=a.policy_id AND p.version=a.version"
                " WHERE a.policy_id=?", (policy_id,)
            ).fetchone()
        return None if row is None else self._decode_policy(row["policy_json"])

    def install_initial(self, policy: Policy):
        if not policy.groups:
            raise ValueError("policy must have groups")
        with self.connect() as con:
            con.execute("BEGIN IMMEDIATE")
            if con.execute(
                "SELECT 1 FROM active_policy WHERE policy_id=?", (policy.policy_id,)
            ).fetchone():
                con.execute("ROLLBACK")
                raise ValueError("active policy already exists")
            con.execute(
                "INSERT INTO policies(policy_id,version,policy_json,state,"
                "relation_to_previous) VALUES(?,?,?,'ACTIVE','INITIAL')",
                (policy.policy_id,policy.version,self._encode_policy(policy)),
            )
            con.execute(
                "INSERT INTO active_policy(policy_id,version) VALUES(?,?)",
                (policy.policy_id,policy.version),
            )
            self._audit(
                con,"INITIAL_POLICY",policy_id=policy.policy_id,
                version=policy.version,detail="initial policy installed"
            )
            con.execute("COMMIT")

    def record_incident(self, incident_id: str, hazard_id: str,
                        severity: str, description: str):
        if severity not in {"LOW","MEDIUM","HIGH","CRITICAL"}:
            raise ValueError("invalid severity")
        with self.connect() as con:
            con.execute("BEGIN IMMEDIATE")
            con.execute(
                "INSERT INTO incidents(incident_id,hazard_id,severity,description,"
                "mapped_group_id,state) VALUES(?,?,?,?,NULL,'OPEN')",
                (incident_id,hazard_id,severity,description),
            )
            self._audit(
                con,"INCIDENT",incident_id=incident_id,
                detail=f"hazard={hazard_id};severity={severity}"
            )
            con.execute("COMMIT")

    def map_incident(self, incident_id: str, group_id: str):
        with self.connect() as con:
            con.execute("BEGIN IMMEDIATE")
            row = con.execute(
                "SELECT 1 FROM incidents WHERE incident_id=?", (incident_id,)
            ).fetchone()
            if row is None:
                con.execute("ROLLBACK")
                raise KeyError(incident_id)
            con.execute(
                "UPDATE incidents SET mapped_group_id=?,state='MAPPED'"
                " WHERE incident_id=?",
                (group_id,incident_id),
            )
            self._audit(
                con,"INCIDENT_MAP",incident_id=incident_id,
                detail=f"group={group_id}"
            )
            con.execute("COMMIT")

    def add_fixture(self, fixture_id: str, policy_id: str,
                    truth: dict[str,bool], expected_allow: bool,
                    source: str):
        with self.connect() as con:
            con.execute(
                "INSERT INTO fixtures(fixture_id,policy_id,truth_json,"
                "expected_allow,source,active) VALUES(?,?,?,?,?,1)",
                (
                    fixture_id,policy_id,json.dumps(truth,sort_keys=True),
                    int(expected_allow),source,
                ),
            )

    def propose(self, candidate: Policy):
        current = self.active(candidate.policy_id)
        if current is None:
            raise ValueError("no active policy")
        if candidate.version <= current.version:
            raise ValueError("candidate version must increase")
        relation = semantic_relation_structural(current,candidate)
        with self.connect() as con:
            con.execute("BEGIN IMMEDIATE")
            con.execute(
                "INSERT INTO policies(policy_id,version,policy_json,state,"
                "relation_to_previous) VALUES(?,?,?,'PROPOSED',?)",
                (
                    candidate.policy_id,candidate.version,
                    self._encode_policy(candidate),relation,
                ),
            )
            self._audit(
                con,"PROPOSE",policy_id=candidate.policy_id,
                version=candidate.version,
                detail=f"relation={relation}"
            )
            con.execute("COMMIT")
        return relation

    def _candidate(self, policy_id, version):
        with self.connect() as con:
            row = con.execute(
                "SELECT policy_json FROM policies WHERE policy_id=? AND version=?",
                (policy_id,version),
            ).fetchone()
        if row is None:
            raise KeyError((policy_id,version))
        return self._decode_policy(row["policy_json"])

    @staticmethod
    def _hazards_by_group(policy: Policy):
        return {
            g.group_id: frozenset(o.hazard_id for o in g.obligations)
            for g in policy.groups
        }

    def evaluate_fixtures(self, candidate: Policy):
        failures = []
        with self.connect() as con:
            rows = con.execute(
                "SELECT * FROM fixtures WHERE policy_id=? AND active=1"
                " ORDER BY fixture_id", (candidate.policy_id,)
            ).fetchall()
        for row in rows:
            truth = json.loads(row["truth_json"])
            observed = policy_formula(candidate, truth)
            expected = bool(row["expected_allow"])
            if observed != expected:
                failures.append({
                    "fixture_id":row["fixture_id"],
                    "source":row["source"],
                    "observed":observed,
                    "expected":expected,
                })
        return failures

    def activate_candidate(self, policy_id: str, version: int):
        candidate = self._candidate(policy_id,version)
        current = self.active(policy_id)
        if current is None:
            raise ValueError("no active policy")
        relation = semantic_relation_structural(current,candidate)

        # Conservative v1.2 lane: no automated weakening/replacement.
        if relation not in {"EQUIVALENT","STRONGER"}:
            with self.connect() as con:
                con.execute(
                    "UPDATE policies SET state='STOPPED'"
                    " WHERE policy_id=? AND version=?",
                    (policy_id,version),
                )
                self._audit(
                    con,"ACTIVATION_STOP",policy_id=policy_id,version=version,
                    detail=f"non-monotonic relation={relation}"
                )
            return EvolutionDecision(
                "STOPPED","non-monotonic-policy-change-requires-external-review",
                relation,policy_id,version
            )

        # Known incident traceability.
        hazards = self._hazards_by_group(candidate)
        with self.connect() as con:
            incidents = con.execute(
                "SELECT * FROM incidents WHERE severity IN ('HIGH','CRITICAL')"
                " ORDER BY incident_id"
            ).fetchall()
        for incident in incidents:
            gid = incident["mapped_group_id"]
            if not gid:
                return EvolutionDecision(
                    "STOPPED","high-severity-incident-unmapped",relation,
                    policy_id,version,incident_id=incident["incident_id"]
                )
            if gid not in hazards or incident["hazard_id"] not in hazards[gid]:
                return EvolutionDecision(
                    "STOPPED","incident-mapping-not-covered-by-candidate",
                    relation,policy_id,version,incident_id=incident["incident_id"]
                )

        failures = self.evaluate_fixtures(candidate)
        if failures:
            return EvolutionDecision(
                "STOPPED","regression-fixture-failed",relation,
                policy_id,version,failing_fixture=failures[0]["fixture_id"]
            )

        with self.connect() as con:
            con.execute("BEGIN IMMEDIATE")
            con.execute(
                "UPDATE policies SET state='RETIRED'"
                " WHERE policy_id=? AND state='ACTIVE'",
                (policy_id,),
            )
            con.execute(
                "UPDATE policies SET state='ACTIVE'"
                " WHERE policy_id=? AND version=?",
                (policy_id,version),
            )
            con.execute(
                "INSERT INTO active_policy(policy_id,version) VALUES(?,?)"
                " ON CONFLICT(policy_id) DO UPDATE SET version=excluded.version",
                (policy_id,version),
            )
            # Mapped incidents whose hazard is represented are now covered by the
            # active runtime policy. This does not mean the incident is "solved".
            for incident in incidents:
                con.execute(
                    "UPDATE incidents SET state='COVERED'"
                    " WHERE incident_id=?", (incident["incident_id"],)
                )
            self._audit(
                con,"ACTIVATE",policy_id=policy_id,version=version,
                detail=f"relation={relation};fixtures=pass;incidents=covered"
            )
            con.execute("COMMIT")
        return EvolutionDecision(
            "ACTIVE","candidate-activated",relation,policy_id,version
        )

    def incident_state(self, incident_id):
        with self.connect() as con:
            row = con.execute(
                "SELECT * FROM incidents WHERE incident_id=?", (incident_id,)
            ).fetchone()
        return None if row is None else dict(row)

    def audit(self):
        with self.connect() as con:
            return [dict(r) for r in con.execute(
                "SELECT * FROM audit ORDER BY sequence"
            ).fetchall()]


def brute_force_relation(old: Policy, new: Policy) -> str:
    """Independent truth-table semantic oracle."""
    atoms = sorted({
        o.obligation_id
        for p in (old,new)
        for g in p.groups
        for o in g.obligations
    })
    old_implies_new = True
    new_implies_old = True
    for bits in __import__("itertools").product((False,True), repeat=len(atoms)):
        truth = dict(zip(atoms,bits))
        ov = policy_formula(old,truth)
        nv = policy_formula(new,truth)
        if ov and not nv:
            old_implies_new = False
        if nv and not ov:
            new_implies_old = False
    if old_implies_new and new_implies_old:
        return "EQUIVALENT"
    if new_implies_old and not old_implies_new:
        return "STRONGER"
    if old_implies_new and not new_implies_old:
        return "WEAKER"
    return "INCOMPARABLE"
