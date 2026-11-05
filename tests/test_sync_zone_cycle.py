"""Sync Zone cycle contract: positive, negative and tampering cases.  [SCAFFOLD]

Claim coverage (18_EXPERIMENTAL/sync-zone-recursive-framework/CLAIMS_AND_LIMITS.md):
  [SCAFFOLD] the validator detects each listed contract violation in a hand-written record
  [SCAFFOLD] the ledger refuses rewrites and names a broken chain
  Limits pinned as tests (test_limit_*): what the validator provably cannot see.

These are author-written engineering checks. They are not independent validation and
they say nothing about whether any real cycle was well run.
"""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "18_EXPERIMENTAL" / "sync-zone-recursive-framework"))

from sync_zone import (  # noqa: E402
    CycleLedger,
    LedgerRefused,
    Policy,
    candidate_digest,
    validate_cycle,
)
from sync_zone import gitbind  # noqa: E402

pytestmark = pytest.mark.scaffold

BASE = "c4d24c9a72200dc8fe4c29318d55c9127213c0dc"
DURABLE = "1111111111111111111111111111111111111111"
NOW = "2026-11-06T12:00:00+00:00"
H1 = "a" * 64
H2 = "b" * 64
NOTE = "18_EXPERIMENTAL/demo/notes.md"


