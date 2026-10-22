#!/usr/bin/env python3
"""Batch 21 (RV22, agent-safety continuations) reproduction.

    python3 -B repro_batch21.py <repo-root> <scratch-dir> [--suites]

Static checks run against the working tree and a `git archive HEAD` copy in scratch.
`--suites` also reruns every continuation's own verifier from that HEAD copy, one at a
time; a timeout is reported as DID NOT RUN, never as FAILED or PASS. Earned Trust runs
from a short directory because its Cycle 009 tests bind AF_UNIX sockets and a long
scratch path exceeds the socket path limit.

Nothing here writes to the repository.
"""
from __future__ import annotations

import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
SCRATCH = Path(sys.argv[2]).resolve()
SUITES = "--suites" in sys.argv
SAFETY = Path("papers/agent-safety")
ET_REL = SAFETY / "earned-trust/cycles_001_009"
SHORT = Path("/tmp/claude-1000/rv22s")
PATCH = ROOT / "FOR-REVIEW/2026-10-22_OPUS_REVIEW/RV22_earned_trust_skip_count.patch"
ENV = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "MPLBACKEND": "Agg"}

results: list[tuple[str, str, str]] = []


def record(check: str, status: str, detail: str) -> None:
    results.append((check, status, detail))
    print(f"[{status}] {check}: {detail}", flush=True)


def expect(check: str, ok: bool, detail: str) -> None:
    record(check, "PASS" if ok else "FAIL", detail)


def run(cmd: list[str], cwd: Path, timeout: int, env: dict | None = None) -> tuple[int | None, str]:
    try:
        proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout, env=env or ENV)
    except subprocess.TimeoutExpired:
        return None, ""
    return proc.returncode, proc.stdout + proc.stderr


def sha(path: Path) -> str:
    import hashlib
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text_manifest(path: Path) -> dict[str, str]:
    out = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            digest, rel = line.split(maxsplit=1)
            out[rel.lstrip("*")] = digest
    return out


def tally(base: Path, digests: dict[str, str]) -> tuple[int, int, int]:
    ok = bad = missing = 0
    for rel, digest in digests.items():
        target = base / rel.removeprefix("./")
        if not target.is_file():
            missing += 1
        elif sha(target) == digest:
            ok += 1
        else:
            bad += 1
    return ok, bad, missing


# --- HEAD copy -------------------------------------------------------------------
HEAD = SCRATCH / "rv22_repro_head"
if HEAD.exists():
    shutil.rmtree(HEAD)
HEAD.mkdir(parents=True)
archive = subprocess.run(["git", "-C", str(ROOT), "archive", "HEAD"], check=True, capture_output=True).stdout
subprocess.run(["tar", "-x", "-C", str(HEAD)], input=archive, check=True)

spec = importlib.util.spec_from_file_location("rv22_cont", ROOT / "tests/test_agent_safety_continuations.py")
cont = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cont)
FUNCS = {
    "maintained": cont.maintained_manifest_problems,
    "intake": cont.earned_light_intake_problems,
    "sovereign": cont.sovereign_forge_problems,
    "runtime": cont.runtime_imports_of_continuations,
}

# --- C1 the new test's functions are clean on the tree --------------------------
for name, fn in FUNCS.items():
    found = fn(ROOT)
    expect(f"C1 tree {name}", found == [], f"{len(found)} problems {found[:2]}")

# --- C2 each function sees a planted defect; the control is clean -----------------
for name, fn in FUNCS.items():
    found = fn(HEAD)
    expect(f"C2 control {name}", found == [], f"HEAD copy {len(found)} problems")


def mutate(check: str, target: Path, fn, change) -> None:
    original = target.read_bytes()
    try:
        change(target, original)
        found = fn(HEAD)
    finally:
        target.write_bytes(original)
    expect(check, bool(found), f"{len(found)} problems, first: {found[:1]}")


