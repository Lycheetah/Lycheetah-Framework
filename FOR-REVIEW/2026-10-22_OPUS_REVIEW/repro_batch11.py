#!/usr/bin/env python3
"""Batch 11 (RV12): reproduce the blind-review aggregator defects on a copy.

Usage: python3 -B repro_batch11.py <repo root> [staged folder] [--tests-only]

The frozen Policy Lab v0.2 folder is copied into a temporary directory and
probed there. A staged folder (laid out as evaluation/ and tests/) is overlaid
onto the copy; with --tests-only only its test files are, so the new tests run
against the frozen aggregator. The frozen folder is hashed before and after.
"""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

LAB = Path("23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/"
           "07_POLICY_LAB_v0.2/Anon_Politician_Policy_Lab_v0_2")
DROP = object()
MAPPING = {"A": "ordinary_baseline", "B": "structured_ledger", "C": "anon_politician"}
KEY = {"experiment_id": "E1", "blind_pack_id": "APB-1", "mapping": MAPPING}
# Hash of aggregate_reviews.py recorded by the 20 October review (28_DEFENSE/review_2026_10_20).
RECORDED_SHA = "4213a823ae9bd03d444354430f10f2313db091cb03c6cd517ec97de164fe7922"
SEALED = ("evaluation/aggregate_reviews.py", "evaluation/reviewer.html",
          "evaluation/test_evaluation.py", "tests/test_evaluation.py")


def digest(folder: Path) -> str:
    h = hashlib.sha256()
    for p in sorted(folder.rglob("*")):
        if p.is_file() and "__pycache__" not in p.parts:
            h.update(str(p.relative_to(folder)).encode() + b"\0" + p.read_bytes())
    return h.hexdigest()