def _digest(arts):
    # Independent recomputation: sorted rows, compact sorted-key JSON, sha256.
    rows = sorted(((a["path"], a["sha256"]) for a in arts))
    body = json.dumps([{"path": p, "sha256": h} for p, h in rows],
                      sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(body.encode()).hexdigest()


def proposed():
    arts = [{"path": NOTE, "sha256": H1}]
    return {
        "schema_version": "sync-zone-cycle-v0.1",
        "cycle_id": "SZ-T-0001",
        "parent_cycle_id": None,
        "depth": 0,
        "anchor": {
            "repository": "Lycheetah/Lycheetah-Framework",
            "baseline_revision": BASE,
            "ruleset_id": "sz-rules-v0.1",
            "principal": "Mac",
            "governing_contracts": [{"path": "AGENTS.md", "sha256": H2}],
            "authority": {"grants": ["research", "local_code_change"],
                          "expires_at": "2026-11-07T00:00:00+00:00", "revoked": False},
            "budget": {"max_depth": 3, "max_runs": 6},
            "task": {"goal": "write a note", "acceptance_criteria": ["note exists"]},
        },
        "runs": [
            {"run_id": "r-build", "role": "builder", "provider": "anthropic", "model": "m-a",
             "context_digest": "ctx-1", "independence": "same_run", "observed_by": "self_reported"},
            {"run_id": "r-review", "role": "reviewer", "provider": "openai", "model": "m-b",
             "context_digest": "ctx-2", "independence": "different_model",
             "observed_by": "self_reported"},
            {"run_id": "r-test", "role": "tool", "provider": "local", "model": "pytest",
             "context_digest": "-", "independence": "deterministic_tool",
             "observed_by": "self_reported"},
        ],
        "candidates": [
            {"candidate_id": "C1", "produced_by": "r-build", "baseline_revision": BASE,
             "artifacts": arts, "digest": _digest(arts), "supersedes": None,
             "meta_governance": False, "effects": ["local_files"]},
        ],
        "evidence": [
            {"evidence_id": "E1", "kind": "UNIT_TEST", "produced_by": "r-test",
             "target_candidate": "C1", "target_digest": _digest(arts),
             "command": "pytest tests/test_demo.py", "outcome": "PASS",
             "observed_at": "2026-11-06T11:00:00+00:00", "valid_until": None},
        ],
        "reviews": [
            {"review_id": "RV1", "by": "r-review", "target_candidate": "C1",
             "target_digest": _digest(arts), "modified_candidate": False, "findings": []},
        ],
        "dissent": [],
        "failures": [{"id": "F1", "text": "first draft hard-coded its own verdict"}],
        "stop": {"reason": "AUTHORITY", "at": NOW},
        "ratification": {"status": "PROPOSED", "by": None, "by_kind": None, "at": None,
                         "candidate_id": "C1", "candidate_digest": _digest(arts)},
        "handoff": {"durable_revision": None, "carried_authority": [],
                    "next_actions": ["Mac reviews C1"], "unresolved": [], "references": []},
    }


def accepted():
    r = proposed()
    r["ratification"].update({"status": "ACCEPTED", "by": "Mac", "by_kind": "human", "at": NOW})
    r["stop"]["reason"] = "COMPLETION"
    r["handoff"]["durable_revision"] = DURABLE
    return r


def child_of(parent):
    c = copy.deepcopy(parent)
    c["cycle_id"] = parent["cycle_id"] + "-child"
    c["parent_cycle_id"] = parent["cycle_id"]
    c["depth"] = parent.get("depth", 0) + 1
    c["anchor"]["baseline_revision"] = DURABLE
    for cand in c["candidates"]:
        cand["baseline_revision"] = DURABLE
    c["ratification"] = {"status": "PROPOSED", "by": None, "by_kind": None, "at": None,
                         "candidate_id": "C1", "candidate_digest": c["candidates"][0]["digest"]}
    c["stop"] = {"reason": "AUTHORITY", "at": NOW}
    c["handoff"]["durable_revision"] = None
    return c


def check(r, **kw):
    kw.setdefault("now", NOW)
    return validate_cycle(r, **kw)


def rebind(r, cid="C1"):
    """Honestly re-record a candidate after its artifacts changed: new digest, old evidence stale."""
    for c in r["candidates"]:
        if c["candidate_id"] == cid:
            c["digest"] = candidate_digest(c["artifacts"])
    r["ratification"]["candidate_digest"] = [c for c in r["candidates"] if c["candidate_id"] == cid][0]["digest"]


# -- positive -------------------------------------------------------------------

def test_digest_matches_independent_recomputation():
    arts = [{"path": "b", "sha256": H2}, {"path": "a", "sha256": None}]
    assert candidate_digest(arts) == _digest(arts)


def test_proposed_cycle_is_valid_and_ratifiable():
    rep = check(proposed())
    assert rep.valid and rep.ratifiable, rep.to_dict()
    assert rep.review_independence == {"RV1": "different_model"}


def test_accepted_cycle_by_principal_is_valid():
    rep = check(accepted())
    assert rep.valid, rep.to_dict()
    assert set(rep.gates().values()) == {"PASS"}


def test_valid_child_cycle():
    rep = check(child_of(accepted()), parent=accepted())
    assert rep.valid, rep.to_dict()


# -- 1-2 baseline -----------------------------------------------------------------

def test_baseline_mismatch():
    r = proposed()
    r["candidates"][0]["baseline_revision"] = DURABLE
    assert "BASELINE_MISMATCH" in check(r).codes()


def test_missing_baseline():
    r = proposed()
    r["anchor"]["baseline_revision"] = "HEAD"
    assert "BASELINE_MISSING" in check(r).codes()


def test_baseline_mutated_after_cycle_start(tmp_path):
    led = CycleLedger(tmp_path / "ledger.jsonl")
    led.append(proposed(), now=NOW)
    r = proposed()
    r["anchor"]["baseline_revision"] = DURABLE
    for c in r["candidates"]:
        c["baseline_revision"] = DURABLE
    with pytest.raises(LedgerRefused) as err:
        led.append(r, now=NOW)
    assert "BASELINE_MUTATED" in str(err.value)


# -- 3-4 candidate and reviewer mutation ----------------------------------------

def test_candidate_changed_after_verification_tampered_digest():
    r = proposed()
    r["candidates"][0]["artifacts"][0]["sha256"] = H2
    assert "CANDIDATE_DIGEST_MISMATCH" in check(r).codes()


def test_candidate_changed_after_verification_honest_rerecord_makes_old_pass_stale():
    r = proposed()
    r["candidates"][0]["artifacts"][0]["sha256"] = H2
    rebind(r)
    rep = check(r)
    assert "STALE_BINDING" in rep.codes()
    assert "NO_BOUND_PASS" in rep.blocker_codes()


def test_reviewer_mutation_unrecorded():
    r = proposed()
    r["reviews"][0]["modified_candidate"] = True
    assert "REVIEWER_MUTATION_UNRECORDED" in check(r).codes()


def test_reviewer_who_edits_becomes_producer_and_cannot_certify_own_edit():
    r = proposed()
    arts = [{"path": NOTE, "sha256": H2}]
    r["candidates"].append({"candidate_id": "C2", "produced_by": "r-review",
                            "baseline_revision": BASE, "artifacts": arts,
                            "digest": _digest(arts), "supersedes": "C1",
                            "meta_governance": False, "effects": ["local_files"]})
    r["reviews"][0].update({"modified_candidate": True, "produced_candidate": "C2"})
    r["ratification"].update({"candidate_id": "C2", "candidate_digest": _digest(arts)})
    rep = check(r)
    assert rep.valid, rep.to_dict()
    assert {"NO_INDEPENDENT_REVIEW", "NO_BOUND_PASS"} <= rep.blocker_codes()


# -- 5-7 provenance and independence --------------------------------------------

def test_missing_provenance():
    r = proposed()
    r["candidates"][0]["produced_by"] = "r-ghost"
    assert "MISSING_PROVENANCE" in check(r).codes()


def test_duplicate_agent_identity():
    r = proposed()
    r["runs"].append(dict(r["runs"][0]))
    assert "DUPLICATE_ID" in check(r).codes()
    r = proposed()
    twin = dict(r["runs"][0], run_id="r-build-2")
    r["runs"].append(twin)
    assert "DUPLICATE_RUN_IDENTITY" in check(r).codes()


def test_same_model_falsely_labelled_independent():
    r = proposed()
    r["runs"][1].update({"provider": "anthropic", "model": "m-a", "context_digest": "ctx-1"})
    rep = check(r)
    assert "FALSE_INDEPENDENCE" in rep.codes()
    assert rep.review_independence["RV1"] == "same_model_same_context"
    assert "NO_INDEPENDENT_REVIEW" in rep.blocker_codes()


def test_self_review_cannot_certify():
    r = proposed()
    r["reviews"][0]["by"] = "r-build"
    rep = check(r)
    assert rep.review_independence["RV1"] == "same_run"
    assert "NO_INDEPENDENT_REVIEW" in rep.blocker_codes()


def test_self_review_is_same_run_even_when_the_run_claims_more():
    # Mutation probe M4: the builder's own label must not lift its self-review.
    r = proposed()
    r["runs"][0]["independence"] = "different_model"
    r["reviews"][0]["by"] = "r-build"
    rep = check(r)
    assert rep.review_independence["RV1"] == "same_run"
    assert "NO_INDEPENDENT_REVIEW" in rep.blocker_codes()


def test_fresh_context_same_model_is_counted_but_not_called_different():
    r = proposed()
    r["runs"][1].update({"provider": "anthropic", "model": "m-a", "independence": "same_model_fresh_context"})
    rep = check(r)
    assert rep.valid and rep.ratifiable
    assert rep.review_independence["RV1"] == "same_model_fresh_context"


def test_model_cannot_produce_human_review_evidence():
    r = proposed()
    r["evidence"].append(dict(r["evidence"][0], evidence_id="E2", kind="INDEPENDENT_EXTERNAL_REVIEW",
                              produced_by="r-review"))
    assert "EVIDENCE_LABEL_INFLATION" in check(r).codes()


# -- 8-9 authority ----------------------------------------------------------------

def test_child_authority_greater_than_parent():
    parent = accepted()
    c = child_of(parent)
    c["anchor"]["authority"]["grants"].append("publish")
    assert "AUTHORITY_WIDENED" in check(c, parent=parent).codes()


def test_child_authority_cannot_outlive_parent():
    parent = accepted()
    c = child_of(parent)
    c["anchor"]["authority"]["expires_at"] = "2027-01-01T00:00:00+00:00"
    assert "AUTHORITY_OUTLIVES_PARENT" in check(c, parent=parent).codes()


def test_expired_authority_blocks_and_accepting_anyway_is_critical():
    r = proposed()
    r["anchor"]["authority"]["expires_at"] = "2026-11-06T00:00:00+00:00"
    assert "AUTHORITY_EXPIRED" in check(r).blocker_codes()
    a = accepted()
    a["anchor"]["authority"]["expires_at"] = "2026-11-06T00:00:00+00:00"
    assert "PROMOTED_WITH_BLOCKER" in check(a).codes()


def test_revoked_authority_blocks():
    r = proposed()
    r["anchor"]["authority"]["revoked"] = True
    assert "AUTHORITY_REVOKED" in check(r).blocker_codes()


def test_authority_creep_through_handoff_text():
    r = proposed()
    r["handoff"]["carried_authority"] = ["research", "deploy"]
    assert "AUTHORITY_CREEP_IN_HANDOFF" in check(r).codes()


def test_helpful_but_unauthorized_patch_is_kept_not_promoted():
    r = proposed()
    r["anchor"]["authority"]["grants"] = ["research"]
    rep = check(r)
    assert rep.valid  # the artifact may be retained
    assert "AUTHORITY_SCOPE" in rep.blocker_codes()


# -- 10-12 evidence ---------------------------------------------------------------

def test_stale_evidence():
    r = proposed()
    r["evidence"][0]["valid_until"] = "2026-11-05T00:00:00+00:00"
    rep = check(r)
    assert {"EVIDENCE_EXPIRED", "NO_BOUND_PASS"} <= rep.blocker_codes()


def test_missing_test_result():
    r = accepted()
    r["evidence"] = []
    rep = check(r)
    assert "PROMOTED_WITH_BLOCKER" in rep.codes()
    r = proposed()
    r["evidence"][0]["outcome"] = "NOT_RUN"
    assert "NO_BOUND_PASS" in check(r).blocker_codes()


def test_test_result_refers_to_different_revision():
    r = proposed()
    r["candidates"][0]["result_revision"] = DURABLE
    r["evidence"][0]["revision"] = BASE
    rep = check(r)
    assert "EVIDENCE_REVISION_MISMATCH" in rep.codes()
    assert "NO_BOUND_PASS" in rep.blocker_codes()


def test_failing_bound_test_blocks():
    r = proposed()
    r["evidence"].append(dict(r["evidence"][0], evidence_id="E2", outcome="FAIL"))
    assert "FAILING_EVIDENCE" in check(r).blocker_codes()


# -- 13 dissent -------------------------------------------------------------------

def test_unresolved_critical_dissent_blocks():
    r = proposed()
    r["dissent"].append({"dissent_id": "D1", "by": "r-review", "severity": "CRITICAL",
                         "text": "the test asserts the fixture", "status": "OPEN"})
    r["handoff"]["unresolved"] = ["D1"]
    rep = check(r)
    assert rep.valid
    assert "OPEN_CRITICAL_DISSENT" in rep.blocker_codes()


def test_consensus_cannot_launder_a_minority_objection():
    r = proposed()
    for i in range(2, 6):
        r["runs"].append({"run_id": f"r-rev{i}", "role": "reviewer", "provider": f"p{i}",
                          "model": f"m{i}", "context_digest": f"c{i}",
                          "independence": "different_model", "observed_by": "self_reported"})
        r["reviews"].append(dict(r["reviews"][0], review_id=f"RV{i}", by=f"r-rev{i}"))
    r["reviews"][0]["findings"] = [{"id": "K1", "severity": "HIGH", "text": "off by one",
                                    "status": "OPEN"}]
    r["handoff"]["unresolved"] = ["K1"]
    assert "OPEN_CRITICAL_DISSENT" in check(r).blocker_codes()


def test_only_the_principal_may_overrule():
    r = proposed()
    r["dissent"].append({"dissent_id": "D1", "by": "r-review", "severity": "HIGH",
                         "text": "x", "status": "OVERRULED", "overruled_by": "r-build"})
    assert "DISSENT_OVERRULED_BY_NON_PRINCIPAL" in check(r).codes()


def test_addressed_dissent_must_name_its_evidence():
    r = proposed()
    r["dissent"].append({"dissent_id": "D1", "by": "r-review", "severity": "HIGH",
                         "text": "x", "status": "ADDRESSED", "addressed_by": "trust me"})
    assert "DISSENT_ADDRESSED_WITHOUT_REF" in check(r).codes()


def test_summary_drift_drops_caveat_from_handoff():
    r = proposed()
    r["dissent"].append({"dissent_id": "D400", "by": "r-review", "severity": "HIGH",
                         "text": "calibration score measures post-hoc entries only",
                         "status": "OPEN"})
    assert "CAVEAT_DROPPED_FROM_HANDOFF" in check(r).codes()


def test_parent_open_dissent_must_be_carried():
    parent = proposed()
    parent["dissent"].append({"dissent_id": "D1", "by": "r-review", "severity": "MEDIUM",
                              "text": "x", "status": "OPEN"})
    c = child_of(parent)
    c["dissent"] = []
    assert "DISSENT_DROPPED" in check(c, parent=parent).codes()


# -- 14 failure retention ---------------------------------------------------------

def test_failure_deleted_in_child():
    parent = accepted()
    c = child_of(parent)
    c["failures"] = []
    assert "FAILURE_ERASED" in check(c, parent=parent).codes()


def test_failure_reworded_in_child():
    parent = accepted()
    c = child_of(parent)
    c["failures"][0]["text"] = "minor draft issue"
    assert "FAILURE_REWRITTEN" in check(c, parent=parent).codes()


def test_failure_superseded_not_deleted_is_fine():
    parent = accepted()
    c = child_of(parent)
    c["failures"][0]["superseded_by"] = "E1"
    assert check(c, parent=parent).valid


def test_ledger_refuses_failure_deletion_in_amendment(tmp_path):
    led = CycleLedger(tmp_path / "l.jsonl")
    led.append(proposed(), now=NOW)
    r = proposed()
    r["failures"] = []
    with pytest.raises(LedgerRefused) as err:
        led.append(r, now=NOW)
    assert "FAILURE_ERASED" in str(err.value)


# -- 15-16 ratification and meta-governance -------------------------------------

def test_accepted_without_human_ratification():
    r = accepted()
    r["ratification"].update({"by": "Sol", "by_kind": "model"})
    assert "FALSE_RATIFICATION" in check(r).codes()


def test_human_who_is_not_principal_cannot_ratify():
    r = accepted()
    r["ratification"]["by"] = "Someone"
    assert "RATIFIER_NOT_PRINCIPAL" in check(r).codes()


def test_ratified_digest_must_match_candidate():
    r = accepted()
    r["ratification"]["candidate_digest"] = H1
    assert "RATIFIED_WRONG_REVISION" in check(r).codes()


def _meta(r):
    arts = [{"path": "18_EXPERIMENTAL/sync-zone-recursive-framework/sync_zone/validator.py", "sha256": H2}]
    c = r["candidates"][0]
    c.update({"artifacts": arts, "digest": _digest(arts), "meta_governance": True})
    r["evidence"][0]["target_digest"] = c["digest"]
    r["reviews"][0]["target_digest"] = c["digest"]
    r["ratification"]["candidate_digest"] = c["digest"]
    return r


def test_meta_change_without_separate_ratification():
    rep = check(_meta(accepted()))
    assert "PROMOTED_WITH_BLOCKER" in rep.codes()
    assert any("META_CHANGE" in f.message for f in rep.findings)


def test_meta_change_with_separate_ack_under_old_rules():
    r = _meta(accepted())
    r["ratification"]["meta_governance_ack"] = {
        "by": "Mac", "ruleset_before": "sz-rules-v0.1", "ruleset_after": "sz-rules-v0.2",
        "separate_review": "RV1 plus Mac read of the diff", "at": NOW}
    assert check(r).valid, check(r).to_dict()


def test_undeclared_meta_change():
    r = _meta(proposed())
    r["candidates"][0]["meta_governance"] = False
    assert "UNDECLARED_META_CHANGE" in check(r).codes()


def test_rule_change_cannot_judge_its_own_adoption():
    r = _meta(accepted())
    r["ratification"]["meta_governance_ack"] = {
        "by": "Mac", "ruleset_before": "sz-rules-v0.1", "ruleset_after": "sz-rules-v0.1",
        "separate_review": "x"}
    assert "SELF_JUDGED_RULE_CHANGE" in check(r).codes()


def test_ruleset_change_between_cycles_needs_ratified_meta_change():
    parent = accepted()
    c = child_of(parent)
    c["anchor"]["ruleset_id"] = "sz-rules-v0.2"
    rep = check(c, parent=parent, policy=Policy(ruleset_id="sz-rules-v0.2"))
    assert "RULESET_CHANGED_WITHOUT_RATIFICATION" in rep.codes()


def test_cycle_is_judged_by_the_rules_it_started_under():
    r = proposed()
    assert "RULESET_MISMATCH" in check(r, policy=Policy(ruleset_id="sz-rules-v0.2")).codes()


def test_deleting_a_judging_test_is_a_meta_change():
    r = proposed()
    arts = [{"path": NOTE, "sha256": H1}, {"path": "tests/test_demo.py", "sha256": None}]
    c = r["candidates"][0]
    c.update({"artifacts": arts, "digest": _digest(arts)})
    assert "TEST_DELETION" in check(r).codes()


# -- 17-18 stopping -------------------------------------------------------------

def test_depth_exhausted():
    parent = accepted()
    parent["depth"] = 3
    c = child_of(parent)
    assert "DEPTH_EXHAUSTED" in check(c, parent=parent).codes()
    c["stop"]["reason"] = "BUDGET"
    assert "DEPTH_EXHAUSTED" not in check(c, parent=parent).codes()


def test_run_budget_exceeded():
    r = proposed()
    r["anchor"]["budget"]["max_runs"] = 2
    assert "BUDGET_EXCEEDED" in check(r).codes()


def test_child_cannot_widen_budget():
    parent = accepted()
    c = child_of(parent)
    c["anchor"]["budget"]["max_runs"] = 99
    assert "BUDGET_WIDENED" in check(c, parent=parent).codes()


def test_no_change_must_stop_with_convergence():
    parent = accepted()
    c = child_of(parent)
    c["ratification"].update({"status": "ACCEPTED", "by": "Mac", "by_kind": "human", "at": NOW})
    c["stop"]["reason"] = "COMPLETION"
    c["handoff"]["durable_revision"] = DURABLE
    assert "PROMOTED_WITH_BLOCKER" in check(c, parent=parent).codes()


def test_every_cycle_says_why_it_stopped():
    r = proposed()
    r["stop"] = {}
    assert "STOP_MISSING" in check(r).codes()


# -- 19 concurrency; 20 unknown effect; 21 tampering; 22 handoff -------------------

def test_concurrent_promotions_from_one_baseline_conflict(tmp_path):
    led = CycleLedger(tmp_path / "l.jsonl")
    led.append(accepted(), now=NOW)
    other = accepted()
    other["cycle_id"] = "SZ-T-0002"
    with pytest.raises(LedgerRefused) as err:
        led.append(other, now=NOW)
    assert "CONCURRENT_CONFLICT" in str(err.value)


def test_ratified_cycle_cannot_be_reopened(tmp_path):
    led = CycleLedger(tmp_path / "l.jsonl")
    led.append(accepted(), now=NOW)
    with pytest.raises(LedgerRefused) as err:
        led.append(proposed(), now=NOW)
    assert "RATIFIED_CYCLE_REOPENED" in str(err.value)


def test_unknown_external_effect_blocks():
    r = proposed()
    r["anchor"]["authority"]["grants"].append("external_effect")
    r["candidates"][0]["effects"] = ["local_files", "external"]
    r["evidence"].append(dict(r["evidence"][0], evidence_id="E2", kind="ACTION_RECEIPT",
                              outcome="UNKNOWN"))
    assert "EFFECT_UNKNOWN" in check(r).blocker_codes()
    r["evidence"][1]["outcome"] = "SUCCEEDED"
    assert check(r).ratifiable


def test_external_effect_without_grant_or_receipt():
    r = proposed()
    r["candidates"][0]["effects"] = ["external"]
    rep = check(r)
    assert {"AUTHORITY_SCOPE", "EFFECT_WITHOUT_RECEIPT"} <= rep.blocker_codes()


def test_ledger_chain_detects_tampering(tmp_path):
    path = tmp_path / "l.jsonl"
    led = CycleLedger(path)
    led.append(proposed(), now=NOW)
    second = proposed()
    second["cycle_id"] = "SZ-T-0002"
    led.append(second, now=NOW)
    assert led.verify().ok
    lines = path.read_text().splitlines()
    tampered = json.loads(lines[0])
    tampered["record"]["failures"] = []
    lines[0] = json.dumps(tampered, sort_keys=True, separators=(",", ":"))
    path.write_text("\n".join(lines) + "\n")
    rep = led.verify()
    assert not rep.ok and "line 0" in rep.problem
    with pytest.raises(LedgerRefused):
        led.append(proposed(), now=NOW)


def test_ledger_detects_removed_line(tmp_path):
    path = tmp_path / "l.jsonl"
    led = CycleLedger(path)
    for i in range(3):
        r = proposed()
        r["cycle_id"] = f"SZ-T-{i}"
        led.append(r, now=NOW)
    lines = path.read_text().splitlines()
    path.write_text("\n".join([lines[0], lines[2]]) + "\n")
    assert not led.verify().ok


def test_ledger_detects_splice_by_forger_who_knows_the_hash(tmp_path):
    # Mutation probe M5: drop a line, renumber, recompute every per-entry hash.
    # Only the prev-link exposes it, because the forger did not rebuild the chain.
    from sync_zone.ledger import _entry_hash

    path = tmp_path / "l.jsonl"
    led = CycleLedger(path)
    for i in range(3):
        r = proposed()
        r["cycle_id"] = f"SZ-T-{i}"
        led.append(r, now=NOW)
    entries = [json.loads(x) for x in path.read_text().splitlines()]
    forged = [entries[0], dict(entries[2], seq=1)]
    forged[1]["hash"] = _entry_hash(forged[1])
    path.write_text("".join(json.dumps(e, sort_keys=True, separators=(",", ":")) + "\n" for e in forged))
    rep = led.verify()
    assert not rep.ok and "chain broken" in rep.problem


def test_handoff_points_to_missing_artifact(tmp_path):
    r = proposed()
    r["handoff"]["references"] = [{"path": "gone.md", "sha256": H1}]
    assert "HANDOFF_MISSING_ARTIFACT" in check(r, repo_root=tmp_path).codes()
    (tmp_path / "gone.md").write_text("now here")
    assert "HANDOFF_ARTIFACT_CHANGED" in check(r, repo_root=tmp_path).codes()


def test_governing_contract_changed_since_anchor(tmp_path):
    (tmp_path / "AGENTS.md").write_text("edited")
    assert "CONTRACT_CHANGED" in check(proposed(), repo_root=tmp_path).blocker_codes()


def test_accepted_handoff_needs_durable_revision():
    r = accepted()
    r["handoff"]["durable_revision"] = None
    assert "HANDOFF_NO_DURABLE_REVISION" in check(r).codes()


# -- limits the validator cannot cross (pinned so nobody upgrades them by prose) ----

def test_limit_shared_fabricated_source_passes_structure():
    """Case B: five models citing one fabricated source. Structure cannot see it.

    It can say the reviewers shared one context (MEDIUM, non-blocking); it cannot say
    the source is fabricated. That needs EXTERNAL_SOURCE evidence.
    """
    r = proposed()
    r["anchor"]["budget"]["max_runs"] = 10
    for i in range(2, 6):
        r["runs"].append({"run_id": f"r-rev{i}", "role": "reviewer", "provider": f"p{i}",
                          "model": f"m{i}", "context_digest": "shared-packet",
                          "independence": "different_model", "observed_by": "self_reported"})
        r["reviews"].append(dict(r["reviews"][0], review_id=f"RV{i}", by=f"r-rev{i}"))
    rep = check(r)
    assert "SHARED_REVIEW_CONTEXT" in rep.codes()
    assert rep.ratifiable  # source verification is EXTERNAL_SOURCE work, not this check


def test_limit_human_identity_is_declared_not_authenticated():
    r = accepted()
    r["ratification"]["by"] = "Mac"  # any process can type this string
    assert check(r).valid


# -- git binding --------------------------------------------------------------------

def test_gitbind_binds_worktree_candidate(tmp_path):
    def git(*a):
        subprocess.run(["git", "-C", str(tmp_path), *a], check=True, capture_output=True)
    git("init", "-q")
    git("config", "user.email", "t@example.invalid")
    git("config", "user.name", "t")
    (tmp_path / "a.txt").write_text("one")
    git("add", "a.txt")
    git("commit", "-q", "-m", "base")
    base = gitbind.head(tmp_path)
    (tmp_path / "a.txt").write_text("two")
    (tmp_path / "b.txt").write_text("new")
    cand = gitbind.candidate_from_worktree(tmp_path, base, "C1", "r-build")
    assert [a["path"] for a in cand["artifacts"]] == ["a.txt", "b.txt"]
    assert cand["artifacts"][0]["sha256"] == hashlib.sha256(b"two").hexdigest()
    assert cand["digest"] == _digest(cand["artifacts"])
    with pytest.raises(gitbind.GitBindError):
        gitbind.assert_baseline(tmp_path, "0" * 40)
