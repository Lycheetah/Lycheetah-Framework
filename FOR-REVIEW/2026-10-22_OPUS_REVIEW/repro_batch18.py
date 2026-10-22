"""Batch 18 (RV19, claims register) witnesses.

Usage: python3 -B repro_batch18.py <framework-root> <scratch-dir>

B1 pointer census and the staged patch · B2 silent CLAUDE.md pointers · B3 absent materials
B4 arithmetic of the three +40.3% accounts · B5 stored paradigm run ties additive
B6 HEAD rerun reproduces +110.05% [CONFIRMED] · B7 repaired rerun says [NO GAIN OVER ADDITIVE]
B8 the new test fails on HEAD, passes repaired, and its fact pin fails under mutation.
Read-only on the repository; every run happens in scratch copies.
"""
import io
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
WORK = Path(sys.argv[2]).resolve() / "rv19_repro"
REVIEW = ROOT / "FOR-REVIEW" / "2026-10-22_OPUS_REVIEW"
REG = "28_DEFENSE/CLAIMS.json"
SIM = "11_MATHEMATICAL_FOUNDATIONS/cascade_simulation.py"
STORED = "11_MATHEMATICAL_FOUNDATIONS/cascade_simulation_results.json"
TEST = "tests/test_claims_evidence_pointers.py"
ENV = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "MPLBACKEND": "Agg"}
failures = []


def check(tag, ok, detail):
    print(f"[{'PASS' if ok else 'FAIL'}] {tag}: {detail}", flush=True)
    if not ok:
        failures.append(tag)


def git(*args, binary=False):
    out = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, check=True).stdout
    return out if binary else out.decode("utf-8")


def head_tree(dest, paths):
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    data = git("archive", "HEAD", *paths, binary=True)
    with tarfile.open(fileobj=io.BytesIO(data)) as tar:
        tar.extractall(dest, filter="data")


def refs(claim):
    return [s.strip() for s in claim["evidence_path"].split(";") if s.strip()]


def missing(register, base=ROOT):
    return {(c["claim_id"], r) for c in register["claims"] for r in refs(c) if not (base / r).exists()}


# B1 ─ pointer census, staged patch, planted control
head_reg = json.loads(git("show", f"HEAD:{REG}"))
before = missing(head_reg)
check("B1 census", sum(len(refs(c)) for c in head_reg["claims"]) == 107 and len(before) == 23,
      f"107 references, {len(before)} missing in {len({c for c, _ in before})} claims")
pdir = WORK / "b1"
head_tree(pdir, [REG])
subprocess.run(["patch", "-p1", "--quiet", "-i", str(REVIEW / "RV19_claims_pointer_repairs.patch")], cwd=pdir, check=True)
patched = json.loads((pdir / REG).read_text(encoding="utf-8"))
after = missing(patched)
same_rest = all({k: v for k, v in a.items() if k != "evidence_path"} == {k: v for k, v in b.items() if k != "evidence_path"}
                for a, b in zip(head_reg["claims"], patched["claims"]))
check("B1 patch", after <= before and {c for c, _ in after} == {"ANA-002", "ANA-003", "ANA-004"} and same_rest,
      f"missing {len(before)} -> {len(after)}, statements and statuses unchanged: {same_rest}")
planted = json.loads(json.dumps(head_reg))
planted["claims"][0]["evidence_path"] += "; 01_CASCADE_L4/NO_SUCH_FILE.md"
check("B1 control", len(missing(planted)) == 24, "a planted dead reference is counted")

# B2 ─ CLAUDE.md pointers: silent now, present before the reforge
now = git("show", "HEAD:CLAUDE.md")
then = git("show", "6cfccf2:CLAUDE.md")
for token, cid in (("EWM", "HAR-004"), ("Two-Point", "XFW-005"), ("PGF", "XFW-006")):
    check(f"B2 {cid}", token not in now and token in then,
          f"'{token}' absent from HEAD:CLAUDE.md, present in 6cfccf2:CLAUDE.md (control)")

