"""Deterministic, side-effect-free demo comparing a spoofable flag to a host token."""
from __future__ import annotations
import base64
import hashlib
import json
import tempfile
from pathlib import Path
from authority_gate import ActionIntent, ApprovalAuthority, ConsequenceGate, GateDenied

KEY = b"demo-only-never-use-in-production-signing-secret-32bytes-min"
POLICY = hashlib.sha256(b"policy-v1").hexdigest()
POLICY_NEW = hashlib.sha256(b"policy-v2").hexdigest()
NOW = 1_800_000_000.0


def tamper_signature(token):
    """Flip a decoded signature byte, not only unused Base64URL pad bits."""
    body, encoded = token.split(".", 1)
    raw = bytearray(base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4)))
    raw[0] ^= 0x01
    changed = base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")
    return f"{body}.{changed}"


def make_action(amount=12.5):
    return ActionIntent("agent-demo", "refund_order", {"order_id": "ORD-1042", "amount": amount},
                        ("orders:write",), "workspace-demo")


def naive_baseline(model_claims, effect):
    """Intentionally unsafe integration comparator: trusts model-supplied boolean."""
    if model_claims.get("human_approved") is True:
        return effect()
    raise PermissionError("approval-missing")


def main():
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        authority = ApprovalAuthority(KEY)
        gate = ConsequenceGate(KEY, Path(tmp) / "used.sqlite3")
        base_action = make_action()
        good = authority.issue(base_action, policy_sha256=POLICY,
                               reviewer_id="reviewer-demo", approval_ref="ui-demo-1",
                               ttl_seconds=60, now=NOW)
        expired = authority.issue(base_action, policy_sha256=POLICY,
                                  reviewer_id="reviewer-demo", approval_ref="ui-demo-2",
                                  ttl_seconds=5, now=NOW)
        tampered = tamper_signature(good)

        cases = [
            ("valid-host-token", good, base_action, POLICY, NOW + 1),
            ("forged-boolean-no-token", None, base_action, POLICY, NOW + 1),
            ("action-substitution", good, make_action(99.9), POLICY, NOW + 1),
            ("policy-drift", good, base_action, POLICY_NEW, NOW + 1),
            ("expired-token", expired, base_action, POLICY, NOW + 5),
            ("tampered-token", tampered, base_action, POLICY, NOW + 1),
        ]
        for name, token, action, policy, current_time in cases:
            side_effects = {"baseline": 0, "candidate": 0}
            try:
                naive_baseline({"human_approved": True},
                               lambda: side_effects.__setitem__("baseline", side_effects["baseline"] + 1))
                baseline = "ALLOW"
            except PermissionError:
                baseline = "DENY"
            try:
                gate.execute(token, action, current_policy_sha256=policy,
                             effect=lambda _: side_effects.__setitem__("candidate", side_effects["candidate"] + 1),
                             now=current_time)
                candidate, reason = "ALLOW", "verified-token-consumed"
            except GateDenied as exc:
                candidate, reason = "DENY", exc.reason
            results.append({"case": name, "naive_claim_baseline": baseline,
                            "candidate": candidate, "candidate_reason": reason,
                            "baseline_effect_calls": side_effects["baseline"],
                            "candidate_effect_calls": side_effects["candidate"]})

        # Demonstrate duplicate call: first is allowed, subsequent uses of same token denied.
        replay_token = authority.issue(base_action, policy_sha256=POLICY,
                                       reviewer_id="reviewer-demo", approval_ref="ui-demo-replay",
                                       ttl_seconds=60, now=NOW)
        replay_outcomes = []
        for _ in range(2):
            try:
                gate.execute(replay_token, base_action, current_policy_sha256=POLICY,
                             effect=lambda _: "dispatched", now=NOW + 1)
                replay_outcomes.append("ALLOW")
            except GateDenied as exc:
                replay_outcomes.append(f"DENY:{exc.reason}")
        results.append({"case": "replay-same-token-twice", "naive_claim_baseline": "ALLOW,ALLOW",
                        "candidate": ",".join(x.split(":")[0] for x in replay_outcomes),
                        "candidate_reason": ",".join(x.split(":", 1)[1] if ":" in x else "ok" for x in replay_outcomes),
                        "candidate_effect_calls": replay_outcomes.count("ALLOW")})

    output = {"status": "SYNTHETIC_LOCAL_DEMO", "cases": len(results), "results": results,
              "limits": ["The baseline deliberately trusts a model-supplied boolean; it is not asserted to describe every real integration.",
                         "The callback is an in-memory counter, not a real provider or human approval workflow.",
                         "Token issuance assumes a trusted host already authenticated the reviewer; this demo does not authenticate humans."]}
    out_path = Path(__file__).with_name("demo_results.json")
    out_path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
