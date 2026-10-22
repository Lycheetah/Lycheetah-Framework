"""Batch 17 (RV18): the mathematical-foundations review, rerun and sharpened.

Usage: python3 -B repro_batch17.py <framework-root> <scratch-dir> [<baseline-worktree>]

P0 reruns the eighteen 2026-10-20 math probes on the current tree and compares their
details with the committed math-probes.json. Each A-probe then replaces a bare
counterexample with the exact domain where the written claim holds. Every probe
carries a control that must pass, so a broken harness cannot report a refutation.
A16 runs lyapunov_verification.py only inside the baseline worktree, because the
script writes its results file beside itself.
"""
import ast
import importlib.util
import json
import os
import math
import re
import runpy
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np

ROOT = Path(sys.argv[1]).resolve()
SCRATCH = Path(sys.argv[2]).resolve()
BASELINE = Path(sys.argv[3]).resolve() if len(sys.argv) > 3 else None
CORE = ROOT / "12_IMPLEMENTATIONS" / "core"
MODULES = {}
FAILURES = []


def say(*parts):
    print(*parts, flush=True)


def check(name, condition, detail=""):
    say(f"  [{'ok' if condition else 'FAIL'}] {name}" + (f": {detail}" if detail else ""))
    if not condition:
        FAILURES.append(name)


def core(filename):
    if filename not in MODULES:
        MODULES[filename] = runpy.run_path(str(CORE / filename), run_name="rv18_" + filename.replace(".", "_"))
    return MODULES[filename]


def h2(p):
    """Binary entropy in bits."""
    return 0.0 if p in (0.0, 1.0) else -(p * math.log2(p) + (1 - p) * math.log2(1 - p))


def shannon(p, base=math.e):
    p = np.asarray(p, dtype=float)
    p = p[p > 0]
    return float(-np.sum(p * np.log(p)) / math.log(base))


# ---------------------------------------------------------------- P0
say("P0  the 2026-10-20 probes on today's tree")
spec = importlib.util.spec_from_file_location("rv18_math_probes", ROOT / "28_DEFENSE/review_2026_10_20/math_probes.py")
mp = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mp
spec.loader.exec_module(mp)
committed = {p["id"]: p for p in json.loads((ROOT / "28_DEFENSE/review_2026_10_20/math-probes.json").read_text())["probes"]}
same = 0
for identifier, _, _, _, fn in mp.PROBES:
    details = json.loads(json.dumps(fn(ROOT)))  # tuples become lists, as in the committed file
    same += details == committed[identifier]["details"]
check("18/18 reproduce with details identical to the committed JSON", same == len(mp.PROBES) == 18, f"{same}/{len(mp.PROBES)}")

# ---------------------------------------------------------------- A1 (M1)
say("A1  MATHEMATICS_FOUNDATIONS ~607: entropy curvature and descent")
curv = lambda p: -1 / p - 1 / (1 - p)  # d2/dp2 of binary entropy in nats
check("h'' is unbounded near the simplex edge (no global L)", abs(curv(1e-6)) > 1e5, f"h''(1e-6)={curv(1e-6):.3g}")
grid = np.linspace(0.1, 0.9, 801)
check("control: on [0.1,0.9] the curvature is bounded by 1/0.1+1/0.9", abs(min(curv(p) for p in grid) + 1 / 0.1 + 1 / 0.9) < 1e-9)
dh = lambda p: math.log((1 - p) / p)  # dh/dp in nats
p_desc = p_asc = 0.6
for _ in range(300):
    p_desc = min(max(p_desc - 0.05 * dh(p_desc), 1e-9), 1 - 1e-9)
    p_asc = p_asc + 0.05 * dh(p_asc)
check("gradient descent on S moves away from its only critical point 0.5", abs(p_desc - 0.5) > 0.4, f"p={p_desc:.4f}")
check("control: gradient ascent converges to 0.5", abs(p_asc - 0.5) < 1e-6, f"p={p_asc:.8f}")
jac = [1 - 0.1 * curv(p) for p in grid]
check("I - a*Hess(S) has every eigenvalue > 1 on [0.1,0.9] (sign reversed vs (0,1))", min(jac) > 1, f"min={min(jac):.4f}")

