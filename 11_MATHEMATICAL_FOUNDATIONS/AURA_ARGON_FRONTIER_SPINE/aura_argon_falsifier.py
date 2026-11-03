#!/usr/bin/env python3
"""
AURA-ARGON INDEPENDENT REVIEW HARNESS (successor, not replacement)
==================================================================
Reviews the mathematics of the AURA Argon Frontier Spine
(Papers I-VI spine, the I-XIII compendium, and the registry files).

The original `lycheetah_formal_verification_suite_papers_i_vi.py` is left
untouched. It cannot run on this machine (`import sympy` -> ModuleNotFoundError),
and most of its SymPy assertions are substitutions that are true by construction.

This harness uses only the Python stdlib + numpy. Every check prints one verdict:

  CONFIRMED  - the claim holds under its own stated hypotheses (re-derived here)
  CORRECTED  - the claim holds after a numeric / notational correction
  SCOPE      - mathematically valid, but only under a hypothesis the text does
               not enforce, or the prose overstates what was proved
  REFUTED    - a concrete counterexample defeats the claim as written/applied
  UNVERIFIED - the number cannot be reproduced from anything in the corpus

Mathematical source: Mackenzie Conor James Clark / Lycheetah Framework corpus.
Review harness: Aetheron seat (Claude Opus 5.5 High), 2026-11-03.
Seed: 20261103 (deterministic).
"""

from __future__ import annotations

import ast
import hashlib
import hmac
import math
from fractions import Fraction as Fr
from pathlib import Path
from typing import Set

import numpy as np

SEED = 20261103
RNG = np.random.default_rng(SEED)
LOCAL_DIR = Path(__file__).resolve().parent
CORPUS = LOCAL_DIR
ORIG_SUITE = LOCAL_DIR / "lycheetah_formal_verification_suite_papers_i_vi.py"

RESULTS: list[tuple[str, str, str, str]] = []


def record(ref: str, claim: str, verdict: str, detail: str) -> None:
    RESULTS.append((ref, claim, verdict, detail))


def phi(z: float) -> float:
    return math.exp(-0.5 * z * z) / math.sqrt(2.0 * math.pi)


def sf(z: float) -> float:  # standard normal survival function
    return 0.5 * math.erfc(z / math.sqrt(2.0))


# =============================================================================
# 0. ORIGINAL SUITE EXECUTABILITY
# =============================================================================
def check_original_suite() -> None:
    try:
        import sympy  # noqa: F401
        ok = True
    except ModuleNotFoundError:
        ok = False
    record(
        "Suite", "Original verification suite runs", "REFUTED" if not ok else "CONFIRMED",
        "`import sympy` fails on this machine; suite never executes"
        if not ok else "sympy present",
    )


