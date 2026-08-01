from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lamague_core import run_source
from lamague_core.errors import LamagueError

cases = json.loads((ROOT / "benchmark" / "CORE_BENCHMARK_CASES.json").read_text(encoding="utf-8"))["cases"]
results = []

for case in cases:
    passed = False
    detail = None
    try:
        _, _, result = run_source(case["source"])
        expected = case["expect"]
        if expected == "ACCEPTED":
            passed = result["status"] == "ACCEPTED"
        elif expected in {True, False}:
            passed = result["checks"][0]["equivalent"] is expected
        elif expected == "WARNINGS":
            passed = len(result["warnings"]) >= 3
        elif expected == "INVARIANT":
            passed = bool(result["invariants"])
        elif expected == "PROHIBITION":
            passed = bool(result["prohibitions"])
        elif isinstance(expected, str) and expected.startswith("("):
            passed = result["expressions"][0] == expected
        detail = result
    except LamagueError as exc:
        passed = case["expect"] == "REJECTED"
        detail = {"error_type": type(exc).__name__, "error": str(exc)}
    results.append({"id":case["id"],"name":case["name"],"passed":passed,"expected":case["expect"],"detail":detail})

summary = {
    "suite":"LAMAGUE Core Algebra v0.1 deterministic benchmark",
    "total":len(results),
    "passed":sum(1 for r in results if r["passed"]),
    "failed":sum(1 for r in results if not r["passed"]),
    "results":results,
    "claim_boundary":"Synthetic software conformance only; no domain validation."
}
(ROOT / "reports" / "BENCHMARK_RESULTS.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps({k:summary[k] for k in ("suite","total","passed","failed")}, indent=2))
raise SystemExit(0 if summary["failed"] == 0 else 1)
