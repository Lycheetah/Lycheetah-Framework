#!/usr/bin/env python3
"""
lamague check — does this decision record still carry the parts that make it accountable?

WHAT THIS IS FOR
----------------
Send a decision up three levels of an organisation and watch what evaporates.
Not the conclusion — that survives. What goes is the dissent, the list of people
affected, the things nobody had worked out yet, the rollback plan. By the time
it reaches the top it reads as clean and settled, and the parts that would have
made someone hesitate are gone.

Nobody lied. It just got shorter.

`22_REVERSIBLE_COMPRESSION_v1.0` proved those deletions are *detectable* — 324
of 324 constructed mutations across nine classes. But it proves it on LAMAGUE
semantic packets, and nobody outside this project has one of those.

**This runs the same check on ordinary JSON.** Point it at an incident report, a
change record, a model card, a clinical decision log. It does not ask you to
adopt LAMAGUE, learn a notation, or believe anything. It reads your file, finds
whichever accountability fields you already have under whatever names you gave
them, and tells you which ones are missing.

That is the whole tool. It is deliberately small.

THE TEN FIELDS
--------------
Taken from the codec's own `CRITICAL_FIELDS`, not invented here:

    purpose · claim · unknowns · invariants · authority
    participants · affectedParties · dissent · valueFlow · recovery

They are the ten whose deletion the benchmark detects. A record carrying all ten
can be argued with. A record missing dissent and affected parties can only be
agreed with, which is a different thing and usually worse.

USAGE
-----
    python3 lamague_check.py record.json
    python3 lamague_check.py record.json --strict     # exit 1 on any gap
    python3 lamague_check.py record.json --explain    # why each field matters
    python3 lamague_check.py --demo                   # run on a worked example

Exit codes: 0 clean · 1 gaps found (with --strict) · 2 unreadable input.
Standard library only. No network, no dependency, no account.

Author: Sol, for the Lycheetah Framework. MIT.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
CODEC_SRC = HERE.parent / "22_REVERSIBLE_COMPRESSION_v1.0" / "src"

#: The ten protected fields, with the aliases real records actually use.
#: Aliasing is the whole usability move: nobody's incident report has a field
#: called `affectedParties`, and refusing to read `impacted_users` would make
#: this tool useless outside the corpus that invented the name.
FIELDS: Dict[str, Dict[str, Any]] = {
    "purpose": {
        "why": "What was this for? Without it, nobody can tell whether it worked.",
        "aliases": ["purpose", "goal", "objective", "intent", "why", "rationale",
                    "motivation", "aim"],
    },
    "claim": {
        "why": "What is being asserted? An unstated claim cannot be checked.",
        "aliases": ["claim", "decision", "conclusion", "outcome", "finding",
                    "summary", "resolution", "determination"],
    },
    "unknowns": {
        "why": "What did you still not know? This is the first field to vanish "
               "and the one that most often mattered.",
        "aliases": ["unknowns", "uncertainties", "open_questions", "risks_unknown",
                    "gaps", "todo", "unresolved", "assumptions", "caveats",
                    "limitations"],
    },
    "invariants": {
        "why": "What must stay true regardless? Without these, later changes "
               "cannot tell whether they broke something.",
        "aliases": ["invariants", "constraints", "requirements", "guarantees",
                    "must_hold", "sla", "acceptance_criteria", "policies"],
    },
    "authority": {
        "why": "Who had the right to decide this? An unsigned decision has no "
               "accountable party.",
        "aliases": ["authority", "owner", "approver", "decided_by", "signoff",
                    "sign_off", "accountable", "responsible", "approved_by"],
    },
    "participants": {
        "why": "Who was in the room? Determines whose knowledge was available.",
        "aliases": ["participants", "attendees", "contributors", "team",
                    "involved", "reviewers", "stakeholders_present"],
    },
    "affectedParties": {
        "why": "Who bears the consequences? Frequently absent, and its absence "
               "is how harm becomes nobody's problem.",
        "aliases": ["affectedparties", "affected_parties", "affected", "impacted",
                    "impacted_users", "impacted_parties", "customers_affected",
                    "stakeholders", "users_affected", "blast_radius"],
    },
    "dissent": {
        "why": "Who disagreed, and on what grounds? A record with no dissent "
               "field cannot distinguish consensus from silence.",
        "aliases": ["dissent", "objections", "disagreement", "concerns",
                    "minority_view", "opposed", "reservations", "pushback"],
    },
    "valueFlow": {
        "why": "Who gains and who pays? Decisions that move value without "
               "saying so are how conflicts of interest hide.",
        "aliases": ["valueflow", "value_flow", "cost", "benefit", "tradeoffs",
                    "trade_offs", "who_benefits", "impact", "economics"],
    },
    "recovery": {
        "why": "How do you undo this? An irreversible step taken without a "
               "rollback plan is a different decision from one with it.",
        "aliases": ["recovery", "rollback", "mitigation", "remediation",
                    "revert", "contingency", "fallback", "undo", "backout"],
    },
}

EMPTY_MARKERS = {"", "n/a", "na", "none", "tbd", "todo", "-", "null",
                 "unknown", "pending", "?"}


def flatten(obj: Any, prefix: str = "") -> Dict[str, Any]:
    """All leaf paths in a nested structure — records nest, and fields hide."""
    out: Dict[str, Any] = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            key = f"{prefix}.{k}" if prefix else str(k)
            out[key] = v
            out.update(flatten(v, key))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out.update(flatten(v, f"{prefix}[{i}]"))
    return out


def is_empty(v: Any) -> bool:
    if v is None:
        return True
    if isinstance(v, str):
        return v.strip().lower() in EMPTY_MARKERS
    if isinstance(v, (list, dict, tuple, set)):
        return len(v) == 0
    return False


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


def find_field(record: Dict[str, Any], aliases: List[str]) -> Tuple[Optional[str], Any]:
    """
    Locate a protected field under whatever name this record gave it.

    Exact alias match first, then suffix match on nested paths. Substring
    matching is deliberately NOT used — `cost` would match `costume` and a tool
    that reports fields you do not have is worse than one that misses some.
    """
    flat = flatten(record)
    wanted = {norm(a) for a in aliases}

    for path, value in flat.items():
        if norm(path.split(".")[-1].split("[")[0]) in wanted:
            return path, value
    for path, value in flat.items():
        leaf = norm(path.split(".")[-1].split("[")[0])
        if any(leaf.endswith(w) or w.endswith(leaf) for w in wanted if len(w) > 4):
            return path, value
    return None, None


def check(record: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows = []
    for field, spec in FIELDS.items():
        path, value = find_field(record, spec["aliases"])
        if path is None:
            status = "MISSING"
        elif is_empty(value):
            status = "EMPTY"
        else:
            status = "PRESENT"
        rows.append({"field": field, "status": status, "found_as": path,
                     "why": spec["why"], "value": value})
    return rows


DEMO = {
    "incident_id": "INC-2026-0814",
    "title": "Payment retries exhausted during regional failover",
    "rationale": "Restore payment processing within the 30-minute SLA.",
    "conclusion": "Failed over to the secondary region and drained the retry queue.",
    "approved_by": "s.okafor (on-call IC)",
    "attendees": ["s.okafor", "j.lindqvist", "payments-oncall"],
    "constraints": ["No double-charging", "PCI scope unchanged"],
    "rollback": "Re-point DNS to primary; queue is idempotent, safe to replay.",
    "impacted_users": [],
    "open_questions": "TBD",
}


def render(rows: List[Dict[str, Any]], explain: bool, source: str) -> Tuple[str, int]:
    icons = {"PRESENT": "✓", "EMPTY": "⚠", "MISSING": "✗"}
    L = ["=" * 72,
         "LAMAGUE CHECK — decision record accountability",
         "=" * 72,
         f"record: {source}", ""]
    for r in rows:
        icon = icons[r["status"]]
        note = ""
        if r["status"] == "PRESENT":
            note = f'found as "{r["found_as"]}"'
        elif r["status"] == "EMPTY":
            note = f'"{r["found_as"]}" is present but empty'
        else:
            note = "no field found under any known name"
        L.append(f"  {icon} {r['field']:<17} {note}")
        if explain and r["status"] != "PRESENT":
            L.append(f"      {r['why']}")

    present = sum(1 for r in rows if r["status"] == "PRESENT")
    gaps = [r for r in rows if r["status"] != "PRESENT"]
    L += ["", f"  {present}/{len(rows)} protected fields carried"]
    if gaps:
        L.append(f"  {len(gaps)} accountability gap(s): "
                 + ", ".join(r["field"] for r in gaps))
        L += ["",
              "  These are the fields whose deletion the LAMAGUE benchmark detects",
              "  324/324 times. A record missing them can be agreed with but not",
              "  argued with — run with --explain for what each one is for."]
    else:
        L += ["", "  No gaps. This record can be argued with, which is the point."]
    L.append("=" * 72)
    return "\n".join(L), len(gaps)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("record", nargs="?", help="path to a JSON decision record")
    ap.add_argument("--strict", action="store_true", help="exit 1 if any gap is found")
    ap.add_argument("--explain", action="store_true", help="say why each missing field matters")
    ap.add_argument("--demo", action="store_true", help="run on a worked example")
    ap.add_argument("--json", metavar="PATH", help="write the result as JSON")
    args = ap.parse_args()

    if args.demo:
        data, source = DEMO, "(built-in demo: an ordinary incident report)"
    elif args.record:
        p = Path(args.record)
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"cannot read {p}: {e}", file=sys.stderr)
            return 2
        source = str(p)
    else:
        ap.print_help()
        return 2

    if not isinstance(data, dict):
        print("expected a JSON object at the top level", file=sys.stderr)
        return 2

    rows = check(data)
    text, gaps = render(rows, args.explain or args.demo, source)
    print(text)

    if args.json:
        Path(args.json).write_text(json.dumps(
            {"source": source, "gaps": gaps,
             "fields": [{k: v for k, v in r.items() if k != "value"} for r in rows]},
            indent=2), encoding="utf-8")
        print(f"\nwrote {args.json}")

    return 1 if (gaps and args.strict) else 0


if __name__ == "__main__":
    raise SystemExit(main())
