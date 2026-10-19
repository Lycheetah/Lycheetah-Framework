"""Reproducible comparison: deliberately weak pre-dispatch check versus a
local SQLite commit-time fence. This is a synthetic experiment, not a field study.
Run: python benchmark.py
"""
from __future__ import annotations
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from choice_fence import Action, ChoiceFence, PreDispatchOnlyBaseline

KEY = b"local-test-secret-not-deployable"
START = 1_800_000_000


def scenario(name: str) -> dict:
    now = [START]
    with TemporaryDirectory() as tmp:
        gate = ChoiceFence(Path(tmp) / "ledger.sqlite3", key=KEY, clock=lambda: now[0])
        gate.register("person")
        initial = Action("person", "agent", "send_email", "recipient@demo.test", "effect-1", "Message A")
        gate.issue("ticket-1", initial, expires_at=START + 100, explicit_human_approval=True)
        baseline = PreDispatchOnlyBaseline(gate)
        assert baseline.predispatch("ticket-1", initial)
        changed = initial
        if name == "revoke":
            gate.revoke("person", "ticket-1")
        elif name == "change_intent":
            gate.revise("person", reason="No longer want to contact them")
        elif name == "expiry":
            now[0] = START + 100
        elif name == "payload_substitution":
            changed = Action("person", "agent", "send_email", "recipient@demo.test", "effect-1", "Message B")
        elif name == "recipient_substitution":
            changed = Action("person", "agent", "send_email", "different@demo.test", "effect-1", "Message A")
        elif name == "agent_substitution":
            changed = Action("person", "agent-2", "send_email", "recipient@demo.test", "effect-1", "Message A")
        else:
            raise ValueError(name)
        # Both arms saw the same precheck and subsequent intervention.
        baseline_committed = baseline.remote_commit("ticket-1", changed)
        fence_result = gate.commit("ticket-1", changed)
        row = {"intervention": name,
               "predispatch_only_effect": baseline_committed,
               "protected_local_effect": fence_result.committed,
               "fence_reason": fence_result.reason,
               "audit_valid": gate.audit_ok(),
               "safety_property_pass": baseline_committed and not fence_result.committed and gate.audit_ok()}
        return row


def before_and_after_examples() -> list[dict]:
    now = START
    with TemporaryDirectory() as tmp:
        gate = ChoiceFence(Path(tmp) / "ledger.sqlite3", key=KEY, clock=lambda: now)
        gate.register("person")
        a = Action("person", "agent", "prepare_draft", "note", "before", "A")
        gate.issue("before-ticket", a, expires_at=now+50, explicit_human_approval=False)
        before = gate.commit("before-ticket", a)
        gate.revise("person", reason="New direction")
        # Revocation cannot undo already committed effect.
        after_revision = gate.commit("before-ticket", a)
        b = Action("person", "agent", "prepare_draft", "note", "after", "B")
        gate.issue("after-ticket", b, expires_at=now+50, explicit_human_approval=False)
        after = gate.commit("after-ticket", b)
        return [
            {"case": "effect_finalized_before_change", "committed": before.committed},
            {"case": "replaying_old_ticket_after_change", "committed": after_revision.committed,
             "reason": after_revision.reason},
            {"case": "fresh_ticket_for_revised_intent", "committed": after.committed},
            {"case": "local_effect_count", "count": gate.effect_count()},
        ]


def main() -> None:
    names = ["revoke", "change_intent", "expiry", "payload_substitution", "recipient_substitution", "agent_substitution"]
    rows = [scenario(name) for name in names]
    other = before_and_after_examples()
    report = {
        "schema": "lycheetah.forge3.synthetic.v0.1",
        "kind": "LOCAL_SYNTHETIC_REPRODUCIBLE",
        "comparison": "intentionally weak pre-dispatch-only anti-pattern vs atomic SQLite local-effect fence",
        "cases": rows, "total_cases": len(rows),
        "weak_baseline_invalid_effects": sum(x["predispatch_only_effect"] for x in rows),
        "local_fence_invalid_effects": sum(x["protected_local_effect"] for x in rows),
        "paired_passes": sum(x["safety_property_pass"] for x in rows),
        "boundary_cases": other,
        "no_claims": ["no remote provider control", "no user identity authentication", "no proof of free will",
                      "no real-world agent evaluation", "no novelty claim for commit-time fencing",
                      "no claim to stop effects already finalized"],
    }
    target = Path(__file__).parent / "results.json"
    target.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    for x in rows:
        print(f"{x['intervention']:24} weak={x['predispatch_only_effect']} fenced={x['protected_local_effect']} reason={x['fence_reason']}")
    print(f"Paired: {report['paired_passes']}/{len(rows)} | weak invalid local-model effects: {report['weak_baseline_invalid_effects']} | fence invalid local effects: {report['local_fence_invalid_effects']}")
    if report["paired_passes"] != len(rows):
        raise SystemExit("synthetic comparison unexpectedly failed")


if __name__ == "__main__":
    main()
