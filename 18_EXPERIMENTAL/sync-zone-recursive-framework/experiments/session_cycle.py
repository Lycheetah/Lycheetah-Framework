"""Dogfood: record this forge as cycle SZ-0001 against the real repository.

It computes the candidate from the working tree (every path changed since the baseline,
except this folder's generated `records/`), runs the checks itself, binds each outcome to
the candidate's exact digest, and validates the result. With --write it saves the record,
the report, and appends to the ledger. A rerun after any file changes records a NEW candidate
that supersedes the old one; the old candidate and its evidence stay in the record.

Expected honest state: PROPOSED, valid, NOT ratifiable. Blockers are deliberate truths:
no review by a different model exists, the session dissents from judging its own rules, and
this cycle creates the rules, so it is a meta-governance change only Mac can adopt.

Run from this folder:  python3 -B session_cycle.py [--write] [--skip-full]
"""

from __future__ import annotations

import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PKG = HERE.parent
REPO = PKG.parents[1]
sys.path.insert(0, str(PKG))

from sync_zone import CycleLedger, candidate_digest, sha256_hex, validate_cycle  # noqa: E402
from sync_zone import gitbind  # noqa: E402

BASE = "c4d24c9a72200dc8fe4c29318d55c9127213c0dc"
REL = PKG.relative_to(REPO).as_posix()
RECORDS = PKG / "records"
LEDGER = RECORDS / "SZ-ledger.jsonl"


def _now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0)


def _check(cmd: list[str]) -> tuple[str, str]:
    proc = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
    tail = (proc.stdout.strip().splitlines() or [""])[-1]
    return ("PASS" if proc.returncode == 0 else "FAIL"), tail


