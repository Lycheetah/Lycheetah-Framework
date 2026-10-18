"""Author-designed v0.4 contract conformance study, NOT a real-world benchmark.

Run: python run_contract_eval.py --output results/contract_eval_v0.4.json
Labels are based on a fictional operator-authorized clause set, not on an
independent human assessor. This measures enforcement, not LLM extraction quality.
"""
from __future__ import annotations
import argparse
from dataclasses import asdict, replace
import json
from pathlib import Path

from hybrid_gateway import (TrustedClause, TrustedContractRegistry, ClaimProposal,
                            SourceDocument, refund_window_quote_validator)

AT = "2026-10-01T00:00:00Z"
SRC = SourceDocument("manual-1", "fictional-shop", "urn:fictional:policy", (
    "Refunds allowed within 14 days. Loyalty members earn 21 points per order. "
    "EXAMPLE ONLY: Refunds allowed within 60 days. "
    "Refunds not allowed within 90 days. Online orders: refunds within 10 days."
))


def c(quote, grammar, subject, predicate, scope):
    return TrustedClause(SRC.source_id, SRC.digest, SRC.tenant, subject, predicate,
                         scope, quote, grammar, AT)

CLAUSES = [
    c("Refunds allowed within 14 days.", "refund_days_v1", "refunds", "window_days", "store"),
    c("Online orders: refunds within 10 days.", "online_refund_days_v1", "refunds", "window_days", "online"),
    c("Loyalty members earn 21 points per order.", "loyalty_points_v1", "loyalty", "points_per_order", "members"),
]


def p(clause, ident):
    return ClaimProposal(ident, SRC.tenant, clause.subject, clause.predicate,
        clause.scope, clause.parsed_value, AT, SRC.source_id, clause.exact_quote)


def cases():
    positives = [(f"authorized-{i+1}-{j+1}", replace(p(cl, f"good{i}-{j}"),
                                 claim_id=f"good{i}-{j}"), True)
                 for i, cl in enumerate(CLAUSES) for j in range(3)]
    valid = p(CLAUSES[0], "original")
    online = p(CLAUSES[1], "online")
    loyalty = p(CLAUSES[2], "loyalty")
    changes = [
      ("substring-1-in-14", replace(valid, value="1")),
      ("substring-4-in-14", replace(valid, value="4")),
      ("wrong-scope", replace(valid, scope="online")),
      ("wrong-tenant", replace(valid, tenant="other")),
      ("wrong-source-id", replace(valid, source_id="manual-other")),
      ("wrong-effective-start", replace(valid, valid_from="2026-09-01T00:00:00Z")),
      ("unapproved-end", replace(valid, valid_until="2026-11-01T00:00:00Z")),
      ("forged-supersession", replace(valid, supersedes=("x",))),
      ("wrong-subject", replace(valid, subject="loyalty")),
      ("wrong-predicate", replace(valid, predicate="points_per_order")),
      ("not-authorized-example", replace(valid, value="60", evidence_quote="Refunds allowed within 60 days.")),
      ("negated-quote", replace(valid, value="90", evidence_quote="Refunds not allowed within 90 days.")),
      ("loyalty-as-refund", replace(valid, value="21", evidence_quote=loyalty.evidence_quote)),
      ("truncated-quote", replace(valid, evidence_quote="Refunds allowed within 14 days")),
      ("online-substring", replace(online, value="1")),
      ("online-wrong-scope", replace(online, scope="store")),
      ("loyalty-wrong-subject", replace(loyalty, subject="refunds")),
      ("loyalty-substring", replace(loyalty, value="2")),
      ("fabricated-quote", replace(valid, evidence_quote="Returns always allowed within 14 days.")),
      ("wrong-value", replace(valid, value="99")),
      ("unrecognized-empty-value", replace(valid, value="")),
      ("unnatural-paraphrase", replace(valid, evidence_quote="There is a fortnight to request a refund.")),
      ("date-not-timezone-aware", replace(valid, valid_from="2026-10-01T00:00:00")),
      ("unapproved-supersession-order", replace(valid, supersedes=("x", "y"))),
    ]
    return positives + [(name, claim, False) for name, claim in changes]


def score(samples):
    tp = tn = fp = fn = 0
    for expected, observed in samples:
        if expected and observed: tp += 1
        elif not expected and not observed: tn += 1
        elif observed: fp += 1
        else: fn += 1
    return {"true_positive": tp, "true_negative": tn, "false_positive": fp,
            "false_negative": fn, "precision": tp / (tp + fp) if tp + fp else None,
            "recall": tp / (tp + fn) if tp + fn else None,
            "accuracy": (tp + tn) / len(samples)}


def evaluate():
    registry = TrustedContractRegistry([SRC], CLAUSES)
    records = []
    for name, claim, expected in cases():
        # A deliberately weak baseline mimicking v0.3 quote+value checks.
        lexical = (claim.evidence_quote in SRC.body and claim.value in claim.evidence_quote)
        prior_refund = (claim.evidence_quote in SRC.body and
                        refund_window_quote_validator(claim))
        contracted = registry.validate_claim(claim)
        records.append({"case": name, "expected_operator_authorized": expected,
                        "lexical_baseline": lexical, "narrow_regex_baseline": prior_refund,
                        "contracted_v0_4": contracted})
    metrics = {method: score([(r["expected_operator_authorized"], r[method]) for r in records])
               for method in ("lexical_baseline", "narrow_regex_baseline", "contracted_v0_4")}
    return {"version": "v0.4", "source": "fully fictional, author-constructed",
            "label_provenance": "operator-contract conformance; no independent annotation",
            "comparison_scope": "claim admission rule only; no live model or retrieval",
            "total_cases": len(records), "metrics": metrics, "cases": records}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="results/contract_eval_v0.4.json")
    args = ap.parse_args()
    report = evaluate()
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf8")
    print(json.dumps({"total_cases": report["total_cases"], "metrics": report["metrics"]}, indent=2))
