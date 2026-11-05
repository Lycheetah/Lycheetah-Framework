"""Deterministic contract validator for one Sync Zone cycle record.  [SCAFFOLD]

What a pass establishes: the record is internally consistent with the rules below,
and with its parent record when one is supplied. What it does NOT establish: that any
test really ran, that a named human really decided, that a review was competent, or
that a simulation is not circular. Identity strings are declarations, not
authentication. See ``CLAIMS_AND_LIMITS.md``.

Two outputs are kept apart on purpose:

* ``findings`` - the record breaks the contract now (it is invalid as written);
* ``blockers`` - the record is valid, but these conditions would stop a human from
  ratifying it. On an ACCEPTED or PARTIAL record every blocker becomes a CRITICAL
  finding, because the record then claims a promotion it was not entitled to.

Every rule names the threat it answers (T01-T20 in ``THREAT_MODEL.md``).
"""

from __future__ import annotations

import datetime as dt
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .canonical import candidate_digest, failure_digest, sha256_hex

SCHEMA_VERSION = "sync-zone-cycle-v0.1"
RULESET_ID = "sz-rules-v0.1"

EVIDENCE_KINDS = frozenset(
    {
        "STATIC_CHECK",
        "UNIT_TEST",
        "INTEGRATION_TEST",
        "SYNTHETIC_EXPERIMENT",
        "EXTERNAL_SOURCE",
        "MODEL_REVIEW",
        "HUMAN_REVIEW",
        "INDEPENDENT_EXTERNAL_REVIEW",
        "ACTION_RECEIPT",
        "NOT_RUN",
    }
)
DETERMINISTIC_KINDS = frozenset({"STATIC_CHECK", "UNIT_TEST", "INTEGRATION_TEST"})
HUMAN_ONLY_KINDS = frozenset({"HUMAN_REVIEW", "INDEPENDENT_EXTERNAL_REVIEW"})
OUTCOMES = frozenset({"PASS", "FAIL", "NOT_RUN", "SUCCEEDED", "FAILED", "UNKNOWN"})

RATIFICATION_STATUSES = frozenset(
    {"PROPOSED", "REJECTED", "PARTIAL", "ACCEPTED", "BLOCKED", "SUPERSEDED"}
)
PROMOTING = frozenset({"ACCEPTED", "PARTIAL"})
STOP_REASONS = frozenset(
    {
        "AUTHORITY",
        "EVIDENCE",
        "SAFETY",
        "REGRESSION",
        "BUDGET",
        "CONVERGENCE",
        "CONFLICT",
        "COMPLETION",
        "EXTERNAL_DEPENDENCY",
    }
)

# Ordered from weakest to strongest. A reviewer's *effective* independence is the
# weaker of what it declares and what the metadata allows.
INDEPENDENCE_ORDER = (
    "same_run",
    "same_model_same_context",
    "same_model_fresh_context",
    "different_model",
    "human",
)
RANK = {name: i for i, name in enumerate(INDEPENDENCE_ORDER)}
DECLARABLE_INDEPENDENCE = frozenset(INDEPENDENCE_ORDER) | {"deterministic_tool"}

SEVERITIES = ("CRITICAL", "HIGH", "MEDIUM", "LOW")
BLOCKING_SEVERITIES = frozenset({"CRITICAL", "HIGH"})

_HEX40 = re.compile(r"^[0-9a-f]{40}([0-9a-f]{24})?$")
_HEX64 = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True)
class Policy:
    """Rules a cycle is judged under. Changing these is a meta-governance change."""

    ruleset_id: str = RULESET_ID
    # Weakest review independence that can count toward acceptance.
    min_review_independence: str = "same_model_fresh_context"
    require_deterministic_pass: bool = True
    # Paths whose change is a change to the rules (constitutional firewall).
    governance_paths: tuple[str, ...] = (
        "18_EXPERIMENTAL/sync-zone-recursive-framework/sync_zone/",
        "18_EXPERIMENTAL/sync-zone-recursive-framework/PROTOCOL.md",
        "AGENTS.md",
        "CLAUDE.md",
        "28_DEFENSE/FAILURE_MUSEUM.md",
        "lycheetah/assurance/policy.py",
    )
    protected_test_prefixes: tuple[str, ...] = ("tests/",)


@dataclass(frozen=True)
class Finding:
    code: str
    severity: str
    gate: str
    message: str
    threat: str = ""

    def to_dict(self) -> dict[str, str]:
        return {
            "code": self.code,
            "severity": self.severity,
            "gate": self.gate,
            "threat": self.threat,
            "message": self.message,
        }