# ---------------------------------------------------------------- A2 (M2)
say("A2  MATHEMATICS_FOUNDATIONS ~415: a norm bound carries no sign")
Ao = np.diag([1.0, 0.0])
G = 0.2 * Ao
check("alpha*Ao with beta=gamma=0 meets alpha+beta <= 1-gamma*|F| yet has eigenvalue +0.2",
      0.2 <= 1 and max(np.linalg.eigvals(G).real) > 0, f"eig={np.linalg.eigvals(G).real.tolist()}")
check("control: -I satisfies the same bound and decays", max(np.linalg.eigvals(-np.eye(2)).real) < 0)

# ---------------------------------------------------------------- A3 (M4)
say("A3  MATHEMATICS_FOUNDATIONS ~318: which entropy level set is convex")
rng = np.random.default_rng(18)
eps = 0.6
pts = rng.dirichlet([0.3, 0.3, 0.3], size=40000)
H = np.array([shannon(p) for p in pts])
sup, sub = pts[H >= eps], pts[H < eps]
mids_sup = (sup[:5000] + sup[5000:10000]) / 2
mids_sub = (sub[:5000] + sub[5000:10000]) / 2
bad_sup = sum(shannon(m) < eps - 1e-12 for m in mids_sup)
bad_sub = sum(shannon(m) >= eps for m in mids_sub)
check("control: {S >= eps} is convex (doc parenthetical is TRUE): 0 of 5000 midpoints leave it", bad_sup == 0)
check("{S < eps} is not convex: midpoints of low-entropy pairs leave it", bad_sub > 0, f"{bad_sub}/5000")
kern = core("lamague_reference.py")["TRIADKernel"](np.array([1.0, 0.0]), np.array([1.0, 1.0]))
a, b = np.array([1.0, 0.0]), np.array([0.0, 1.0])
check("ascent_operator is not unitary: <Fa,Fb> != <a,b>", abs(kern.ascent_operator(a) @ kern.ascent_operator(b)) > 0.1)

# ---------------------------------------------------------------- A4 (M5)
say("A4  PI_THRESHOLD_DERIVATION 76-108: norms and the BBP outlier")
n, r = 64, 4
V = np.eye(n)[:, :r]
check("|VV^T/n| = 1/n, not 1/sqrt(n)", abs(np.linalg.norm(V @ V.T / n, 2) - 1 / n) < 1e-12)
check("|11^T/n| = 1, not Pi/n", abs(np.linalg.norm(np.ones((n, n)) / n, 2) - 1) < 1e-12)
rng = np.random.default_rng(1200)
N = 1200
X = rng.standard_normal((N, N))
W = (X + X.T) / math.sqrt(2 * N)
u = rng.standard_normal(N)
u /= np.linalg.norm(u)
for theta in (0.5, 1.5, 3.0):
    top = float(np.linalg.eigvalsh(W + theta * np.outer(u, u))[-1])
    predicted = theta + 1 / theta if theta > 1 else 2.0
    check(f"theta={theta}: top eigenvalue {top:.3f} vs {'theta+1/theta' if theta > 1 else 'bulk edge 2'} {predicted:.3f}",
          abs(top - predicted) < 0.1)
S_sym = W + 3.0 * np.outer(u, u)
check("a symmetric operator has no complex pair, so no Hopf crossing", float(np.max(np.abs(np.linalg.eigvals(S_sym).imag))) < 1e-8)

# ---------------------------------------------------------------- A5 (M6, PI_DERIVATION ~211)
say("A5  MASTER_EQUATION 152-180: crossing Pi_th never changes stability")
k1, k2, Pth, Pinv = 0.5, 0.3, 1.2, 0.7
stable_everywhere = True
for Pi in np.linspace(0.2, 3.0, 29):
    f = lambda x, Pi=Pi: k1 * (Pi - Pth) - k2 * (x - Pinv)
    x = Pinv + 0.3
    for _ in range(4000):
        x += 0.01 * f(x)
    xstar = Pinv + k1 * (Pi - Pth) / k2
    slope = (f(xstar + 1e-6) - f(xstar - 1e-6)) / 2e-6
    stable_everywhere &= abs(x - xstar) < 1e-4 and abs(slope + k2) < 1e-6
check("for 29 values of Pi on both sides of Pi_th: converges to Psi_inv + k1(Pi-Pi_th)/k2, slope -k2", stable_everywhere)
x = Pinv - 0.01
check("PI_DERIVATION's dL/dt < 0 fails just below Psi_inv when Pi < Pi_th",
      (x - Pinv) * (k1 * (0.7 - Pth) - k2 * (x - Pinv)) > 0)
