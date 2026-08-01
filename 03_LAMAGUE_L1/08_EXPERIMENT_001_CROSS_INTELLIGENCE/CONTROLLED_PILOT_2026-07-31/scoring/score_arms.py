#!/usr/bin/env python3
"""Score LAMAGUE (treatment) against plain English (control) on ONE question:

    does the notation preserve protected meaning better than prose?

WHAT IS MEASURED, AND WHY IT IS NOT ACCURACY
--------------------------------------------
There is no ground truth to score against here — the sealed references belong to
the operator arm and reading them would contaminate this comparison. So this
measures the two things the preregistration actually protects, both of which are
checkable without a reference:

  1. PRESERVATION — did the decoder keep the protected field populated when the
     source supports it, rather than dropping it? The failure the experiment
     names is UNSAFE_COLLAPSE: a syntactically valid packet that lost content.

  2. FABRICATION — did the decoder INVENT authority, evidence, consequences or
     consensus that the source never supplied? Both arms are told not to. A
     notation that suppresses invention is doing real work.

  3. AGREEMENT — do independent lineages converge on the same protected fields?
     Convergence is the cross-intelligence claim. Prose that produces eight
     different readings while LAMAGUE produces one is the thesis surviving.

⚠ HONESTY BOUNDARY. This is a FIELD-LEVEL structural comparison, not semantic
   equivalence. It can say "the unknown was kept" — it cannot say "the unknown
   was understood correctly." Only the operator arm, scoring against sealed
   references, can do that. Nothing here should be reported as accuracy.
"""
from __future__ import annotations

import json
import statistics
from collections import defaultdict
from pathlib import Path

# ⚠ THE CONTROL ARM POINTED AT A DELETED SESSION SCRATCHPAD.
# `/tmp/claude-1000/…/de0fd768-…/scratchpad/control_submissions` no longer exists,
# so re-running this scorer reported PLAIN ENGLISH with 0 packets and silently
# dropped the entire control arm — the headline (+0.195 preservation) could not be
# re-derived from the repository at all. The 29 submissions were preserved into
# `control_arm/` beside this script; the path simply never followed them.
# Anchored relative to THIS file so it cannot rot again when the CWD changes.
SC = Path(__file__).resolve().parent.parent
TREAT = Path("/home/guestpc/CODEX_AURA_PRIME/03_LAMAGUE_L1/"
             "08_EXPERIMENT_001_CROSS_INTELLIGENCE/OPERATOR_PACK/submissions/OTHER")
CTRL = SC / "control_arm"

PROTECTED = ["invariants", "unknowns", "authority", "participants",
             "affected_parties", "evidence", "provenance", "dissent",
             "value_ledger", "consequences"]

# Which fields the SOURCE actually supports, per case. Derived from the source
# statements only — never from the sealed references. A decoder cannot be
# credited for keeping a field the source never contained, and cannot be blamed
# for dropping one that was never there.
# Derived by READING each source statement, not by assumption. The first version
# of this table was written from a skim and was wrong in a way that produced a
# headline finding: it declared `consequences` and `provenance` unsupported by
# every case, so a decoder writing "publication of a context-limited result" —
# which C01 states verbatim — scored as FABRICATION. The measured "LAMAGUE
# invents 2.4x more than prose" was an artifact of that mistake, not an effect.
#
# C01 "publish only a context-limited result and retain the unresolved method question"
# C02 "both positions remain attributable while an alternative staged release is proposed"
# C03 "declared, limited to analysis, explicitly consented to, and reversible through deletion"
# C04 "keeps its original purpose and invariants, records lineage, adds ... unresolved question"
# C05 "consequential, an unknown remains, decoder confidence is weak, must expand"
SUPPORTED = {
    "C01_UNPROVEN_CLAIM":       {"unknowns", "evidence", "participants", "consequences"},
    "C02_PROTECTED_DISSENT":    {"dissent", "participants", "consequences"},
    "C03_VISIBLE_EXCHANGE":     {"value_ledger", "participants", "consequences"},
    "C04_SEMANTIC_MIGRATION":   {"invariants", "participants", "provenance"},
    "C05_BREATHING_COMPRESSION": {"unknowns", "invariants"},
}