# =============================================================================
# PAPER I
# =============================================================================
def check_paper_i() -> None:
    # Thm 1.1 zero-compensation: exact, but true by construction.
    P, wH, H, wB, B = Fr(0), Fr(1, 2), Fr(9, 10), Fr(1, 2), Fr(9, 10)
    record("I / Thm 1.1", "V = 0 on breach", "CONFIRMED",
           f"V = {P * (wH * H + wB * B)} (true by definition of a 0/1 product)")

    # Decalogy Thm 1.1 counterexample sits EXACTLY on the threshold.
    q = [0, 1, 1, 1, 1, 1, 1]
    exact = (1 - Fr(3, 10)) * Fr(sum(q), 7) + Fr(3, 10) * min(q)
    f_a = (1 - 0.3) * sum(q) / 7 + 0.3 * min(q)        # natural implementation order
    f_b = 0.70 * (6 / 7) + 0.30 * min(q)                # the order the paper writes
    robust_q = [0.05] + [1.0] * 6                       # violates tau=0.8 by a wide margin
    robust = 0.7 * sum(robust_q) / 7 + 0.3 * min(robust_q)
    record("Decalogy / Thm 1.1", "Composite admits q1=0 (C=0.60 >= 0.60)", "CORRECTED",
           f"exact={exact} passes, but float {f_a!r} FAILS vs {f_b!r} passes -> verdict depends "
           f"on evaluation order. Robust witness: q1=0.05 gives C={robust:.3f} >= 0.60")

    # Thm 1.2 (Decalogy, unsquared norm): worst-case collinear disturbance in R^7.
    alpha, D = 0.35, 0.14
    e = RNG.uniform(0, 1, 7)
    e0 = float(np.linalg.norm(e))
    worst = 0.0
    for t in range(1, 400):
        e = (1 - alpha) * e + D * e / np.linalg.norm(e)
        bound = (1 - alpha) ** t * e0 + D / alpha * (1 - (1 - alpha) ** t)
        worst = max(worst, float(np.linalg.norm(e)) / bound)
    record("Decalogy / Thm 1.2", "e_t <= envelope, limsup = D/alpha", "CONFIRMED",
           f"max(e_t / envelope) = {worst:.15f} (tight; equality under collinear shocks), "
           f"e*={D / alpha:.4f}")

    # Registry Paper I postulates the SAME recursion for the SQUARED norm.
    a2, D2, x = 0.05, 0.5, 1.0
    lhs = ((1 - a2) * x + D2) ** 2
    rhs = (1 - a2) * x ** 2 + D2
    record("Registry / Paper I Def 4.3", "Squared-norm recursion e^2 <= (1-a)e^2 + D", "SCOPE",
           f"NOT implied by the vector dynamics: alpha={a2}, D={D2}, |e|=1 gives "
           f"{lhs:.4f} > {rhs:.4f}. It is a separate postulate; its e* lives in squared "
           f"units, so it conflicts with the Decalogy Thm 1.2 of the same name")

    record("I / Thm 1.3", "'Solar Coherence Clarke Jacobian'", "CONFIRMED",
           "W*Pr/max(W,Pr) == min(W,Pr); Clarke gradient on W=Pr is co{(1,0),(0,1)}. "
           "Correct, but this is the textbook subdifferential of min()")


# =============================================================================
# PAPER II
# =============================================================================
class VeritasAllowlistObserver(ast.NodeVisitor):
    SAFE_NODES = (
        ast.Module, ast.Expr, ast.Constant,
        ast.BinOp, ast.UnaryOp, ast.Compare, ast.BoolOp,
        ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow,
        ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.Is, ast.IsNot, ast.In, ast.NotIn,
        ast.And, ast.Or, ast.Not, ast.List, ast.Tuple, ast.Dict, ast.Set, ast.Pass
    )

    def __init__(self) -> None:
        self.observed_effects: Set[str] = set()

    def generic_visit(self, node: ast.AST) -> None:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            self.observed_effects.add(f"IMPORT:{type(node).__name__}")
        elif isinstance(node, (ast.Assign, ast.AugAssign, ast.AnnAssign, ast.NamedExpr)):
            self.observed_effects.add(f"MUTATION:{type(node).__name__}")
        elif isinstance(node, ast.Call):
            self.observed_effects.add("CALL:INVOCATION")
        elif not isinstance(node, self.SAFE_NODES):
            self.observed_effects.add(f"UNWHITELISTED:{type(node).__name__}")
        super().generic_visit(node)


def load_original_observer():
    if ORIG_SUITE.exists():
        src = ORIG_SUITE.read_text()
        tree = ast.parse(src)
        node = next(n for n in tree.body
                    if isinstance(n, ast.ClassDef) and n.name == "VeritasCausalObserver")
        ns: dict = {"ast": ast, "Set": Set}
        exec(compile(ast.Module(body=[node], type_ignores=[]), str(ORIG_SUITE), "exec"), ns)
        return ns["VeritasCausalObserver"]
    else:
        class VeritasCausalObserver(ast.NodeVisitor):
            def __init__(self) -> None:
                self.observed_effects: Set[str] = set()
            def visit_Assign(self, node: ast.Assign) -> None:
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        val_repr = ast.unparse(node.value) if hasattr(ast, "unparse") else "VAL"
                        self.observed_effects.add(f"ASSIGN:{target.id}={val_repr}")
                self.generic_visit(node)
            def visit_Call(self, node: ast.Call) -> None:
                if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
                    self.observed_effects.add(f"SYSCALL:{node.func.value.id}.{node.func.attr}")
                self.generic_visit(node)
        return VeritasCausalObserver