# B3 ─ the EMPIRICAL_RESULTS materials and the manifest code path
history = set(git("log", "--all", "--name-only", "--format=").split())
tree = set(git("ls-files").split())
absent = ["50_belief_corpus.json", "annotator_labels.csv", "trial_results_200.csv", "analysis.py",
          "trial_config.json", "cascade_synthetic_experiment.py"]
found = [n for n in absent if any(p.split("/")[-1] == n for p in history | tree)]
check("B3 materials", not found, f"{len(absent)} named artifacts in neither the tree nor any commit: {found or 'none found'}")
check("B3 control", any(p.endswith("cascade_simulation_results.json") for p in history),
      "the same search finds an artifact that exists")
engine = git("show", "HEAD:12_IMPLEMENTATIONS/core/cascade_engine.py")
check("B3 engine", len(engine.splitlines()) == 744 and "compute_coherence" not in engine
      and "compute_forgetting" not in engine, "cascade_engine.py has 744 lines, no compute_coherence/compute_forgetting")

# B4 ─ arithmetic of the three accounts
pooled = math.sqrt((0.063 ** 2 + 0.058 ** 2) / 2)
d_table, glass = (0.742 - 0.529) / pooled, (0.742 - 0.529) / 0.058
need_sd = 0.213 / 2.84
t_table = 0.213 / math.sqrt(0.063 ** 2 / 100 + 0.058 ** 2 / 100)
check("B4 EMPIRICAL_RESULTS", round(d_table, 2) == 3.52 and round(glass, 2) == 3.67 and round(need_sd, 3) == 0.075,
      f"pooled d {d_table:.2f}, Glass {glass:.2f}; d=2.84 needs pooled SD {need_sd:.3f}; t {t_table:.1f} vs 24.7 stated")
syn_d = (0.93 - 0.58) / math.sqrt((0.04 ** 2 + 0.09 ** 2) / 2)
check("B4 CAS-009 / SYNTHESIS", round((0.93 - 0.58) / 0.58 * 100, 1) == 60.3 and round(syn_d, 2) == 5.03,
      f"0.58->0.93 is +60.3%, and SDs 0.04/0.09 give d {syn_d:.2f}, not 2.84")
stored = json.loads(git("show", f"HEAD:{STORED}"))
pcts = [dm["pct"] for dm in stored["per_domain"]]
check("B4 CAS-010", round(sum(pcts) / len(pcts), 2) == 110.05 and round((1 - 0.47) / 0.47 * 100, 1) == 112.8,
      f"110.05% is the mean of {pcts}; 0.47->1.0 would be +112.8%")
check("B4 CAS-011", round((0.42 - 0.02) / 0.42 * 100, 1) == 95.2 and round((1.00 - 0.048) / 1.00 * 100, 1) == 95.2,
      "0.42->0.02 and 1.00%->0.048% both give 95.2% from different numbers")

# B5 ─ the stored run
tie = all(dm["raw"]["raw"]["cascade"]["coherence"] == dm["raw"]["raw"]["additive"]["coherence"] for dm in stored["per_domain"])
flat = all(len(set(dm["raw"]["raw"]["static"]["coherence"])) == 1 and len(set(dm["raw"]["raw"]["cascade"]["coherence"])) == 1
           for dm in stored["per_domain"])
dz = all(dm["raw"]["stats"]["cascade_vs_additive"]["d"] == 0.0 for dm in stored["per_domain"])
check("B5 stored run", tie and flat and dz and stored["status"] == "[CONFIRMED]",
      f"cascade == additive in every trial of every domain; static and cascade have zero variance; "
      f"stored status {stored['status']} against claimed {stored['claimed_pct']}")


