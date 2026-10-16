"""Deterministic synthetic verification: action mutation + concurrent approval consumption.
All provider behavior is simulated. No network or real GitHub effect occurs.
"""
from __future__ import annotations
import json
import tempfile
import threading
from pathlib import Path
from action_guard_v07 import PersistentActionGuard


def main():
    with tempfile.TemporaryDirectory() as td:
        db = Path(td) / "verification.sqlite3"
        g = PersistentActionGuard(db)
        original = {"tool": "github.merge", "repo": "Lycheetah/demo", "pull_request": 17,
                    "head_sha": "head-A", "base_sha": "base-A", "merge_method": "squash"}
        scope = "merge:Lycheetah/demo#17"
        fields = ["repo", "pull_request", "head_sha", "base_sha", "merge_method"]
        tamper_trials = 1000
        guard_denied = 0
        guard_allowed_tamper = 0
        reasons = {}
        for i in range(tamper_trials):
            approval_id = f"tamper-ap-{i}"
            changed = dict(original)
            field = fields[i % len(fields)]
            changed[field] = f"mutated-{i}" if field != "pull_request" else 1000 + i
            g.issue_approval(approval_id, "coding-agent", "human-reviewer", original,
                             scope, 100, 1000)
            decision = g.prepare_effect(f"tamper-fx-{i}", approval_id, "coding-agent",
                                        changed, scope, 200)
            if decision.allowed:
                guard_allowed_tamper += 1
            else:
                guard_denied += 1
                reasons[decision.reason] = reasons.get(decision.reason, 0) + 1
            # Deliberately weak comparison: role/tool allow-list does not bind parameters.
            # All mutated actions retain the github.merge tool name, so this baseline allows.
        positive_controls = 100
        positive_allowed = 0
        for i in range(positive_controls):
            aid = f"positive-ap-{i}"
            g.issue_approval(aid, "coding-agent", "human-reviewer", original,
                             scope, 100, 1000)
            d = g.prepare_effect(f"positive-fx-{i}", aid, "coding-agent", original, scope, 200)
            positive_allowed += int(d.allowed)

        rounds, contenders = 25, 8
        winners, denied, concurrency_errors = 0, 0, []
        for r in range(rounds):
            approval_id = f"race-ap-{r}"
            g.issue_approval(approval_id, "coding-agent", "human-reviewer", original,
                             scope, 100, 1000)
            barrier = threading.Barrier(contenders)
            result_lock = threading.Lock()
            results = []
            guards = [PersistentActionGuard(db) for _ in range(contenders)]
            def attempt(i):
                try:
                    barrier.wait(timeout=5)
                    d = guards[i].prepare_effect(f"race-{r}-fx-{i}", approval_id,
                        "coding-agent", original, scope, 200)
                    with result_lock: results.append(d)
                except Exception as exc:  # surfaced as a failed verification, never ignored
                    with result_lock: concurrency_errors.append(repr(exc))
            threads = [threading.Thread(target=attempt, args=(i,)) for i in range(contenders)]
            for t in threads: t.start()
            for t in threads: t.join(timeout=10)
            if any(t.is_alive() for t in threads):
                concurrency_errors.append(f"race-{r}: thread timeout")
            round_winners = sum(d.allowed for d in results)
            winners += round_winners
            denied += sum(not d.allowed for d in results)
            if round_winners != 1 or len(results) != contenders:
                concurrency_errors.append(f"race-{r}: results={len(results)} winners={round_winners}")

        audit_status = g.verify_audit_chain()
        result = {
            "classification": "synthetic local verification; not independent or production validation",
            "audit_chain_valid_after_benchmark": audit_status["valid"],
            "audit_chain_event_count": audit_status["event_count"],
            "audit_chain_root_hash": audit_status["root_hash"],
            "live_provider_calls": 0,
            "action_mutation_trials": tamper_trials,
            "mutated_fields": fields,
            "role_tool_acl_baseline_allowed_mutations": tamper_trials,
            "persistent_guard_denied_mutations": guard_denied,
            "persistent_guard_allowed_mutations": guard_allowed_tamper,
            "guard_denial_reasons": reasons,
            "exact_action_positive_controls": positive_controls,
            "exact_action_positive_controls_allowed": positive_allowed,
            "concurrency_rounds": rounds,
            "contenders_per_round": contenders,
            "concurrency_attempts": rounds * contenders,
            "concurrency_allowed": winners,
            "concurrency_denied": denied,
            "concurrency_errors": concurrency_errors,
        }
        Path(__file__).with_name("v07_synthetic_benchmark_results.json").write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(result, indent=2, sort_keys=True))
        if guard_allowed_tamper or positive_allowed != positive_controls or concurrency_errors or winners != rounds or denied != rounds * (contenders - 1) or not audit_status["valid"]:
            raise SystemExit("verification failed")

if __name__ == "__main__":
    main()
