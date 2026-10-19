#!/usr/bin/env python3
"""Offline record-preservation demo, using the installed LAMAGUE codec.

No models, network, inference from prose, training dictionary or implicit writes.
Exit codes in --candidate mode: 0 exact record, 1 changed, 2 malformed input.
"""

from __future__ import annotations

import argparse
import base64
import copy
import gzip
import hashlib
import json
import platform
import sys
import zlib
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from lycheetah.compaction.codec import (  # noqa: E402
    CRITICAL_FIELDS,
    REQUIRED_FIELDS,
    CodecError,
    canonical_json,
    classify,
    decode,
    encode,
    safety_violations,
    validate_packet,
)

HERE = Path(__file__).resolve().parent
BUDGETS = (1024, 2048, 4096)
LABELS = {
    "authority": "Who may decide",
    "unknowns": "What is still unknown",
    "dissent": "Who objected, and why",
    "risk": "Declared risk",
    "evidence": "Evidence and its source",
    "recovery": "How to recover",
    "horizon": "When to review",
    "yield": "The next step",
}


def compare_records(reference: Any, candidate: Any) -> dict[str, Any]:
    """Compare every declared field; never turn a critical-hash match into 'safe'.

    Equality means identical canonical JSON values, not equivalent human meaning.
    Schema validation is also reported. A malformed reference is an input error.
    """
    reference = validate_packet(copy.deepcopy(reference))
    shape_error = None
    try:
        validate_packet(copy.deepcopy(candidate))
    except (CodecError, TypeError) as error:
        shape_error = str(error)
    obj = candidate if isinstance(candidate, dict) else {}
    fields = sorted(set(reference) | set(obj))
    changes = []
    for field in fields:
        before_present, after_present = field in reference, field in obj
        same = (
            before_present == after_present
            and canonical_json(reference.get(field)) == canonical_json(obj.get(field))
        )
        if not same:
            changes.append({
                "field": field,
                "label": LABELS.get(field, field),
                "before_present": before_present,
                "after_present": after_present,
                "before": reference.get(field),
                "after": obj.get(field),
                "in_critical_projection": field in CRITICAL_FIELDS,
            })
    exact = not changes and shape_error is None
    return {
        "status": "MALFORMED_RECORD" if shape_error else (
            "EXACT_RECORD" if exact else "CHANGED_RECORD"
        ),
        "record_match": exact,
        "fields_examined": len(fields),
        "unchanged_fields": len(fields) - len(changes),
        "changes": changes,
        "shape_error": shape_error,
        "codec_classification": None if shape_error else classify(reference, candidate),
        "declared_rule_violations": None if shape_error else safety_violations(candidate),
    }


def formats(packet: dict[str, Any]) -> list[dict[str, Any]]:
    """Measure complete text messages; charge gzip's base64 and prefix overhead."""
    plain = canonical_json(packet)
    compressed = "GZ1" + base64.b64encode(
        gzip.compress(plain.encode("utf-8"), compresslevel=9, mtime=0)
    ).decode("ascii")
    alternatives = [
        ("json", "Compact JSON", plain, json.loads(plain), "JSON parser"),
        ("lamague", "LAMAGUE L1", encode(packet), decode(encode(packet)), "LAMAGUE L1 decoder"),
        (
            "gzip-json", "JSON + gzip + base64", compressed,
            json.loads(gzip.decompress(base64.b64decode(compressed[3:]))),
            "Base64 decoder, gzip decoder, JSON parser",
        ),
    ]
    rows = []
    for key, label, wire, restored, decoder in alternatives:
        comparison = compare_records(packet, restored)
        size = len(wire.encode("utf-8"))
        rows.append({
            "id": key, "label": label, "bytes": size, "wire": wire,
            "required_decoder": decoder,
            "exact_roundtrip": comparison["record_match"],
            "fields_preserved": comparison["unchanged_fields"],
            "budget_fit": {str(limit): size <= limit for limit in BUDGETS},
        })
    return rows


def controls(packet: dict[str, Any]) -> list[dict[str, Any]]:
    """Construct visible failure controls; these are not model-generated summaries."""
    cases = []

    def add(key: str, title: str, candidate: dict[str, Any], exact: bool = False) -> None:
        cases.append({
            "id": key, "title": title, "expected_exact": exact,
            "candidate": candidate, "comparison": compare_records(packet, candidate),
        })

    add("unchanged", "Keep the original handover", copy.deepcopy(packet), True)
    add("reordered", "Reorder JSON keys only", dict(reversed(list(packet.items()))), True)
    candidate = copy.deepcopy(packet)
    candidate["authority"][0]["scope"] = "Publish the release immediately."
    add("permission", "Broaden permission to publish", candidate)
    candidate = copy.deepcopy(packet)
    candidate["unknowns"] = []
    add("unknowns", "Drop the unanswered questions", candidate)
    candidate = copy.deepcopy(packet)
    candidate["dissent"][0]["party"] = "Mira"
    add("speaker", "Attribute Jules's objection to Mira", candidate)
    candidate = copy.deepcopy(packet)
    candidate["dissent"] = []
    add("dissent", "Remove the objection", candidate)
    candidate = copy.deepcopy(packet)
    candidate["risk"] = "LOW"
    add("risk", "Lower the declared risk", candidate)
    candidate = copy.deepcopy(packet)
    candidate["evidence"][0]["text"] = "The desktop, phone and accessibility checks passed."
    add("evidence", "Invent a stronger test result", candidate)
    candidate = copy.deepcopy(packet)
    candidate["recovery"] = []
    add("recovery", "Remove the recovery path", candidate)
    candidate = copy.deepcopy(packet)
    candidate["horizon"] = "Publish immediately."
    add("horizon", "Replace the review condition", candidate)
    candidate = copy.deepcopy(packet)
    candidate["yield"] = "Publish now without further review."
    add("next-step", "Change the next step to publication", candidate)
    candidate = copy.deepcopy(packet)
    del candidate["authority"]
    add("malformed", "Delete a required field", candidate)
    return cases


