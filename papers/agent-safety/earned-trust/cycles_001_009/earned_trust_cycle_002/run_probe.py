"""Reproducible representative negative/positive checks, no external API."""
import concurrent.futures
import json
import tempfile
from pathlib import Path
from transactional_provider import ConditionalRefundProvider, Intent, LostResponse


def probe_one(case, mutation=None, *, outcome_loss=False):
    with tempfile.TemporaryDirectory() as d:
        p = ConditionalRefundProvider(Path(d)/"provider.sqlite")
        i = Intent("effect-1", "approval-1", "agent-1", "ORDER-17", 1200)
        p.seed(i)
        before = p.preview(i).code
        if mutation:
            mutation(p, i)
        try:
            after = p.commit(i, lose_response=outcome_loss)
            result = after.code
        except LostResponse:
            result = "RESPONSE_LOST_AFTER_COMMIT"
        return {"case":case, "admission_snapshot": before, "commit":result,
                "effect_count":p.effect_count(), "independent_truth_eligible":p.recorded_truth_for(i.subject),
                "reconciliation": p.reconcile(i).code}


def run():
    cases = [
        probe_one("stable_authorized"),
        probe_one("revoke_after_snapshot",lambda p,i:p.change(actor=i.actor,revoke=True)),
        probe_one("evidence_revoked_after_snapshot",lambda p,i:p.change(subject=i.subject,eligible=False,truth=False)),
        probe_one("max_policy_reduced",lambda p,i:p.change(maximum=1000)),
        probe_one("evidence_status_failed",lambda p,i:p.change(subject=i.subject,evidence_status="FAIL")),
        probe_one("authority_is_wrong",lambda p,i:p.change(subject=i.subject,truth=False)),
        probe_one("commit_reply_lost",outcome_loss=True),
    ]
    with tempfile.TemporaryDirectory() as d:
        p=ConditionalRefundProvider(Path(d)/"provider.sqlite")
        i=Intent("effect-concurrent","approval-concurrent","agent-1","ORDER-17",1200)
        p.seed(i)
        with concurrent.futures.ThreadPoolExecutor(max_workers=16) as pool:
            responses=list(pool.map(lambda _:p.commit(i).code,range(32)))
        concurrency={"workers_submissions":len(responses),"committed_responses":responses.count("COMMITTED"),
                     "idempotent_replay_responses":responses.count("IDEMPOTENT_REPLAY"),"effect_count":p.effect_count()}
    return {"evidence_status":"SYNTHETIC_LOCAL_SQLITE", "cases":cases,"concurrency":concurrency,
            "limitations":["A single SQLite database implements all simulated provider checks",
                           "No authentic external payments, data producers, processes, authentication, or network",
                           "True eligibility is an independent modeled oracle, not a provider sensor",
                           "This tests no actual Lycheetah runtime modules; run run_framework_contract.py inside the real repo"]}


if __name__ == "__main__":
    print(json.dumps(run(),indent=2))