@dataclass
class Report:
    cycle_id: str
    status: str
    findings: list[Finding] = field(default_factory=list)
    blockers: list[Finding] = field(default_factory=list)
    review_independence: dict[str, str] = field(default_factory=dict)

    @property
    def valid(self) -> bool:
        """No CRITICAL or HIGH contract violation in the record as written."""
        return not any(f.severity in BLOCKING_SEVERITIES for f in self.findings)

    @property
    def ratifiable(self) -> bool:
        """Valid, and nothing would block a human from ratifying the candidate."""
        return self.valid and not self.blockers

    def codes(self) -> set[str]:
        return {f.code for f in self.findings}

    def blocker_codes(self) -> set[str]:
        return {f.code for f in self.blockers}

    def gates(self) -> dict[str, str]:
        names = (
            "structure",
            "integrity",
            "authority",
            "evidence",
            "regression",
            "dissent",
            "human",
            "consequence",
            "stop",
            "handoff",
        )
        out = {}
        for g in names:
            bad = [f for f in self.findings + self.blockers if f.gate == g]
            out[g] = "FAIL" if bad else "PASS"
        return out

    def to_dict(self) -> dict[str, Any]:
        return {
            "cycle_id": self.cycle_id,
            "status": self.status,
            "valid": self.valid,
            "ratifiable": self.ratifiable,
            "gates": self.gates(),
            "review_independence": dict(self.review_independence),
            "findings": [f.to_dict() for f in self.findings],
            "blockers": [f.to_dict() for f in self.blockers],
        }


def _parse_time(value: Any) -> dt.datetime | None:
    if not isinstance(value, str) or not value:
        return None
    text = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = dt.datetime.fromisoformat(text)
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None else None


def _list(record: Mapping[str, Any], key: str) -> list[Mapping[str, Any]]:
    value = record.get(key, [])
    return [v for v in value if isinstance(v, Mapping)] if isinstance(value, list) else []


def _under(path: str, prefixes: Sequence[str]) -> bool:
    return any(path == p.rstrip("/") or path.startswith(p) for p in prefixes)


