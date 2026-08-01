from __future__ import annotations
import json
from pathlib import Path
from .bridge import analyze_dict


def run_manifest(path: str | Path) -> dict:
    path = Path(path)
    manifest = json.loads(path.read_text(encoding="utf-8"))
    results = []
    matches = 0
    for case in manifest["cases"]:
        packet_path = path.parent / case["packet"]
        packet = json.loads(packet_path.read_text(encoding="utf-8"))
        result = analyze_dict(packet)
        expected = case["expected"]
        checks = {key: result.get(key) == value for key, value in expected.items()}
        passed = all(checks.values())
        matches += int(passed)
        results.append({
            "case_id": case["case_id"],
            "passed": passed,
            "checks": checks,
            "expected": expected,
            "observed": {key: result.get(key) for key in expected},
        })
    return {
        "suite": manifest["suite"],
        "case_count": len(results),
        "expected_matches": matches,
        "accuracy": matches / len(results) if results else None,
        "results": results,
        "claim_boundary": manifest["claim_boundary"],
    }
