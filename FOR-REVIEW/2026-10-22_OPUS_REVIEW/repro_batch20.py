"""Batch 20 (RV21, Truth Pressure forge, cybernetics, Tianxia operators) witnesses.

Usage: python3 -B repro_batch20.py <framework-root> <scratch-dir>

C1 forge zips equal the expanded tree; forge and per-bundle SHA-256 manifests verify
C2 the new mirror test fails when one expanded byte or one zip byte is flipped (scratch copy)
C3 v0.7 disagreement gate: HEAD passes with zero comparable records; the staged patch's
   new check fails against HEAD source and the patched bundle passes verify:review and verify:bridge
C4 v0.4 analyzer: one packet tripled reports alpha 1.0 at HEAD and is refused when patched;
   constant ratings report 1.0 at HEAD and undefined when patched; independent raters give
   the same alpha in both, equal to an independent Krippendorff computation (control)
C5 v0.8 collector on a fixture: HEAD copies keys pasted into selected files and still prints
   "No .env, keys ... were collected"; patched withholds them; .env and a benign file are controls
C6 Tianxia: the worked examples' R(s) is not the implemented operator; Example 4 arithmetic
C7 cybernetics loop audit, its mutation self-test and the variety demo still run clean
C8 v0.1 engine gates compare 6-dp rounded support: 0.5499996 clears a 0.55 minimum
C9 the dated review notes are present in MASTER_EQUATION.md and WORKED_EXAMPLES_v0.3.md

Read-only on the repository. Every bundle is run from a `git archive HEAD` copy in scratch;
test key strings are assembled at runtime and written only to scratch.
"""
import csv
import hashlib
import importlib.util
import io
import itertools
import json
import os
import random
import re
import shutil
import statistics
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path

OUT = "FOR-REVIEW/2026-10-22_OPUS_REVIEW"
EXP = "TRUTH_PRESSURE/FORGE_2026-08-02_EXPANDED"
FORGE = "TRUTH_PRESSURE/FORGE_2026-08-02"
V07 = f"{EXP}/TRUTH_PRESSURE_SHADOW_EVIDENCE_CONSOLE_v0.7"
V04 = f"{EXP}/TRUTH_PRESSURE_MEASUREMENT_PACK_v0.4"
V08 = f"{EXP}/TRUTH_PRESSURE_LIVE_SOURCE_COLLECTOR_v0.8"
V01 = f"{EXP}/TRUTH_PRESSURE_v0.1_EVIDENCE_WEIGHTED_REVISION"
ENV = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "MPLBACKEND": "Agg"}
RESULTS = []


def record(name, ok, detail):
    ok = bool(ok)
    RESULTS.append((name, ok))
    print(f"{'PASS' if ok else 'FAIL'} {name}: {json.dumps(detail, ensure_ascii=False)}")


def fresh(path):
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)
    return path


def extract_head(root, rel, dest):
    data = subprocess.run(["git", "-C", str(root), "archive", "HEAD", rel],
                          check=True, capture_output=True).stdout
    with tarfile.open(fileobj=io.BytesIO(data)) as archive:
        archive.extractall(dest, filter="data")


def apply_patch(root, base, name):
    subprocess.run(["patch", "-p1", "--quiet", "-i", str(root / OUT / name)], cwd=base, check=True)


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def c1(root):
    mirrors = load_module(root / "tests/test_truth_pressure_forge_mirrors.py", "forge_mirrors")
    bundles = {}
    for manifest in sorted((root / EXP).glob("*/SHA256_MANIFEST.json")):
        files = json.loads(manifest.read_text())["files"]
        bad = [rel for rel, meta in files.items()
               if hashlib.sha256((manifest.parent / rel).read_bytes()).hexdigest() != meta["sha256"]
               or (manifest.parent / rel).stat().st_size != meta["bytes"]]
        bundles[manifest.parent.name] = {"listed": len(files), "bad": bad}
    zips = len(list((root / FORGE).rglob("*.zip")))
    mirror, forge = mirrors.mirror_mismatches(root), mirrors.manifest_mismatches(root)
    ok = zips == 9 and not mirror and not forge and all(not b["bad"] for b in bundles.values())
    record("C1 forge mirrors and manifests", ok,
           {"zips": zips, "mirror_problems": mirror, "forge_manifest_problems": forge, "bundle_manifests": bundles})
    return mirrors