frontier = HEAD / SAFETY / "frontier-controls"
first_frontier = next(iter(json.loads((frontier / "INTEGRATION_MANIFEST.json").read_text())["files"]))
mutate("C2 mutate frontier byte", frontier / first_frontier, FUNCS["maintained"],
       lambda p, b: p.write_bytes(bytes([b[0] ^ 1]) + b[1:]))
forge04 = HEAD / SAFETY / "earned-light/forges_01_07/Forge_04"
first_el = next(iter(text_manifest(forge04 / "SHA256SUMS.txt")))
mutate("C2 mutate earned-light Forge_04 file", forge04 / first_el, FUNCS["maintained"],
       lambda p, b: p.write_bytes(b + b"\n"))
intake = set(text_manifest(HEAD / SAFETY / "earned-light/intake/SHA256SUMS.txt").values())
story = next(p for p in sorted((HEAD / cont.STORY_HOME).rglob("*")) if p.is_file() and sha(p) in intake)
mutate(f"C2 delete Mythos story {story.name}", story, FUNCS["intake"], lambda p, b: p.unlink())
forge_v = HEAD / SAFETY / "sovereign-choice-research/forges/forge_v"
v_manifest = next(m for m in forge_v.glob("*.json") if "MANIFEST" in m.name)
v_first = next(r for r in cont._forge_digests(json.loads(v_manifest.read_text())) if not r.startswith("lineage/"))
mutate(f"C2 corrupt forge_v {v_first}", forge_v / v_first, FUNCS["sovereign"], lambda p, b: p.write_bytes(b + b" "))
mutate("C2 runtime marker hybrid_gateway", HEAD / "lycheetah/__init__.py", FUNCS["runtime"],
       lambda p, b: p.write_bytes(b + b"\n# hybrid_gateway\n"))
try:
    cont._forge_digests({"files": {"x": "not-a-digest"}})
    expect("C2 unknown forge shape refused", False, "accepted")
except ValueError as exc:
    expect("C2 unknown forge shape refused", True, str(exc))
for name, fn in FUNCS.items():
    expect(f"C2 restored {name}", fn(HEAD) == [], "HEAD copy clean after mutations")

# --- C3 historical manifests do not verify the current tree, by known counts -------
hybrid = ROOT / "papers/ai-futures/hybrid-gateway/v1.2"
hist = {m.name: tally(hybrid, text_manifest(m)) for m in sorted(hybrid.glob("SHA256SUMS_v0.*"))}
pairs = sorted((ok, bad + missing) for ok, bad, missing in hist.values())
expect("C3 hybrid SHA256SUMS_v0.* (ok, non-matching)",
       pairs == sorted([(12, 4), (22, 5), (32, 7), (47, 6), (67, 5), (77, 4), (93, 4), (102, 4)]),
       f"{ {k: (v[0], v[1] + v[2]) for k, v in hist.items()} }")
current = tally(hybrid, text_manifest(hybrid / "SHA256SUMS.txt"))
expect("C3 hybrid current SHA256SUMS.txt", current[1:] == (0, 0), f"ok {current[0]}, bad {current[1]}, missing {current[2]}")
src_expected = {"01": (3, 1), "02": (2, 2), "03": (4, 1), "04": (2, 0), "05": (2, 0), "06": (1, 0), "07": (2, 0), "08": (0, 2)}
src = {}
for sums in sorted((ROOT / SAFETY / "frontier-controls").glob("0*/SOURCE_SHA256SUMS.json")):
    _, bad, missing = tally(sums.parent, json.loads(sums.read_text()))
    src[sums.parent.name[:2]] = (bad, missing)
