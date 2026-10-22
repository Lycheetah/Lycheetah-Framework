"""Batch 13 repro (RV14): LAMAGUE parser conformance against 04_BNF_GRAMMAR.md.

Usage: python3 -B repro_batch13.py <framework-root>

Loads <root>/12_IMPLEMENTATIONS/core/lamague_parser.py by path and never writes
to <root>. Prints one JSON line per probe, keyed by "id", so a BEFORE run (on a
`git archive HEAD` copy) and an AFTER run (on the working tree) can be diffed.
"""
import hashlib
import importlib.util
import json
import sys
import time
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
SRC = ROOT / "12_IMPLEMENTATIONS" / "core" / "lamague_parser.py"
BNF = ROOT / "03_LAMAGUE_L1" / "04_BNF_GRAMMAR.md"

spec = importlib.util.spec_from_file_location("lamague_parser_probe", SRC)
lp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lp)
V = lp.LAMAGUEValidator()
TOK = lp.LAMAGUETokenizer()
BNF_TEXT = BNF.read_text(encoding="utf-8")


def emit(pid, **data):
    print(json.dumps({"id": pid, **data}, ensure_ascii=False))


def shape(node):
    if node is None:
        return None
    if node.node_type == "composition":
        left, op, right = node.children
        return f"({shape(left)} {op.value} {shape(right)})"
    return node.value


def check(expr, tokens=False):
    try:
        r = V.validate(expr)
    except RecursionError:
        return {"raised": "RecursionError"}
    except Exception as exc:  # the probe reports, it does not judge
        return {"raised": f"{type(exc).__name__}: {exc}"[:160]}
    out = {"valid": r.valid, "errors": r.errors[:3]}
    if tokens:
        out["tokens"] = [f"{t.type.value}:{t.value}" for t in r.tokens]
    return out


emit("PROVENANCE", source=str(ROOT), sha256_16=hashlib.sha256(SRC.read_bytes()).hexdigest()[:16])

# Controls: must hold before and after.
r = V.validate("Ao → Φ↑ → Ψ_inv")
emit("C1 control: canonical TRIAD cycle", valid=r.valid, symbols=r.tree.symbols() if r.tree else None)
emit("C2 control: double operator", **check("Ao → → Ψ"))
emit("C3 control: newline is whitespace", **check("Ao →\nΨ"))

# P1: the subscript scanner stops only at a fixed list of characters.
emit("P1 subscript body swallows operators and unknown symbols",
     cases={e: check(e, tokens=True) for e in ("Ψ_inv↯Ao", "Ψ_inv@#$", "Ao_x;y", "Φ_inv↑", "Ψ_")})

# P2/P3: the BNF's <dynamic> class.
standalone = {}
for d in sorted(lp.DYNAMICS):
    res = V.validate(d)
    standalone[d] = {"valid": res.valid, "class": res.tree.symbol_class if res.tree else None}
emit("P2 BNF <dynamic> symbols standing alone", cases=standalone)
emit("P3 token type produced for each BNF dynamic",
     types={d: TOK.tokenize(d)[0].type.value for d in sorted(lp.DYNAMICS)})

# P4: the ↑ compound for every field.
emit("P4 field↑ compound per field", cases={f: check(f)["valid"] for f in ("Φ↑", "Ψ↑", "S↑", "Δ↑", "Ao↑")})

# P5: every expression 04_BNF_GRAMMAR.md presents as LAMAGUE.
doc_exprs = [
    "Ao → Φ↑ → Ψ → Ψ_inv | C(Ψ_t) ≥ C(Ψ₀)",
    "Ψ ↯ Ao → Φ↑ → Ψ_inv",
    "x₀ → ⟲[x ← x - η∇f(x)] → (‖∇f‖ < ε) → Yield(x*)",
    "condition ↯ [option_a], [option_b]",
    "Array[mid] ↯ Junction:",
]
emit("P5 the BNF document's own expressions",
     cases={e: {"in_doc": e in BNF_TEXT, **check(e)} for e in doc_exprs})

# P6: constructs that proposal 02 says already match the parser.
emit("P6 proposal 02 constructs", cases={e: check(e) for e in ("Ao · Ψ", "Φ↑_inv", "↯", "Ao↑")})

# P7: grouping in the tree versus the node's value string.
a, b = V.validate("(Ao → Φ) → Ψ").tree, V.validate("Ao → (Φ → Ψ)").tree
emit("P7 parenthesised grouping", shapes=[shape(a), shape(b)], values=[a.value, b.value],
     values_equal=a.value == b.value)

# P8: precedence and associativity.
emit("P8 mixed operators parse shape",
     cases={e: shape(V.validate(e).tree) for e in ("Ψ → Ao ⊗ Φ", "Ψ ⊗ Ao → Φ", "Ψ ↯ Ao → Φ↑")})

# P9: whitespace other than space, tab and newline.
emit("P9 CRLF and non-breaking space", cases={repr(e): check(e) for e in ("Ao →\r\nΨ", "Ao → Ψ")})


def nested(depth):
    return check("(" * depth + "Ao" + ")" * depth)


lo, hi = 1, 4096
if "raised" in nested(hi):
    while lo < hi:
        mid = (lo + hi) // 2
        if "raised" in nested(mid):
            hi = mid
        else:
            lo = mid + 1
    emit("P10 parenthesis nesting depth", first_crash_depth=lo, at_depth=nested(lo),
         recursion_limit=sys.getrecursionlimit())
else:
    emit("P10 parenthesis nesting depth", first_crash_depth=None, at_4096=nested(4096))

chains = {}
for n in (500, 1500, 3000):
    expr = " → ".join(["Ao"] * n)
    t0 = time.perf_counter()
    res = check(expr)
    entry = {"validate": res if "raised" in res else {"valid": res["valid"], "errors": res["errors"][:1]},
             "seconds": round(time.perf_counter() - t0, 2)}
    tree = None if "raised" in res else V.validate(expr).tree
    if tree is not None:
        for name in ("symbols", "to_dict"):
            try:
                getattr(tree, name)()
                entry[name] = "ok"
            except RecursionError:
                entry[name] = "RecursionError"
    chains[n] = entry
emit("P11 long operator chains", cases=chains)

emit("P12 pipe placement", cases={e: check(e) for e in ("| Ao", "| Ao → → Ψ", "Ao | Ψ | Φ", "Ao |")})

measurer = lp.CompressionMeasurer()
ms = [measurer.measure(x["expr"], x["nl"]) for x in lp.CANONICAL_EXAMPLES]
emit("P13 compression figures the BNF cites from this parser",
     avg_token_ratio=round(sum(m["token_ratio"] for m in ms) / len(ms), 2),
     avg_char_ratio=round(sum(m["char_ratio"] for m in ms) / len(ms), 2),
     all_valid=all(m["parse_valid"] for m in ms),
     doc_claims_token_3_char_11="Token ratio: **~3:1**" in BNF_TEXT and "Character ratio: **~11:1**" in BNF_TEXT)

emit("P14 expansion text per operator",
     cases={op: measurer.build_expansion(f"Ψ {op} Ao") for op in ("→", "⊗", "⇌", "⟲", "↯")})
emit("P15 detached and empty subscripts", cases={e: check(e) for e in ("_inv", "Ao → _x", "Ψ_ → Ao")})
