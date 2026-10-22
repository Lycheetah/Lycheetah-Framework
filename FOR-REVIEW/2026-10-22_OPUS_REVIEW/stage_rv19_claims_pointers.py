"""Stage RV19_claims_pointer_repairs.patch for 28_DEFENSE/CLAIMS.json.

Usage: python3 -B stage_rv19_claims_pointers.py <framework-root> <scratch-dir>

CLAIMS.json is canon and its sha256 is pinned by 28_DEFENSE/review_2026_10_20/claim-assessments.json,
so it is not edited in place. Only `evidence_path` changes. Every repoint is checked first: a dead
reference must be dead, a silent one must lack the claim's token, and the new target must carry the
claim at the named line or contain its token. Statements and author statuses are untouched.
"""
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
WORK = Path(sys.argv[2]).resolve() / "rv19_patch"
REVIEW = ROOT / "FOR-REVIEW" / "2026-10-22_OPUS_REVIEW"
OUT = REVIEW / "RV19_claims_pointer_repairs.patch"
RECORD = REVIEW / "RV19_claims_pointer_repairs.json"
REL = "28_DEFENSE/CLAIMS.json"
FS = "30_MAPS/FORMAL_SPINE.md"
IMPL, INV = "01_CASCADE_L4/implementations/", "29_GOVERNANCE/EMPIRICAL_INVENTORY.md"
EMP, SYN = "TRUTH_PRESSURE/EMPIRICAL_RESULTS.md", "papers/LYCHEETAH_SYNTHESIS_v0.1.md"
SIM = "11_MATHEMATICAL_FOUNDATIONS/cascade_simulation"

# Dead references replaced by where the claim is actually stated (None drops a duplicate).
STATED = {
    "CAS-003": (FS, 207, "Theorem C1"), "CAS-004": (FS, 213, "Theorem C2"),
    "CAS-005": (FS, 218, "Theorem C3"), "CAS-006": (FS, 222, "Theorem C4"),
    "CAS-008": (FS, 227, "Conjecture C5"),
    "LAM-003": (FS, 312, "Theorem L1"), "LAM-004": (FS, 317, "Theorem L2"),
    "TRI-003": (FS, 152, "Theorem T1"), "TRI-004": (FS, 156, "Theorem T2"),
    "TRI-005": (FS, 161, "Theorem T3"), "TRI-007": (FS, 153, "α + β ≤ 1"),
    "CRY-002": (FS, 519, "non-commutative"), "CRY-003": (FS, 514, "Theorem X1"),
    "CRY-004": (FS, 522, "Theorem X3"),
    "AUR-009": ("30_MAPS/CODEX_DISTILLATION.md", 536, "simultaneously satisfiable"),
    "MIC-003": (None, 366, "Theorem M2"), "TRI-006": (None, None, "Banach"),
}
# References that are dead, or resolve without stating the claim: (old, token) -> (new, token new carries).
SILENT = {
    "HAR-004": [(("CLAUDE.md", "EWM"), ("AGENTS.md", "Emotional Wavelength Matching"))],
    "XFW-005": [(("CLAUDE.md", "Two-Point"), ("THE_SOL_PROTOCOL.md", "Two-Point Protocol"))],
    "XFW-006": [(("CLAUDE.md", "PGF"), ("THE_SOL_PROTOCOL.md", "Prime Generative Field"))],
    "CAS-009": [((IMPL, "40.3"), (EMP, "40.3")), ((INV, "40.3"), (SYN, "0.58"))],
    "CAS-010": [((IMPL, "0.47"), (SIM + ".py", "paradigm")),
                ((INV, "0.47"), (SIM + "_results.json", "cascade_vs_additive"))],
    "CAS-011": [((IMPL, "95.2"), (EMP, "0.048")), ((INV, "95.2"), (SYN, "95.2"))],
}
APPEND = {"LYV-001": (SYN, "11/11")}
SILENT_TOO = {"LYV-001": [("11_MATHEMATICAL_FOUNDATIONS/MATHEMATICS_FOUNDATIONS.md", "11/11"), (INV, "11/11")],
              "CAS-008": [("11_MATHEMATICAL_FOUNDATIONS/MATHEMATICS_FOUNDATIONS.md", "Conjecture C5")]}


def refs(claim):
    return [s.strip() for s in claim["evidence_path"].split(";") if s.strip()]


def missing(register):
    return sorted((c["claim_id"], r) for c in register["claims"] for r in refs(c) if not (ROOT / r).exists())


def contains(rel, token):
    path = ROOT / rel
    files = [p for p in path.rglob("*") if p.is_file()] if path.is_dir() else [path]
    return any(token in p.read_text(encoding="utf-8", errors="ignore") for p in files)


def line_has(rel, n, token):
    return token in (ROOT / rel).read_text(encoding="utf-8").splitlines()[n - 1]


head = subprocess.run(["git", "show", f"HEAD:{REL}"], cwd=ROOT, capture_output=True, check=True).stdout
assert (ROOT / REL).read_bytes() == head, "working-tree register differs from HEAD"
register = json.loads(head)
by_id = {c["claim_id"]: c for c in register["claims"]}
before_missing = missing(register)
assert sum(len(refs(c)) for c in register["claims"]) == 107 and len(before_missing) == 23