expect("C3 frontier SOURCE_SHA256SUMS (bad, missing)", src == src_expected, f"{src}")
sim = json.loads((ROOT / SAFETY / "simulator/reports/artifact-manifest.json").read_text())
sim_t = tally(ROOT / SAFETY, {f["path"]: f["sha256"] for f in sim["files"]})
expect("C3 simulator v0.3 artifact-manifest (ok, non-matching)", (sim_t[0], sim_t[1] + sim_t[2]) == (16, 12), f"{sim_t}")
comp = ROOT / SAFETY / "compensation-race-benchmark"
comp_src = text_manifest(comp / "SOURCE_MANIFEST.sha256")
comp_bad = sorted(r for r, d in comp_src.items() if not (comp / r).is_file() or sha(comp / r) != d)
expect("C3 compensation SOURCE_MANIFEST", comp_bad == ["README.md"], f"{len(comp_src)} entries, non-matching {comp_bad}")

# --- C5 the Sovereign Will count composition ---------------------------------------
sov = ROOT / SAFETY / "sovereign-choice-research"
vii = json.loads((sov / "forges/forge_vii/results/verification.json").read_text())
expect("C5 forge_vii lineage 23 + 87 = 110",
       (vii["forge_vii_tests"], vii["prior_lineage_tests"], vii["combined_tests"]) == (23, 87, 110),
       f"{vii['forge_vii_tests']} + {vii['prior_lineage_tests']} = {vii['combined_tests']}")
gate_hits = []
for runner in sorted(list(sov.rglob("run_verification.py")) + list((ROOT / "35_ABSTRACT_AND_GENERATIVE/SOVEREIGN_WILL").rglob("run_verification.py"))):
    for n, line in enumerate(runner.read_text(encoding="utf-8").splitlines(), 1):
        if re.search(r"""get\(['"]tests['"]\)\s*==\s*110""", line):
            gate_hits.append(f"{runner.relative_to(ROOT)}:{n}")
expect("C5 Forge VIII runner requires exactly 110 historical tests", bool(gate_hits), f"{gate_hits}")
validation = (ROOT / "35_ABSTRACT_AND_GENERATIVE/SOVEREIGN_WILL/VALIDATION_AND_LIMITATIONS.md").read_text(encoding="utf-8")
expect("C5 correction note present, original bullet kept",
       "Review correction (2026-10-22, RV22)" in validation and "through Forges II–VII" in validation,
       "note + preserved handoff bullet")

# --- C6 the staged patch applies to HEAD and changes the summary line ---------------
stage = SCRATCH / "rv22_patch_apply"
if stage.exists():
    shutil.rmtree(stage)
shutil.copytree(HEAD / ET_REL, stage)
rc, out = run(["patch", "-p5", "--quiet", "-i", str(PATCH)], stage, 30)
patched = (stage / "verify_release.py").read_text(encoding="utf-8")
expect("C6 patch applies to HEAD runner", rc == 0 and "a skip is not a pass" in patched, out.strip() or "applied")
rc, out = run([sys.executable, "-B", "-m", "py_compile", str(stage / "verify_release.py")], stage, 30)
expect("C6 patched runner compiles", rc == 0, out.strip() or "ok")
shutil.rmtree(stage)

# --- C7 preserved negative and neutral results -------------------------------------
el = ROOT / SAFETY / "earned-light/forges_01_07"
c009 = json.loads((ROOT / ET_REL / "earned_trust_cycle_009/scenario_results.json").read_text())
expect("C7 earned-trust C009 provider baseline agrees 15/15", (c009["cases"], c009["agreements"]) == (15, 15), f"{c009['cases']}/{c009['agreements']}")
eac = json.loads((el / "Forge_02/results/metrics.json").read_text())["metrics"]["eac"]
expect("C7 earned-light Forge_02 EAC still lets 2/33 through, blocks 2/10 benign",
       (eac["unauthorized_effect_ratio"], eac["benign_completion_ratio"]) == ("2/33", "8/10"), f"{eac}")
f5 = (el / "Forge_05/README.md").read_text(encoding="utf-8")
expect("C7 Forge_05 conventional JSON ties", "tie** on every task" in f5, "Central negative result kept")
fx = vii["fixture_results"]
expect("C7 forge_vii standard ties sovereign 18/18",
       fx["standard"]["acceptable"] == fx["sovereign"]["acceptable"] == 18 and vii["baseline_parity"] is True, f"{fx['standard']} vs {fx['sovereign']}")