def sha16(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()[:16]


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def outcome(fn):
    try:
        return fn()
    except Exception as exc:  # the probe records how each input is refused
        return f"{type(exc).__name__}: {exc}"[:130]


def seal(root: Path) -> dict:
    handoff = root / LAB.parents[1]
    entries = {}
    for line in (handoff / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
        hit = re.match(r"^([0-9a-f]{64})\s+\*?(.+)$", line.strip())
        if hit:
            entries[hit.group(2).removeprefix("./")] = hit.group(1)
    differ, missing = [], []
    for rel, want in entries.items():
        p = handoff / rel
        if not p.is_file():
            missing.append(rel)
        elif hashlib.sha256(p.read_bytes()).hexdigest() != want:
            differ.append(rel)
    lab_rel = str(LAB.relative_to(LAB.parents[1]))
    files = {}
    for rel in SEALED:
        key = f"{lab_rel}/{rel}"
        disk = hashlib.sha256((handoff / key).read_bytes()).hexdigest()
        files[rel] = "not listed" if key not in entries else ("match" if entries[key] == disk else "DIFF")
    agg = hashlib.sha256((root / LAB / "evaluation/aggregate_reviews.py").read_bytes()).hexdigest()
    return {"entries": len(entries), "match": len(entries) - len(differ) - len(missing),
            "differ": differ[:10], "missing": missing[:10], "policy_lab_files": files,
            "aggregator_equals_20_oct_record": agg == RECORDED_SHA}


def unit(lab: Path, start: str, pattern: str) -> dict:
    p = subprocess.run([sys.executable, "-B", "-m", "unittest", "discover", "-s", start, "-p", pattern],
                       cwd=lab, capture_output=True, text=True)
    ran = re.search(r"Ran (\d+) test", p.stderr)
    return {"ran": int(ran.group(1)) if ran else None,
            "verdict": p.stderr.strip().splitlines()[-1] if p.stderr.strip() else "",
            "not_passing": [f"{k} {n}" for k, n in re.findall(r"^(FAIL|ERROR): (\w+)", p.stderr, re.M)]}


def main() -> None:
    root = Path(sys.argv[1]).resolve()
    staged = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else None
    tests_only = "--tests-only" in sys.argv
    frozen = root / LAB
    before = digest(frozen)
    tmp = Path(tempfile.mkdtemp(prefix="rv12_"))
    lab = tmp / "lab"
    shutil.copytree(frozen, lab, ignore=shutil.ignore_patterns("__pycache__"))
    if staged:
        for src in sorted(staged.rglob("*")):
            if src.is_file() and (not tests_only or src.name.startswith("test_")):
                shutil.copyfile(src, lab / src.relative_to(staged))
    m = load(lab / "evaluation/aggregate_reviews.py", "aggregate_reviews")
    prep = load(lab / "evaluation/prepare_blind_pack.py", "prepare_blind_pack")
    dims = m.DIMENSIONS
    d0 = dims[0]
    raw = {"experiment_id": "E9", "case_id": "C9", "policy_question": "Q", "source_packet_sha256": "abc",
           "source_cutoff": "2026-10-16", "reference_context": {"known_facts": ["fact"]},
           "methods": [{"method_id": k, "label": k, "analysis_text": f"Analysis for {k}."}
                       for k in ("ordinary_baseline", "structured_ledger", "anon_politician")]}

    def review(rid="r1", scores=None, aliases="ABC", **fields):
        scores = scores or {}
        r = {"schema_version": "anon-politician-review-v0.2", "experiment_id": "E1", "blind_pack_id": "APB-1",
             "case_id": "C1", "source_packet_sha256": "s1", "reviewer_id": rid,
             "reviewed_at": "2026-10-22T00:00:00Z", "candidates": []}
        for a in aliases:
            s = scores.get(a, "2")
            r["candidates"].append({"candidate_id": a, "critical_flags": [],
                                    "ratings": {d: {"score": s, "note": "n"} for d in dims}})
        r.update(fields)
        return {k: v for k, v in r.items() if v is not DROP}

    def from_pack(pack, rid, **fields):
        return review(rid, experiment_id=pack["experiment_id"], blind_pack_id=pack["blind_pack_id"],
                      case_id=pack["case_id"], source_packet_sha256=pack["source_packet_sha256"], **fields)

    def summary(out, method="ordinary_baseline"):
        p = out["methods_or_aliases"][method]
        d = p["dimensions"][d0]
        return {"reviewer_count": p["reviewer_count"], "n_ratings": d["n_ratings"],
                "ratings": d["ratings"], "median": d["median"]}

    def agg(reviews, key=None, method="ordinary_baseline"):
        return summary(m.aggregate(reviews, key), method)

    def header(out):
        return {"experiment_id": out["experiment_id"], "blind_pack_id": out["blind_pack_id"],
                "case_id": out["case_id"], "review_count": out["review_count"],
                "profiles": sorted(map(str, out["methods_or_aliases"]))}

    R: dict = {}
    # Identity and deduplication
    R["R1_same_file_twice"] = outcome(lambda: agg(
        [review("r1", {"A": "2"}), review("r2", {"A": "0"}), review("r1", {"A": "2"})], KEY))
    R["R1b_revised_reexport"] = outcome(lambda: agg(
        [review("r1", {"A": "0"}, reviewed_at="t1"), review("r1", {"A": "2"}, reviewed_at="t2")], KEY))

    def dup_inside():
        r = review("r1")
        r["candidates"].append(copy.deepcopy(r["candidates"][0]))
        return agg([r], KEY)
    R["R1c_candidate_twice_in_one_review"] = outcome(dup_inside)
    R["R2_two_reviews_no_reviewer_id"] = outcome(lambda: agg(
        [review(DROP, {"A": "2"}), review(DROP, {"A": "0"})], KEY))
    R["R2b_two_reviews_unspecified"] = outcome(lambda: agg(
        [review("unspecified", {"A": "2"}), review("unspecified", {"A": "0"})], KEY))
    R["R2c_one_review_unspecified"] = outcome(lambda: agg([review("unspecified")], KEY))
    # Case and experiment identity
    R["R3_two_cases"] = outcome(lambda: header(m.aggregate([review("r1"), review("r2", case_id="C2")])))
    R["R3b_no_case_id"] = outcome(lambda: header(m.aggregate([review("r1", case_id=DROP)])))
    R["R3c_no_experiment_id"] = outcome(lambda: header(m.aggregate([review("r1", experiment_id=DROP)])))

    # Candidate identity
    def lower_alias():
        low = review("r2")
        low["candidates"][0]["candidate_id"] = "a"
        return header(m.aggregate([review("r1"), low], KEY))
    R["R4_lowercase_alias_with_key"] = outcome(lower_alias)
    R["R4b_alias_D_no_key"] = outcome(lambda: header(m.aggregate([review("r1", aliases="ABD")])))

    def no_alias():
        r = review("r1")
        r["candidates"][0].pop("candidate_id")
        return header(m.aggregate([r], KEY))
    R["R4c_candidate_without_id"] = outcome(no_alias)

    # Provenance: binding the private key to the reviewed pack
    other = {"experiment_id": "E1", "blind_pack_id": "APB-2",
             "mapping": {"A": "anon_politician", "B": "ordinary_baseline", "C": "structured_ledger"}}

    def foreign_key():
        out = m.aggregate([review("r1", {"A": "0"}, blind_pack_id=DROP)], other)
        landed = [k for k, p in out["methods_or_aliases"].items() if p["dimensions"][d0]["ratings"] == [0]]
        return {"blind_pack_id": out["blind_pack_id"], "alias_A_zero_landed_under": landed}
    R["R5_reviews_name_no_pack_foreign_key"] = outcome(foreign_key)
    R["R5b_one_review_names_no_pack"] = outcome(lambda: header(
        m.aggregate([review("r1"), review("r2", blind_pack_id=DROP)], KEY)))
    R["R5c_key_names_no_pack"] = outcome(lambda: header(m.aggregate([review("r1")], {"mapping": MAPPING})))
    R["R5d_key_other_experiment"] = outcome(lambda: header(m.aggregate([review("r1")], dict(KEY, experiment_id="E2"))))
    R["R5e_two_source_packets"] = outcome(lambda: header(
        m.aggregate([review("r1"), review("r2", source_packet_sha256="s2")], KEY)))

    # Denominators
    def denominators():
        na = review("r1")
        na["candidates"][0]["ratings"][d0]["score"] = "N/A"
        gap = review("r2")
        del gap["candidates"][0]["ratings"][d0]
        out = m.aggregate([na, gap, review("r3")], KEY)
        p = out["methods_or_aliases"]["ordinary_baseline"]
        d = p["dimensions"][d0]
        return {"reviewer_count": p["reviewer_count"],
                **{k: d.get(k, "absent") for k in ("n_ratings", "n_not_assessable", "n_missing")}}
    R["R6_explicit_NA_vs_missing"] = outcome(denominators)

    # The command line over a real folder: a renamed blind pack, then a re-run
    def stray_files():
        pack, key = prep.prepare(raw, seed=3)
        rdir, kdir = tmp / "reviews", tmp / "key"
        rdir.mkdir()
        kdir.mkdir()
        kpath = kdir / "PRIVATE_method_mapping_key.json"
        kpath.write_text(json.dumps(key), encoding="utf-8")
        (rdir / "review_r1.json").write_text(json.dumps(from_pack(pack, "r1")), encoding="utf-8")
        (rdir / "case1_pack.json").write_text(json.dumps(pack), encoding="utf-8")
        out = rdir / "review_aggregate.json"
        runs = []
        for _ in range(2):
            p = subprocess.run([sys.executable, "-B", str(lab / "evaluation/aggregate_reviews.py"), str(rdir),
                                "--key", str(kpath), "--out", str(out)], capture_output=True, text=True)
            if p.returncode == 0:
                res = json.loads(out.read_text(encoding="utf-8"))
                runs.append({"rc": 0, "review_count": res["review_count"],
                             "reviewer_count": {k: v["reviewer_count"] for k, v in res["methods_or_aliases"].items()}})
            else:
                runs.append({"rc": p.returncode, "stderr": (p.stderr.strip().splitlines() or [""])[0][:120]})
        return runs
    R["R7_renamed_pack_then_rerun"] = outcome(stray_files)
    R["R8_two_reviewers_1_and_2"] = outcome(lambda: agg([review("r1", {"A": "1"}), review("r2", {"A": "2"})], KEY))

    # Controls: a clean study must aggregate identically, and one reviewer may split across files
    def clean_study():
        pack, key = prep.prepare(raw, seed=5)
        reviews = []
        for i, rid in enumerate(("r1", "r2", "r3")):
            r = from_pack(pack, rid)
            for c in r["candidates"]:
                for j, d in enumerate(dims):
                    c["ratings"][d]["score"] = "N/A" if (i + j) % 7 == 0 else str((i + j + ord(c["candidate_id"])) % 3)
            if i == 1:
                r["candidates"][2]["critical_flags"] = [{"code": "material_factual_error",
                                                         "label": "Material factual error"}]
            reviews.append(r)
        out = m.aggregate(reviews, key)
        shared = {meth: {"reviewer_count": p["reviewer_count"], "critical_flags": p["critical_flags"],
                         "dims": {d: {k: v[k] for k in ("n_ratings", "median", "range", "ratings")}
                                  for d, v in p["dimensions"].items()}}
                  for meth, p in out["methods_or_aliases"].items()}
        return {"fingerprint": sha16(shared), "review_count": out["review_count"], "profiles": sorted(shared)}
    R["C1_clean_three_reviewer_study"] = outcome(clean_study)

    def split_reviewer():
        out = m.aggregate([review("r1", aliases="A"), review("r1", aliases="BC")], KEY)
        return {k: p["reviewer_count"] for k, p in out["methods_or_aliases"].items()}
    R["C2_one_reviewer_split_over_two_files"] = outcome(split_reviewer)
    R["U1_tests_folder"] = unit(lab, "tests", "test_*.py")
    R["U2_evaluation_folder"] = unit(lab, "evaluation", "test_evaluation.py")
    R["SEAL"] = seal(root)
    shutil.rmtree(tmp)
    R["FROZEN_BYTES_UNCHANGED"] = digest(frozen) == before
    mode = "frozen" if not staged else ("frozen code + staged tests" if tests_only else "staged")
    print(f"mode: {mode}")
    for k, v in R.items():
        print(f"{k}: {json.dumps(v)}")


if __name__ == "__main__":
    main()
