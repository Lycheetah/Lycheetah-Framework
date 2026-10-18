#!/usr/bin/env python3
"""Reproduce early audit blockers in the frozen v2.0 inherited runtime.

Exit 1 means at least one OPEN finding reproduced, not a successful safety gate.
Exit 2 means the probe itself could not execute. No source is changed and no
action is executed. Host permission artifacts below are synthetic test fixtures.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

RUNTIME = Path(__file__).resolve().parent / "v2.0/baseline/runtime"
sys.path.insert(0, str(RUNTIME))


def run_probes():
    import compact
    import meaning_diff
    import pragmatics
    import sxpl_v02
    from authz import grant_claims, sign_fixture
    from authority_bridge import inspect
    from dialogue10 import parse_document

    findings = []

    def record(identity, reproduced, evidence):
        findings.append({"id": identity,
                         "status": "OPEN_REPRODUCED" if reproduced else "NOT_REPRODUCED_REQUIRES_REVIEW",
                         "evidence": evidence})

    ast = {"lang": "SXP-L", "schema": "0.2.0", "register": "canonical",
           "clause": {"mood": "assert", "polarity": "positive", "modality": None,
                      "time": None, "op": "USR:A", "roles": {}}}
    sxpl_v02.validate_ast(ast)
    reparsed = sxpl_v02.parse(sxpl_v02.render(ast))
    record("USR_NATIVE36_ALIAS", ast != reparsed,
           {"before": "USR:A", "after": reparsed["clause"]["op"]})

    try:
        compact.hear_compact("ti ariva.")
    except sxpl_v02.SXPError as error:
        record("ARRIVE_VALENCY", True, {"exception": str(error)})
    else:
        record("ARRIVE_VALENCY", False, {})

    first = pragmatics.parse_expression("mi hira bakumo fura ti ariva mi tesavo devora")
    second = pragmatics.parse_expression("mi hira bakumo fura ti satoma tesavo devora")
    kinds = [first["node"]["kind"], second["node"]["kind"]]
    record("ATTITUDE_SCHEMA_SPLIT", kinds[0] != kinds[1], {"node_kinds": kinds})

    consent = "mi periva ti bakumo lenova gonape darafa dimotu tesavo devora"
    try:
        meaning_diff.compare(consent, consent)
    except sxpl_v02.SXPError as error:
        record("MEANING_DIFF_CONSENT", True, {"exception": str(error)})
    else:
        record("MEANING_DIFF_CONSENT", False, {})
    differences = meaning_diff.compare("mi liva ti devora",
                                       "mi liva gonape agena dimotu devora")["differences"]
    priorities = [d["priority"] for d in differences if "/target/" in d["path"]]
    record("MEANING_DIFF_PARTICIPANTS", bool(priorities) and "high" not in priorities,
           {"target_change_priorities": priorities})

    def dialogue(lines):
        return parse_document("diala 1.0\npersona elena\npersona agena\n"
                              "tura elena to agena\n" + "\n".join(lines) + "\nenda\n")

    def report(doc):
        key = b"local-synthetic-not-a-production-key"
        claims = grant_claims("probe_grant", "elena", "agena", "publish_post", "darafa", 100, 200)
        request = {"grantee": "agena", "operation": "publish_post", "resource": "darafa"}
        return inspect(doc, request, [sign_fixture(claims, key)],
                       {"elena": key}, {"elena": {"darafa"}}, now=150)

    denial_results = {}
    for word in ("nelora", "revona"):
        result = report(dialogue([f"lina u1 ^ mi {word} ti bakumo tavona gonape darafa dimotu tesavo devora"]))
        denial_results[word] = {"policy_allowed": result["policy"]["allowed"],
                                "review_advised": result["review_advised"],
                                "boundary_count": len(result["reported_boundaries"])}
    record("LINGUISTIC_DENIAL_REVOCATION", all(r["policy_allowed"] and not r["review_advised"]
                                             for r in denial_results.values()), denial_results)

    repaired = report(dialogue([
        "lina u1 ^ mi resama ti bakumo tavona gonape darafa dimotu tesavo devora",
        "lina u2 ^ mi dalora ti bakumo tavona gonape darafa dimotu tesavo devora",
        "repara u1 u2",
    ]))
    ids = [r["id"] for r in repaired["reported_boundaries"]]
    record("SUPERSEDED_REFUSAL", "u1" in ids, {"reported_boundary_ids": ids})

    try:
        dialogue(["lina u1 ^ mi liva ti devora", "lina u2 ^ mi luma ti devora",
                  "lina u3 ^ mi rava ti devora", "repara u2 u3", "repara u1 u2"])
    except sxpl_v02.SXPError as error:
        record("SUPERSEDED_REPAIR_TARGET", False, {"exception": str(error)})
    else:
        record("SUPERSEDED_REPAIR_TARGET", True, {"already_superseded_target_accepted": True})
    return {"source": "frozen v2.0 baseline/runtime", "findings": findings,
            "execution_performed": False, "human_results": 0}


def main():
    try:
        report = run_probes()
    except Exception as error:
        print(json.dumps({"status": "PROBE_DID_NOT_COMPLETE", "error": type(error).__name__,
                          "detail": str(error)}))
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if any(f["status"] == "OPEN_REPRODUCED" for f in report["findings"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())
