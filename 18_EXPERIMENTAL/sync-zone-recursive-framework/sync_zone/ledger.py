"""Append-only, hash-chained cycle ledger (JSON Lines).  [SCAFFOLD]

Each line holds one cycle record and the hash of the previous line. A changed,
removed or reordered line breaks the chain and ``verify`` names where.

Boundary: the chain detects edits by someone who does not also rewrite every later
line. Anyone who can rewrite the whole file can forge a fresh chain; anchoring the
head hash elsewhere (a commit, the Assurance checkpoint authority) is the next
maturity step and is not done here.
"""

from __future__ import annotations

import datetime as dt
import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .canonical import canonical_json, failure_digest, json_digest
from .validator import Finding, Policy, Report, validate_cycle

GENESIS = "0" * 64


class LedgerRefused(ValueError):
    """Raised when an append would break the ledger's contract."""

    def __init__(self, message: str, findings: list[Finding] | None = None) -> None:
        super().__init__(message)
        self.findings = findings or []


@dataclass(frozen=True)
class ChainReport:
    ok: bool
    entries: int
    head: str
    problem: str = ""


def _entry_hash(entry: Mapping[str, Any]) -> str:
    return json_digest({k: entry[k] for k in ("seq", "prev", "cycle_id", "record_digest", "record")})


class CycleLedger:
    def __init__(self, path: str | Path, policy: Policy | None = None) -> None:
        self.path = Path(path)
        self.policy = policy or Policy()

    # -- reading -------------------------------------------------------------
    def entries(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        out = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                out.append(json.loads(line))
        return out

    def verify(self) -> ChainReport:
        prev = GENESIS
        entries = self.entries()
        for i, e in enumerate(entries):
            if e.get("seq") != i:
                return ChainReport(False, len(entries), prev, f"line {i}: sequence {e.get('seq')}")
            if e.get("prev") != prev:
                return ChainReport(False, len(entries), prev, f"line {i}: chain broken")
            if e.get("record_digest") != json_digest(e.get("record")):
                return ChainReport(False, len(entries), prev, f"line {i}: record changed")
            if e.get("hash") != _entry_hash(e):
                return ChainReport(False, len(entries), prev, f"line {i}: entry hash")
            prev = e["hash"]
        return ChainReport(True, len(entries), prev)

    def latest(self, cycle_id: str) -> dict[str, Any] | None:
        found = None
        for e in self.entries():
            if e["cycle_id"] == cycle_id:
                found = e["record"]
        return found

    def history(self, cycle_id: str) -> list[dict[str, Any]]:
        return [e["record"] for e in self.entries() if e["cycle_id"] == cycle_id]

    # -- writing -------------------------------------------------------------
    def append(self, record: Mapping[str, Any], *, now: dt.datetime | str | None = None,
               repo_root: str | Path | None = None) -> Report:
        chain = self.verify()
        if not chain.ok:
            raise LedgerRefused(f"ledger chain is broken ({chain.problem}); nothing appended")
        cid = str(record.get("cycle_id", ""))
        pid = record.get("parent_cycle_id")
        parent = self.latest(str(pid)) if pid else None
        report = validate_cycle(record, parent=parent, now=now, policy=self.policy, repo_root=repo_root)
        problems = [f for f in report.findings if f.severity in ("CRITICAL", "HIGH")]
        problems += self._amendment_problems(cid, record)
        problems += self._concurrency_problems(record)
        if problems:
            raise LedgerRefused(
                f"cycle {cid} refused: " + "; ".join(sorted({p.code for p in problems})), problems
            )
        entries = self.entries()
        entry: dict[str, Any] = {
            "seq": len(entries),
            "prev": chain.head,
            "cycle_id": cid,
            "record_digest": json_digest(record),
            "record": json.loads(canonical_json(record)),
        }
        entry["hash"] = _entry_hash(entry)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(canonical_json(entry) + "\n")
        return report

    def _amendment_problems(self, cid: str, record: Mapping[str, Any]) -> list[Finding]:
        """A later revision of the same cycle may add, never remove or rewrite."""
        prior = self.latest(cid)
        if prior is None:
            return []
        out = []
        if prior["anchor"].get("baseline_revision") != record["anchor"].get("baseline_revision"):
            out.append(Finding("BASELINE_MUTATED", "CRITICAL", "integrity",
                               "the baseline of a started cycle cannot change; open a new cycle",
                               "T01"))
        new_f = {f.get("id"): f for f in record.get("failures", [])}
        for f in prior.get("failures", []):
            nf = new_f.get(f.get("id"))
            if nf is None:
                out.append(Finding("FAILURE_ERASED", "CRITICAL", "integrity",
                                   f"amendment removes failure {f.get('id')}", "T09"))
            elif failure_digest(nf) != failure_digest(f):
                out.append(Finding("FAILURE_REWRITTEN", "CRITICAL", "integrity",
                                   f"amendment rewords failure {f.get('id')}", "T09"))
        old_c = {c["candidate_id"]: c for c in prior.get("candidates", [])}
        new_c = {c["candidate_id"]: c for c in record.get("candidates", [])}
        for k, c in old_c.items():
            if k not in new_c:
                out.append(Finding("CANDIDATE_ERASED", "CRITICAL", "integrity",
                                   f"amendment removes candidate {k}; rejected work stays locatable",
                                   "T09"))
            elif new_c[k].get("digest") != c.get("digest"):
                out.append(Finding("CANDIDATE_REWRITTEN", "CRITICAL", "integrity",
                                   f"candidate {k} changed in place; record a new candidate", "T03"))
        old_status = (prior.get("ratification") or {}).get("status")
        if old_status in ("ACCEPTED", "REJECTED", "SUPERSEDED"):
            out.append(Finding("RATIFIED_CYCLE_REOPENED", "CRITICAL", "human",
                               f"cycle {cid} is {old_status}; later work is a new child cycle"))
        return out

    def _concurrency_problems(self, record: Mapping[str, Any]) -> list[Finding]:
        """Two promotions from one baseline that touch the same paths are a conflict."""
        rat = record.get("ratification") or {}
        if rat.get("status") not in ("ACCEPTED", "PARTIAL"):
            return []
        base = record["anchor"].get("baseline_revision")
        mine = _ratified_paths(record)
        out = []
        latest: dict[str, dict[str, Any]] = {}
        for e in self.entries():
            latest[e["cycle_id"]] = e["record"]
        for other_id, other in latest.items():
            if other_id == record.get("cycle_id"):
                continue
            if (other.get("ratification") or {}).get("status") not in ("ACCEPTED", "PARTIAL"):
                continue
            if other["anchor"].get("baseline_revision") != base:
                continue
            overlap = mine & _ratified_paths(other)
            if overlap:
                out.append(Finding("CONCURRENT_CONFLICT", "CRITICAL", "integrity",
                                   f"{other_id} already promoted {sorted(overlap)} from the same "
                                   "baseline; reconcile in a new cycle on the merged state"))
        return out


def _ratified_paths(record: Mapping[str, Any]) -> set[str]:
    cid = (record.get("ratification") or {}).get("candidate_id")
    for c in record.get("candidates", []):
        if c.get("candidate_id") == cid:
            return {str(a.get("path")) for a in c.get("artifacts", [])}
    return set()