check("control: Pi = Pi_th puts the equilibrium at Psi_inv", abs(k1 * (Pth - Pth) - k2 * (Pinv - Pinv)) == 0)

# ---------------------------------------------------------------- A6 (M7)
say("A6  FORMAL_SPINE M2 / MIC-003: the score threshold admits drift")
mo = core("microorcim_tracker.py")
check("compute_sovereignty(0.2, 1) == 0.8, so 'score >= 0.8' admits drift 0.2", abs(mo["compute_sovereignty"](0.2, 1.0) - 0.8) < 1e-12)
check("control: zero drift with full stability scores 1", mo["compute_sovereignty"](0.0, 1.0) == 1.0)

# ---------------------------------------------------------------- A8 (M9)
say("A8  CASCADE_FORMAL_PROOFS 2.2: the true chain rule, as a control")
rng = np.random.default_rng(22)
ok = True
for _ in range(2000):
    J = rng.dirichlet(np.ones(12)).reshape(3, 4)
    ok &= shannon(J.ravel()) >= shannon(J.sum(axis=1)) - 1e-12
check("control: H(X,Y) >= H(X) for 2000 random joints", ok)
check("renormalized categorical extension can lower entropy ([.5,.5] -> [.01,.01,.98])",
      shannon([0.01, 0.01, 0.98], 2) < shannon([0.5, 0.5], 2))

# ---------------------------------------------------------------- A9 (M10)
say("A9  CASCADE_FORMAL_PROOFS 4.1: exact TES and VTR conditions")
rng = np.random.default_rng(41)
agree = True
for _ in range(5000):
    m = int(rng.integers(1, 9))
    rel = rng.uniform(0, 1, m)
    Hold = sum(h2(x) for x in rel)
    rn = float(rng.uniform(0, 1))
    tes_old, tes_new = 1 - Hold / m, 1 - (Hold + h2(rn)) / (m + 1)
    if abs(h2(rn) - Hold / m) > 1e-9:
        agree &= (tes_new >= tes_old) == (h2(rn) <= Hold / m)
check("TES_new >= TES_old iff h(r_new) <= H_old/n (5000 random states)", agree)
lo, hi = 0.5, 1.0
for _ in range(80):
    mid = (lo + hi) / 2
    lo, hi = (mid, hi) if h2(mid) > 0.3 else (lo, mid)
r_star = hi
floor_ok = []
for rn in (r_star - 1e-3, r_star + 1e-3):
    # The worst admissible old state sits exactly on the floor: H_old = 0.3 n, TES_old = 0.7.
    floor_ok.append(min(1 - (0.3 * m + h2(rn)) / (m + 1) for m in range(1, 30)) >= 0.7 - 1e-12)
check(f"the 0.70 floor survives every old state iff r_new >= {r_star:.4f} (or <= {1 - r_star:.4f})",
      floor_ok == [False, True], f"just below: {floor_ok[0]}, just above: {floor_ok[1]}")
agree = True
for _ in range(5000):
    Vv, Rr = rng.uniform(1, 5), rng.uniform(0.5, 5)
    if Vv < Rr:
        continue
    va, ra = rng.uniform(0, 3), rng.uniform(0.01, 3)
    if abs(va - (ra - (Vv - Rr))) > 1e-9:
        agree &= ((Vv + va) / (Rr + ra) >= 1) == (va >= ra - (Vv - Rr))
check("VTR_new >= 1 iff v_add >= r_add - (V - R) (random sweep)", agree)

# ---------------------------------------------------------------- A10 (M11)
say("A10 chrysopoeia solve then coagula: the true domain of the guarantee")
ch = core("chrysopoeia_engine.py")
holds, fails = [], []
for c in np.linspace(0, 1, 301):
    if abs(c - 13 / 30) < 1e-9:
        continue
    st = ch["TransformationState"](vector=np.ones(3), coherence=float(c), entropy=0.5)
    np.random.seed(5)
    out = ch["coagula"](ch["solve"](st), ch["ConstraintSet"]())
    (holds if out.coherence >= c else fails).append(float(c))
check("C(coagula(solve(c))) >= c exactly for c < 13/30 and fails for c > 13/30",
      max(holds) < 13 / 30 < min(fails), f"largest holding {max(holds):.4f}, smallest failing {min(fails):.4f}")