class _Checker:
    def __init__(
        self,
        record: Mapping[str, Any],
        parent: Mapping[str, Any] | None,
        now: dt.datetime,
        policy: Policy,
        repo_root: Path | None,
    ) -> None:
        self.r = record
        self.parent = parent
        self.now = now
        self.policy = policy
        self.repo_root = repo_root
        anchor = record.get("anchor")
        self.anchor: Mapping[str, Any] = anchor if isinstance(anchor, Mapping) else {}
        rat = record.get("ratification")
        self.rat: Mapping[str, Any] = rat if isinstance(rat, Mapping) else {}
        self.status = str(self.rat.get("status", ""))
        self.report = Report(cycle_id=str(record.get("cycle_id", "")), status=self.status)
        self.runs = {str(x.get("run_id")): x for x in _list(record, "runs")}
        self.candidates = {str(x.get("candidate_id")): x for x in _list(record, "candidates")}
        auth = self.anchor.get("authority")
        self.authority: Mapping[str, Any] = auth if isinstance(auth, Mapping) else {}
        grants = self.authority.get("grants", [])
        self.grants = {str(g) for g in grants} if isinstance(grants, list) else set()

    # -- recording -----------------------------------------------------------
    def find(self, code: str, sev: str, gate: str, msg: str, threat: str = "") -> None:
        self.report.findings.append(Finding(code, sev, gate, msg, threat))

    def block(self, code: str, gate: str, msg: str, threat: str = "") -> None:
        self.report.blockers.append(Finding(code, "HIGH", gate, msg, threat))

    # -- top level -----------------------------------------------------------
    def run(self) -> Report:
        if not self.structure():
            return self.report
        self.check_anchor()
        self.check_runs()
        self.check_candidates()
        self.check_evidence()
        self.check_reviews()
        self.check_dissent()
        self.check_parent()
        self.check_ratification()
        self.check_stop()
        self.check_handoff()
        if self.status in PROMOTING:
            for b in self.report.blockers:
                self.find(
                    "PROMOTED_WITH_BLOCKER",
                    "CRITICAL",
                    b.gate,
                    f"{self.status} recorded while {b.code} blocks ratification: {b.message}",
                    b.threat,
                )
        return self.report

    def structure(self) -> bool:
        r = self.r
        required = ("schema_version", "cycle_id", "anchor", "runs", "candidates",
                    "evidence", "reviews", "dissent", "failures", "stop",
                    "ratification", "handoff")
        missing = [k for k in required if k not in r]
        if missing:
            self.find("MISSING_FIELDS", "CRITICAL", "structure", f"missing {missing}")
            return False
        if r.get("schema_version") != SCHEMA_VERSION:
            self.find("SCHEMA_VERSION", "CRITICAL", "structure",
                      f"schema_version must be {SCHEMA_VERSION!r}")
            return False
        if self.status not in RATIFICATION_STATUSES:
            self.find("RATIFICATION_STATUS", "CRITICAL", "structure",
                      f"unknown ratification status {self.status!r}")
            return False
        # Ids are unique across every list in the record.
        seen: dict[str, str] = {}
        for key, idkey in (("runs", "run_id"), ("candidates", "candidate_id"),
                           ("evidence", "evidence_id"), ("reviews", "review_id"),
                           ("dissent", "dissent_id"), ("failures", "id")):
            for item in _list(r, key):
                ident = item.get(idkey)
                if not isinstance(ident, str) or not ident:
                    self.find("MISSING_ID", "CRITICAL", "structure", f"{key} entry without {idkey}")
                elif ident in seen:
                    self.find("DUPLICATE_ID", "CRITICAL", "structure",
                              f"id {ident!r} used in {seen[ident]} and {key}", "T04")
                else:
                    seen[ident] = key
        return True

    # -- anchor and authority ------------------------------------------------
    def check_anchor(self) -> None:
        a = self.anchor
        if not _HEX40.match(str(a.get("baseline_revision", ""))):
            self.find("BASELINE_MISSING", "CRITICAL", "integrity",
                      "anchor.baseline_revision must be a full git object id", "T01")
        if not str(a.get("principal", "")).strip():
            self.find("PRINCIPAL_MISSING", "CRITICAL", "authority",
                      "anchor.principal names the human with canonical authority")
        if a.get("ruleset_id") != self.policy.ruleset_id:
            self.find("RULESET_MISMATCH", "CRITICAL", "authority",
                      f"cycle is anchored to {a.get('ruleset_id')!r} but is being judged under "
                      f"{self.policy.ruleset_id!r}; a cycle is judged by the rules it started under",
                      "T07")
        for c in _list(a, "governing_contracts"):
            if not _HEX64.match(str(c.get("sha256", ""))):
                self.find("CONTRACT_DIGEST", "HIGH", "integrity",
                          f"governing contract {c.get('path')!r} has no sha256", "T01")
            elif self.repo_root is not None:
                p = self.repo_root / str(c.get("path"))
                if p.is_file() and sha256_hex(p.read_bytes()) != c["sha256"]:
                    self.block("CONTRACT_CHANGED", "integrity",
                               f"{c.get('path')} changed since the cycle was anchored", "T10")
        if not self.authority:
            self.find("AUTHORITY_MISSING", "CRITICAL", "authority", "anchor.authority is required")
            return
        if self.authority.get("revoked") is True:
            self.block("AUTHORITY_REVOKED", "authority", "the principal revoked this cycle's authority")
        expires = self.authority.get("expires_at")
        if expires is not None:
            t = _parse_time(expires)
            if t is None:
                self.find("AUTHORITY_EXPIRY_FORMAT", "HIGH", "authority",
                          "authority.expires_at must be ISO-8601 with a timezone")
            elif t <= self.now:
                self.block("AUTHORITY_EXPIRED", "authority", f"authority expired at {expires}")
        budget = self.anchor.get("budget")
        if not isinstance(budget, Mapping) or not all(
            isinstance(budget.get(k), int) and budget[k] > 0 for k in ("max_depth", "max_runs")
        ):
            self.find("BUDGET_MISSING", "HIGH", "stop",
                      "anchor.budget needs positive max_depth and max_runs", "T13")

    # -- runs and independence -----------------------------------------------
    def check_runs(self) -> None:
        identities: dict[tuple[str, str, str, str], str] = {}
        for run_id, run in self.runs.items():
            for k in ("role", "provider", "model", "independence", "observed_by"):
                if not str(run.get(k, "")).strip():
                    self.find("RUN_METADATA", "HIGH", "integrity",
                              f"run {run_id} is missing {k}", "T04")
            if run.get("independence") not in DECLARABLE_INDEPENDENCE:
                self.find("RUN_INDEPENDENCE", "HIGH", "integrity",
                          f"run {run_id} declares unknown independence "
                          f"{run.get('independence')!r}", "T04")
            if run.get("observed_by") not in ("self_reported", "platform_observed"):
                self.find("RUN_OBSERVED_BY", "MEDIUM", "integrity",
                          f"run {run_id}: observed_by must be self_reported or platform_observed")
            ident = (str(run.get("provider")), str(run.get("model")),
                     str(run.get("context_digest")), str(run.get("role")))
            if run.get("role") != "human" and ident in identities:
                self.find("DUPLICATE_RUN_IDENTITY", "MEDIUM", "integrity",
                          f"runs {identities[ident]} and {run_id} share provider, model, "
                          "context and role; they are one witness counted twice", "T04")
            identities.setdefault(ident, run_id)

    def effective_independence(self, reviewer_id: str, producer_id: str) -> str:
        rev, prod = self.runs.get(reviewer_id), self.runs.get(producer_id)
        if rev is None or prod is None:
            return "same_run"
        if reviewer_id == producer_id:
            return "same_run"
        if rev.get("role") == "human":
            return "human"
        same_model = (rev.get("provider"), rev.get("model")) == (prod.get("provider"), prod.get("model"))
        if same_model:
            same_ctx = rev.get("context_digest") and rev.get("context_digest") == prod.get("context_digest")
            observed = "same_model_same_context" if same_ctx else "same_model_fresh_context"
        else:
            observed = "different_model"
        declared = str(rev.get("independence", "same_run"))
        if declared in RANK and RANK[declared] > RANK[observed]:
            self.find("FALSE_INDEPENDENCE", "HIGH", "integrity",
                      f"run {reviewer_id} declares {declared} independence from {producer_id} "
                      f"but the metadata allows only {observed}", "T04")
        if declared in RANK:
            return INDEPENDENCE_ORDER[min(RANK[declared], RANK[observed])]
        return observed

    # -- candidates ----------------------------------------------------------
    def check_candidates(self) -> None:
        if not self.candidates:
            self.find("NO_CANDIDATE", "HIGH", "structure", "a cycle records at least one candidate")
        for cid, c in self.candidates.items():
            if str(c.get("produced_by")) not in self.runs:
                self.find("MISSING_PROVENANCE", "HIGH", "integrity",
                          f"candidate {cid} names no recorded producing run", "T04")
            base = c.get("baseline_revision")
            if base != self.anchor.get("baseline_revision"):
                if c.get("rebased_from") == base and str(c.get("reconciliation", "")).strip():
                    self.block("REBASED_CANDIDATE", "integrity",
                               f"candidate {cid} was built on {base}; its rebase must be "
                               "re-verified in a new cycle anchored to the new baseline", "T01")
                else:
                    self.find("BASELINE_MISMATCH", "CRITICAL", "integrity",
                              f"candidate {cid} was built on {base!r}, cycle is anchored to "
                              f"{self.anchor.get('baseline_revision')!r}", "T01")
            arts = c.get("artifacts")
            if not isinstance(arts, list) or not all(isinstance(a, Mapping) and "path" in a for a in arts):
                self.find("ARTIFACTS_MALFORMED", "CRITICAL", "integrity", f"candidate {cid} artifacts")
                continue
            if c.get("digest") != candidate_digest(arts):
                self.find("CANDIDATE_DIGEST_MISMATCH", "CRITICAL", "integrity",
                          f"candidate {cid}: recorded digest does not match its artifacts "
                          "(changed after it was recorded)", "T02")
            sup = c.get("supersedes")
            if sup is not None and sup not in self.candidates:
                self.find("SUPERSEDES_UNKNOWN", "HIGH", "integrity",
                          f"candidate {cid} supersedes unknown {sup!r}")
            paths = [str(a["path"]) for a in arts]
            touches_rules = any(_under(p, self.policy.governance_paths) for p in paths)
            if touches_rules and c.get("meta_governance") is not True:
                self.find("UNDECLARED_META_CHANGE", "HIGH", "authority",
                          f"candidate {cid} changes governing rules without declaring "
                          "meta_governance", "T07")
            for a in arts:
                if a.get("sha256") is None and _under(str(a["path"]), self.policy.protected_test_prefixes):
                    if c.get("meta_governance") is not True:
                        self.find("TEST_DELETION", "HIGH", "regression",
                                  f"candidate {cid} deletes {a['path']}; deleting a judging "
                                  "test is a meta-governance change", "T08")
                elif a.get("sha256") is not None and not _HEX64.match(str(a.get("sha256"))):
                    self.find("ARTIFACT_DIGEST", "HIGH", "integrity",
                              f"candidate {cid}: {a['path']} has a malformed sha256")
            if arts and "local_code_change" not in self.grants:
                self.block("AUTHORITY_SCOPE", "authority",
                           f"candidate {cid} changes files but the cycle holds no "
                           "local_code_change grant; it may be kept, not promoted", "T06")
            effects = c.get("effects", [])
            if isinstance(effects, list) and "external" in effects and "external_effect" not in self.grants:
                self.block("AUTHORITY_SCOPE", "consequence",
                           f"candidate {cid} declares an external effect without an "
                           "external_effect grant", "T15")

    def bound_evidence(self, cid: str) -> list[Mapping[str, Any]]:
        """Evidence that may count for candidate ``cid``: bound to its exact digest and fresh."""
        c = self.candidates.get(cid, {})
        out = []
        for e in _list(self.r, "evidence"):
            if e.get("target_candidate") != cid or e.get("target_digest") != c.get("digest"):
                continue
            until = e.get("valid_until")
            if until is not None:
                t = _parse_time(until)
                if t is None or t <= self.now:
                    continue
            if e.get("revision") and c.get("result_revision") and e["revision"] != c["result_revision"]:
                continue
            out.append(e)
        return out

    # -- evidence ------------------------------------------------------------
    def check_evidence(self) -> None:
        for e in _list(self.r, "evidence"):
            eid = e.get("evidence_id")
            kind = e.get("kind")
            if kind not in EVIDENCE_KINDS:
                self.find("EVIDENCE_KIND", "HIGH", "evidence", f"{eid}: unknown kind {kind!r}", "T17")
            if e.get("outcome") not in OUTCOMES:
                self.find("EVIDENCE_OUTCOME", "HIGH", "evidence", f"{eid}: unknown outcome")
            producer = self.runs.get(str(e.get("produced_by")))
            if producer is None:
                self.find("MISSING_PROVENANCE", "HIGH", "evidence",
                          f"{eid}: no recorded run produced this evidence", "T04")
            elif kind in HUMAN_ONLY_KINDS and producer.get("role") != "human":
                self.find("EVIDENCE_LABEL_INFLATION", "HIGH", "evidence",
                          f"{eid}: a {producer.get('role')} run cannot produce {kind}", "T17")
            cid = str(e.get("target_candidate"))
            c = self.candidates.get(cid)
            if c is None:
                self.find("EVIDENCE_TARGET", "HIGH", "evidence", f"{eid}: unknown target {cid!r}")
                continue
            if e.get("target_digest") != c.get("digest"):
                self.find("STALE_BINDING", "HIGH", "evidence",
                          f"{eid} judged a different revision of {cid}; it cannot count", "T02")
            if e.get("revision") and c.get("result_revision") and e["revision"] != c["result_revision"]:
                self.find("EVIDENCE_REVISION_MISMATCH", "HIGH", "evidence",
                          f"{eid} ran at {e['revision']} but {cid} is {c['result_revision']}", "T02")
            if e.get("valid_until") is not None:
                t = _parse_time(e.get("valid_until"))
                if t is None:
                    self.find("EVIDENCE_EXPIRY_FORMAT", "MEDIUM", "evidence", f"{eid}: bad valid_until")
                elif t <= self.now:
                    self.block("EVIDENCE_EXPIRED", "evidence",
                               f"{eid} expired at {e['valid_until']}; revalidate before relying on it",
                               "T10")

    # -- reviews -------------------------------------------------------------
    def check_reviews(self) -> None:
        shared: dict[tuple[str, str], list[str]] = {}
        for rv in _list(self.r, "reviews"):
            run = self.runs.get(str(rv.get("by")), {})
            ctx = str(run.get("context_digest", ""))
            if ctx and ctx != "-" and run.get("role") != "human":
                shared.setdefault((str(rv.get("target_candidate")), ctx), []).append(str(rv.get("review_id")))
        for (cid, ctx), ids in shared.items():
            if len(ids) > 1:
                self.find("SHARED_REVIEW_CONTEXT", "MEDIUM", "evidence",
                          f"reviews {ids} of {cid} all read context {ctx}; a shared source "
                          "error would reach every one of them, so they are correlated", "T18")
        for rv in _list(self.r, "reviews"):
            rid = str(rv.get("review_id"))
            by = str(rv.get("by"))
            cid = str(rv.get("target_candidate"))
            c = self.candidates.get(cid)
            if by not in self.runs:
                self.find("MISSING_PROVENANCE", "HIGH", "evidence", f"review {rid} has no recorded run")
            if c is None:
                self.find("REVIEW_TARGET", "HIGH", "evidence", f"review {rid}: unknown target {cid!r}")
                continue
            if rv.get("target_digest") != c.get("digest"):
                self.find("STALE_BINDING", "HIGH", "evidence",
                          f"review {rid} read a different revision of {cid}", "T02")
            if rv.get("modified_candidate") is True:
                new = self.candidates.get(str(rv.get("produced_candidate")))
                if new is None or new.get("produced_by") != by or new.get("supersedes") != cid:
                    self.find("REVIEWER_MUTATION_UNRECORDED", "CRITICAL", "integrity",
                              f"review {rid} changed {cid} but no new candidate records the "
                              "reviewer as its producer and the old candidate as superseded", "T03")
            self.report.review_independence[rid] = self.effective_independence(
                by, str(c.get("produced_by"))
            )
            for f in _list(rv, "findings"):
                if not isinstance(f.get("id"), str) or not f.get("id"):
                    self.find("FINDING_ID", "HIGH", "dissent", f"review {rid} has a finding without id")
                if f.get("severity") not in SEVERITIES:
                    self.find("FINDING_SEVERITY", "MEDIUM", "dissent",
                              f"review {rid} finding {f.get('id')}: unknown severity")

    def open_blocking_items(self) -> list[tuple[str, str, Mapping[str, Any]]]:
        """(id, kind, item) for every open CRITICAL/HIGH review finding and dissent."""
        out = []
        for rv in _list(self.r, "reviews"):
            for f in _list(rv, "findings"):
                if f.get("severity") in BLOCKING_SEVERITIES and f.get("status", "OPEN") == "OPEN":
                    out.append((str(f.get("id")), "finding", f))
        for d in _list(self.r, "dissent"):
            if d.get("severity") in BLOCKING_SEVERITIES and d.get("status", "OPEN") == "OPEN":
                out.append((str(d.get("dissent_id")), "dissent", d))
        return out

    # -- dissent -------------------------------------------------------------
    def check_dissent(self) -> None:
        principal = self.anchor.get("principal")
        for d in _list(self.r, "dissent"):
            did = d.get("dissent_id")
            if d.get("status") not in ("OPEN", "ADDRESSED", "OVERRULED"):
                self.find("DISSENT_STATUS", "HIGH", "dissent", f"{did}: unknown status")
            if d.get("status") == "ADDRESSED":
                ref = d.get("addressed_by")
                ids = {e.get("evidence_id") for e in _list(self.r, "evidence")} | set(self.candidates)
                if ref not in ids:
                    self.find("DISSENT_ADDRESSED_WITHOUT_REF", "HIGH", "dissent",
                              f"{did} marked ADDRESSED without naming the evidence or candidate "
                              "that addresses it", "T05")
            if d.get("status") == "OVERRULED" and d.get("overruled_by") != principal:
                self.find("DISSENT_OVERRULED_BY_NON_PRINCIPAL", "CRITICAL", "dissent",
                          f"{did} overruled by {d.get('overruled_by')!r}; only the principal "
                          "may overrule a dissent", "T05")
        for ident, kind, _item in self.open_blocking_items():
            self.block("OPEN_CRITICAL_DISSENT", "dissent",
                       f"open {kind} {ident} blocks promotion until addressed or overruled "
                       "by the principal", "T05")

    # -- parent lineage ------------------------------------------------------
    def check_parent(self) -> None:
        pid = self.r.get("parent_cycle_id")
        p = self.parent
        if pid is None:
            if p is not None:
                self.find("PARENT_UNDECLARED", "HIGH", "integrity", "a parent was supplied but not declared")
            return
        if p is None:
            self.block("PARENT_UNVERIFIED", "integrity",
                       f"parent {pid} was not supplied, so lineage cannot be checked")
            return
        if p.get("cycle_id") != pid:
            self.find("PARENT_MISMATCH", "CRITICAL", "integrity",
                      f"declared parent {pid} but {p.get('cycle_id')} was supplied")
            return
        pa = p.get("anchor", {}) if isinstance(p.get("anchor"), Mapping) else {}
        pauth = pa.get("authority", {}) if isinstance(pa.get("authority"), Mapping) else {}
        pgrants = set(pauth.get("grants", [])) if isinstance(pauth.get("grants"), list) else set()
        if not self.grants <= pgrants:
            self.find("AUTHORITY_WIDENED", "CRITICAL", "authority",
                      f"child grants {sorted(self.grants - pgrants)} that its parent never held; "
                      "authority does not grow through recursion", "T06")
        if pauth.get("revoked") is True:
            self.block("AUTHORITY_REVOKED", "authority", f"parent {pid}'s authority was revoked")
        pexp, cexp = _parse_time(pauth.get("expires_at")), _parse_time(self.authority.get("expires_at"))
        if pexp is not None and (cexp is None or cexp > pexp):
            self.find("AUTHORITY_OUTLIVES_PARENT", "CRITICAL", "authority",
                      "child authority must expire no later than its parent's", "T06")
        if pa.get("principal") != self.anchor.get("principal"):
            self.find("PRINCIPAL_CHANGED", "CRITICAL", "authority",
                      "the principal cannot change inside a lineage without a new root cycle")
        pb = pa.get("budget", {}) if isinstance(pa.get("budget"), Mapping) else {}
        cb = self.anchor.get("budget", {}) if isinstance(self.anchor.get("budget"), Mapping) else {}
        for k in ("max_depth", "max_runs"):
            if isinstance(pb.get(k), int) and isinstance(cb.get(k), int) and cb[k] > pb[k]:
                self.find("BUDGET_WIDENED", "CRITICAL", "stop",
                          f"child {k}={cb[k]} exceeds parent {k}={pb[k]}", "T13")
        depth = int(p.get("depth", 0)) + 1
        if self.r.get("depth") != depth:
            self.find("DEPTH_MISMATCH", "HIGH", "stop", f"depth must be {depth}", "T13")
        if isinstance(cb.get("max_depth"), int) and depth > cb["max_depth"]:
            if (self.r.get("stop") or {}).get("reason") != "BUDGET":
                self.find("DEPTH_EXHAUSTED", "HIGH", "stop",
                          f"depth {depth} exceeds max_depth {cb['max_depth']}; the cycle "
                          "must stop with reason BUDGET", "T13")
        # Rules may only change through a ratified meta change in the parent.
        if pa.get("ruleset_id") != self.anchor.get("ruleset_id"):
            ack = (p.get("ratification") or {}).get("meta_governance_ack") or {}
            if not ((p.get("ratification") or {}).get("status") == "ACCEPTED"
                    and ack.get("ruleset_after") == self.anchor.get("ruleset_id")):
                self.find("RULESET_CHANGED_WITHOUT_RATIFICATION", "CRITICAL", "authority",
                          "the ruleset changed between parent and child without a ratified "
                          "meta-governance change", "T07")
        # Failures are append-only: present, and byte-identical in their claim.
        child_f = {f.get("id"): f for f in _list(self.r, "failures")}
        for pf in _list(p, "failures"):
            cf = child_f.get(pf.get("id"))
            if cf is None:
                self.find("FAILURE_ERASED", "CRITICAL", "integrity",
                          f"failure {pf.get('id')} from the parent is missing", "T09")
            elif failure_digest(cf) != failure_digest(pf):
                self.find("FAILURE_REWRITTEN", "CRITICAL", "integrity",
                          f"failure {pf.get('id')} was reworded; supersede it instead", "T09")
        child_d = {d.get("dissent_id") for d in _list(self.r, "dissent")}
        for pd in _list(p, "dissent"):
            if pd.get("status") == "OPEN" and pd.get("dissent_id") not in child_d:
                self.find("DISSENT_DROPPED", "HIGH", "dissent",
                          f"open dissent {pd.get('dissent_id')} from the parent was not carried", "T05")
        prat = p.get("ratification") or {}
        if prat.get("status") == "ACCEPTED":
            durable = (p.get("handoff") or {}).get("durable_revision")
            if durable and self.anchor.get("baseline_revision") != durable and not self.anchor.get("rebase_note"):
                self.find("BASELINE_NOT_PARENT_DURABLE", "HIGH", "integrity",
                          "child does not start from the parent's durable revision", "T01")
            pdig = prat.get("candidate_digest")
            if self.status in PROMOTING and pdig and pdig == self.rat.get("candidate_digest"):
                self.block("NO_CHANGE", "stop",
                           "the ratified candidate is identical to the parent's; stop with "
                           "CONVERGENCE instead of promoting again", "T13")

    # -- ratification --------------------------------------------------------
    def check_ratification(self) -> None:
        rat, principal = self.rat, self.anchor.get("principal")
        if rat.get("by") is not None and rat.get("by_kind") == "human" and rat.get("by") != principal:
            self.find("RATIFIER_NOT_PRINCIPAL", "CRITICAL", "human",
                      f"{rat.get('by')!r} is not the principal {principal!r}")
        if self.status not in PROMOTING:
            # Not promoted: report what would block a promotion, but nothing more.
            self.acceptance_blockers(self.target_candidate())
            return
        if rat.get("by_kind") != "human" or rat.get("by") != principal:
            self.find("FALSE_RATIFICATION", "CRITICAL", "human",
                      f"{self.status} must be recorded by the principal {principal!r} as a human "
                      f"decision; got by={rat.get('by')!r} by_kind={rat.get('by_kind')!r}", "T17")
        if _parse_time(rat.get("at")) is None:
            self.find("RATIFICATION_TIME", "HIGH", "human", "ratification.at must be a timestamp")
        cid = self.target_candidate()
        c = self.candidates.get(cid or "")
        if c is None:
            self.find("RATIFIED_UNKNOWN_CANDIDATE", "CRITICAL", "integrity",
                      f"ratification names unknown candidate {cid!r}")
            return
        if rat.get("candidate_digest") != c.get("digest"):
            self.find("RATIFIED_WRONG_REVISION", "CRITICAL", "integrity",
                      "the ratified digest is not the candidate's digest", "T02")
        self.acceptance_blockers(cid)

    def target_candidate(self) -> str | None:
        cid = self.rat.get("candidate_id")
        if cid:
            return str(cid)
        superseded = {c.get("supersedes") for c in self.candidates.values()}
        latest = [k for k in self.candidates if k not in superseded]
        return latest[-1] if latest else None

    def acceptance_blockers(self, cid: str | None) -> None:
        c = self.candidates.get(cid or "")
        if c is None:
            return
        bound = self.bound_evidence(str(cid))
        if any(e.get("outcome") in ("FAIL", "FAILED") for e in bound):
            self.block("FAILING_EVIDENCE", "regression", f"bound evidence for {cid} failed", "T08")
        if self.policy.require_deterministic_pass and not any(
            e.get("kind") in DETERMINISTIC_KINDS and e.get("outcome") == "PASS" for e in bound
        ):
            self.block("NO_BOUND_PASS", "evidence",
                       f"no fresh deterministic PASS is bound to {cid}'s exact digest", "T02")
        if "external" in (c.get("effects") or []):
            receipts = [e for e in bound if e.get("kind") == "ACTION_RECEIPT"]
            if not receipts:
                self.block("EFFECT_WITHOUT_RECEIPT", "consequence",
                           f"{cid} declares an external effect with no ACTION_RECEIPT", "T15")
            elif any(e.get("outcome") == "UNKNOWN" for e in receipts):
                self.block("EFFECT_UNKNOWN", "consequence",
                           f"{cid}'s external effect is UNKNOWN; reconcile before promotion or "
                           "retry", "T16")
            elif not any(e.get("outcome") == "SUCCEEDED" for e in receipts):
                self.block("EFFECT_NOT_SUCCEEDED", "consequence", f"{cid}'s effect did not succeed")
        need = RANK[self.policy.min_review_independence]
        counted = [
            rv for rv in _list(self.r, "reviews")
            if rv.get("target_candidate") == cid
            and rv.get("target_digest") == c.get("digest")
            and rv.get("modified_candidate") is not True
            and RANK.get(self.report.review_independence.get(str(rv.get("review_id")), "same_run"), 0) >= need
        ]
        if not counted:
            self.block("NO_INDEPENDENT_REVIEW", "evidence",
                       f"no review of {cid}'s exact digest reaches "
                       f"{self.policy.min_review_independence}; self-review cannot certify", "T04")
        if c.get("meta_governance") is True or any(
            _under(str(a.get("path")), self.policy.governance_paths) for a in c.get("artifacts", [])
        ):
            ack = self.rat.get("meta_governance_ack") or {}
            if not (ack.get("by") == self.anchor.get("principal")
                    and ack.get("ruleset_before") == self.anchor.get("ruleset_id")
                    and str(ack.get("separate_review", "")).strip()):
                self.block("META_CHANGE_NEEDS_SEPARATE_RATIFICATION", "human",
                           f"{cid} changes the rules; it needs the principal's separate "
                           "meta-governance acknowledgement, judged under the previous ruleset "
                           "and naming a separate review", "T07")
            if ack.get("ruleset_after") == self.anchor.get("ruleset_id"):
                self.find("SELF_JUDGED_RULE_CHANGE", "CRITICAL", "authority",
                          "the new ruleset is judging its own adoption", "T07")

    # -- stop ----------------------------------------------------------------
    def check_stop(self) -> None:
        stop = self.r.get("stop")
        reason = stop.get("reason") if isinstance(stop, Mapping) else None
        if reason not in STOP_REASONS:
            self.find("STOP_MISSING", "HIGH", "stop",
                      f"every cycle records why it stopped; got {reason!r}", "T13")
            return
        if self.status == "ACCEPTED" and reason != "COMPLETION":
            self.find("STOP_INCONSISTENT", "HIGH", "stop", "ACCEPTED cycles stop with COMPLETION")
        if self.status == "PROPOSED" and reason not in ("AUTHORITY", "EXTERNAL_DEPENDENCY"):
            self.find("STOP_INCONSISTENT", "MEDIUM", "stop",
                      "a PROPOSED cycle is waiting on the principal: reason AUTHORITY")
        budget = self.anchor.get("budget")
        if isinstance(budget, Mapping) and isinstance(budget.get("max_runs"), int):
            n = len([r for r in self.runs.values() if r.get("role") != "human"])
            if n > budget["max_runs"] and reason != "BUDGET":
                self.find("BUDGET_EXCEEDED", "HIGH", "stop",
                          f"{n} agent runs exceed max_runs {budget['max_runs']}; stop with BUDGET", "T13")

    # -- handoff -------------------------------------------------------------
    def check_handoff(self) -> None:
        h = self.r.get("handoff")
        if not isinstance(h, Mapping):
            self.find("HANDOFF_MISSING", "HIGH", "handoff", "handoff must be an object")
            return
        carried = h.get("carried_authority", [])
        carried = set(carried) if isinstance(carried, list) else set()
        if not carried <= self.grants:
            self.find("AUTHORITY_CREEP_IN_HANDOFF", "CRITICAL", "authority",
                      f"handoff carries {sorted(carried - self.grants)} that this cycle never held",
                      "T06")
        if self.status in PROMOTING and not _HEX40.match(str(h.get("durable_revision", ""))):
            self.find("HANDOFF_NO_DURABLE_REVISION", "HIGH", "handoff",
                      "a promoted cycle hands off an exact durable revision")
        unresolved = {str(u.get("id")) if isinstance(u, Mapping) else str(u)
                      for u in h.get("unresolved", []) if u is not None}
        for ident, kind, _item in self.open_blocking_items():
            if ident not in unresolved:
                self.find("CAVEAT_DROPPED_FROM_HANDOFF", "HIGH", "handoff",
                          f"open {kind} {ident} is missing from handoff.unresolved; the next "
                          "cycle would inherit the conclusion without the caveat", "T11")
        for ref in _list(h, "references"):
            path = str(ref.get("path", ""))
            if self.repo_root is None:
                continue
            p = self.repo_root / path
            if not p.is_file():
                self.find("HANDOFF_MISSING_ARTIFACT", "HIGH", "handoff",
                          f"handoff points to {path}, which does not exist")
            elif ref.get("sha256") and sha256_hex(p.read_bytes()) != ref["sha256"]:
                self.find("HANDOFF_ARTIFACT_CHANGED", "HIGH", "handoff",
                          f"{path} no longer matches the digest the handoff recorded", "T10")


def validate_cycle(
    record: Mapping[str, Any],
    *,
    parent: Mapping[str, Any] | None = None,
    now: dt.datetime | str | None = None,
    policy: Policy | None = None,
    repo_root: str | Path | None = None,
) -> Report:
    """Validate one cycle record. ``now`` is explicit so results are reproducible."""
    if isinstance(now, str):
        parsed = _parse_time(now)
        if parsed is None:
            raise ValueError("now must be ISO-8601 with a timezone")
        now = parsed
    if now is None:
        now = dt.datetime.now(dt.timezone.utc)
    root = Path(repo_root) if repo_root is not None else None
    return _Checker(record, parent, now, policy or Policy(), root).run()
