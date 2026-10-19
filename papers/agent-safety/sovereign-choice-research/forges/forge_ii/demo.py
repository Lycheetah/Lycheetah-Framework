"""CLI demo: baseline task-following versus sovereignty-preserving authority checks."""
from sovereign_choice import Request, SovereignChoice
import hashlib

NOW = 1800000000
KEY = b"example-only-key-not-production-secret"
BODY_DIGEST = hashlib.sha256(b"approved message").hexdigest()


def show(label, result):
    print(f"{label:35} {'ALLOW ' if result.allowed else 'DENY  '} reason={result.reason}")


def main():
    g = SovereignChoice(audit_key=KEY, clock=lambda: NOW)
    g.register_owner("human")
    g.issue_grant(grant_id="outreach", owner="human", agent="reachforge",
                  operation="send_email", resource="customer_a", expires_at=NOW + 600)
    show("Agent wants to send without approval", g.decide(Request(
        "human", "reachforge", "outreach", "send_email", "customer_a", "req1", None, BODY_DIGEST)))
    g.approve_once(owner="human", approval_id="approve2", grant_id="outreach", request_id="req2",
                   operation="send_email", resource="customer_a", expires_at=NOW + 100, payload_digest=BODY_DIGEST)
    # The user changes direction; this invalidates an otherwise technically valid request.
    g.revise_intent("human", reason="I do not want to send that message")
    show("Outdated plan with prior approval", g.decide(Request(
        "human", "reachforge", "outreach", "send_email", "customer_a", "req2", "approve2", BODY_DIGEST)))
    g.issue_grant(grant_id="draft", owner="human", agent="reachforge",
                  operation="prepare_draft", resource="customer_a", expires_at=NOW + 600)
    show("New human-approved draft-only path", g.decide(Request(
        "human", "reachforge", "draft", "prepare_draft", "customer_a", "req3")))
    print(f"Audit hash chain: {'OK' if g.audit_ok() else 'FAIL'} ({g.audit_count()} events)")
    print("No emails were sent. Decisions only. No human free-will measurement was attempted.")
    g.close()


if __name__ == "__main__":
    main()
