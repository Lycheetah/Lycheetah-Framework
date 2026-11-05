"""Retrospective: encode real Sync Zone events as cycle records and see what the contract sees.

Source: github.com/Lycheetah/lycheetah-sync-zone at a41c2a79d70666f243d971ed8ca70c3a5723973f,
read on 2026-11-06. Digests below were computed from that checkout. The dossier digest is
of the file Mac supplied to this session (LYCHEETAH_SYNC_ZONE_RECURSIVE_MASTER_DOSSIER.md).

Four encodings:

  V1 as written   dispute 1100 settled in the ledger by the seat that wrote the claim,
                  the strawman defender, the run and the verdict.
  V2 charitable   the same, but Mac ratifies it in person.
  V3 dressed up   V2 plus a different-model review that reports no finding.
  H1 handoff      the 2026-11-06 dossier as a handoff that inherits dispute 400's
                  calibration number without dispute 400's verdict.

The point of V3 is the null result: the contract cannot see that the simulation
types in the conclusion it reports. That is a modelling defect, and only a reviewer
who reads the formula can find it.

Run: python3 retrospective_1100.py [--write]   (from this folder)
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from sync_zone import candidate_digest, validate_cycle  # noqa: E402

ZONE_HEAD = "a41c2a79d70666f243d971ed8ca70c3a5723973f"
NOW = "2026-11-06T12:00:00+00:00"

ARTIFACTS_1100 = [
    {"path": "code/24_recursive_dark_node_engine.py",
     "sha256": "c749995120e29a033438f6c7dff8c4d7cb31e3b0b84880a0e1277da2fc6932fb"},
    {"path": "code/25_test_recursive_dark_node_engine.py",
     "sha256": "6f15b7d3acde98afa4b045db633fa82424b0f2b1d5fcbfad5040026dde987c83"},
    {"path": "disputes/1100-the-recursive-orchestrator-invariant/README.md",
     "sha256": "f02dfb3d70666c3da338d8fa1873a7774bc6cef92b04baf4ac441af5a4e5e648"},
    {"path": "disputes/1100-the-recursive-orchestrator-invariant/run.py",
     "sha256": "a8a4c2f311a0478404050bbb0074f94b9c9f020d17424c40c22b9048a424728d"},
]
D1100 = candidate_digest(ARTIFACTS_1100)


def dispute_1100_as_written() -> dict:
    return {
        "schema_version": "sync-zone-cycle-v0.1",
        "cycle_id": "SZ-RETRO-1100",
        "parent_cycle_id": None,
        "depth": 0,
        "anchor": {
            "repository": "Lycheetah/lycheetah-sync-zone",
            "baseline_revision": ZONE_HEAD,
            "ruleset_id": "sz-rules-v0.1",
            "principal": "Mac",
            "governing_contracts": [],
            "authority": {"grants": ["research", "local_code_change"], "revoked": False},
            "budget": {"max_depth": 4, "max_runs": 12},
            "task": {"goal": "settle dispute 1100", "acceptance_criteria": ["run.py prints FALLS"]},
        },
        "runs": [
            {"run_id": "aetheron", "role": "builder", "provider": "google", "model": "Gemini",
             "context_digest": "round-27", "independence": "same_run",
             "observed_by": "self_reported"},
            {"run_id": "pytest", "role": "tool", "provider": "local", "model": "pytest",
             "context_digest": "-", "independence": "deterministic_tool",
             "observed_by": "self_reported"},
        ],
        "candidates": [
            {"candidate_id": "C-1100", "produced_by": "aetheron", "baseline_revision": ZONE_HEAD,
             "artifacts": ARTIFACTS_1100, "digest": D1100, "supersedes": None,
             "meta_governance": False, "effects": ["local_files"]},
        ],
        "evidence": [
            # MEASURED in this session: 7 passed; run.py exits 0 and prints FALLS.
            {"evidence_id": "E-tests", "kind": "UNIT_TEST", "produced_by": "pytest",
             "target_candidate": "C-1100", "target_digest": D1100,
             "command": "pytest code/25_test_recursive_dark_node_engine.py", "outcome": "PASS",
             "observed_at": NOW, "valid_until": None},
        ],
        # The verdict section is written by the claim's author.
        "reviews": [
            {"review_id": "R-verdict", "by": "aetheron", "target_candidate": "C-1100",
             "target_digest": D1100, "modified_candidate": False, "findings": []},
        ],
        "dissent": [],
        "failures": [],
        "stop": {"reason": "COMPLETION", "at": NOW},
        "ratification": {"status": "ACCEPTED", "by": "Aetheron & Mac", "by_kind": "model",
                         "at": "2026-11-05T00:00:00+00:00", "candidate_id": "C-1100",
                         "candidate_digest": D1100},
        "handoff": {"durable_revision": ZONE_HEAD, "carried_authority": [],
                    "next_actions": [], "unresolved": [], "references": []},
    }


def dispute_1100_charitable() -> dict:
    r = dispute_1100_as_written()
    r["ratification"].update({"by": "Mac", "by_kind": "human"})
    return r


def dispute_1100_dressed_up() -> dict:
    r = dispute_1100_charitable()
    r["runs"].append({"run_id": "reviewer-x", "role": "reviewer", "provider": "anthropic",
                      "model": "Claude", "context_digest": "fresh", "independence": "different_model",
                      "observed_by": "self_reported"})
    r["reviews"].append({"review_id": "R-x", "by": "reviewer-x", "target_candidate": "C-1100",
                         "target_digest": D1100, "modified_candidate": False, "findings": []})
    return r


def dossier_handoff() -> dict:
    """The dossier carries dispute 400's number (Brier 0.000428) as calibration evidence.

    Dispute 400 (Nettle, 2026-10-23) found that number measures nothing about calibration:
    all 29 settled entries were committed already HIT. Its ledger line has no later
    RESOLVED entry, so the finding stands. The dossier's handoff omits it.
    """
    r = dispute_1100_charitable()
    r["cycle_id"] = "SZ-RETRO-DOSSIER"
    r["ratification"] = {"status": "PROPOSED", "by": None, "by_kind": None, "at": None,
                         "candidate_id": "C-1100", "candidate_digest": D1100}
    r["stop"] = {"reason": "AUTHORITY", "at": NOW}
    r["handoff"]["durable_revision"] = None
    r["runs"].append({"run_id": "nettle", "role": "reviewer", "provider": "anthropic",
                      "model": "Claude Sonnet", "context_digest": "round-six",
                      "independence": "different_model", "observed_by": "self_reported"})
    r["dissent"].append({
        "dissent_id": "D-400", "by": "nettle", "severity": "HIGH", "status": "OPEN",
        "text": "Brier 0.000428 is correct arithmetic over 29 post-hoc entries; it measures "
                "nothing about calibration (disputes/400, sha256 b3c5409e...)"})
    r["handoff"]["unresolved"] = []  # what the dossier carried forward
    r["handoff"]["references"] = [{
        "path": "LYCHEETAH_SYNC_ZONE_RECURSIVE_MASTER_DOSSIER.md",
        "sha256": "e3b90ee7eeb1d7c87158fdecf833a514ac51b252e9594aa117f28ed54e09e729"}]
    return r


def run_all() -> dict:
    variants = {
        "V1_as_written": dispute_1100_as_written(),
        "V2_charitable": dispute_1100_charitable(),
        "V3_dressed_up": dispute_1100_dressed_up(),
        "H1_dossier_handoff": dossier_handoff(),
    }
    out = {}
    for name, rec in variants.items():
        rep = validate_cycle(copy.deepcopy(rec), now=NOW)
        out[name] = {
            "valid": rep.valid,
            "ratifiable": rep.ratifiable,
            "findings": sorted(rep.codes()),
            "blockers": sorted(rep.blocker_codes()),
            "review_independence": rep.review_independence,
        }
    return out


if __name__ == "__main__":
    result = run_all()
    text = json.dumps(result, indent=2, sort_keys=True)
    print(text)
    if "--write" in sys.argv:
        (HERE.parent / "records" / "retrospective_1100_report.json").write_text(text + "\n")
