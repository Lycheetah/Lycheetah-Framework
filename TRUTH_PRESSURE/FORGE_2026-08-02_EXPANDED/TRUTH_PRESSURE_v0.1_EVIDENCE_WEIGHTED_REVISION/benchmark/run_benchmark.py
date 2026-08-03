from __future__ import annotations

import copy
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from truth_pressure import ClaimEvidence, PressureConfig, TruthPressureError, evaluate_claim

suite = json.loads((ROOT / "benchmark/BENCHMARK_CASES.json").read_text())
strong = json.loads((ROOT / "examples/strong_challenger.json").read_text())
frontier = json.loads((ROOT / "examples/frontier_claim.json").read_text())
compatible = json.loads((ROOT / "examples/compatible_claim.json").read_text())
lookup = {"strong": strong, "frontier": frontier, "compatible": compatible}
results = []

for case in suite["cases"]:
    passed = False
    detail = {}
    try:
        if "example" in case:
            packet = json.loads((ROOT / "examples" / case["example"]).read_text())
        else:
            packet = copy.deepcopy(lookup[case["base"]])
        if case.get("remove_foundation"):
            packet.pop("foundation", None)
        if case.get("foundation_same"):
            packet["foundation"] = copy.deepcopy(packet["claim"])
        if case.get("swap"):
            packet["claim"], packet["foundation"] = packet["foundation"], packet["claim"]
        packet["claim"].update(case.get("set", {}))
        config = PressureConfig(**case.get("config", {}))
        claim = ClaimEvidence(**packet["claim"])
        foundation = ClaimEvidence(**packet["foundation"]) if packet.get("foundation") else None
        result = evaluate_claim(claim, foundation=foundation, config=config)
        detail = result.export()
        if "expected_state" in case:
            passed = result.state.value == case["expected_state"]
        elif case.get("expected_not_candidate"):
            passed = not result.cascade_authorized
        elif case.get("expected_finite"):
            passed = math.isfinite(result.raw_pressure) and math.isfinite(result.bounded_pressure)
        elif case.get("expected_rejected"):
            passed = False
    except (TruthPressureError, TypeError, KeyError) as exc:
        detail = {"error_type": type(exc).__name__, "error": str(exc)}
        passed = bool(case.get("expected_rejected"))
    results.append({"id":case["id"],"name":case["name"],"passed":passed,"detail":detail})

report = {
    "suite": suite["suite"],
    "total": len(results),
    "passed": sum(r["passed"] for r in results),
    "failed": sum(not r["passed"] for r in results),
    "results": results,
    "claim_boundary": suite["claim_boundary"]
}
(ROOT / "reports/BENCHMARK_RESULTS.json").write_text(json.dumps(report, indent=2, ensure_ascii=False))
print(json.dumps({k:report[k] for k in ("suite","total","passed","failed")}, indent=2))
raise SystemExit(0 if report["failed"] == 0 else 1)
