"""Produce machine-readable observed behavior for in-pack provider controls."""
from __future__ import annotations
import json
import tempfile
from pathlib import Path
from provider_contract import AtomicConditionalProvider, CheckThenActProvider, NonIdempotentProvider, ResponseLost, IdempotencyConflict
from model_check import VALID, evaluate_atomic, evaluate_split


def atomic_probe(root: Path) -> dict:
    provider = AtomicConditionalProvider(root / "atomic.db")
    provider.set_condition("release", "v1", "PASS")
    payload = {"artifact": "sha256:abc", "environment": "staging"}
    first = provider.execute("op", payload, condition_key="release", required_status="PASS", required_version="v1")
    retry = provider.execute("op", payload, condition_key="release", required_status="FAIL")
    conflict = False
    try:
        provider.execute("op", {**payload, "environment": "prod"}, condition_key="release", required_status="PASS")
    except IdempotencyConflict:
        conflict = True
    provider.set_condition("release", "v2", "FAIL")
    denied = False
    try:
        provider.execute("op-2", payload, condition_key="release", required_status="PASS")
    except Exception:
        denied = True
    return {"provider_model": "atomic_conditional_reference", "initial_action_accepted": first["accepted"],
            "same_key_retry_replayed": retry["replayed"], "effects_after_retry": provider.effect_count("op"),
            "same_key_different_payload_conflicts": conflict, "false_condition_denied": denied,
            "claimed_contract_pass": first["accepted"] and retry["replayed"] and provider.effect_count("op") == 1 and conflict and denied}


def split_probe() -> dict:
    provider = CheckThenActProvider()
    payload = {"artifact": "sha256:abc", "environment": "staging"}
    provider.after_check = lambda: provider.set_condition("v2", "FAIL")
    result = provider.execute("op", payload)
    violation = result["condition_status"] == "PASS" and provider.condition["status"] == "FAIL" and provider.effect_count() == 1
    return {"provider_model": "split_check_then_act_negative_control", "accepted_using_stale_snapshot": violation,
            "final_condition": provider.condition, "effect_count": provider.effect_count(),
            "atomic_condition_contract_pass": not violation}


def non_idempotent_probe() -> dict:
    provider = NonIdempotentProvider()
    payload = {"refund": 4}
    provider.drop_next_response = True
    response_lost = False
    try:
        provider.execute("op", payload)
    except ResponseLost:
        response_lost = True
    provider.execute("op", payload)
    count = provider.effect_count()
    return {"provider_model": "non_idempotent_negative_control", "response_lost_after_first_effect": response_lost,
            "effects_after_retry": count, "durable_idempotency_contract_pass": count == 1}


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as td:
        results = {
            "scope": "local reference providers only; no real provider API called",
            "atomic_reference": atomic_probe(Path(td)),
            "split_check_negative_control": split_probe(),
            "non_idempotent_negative_control": non_idempotent_probe(),
            "bounded_model": {
                "schedule_count": len(VALID),
                "split_check_violations": sum(x["safety_violation"] for x in map(evaluate_split, VALID)),
                "atomic_condition_violations": sum(x["safety_violation"] for x in map(evaluate_atomic, VALID)),
            },
        }
        print(json.dumps(results, indent=2, sort_keys=True))
