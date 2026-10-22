"""Batch 12 (RV13, part 1): runtime-boundary probes for 12_IMPLEMENTATIONS.

Usage:
  python3 -B repro_batch12.py <repo>              probe the working tree
  python3 -B repro_batch12.py <repo> --ref <sha>  probe a committed tree (git archive)

Every probe runs on a temporary copy of 12_IMPLEMENTATIONS/ and lycheetah/; the
repository is never written. Each output line is one JSON observation. A probe
that raises records the refusal as its observation; a probe that cannot start
records DID NOT RUN, never PASS.

Families:
  W  triad_wuwei admission of NaN/inf/shape/modulator values, step atomicity
  T  tri_axial_checker TES input range, hedge proxy, demo() stdout rebinding
  S  import-time stdout mutation by seven core modules (StringIO, ascii, None)
  M  sol_workspace_mcp task-board and version writes, MCP error semantics
  G  lycheetah_guard_mcp import modes, lexicon phrases, MCP availability
  L  census: multi-word lexicon entries compared against whitespace tokens
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import io
import json
import math
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import textwrap
import warnings
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("repo")
ap.add_argument("--ref", help="git ref to probe instead of the working tree")
args = ap.parse_args()

REPO = Path(args.repo).resolve()
TMP = Path(tempfile.mkdtemp(prefix="rv13_b12_"))
IMPL = TMP / "12_IMPLEMENTATIONS"
CORE, APPS = IMPL / "core", IMPL / "applications"
ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", MPLBACKEND="Agg", PYTHONIOENCODING="utf-8")
STDOUT_MODULES = ["triad_wuwei", "harmonia_calculator", "calibrate_master_equation", "sovereign_pipeline",
                  "aura_score_hexie", "triad_tracker", "microorcim_tracker"]

warnings.simplefilter("ignore")


def emit(pid, **fields):
    print(json.dumps({"id": pid, **fields}, default=str), flush=True)


def probe(pid, fn):
    try:
        out = fn()
    except Exception as exc:  # the refusal itself is the observation
        out = {"raised": f"{type(exc).__name__}: {str(exc)[:140]}"}
    emit(pid, **out)


def run_py(code, *argv, cwd=None):
    return subprocess.run([sys.executable, "-B", "-c", code, *argv], cwd=cwd or TMP, env=ENV,
                          capture_output=True, text=True, timeout=180)


def last_json(proc):
    try:
        return json.loads(proc.stdout.strip().splitlines()[-1])
    except (IndexError, json.JSONDecodeError):
        return {"DID NOT RUN": (proc.stderr.strip().splitlines() or ["no output"])[-1][:120]}


def materialize():
    if args.ref:
        tar = subprocess.run(["git", "-C", str(REPO), "archive", "--format=tar", args.ref,
                              "12_IMPLEMENTATIONS", "lycheetah", "pyproject.toml"],
                             capture_output=True, check=True).stdout
        with tarfile.open(fileobj=io.BytesIO(tar)) as t:
            t.extractall(TMP, filter="data")
    else:
        for d in ("12_IMPLEMENTATIONS", "lycheetah"):
            shutil.copytree(REPO / d, TMP / d, ignore=shutil.ignore_patterns("__pycache__", "node_modules"))
        shutil.copy2(REPO / "pyproject.toml", TMP / "pyproject.toml")


# ── W: triad_wuwei ───────────────────────────────────────────────────────────

def family_w():
    import numpy as np
    import triad_wuwei as tw
    np.seterr(all="ignore")
    one, nan, inf = np.array([1.0]), math.nan, math.inf

    probe("W1 gamma, NaN intervention", lambda: {"gamma": tw.grain_alignment(np.array([nan]), one)})
    probe("W2 gamma, NaN restoration", lambda: {"gamma": tw.grain_alignment(np.array([0.3]), np.array([nan]))})

    def w3():
        t = tw.WuweiTriad(mu=1.0)
        s = t.step(state=one, intervention=np.array([0.3]), restoration=np.array([nan]))
        honest = tw.WuweiTriad(mu=1.0).step(state=one, intervention=np.array([0.3]), restoration=np.array([-1.0]))
        return {"gamma": s.gamma, "h": s.h, "wuwei_delta": s.wuwei_debt_delta, "coherent": s.is_wuwei_coherent(),
                "same_step_with_finite_R": {"gamma": honest.gamma, "wuwei_delta": honest.wuwei_debt_delta,
                                            "coherent": honest.is_wuwei_coherent()}}
    probe("W3 forcing step with NaN restoration", w3)

    def w3b():
        t = tw.WuweiTriad(mu=1.0)
        try:
            t.step(one, np.array([0.3]), restoration=np.array([nan]))
            refused = False
        except ValueError:
            refused = True
        return {"refused": refused, "history": len(t.history), "std_debt": t.standard_debt, "wuwei_debt": t.wuwei_debt}
    probe("W3b ledger after NaN restoration step", w3b)

    def w4():
        t = tw.WuweiTriad(mu=1.0)
        t.step(one, np.array([inf]), restoration=np.array([-1.0]))
        return {"std_debt": t.standard_debt, "wuwei_debt": t.wuwei_debt, "history": len(t.history)}
    probe("W4 infinite intervention", w4)

    def w5():
        out = {}
        for label, kw in [("mu=nan", {"mu": nan}), ("mu=inf", {"mu": inf}), ("k_cost=nan", {"k_cost": nan}),
                          ("theta=nan", {"theta_wuwei": nan}), ("theta=5", {"theta_wuwei": 5.0})]:
            try:
                tw.WuweiTriad(**kw)
                out[label] = "accepted"
            except ValueError:
                out[label] = "refused"
        return out
    probe("W5 constructor parameters", w5)

    def w6():
        out = {}
        for label, a in [("gamma=-2,p=2.5", (-2.0, 2.5)), ("gamma=0,p=nan", (0.0, nan)), ("gamma=nan,p=2", (nan, 2.0))]:
            try:
                out[label] = repr(tw.grain_cost_modulator_bounded(*a))
            except (ValueError, OverflowError) as exc:
                out[label] = f"refused ({type(exc).__name__})"
        return out
    probe("W6 bounded modulator domain", w6)

    def w7():
        out = {}
        for label, a in [("gamma=0,mu=nan", (0.0, nan)), ("gamma=nan,mu=1", (nan, 1.0)), ("gamma=-1,mu=1000", (-1.0, 1000.0))]:
            try:
                out[label] = repr(tw.grain_cost_modulator_exp(*a))
            except (ValueError, OverflowError) as exc:
                out[label] = f"refused ({type(exc).__name__})"
        return out
    probe("W7 exponential modulator domain", w7)

    def w8():
        t = tw.WuweiTriad()
        try:
            t.step(np.array([1.0, 2.0, 3.0]), np.array([0.3]), restoration=np.array([-1.0]))
            verdict = "accepted"
        except ValueError:
            verdict = "refused"
        return {"state_dim3_intervention_dim1": verdict, "history": len(t.history)}
    probe("W8 state/intervention dimension mismatch", w8)

    def w9():
        out = {}
        for label, fn in [("h=-1", lambda g: -1.0), ("h=nan", lambda g: nan)]:
            t = tw.WuweiTriad(modulator=fn)
            try:
                t.step(one, np.array([0.3]), restoration=np.array([-1.0]))
                out[label] = {"accepted": True, "wuwei_debt": t.wuwei_debt}
            except ValueError:
                out[label] = {"accepted": False, "wuwei_debt": t.wuwei_debt, "history": len(t.history)}
        return out
    probe("W9 custom modulator output", w9)

    def cw():
        a = tw.WuweiTriad(mu=1.0)
        s1 = a.step(one, np.array([-0.3]), restoration=np.array([-1.0]))
        b = tw.WuweiTriad(mu=1.0)
        s2 = b.step(one, np.array([0.3]), restoration=np.array([-1.0]))
        z = tw.WuweiTriad(mu=0.0)
        z.step(one, np.array([-0.5]), restoration=np.array([-1.0]))
        z.step(one, np.array([0.5]), restoration=np.array([-1.0]))
        at = tw.WuweiTriad(mu=1.0).step(np.array([0.0]), np.array([0.1]), restoration=np.array([0.0]))
        return {"ratio": round(s2.wuwei_debt_delta / s1.wuwei_debt_delta, 6), "e2": round(math.exp(2), 6),
                "aligned_coherent": s1.is_wuwei_coherent(), "forced_coherent": s2.is_wuwei_coherent(),
                "mu0_divergence": z.report().divergence(), "attractor_gamma_h": [at.gamma, at.h]}
    probe("CW control: T-4 section V example, mu=0, attractor", cw)


# ── T: tri_axial_checker ─────────────────────────────────────────────────────

def family_t():
    import tri_axial_checker as ta
    c = ta.TriAxialChecker()

    def tes(h, d):
        r = c.compute_tes(h_output=h, drift=d)
        return {"score": round(r.score, 6), "status": r.status.value}
    probe("T1 TES with drift=-1.0", lambda: tes(0.0, -1.0))
    probe("T1b TES with h_output=-0.5", lambda: tes(-0.5, 0.2))
    probe("T2 control: TES saturates h_output=5.0 at the maximum penalty", lambda: tes(5.0, 0.0))
    probe("T2b control: TES at h=1,d=1", lambda: tes(1.0, 1.0))
    e = ta.TriAxialChecker.estimate_output_entropy
    probe("T3 hedge 'I think'", lambda: {"h": e("I think it works.")})
    probe("T4 hedge with punctuation 'Maybe,'", lambda: {"h": e("Maybe, it works.")})
    probe("T5 control: confident text", lambda: {"h": e("The proof uses the Banach fixed-point theorem.")})

    code = ("import sys; sys.path.insert(0, sys.argv[1]); import tri_axial_checker as t; "
            "t.demo(); t.demo(); sys.stderr.write('SECOND-DEMO-RETURNED\\n')")
    p = run_py(code, str(CORE))
    emit("T6 demo() called twice in one process", returncode=p.returncode,
         second_returned="SECOND-DEMO-RETURNED" in p.stderr,
         banners=p.stdout.count("TRI-AXIAL CONSTITUTIONAL METRICS CHECKER"),
         stderr_tail=[ln[:110] for ln in p.stderr.strip().splitlines()[-2:]])


# ── S: import-time stdout mutation ───────────────────────────────────────────

S_CODE = textwrap.dedent('''
    import contextlib, io, json, sys
    mod, mode = sys.argv[1], sys.argv[2]
    sys.path[:0] = sys.argv[3:]
    res = {}
    def attempt():
        try:
            __import__(mod)
            return "ok"
        except Exception as e:
            return f"{type(e).__name__}: {e}"[:110]
    if mode == "stringio":
        with contextlib.redirect_stdout(io.StringIO()):
            res["import"] = attempt()
    elif mode == "ascii":
        real, stream = sys.stdout, io.TextIOWrapper(io.BytesIO(), encoding="ascii")
        sys.stdout = stream
        try:
            res["import"] = attempt()
        finally:
            sys.stdout = real
        res["host_stream_encoding_after_import"] = stream.encoding
    else:
        real = sys.stdout
        sys.stdout = None
        try:
            res["import"] = attempt()
        finally:
            sys.stdout = real
    print(json.dumps(res))
''')


def family_s():
    for m in STDOUT_MODULES:
        row = {mode: last_json(run_py(S_CODE, m, mode, str(CORE), str(IMPL), str(APPS)))
               for mode in ("stringio", "ascii", "none")}
        emit(f"S {m}", **row)


# ── M: sol_workspace_mcp ─────────────────────────────────────────────────────

BOARD = """# TASKS