def c2(root, scratch, mirrors):
    base = fresh(scratch / "c2")
    for rel in (FORGE, EXP):
        shutil.copytree(root / rel, base / rel)
    clean = (mirrors.mirror_mismatches(base), mirrors.manifest_mismatches(base))
    target = base / V04 / "README.md"
    target.write_bytes(target.read_bytes() + b"\n")
    after_expanded = mirrors.mirror_mismatches(base)
    target.write_bytes(target.read_bytes()[:-1])
    zip_path = sorted((base / FORGE).rglob("*.zip"))[0]
    raw = bytearray(zip_path.read_bytes())
    raw[-1] ^= 0x01
    zip_path.write_bytes(bytes(raw))
    after_zip = mirrors.manifest_mismatches(base)
    ok = clean == ([], []) and after_expanded and after_zip
    record("C2 mirror test fails under mutation", ok,
           {"clean_copy": clean, "expanded_byte_flipped": after_expanded, "zip_byte_flipped": after_zip})


def c3(root, scratch):
    new_check = "100 records with no comparable trigger do not meet the engineering gate"
    dirs = {name: fresh(scratch / f"c3_{name}") for name in ("head", "head_newtest", "patched")}
    for d in dirs.values():
        extract_head(root, V07, d)
    apply_patch(root, dirs["patched"], "RV21_v07_disagreement_gate.patch")
    shutil.copy(dirs["patched"] / V07 / "scripts/verify-shadow-review.ts",
                dirs["head_newtest"] / V07 / "scripts/verify-shadow-review.ts")

    def run(name, script):
        r = subprocess.run(["node", "--experimental-strip-types", f"scripts/{script}"],
                           cwd=dirs[name] / V07, capture_output=True, text=True, timeout=180)
        return r.returncode, r.stdout + r.stderr

    head_rc, head_out = run("head", "verify-shadow-review.ts")
    mixed_rc, mixed_out = run("head_newtest", "verify-shadow-review.ts")
    patched_rc, patched_out = run("patched", "verify-shadow-review.ts")
    bridge_rc, bridge_out = run("patched", "verify-shadow-bridge.ts")
    count = re.findall(r"(\d+) evidence-console checks passed", patched_out)
    ok = (head_rc == 0 and mixed_rc != 0 and f"✅ {new_check}" not in mixed_out
          and patched_rc == 0 and f"✅ {new_check}" in patched_out and bridge_rc == 0)
    record("C3 v0.7 disagreement gate", ok, {
        "head_verify_review_rc": head_rc,
        "new_check_against_head_source_rc": mixed_rc,
        "new_check_against_head_source_error": [l for l in mixed_out.splitlines() if "Error" in l][:2],
        "patched_verify_review_rc": patched_rc, "patched_checks_passed": count,
        "patched_verify_bridge_rc": bridge_rc,
        "patched_bridge_tail": bridge_out.strip().splitlines()[-1:],
    })


def krippendorff_interval(units):
    """Coincidence-form alpha, written independently of the analyzer."""
    values = [v for unit in units for v in unit]
    n = len(values)
    d_o = sum(sum((a - b) ** 2 for a, b in itertools.permutations(unit, 2)) / (len(unit) - 1)
              for unit in units) / n
    d_e = sum((a - b) ** 2 for a, b in itertools.permutations(values, 2)) / (n * (n - 1))
    return None if d_e == 0 else 1 - d_o / d_e