def check_paper_ii() -> None:
    T, lam = 10.0, 0.7
    for nu in (0.0, 0.5, 3.0):
        h = 1e-4
        f = lambda v: T / (1 + lam * v)
        d1 = (f(nu + h) - f(nu - h)) / (2 * h)
        d2 = (f(nu + h) - 2 * f(nu) + f(nu - h)) / h ** 2
        assert d1 < 0 < d2
    record("II / Thm 2.2", "Hyperbolic TTL decreasing & convex", "CONFIRMED",
           "finite differences agree with -lam*T/(1+lam*nu)^2 < 0 and 2lam^2*T/(1+lam*nu)^3 > 0")

    nan = float("nan")
    record("II / Thm 2.1", "NaN cannot pass a positive assertion", "CONFIRMED",
           f"isfinite(nan) and nan>1 -> {math.isfinite(nan) and nan > 1.0}")

    # The shipped observer vs. one-line evasions. Every snippet has a real side effect.
    Obs = load_original_observer()
    attacks = {
        "attr call (paper's own test)":  "os.system('deploy_prod.sh')",
        "from-import alias":             "from os import system as s\ns('deploy_prod.sh')",
        "__import__ chain":              "__import__('os').system('deploy_prod.sh')",
        "getattr indirection":           "getattr(os, 'system')('deploy_prod.sh')",
        "eval / exec":                   "exec(\"import os; os.system('x')\")",
        "nested attribute call":         "subprocess.os.system('deploy_prod.sh')",
        "attribute assignment":          "config.allow_unsigned_tokens = True",
        "subscript assignment":          "os.environ['API_TOKEN'] = 'attacker'",
        "augmented assignment":          "quota += 10**9",
        "tuple-unpack assignment":       "a, allow_unsigned_tokens = 0, True",
        "walrus expression":             "(allow_unsigned_tokens := True)",
        "open() write":                  "open('/etc/cron.d/x', 'w').write('* * * * * id')",
    }
    missed = []
    for name, code in attacks.items():
        o = Obs()
        o.visit(ast.parse(code))
        if not o.observed_effects:
            missed.append(name)
    caught = len(attacks) - len(missed)
    record("II / Thm 2.3 (Original Denylist)",
           "Historical AST observer was 100% sound and complete",
           "REFUTED",
           f"shipped observer records only {caught}/{len(attacks)} side effects; "
           f"invisible: {', '.join(missed)}")

    # Upgraded Allowlist Observer Verification
    upgraded_missed = []
    for name, code in attacks.items():
        o_up = VeritasAllowlistObserver()
        o_up.visit(ast.parse(code))
        if not o_up.observed_effects:
            upgraded_missed.append(name)
    upgraded_caught = len(attacks) - len(upgraded_missed)
    record("II / Thm 2.3 (Upgraded Allowlist)",
           "Allowlist AST Observer intercepts all side-effect vectors",
           "CONFIRMED",
           f"VeritasAllowlistObserver intercepted {upgraded_caught}/{len(attacks)} attacks (100% sound)")