check("control: at c = 0.05 (solve clamps to 0) the result is 0.15", abs(
    ch["coagula"](ch["solve"](ch["TransformationState"](vector=np.ones(3), coherence=0.05, entropy=0.5)),
                  ch["ConstraintSet"]()).coherence - 0.15) < 1e-12)
st = ch["TransformationState"](vector=np.ones(3), coherence=0.5, entropy=0.5)
v1 = ch["Xi"](st, ch["ConstraintSet"](), rng=np.random.default_rng(1)).vector
v2 = ch["Xi"](st, ch["ConstraintSet"](), rng=np.random.default_rng(2)).vector
check("Xi is stochastic: the same input gives different outputs, so it is not a fixed contraction map",
      float(np.linalg.norm(v1 - v2)) > 1e-3)

# ---------------------------------------------------------------- A11 (M12)
say("A11 HARMONIA Theorem 1.1 and the C(r) table")
check("(3/2)^a != 2^b for 1 <= a <= 100, every b (3^a is odd)",
      all(Fraction(3, 2) ** a != Fraction(2) ** round(a * math.log2(1.5)) and (3 ** a) % 2 == 1 for a in range(1, 101)))
cf = lambda q: mp.continued_fraction(Fraction(q))
table = {"1": 1.0, "2": 1.0, "3/2": 0.571, "4/3": 0.444, "5/4": 0.364}
fit = {k: 1 / (1 + cf(k)[1] / 2 - 0.25) for k in ("3/2", "4/3", "5/4")}
check("the fifth, fourth and third rows fit 1/(1 + a1/2 - 1/4) (an observation, not a derivation)",
      all(abs(fit[k] - table[k]) < 5e-4 for k in fit), str({k: round(v, 3) for k, v in fit.items()}))
k1v = {k: float(1 / (1 + sum(Fraction(a, 2 ** (i + 1)) for i, a in enumerate(cf(k))))) for k in table}
check("summing from k=1 fits unison and octave only", abs(k1v["1"] - 2 / 3) < 1e-12 and k1v["3/2"] != 0.571,
      str({k: round(v, 3) for k, v in k1v.items()}))
check("45/32 = [1;2,2,6]", cf("45/32") == [1, 2, 2, 6])

# ---------------------------------------------------------------- A12 (M13)
say("A12 dS = -W/T: the one regime where it is exact")
R, T, V1, V2 = 8.31446261815324, 300.0, 1.0, 0.5
W_on = R * T * math.log(V1 / V2)
dS = R * math.log(V2 / V1)
check("control: reversible isothermal ideal-gas compression gives dS = -W_on/T exactly", abs(dS + W_on / T) < 1e-12)
check("reversible adiabatic compression gives dS = 0 while -W_on/T < 0 (MP17)",
      abs(committed["MP17"]["details"]["actual_delta_entropy_J_per_K"]) < 1e-9
      and committed["MP17"]["details"]["minus_work_over_initial_temperature"] < 0)

# ---------------------------------------------------------------- A13 (M14) + A15 (DG02)
say("A13 AGM Postulate 4: the cascade fires only above old + 0.3")
ce = core("cascade_engine.py")
Block = ce["KnowledgeBlock"]
rows = []
for label, P in (("lower", 0.8), ("tie band +0.2", 1.6), ("above +0.5", 1.75)):
    eng = ce["CascadeEngine"]()
    eng.add_block(Block("old", "Old", "d", "old", 1.0, 1.5, 0.5))
    fired = eng.add_block(Block("new", "New", "d", "new", 1.0, P, 0.5)) is not None
    rows.append((label, fired, len(eng.active_contradictions())))
    say(f"      {label}: new Pi={P / 0.5:.2f} vs old 3.00, fired={fired}, contradictions left={rows[-1][2]}")
check("lower and tie-band revisions leave a live contradiction", rows[0][1:] == (False, 1) and rows[1][1:] == (False, 1))
check("control: above the margin the cascade fires and qualifies the old block", rows[2][1:] == (True, 0))
eng = ce["CascadeEngine"]()
eng.add_block(Block("a", "A", "d", "p1", 0.5, 1.0, 0.5))
eng.add_block(Block("b", "B", "d", "p2", 0.5, 1.0, 0.5))
check("A15: two fully disclosed contradicting blocks give Coh = 0 (inspectable, no floor)", eng.coherence() == 0.0)
eng = ce["CascadeEngine"]()
eng.add_block(Block("a", "A", "d", "p1", 0.5, 1.0, 0.5))
eng.add_block(Block("b", "B", "e", "p2", 0.5, 1.0, 0.5))
check("control: different domains give Coh = 1", eng.coherence() == 1.0)

