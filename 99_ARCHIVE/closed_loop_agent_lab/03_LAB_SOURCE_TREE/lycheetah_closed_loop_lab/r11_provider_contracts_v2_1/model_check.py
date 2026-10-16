"""Enumerate allowed orderings for condition check/update/effect linearization."""
from itertools import permutations
import json

EVENTS = ("CHECK", "UPDATE_FALSE", "EFFECT")
VALID = []
for order in permutations(EVENTS):
    if order.index("CHECK") < order.index("EFFECT"):
        VALID.append(order)


def evaluate_split(order):
    status = "PASS"
    checked = None
    effect_applied = False
    observed_status = None
    for event in order:
        if event == "CHECK":
            checked = status == "PASS"
            observed_status = status
        elif event == "UPDATE_FALSE":
            status = "FAIL"
        elif event == "EFFECT" and checked:
            effect_applied = True
    violation = effect_applied and status == "FAIL" and order.index("UPDATE_FALSE") < order.index("EFFECT")
    return {"order": list(order), "check_saw": observed_status, "final_status": status,
            "effect_applied": effect_applied, "safety_violation": violation}


def evaluate_atomic(order):
    status = "PASS"
    effect_applied = False
    effect_saw = None
    for event in order:
        if event == "UPDATE_FALSE":
            status = "FAIL"
        elif event == "EFFECT":
            effect_saw = status
            effect_applied = status == "PASS"
    violation = effect_applied and effect_saw != "PASS"
    return {"order": list(order), "effect_saw": effect_saw, "final_status": status,
            "effect_applied": effect_applied, "safety_violation": violation}


if __name__ == "__main__":
    records = [evaluate_split(p) for p in VALID]
    atomic = [evaluate_atomic(p) for p in VALID]
    output = {"model": "three-event bounded interleaving; CHECK must precede EFFECT in baseline",
              "valid_schedules": len(VALID),
              "split_check_then_act": {"violations": sum(x["safety_violation"] for x in records), "records": records},
              "atomic_condition_effect": {"violations": sum(x["safety_violation"] for x in atomic), "records": atomic}}
    print(json.dumps(output, indent=2))