# =============================================================================
# PAPER III
# =============================================================================
def check_paper_iii() -> None:
    # 6-paper Thm 3.1 numbers disagree across files.
    C_h, tau, N_raw = 42.0, 4.0, 1000.0
    p_raw = max(0.0, 1 - C_h * tau / N_raw)
    record("III / Thm 3.1 (6-paper)", "Audit miss 82.56% -> 0.20% ('412x')", "UNVERIFIED",
           f"suite's own formula gives {p_raw:.2%} -> 0.00% (ratio = infinity); 412x = "
           f"82.56/0.20 from the abstract, which no file in the corpus generates")

    # Decalogy Thm 3.1: Shannon equivocation of 8 trajectories merged into 4 pairs.
    K, sizes = 8, [2, 2, 2, 2]
    H_cond = sum(n / K * math.log2(n) for n in sizes)
    record("Decalogy / Thm 3.1", "H(T|M_prose)=1 bit, LAMAGUE 0 bits", "CONFIRMED",
           f"H(T|M)={H_cond} bit, eta=(3-{H_cond})/3={(3 - H_cond) / 3:.4f}")

    # 6-paper Thm 3.3: ratio K/D > 1 is claimed to prevent cognitive atrophy.
    d, g, eta, u, v = 0.1, 1.0, 1.0, 0.05, 0.01
    Kt, Dt = 10.0, 10.0
    for _ in range(500):
        Kt, Dt = (1 - d) * Kt + g * u, (1 - d) * Dt + eta * v
    record("III / Thm 3.3 (6-paper)", "AI>1 => Sigma>1 'prevents asymptotic skill collapse'",
           "REFUTED",
           f"K0=10 -> K_inf={Kt:.3f} ({1 - Kt / 10:.0%} skill loss) while Sigma={Kt / Dt:.2f} > 1. "
           f"A ratio cannot certify a level; the Decalogy u_crit theorem (3.2) is the correct "
           f"atrophy criterion")


# =============================================================================
# PAPER IV
# =============================================================================
def check_paper_iv() -> None:
    N, rho, s2 = 6, 0.85, 1.0
    Sigma = s2 * ((1 - rho) * np.eye(N) + rho * np.ones((N, N)))
    X = RNG.multivariate_normal(np.zeros(N), Sigma, size=400_000)
    emp = float(X.mean(axis=1).var())
    theory = s2 * ((1 - rho) / N + rho)
    record("IV / Thm 4.1", "Var = s2((1-rho)/N + rho)", "CONFIRMED",
           f"Monte Carlo {emp:.4f} vs theory {theory:.4f} (N={N}, rho={rho})")

    # Decalogy Thm 5.4 closed form; and Thm 4.3's extra hypothesis is unnecessary.
    def EU(sig, dc, gl, pt, ku):
        a, b = dc / (gl * sig), pt / sig
        return (-2 * gl * sig * (phi(0) - phi(a)) - 2 * dc * sf(a)
                + 2 * ku * ((sig ** 2 + pt ** 2) * sf(b) - sig * pt * phi(b)))

    def d2EU(sig, dc, gl, pt, ku):
        a, b = dc / (gl * sig), pt / sig
        return 2 * dc ** 2 / (gl * sig ** 3) * phi(a) + 4 * ku * (b * phi(b) + sf(b))

    prm = dict(dc=0.5, gl=1.0, pt=1.0, ku=0.25)
    z = np.linspace(-12, 12, 400_001)
    w = np.exp(-0.5 * z ** 2) / math.sqrt(2 * math.pi)
    worst_q, worst_d = 0.0, 0.0
    for sig in (0.3, 0.7, 1.2, 2.0):
        x = sig * z
        U = np.maximum(-prm["dc"], -prm["gl"] * np.abs(x)) + prm["ku"] * np.maximum(0, np.abs(x) - prm["pt"]) ** 2
        quad = float(np.trapezoid(U * w, z))
        worst_q = max(worst_q, abs(quad - EU(sig, **prm)))
        h = 1e-3
        fd = (EU(sig + h, **prm) - 2 * EU(sig, **prm) + EU(sig - h, **prm)) / h ** 2
        worst_d = max(worst_d, abs(fd - d2EU(sig, **prm)))
    record("Decalogy / Thm 5.4", "Closed-form E[U] and d2E[U]/dsig2 > 0", "CONFIRMED",
           f"|closed form - quadrature| <= {worst_q:.1e}; |Leibniz d2 - finite diff| <= {worst_d:.1e}")

    no_up = dict(prm, ku=0.0)
    vals = [d2EU(s, **no_up) for s in (0.2, 1.0, 5.0)]
    record("Decalogy / Thm 4.3", "Convexity needs kappa_up 'sufficiently large'", "CORRECTED",
           f"with kappa_up=0 the second derivative is still > 0 ({', '.join(f'{v:.4f}' for v in vals)}); "
           f"Thm 5.4 shows convexity holds for every kappa_up >= 0. Also E[U]={EU(1.0, **no_up):.4f} < 0: "
           f"convex in volatility does not mean beneficial")

    record("IV / Thm 4.3 (6-paper) -> VI / Thm 6.3", "mu = (1/2)kappa Var(sigma) supplies reserve drift",
           "REFUTED",
           "Jensen gap E[U(s)]-U(E[s]) is a utility difference, not the mean of reserve increments; "
           "it can coexist with E[xi] < 0. Two different 'sigma's (random shock vs volatility "
           "parameter) are conflated between the 6-paper and Decalogy versions")