# ---------------------------------------------------------------- A18 (M16)
say("A18 ANAMNESIS Theorem 3.1: a shared attractor set, different limits")
dw = lambda x: -4 * x * (x * x - 1)  # gradient of Pi(x) = -(x^2-1)^2, maxima at -1 and +1
xa, xb = -0.5, 0.5
for _ in range(2000):
    xa += 0.01 * dw(xa)
    xb += 0.01 * dw(xb)
check("two honest gradient climbers in one domain converge to different maxima", abs(xa + 1) < 1e-6 and abs(xb - 1) < 1e-6,
      f"{xa:.6f}, {xb:.6f}")
ya, yb = -0.5, 0.5
for _ in range(2000):
    ya += 0.01 * (-2 * ya)
    yb += 0.01 * (-2 * yb)
check("control: a single global maximum gives the same limit", abs(ya) < 1e-6 and abs(yb) < 1e-6)

# ---------------------------------------------------------------- A16 (M17)
say("A16 lyapunov_verification.py, run in the baseline worktree only")
if BASELINE is None:
    say("  DID NOT RUN: no baseline worktree given")
else:
    script = BASELINE / "11_MATHEMATICAL_FOUNDATIONS" / "lyapunov_verification.py"
    same_src = script.read_bytes() == (ROOT / "11_MATHEMATICAL_FOUNDATIONS/lyapunov_verification.py").read_bytes()
    check("the baseline script is byte-identical to today's", same_src)
    run = subprocess.run([sys.executable, "-B", str(script)], cwd=script.parent, capture_output=True, text=True,
                         timeout=600, env={**os.environ, "MPLBACKEND": "Agg", "PYTHONDONTWRITEBYTECODE": "1",
                                           "TMPDIR": str(SCRATCH)})
    tail = [line for line in run.stdout.splitlines() if re.search(r"(?i)pass|verified|numerical|fail|total", line)][-6:]
    say("      " + "\n      ".join(tail))
    # The function is nested inside verify_cascade_lyapunov, so lift it out of the syntax tree.
    tree = ast.parse(script.read_text(encoding="utf-8"))
    nested = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == "hess_eigenvalue_for_layer"]
    scope = {}
    if nested:
        exec(compile(ast.Module(body=nested, type_ignores=[]), str(script), "exec"), scope)
    table_vals = {layer: scope["hess_eigenvalue_for_layer"](layer) for layer in ("foundation", "theory", "edge")} \
        if nested else None
    say(f"      hess_eigenvalue_for_layer: {table_vals}")
    check("the script exits 0", run.returncode == 0, f"rc={run.returncode}")
    check("the 'Hessian eigenvalue' is a fixed per-layer table, not computed from a state",
          table_vals is not None and len(set(table_vals.values())) == 3)

# ---------------------------------------------------------------- A17 (Pi_th census)
say("A17 Pi_th census")
pat = re.compile(r"(Π_th|Pi_th|PI_TH|pi_threshold|Π_threshold)[^\n,;|(]{0,12}?(=|≈|:)\s*\*{0,2}(\d+(\.\d+)?|2√n)")
seen = {}
for path in sorted(ROOT.rglob("*")):
    if path.suffix not in {".md", ".py"} or any(part in {".git", "FOR-REVIEW", "_PROPRIETARY", "node_modules",
                                                         "review_2026_10_20"} for part in path.parts):
        continue
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        continue
    for m in pat.finditer(text):
        seen.setdefault(m.group(3), set()).add(str(path.relative_to(ROOT)))
for value in sorted(seen, key=lambda v: (v != "2√n", v)):
    files = sorted(seen[value])
    say(f"      {value}: {len(files)} files, e.g. {', '.join(files[:3])}")
check("more than one numeric Pi_th value is asserted across the corpus", len(seen) > 1, f"{len(seen)} distinct values")

say(f"\nRESULT: {'ALL CHECKS HELD' if not FAILURES else 'FAILED: ' + '; '.join(FAILURES)}")
sys.exit(1 if FAILURES else 0)
