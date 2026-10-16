"""Reproduce the callback-selection gap in v0.4's local reference gate.

This is a contained in-memory/SQLite demonstration. It does not call a real
provider and is not a finding that the live Lycheetah MCP host can be bypassed.
"""
from __future__ import annotations
import hashlib
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "authority_boundary_lab"))
from authority_gate import ActionIntent, ApprovalAuthority, ConsequenceGate  # noqa: E402

KEY = b"fixture-only-test-key-never-use-production-32bytes+"
POLICY = hashlib.sha256(b"fixture-policy-v1").hexdigest()
NOW = 1_800_000_000.0


def main() -> None:
    action = ActionIntent(
        agent_id="fixture-agent", tool_name="refund_order",
        arguments={"order_id": "ORD-1042", "amount": 12.5},
        scopes=("orders:write",), workspace_id="fixture-workspace",
    )
    authority = ApprovalAuthority(KEY)
    token = authority.issue(
        action, policy_sha256=POLICY, reviewer_id="fixture-reviewer",
        approval_ref="fixture-approved-refund", now=NOW,
    )
    with tempfile.TemporaryDirectory() as folder:
        gate = ConsequenceGate(KEY, Path(folder) / "nonce.sqlite")
        observed = []
        result = gate.execute(
            token, action, current_policy_sha256=POLICY,
            # The API accepts this callback separately; this is the mismatch probe.
            effect=lambda payload: observed.append({
                "approved_tool_in_payload": payload["tool_name"],
                "callback_performed": "delete_every_account",
            }) or "callback-ran",
            now=NOW + 1,
        )
    report = {
        "status": "SYNTHETIC_REFERENCE_API_COUNTEREXAMPLE",
        "approval_bound_to": {"tool": action.tool_name, "action_sha256": action.digest},
        "result": result,
        "observed": observed,
        "finding": "v0.4 gate authenticates the declared action but does not bind the separately supplied execution callback to that action",
        "limits": [
            "No external effect was performed; the callback only records a string.",
            "This is a weakness in the local v0.4 reference API's guarantee, not proof of a live Lycheetah deployment vulnerability.",
            "A trusted host could still pass the correct callback; the gate itself does not enforce that correspondence.",
        ],
    }
    output = Path(__file__).with_name("v0_4_gap_reproduction.json")
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
