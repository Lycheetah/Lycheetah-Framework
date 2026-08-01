from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lamague_core import run_source
from lamague_core.errors import LamagueError

suite = json.loads(
    (ROOT / "benchmark" / "OPERATOR_BENCHMARK_CASES.json").read_text(
        encoding="utf-8"
    )
)
results = []

for case in suite["cases"]:
    passed = False
    detail = None
    try:
        _, _, result = run_source(case["source"])
        field = case["field"]
        expect = case["expect"]

        if field in {"status", "value", "equivalent", "structurally_composable"}:
            record = result["checks"][0]
            actual = record.get(field)
        elif field == "expression":
            actual = result["expressions"][0]
        elif field == "description_kind":
            actual = result["descriptions"][0]["kind"]
        elif field == "trace_rule":
            actual = [
                x["rule"]
                for x in result["descriptions"][0]["rewrite_trace"]
            ]
            passed = expect in actual
            detail = result
            results.append({
                "id": case["id"],
                "passed": passed,
                "expected": expect,
                "actual": actual,
                "detail": detail,
            })
            continue
        else:
            raise RuntimeError(field)

        passed = actual == expect
        detail = result
    except (LamagueError, ValueError) as exc:
        actual = "REJECTED"
        passed = case["expect"] == "REJECTED"
        detail = {"error_type": type(exc).__name__, "error": str(exc)}

    results.append({
        "id": case["id"],
        "passed": passed,
        "expected": case["expect"],
        "actual": actual,
        "detail": detail,
    })

summary = {
    "suite": suite["suite"],
    "total": len(results),
    "passed": sum(1 for x in results if x["passed"]),
    "failed": sum(1 for x in results if not x["passed"]),
    "results": results,
    "claim_boundary": suite["claim_boundary"],
}
(ROOT / "reports" / "BENCHMARK_RESULTS_v0.3.json").write_text(
    json.dumps(summary, indent=2, ensure_ascii=False),
    encoding="utf-8",
)
print(json.dumps({
    "suite": summary["suite"],
    "total": summary["total"],
    "passed": summary["passed"],
    "failed": summary["failed"],
}, indent=2))
raise SystemExit(0 if summary["failed"] == 0 else 1)
