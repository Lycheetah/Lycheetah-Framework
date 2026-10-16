"""Tiny deterministic scenario demo. It only exercises FakeMergeProvider; no network."""
import tempfile
from pathlib import Path
from action_guard_v07 import PersistentActionGuard, FakeMergeProvider

with tempfile.TemporaryDirectory() as td:
    guard = PersistentActionGuard(Path(td) / "ledger.sqlite3")
    provider = FakeMergeProvider()
    provider.seed_pr("Lycheetah/demo", 17, "head-A", "base-A")
    action = provider.read_action("Lycheetah/demo", 17)
    scope = "merge:Lycheetah/demo#17"
    approval = guard.issue_approval("approval-1", "coding-agent", "test-human", action, scope, 10, 100)
    intent = guard.prepare_effect("effect-1", "approval-1", "coding-agent", action, scope, 20)
    trusted_anchor = guard.audit_anchor()  # in production, copy to an independent trusted store
    claim = guard.claim_dispatch("effect-1", 30, provider.read_action("Lycheetah/demo", 17), trusted_anchor)
    outcome = provider.merge(claim.action, "effect-1") if claim.allowed else {"status": "denied", "reason": claim.reason}
    guard.record_result("effect-1", 31, "success" if outcome.get("status") == "success" else "failure", outcome)
    print({"approval": approval.reason, "intent": intent.reason, "claim": claim.reason,
           "provider_outcome": outcome, "ledger_status": guard.get_effect("effect-1")["status"],
           "live_provider": False})
