"""Run the researcher-authored synthetic CASCADE structural conformance suite.

This is not a real-world efficacy benchmark. Expected review sets are authored from
our declared graph-traversal policy and require independent review before being
used as a performance claim.
"""
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone
from cascade import KnowledgeBlock, KnowledgeGraph

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "structural_benchmark_cases.json"
OUT_JSON = HERE / "structural_benchmark_results.json"
OUT_MD = HERE / "structural_benchmark_report.md"


def build_block(raw: dict) -> KnowledgeBlock:
    return KnowledgeBlock(
        block_id=raw["block_id"],
        content=raw["content"],
        claim_type=raw["claim_type"],
        status=raw.get("status", "pending_review"),
        dependencies=raw.get("dependencies", []),
        contradicts=raw.get("contradicts", []),
        evidence_ids=raw.get("evidence_ids", []),
        provenance_ids=raw.get("provenance_ids", []),
    )


def main() -> int:
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    details = []
    passed = 0
    total_fp = 0
    total_fn = 0
    all_safety_ok = True

    for case in data["cases"]:
        graph = KnowledgeGraph([build_block(b) for b in case["blocks"]])
        before = {k: b.status for k, b in graph.blocks.items()}
        review = graph.propose_cascade(case["changed_block_id"], f"Synthetic test {case['case_id']}")
        expected = set(case["expected_affected"])
        actual = set(review.affected_block_ids)
        fp = sorted(actual - expected)
        fn = sorted(expected - actual)
        statuses_unchanged = before == {k: b.status for k, b in graph.blocks.items()}
        no_automatic_status_changes = review.automatic_status_changes == []
        marked_exactly = {k for k, b in graph.blocks.items() if b.review_required} == actual
        safety_ok = statuses_unchanged and no_automatic_status_changes and marked_exactly
        exact = not fp and not fn and safety_ok
        passed += int(exact)
        total_fp += len(fp)
        total_fn += len(fn)
        all_safety_ok = all_safety_ok and safety_ok
        details.append({
            "case_id": case["case_id"],
            "title": case["title"],
            "expected_affected": sorted(expected),
            "actual_affected": sorted(actual),
            "false_positives_vs_declared_rule": fp,
            "false_negatives_vs_declared_rule": fn,
            "statuses_unchanged": statuses_unchanged,
            "no_automatic_status_changes": no_automatic_status_changes,
            "review_flags_match_report": marked_exactly,
            "pass": exact,
        })

    result = {
        "benchmark_id": data["benchmark_id"],
        "version": data["version"],
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "label_origin": data["label_origin"],
        "cases_total": len(details),
        "cases_passed": passed,
        "cases_failed": len(details) - passed,
        "false_positives_vs_declared_rule": total_fp,
        "false_negatives_vs_declared_rule": total_fn,
        "all_safety_invariants_met": all_safety_ok,
        "details": details,
        "interpretation": "Structural conformance only. This run does not estimate real-world materiality, factual accuracy, political neutrality, policy utility, or AURA metric validity.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "# CASCADE structural conformance benchmark v0.1",
        "",
        f"- **Fixture suite:** {data['benchmark_id']} (version {data['version']})",
        f"- **Cases:** {passed}/{len(details)} exact matches; {len(details)-passed} failures.",
        f"- **False positives vs declared traversal rule:** {total_fp}",
        f"- **False negatives vs declared traversal rule:** {total_fn}",
        f"- **Safety invariants:** {'PASS' if all_safety_ok else 'FAIL'} (statuses unchanged; no automatic status changes; review flags match reported queue).",
        "",
        "## Scope and caveat",
        "",
        data["label_origin"],
        "",
        "This suite tests conformance to a declared software traversal rule. It does not test whether queued claims are substantively or politically material, whether evidence is true, or whether CASCADE improves on human review or a static evidence ledger. A second reviewer should inspect the expected sets before these fixtures are treated as an evaluation benchmark.",
        "",
        "## Case results",
        "",
        "| Case | Scenario | Expected affected | Actual affected | Result |",
        "|---|---|---|---|---|",
    ]
    for d in details:
        lines.append(f"| {d['case_id']} | {d['title']} | {', '.join(d['expected_affected']) or '—'} | {', '.join(d['actual_affected']) or '—'} | {'PASS' if d['pass'] else 'FAIL'} |")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Structural benchmark: {passed}/{len(details)} passed; FP={total_fp}; FN={total_fn}; safety={'PASS' if all_safety_ok else 'FAIL'}")
    print(f"Wrote {OUT_MD.name} and {OUT_JSON.name}")
    return 0 if passed == len(details) and all_safety_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