# B6 / B7 ─ reruns in scratch copies
def rerun(tag, sim_source):
    dest = WORK / tag
    head_tree(dest, [SIM, "12_IMPLEMENTATIONS"])
    if sim_source is not None:
        shutil.copyfile(sim_source, dest / SIM)
    run = subprocess.run([sys.executable, "-B", SIM], cwd=dest, capture_output=True, text=True, env=ENV, timeout=900)
    out = json.loads((dest / STORED).read_text(encoding="utf-8"))
    return run.returncode, run.stdout, out


code, out, res = rerun("b6_head", None)
check("B6 HEAD rerun", code == 0 and "+110.05%" in out and res["status"] == "[CONFIRMED]",
      f"exit {code}; measured {res['measured_pct']}, status {res['status']}")
code, out, res = rerun("b7_repaired", ROOT / SIM)
gain = re.search(r"Gain over additive:\s+(\S+)", out)
check("B7 repaired rerun", code == 0 and res["status"] == "[NO GAIN OVER ADDITIVE]" and res["measured_pct"] == 110.05
      and res["gain_over_additive"] == 0.0,
      f"exit {code}; measured {res['measured_pct']}, gain {gain.group(1) if gain else None}, status {res['status']}")

# B8 ─ the new test on HEAD, repaired, and mutated
dest = WORK / "b8"
existing = [r.rstrip("/") for reg in (head_reg, patched) for c in reg["claims"] for r in refs(c)
            if subprocess.run(["git", "cat-file", "-e", f"HEAD:{r.rstrip('/')}"], cwd=ROOT,
                              stderr=subprocess.DEVNULL).returncode == 0]
head_tree(dest, sorted(set(existing) | {"28_DEFENSE", "TRUTH_PRESSURE", "11_MATHEMATICAL_FOUNDATIONS",
                                        "12_IMPLEMENTATIONS", "tests/conftest.py", "pyproject.toml"}))
(dest / TEST).write_bytes((ROOT / TEST).read_bytes())


def pytest_run():
    run = subprocess.run([sys.executable, "-B", "-m", "pytest", "-q", "-p", "no:cacheprovider", "--tb=no", "-rf", TEST],
                         cwd=dest, capture_output=True, text=True, env=ENV, timeout=300)
    failed = sorted(set(re.findall(r"FAILED \S+::(\w+)", run.stdout)))
    tail = run.stdout.strip().splitlines()[-1] if run.stdout.strip() else run.stderr[-200:]
    return failed, tail


failed, tail = pytest_run()
check("B8 HEAD", failed == ["test_a_verdict_confirms_only_near_the_claim_and_only_with_a_gain",
                            "test_the_empirical_results_carry_their_status_note",
                            "test_the_stored_run_ties_the_additive_baseline"], f"{tail}; failing: {failed}")
for rel in (SIM, "TRUTH_PRESSURE/EMPIRICAL_RESULTS.md"):
    shutil.copyfile(ROOT / rel, dest / rel)
failed, tail = pytest_run()
check("B8 repaired", not failed, tail)
subprocess.run(["patch", "-p1", "--quiet", "-i", str(REVIEW / "RV19_claims_pointer_repairs.patch")], cwd=dest, check=True)
failed, tail = pytest_run()
check("B8 patched register", not failed, f"ratchet holds with the pointer patch applied: {tail}")
mutated = json.loads((dest / STORED).read_text(encoding="utf-8"))
mutated["per_domain"][0]["raw"]["raw"]["additive"]["coherence"][0] = 0.9
(dest / STORED).write_text(json.dumps(mutated), encoding="utf-8")
failed, tail = pytest_run()
check("B8 mutation", failed == ["test_the_stored_run_ties_the_additive_baseline"], f"fact pin fails under mutation: {failed}")

shutil.rmtree(WORK)
print(f"\nBatch 18: {'ALL PASS' if not failures else 'FAILURES: ' + ', '.join(failures)}")
sys.exit(1 if failures else 0)
