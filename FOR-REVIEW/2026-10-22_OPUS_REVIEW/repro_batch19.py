"""Batch 19 (RV20, cellular sheaf and factorial experiment) witnesses.

Usage: python3 -B repro_batch19.py <framework-root> <scratch-dir>

C1 lookahead + work_coupled leaves work unpaid; snapshot cells pay exactly (control)
C2 the new receipts count the same underpaid jobs an external probe counts; HEAD has none
C3 Euler-Poincare holds under a corrupted rank: the identity cannot check the rank
C4 hashed labels collide; for a/b the obstruction equals parent-label inequality
C5 has_discordant_parent's coboundary-energy condition never vetoes an obstructed star
C6 parents_v3 docstring at HEAD names (k-3, k-2); the code uses (k-2, k-1)
C7 Yates effects equal twice the OLS coefficients (control on the effect algebra)
C8 ConsensusArena dim H^1 is the same for agreeing and opposed agents (topology only)
C9 the new tests fail on HEAD source, pass on the working tree, and fail under mutation
Read-only on the repository; HEAD and the mutant run from scratch copies.
"""
import io
import itertools
import json
import os
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

MOD = "12_IMPLEMENTATIONS/core/sheaf_cohomology_factorial.py"
TEST = "tests/test_sheaf_cohomology_factorial.py"
NEW_TESTS = (
    "test_work_coupled_receipts_expose_lookahead_underpayment",
    "test_factorial_summary_carries_per_cell_receipts",
)
ENV = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "MPLBACKEND": "Agg"}