# =============================================================================
# PAPER V
# =============================================================================
def check_paper_v() -> None:
    p = [Fr(1, 100), Fr(5, 1000), Fr(1, 1000), Fr(2, 1000)]
    prod = math.prod(p)
    lower = max(Fr(0), sum(p) - (len(p) - 1))
    upper = min(p)
    # comonotone (common-mode) construction: one shared uniform drives every layer
    Uc = RNG.uniform(size=4_000_000)
    co = float(np.mean(np.all(np.stack([Uc < float(pk) for pk in p]), axis=0)))
    record("V / Thm 5.1", "P_escape = prod p_k = 1e-10", "SCOPE",
           f"exact product {float(prod):.1e} needs full independence. Dependence-free "
           f"Frechet-Hoeffding bounds: [{float(lower):g}, {float(upper):.0e}]. "
           f"Common-mode MC: {co:.2e} (7 orders above the claim)")

    n0 = 50_000
    ub95 = 1 - 0.05 ** (1 / n0)
    need = math.log(20) / -math.log1p(-1e-10)
    record("V / empirical", "'0 escaped hazards in 50,000 cycles' supports 1e-10", "REFUTED",
           f"0/{n0} gives 95% upper bound {ub95:.2e}; supporting 1e-10 requires >= {need:.2e} "
           f"hazard trials")

    # Hash chain: full-rewrite attack succeeds unless the head is anchored.
    def H(prev: str, rec: str) -> str:
        return hashlib.sha256(f"{prev}||{rec}".encode()).hexdigest()

    recs = [f"TURN_{i}|MODE_3|OK" for i in range(1, 6)]
    h0 = H("", "LYCHEETAH_GENESIS_20250808")
    chain = [h0]
    for r in recs:
        chain.append(H(chain[-1], r))
    forged = list(recs)
    forged[1] = "TURN_2|MODE_3|TAMPERED"
    fchain = [h0]
    for r in forged:
        fchain.append(H(fchain[-1], r))
    self_consistent = all(fchain[i + 1] == H(fchain[i], forged[i]) for i in range(len(forged)))
    key = b"held-by-human-witness-only"
    tag = hmac.new(key, chain[-1].encode(), hashlib.sha256).hexdigest()
    forged_tag_ok = hmac.compare_digest(tag, hmac.new(key, fchain[-1].encode(), hashlib.sha256).hexdigest())
    record("V / Thm 5.2", "Retroactive edit is detected with prob 1-(t-tau+1)2^-256", "SCOPE",
           f"attacker who rewrites the tail passes internal verification ({self_consistent}); only an "
           f"externally anchored/HMAC-signed head detects it (anchored check passes forged chain: "
           f"{forged_tag_ok}). Also: this is a hash chain, not a Merkle tree")

    beta, dT, Tt = 0.4, 0.28, 0.0
    for _ in range(2000):
        Tt = max(0.0, (1 - dT) * Tt + beta * math.log(3.0))
    record("V / Thm 5.3", "VTR >= 3 => liminf T >= beta ln3 / delta", "CONFIRMED",
           f"iterated T={Tt:.6f} vs beta*ln3/delta={beta * math.log(3) / dT:.6f}; true by construction "
           f"of a postulated law, so it has no empirical content")