def c4(root, scratch):
    dirs = {name: fresh(scratch / f"c4_{name}") for name in ("head", "patched")}
    for d in dirs.values():
        extract_head(root, V04, d)
    apply_patch(root, dirs["patched"], "RV21_v04_analyzer_integrity.patch")
    pack = dirs["head"] / V04
    key = json.loads((pack / "admin/BLINDING_KEY.json").read_text())
    case_of = {m["item_code"]: m["case_id"] for items in key["raters"].values() for m in items}
    ratings = fresh(scratch / "c4_ratings")

    def fill(rater, label, scorer):
        src = pack / f"rater_packets/RATER_{rater}_PACKET.csv"
        with src.open(encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))
        for row in rows:
            for c in "EPS":
                row[f"{c}_score_0_4"] = str(scorer(rater, case_of[row["item_code"]], c))
                row[f"{c}_confidence_1_3"] = "2"
            row["brief_reason"], row["ambiguity_flag_yes_no"] = "synthetic", "no"
        dest = ratings / f"{label}_{rater}.csv"
        with dest.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        return dest

    def independent(rater, case, c):
        base = random.Random(f"{case}-{c}").randint(0, 4)
        return min(4, max(0, base + random.Random(f"{rater}-{case}-{c}").choice((-1, 0, 0, 1))))

    control = [fill(r, "control", independent) for r in "ABC"]
    constant = [fill(r, "constant", lambda *_: 2) for r in "ABC"]
    tripled = [control[0]] * 3

    def analyze(name, paths, tag):
        out = scratch / f"c4_{name}_{tag}.json"
        r = subprocess.run([sys.executable, "-B", "-I", "scripts/analyze_annotations.py",
                            "--key", "admin/BLINDING_KEY.json", "--ratings", *map(str, paths),
                            "--output", str(out)], cwd=dirs[name] / V04, capture_output=True, text=True, env=ENV)
        if r.returncode:
            return {"rc": r.returncode, "error": r.stderr.strip().splitlines()[-1]}
        report = json.loads(out.read_text())
        return {"rc": 0, "cases": report["cases"],
                "alpha": {c: v["alpha_interval_squared"] for c, v in report["components"].items()}}

    by_case = {}
    for rater, path in zip("ABC", control):
        with path.open(encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                by_case.setdefault(case_of[row["item_code"]], {})[rater] = row
    reference = {c: krippendorff_interval([[int(rows[r][f"{c}_score_0_4"]) for r in "ABC"]
                                           for rows in by_case.values()]) for c in "EPS"}
    got = {(name, tag): analyze(name, paths, tag)
           for name in ("head", "patched")
           for tag, paths in (("tripled", tripled), ("constant", constant), ("control", control))}
    h, p = (lambda tag: got[("head", tag)]), (lambda tag: got[("patched", tag)])
    ok = (h("tripled")["rc"] == 0 and all(a == 1.0 for a in h("tripled")["alpha"].values())
          and p("tripled")["rc"] != 0 and "supplied twice" in p("tripled")["error"]
          and all(a == 1.0 for a in h("constant")["alpha"].values())
          and all(a is None for a in p("constant")["alpha"].values())
          and all(abs(h("control")["alpha"][c] - reference[c]) < 1e-12
                  and abs(p("control")["alpha"][c] - reference[c]) < 1e-12 for c in "EPS"))
    record("C4 v0.4 analyzer integrity", ok,
           {f"{name}/{tag}": v for (name, tag), v in got.items()} | {"independent_krippendorff": reference})


def c5(root, scratch):
    dirs = {name: fresh(scratch / f"c5_{name}") for name in ("head", "patched")}
    for d in dirs.values():
        extract_head(root, V08, d)
    apply_patch(root, dirs["patched"], "RV21_v08_collector_content_scan.patch")
    fixture = fresh(scratch / "c5_fixture")
    sk, gk = "sk-" + "A" * 40, "AIza" + "B" * 35
    (fixture / "package.json").write_text(json.dumps({"name": "lycheetah-mobile", "version": "0.0.0"}))
    (fixture / "app.config.ts").write_text(f'export default {{ extra: {{ openaiKey: "{sk}" }} }};\n')
    (fixture / "lib").mkdir()
    (fixture / "lib/score.ts").write_text(f'const GEMINI = "{gk}";\nexport const truthPressure = 1;\n')
    (fixture / "lib/view.ts").write_text("export const truthPressure = 0.5;\n")
    (fixture / ".env").write_text(f"OPENAI_KEY={sk}\n")
    extract = fixture / "_truth-pressure-live-source-extract"
    out = {}
    for name, d in dirs.items():
        r = subprocess.run(["node", str(d / V08 / "collect-truth-pressure-live-source.mjs"), str(fixture)],
                           capture_output=True, text=True, timeout=120)
        files = [p for p in extract.rglob("*") if p.is_file()]
        leaked = sorted({p.relative_to(extract).as_posix() for p in files
                         if sk in p.read_text(errors="ignore") or gk in p.read_text(errors="ignore")})
        copied = sorted(p.relative_to(extract / "SOURCE").as_posix() for p in (extract / "SOURCE").rglob("*") if p.is_file()) \
            if (extract / "SOURCE").is_dir() else []
        out[name] = {"rc": r.returncode, "files_holding_a_key": leaked, "copied_sources": copied,
                     "claims_no_keys": "No .env, keys" in r.stdout,
                     "withheld_lines": [l.strip() for l in r.stdout.splitlines() if "Withheld" in l or "[" in l and "KEY" in l]}
    h, p = out["head"], out["patched"]
    ok = (h["rc"] == 0 and h["files_holding_a_key"] and h["claims_no_keys"]
          and ".env" not in h["copied_sources"] and "lib/view.ts" in h["copied_sources"]
          and p["rc"] == 0 and not p["files_holding_a_key"] and not p["claims_no_keys"]
          and "lib/view.ts" in p["copied_sources"] and ".env" not in p["copied_sources"])
    record("C5 v0.8 collector content scan", ok, out)


def c6(root):
    sys.path.insert(0, str(root / "32_TIANXIA/implementations"))
    import ren_zheng as RZ
    doc = (root / "32_TIANXIA/WORKED_EXAMPLES_v0.3.md").read_text(encoding="utf-8")
    # (W, V, force component, the text the document prints)
    cases = {"Ex2": (0.75, 0.80, 0.15, "     = 0.59"), "Ex3": (0.40, 0.15, 0.60, "= 0.10"),
             "Ex4": (0.75, 0.70, 0.20, "R(s) = 0.52")}
    rows = {}
    for ex, (w, v, f, printed) in cases.items():
        state = RZ.GovernanceState(w, v, 1 - f, ex)
        rows[ex] = {"doc_formula": round(0.4 * w + 0.4 * v - 0.2 * f, 4), "doc_printed": printed.split("=")[-1].strip(),
                    "printed_present": printed in doc, "operator": round(RZ.ren_zheng_score(state), 4),
                    "operator_wang_eligible": RZ.wang_dao_eligible(state)}
    h5 = [0.70, 0.65, 0.72, 0.12, 0.52]
    composites = {}
    for title, end in (("## Example 1", "## Example 2"), ("## Example 2", "## Example 3")):
        section = doc[doc.index(title):doc.index(end)]
        table = section[section.index("Five-Fold H₅"):section.index("H₅ composite")]
        values = [float(m) for m in re.findall(r"^\|[^|]+\|\s*([+-]?\d\.\d+)\s*\|", table, re.M)]
        composites[title[3:]] = {"components": values, "mean": round(statistics.mean(values), 3),
                                 "printed": re.search(r"H₅ composite = ([\d.]+)", section).group(1)}
    ok = (RZ.THETA_R_DEFAULT == 0.618 and "θ_r = 0.60" in doc
          and all(r["printed_present"] for r in rows.values())
          and rows["Ex2"]["doc_formula"] == 0.59 and rows["Ex2"]["operator_wang_eligible"]
          and rows["Ex4"]["doc_formula"] == 0.54 and rows["Ex4"]["operator_wang_eligible"]
          and not rows["Ex3"]["operator_wang_eligible"]
          and "→ H₅ = 0.64" in doc and round(statistics.mean(h5), 3) == 0.542)
    record("C6 Tianxia R(s) two definitions and Example 4 arithmetic", ok, {
        "theta_r_operator": RZ.THETA_R_DEFAULT, "examples": rows,
        "ex4_h5_components": h5, "ex4_h5_mean": round(statistics.mean(h5), 3), "ex4_h5_printed": 0.64,
        "ex1_ex2_h5_tables_for_comparison": composites,
    })


def c7(root):
    runs = {}
    for label, args in (("audit", ["34_CYBERNETICS/loop_audit.py"]),
                        ("self_test", ["34_CYBERNETICS/loop_audit.py", "--self-test"]),
                        ("variety", ["34_CYBERNETICS/variety_demo.py"])):
        r = subprocess.run([sys.executable, "-B", *args], cwd=root, capture_output=True, text=True, env=ENV, timeout=300)
        runs[label] = {"rc": r.returncode, "tail": r.stdout.strip().splitlines()[-3:]}
    record("C7 cybernetics loop audit, self-test, variety demo", all(v["rc"] == 0 for v in runs.values()), runs)


def c8(root):
    src = (root / V01 / "truth_pressure/engine.py").read_text(encoding="utf-8")
    sys.path.insert(0, str(root / V01))
    from truth_pressure import engine as E
    raw = 0.5499996
    minimum = E.PressureConfig().minimum_support
    ok = ("support=_round(support)" in src and "vector.support >= config.minimum_support" in src
          and raw < minimum and E._round(raw) >= minimum)
    record("C8 v0.1 gate compares rounded support", ok,
           {"raw_support": raw, "minimum_support": minimum, "rounded": E._round(raw),
            "raw_clears": raw >= minimum, "rounded_clears": E._round(raw) >= minimum})


def c9(root):
    master = (root / "TRUTH_PRESSURE/MASTER_EQUATION.md").read_text(encoding="utf-8")
    examples = (root / "32_TIANXIA/WORKED_EXAMPLES_v0.3.md").read_text(encoding="utf-8")
    found = {"master_s5": "Status note (review 2026-10-22, RV21, §5)" in master,
             "master_s6": "Status note (review 2026-10-22, RV21, §6)" in master,
             "examples_top": "Review status note (2026-10-22, RV21)." in examples,
             "examples_ex4": "Review status note (2026-10-22, RV21, Example 4)." in examples}
    record("C9 dated review notes present", all(found.values()), found)


def main():
    root, scratch = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve() / "batch20"
    scratch.mkdir(parents=True, exist_ok=True)
    mirrors = c1(root)
    c2(root, scratch, mirrors)
    c3(root, scratch)
    c4(root, scratch)
    c5(root, scratch)
    c6(root)
    c7(root)
    c8(root)
    c9(root)
    passed = sum(ok for _, ok in RESULTS)
    print(f"\n{passed}/{len(RESULTS)} PASS")
    return 0 if passed == len(RESULTS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