def probe(root):
    """Measure every claim against the module found under ``root``; print JSON."""
    root = Path(root)
    for sub in ("", "12_IMPLEMENTATIONS", "12_IMPLEMENTATIONS/core"):
        sys.path.insert(0, str(root / sub))
    import numpy as np
    import sheaf_cohomology_factorial as M

    out = {}
    log = []
    orig = M._adjudicate_orthogonal

    def wrapped(engine, job, pending, model, **kw):
        work = orig(engine, job, pending, model, **kw)
        log.append((job, work))
        return work

    M._adjudicate_orthogonal = wrapped
    cells = {}
    for topo in ("chain", "star", "diamond", "diamond_cycle"):
        cal = M.calibrate_v3(8, topo, 64.0)
        for seed, load in itertools.product((0, 1), (1.0, 3.0)):
            trace = M.arrival_trace_v3(8, topo, seed, load / cal.tau, 48)
            for cell in M.FACTORIAL_CELLS:
                if cell[2] != "work_coupled":
                    continue
                log.clear()
                row = M.simulate_orthogonal(
                    trace, cal, "cascade",
                    timing_mode=cell[0], queue_scope=cell[1], duration_mode=cell[2],
                )
                planned, actual = log[0::2], log[1::2]
                assert all(p[0] == a[0] for p, a in zip(planned, actual)), "pairing broke"
                acc = cells.setdefault("/".join(cell), {
                    "jobs": 0, "differ": 0, "net": 0.0, "underpaid_probe": 0,
                    "max_ratio": 0.0, "receipt_underpaid": None,
                })
                paid_run = sum(max(1.0, p[1]) for p in planned)
                actual_run = sum(a[1] for a in actual)
                acc["max_ratio"] = max(acc["max_ratio"], actual_run / paid_run)
                for (_, pw), (_, aw) in zip(planned, actual):
                    acc["jobs"] += 1
                    acc["differ"] += pw != aw
                    acc["net"] += aw - pw
                    acc["underpaid_probe"] += aw > max(1.0, pw) * (1 + 1e-6)
                if "receipt_jobs_underpaid" in row:
                    acc["receipt_underpaid"] = (acc["receipt_underpaid"] or 0) + row["receipt_jobs_underpaid"]
    M._adjudicate_orthogonal = orig
    out["c1"] = cells

    orig_svd = M._svd_parts

    def rank_one(matrix, atol, rtol):
        u, s, vh, keep, cut = orig_svd(matrix, atol, rtol)
        keep = keep.copy()
        keep[:] = False
        keep[0] = True
        return u, s, vh, keep, cut

    sheaf = M.CellularSheaf.from_parent_graph(M.parents_v3(6, "diamond_cycle"))
    M._svd_parts = rank_one
    bad = sheaf.cohomology_certificate()
    M._svd_parts = orig_svd
    good = sheaf.cohomology_certificate()
    out["c3"] = {
        "bad": [bad.coboundary_rank, bad.dim_h0_global_sections, bad.euler_poincare_lhs == bad.euler_poincare_rhs],
        "good": [good.coboundary_rank, good.dim_h0_global_sections, good.euler_poincare_lhs == good.euler_poincare_rhs],
    }

    vec = M.paradigm_stalk_vector
    hidden = 0
    for k in (1, 2, 3):
        for combo in itertools.product("abcd", repeat=k):
            star = M.CellularSheaf(k + 1, [(i, k) for i in range(k)], stalk_dim=2)
            cert = star.relative_obstruction({i: vec(p, 2) for i, p in enumerate(combo)})
            hidden += len(set(combo)) > 1 and not cert.obstructed
    ab_equiv = all(
        M.CellularSheaf(k + 1, [(i, k) for i in range(k)]).relative_obstruction(
            {i: vec(p) for i, p in enumerate(combo)}
        ).obstructed == (len(set(combo)) > 1)
        for k in (1, 2, 3, 4)
        for combo in itertools.product("ab", repeat=k)
    )
    out["c4"] = {"hidden": hidden, "ab_equiv": ab_equiv,
                 "c_is_a_d2": bool(np.array_equal(vec("c", 2), vec("a", 2)))}

    total = veto = 0
    for k in (2, 3):
        for combo in itertools.product("ab", repeat=k):
            for child in "ab":
                star = M.CellularSheaf(k + 1, [(i, k) for i in range(k)])
                parents = {i: vec(p) for i, p in enumerate(combo)}
                if not star.relative_obstruction(parents).obstructed:
                    continue
                total += 1
                x = np.concatenate([parents[i] for i in range(k)] + [vec(child)])
                veto += not np.linalg.norm(star.coboundary_matrix() @ x) > 1e-6
    out["c5"] = {"total": total, "veto": veto}

    doc = M.parents_v3.__doc__ or ""
    out["c6"] = {"parents_7": {str(k): list(v) for k, v in enumerate(M.parents_v3(7, "diamond_cycle"))},
                 "doc_says_k3": "(k-3, k-2)" in doc.replace(" - ", "-"),
                 "doc_says_k2": "(k-2, k-1)" in doc.replace(" - ", "-")}

    rng = np.random.default_rng(7)
    vals = {c: float(rng.normal()) for c in M.FACTORIAL_CELLS}
    eff = M.compute_yates_factorial_effects(vals)
    sa = {"lookahead": -1, "snapshot": 1}
    sb = {"all_domains": -1, "domain_isolated": 1}
    sc = {"fixed_tau": -1, "work_coupled": 1}
    X = np.array([[1, sa[a], sb[b], sc[c], sa[a] * sb[b], sa[a] * sc[c], sb[b] * sc[c], sa[a] * sb[b] * sc[c]]
                  for a, b, c in M.FACTORIAL_CELLS], float)
    beta = np.linalg.lstsq(X, np.array([vals[c] for c in M.FACTORIAL_CELLS]), rcond=None)[0]
    names = ["grand_mean", "main_effect_timing_snapshot_minus_lookahead",
             "main_effect_queue_isolated_minus_all_domains", "main_effect_duration_work_coupled_minus_fixed_tau",
             "interaction_timing_x_queue", "interaction_timing_x_duration",
             "interaction_queue_x_duration", "interaction_three_way"]
    out["c7"] = all(abs(eff[n] - (beta[i] if i == 0 else 2 * beta[i])) < 1e-12 for i, n in enumerate(names))

    from lycheetah.consensus.arena import ConsensusArena

    reports = {}
    for name, vecs in (("agree", ([1, 0], [1, 0], [1, 0])), ("opposed", ([1, 0], [-1, 0], [0, 1]))):
        arena = ConsensusArena(anchor=[1.0, 0.0])
        for i, v in enumerate(vecs):
            arena.add_agent(f"a{i}", v)
        rep = arena.sheaf_cohomology_report()
        reports[name] = {"h0": rep["cohomology"]["dim_h0_global_sections"],
                         "h1": rep["cohomology"]["dim_h1_cohomology"],
                         "energy": rep["dirichlet_energy"]}
    out["c8"] = reports
    print(json.dumps(out))