expect("C7 SOVEREIGN_WILL keeps the tie and fictional fixtures",
       "18/18 policy *tie*" in validation and "fictional graph fixtures" in validation, "VALIDATION_AND_LIMITATIONS.md:20")
viii = None
for p in sorted(sov.rglob("*.json")):
    try:
        text = p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    if '"negative_control_pairs"' in text:
        m = {k: re.search(rf'"{k}":\s*(\d+)', text) for k in ("matched_usage_pairs", "different_surface_verdicts", "negative_control_pairs")}
        if all(m.values()):
            viii = (p.relative_to(ROOT), *(int(v.group(1)) for v in m.values()))
            break
expect("C7 Forge VIII 7 of 8 matched pairs differ, 1 negative control", viii is not None and viii[1:] == (8, 7, 1), f"{viii}")
rc, out = run([sys.executable, "-B", "demo_sql_comparison.py"], HEAD / "papers/ai-futures/hybrid-gateway/v1.2", 120)
counts = json.loads(out[out.index("{"):])["counts"] if rc == 0 else {}
expect("C7 hybrid: SQL ties gateway 4/4, latest-known 2/4",
       counts == {"naive_latest_known": 2, "sql_temporal": 4, "gateway": 4}, f"{counts}")

# --- C8 intake wrapper footing intact after the README note --------------------------
readme = (ROOT / "papers/ai-futures/hybrid-gateway/README.md").read_text(encoding="utf-8")
expect("C8 hybrid README note present", "Review note (2026-10-22, RV22)" in readme and "**[SCAFFOLD]" in readme, "note + [SCAFFOLD] marker")
rc, out = run([sys.executable, "-B", "tools/verify_research_intake.py"], ROOT, 300)
expect("C8 tools/verify_research_intake.py", rc == 0, (out.strip().splitlines() or ["(no output)"])[-1])

# --- C4 suites, one at a time, from the HEAD copy -----------------------------------
def ran_counts(text: str) -> list[int]:
    return [int(n) for n in re.findall(r"Ran (\d+) tests?", text)]


def suite(check: str, cmd: list[str], cwd: Path, timeout: int, ok, env: dict | None = None) -> str:
    rc, out = run(cmd, cwd, timeout, env)
    if rc is None:
        record(check, "DID NOT RUN", f"timeout {timeout}s")
        return ""
    good, detail = ok(rc, out)
    expect(check, good, detail)
    return out


