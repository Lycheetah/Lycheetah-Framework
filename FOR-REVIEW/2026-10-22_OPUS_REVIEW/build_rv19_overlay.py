"""Build RV19_claim_review_overlay.json: one row per register claim.

Usage: python3 -B build_rv19_overlay.py <framework-root>

Each row joins the author status, the 2026-10-20 review classification, this review's verdict on
that classification, and the state of every evidence reference on HEAD and after the staged
pointer patch. "resolves" means the path exists; only references this review read for the claim's
token are marked "resolves, silent". A claim not re-audited here says so.
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
REVIEW = ROOT / "FOR-REVIEW" / "2026-10-22_OPUS_REVIEW"
register = json.loads(subprocess.run(["git", "show", "HEAD:28_DEFENSE/CLAIMS.json"], cwd=ROOT,
                                     capture_output=True, check=True).stdout)
assessments = {a["claim_id"]: a for a in json.loads(
    (ROOT / "28_DEFENSE/review_2026_10_20/claim-assessments.json").read_text(encoding="utf-8"))["assessments"]}
repairs = {r["claim_id"]: r for r in json.loads(
    (REVIEW / "RV19_claims_pointer_repairs.json").read_text(encoding="utf-8"))["repairs"]}

B17, B18 = "BATCH17_FINDINGS_AND_LEDGER.md", "BATCH18_FINDINGS_AND_LEDGER.md"
VERDICTS = {
    "CAS-009": ("sharpen", [B18 + " F1 F2 F6", "repro_batch18 B3 B4"],
                "Not merely unrerun: no runner exists. cascade_synthetic_experiment.py and every EMPIRICAL_RESULTS "
                "material are absent from the tree and all history. The three accounts disagree: 0.58->0.93 is +60.3%, "
                "the 200-trial table gives pooled d 3.52, the SYNTHESIS SDs give d 5.03; none gives 2.84 with +40.3%. UNVERIFIED."),
    "CAS-010": ("sharpen", [B18 + " F3 F4", "repro_batch18 B4 B5 B6 B7"],
                "Rerun here: reproduces exactly, and the additive baseline also scores 1.0 in every trial (t 0, d 0). "
                "The +110% is over a static no-update baseline; the 200 trials per domain are identical deterministic "
                "runs. MEASURED: beats no update, ties additive update."),
    "CAS-011": ("sharpen", [B18 + " F5 F6", "repro_batch18 B3 B4"],
                "No runner or data exists. 0.42->0.02 (register) and 1.00%->0.048% (EMPIRICAL_RESULTS) both give 95.2% "
                "from different numbers. UNVERIFIED."),
    "LYV-001": ("sharpen", [B17, B18 + " F8"],
                "Agree, and RV18 measured the honest symbolic tally at 2/6 with sympy DID NOT RUN. Neither register "
                "pointer states 11/11; only papers/LYCHEETAH_SYNTHESIS_v0.1.md:136 does."),
    "HAR-004": ("sharpen", [B18 + " F8", "repro_batch18 B2"],
                "Agree on the classification. The CLAUDE.md pointer has been silent since the reforge (3980262); the "
                "table lives in AGENTS.md and 10_HARMONIA_L6/essentials.md."),
    "XFW-005": ("sharpen", [B18 + " F8", "repro_batch18 B2"],
                "Agree on the classification. CLAUDE.md no longer states the Two-Point Protocol; THE_SOL_PROTOCOL.md:80 does."),
    "XFW-006": ("sharpen", [B18 + " F8", "repro_batch18 B2"],
                "Agree on the classification. CLAUDE.md no longer defines PGF; THE_SOL_PROTOCOL.md:131 does."),
    "ANA-003": ("sharpen", [B18 + " F9"],
                "Agree. The register's count of 4 is stated nowhere that resolves; the only resolving statement, "
                "30_MAPS/FORMAL_SPINE.md:439, says TC(pi, >=3). TC_CATALOG.md stays missing."),
    "ANA-004": ("sharpen", [B18 + " F9"],
                "Agree. FORMAL_SPINE.md:439 says TC(symmetry_groups, >=3), not 4. TC_CATALOG.md stays missing."),
}
for cid in ("CAS-003", "MIC-003", "XFW-001", "HAR-001", "HAR-002", "ELI-003", "CRY-003", "TRI-007"):
    VERDICTS[cid] = ("agree", [B17], "Matches this review's RV18 witnesses.")
SILENT = {
    "HAR-004": {"CLAUDE.md"}, "XFW-005": {"CLAUDE.md"}, "XFW-006": {"CLAUDE.md"},
    "CAS-009": {"29_GOVERNANCE/EMPIRICAL_INVENTORY.md"}, "CAS-010": {"29_GOVERNANCE/EMPIRICAL_INVENTORY.md"},
    "CAS-011": {"29_GOVERNANCE/EMPIRICAL_INVENTORY.md"},
    "LYV-001": {"11_MATHEMATICAL_FOUNDATIONS/MATHEMATICS_FOUNDATIONS.md", "29_GOVERNANCE/EMPIRICAL_INVENTORY.md"},
    "CAS-008": {"11_MATHEMATICAL_FOUNDATIONS/MATHEMATICS_FOUNDATIONS.md"},
}


def refs(text):
    return [s.strip() for s in text.split(";") if s.strip()]


def state(cid, ref):
    if not (ROOT / ref).exists():
        return "missing"
    return "resolves, silent" if ref in SILENT.get(cid, ()) else "resolves"


rows = []
for claim in register["claims"]:
    cid = claim["claim_id"]
    a = assessments[cid]
    verdict, witnesses, note = VERDICTS.get(cid, ("not re-audited in RV19", [], ""))
    row = {
        "claim_id": cid,
        "author_status": claim["status"],
        "review_2026_10_20": a["review_classification"],
        "rv19_verdict": verdict,
        "rv19_note": note,
        "witnesses": witnesses,
        "references_head": [{"ref": r, "state": state(cid, r)} for r in refs(claim["evidence_path"])],
    }
    if cid in repairs:
        row["references_after_patch"] = refs(repairs[cid]["after"])
        if "stated_at" in repairs[cid]:
            row["stated_at"] = repairs[cid]["stated_at"]
    rows.append(row)

assert len(rows) == 71 and set(VERDICTS) <= {r["claim_id"] for r in rows}
out = {
    "date": "2026-10-22", "review": "RV19",
    "register_sha256": "9d8e76dccb7b34e93787b6355d55cf5cabd394dc123bf56d56b752308464eb9f",
    "verdict_counts": {v: sum(r["rv19_verdict"] == v for r in rows) for v in sorted({r["rv19_verdict"] for r in rows})},
    "disagreements_with_2026_10_20": [r["claim_id"] for r in rows if r["rv19_verdict"] == "disagree"],
    "claims": rows,
}
(REVIEW / "RV19_claim_review_overlay.json").write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("overlay:", out["verdict_counts"], "disagreements:", out["disagreements_with_2026_10_20"])