def build_report() -> dict[str, Any]:
    case = json.loads((HERE / "case.json").read_text(encoding="utf-8"))
    packet = validate_packet(copy.deepcopy(case["packet"]))
    rows = formats(packet)
    cases = controls(packet)
    sources = [
        HERE / "case.json", HERE / "demo.py", HERE / "page.html",
        ROOT / "lycheetah/compaction/codec.py",
    ]
    return {
        "schema": "LYCHEETAH-HANDOVER-DEMO-1",
        "evidence_status": "Constructed example; local deterministic record comparison.",
        "case": case,
        "field_count": len(REQUIRED_FIELDS),
        "critical_fields": CRITICAL_FIELDS,
        "budgets_utf8_bytes": list(BUDGETS),
        "formats": rows,
        "controls": cases,
        "summary": {
            "formats_measured": len(rows),
            "exact_roundtrips": sum(row["exact_roundtrip"] for row in rows),
            "controls_examined": len(cases),
            "controls_matching_expectation": sum(
                row["comparison"]["record_match"] == row["expected_exact"] for row in cases
            ),
        },
        "environment": {"python": platform.python_version(), "zlib": zlib.ZLIB_RUNTIME_VERSION},
        "source_sha256": {
            path.relative_to(ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sources
        },
        "boundaries": [
            "The source-to-packet mapping was authored by us, not extracted or verified by the codec.",
            "Every format gets the same packet. No format is truncated to fit a budget.",
            "Sizes are UTF-8 bytes, not model tokens; complete base64 and prefix costs are included.",
            "Decoder code is assumed available and excluded for every format. L1 uses no codebook.",
            "The JSON baseline receives the same full-field comparison as LAMAGUE.",
            "Changed-record controls are deliberately authored, not natural-language benchmark results.",
            "Exact record equality does not establish truth, human understanding, consent or safe execution.",
            "A critical-hash match omits risk, evidence, operations, horizon, yield, id and schema.",
            "No models, external participants, model-token measurements or independent replication ran.",
        ],
    }


def render_page(report: dict[str, Any]) -> str:
    template = (HERE / "page.html").read_text(encoding="utf-8")
    marker = "__HANDOVER_REPORT_JSON__"
    if template.count(marker) != 1:
        raise ValueError("page template must contain exactly one data marker")
    # Prevent source text from closing the data script element or injecting HTML.
    data = json.dumps(report, ensure_ascii=True, sort_keys=True).replace("<", "\\u003c")
    return template.replace(marker, data)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print the complete result as JSON")
    parser.add_argument("--reference", type=Path, help="Your reference packet JSON file")
    parser.add_argument("--candidate", type=Path, help="Your received packet JSON file")
    parser.add_argument("--write-report", type=Path, help="Explicitly write the example report")
    parser.add_argument("--write-page", type=Path, help="Explicitly write the offline HTML page")
    args = parser.parse_args(argv)
    if bool(args.reference) != bool(args.candidate):
        parser.error("--reference and --candidate must be supplied together")
    if args.reference and (args.write_report or args.write_page):
        parser.error("build outputs apply to the example, not a private custom record")
    try:
        if args.reference:
            reference = json.loads(args.reference.read_text(encoding="utf-8"))
            candidate = json.loads(args.candidate.read_text(encoding="utf-8"))
            result = compare_records(reference, candidate)
            if args.json:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print(f"{result['status']}: {result['unchanged_fields']}/{result['fields_examined']} fields unchanged")
                for change in result["changes"]:
                    print(f"  changed: {change['field']}")
                if result["shape_error"]:
                    print(f"  malformed: {result['shape_error']}")
            return 2 if result["shape_error"] else (0 if result["record_match"] else 1)
        report = build_report()
        if args.write_report:
            args.write_report.write_text(
                json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
        if args.write_page:
            args.write_page.write_text(render_page(report), encoding="utf-8")
        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            print("LAMAGUE handover demonstration — constructed example, no model calls")
            for row in report["formats"]:
                print(f"  {row['label']}: {row['bytes']} UTF-8 bytes; {row['fields_preserved']}/{report['field_count']} fields restored")
            summary = report["summary"]
            print(f"  Controls: {summary['controls_matching_expectation']}/{summary['controls_examined']} expected outcomes")
            print("  Exact records do not establish truth or human understanding.")
        good = all(row["exact_roundtrip"] for row in report["formats"])
        good = good and report["summary"]["controls_matching_expectation"] == len(report["controls"])
        return 0 if good else 1
    except (OSError, ValueError, TypeError) as error:
        print(f"Input/build error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