if SUITES:
    py = sys.executable
    H = HEAD / SAFETY

    def el_ok(rc, out):
        # Forges mix unittest and pytest output; the verifier reports its own total.
        data = json.loads(out[out.index("{"):]) if rc == 0 else {}
        return data.get("all_passed") is True and data.get("test_executions") == 207, f"rc {rc}, test_executions {data.get('test_executions')}"
    suite("C4 earned-light verify.py (207)", [py, "-B", "verify.py"], H / "earned-light", 900, el_ok)

    def sov_ok(rc, out):
        return rc == 0 and '"all_passed": true' in out, f"rc {rc}, Ran {ran_counts(out)}"
    suite("C4 sovereign-choice verify.py", [py, "-B", "verify.py"], H / "sovereign-choice-research", 900, sov_ok)

    hy = HEAD / "papers/ai-futures/hybrid-gateway/v1.2"
    suite("C4 hybrid verify_release.py", [py, "-B", "verify_release.py"], hy, 300,
          lambda rc, out: (rc == 0 and "VERIFIED 137 files" in out, out.strip().splitlines()[-1]))
    suite("C4 hybrid tests (264)", [py, "-B", "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests"], hy, 600,
          lambda rc, out: (rc == 0 and re.search(r"\b264 passed", out) is not None, out.strip().splitlines()[-1]))
    suite("C4 simulator tests (63)", [py, "-B", "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests"], H / "simulator", 300,
          lambda rc, out: (rc == 0 and re.search(r"\b63 passed", out) is not None, out.strip().splitlines()[-1]))
    suite("C4 compensation unittest (5)", [py, "-B", "-m", "unittest", "discover", "-s", "tests"], H / "compensation-race-benchmark", 300,
          lambda rc, out: (rc == 0 and ran_counts(out) == [5], f"rc {rc}, Ran {ran_counts(out)}"))
    bench = SCRATCH / "rv22_comp_bench.json"

    def bench_ok(rc, out):
        data = json.loads(bench.read_text()) if rc == 0 and bench.is_file() else {}
        keys = ("weak_precheck_overwrites", "sequential_partial_repairs", "atomic_stale_refusals")
        return all(data.get(k) == 1000 for k in keys), f"{ {k: data.get(k) for k in keys} }"
    suite("C4 compensation benchmark 1000 rounds", [py, "-B", "-m", "compensation_race.benchmark", "--rounds", "1000", "--output", str(bench)],
          H / "compensation-race-benchmark", 600, bench_ok)

    # Earned Trust: HEAD runner and patched runner, from a short path.
    if SHORT.exists():
        shutil.rmtree(f"{SHORT}")
    SHORT.mkdir(parents=True)
    for label, patch in (("HEAD", False), ("patched", True)):
        et = SHORT / label
        shutil.copytree(HEAD / ET_REL, et)
        if patch:
            subprocess.run(["patch", "-p5", "--quiet", "-i", str(PATCH)], cwd=et, check=True)
        root_host = os.geteuid() == 0
        if patch:
            want = "378 passed, 0 skipped (378 run)" if root_host else "369 passed, 9 skipped (378 run)"
        else:
            want = "378 passing tests"
        # Cycle 009 binds AF_UNIX sockets under TMPDIR; a long TMPDIR errors 9 tests (F4).
        suite(f"C4 earned-trust --tests ({label})", [py, "-B", "verify_release.py", "--tests"], et, 900,
              lambda rc, out, want=want: (rc == 0 and want in out, [l for l in out.splitlines() if "Selected" in l or "C009" in l]),
              env={**ENV, "TMPDIR": str(SHORT)})
    shutil.rmtree(f"{SHORT}")

    # Frontier drivers: rc and whether running a driver rewrites its own manifested files.
    for comp_dir in sorted((H / "frontier-controls").glob("0*")):
        driver = comp_dir / ("reproduce_boundary_audit.py" if comp_dir.name.startswith("08") else "benchmark.py")
        if not driver.is_file():
            record(f"C4 frontier {comp_dir.name}", "DID NOT RUN", "no driver")
            continue
        rc, out = run([py, "-B", driver.name], comp_dir, 240)
        if rc is None:
            record(f"C4 frontier {comp_dir.name}", "DID NOT RUN", "timeout 240s")
            continue
        drift = cont._check(comp_dir, json.loads((comp_dir / "SHA256SUMS.json").read_text()), comp_dir.name)
        tail = (out.strip().splitlines() or ["(no output)"])[-1][:160]
        # Drivers 01-05 rewrite reports/report.json with run-dependent race counts (F12);
        # drift is reported, not judged.
        expect(f"C4 frontier {comp_dir.name} {driver.name}", rc == 0, f"rc {rc}; manifest drift after run: {len(drift)} {drift[:2]}; tail: {tail}")
else:
    record("C4 suites", "DID NOT RUN", "pass --suites")

shutil.rmtree(HEAD)
fails = [r for r in results if r[1] == "FAIL"]
skipped = [r for r in results if r[1] == "DID NOT RUN"]
print(f"\nBatch 21: {len(results) - len(fails) - len(skipped)} PASS, {len(fails)} FAIL, {len(skipped)} DID NOT RUN")
raise SystemExit(1 if fails else 0)