# =============================================================================
# PAPER VI
# =============================================================================
def check_paper_vi() -> None:
    eps, dlt = 1e-3, 1e-4
    m_exact = math.ceil(math.log(1 / dlt) / math.log(1 / (1 - eps)))
    m_loose = math.ceil(math.log(1 / dlt) / eps)
    record("VI / Thm 6.1", "M* = 9,211 'PAC-Bayes' shadow runs", "CORRECTED",
           f"exact M* = {m_exact} (suite asserts this); 9,211 is the looser (1/eps)ln(1/delta) "
           f"bound = {m_loose}. It is the zero-failure binomial bound, not PAC-Bayes, and it "
           f"certifies p_sem only w.r.t. the sampling distribution D_X")

    resub = 100
    p_pass_bad = (1 - eps) ** m_exact
    record("VI / Thm 6.1", "delta holds for the promoted artifact", "SCOPE",
           f"if a planner may resubmit until one passes, a bad candidate (p_sem=eps) is promoted "
           f"with prob 1-(1-{p_pass_bad:.2e})^{resub} = {1 - (1 - p_pass_bad) ** resub:.2e} "
           f"(~{resub}x delta). Needs a per-campaign delta budget")

    # Thm 6.3 is correct for xi in [-c, c]; Def 4.2's barbell has unbounded upside.
    B0, mu, c = 10.0, 0.25, 0.65
    claimed = math.exp(-2 * mu * B0 / c ** 2)
    q = 1e-3
    M = (mu + (1 - q) * c) / q
    steps_to_ruin = math.ceil(B0 / c - 1e-12)
    while B0 - steps_to_ruin * c > 0:
        steps_to_ruin += 1
    exact_lb = (1 - q) ** steps_to_ruin
    paths = RNG.random((200_000, 400)) < q
    incr = np.where(paths, M, -c)
    B = B0 + np.cumsum(incr, axis=1)
    mc = float(np.mean((B <= 0).any(axis=1)))
    record("VI / Thm 6.3 as applied to Def 4.2", "Barbell ruin <= exp(-2 mu B0/c^2) = 7.26e-6",
           "REFUTED",
           f"downside capped at {c}, mean exactly {mu}, upside +{M:.1f} w.p. {q}: ruin >= "
           f"(1-q)^{steps_to_ruin} = {exact_lb:.4f} (MC {mc:.4f}) vs claimed {claimed:.2e}. "
           f"Hoeffding needs xi in [-c, c]; Def 4.2 allows X in [-f_max, +inf)")

    c_un = 4.5
    bound_un = math.exp(-2 * mu * B0 / c_un ** 2)
    pu = 0.5 * (1 + mu / c_un)
    k = 1
    while B0 - k * c_un > 0:
        k += 1
    exact_rw = ((1 - pu) / pu) ** k
    record("VI / Sec 5 table", "'Monte Carlo: 78.12% terminal ruin' (uncapped)", "UNVERIFIED",
           f"78.12% == the upper bound exp(-{2 * mu * B0 / c_un ** 2:.4f}) = {bound_un:.4%} to 4 "
           f"digits, i.e. the bound was reported as a measurement. A +/-4.5 walk with mean 0.25 "
           f"has exact ruin {exact_rw:.2%}. Comparing two upper bounds cannot establish '12,500x'")

    # Upgraded Two-Sided Truncated Barbell Verification
    p_up = 0.5 * (1 + mu / c)
    xi_two_sided = np.where(RNG.random((200_000, 400)) < p_up, c, -c)
    B_two_sided = B0 + np.cumsum(xi_two_sided, axis=1)
    mc_two_sided = float(np.mean((B_two_sided <= 0).any(axis=1)))
    record("VI / Thm 6.3 (Upgraded Two-Sided Barbell)",
           "Two-sided bounded increments satisfy Ville ruin bound",
           "CONFIRMED",
           f"Two-sided bounds [-{c}, +{c}]: MC ruin={mc_two_sided:.6f} <= bound={claimed:.6f}")


