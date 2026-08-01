from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Any
import json

from .engine import compare


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def run_manifest(manifest_path: str | Path) -> dict[str, Any]:
    manifest_path = Path(manifest_path)
    manifest = load_json(manifest_path)
    root = manifest_path.parent
    results = []
    confusion: dict[str, Counter[str]] = defaultdict(Counter)
    for item in manifest["candidates"]:
        reference = load_json(root / item["reference"])
        candidate = load_json(root / item["candidate"])
        result = compare(reference, candidate).to_dict()
        result["expected_class"] = item["expected_class"]
        result["match"] = result["classification"] == item["expected_class"]
        results.append(result)
        confusion[item["expected_class"]][result["classification"]] += 1

    total = len(results)
    matches = sum(1 for x in results if x["match"])
    distribution = Counter(x["classification"] for x in results)
    expected_distribution = Counter(x["expected_class"] for x in results)
    per_field_loss = Counter()
    for result in results:
        for lost in result["lost_critical"]:
            per_field_loss[lost.split(":", 1)[0]] += 1

    return {
        "benchmark": manifest["benchmark"],
        "version": manifest["version"],
        "corpus_type": manifest["corpus_type"],
        "reference_cases": len(manifest["references"]),
        "candidate_packets": total,
        "expected_matches": matches,
        "accuracy": matches / total if total else 0.0,
        "classification_distribution": dict(sorted(distribution.items())),
        "expected_distribution": dict(sorted(expected_distribution.items())),
        "critical_loss_events_by_field": dict(sorted(per_field_loss.items())),
        "confusion_matrix": {k: dict(v) for k, v in sorted(confusion.items())},
        "results": results,
    }