new_paths, record = {}, []
for cid, (target, line, token) in STATED.items():
    old = refs(by_id[cid])
    dead = [r for r in old if not (ROOT / r).exists()]
    assert dead, cid
    if target is None:
        assert contains(FS, token) and FS in old, cid
        if line:
            assert line_has(FS, line, token), cid
        new = [r for r in old if r not in dead]
    else:
        assert line_has(target, line, token), (cid, target, line)
        new = []
        for r in old:
            r = target if r in dead else r
            if r not in new:
                new.append(r)
    for rel, tok in SILENT_TOO.get(cid, []):
        assert not contains(rel, tok), (cid, rel)
    new_paths[cid] = new
    record.append({"claim_id": cid, "reason": "missing reference", "dead": dead,
                   "stated_at": f"{target or FS}:{line}" if line else f"{FS} ('{token}')"})
for cid, swaps in SILENT.items():
    new = refs(by_id[cid])
    for (old_rel, old_tok), (new_rel, new_tok) in swaps:
        assert not (ROOT / old_rel).exists() or not contains(old_rel, old_tok), (cid, old_rel)
        assert contains(new_rel, new_tok), (cid, new_rel)
        new = [new_rel if r == old_rel else r for r in new]
    new_paths[cid] = list(dict.fromkeys(new))
    olds = [o for (o, _), _ in swaps]
    entry = {"claim_id": cid, "reason": "references dead or silent"}
    entry["dead"] = [o for o in olds if not (ROOT / o).exists()]
    entry["silent"] = [o for o in olds if (ROOT / o).exists()]
    record.append({k: v for k, v in entry.items() if v})
for cid, (rel, tok) in APPEND.items():
    for old_rel, old_tok in SILENT_TOO[cid]:
        assert not contains(old_rel, old_tok), (cid, old_rel)
    assert contains(rel, tok)
    new_paths[cid] = refs(by_id[cid]) + [rel]
    record.append({"claim_id": cid, "reason": "no existing reference states the figure; the statement is added",
                   "silent": [r for r, _ in SILENT_TOO[cid]]})

text = head.decode("utf-8")
lines = text.split("\n")
for cid, new in new_paths.items():
    old_field = '"evidence_path":' + json.dumps(by_id[cid]["evidence_path"], ensure_ascii=False)
    new_field = '"evidence_path":' + json.dumps("; ".join(new), ensure_ascii=False)
    hit = [i for i, l in enumerate(lines) if f'"claim_id":"{cid}"' in l]
    assert len(hit) == 1 and lines[hit[0]].count(old_field) == 1, cid
    lines[hit[0]] = lines[hit[0]].replace(old_field, new_field)
after = "\n".join(lines)
patched = json.loads(after)
for a, b in zip(register["claims"], patched["claims"]):
    assert {k: v for k, v in a.items() if k != "evidence_path"} == {k: v for k, v in b.items() if k != "evidence_path"}
    if a["claim_id"] in new_paths:
        assert a["evidence_path"] != b["evidence_path"]
        assert all((ROOT / r).exists() for r in refs(b)), a["claim_id"]
    else:
        assert a["evidence_path"] == b["evidence_path"]
after_missing = missing(patched)
assert set(after_missing) <= set(before_missing)
assert {cid for cid, _ in after_missing} == {"ANA-002", "ANA-003", "ANA-004"}

for entry in record:
    entry["before"] = by_id[entry["claim_id"]]["evidence_path"]
    entry["after"] = "; ".join(new_paths[entry["claim_id"]])
record.sort(key=lambda e: e["claim_id"])

if WORK.exists():
    shutil.rmtree(WORK)
for side, body in (("a", head), ("b", after.encode("utf-8"))):
    (WORK / side / REL).parent.mkdir(parents=True, exist_ok=True)
    (WORK / side / REL).write_bytes(body)
diff = subprocess.run(["diff", "-ruN", "a", "b"], cwd=WORK, capture_output=True).stdout
assert diff and b"\r" not in diff
OUT.write_bytes(diff)
check = WORK / "check"
shutil.copytree(WORK / "a", check)
subprocess.run(["patch", "-p1", "--quiet", "-i", str(OUT)], cwd=check, check=True)
assert (check / REL).read_bytes() == after.encode("utf-8")

RECORD.write_text(json.dumps({
    "date": "2026-10-22", "review": "RV19",
    "register": REL,
    "register_sha256_before": hashlib.sha256(head).hexdigest(),
    "register_sha256_after": hashlib.sha256(after.encode("utf-8")).hexdigest(),
    "pinned_by": "28_DEFENSE/review_2026_10_20/claim-assessments.json (register_sha256): applying this patch stales that pin",
    "statements_and_author_statuses_unchanged": True,
    "claims_updated": len(record),
    "references_before": 107, "missing_before": len(before_missing),
    "references_after": sum(len(refs(c)) for c in patched["claims"]), "missing_after": len(after_missing),
    "remaining_missing": [{"claim_id": c, "reference": r} for c, r in after_missing],
    "caution": "A pointer to where a claim is stated is not evidence for it. CAS-009 and CAS-011 now point at "
               "documents whose materials are absent (BATCH18 F-EMP); CAS-010 points at a run that ties the "
               "additive baseline (F-PARADIGM).",
    "repairs": record,
}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"patch {OUT.name}: {len(diff)} bytes, {len(record)} claims, missing {len(before_missing)} -> "
      f"{len(after_missing)}, applies to HEAD and matches: True, CR bytes: 0")
print("BEFORE_MISSING", json.dumps(before_missing))
