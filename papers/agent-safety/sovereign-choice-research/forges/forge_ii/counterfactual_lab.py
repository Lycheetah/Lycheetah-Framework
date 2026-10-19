"""Synthetic paired intervention tests; not a human study or external-agent benchmark.

For each case, the *same original plan* is run twice in fresh policy stores:
  Control: still-valid human authority -> should allow.
  Intervention: one consequential condition is changed -> should deny.

The toy 'frozen plan' baseline ignores changed authority and always follows the
original plan. This is a deliberately weak illustrative baseline, not a claim
about commercial competitors or Lycheetah's existing commit-time fence.
"""
import hashlib
import json
from pathlib import Path
from sovereign_choice import Request, SovereignChoice

NOW = 1_800_000_000
KEY = b"for-local-study-only-reference-key"
PAYLOAD = hashlib.sha256(b"original approved email body").hexdigest()
ALTERED = hashlib.sha256(b"materially altered email body").hexdigest()


def simulate(change: str, modified: bool) -> dict:
    gate = SovereignChoice(audit_key=KEY, clock=lambda: NOW)
    gate.register_owner("person")
    high = change in {"high_impact_revoke", "payload_substitution", "stale_approval"}
    op = "send_email" if high else "prepare_draft"
    resource = "prospect_1"
    gate.issue_grant(grant_id="consent-1", owner="person", agent="assistant", operation=op,
                     resource=resource, expires_at=NOW if modified and change == "expiry" else NOW+100)
    if high:
        gate.approve_once(owner="person", approval_id="approve-1", grant_id="consent-1",
                          request_id="req-1", operation=op, resource=resource,
                          expires_at=NOW+50, payload_digest=PAYLOAD)
    if modified:
        if change == "revoke":
            gate.revoke("person", "consent-1")
        if change == "revised_goal":
            gate.revise_intent("person", reason="I want to write a different document")
        if change == "high_impact_revoke":
            gate.revoke("person", "consent-1")
        if change == "stale_approval":
            gate.revise_intent("person", reason="Actually, stop the email")
    req = Request(
        "person", "other_agent" if modified and change == "other_agent" else "assistant",
        "consent-1", op,
        "unapproved_prospect" if modified and change == "other_resource" else resource,
        "req-1", "approve-1" if high else None,
        ALTERED if modified and change == "payload_substitution" else PAYLOAD,
    )
    d = gate.decide(req)
    integrity = gate.audit_ok()
    gate.close()
    return {"allowed": d.allowed, "reason": d.reason, "audit_ok": integrity}


def main():
    cases = [
        ("revoke", "Human withdraws authorisation"),
        ("revised_goal", "Human explicitly changes the goal"),
        ("high_impact_revoke", "Human revokes a message-send grant"),
        ("stale_approval", "Human revises intent after approving an email"),
        ("expiry", "Grant expires"),
        ("other_agent", "A different agent attempts the action"),
        ("other_resource", "Agent changes the target"),
        ("payload_substitution", "Approved message content is changed"),
    ]
    rows = []
    for change, label in cases:
        control = simulate(change, False)
        intervened = simulate(change, True)
        rows.append({"case": change, "question": label, "control": control,
                     "intervention": intervened, "pair_pass": control["allowed"]
                     and not intervened["allowed"] and control["audit_ok"]
                     and intervened["audit_ok"]})
    result = {
        "status": "LOCAL_SYNTHETIC", "version": "0.1", "cases": rows,
        "paired_pass_count": sum(row["pair_pass"] for row in rows),
        "paired_total": len(rows),
        "note": "Toy frozen-plan baseline would allow after each intervention; deliberately weak and not measured against a real competing agent.",
        "limit": "Gate decisions do not execute external effects or prove user comprehension, coercion absence, identity verification, deployment safety or metaphysical free will.",
    }
    Path("counterfactual_results.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for row in rows:
        print(f"{row['case']:<22} control={row['control']['reason']:<8} changed={row['intervention']['reason']:<24} {'PASS' if row['pair_pass'] else 'FAIL'}")
    print(f"PASSED {result['paired_pass_count']}/{result['paired_total']} paired scenario checks")
    if result["paired_pass_count"] != result["paired_total"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
