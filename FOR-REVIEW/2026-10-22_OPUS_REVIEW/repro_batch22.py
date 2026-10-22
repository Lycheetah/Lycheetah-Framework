#!/usr/bin/env python3
"""RV23 repro: re-score the external validations and re-test their significance.

    python3 -B repro_batch22.py <tree-root> <data-dir> [--perms 400] [--json PATH]

<tree-root> is a `git archive HEAD` copy holding 33_APPLICATIONS, 12_IMPLEMENTATIONS
and lycheetah. <data-dir> holds the public datasets downloaded from the URLs pinned in
the scripts: ucc/unhealthy_full.csv and persona/persona.jsonl. Each file is checked
against the script's own SHA-256 pin before use.

The question: both `independent_publisher_test.auc_sig` and
`external_validation.auc_significance` use the Mann-Whitney null standard error
without the tie correction, sqrt((n1+n2+1)/(12 n1 n2)). The hand-written lens fires
on a few percent of texts, so most scores are identical. Ties shrink the true null
variance, which makes the reported p-values conservative, and a "null" AUC near 0.5
may in fact be a significant WRONG-DIRECTION result. Three independent referees
decide it, so this does not hinge on one formula Sol wrote:

  1. the tie-corrected normal approximation, computed here;
  2. scipy.stats.mannwhitneyu (asymptotic, no continuity correction) on the same
     scores, which must agree with (1);
  3. a label-permutation null: the empirical SD of the AUC over random relabellings,
     which needs no variance formula at all.

Holm correction across the six UCC attributes is reported beside the raw verdicts.
Nothing here edits the repository; dated reports are records, not targets.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import random
import re
import sys
import zlib
from pathlib import Path

import numpy as np
from scipy import stats

CHECKS: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    CHECKS.append((name, ok, detail))
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  — {detail}" if detail else ""), flush=True)


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod  # dataclasses resolve their module through sys.modules
    spec.loader.exec_module(mod)
    return mod


def auc_and_tie_p(healthy: np.ndarray, unhealthy: np.ndarray) -> tuple[float, float, float]:
    """AUC = P(healthy > unhealthy), ties at half; tie-corrected two-sided z and p."""
    n1, n2 = len(healthy), len(unhealthy)
    allv = np.concatenate([healthy, unhealthy])
    ranks = stats.rankdata(allv)
    u = ranks[:n1].sum() - n1 * (n1 + 1) / 2
    a = u / (n1 * n2)
    n = n1 + n2
    _, counts = np.unique(allv, return_counts=True)
    tie_term = float(((counts.astype(float) ** 3) - counts).sum()) / (n * (n - 1))
    var = (n1 * n2 / 12.0) * ((n + 1) - tie_term)
    if var <= 0:
        return a, float("nan"), float("nan")
    z = (u - n1 * n2 / 2) / math.sqrt(var)
    return a, z, math.erfc(abs(z) / math.sqrt(2.0))


def perm_sd(healthy: np.ndarray, unhealthy: np.ndarray, perms: int, seed: int) -> float:
    allv = np.concatenate([healthy, unhealthy])
    ranks = stats.rankdata(allv)
    n1, n2 = len(healthy), len(unhealthy)
    rng = np.random.default_rng(seed)
    out = np.empty(perms)
    for i in range(perms):
        idx = rng.permutation(len(allv))[:n1]
        out[i] = (ranks[idx].sum() - n1 * (n1 + 1) / 2) / (n1 * n2)
    return float(out.std(ddof=1))


def holm(pvals: list[float]) -> list[float]:
    order = sorted(range(len(pvals)), key=lambda i: pvals[i])
    adj = [0.0] * len(pvals)
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (len(pvals) - rank) * pvals[i]))
        adj[i] = running
    return adj


def verdict(a: float, p: float) -> str:
    if p != p or p >= 0.05:
        return "null"
    return "CORRECT" if a > 0.5 else "WRONG-DIRECTION"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", type=Path)
    ap.add_argument("data", type=Path)
    ap.add_argument("--perms", type=int, default=400)
    ap.add_argument("--json", type=Path, default=None)
    args = ap.parse_args()
    root, data = args.root.resolve(), args.data.resolve()
    apps = root / "33_APPLICATIONS"

    ipt = load(apps / "independent_publisher_test.py", "ipt")
    ext = load(apps / "external_validation.py", "ext")
    sys.path.insert(0, str(root))
    sys.path.insert(0, str(root / "12_IMPLEMENTATIONS"))
    import lycheetah  # noqa: E402

    ucc_raw = (data / "ucc/unhealthy_full.csv").read_bytes()
    per_raw = (data / "persona/persona.jsonl").read_bytes()
    check("C1 UCC bytes match the script's pin",
          hashlib.sha256(ucc_raw).hexdigest() == ipt.UCC_SHA256)
    check("C1 persona bytes match the script's pin",
          hashlib.sha256(per_raw).hexdigest() == ext.PERSONA_SHA256)

    # Same aggregation, filter, seed and sample as independent_publisher_test.main.
    items = ipt.aggregate(ucc_raw)
    items = [v for v in items if len(v["text"].split()) >= 5]
    random.Random(7).shuffle(items)
    items = items[:12000]
    check("C2 UCC sample size is the published 12,000", len(items) == 12000, str(len(items)))

    cues = json.loads((apps / "derived/harm_cues_v1.json").read_text())
    names = list(cues["families"])
    pats = [re.compile(cues["families"][n], re.I) for n in names]
    w = np.array([cues["weights"][n] for n in names])
    lenses = {
        "aura": lambda t: lycheetah.check(t).alignment_percent,
        "derived": lambda t: float(np.array([1.0 if p.search(t) else 0.0 for p in pats]) @ w),
    }

    result: dict = {"ucc": {}, "persona": {}}
    for lname, score in lenses.items():
        sc = np.array([score(v["text"]) for v in items], dtype=float)
        _, counts = np.unique(sc, return_counts=True)
        modal = counts.max() / len(sc)
        rows = []
        for k in ipt.ATTRIBUTES:
            lab = np.array([v[k] >= 0.5 for v in items])
            pos, neg = sc[lab], sc[~lab]
            if len(pos) < 30:
                continue
            a_mod = ipt.auc(list(neg), list(pos))
            _, p_mod = ipt.auc_sig(a_mod, len(pos), len(neg))
            a, z, p_tie = auc_and_tie_p(neg, pos)
            sp = stats.mannwhitneyu(neg, pos, alternative="two-sided",
                                    method="asymptotic", use_continuity=False).pvalue
            se_noties = math.sqrt((len(pos) + len(neg) + 1) / (12.0 * len(pos) * len(neg)))
            psd = perm_sd(neg, pos, args.perms, seed=zlib.crc32(f"{lname}:{k}".encode()))
            rows.append(dict(attr=k, n_pos=int(len(pos)), auc=a, auc_module=a_mod,
                             p_module=p_mod, p_tie=p_tie, p_scipy=float(sp),
                             se_noties=se_noties, se_perm=psd, z_tie=z))
        for r, h in zip(rows, holm([r["p_tie"] for r in rows])):
            r["p_tie_holm"] = h
        for r, h in zip(rows, holm([r["p_module"] for r in rows])):
            r["p_module_holm"] = h
        result["ucc"][lname] = {"modal_score_share": modal, "rows": rows}

        print(f"\nUCC · {lname} lens · modal score share {modal:.1%}")
        print(f"  {'attribute':<15}{'n_pos':>6}{'AUC':>7}{'p(no-ties)':>12}{'p(ties)':>11}"
              f"{'p(scipy)':>11}{'SE no-ties':>11}{'SE perm':>9}{'Holm(ties)':>11}  module → corrected")
        for r in rows:
            print(f"  {r['attr']:<15}{r['n_pos']:>6}{r['auc']:>7.3f}{r['p_module']:>12.2e}"
                  f"{r['p_tie']:>11.2e}{r['p_scipy']:>11.2e}{r['se_noties']:>11.4f}"
                  f"{r['se_perm']:>9.4f}{r['p_tie_holm']:>11.2e}  "
                  f"{verdict(r['auc'], r['p_module'])} → {verdict(r['auc'], r['p_tie'])}"
                  f" / Holm {verdict(r['auc'], r['p_tie_holm'])}")
        check(f"C3 {lname}: module AUC reproduced by rank AUC",
              all(abs(r["auc"] - r["auc_module"]) < 1e-12 for r in rows))
        check(f"C3 {lname}: tie-corrected p agrees with scipy",
              all(math.isclose(r["p_tie"], r["p_scipy"], rel_tol=1e-6, abs_tol=1e-300) for r in rows))
        ratio = [r["se_perm"] / r["se_noties"] for r in rows]
        result["ucc"][lname]["se_perm_over_noties"] = ratio
        print(f"  permutation SE / no-ties SE: " + ", ".join(f"{x:.3f}" for x in ratio))

    # Persona: the single social-engineering test.
    prow = [json.loads(l) for l in per_raw.decode("utf-8").splitlines() if l.strip()]
    conc = [r["statement"] for r in prow if r["answer_matching_behavior"] == " Yes"]
    alig = [r["statement"] for r in prow if r["answer_matching_behavior"] == " No"]
    lens = lenses["aura"]
    sa = np.array([lens(t) for t in alig], float)
    scn = np.array([lens(t) for t in conc], float)
    a_mod = ext.roc_auc(list(sa), list(scn))
    _, p_mod = ext.auc_significance(a_mod, len(sa), len(scn))
    a, z, p_tie = auc_and_tie_p(sa, scn)
    psd = perm_sd(sa, scn, args.perms, seed=11)
    se_nt = math.sqrt((len(sa) + len(scn) + 1) / (12.0 * len(sa) * len(scn)))
    _, counts = np.unique(np.concatenate([sa, scn]), return_counts=True)
    result["persona"] = dict(n_aligned=len(sa), n_concerning=len(scn), auc=a, auc_module=a_mod,
                             p_module=p_mod, p_tie=p_tie, se_noties=se_nt, se_perm=psd,
                             modal_score_share=float(counts.max() / counts.sum()))
    print(f"\nPersona social-engineering · aura lens · {len(sa)}/{len(scn)} · "
          f"modal share {result['persona']['modal_score_share']:.1%}")
    print(f"  AUC {a:.3f} (module {a_mod:.3f})  p no-ties {p_mod:.3f}  p ties {p_tie:.3f}  "
          f"SE no-ties {se_nt:.4f}  SE perm {psd:.4f}")
    check("C4 persona AUC reproduced", abs(a - a_mod) < 1e-12, f"{a:.4f}")

    if args.json:
        args.json.write_text(json.dumps(result, indent=2), encoding="utf-8")
    fails = sum(1 for _, ok, _ in CHECKS if not ok)
    print(f"\n{len(CHECKS) - fails} PASS, {fails} FAIL")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
