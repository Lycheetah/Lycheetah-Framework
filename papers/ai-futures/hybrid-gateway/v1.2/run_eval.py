"""Bounded synthetic checkpoint: latest-known, bitemporal retrieval, hybrid.

This is NOT an LLM benchmark, a held-out evaluation, or a comparison to VersionRAG.
All systems see the same source-checked admitted claims and query constraints.
B0 ignores effective time, B1 respects both clocks but ignores explicit
supersession/withdrawal/conflict; H1 uses query-time version graph and abstention.
"""
from __future__ import annotations
import json
import pathlib
from dataclasses import asdict
from hybrid_gateway import HybridGateway, SourceDocument, ClaimProposal, refund_window_quote_validator

ROOT = pathlib.Path(__file__).resolve().parent
T = lambda day: f"2026-{day}T00:00:00Z"


def make_case(cid: str, sid: str, val: str, effective: str, *, tenant: str = "shop-A",
              scope: str = "NZ-online", supersedes: tuple[str, ...] = ()) -> ClaimProposal:
    return ClaimProposal(cid, tenant, "refunds", "window_days", scope, val, T(effective),
                         sid, f"Refunds allowed within {val} days.", supersedes=supersedes)


def build_fixture() -> HybridGateway:
    g = HybridGateway(semantic_validator=refund_window_quote_validator)
    definitions = [
        ("v1", "official-v1", "14", "01-01", "01-02", "shop-A", "NZ-online", ()),
        ("v2", "official-v2", "21", "02-01", "02-10", "shop-A", "NZ-online", ("v1",)),
        ("v4", "official-future", "30", "04-01", "02-25", "shop-A", "NZ-online", ("v2",)),
        ("v3-dispute", "official-dispute", "35", "02-01", "03-01", "shop-A", "NZ-online", ()),
        ("store", "official-store", "45", "01-01", "03-02", "shop-A", "in-store", ()),
        ("shop-B", "official-B", "7", "01-01", "03-02", "shop-B", "NZ-online", ()),
    ]
    for cid, sid, val, effective, at, tenant, scope, parents in definitions:
        g.register_source(SourceDocument(sid, tenant, f"urn:fictional:{sid}", f"Refunds allowed within {val} days."))
        p = make_case(cid, sid, val, effective, tenant=tenant, scope=scope, supersedes=parents)
        d = g.ingest(p, recorded_at=T(at), reviewer_approved=True)
        if d.disposition != "ALLOW":
            raise RuntimeError(f"Fixture invalid: {d}")
    for target, effective, observed in [
        ("v3-dispute", "03-12", "03-12"),
        ("v2", "03-15", "03-20"),
        ("v4", "04-10", "04-12"),
    ]:
        d = g.withdraw(target, effective_from=T(effective), recorded_at=T(observed), reviewer_approved=True)
        if d.disposition != "ALLOW":
            raise RuntimeError(f"Fixture withdrawal invalid: {d}")
    return g


def conventional_retrieval(g: HybridGateway, case: dict, temporal: bool) -> tuple[str, str | None, list[str]]:
    tenant, scope = case.get("tenant", "shop-A"), case.get("scope", "NZ-online")
    effective, known = T(case["effective"]), T(case["known"])
    matches = [c for c in g.claims.values()
               if (c.tenant, c.subject, c.predicate, c.scope) == (tenant, "refunds", "window_days", scope)
               and g.admitted_at[c.claim_id] <= known
               and (not temporal or (c.valid_from <= effective and (c.valid_until is None or effective < c.valid_until)))]
    if not matches:
        return ("ABSTAIN_NO_EVIDENCE", None, [])
    # Conventional latest-hit retrieval: deterministic tie-breaking; no graph adjudication.
    rank = (lambda c: (c.valid_from, g.admitted_at[c.claim_id], c.claim_id)) if temporal else \
           (lambda c: (g.admitted_at[c.claim_id], c.claim_id))
    best = max(matches, key=rank)
    return ("ANSWER", best.value, [best.source_id])


def assess(g: HybridGateway, case: dict, engine: str) -> dict:
    if engine == "H1":
        r = g.query(tenant=case.get("tenant", "shop-A"), subject="refunds", predicate="window_days",
                    scope=case.get("scope", "NZ-online"), effective_at=T(case["effective"]),
                    known_at=T(case["known"]))
        state, value, source_ids = r.disposition, r.value, [c["source_id"] for c in r.citations]
        provenance_ok = all(g.sources[c["source_id"]].digest == c["digest"] and
                            c["evidence_quote"] in g.sources[c["source_id"]].body
                            for c in r.citations)
    else:
        state, value, source_ids = conventional_retrieval(g, case, temporal=(engine == "B1"))
        provenance_ok = all(source_id in g.sources for source_id in source_ids)
    return {"state": state, "value": value, "citations": source_ids,
            "correct": state == case["kind"] and value == case["expect"],
            "citation_anchor_valid": provenance_ok}


def run() -> dict:
    with (ROOT / "fixtures" / "synthetic_eval_cases.json").open() as f:
        scenarios = json.load(f)
    g = build_fixture()
    results = []
    for case in scenarios["cases"]:
        comparison = {engine: assess(g, case, engine) for engine in ("B0", "B1", "H1")}
        results.append({"id": case["id"], "expected": {"state": case["kind"], "value": case["expect"]}, **comparison})
    stats = {engine: {"correct": sum(r[engine]["correct"] for r in results),
                      "total": len(results),
                      "citation_anchor_valid": sum(r[engine]["citation_anchor_valid"] for r in results)}
             for engine in ("B0", "B1", "H1")}
    return {"evaluation": scenarios["dataset"], "data_status": scenarios["status"],
            "method": "Deterministic fictional cases, authored by experiment builder; no model inference or live user data",
            "baseline_limits": {"B0": "latest admitted document, scope-filtered, ignores valid time and disputes",
                                "B1": "bi-temporal latest-hit retrieval, no supersession, withdrawal, or conflict adjudication",
                                "H1": "source-checked ledger with two clocks, explicit supersession, withdrawals and abstention"},
            "scores": stats, "cases": results, "ledger_head": g.head_digest,
            "ledger_chain_verified": g.verify_chain()}


if __name__ == "__main__":
    output = run()
    destination = ROOT / "results" / "synthetic_evaluation_v0.2.json"
    destination.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps(output["scores"], indent=2))
    print("Ledger integrity check:", output["ledger_chain_verified"])
    print("Full per-case results:", destination)