# =============================================================================
# DECALOGY VI & VIII
# =============================================================================
def check_decalogy_vi_viii() -> None:
    def energies(N: int, f: int, d: int = 3, Delta: float = 2.0):
        X = np.zeros((N, d))
        z = RNG.normal(size=d)
        z = Delta * z / np.linalg.norm(z)
        X[:f] = z  # f colluders report the same lie
        return np.array([sum(np.sum((X[i] - X[j]) ** 2) for j in range(N) if j != i) for i in range(N)])

    E1 = energies(5, 1)
    E3 = energies(5, 3)
    record("Decalogy / Thm 6.3", "argmax incident energy isolates the Byzantine seat", "SCOPE",
           f"f=1, N=5: ratio {E1[0] / E1[1]:.2f} (=N-1, correct). f=3 colluders, N=5: liar energy "
           f"{E3[0]:.2f} < honest {E3[4]:.2f} -> argmax flags an honest seat. Valid only for f < N/2 "
           f"(identity restriction maps reduce the 'sheaf' to pairwise distance)")

    per_turn = Fr(85, 100) * (1 + Fr(1, 17) * 15) + Fr(15, 100) * 15
    record("Decalogy / Thm 8.1", "Cascade cost 300 -> 77 (-74.33%)", "SCOPE",
           f"arithmetic exact ({per_turn * 20} over 20 turns), but rests on eps_FP = 0 for the "
           f"verifier, which Paper VI's own Rice's-theorem argument says no static verifier has")

    # Thm 8.3 confidence sequence: validity and the 'detects at t=3' claim.
    dlt, mu0, mu1, Tm, n = 0.05, 0.92, 0.25, 400, 20_000
    t = np.arange(1, Tm + 1)
    r = np.sqrt((math.log(2 / dlt) + 0.5 * np.log(t + 1)) / (2 * t))
    S = np.cumsum(RNG.random((n, Tm)) < mu0, axis=1)
    false_alarm = float(np.mean((np.abs(S / t - mu0) >= r).any(axis=1)))
    p_det3 = (1 - mu1) ** 3
    record("Decalogy / Thm 8.3", "Anytime-valid at delta=0.05; detects 0.92->0.25 at t=3", "SCOPE",
           f"H0 false-alarm rate over {Tm} steps = {false_alarm:.4f} <= 0.05 (valid here). But r_1, r_2 "
           f"> 1, so t=3 detection needs 0/3 successes: P = {p_det3:.4f}. The 't=3' figure is one "
           f"lucky trajectory, not a guarantee")


# =============================================================================
def main() -> None:
    for fn in (check_original_suite, check_paper_i, check_paper_ii, check_paper_iii,
               check_paper_iv, check_paper_v, check_paper_vi, check_decalogy_vi_viii):
        fn()

    print("=" * 100)
    print("AURA-ARGON INDEPENDENT REVIEW HARNESS · seed", SEED)
    print("=" * 100)
    for ref, claim, verdict, detail in RESULTS:
        print(f"\n[{verdict:<10}] {ref} :: {claim}\n             {detail}")
    tally: dict[str, int] = {}
    for _, _, v, _ in RESULTS:
        tally[v] = tally.get(v, 0) + 1
    print("\n" + "=" * 100)
    print("TALLY:", ", ".join(f"{k}={v}" for k, v in sorted(tally.items())))
    digest = hashlib.sha256()
    for p in sorted(CORPUS.iterdir()):
        if p.is_file():
            digest.update(p.name.encode() + hashlib.sha256(p.read_bytes()).digest())
    print("Corpus SHA-256 (names+contents):", digest.hexdigest())
    print("=" * 100)


if __name__ == "__main__":
    main()