Last issued id: **#91** (current high-water mark)

## GATE 3 — Ship

| # | Task | File | Fable | Status |
|---|---|---|---|---|
| 90 | Wire the door | app/door.tsx | — | **open** |
| 91 | Paint the sky | app/sky.tsx | — | ✅ done |

## GATE 4 — Next

| # | Task | File | Fable | Status |
|---|---|---|---|---|
| 85 | Tune the bell | | — | **open** |

## POST-LAUNCH

| # | Task | File | Fable | Status |
|---|---|---|---|---|
| 80 | Retro | | — | ✅ done |
"""
NO_HWM = (BOARD.replace("Last issued id: **#91** (current high-water mark)\n\n", "")
          .replace("| 91 | Paint the sky | app/sky.tsx | — | ✅ done |\n",
                   "| 91 | Paint the sky | app/sky.tsx | — | ✅ done |\n| 92 | Hang the lamp | | — | ✅ done |\n"))
EMPTY_POST = BOARD.replace("| 80 | Retro | | — | ✅ done |\n", "")


def family_m():
    import sol_workspace_mcp as sw

    def board(case, text=BOARD):
        d = TMP / "ws" / case
        d.mkdir(parents=True)
        (d / "TASKS.md").write_text(text, encoding="utf-8")
        sw.TASKS_MD, sw.APP_JSON, sw.SETTINGS_TSX = d / "TASKS.md", d / "app.json", d / "settings.tsx"
        return d

    def tasks(d):
        return sw._parse_tasks((d / "TASKS.md").read_text(encoding="utf-8"))

    def dups(d):
        ids = [t["id"] for t in tasks(d)]
        return sorted({i for i in ids if ids.count(i) > 1})

    def app(d, version="9.1.0", tsx='export const LABEL = "Sol v9.1.0";\n'):
        (d / "app.json").write_text(json.dumps({"expo": {"name": "Sol", "version": version}}, indent=2) + "\n",
                                    encoding="utf-8")
        if tsx is not None:
            (d / "settings.tsx").write_text(tsx, encoding="utf-8")

    def versions(d):
        tsx = d / "settings.tsx"
        return {"app_json": json.loads((d / "app.json").read_text(encoding="utf-8"))["expo"]["version"],
                "settings_tsx": tsx.read_text(encoding="utf-8").strip() if tsx.exists() else None}

    def attempt(fn, *a):
        try:
            return {"reply": fn(*a).splitlines()[0][:90]}
        except Exception as exc:
            return {"refused": f"{type(exc).__name__}: {str(exc)[:90]}"}

    def m1():
        d = board("m1")
        replies = [attempt(sw.add_task_impl, f"Task {k}", "3") for k in range(3)]
        return {"replies": replies, "duplicate_ids_in_board": dups(d)}
    probe("M1 three add_task calls", m1)

    def m2():
        d = board("m2", NO_HWM)
        return {**attempt(sw.add_task_impl, "Guess my id", "3"), "duplicate_ids_in_board": dups(d)}
    probe("M2 add_task on a board with no high-water mark (id 92 already used)", m2)

    def m3():
        d = board("m3")
        sw.add_task_impl("Place me", "3")
        lines = (d / "TASKS.md").read_text(encoding="utf-8").splitlines()
        i = next(k for k, ln in enumerate(lines) if "Place me" in ln)
        return {"line_before_new_row": lines[i - 1], "line_after_new_row": lines[i + 1] if i + 1 < len(lines) else None}
    probe("M3 placement of the new row", m3)

    def m4():
        d = board("m4")
        out = attempt(sw.add_task_impl, "Fix a | b", "3")
        new = [t for t in tasks(d) if t["id"] == 92]
        return {**out, "parsed_new_row": new}
    probe("M4 subject containing a pipe", m4)

    def m5():
        d = board("m5")
        out = attempt(sw.add_task_impl, "Real task |  | — | **open** |\n| 999 | Injected by tool input", "3")
        return {**out, "open_ids": [t["id"] for t in tasks(d) if t["status"] == "open"]}
    probe("M5 subject containing a newline", m5)

    def m6():
        d = board("m6")
        out = attempt(sw.add_task_impl, "Where am I", "5")
        return {**out, "landed_in": [t["gate"] for t in tasks(d) if t["task"] == "Where am I"]}
    probe("M6 unknown gate '5'", m6)

    def m6b():
        d = board("m6b", EMPTY_POST)
        out = attempt(sw.add_task_impl, "First post-launch task", "post")
        return {**out, "landed_in": [t["gate"] for t in tasks(d) if t["task"] == "First post-launch task"]}
    probe("M6b first task into an empty POST-LAUNCH table", m6b)

    def m7():
        d = board("m7")
        app(d)
        return {**attempt(sw.bump_version_impl, "banana"), **versions(d)}
    probe("M7 bump_version('banana')", m7)

    def m8():
        d = board("m8")
        app(d, tsx='export const LABEL = "Sol";\n')
        return {**attempt(sw.bump_version_impl, "patch"), **versions(d)}
    probe("M8 bump when settings.tsx holds no version", m8)

    def m9():
        d = board("m9")
        app(d, tsx='// built against sdk v51.0.0\nexport const LABEL = "Sol v9.1.0";\n')
        return {**attempt(sw.bump_version_impl, "patch"), **versions(d)}
    probe("M9 bump when settings.tsx holds an earlier unrelated version", m9)

    def m10():
        d = board("m10")
        app(d, tsx=None)
        return {**attempt(sw.bump_version_impl, "patch"), **versions(d)}
    probe("M10 bump when settings.tsx is missing", m10)

    def m11():
        if not getattr(sw, "MCP_AVAILABLE", False):
            return {"status": "DID NOT RUN", "reason": "mcp low-level Server API unavailable"}
        import anyio
        from mcp.shared.memory import create_connected_server_and_client_session
        d = board("m11")

        async def go():
            with anyio.fail_after(30):
                async with create_connected_server_and_client_session(sw.build_server()) as client:
                    sw.TASKS_MD = d / "MISSING.md"
                    r1 = await client.call_tool("complete_task", {"task_id": 5})
                    sw.TASKS_MD = d / "TASKS.md"
                    r2 = await client.call_tool("add_task", {"subject": "x", "gate": "5"})
                    return r1, r2
        r1, r2 = anyio.run(go)
        return {"missing_board": {"isError": r1.isError, "text": r1.content[0].text[:80]},
                "unknown_gate": {"isError": r2.isError, "text": r2.content[0].text[:80]}}
    probe("M11 MCP protocol: isError on a failed tool call", m11)


# ── G: lycheetah_guard_mcp ───────────────────────────────────────────────────

G_CODE = textwrap.dedent('''
    import json, sys
    sys.path[:0] = [sys.argv[1], sys.argv[2]]
    import applications.lycheetah_guard_mcp as g
    out = {"MCP_AVAILABLE": g.MCP_AVAILABLE}
    try:
        out["verify_empty_object"] = g.tool_verify_assurance_receipt("{}")
    except Exception as e:
        out["verify_empty_object"] = f"{type(e).__name__}: {e}"[:140]
    class R:  # fixed analyser report: only the lexicon dimensions can move
        tes_score, vtr_score, pai_score, invariants = 0.5, 1.0, 0.5, []
    class A:
        def analyse(self, text):
            return R()
    g.analyser = A()
    import numpy as np
    base = g.text_to_alignment_vector("We walk the road together today.")
    def moved(text):
        return bool(not np.allclose(base, g.text_to_alignment_vector(text)))
    out["coercive phrase 'you have to ... no choice' moves vector"] = moved("You have to walk, there is no choice.")
    out["clarity phrase 'this means' moves vector"] = moved("This means we walk.")
    out["coercive word with punctuation 'must,' moves vector"] = moved("We must, today, walk.")
    out["control: bare 'must' moves vector"] = moved("We must walk today.")
    print(json.dumps(out, default=str))
''')


def family_g():
    p = run_py(G_CODE, str(TMP), str(IMPL))
    emit("G2+G3 guard imported as applications.*", **last_json(p))
    neutral = TMP / "neutral_cwd"
    neutral.mkdir(exist_ok=True)
    s = subprocess.run([sys.executable, "-B", str(APPS / "lycheetah_guard_mcp.py"), "--help"], cwd=neutral, env=ENV,
                       capture_output=True, text=True, timeout=120)
    src = (APPS / "lycheetah_guard_mcp.py").read_text(encoding="utf-8")
    emit("G1 guard run as a file, as its docstring SETUP advertises", returncode=s.returncode,
         stderr_tail=(s.stderr.strip().splitlines() or [""])[-1][:110],
         docstring_advertises_file_path='"args": ["path/to/lycheetah_guard_mcp.py"]' in src)
    try:
        from importlib.metadata import version
        mcp_version = version("mcp")
    except Exception as exc:
        mcp_version = f"unavailable ({type(exc).__name__})"
    try:
        from mcp.server import MCPServer  # noqa: F401
        status = "MCPServer importable"
    except Exception as exc:
        status = f"DID NOT RUN: {type(exc).__name__}: {str(exc)[:80]}"
    emit("G4 guard MCP protocol error semantics", mcp_installed=mcp_version, status=status)


# ── L: lexicon census ────────────────────────────────────────────────────────

def _is_split(node):
    return (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            and node.func.attr == "split" and not node.args)


def family_l():
    found = []
    for root in (IMPL, TMP / "lycheetah"):
        for p in sorted(root.rglob("*.py")):
            if "__pycache__" in p.parts:
                continue
            try:
                tree = ast.parse(p.read_text(encoding="utf-8"))
            except (SyntaxError, UnicodeDecodeError):
                continue
            literals, splits = {}, {}
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                    name, value = node.targets[0].id, node.value
                    if (isinstance(value, (ast.Set, ast.List, ast.Tuple)) and value.elts
                            and all(isinstance(e, ast.Constant) and isinstance(e.value, str) for e in value.elts)):
                        literals[name] = [e.value for e in value.elts]
                    elif _is_split(value):
                        splits[name] = ".lower()" in ast.unparse(value)
            for node in ast.walk(tree):
                if not isinstance(node, (ast.GeneratorExp, ast.ListComp, ast.SetComp)):
                    continue
                for gen in node.generators:
                    if not isinstance(gen.target, ast.Name):
                        continue
                    if isinstance(gen.iter, ast.Name) and gen.iter.id in splits:
                        lowered = splits[gen.iter.id]
                    elif _is_split(gen.iter):
                        lowered = ".lower()" in ast.unparse(gen.iter)
                    else:
                        continue
                    for cmp in ast.walk(node):
                        if (isinstance(cmp, ast.Compare) and isinstance(cmp.left, ast.Name)
                                and cmp.left.id == gen.target.id and isinstance(cmp.ops[0], ast.In)
                                and isinstance(cmp.comparators[0], ast.Name) and cmp.comparators[0].id in literals):
                            lex = cmp.comparators[0].id
                            dead = [w for w in literals[lex]
                                    if any(ch.isspace() for ch in w) or (lowered and w != w.lower())]
                            if dead:
                                found.append({"file": str(p.relative_to(TMP)), "line": cmp.lineno,
                                              "lexicon": lex, "never_matches": dead})
    emit("L lexicon entries that a whitespace token can never equal (names resolved per file)", hits=found)


try:
    materialize()
    sys.path[:0] = [str(CORE), str(APPS), str(IMPL)]
    tracked = [CORE / "triad_wuwei.py", CORE / "tri_axial_checker.py", APPS / "sol_workspace_mcp.py",
               APPS / "lycheetah_guard_mcp.py"] + [CORE / f"{m}.py" for m in STDOUT_MODULES[1:]]
    emit("PROVENANCE", source=args.ref or "working tree",
         sha256_16={p.name: hashlib.sha256(p.read_bytes()).hexdigest()[:16] for p in tracked})
    for family in (family_w, family_t, family_s, family_m, family_g, family_l):
        try:
            family()
        except Exception as exc:
            emit(f"{family.__name__} DID NOT RUN", reason=f"{type(exc).__name__}: {str(exc)[:160]}")
finally:
    shutil.rmtree(TMP, ignore_errors=True)