def main():
    root = Path(sys.argv[1]).resolve()
    work = Path(sys.argv[2]).resolve() / "rv20_repro"
    failures = []

    def check(tag, ok, detail):
        print(f"[{'PASS' if ok else 'FAIL'}] {tag}: {detail}", flush=True)
        if not ok:
            failures.append(tag)

    def run_probe(tree):
        out = subprocess.run([sys.executable, "-B", __file__, "--probe", str(tree)],
                             capture_output=True, text=True, env=ENV, cwd=work)
        if out.returncode:
            raise SystemExit(out.stderr[-2000:])
        return json.loads(out.stdout.strip().splitlines()[-1])

    def pytest(tree):
        out = subprocess.run([sys.executable, "-B", "-m", "pytest", "-q", "-p", "no:cacheprovider", TEST],
                             capture_output=True, text=True, env=ENV, cwd=tree)
        return out.returncode, out.stdout

    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    head = work / "head"
    archive = subprocess.run(["git", "archive", "HEAD"], cwd=root, capture_output=True, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        tar.extractall(head, filter="data")

    tree_p, head_p = run_probe(root), run_probe(head)

    for label, p in (("tree", tree_p), ("HEAD", head_p)):
        la = p["c1"]["lookahead/all_domains/work_coupled"]
        snaps = [p["c1"][f"snapshot/{q}/work_coupled"] for q in ("all_domains", "domain_isolated")]
        check(f"C1 {label} lookahead underpays",
              la["differ"] > 0 and la["net"] > 0,
              f"{la['differ']}/{la['jobs']} jobs differ, net {la['net']:+.0f} work, max run ratio {la['max_ratio']:.2f}")
        check(f"C1 {label} snapshot control",
              all(s["differ"] == 0 for s in snaps),
              ", ".join(f"{s['differ']}/{s['jobs']}" for s in snaps))
    agree = all(c["receipt_underpaid"] == c["underpaid_probe"] for c in tree_p["c1"].values())
    check("C2 tree receipts match probe", agree,
          {k: (c["receipt_underpaid"], c["underpaid_probe"]) for k, c in tree_p["c1"].items()})
    check("C2 HEAD has no receipt", all(c["receipt_underpaid"] is None for c in head_p["c1"].values()),
          "receipt_jobs_underpaid absent at HEAD")

    c3 = tree_p["c3"]
    check("C3 Euler-Poincare cannot fail", c3["bad"][2] and c3["good"][2] and c3["bad"][0] != c3["good"][0],
          f"rank {c3['bad'][0]} -> dimH0 {c3['bad'][1]} EP holds; rank {c3['good'][0]} -> dimH0 {c3['good'][1]} EP holds")
    c4 = tree_p["c4"]
    check("C4 encodings", c4["hidden"] > 0 and c4["ab_equiv"] and c4["c_is_a_d2"],
          f"{c4['hidden']} distinct-label parent sets read consistent (d=2, a-d, k<=3); a/b obstruction == inequality: {c4['ab_equiv']}")
    c5 = tree_p["c5"]
    check("C5 redundant condition", c5["total"] > 0 and c5["veto"] == 0,
          f"{c5['veto']} vetoes over {c5['total']} obstructed stars")
    c6h, c6t = head_p["c6"], tree_p["c6"]
    check("C6 docstring", c6h["doc_says_k3"] and c6t["doc_says_k2"] and not c6t["doc_says_k3"]
          and c6t["parents_7"]["4"] == [2, 3],
          f"code parents(4)={c6t['parents_7']['4']}; HEAD doc (k-3,k-2): {c6h['doc_says_k3']}; tree doc (k-2,k-1): {c6t['doc_says_k2']}")
    check("C7 Yates == 2*OLS (control)", tree_p["c7"], "all seven effects and the mean")
    c8 = tree_p["c8"]
    check("C8 arena H^1 is topology only",
          c8["agree"]["h1"] == c8["opposed"]["h1"] and c8["agree"]["h0"] == c8["opposed"]["h0"]
          and c8["agree"]["energy"] == 0 and c8["opposed"]["energy"] > 0,
          c8)

    shutil.copy(root / TEST, head / TEST)
    code, out = pytest(head)
    failed = sorted(line.split("::")[1].split()[0] for line in out.splitlines() if line.startswith("FAILED"))
    check("C9 HEAD source fails the new tests", code != 0 and failed == sorted(NEW_TESTS), failed)
    code, out = pytest(root)
    check("C9 working tree passes", code == 0, out.strip().splitlines()[-1])
    mutant = work / "mutant"
    shutil.copytree(head, mutant)
    shutil.copy(root / MOD, mutant / MOD)
    src = (mutant / MOD).read_text()
    swap = '"receipt_jobs_underpaid": len(shortfalls),'
    assert src.count(swap) == 1
    (mutant / MOD).write_text(src.replace(swap, '"receipt_jobs_underpaid": 0,'))
    code, out = pytest(mutant)
    check("C9 receipt pin fails under mutation", code != 0 and NEW_TESTS[0] in out,
          out.strip().splitlines()[-1])

    shutil.rmtree(work)
    print("\nRESULT:", "ALL PASS" if not failures else f"FAILED {failures}")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--probe":
        probe(sys.argv[2])
    else:
        main()