def build(skip_full: bool) -> dict:
    now = _now()
    paths = [p for p in gitbind.changed_paths(REPO, BASE) if not p.startswith(f"{REL}/records/")]
    arts = gitbind.artifacts(REPO, paths)
    digest = candidate_digest(arts)

    prior = CycleLedger(LEDGER).latest("SZ-0001") if LEDGER.exists() else None
    candidates = list(prior["candidates"]) if prior else []
    evidence = list(prior["evidence"]) if prior else []
    reviews = list(prior["reviews"]) if prior else []
    same = [c for c in candidates if c["digest"] == digest]
    if same:
        cid = same[0]["candidate_id"]
    else:
        cid = f"C{len(candidates) + 1}"
        candidates.append({
            "candidate_id": cid, "produced_by": "r-claude", "baseline_revision": BASE,
            "artifacts": arts, "digest": digest,
            "supersedes": candidates[-1]["candidate_id"] if candidates else None,
            "meta_governance": True, "effects": ["local_files"],
        })

    py = sys.executable
    checks = [("STATIC_CHECK", [py, "-m", "ruff", "check", REL, "tests/test_sync_zone_cycle.py"]),
              ("UNIT_TEST", [py, "-m", "pytest", "-q", "-p", "no:cacheprovider",
                             "tests/test_sync_zone_cycle.py"])]
    if not skip_full:
        checks.append(("INTEGRATION_TEST", [py, "-m", "pytest", "-q", "-p", "no:cacheprovider"]))
    for kind, cmd in checks:
        outcome, tail = _check(cmd)
        evidence.append({
            "evidence_id": f"E{len(evidence) + 1}", "kind": kind, "produced_by": "r-pytest",
            "target_candidate": cid, "target_digest": digest, "command": " ".join(cmd[1:]),
            "outcome": outcome, "summary": tail, "observed_at": now.isoformat(),
            "valid_until": (now + dt.timedelta(days=7)).isoformat(),
        })
    reviews.append({
        "review_id": f"RV{len(reviews) + 1}", "by": "r-claude", "target_candidate": cid,
        "target_digest": digest, "modified_candidate": False,
        "findings": [], "note": "author self-review incl. mutation probes M1-M8 (SZF-05)",
    })

    contracts = [{"path": p, "sha256": sha256_hex((REPO / p).read_bytes())}
                 for p in ("AGENTS.md", "CLAUDE.md", "WORKING_HOME.md", "CONTRIBUTING.md")]
    refs = [{"path": f"{REL}/{p}", "sha256": sha256_hex((PKG / p).read_bytes())}
            for p in ("README.md", "PROTOCOL.md", "SYNC_ZONE_FINDINGS.md")]
    dissent = [{
        "dissent_id": "D-SELF-RULES", "by": "r-claude", "severity": "HIGH", "status": "OPEN",
        "text": "The rules this cycle is judged by were written in this cycle by the same "
                "session. Only Mac can adopt a genesis ruleset; nothing here can.",
    }]
    failures = [
        {"id": "SZF-02", "text": "Workshop dispute 1100 is circular by construction."},
        {"id": "SZF-04", "text": "The 2026-11-06 dossier dropped dispute 400's standing finding."},
        {"id": "SZF-05", "text": "Two of this session's own tests were vacuous under mutation (M4, M5)."},
        {"id": "SZF-06", "text": "A limit test first failed on a fixture budget error, not the validator."},
    ]
    return {
        "schema_version": "sync-zone-cycle-v0.1",
        "cycle_id": "SZ-0001",
        "parent_cycle_id": None,
        "depth": 0,
        "anchor": {
            "repository": "Lycheetah/Lycheetah-Framework",
            "baseline_revision": BASE,
            "ruleset_id": "sz-rules-v0.1",
            "principal": "Mac",
            "governing_contracts": contracts,
            "authority": {"grants": ["research", "local_code_change"],
                          "expires_at": "2026-11-13T00:00:00+00:00", "revoked": False,
                          "source": "Mac's request in the session; push to the Framework not granted"},
            "budget": {"max_depth": 4, "max_runs": 12},
            "task": {"goal": "Investigate, formalize, falsify and minimally scaffold the Sync Zone "
                             "cycle contract (Cassian's packet)",
                     "acceptance_criteria": ["integration map", "validator + negative tests",
                                             "no suite regression", "honest handoff"]},
        },
        "runs": [
            {"run_id": "r-claude", "role": "builder", "provider": "anthropic",
             "model": "Claude (Claude Code cloud session; model id not recorded)",
             "context_digest": "forge-2026-11-06", "independence": "same_run",
             "observed_by": "self_reported"},
            {"run_id": "r-pytest", "role": "tool", "provider": "local", "model": "pytest/ruff",
             "context_digest": "-", "independence": "deterministic_tool",
             "observed_by": "self_reported"},
        ],
        "candidates": candidates,
        "evidence": evidence,
        "reviews": reviews,
        "dissent": dissent,
        "failures": failures,
        "stop": {"reason": "AUTHORITY", "at": now.isoformat()},
        "ratification": {"status": "PROPOSED", "by": None, "by_kind": None, "at": None,
                         "candidate_id": cid, "candidate_digest": digest},
        "handoff": {
            "durable_revision": None,
            "carried_authority": [],
            "next_actions": ["Mac: ratify, amend or reject sz-rules-v0.1 (genesis ruleset)",
                             "Different-model review of this branch (e.g. Caelorynth)",
                             "Matched comparator: handoff fidelity, ordinary note vs cycle record"],
            "unresolved": ["D-SELF-RULES"],
            "references": refs,
        },
    }


def main() -> int:
    record = build("--skip-full" in sys.argv)
    report = validate_cycle(record, now=_now(), repo_root=REPO)
    out = report.to_dict()
    print(json.dumps({"candidate": record["ratification"]["candidate_id"],
                      "digest": record["ratification"]["candidate_digest"],
                      "evidence": [(e["evidence_id"], e["kind"], e["outcome"], e["summary"])
                                   for e in record["evidence"]],
                      **out}, indent=2))
    if "--write" in sys.argv:
        RECORDS.mkdir(exist_ok=True)
        CycleLedger(LEDGER).append(record, now=_now(), repo_root=REPO)
        (RECORDS / "SZ-0001.json").write_text(json.dumps(record, indent=2) + "\n")
        (RECORDS / "SZ-0001_report.json").write_text(json.dumps(out, indent=2) + "\n")
    return 0 if report.valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