# Fields the source genuinely does not supply, PER CASE. Populating one of these
# is invention. No case names an authorising party or an affected third party,
# so those are the honest fabrication probes.
NEVER_SUPPORTED_BY_CASE = {
    "C01_UNPROVEN_CLAIM":       {"authority", "affected_parties", "value_ledger"},
    "C02_PROTECTED_DISSENT":    {"authority", "affected_parties", "value_ledger"},
    "C03_VISIBLE_EXCHANGE":     {"authority", "affected_parties", "dissent"},
    "C04_SEMANTIC_MIGRATION":   {"authority", "affected_parties", "dissent", "value_ledger"},
    "C05_BREATHING_COMPRESSION": {"authority", "affected_parties", "dissent", "value_ledger"},
}
NEVER_SUPPORTED = {"authority", "affected_parties"}   # kept for compatibility


def load(d: Path) -> dict:
    out = {}
    for f in sorted(d.glob("*.json")):
        try:
            p = json.loads(f.read_text())
        except ValueError:
            continue
        cid = p.get("case_id", "")
        did = p.get("decoder_id", f.stem)
        if cid:
            out[(cid, did)] = p
    return out


def nonempty(p: dict, field: str) -> bool:
    v = p.get(field)
    if isinstance(v, list):
        return len([x for x in v if str(x).strip()]) > 0
    return bool(str(v or "").strip())


def score(packets: dict, label: str) -> dict:
    pres_hits = pres_total = 0
    fab = 0
    by_case_field = defaultdict(list)
    for (cid, did), p in packets.items():
        want = SUPPORTED.get(cid, set())
        for f in want:
            pres_total += 1
            if nonempty(p, f):
                pres_hits += 1
        for f in NEVER_SUPPORTED_BY_CASE.get(cid, set()):
            if nonempty(p, f):
                fab += 1
        for f in PROTECTED:
            by_case_field[(cid, f)].append(1 if nonempty(p, f) else 0)

    # Agreement: for each (case, field), how uniformly did decoders answer?
    # 1.0 = every decoder made the same call. Mean over all field slots.
    agrees = []
    for (_cid, _f), votes in by_case_field.items():
        if len(votes) < 2:
            continue
        agrees.append(max(sum(votes), len(votes) - sum(votes)) / len(votes))

    n = len(packets)
    return {
        "label": label,
        "packets": n,
        "decoders": len({d for _, d in packets}),
        "preservation": round(pres_hits / pres_total, 3) if pres_total else 0.0,
        "preserved": f"{pres_hits}/{pres_total}",
        # PER PACKET, not a raw count. An earlier version compared a raw 21
        # against a raw 2 while the arms held 15 and 6 packets — a 2.5x sample
        # difference read as a 10x effect. A count is not a rate.
        "fabrication_rate": round(fab / n, 3) if n else 0.0,
        "fabrication_events": fab,
        "agreement": round(statistics.mean(agrees), 3) if agrees else 0.0,
    }


def main() -> None:
    t, c = load(TREAT), load(CTRL)
    rows = [score(t, "LAMAGUE (treatment)"), score(c, "PLAIN ENGLISH (control)")]
    print("\n  EXPERIMENT 001 — TREATMENT vs CONTROL")
    print("  " + "-" * 74)
    print(f"  {'arm':26} {'packets':>8} {'preserved':>11} {'preserve':>9} "
          f"{'fab/pkt':>8} {'agree':>7}")
    for r in rows:
        print(f"  {r['label']:26} {r['packets']:>8} {r['preserved']:>11} "
              f"{r['preservation']:>9.3f} {r['fabrication_rate']:>8.3f} "
              f"{r['agreement']:>7.3f}")
    print("  " + "-" * 74)
    if rows[0]["packets"] and rows[1]["packets"]:
        dp = rows[0]["preservation"] - rows[1]["preservation"]
        da = rows[0]["agreement"] - rows[1]["agreement"]
        df = rows[1]["fabrication_rate"] - rows[0]["fabrication_rate"]
        print(f"\n  preservation delta : {dp:+.3f}   (LAMAGUE minus prose)")
        print(f"  agreement delta    : {da:+.3f}")
        print(f"  fabrication delta  : {df:+.3f} per packet (positive = LAMAGUE invents less)")
        print()
        if dp <= 0.02 and da <= 0.02:
            print("  → THESIS NOT SUPPORTED at this n. Prose preserved protected")
            print("    fields as well as the notation. That is the most valuable")
            print("    result available tonight and it must be published as-is.")
        else:
            print("  → LAMAGUE preserved more / agreed more than prose on these")
            print("    cases. Structural only — NOT semantic accuracy.")
    print("\n  ⚠ field-level structure, not correctness. Only the operator arm,")
    print("    scored against sealed references, can speak to accuracy.\n")


if __name__ == "__main__":
    main()
