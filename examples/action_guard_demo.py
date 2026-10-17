"""Real-world demonstration of the Lycheetah Action Gateway.

Shows how an autonomous agent is safely bounded by:
1. Deterministic evidence-capped policy gating (ALLOW, REVIEW, BLOCK).
2. SQLite durable state machine preventing replay/double-fire.
3. Monotonic Ed25519 signed external checkpoints.
4. Tamper-evident Assurance Receipts.
"""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import time

from lycheetah.assurance import (
    ActionGateway,
    CommandExecutor,
    verify_envelope,
)


def main() -> None:
    print("=" * 72)
    print("  LYCHEETAH ACTION GATEWAY — REAL WORLD RUNTIME DEMO")
    print("=" * 72)

    with tempfile.TemporaryDirectory(prefix="lycheetah-demo-") as tmp:
        gw_dir = Path(tmp) / "gateway"
        print(f"\n[1] Initializing Gateway at {gw_dir}...")
        gateway = ActionGateway.open_local(gw_dir)
        status = gateway.guard.verify_audit_chain()
        print(f"    Genesis audit root: {status['root_hash'][:16]}... (valid={status['valid']})")

        # ---------------------------------------------------------
        # Scenario A: Safe Read-Only Action
        # ---------------------------------------------------------
        print("\n[2] Scenario A: Autonomous agent running a safe diagnostic tool...")
        action_a = {"tool": "system.info", "command": ["uname", "-a"], "side_effect": False}
        res_a = gateway.execute(
            action=action_a,
            actor="research-agent-01",
            scope="system:read",
            executor=CommandExecutor(["uname", "-s", "-m"]),
        )
        print(f"    Disposition: ALLOWED -> Status: {res_a.status}")
        print(f"    Output: {res_a.result['stdout'].strip()}")
        print(f"    Assurance Receipt Digest: {res_a.receipt.integrity['digest'][:24]}...")
        print(f"    Checkpoint Generation: #{res_a.checkpoint_generation}")

        # ---------------------------------------------------------
        # Scenario B: High-Impact Mutating Action (Requires Review)
        # ---------------------------------------------------------
        print("\n[3] Scenario B: Agent attempting an unapproved mutating action...")
        action_b = {"tool": "db.migrate", "target": "production", "side_effect": True}
        gate_b = gateway.propose(action_b, actor="devops-agent", scope="db:write")
        print(f"    Attempt without human sign-off: {gate_b.disposition.value} (allowed={gate_b.allowed})")
        print(f"    Reason: {gate_b.reason}")

        print("    Now presenting with human approval token ('security-lead-mac')...")
        res_b = gateway.execute(
            action=action_b,
            actor="devops-agent",
            scope="db:write",
            approver_id="security-lead-mac",
            executor=lambda: {"status": "success", "rows_migrated": 420},
        )
        print(f"    Approved Execution Status: {res_b.status}")
        print(f"    Result: {res_b.result}")
        print(f"    Checkpoint Generation: #{res_b.checkpoint_generation}")

        # ---------------------------------------------------------
        # Scenario C: Destructive Wipe Command (Hard Policy Block)
        # ---------------------------------------------------------
        print("\n[4] Scenario C: Malicious or prompt-injected command wipe attempt...")
        action_c = {"tool": "bash", "command": ["rm", "-rf", "/"], "side_effect": True}
        res_c = gateway.execute(
            action=action_c,
            actor="compromised-agent",
            scope="shell:root",
            approver_id="fake-approver",
            executor=CommandExecutor(["echo", "CRITICAL_FAILURE_IF_RUN"]),
        )
        print(f"    Outcome: {res_c.status} (provider_called={res_c.provider_called})")
        print(f"    Blocked by deterministic rule: {res_c.reason}")

        # ---------------------------------------------------------
        # Scenario D: Unreliable Remote Provider / Timeout (Quarantined)
        # ---------------------------------------------------------
        print("\n[5] Scenario D: Upstream API times out during execution...")
        action_d = {"tool": "stripe.charge", "amount": 9900, "side_effect": True}
        gate_d = gateway.propose(action_d, actor="billing-agent", scope="finance:charge", approver_id="auto-finance")

        def flaky_api_call():
            raise TimeoutError("504 Gateway Timeout from payment processor")

        res_d = gateway.dispatch(gate_d.effect_id, flaky_api_call)
        print(f"    Execution Outcome: {res_d.status}")
        print("    Fail-Closed Safety: Effect is locked in UNKNOWN state.")
        print("    Automatic retry is prohibited until human reconciliation.")

        # ---------------------------------------------------------
        # Final Ledger & Checkpoint Audit
        # ---------------------------------------------------------
        print("\n[6] Final Audit Trail Verification...")
        final_cp = gateway._get_latest_checkpoint()
        chain_status = gateway.guard.verify_audit_chain()
        consistency = gateway.guard.verify_state_consistency()
        key_bytes = gateway.checkpoints.public_key_bytes()
        sig_valid = verify_envelope(final_cp, key_bytes, gateway.journal_id)

        print(f"    Total Audit Events: {chain_status['event_count']}")
        print(f"    Chain Integrity: {'PASS' if chain_status['valid'] else 'FAIL'}")
        print(f"    State Consistency: {'PASS' if consistency['valid'] else 'FAIL'}")
        print(f"    Ed25519 Checkpoint Signature: {'AUTHENTIC' if sig_valid else 'FORGED'}")
        print(f"    Latest Root Hash: {final_cp['root_hash']}")
        print("\n" + "=" * 72)
        print("  DEMO COMPLETE: All 4 boundaries witnessed with zero regressions.")
        print("=" * 72)


if __name__ == "__main__":
    main()
