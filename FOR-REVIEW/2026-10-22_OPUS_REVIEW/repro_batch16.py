"""Batch 16 repro (RV17): compression and interoperability claims, measured independently.

Usage: python3 -B repro_batch16.py <framework-root> <scratch-dir>

Never writes under <root>. The codec benchmark rewrites its own corpus/ and reports/,
so it is only ever run on a copy inside <scratch-dir>. Prints one JSON line per probe.

P1  seal: the 22_REVERSIBLE_COMPRESSION package against its own SHA256_MANIFEST.json
P2  rerun: benchmark + unit tests on a scratch copy; regenerated outputs vs committed
P3  conventional baselines on the same frozen split (gzip, deflate, zlib preset dictionary)
P4  template share: how much of the held-out text is the generator's boilerplate
P5  parser ratios: the "~11:1 character / ~3:1 token" figure re-measured in bytes
P6  unique decodability: an independent Sardinas-Patterson plus a brute-force parse count
P7  the SpL checker's own verdicts on the same inventories (agreement, not authority)
"""
import bz2
import gzip
import hashlib
import importlib.util
import json
import lzma
import os
import shutil
import subprocess
import sys
import zlib
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
SCRATCH = Path(sys.argv[2]).resolve()
PKG = ROOT / "03_LAMAGUE_L1" / "22_REVERSIBLE_COMPRESSION_v1.0"
SPL = ROOT / "03_LAMAGUE_L1" / "23_SPOKEN_LAMAGUE"


def emit(pid, **data):
    print(json.dumps({"id": pid, **data}, ensure_ascii=False), flush=True)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# ── P1 seal ────────────────────────────────────────────────────────────────
manifest = json.loads((PKG / "SHA256_MANIFEST.json").read_text(encoding="utf-8"))
seal = {"ok": [], "changed": [], "missing": []}
for rel, entry in manifest["files"].items():
    path = PKG / rel
    if not path.exists():
        seal["missing"].append(rel)
        continue
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    seal["ok" if digest == entry["sha256"] else "changed"].append(rel)
listed = set(manifest["files"])
unlisted = sorted(str(p.relative_to(PKG)) for p in PKG.rglob("*")
                  if p.is_file() and "__pycache__" not in p.parts and str(p.relative_to(PKG)) not in listed)
emit("P1 package seal", ok=len(seal["ok"]), changed=seal["changed"], missing=seal["missing"], unlisted=unlisted)

# ── P2 rerun on a scratch copy ─────────────────────────────────────────────
copy_dir = SCRATCH / "rv17_codec_pkg"
if copy_dir.exists():
    shutil.rmtree(copy_dir)
shutil.copytree(PKG, copy_dir, ignore=shutil.ignore_patterns("__pycache__"))
env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
bench = subprocess.run([sys.executable, "-B", "src/benchmark.py"], cwd=copy_dir, env=env,
                       capture_output=True, text=True, timeout=300)
tests = subprocess.run([sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests"], cwd=copy_dir,
                       env=env, capture_output=True, text=True, timeout=300)
regenerated = ["corpus/codebook.json", "reports/benchmark_report.json", "reports/packet_sizes.csv",
               "reports/mutation_results.jsonl", "reports/sample_roundtrip.json"]
identical = {rel: (copy_dir / rel).read_bytes() == (PKG / rel).read_bytes() for rel in regenerated}
report = json.loads((copy_dir / "reports/benchmark_report.json").read_text(encoding="utf-8"))
c = report["compression"]
emit("P2 benchmark rerun on scratch copy", bench_exit=bench.returncode, tests_exit=tests.returncode,
     tests_tail=tests.stderr.strip().splitlines()[-1:], regenerated_identical_to_committed=identical,
     heldout_l1=round(c["heldout_l1_reduction_vs_minified_json"], 4),
     heldout_warm=round(c["heldout_l1d_warm_reduction_vs_minified_json"], 4),
     heldout_cold=round(c["heldout_l1d_cold_reduction_including_codebook"], 4),
     codebook_wire_bytes=report["codebook"]["wire_bytes"], sizes_heldout=report["sizes"]["heldout"])

# ── P3 conventional baselines, same split, same denominator ────────────────
codec = load("rv17_lamague_codec", copy_dir / "src" / "lamague_codec.py")
packets = [json.loads(line) for line in (copy_dir / "corpus/packets.jsonl").read_text(encoding="utf-8").splitlines()
           if line.strip()]
split = json.loads((copy_dir / "corpus/split.json").read_text(encoding="utf-8"))
train = [p for p in packets if p["id"] in set(split["training"])]
held = [p for p in packets if p["id"] in set(split["heldout"])]
codebook = json.loads((copy_dir / "corpus/codebook.json").read_text(encoding="utf-8"))
cb_wire = len(codec.canonical_bytes(codebook))


def raw_deflate(data, zdict=None):
    obj = zlib.compressobj(9, zlib.DEFLATED, -15, 9, zlib.Z_DEFAULT_STRATEGY, **({"zdict": zdict} if zdict else {}))
    return len(obj.compress(data) + obj.flush())


def inflate_ok(data, zdict):
    obj = zlib.compressobj(9, zlib.DEFLATED, -15, 9, zlib.Z_DEFAULT_STRATEGY, zdict=zdict)
    blob = obj.compress(data) + obj.flush()
    dec = zlib.decompressobj(-15, zdict=zdict)
    return dec.decompress(blob) + dec.flush() == data


base = [codec.canonical_bytes(p) for p in held]
B = sum(map(len, base))
l1 = [codec.encode(p).encode("utf-8") for p in held]
l1d = [codec.encode(p, codebook).encode("utf-8") for p in held]
train_concat = b"".join(codec.canonical_bytes(p) for p in train)
zdict_full = train_concat[-32768:]                                   # what zlib actually uses
zdict_cb = "".join(codebook["entries"]).encode("utf-8")              # the SAME strings as the LAMAGUE codebook
red = lambda n: round(1 - n / B, 4)                                   # noqa: E731
arms = {
    "lamague_L1": sum(map(len, l1)),
    "lamague_L1D_warm": sum(map(len, l1d)),
    "lamague_L1D_cold(+codebook)": sum(map(len, l1d)) + cb_wire,
    "gzip-9 per packet": sum(len(gzip.compress(b, 9, mtime=0)) for b in base),
    "raw deflate-9 per packet": sum(raw_deflate(b) for b in base),
    "bz2-9 per packet": sum(len(bz2.compress(b, 9)) for b in base),
    "xz per packet": sum(len(lzma.compress(b)) for b in base),
    "deflate+preset dict = codebook strings, warm": sum(raw_deflate(b, zdict_cb) for b in base),
    "deflate+preset dict = codebook strings, cold(+dict)": sum(raw_deflate(b, zdict_cb) for b in base) + len(zdict_cb),
    "deflate+preset dict = training split (32KB), warm": sum(raw_deflate(b, zdict_full) for b in base),
    "deflate+preset dict = training split, cold(+deflated dict)":
        sum(raw_deflate(b, zdict_full) for b in base) + raw_deflate(zdict_full),
    "L1D then raw deflate-9, warm": sum(raw_deflate(b) for b in l1d),
    "gzip of the whole held-out stream (12 packets, one member)": len(gzip.compress(b"\n".join(base), 9, mtime=0)),
}
emit("P3 held-out bytes and reduction vs minified JSON (higher is smaller)",
     baseline_bytes=B, packets=len(held), codebook_wire_bytes=cb_wire, zdict_codebook_bytes=len(zdict_cb),
     preset_dict_roundtrip_ok=all(inflate_ok(b, zdict_full) and inflate_ok(b, zdict_cb) for b in base),
     arms={k: {"bytes": v, "reduction": red(v)} for k, v in arms.items()})

# ── P4 template share ──────────────────────────────────────────────────────
def stem(pid):
    return pid.rsplit("_", 1)[0]


def strings(v):
    if isinstance(v, str):
        yield v
    elif isinstance(v, list):
        for x in v:
            yield from strings(x)
    elif isinstance(v, dict):
        for x in v.values():
            yield from strings(x)


def templated(p):
    return [s.replace(p["id"], "{ID}").replace(stem(p["id"]), "{D}") for s in strings(p)]


train_t = {s for p in train for s in templated(p)}
held_s = [(s, t) for p in held for s, t in zip(strings(p), templated(p))]
held_bytes = sum(len(s.encode()) for s, _ in held_s)
seen_bytes = sum(len(s.encode()) for s, t in held_s if t in train_t)
train_stems = {stem(p["id"]) for p in train}
held_stems = {stem(p["id"]) for p in held}
cb_domain = [e for e in codebook["entries"] if any(s in e for s in train_stems)]
emit("P4 held-out text that is training boilerplate after the domain name is masked",
     heldout_domains_unseen_in_training=sorted(held_stems - train_stems) == sorted(held_stems),
     heldout_string_values=len(held_s), heldout_string_bytes=held_bytes,
     bytes_identical_to_a_training_template=seen_bytes, share=round(seen_bytes / held_bytes, 4),
     codebook_entries=len(codebook["entries"]), codebook_entries_naming_a_domain=len(cb_domain),
     codebook_sample=codebook["entries"][:6])

# ── P5 parser ratios ───────────────────────────────────────────────────────
parser = load("rv17_lamague_parser", ROOT / "12_IMPLEMENTATIONS" / "core" / "lamague_parser.py")
measurer = parser.CompressionMeasurer()
rows = []
for ex in parser.CANONICAL_EXAMPLES:
    m = measurer.measure(ex["expr"], ex["nl"])
    lb, nb = len(ex["expr"].encode("utf-8")), len(ex["nl"].encode("utf-8"))
    rows.append({"expr": ex["expr"], "tokens": m["lamague_tokens"], "words": m["nl_words"],
                 "token_ratio": m["token_ratio"], "char_ratio_no_spaces": m["char_ratio"],
                 "utf8_byte_ratio_with_spaces": round(nb / lb, 2),
                 "non_ascii_codepoints": sum(ord(ch) > 127 for ch in ex["expr"]), "parse_valid": m["parse_valid"]})
mean = lambda k: round(sum(r[k] for r in rows) / len(rows), 2)  # noqa: E731
emit("P5 parser compression figure re-measured", n=len(rows), mean_token_ratio=mean("token_ratio"),
     mean_char_ratio=mean("char_ratio_no_spaces"), mean_utf8_byte_ratio=mean("utf8_byte_ratio_with_spaces"),
     english_side="author-written gloss, not an independent corpus", bpe_tokenizer="DID NOT RUN (tiktoken absent)",
     rows=rows)


# ── P6 unique decodability, written independently ─────────────────────────
def sp_closure(code):
    """Sardinas-Patterson as a worklist closure over dangling suffixes (terminates exactly)."""
    code = set(code)

    def dang(xs, ys):
        out = set()
        for x in xs:
            for y in ys:
                if x != y and x.startswith(y):
                    out.add(x[len(y):])
        return out
    start = dang(code, code)
    seen, todo = set(start), list(start)
    while todo:
        s = todo.pop()
        if s in code:
            return False, s
        for t in dang({s}, code) | dang(code, {s}):
            if t and t not in seen:
                seen.add(t)
                todo.append(t)
    return True, ""


def shortest_ambiguity(code, max_len=40):
    """Constructive search, independent of the closure above: grow two parses that differ in
    their first word and keep the leading one's overhang. Dijkstra on the leading string's
    length, so the first collision is a shortest ambiguous string. Returns (string, A, B)."""
    import heapq
    code = sorted(set(code))
    heap = []
    for u in code:
        for v in code:
            if u != v and u.startswith(v):
                heapq.heappush(heap, (len(u), u[len(v):], (u,), (v,)))
    done = set()
    while heap:
        n, s, ahead, behind = heapq.heappop(heap)
        if n > max_len:
            return None
        if s in done:
            continue
        done.add(s)
        for w in code:
            if w == s:
                return "".join(ahead), list(ahead), list(behind) + [w]
            if s.startswith(w):
                heapq.heappush(heap, (n, s[len(w):], ahead, behind + (w,)))
            elif w.startswith(s):
                heapq.heappush(heap, (n + len(w) - len(s), w[len(s):], behind + (w,), ahead))
    return None


def their_ud(code):
    r = spl_ref.uniquely_decodable(code)
    return r[0] if isinstance(r, tuple) else r


controls = {"{0,10,110}": ({"0", "10", "110"}, True), "{0,01,11}": ({"0", "01", "11"}, True),
            "{a,ab,bb}": ({"a", "ab", "bb"}, True), "{a,ab,b}": ({"a", "ab", "b"}, False),
            "{a,ba,bb}": ({"a", "ba", "bb"}, True),
            "{a,c,ad,abb,bad,deb,bbcde}": ({"a", "c", "ad", "abb", "bad", "deb", "bbcde"}, False)}
spl_ref = load("rv17_spl_phonology", SPL / "spl_phonology.py")
emit("P6a controls (truth table from the definition)", cases={
    name: {"expected_ud": exp, "independent": sp_closure(c)[0], "spl_checker": their_ud(c),
           "constructive_witness": (shortest_ambiguity(c) or [None])[0]}
    for name, (c, exp) in controls.items()})

reg = json.loads((SPL / "spl_registry_v0.1.json").read_text(encoding="utf-8"))
inv = spl_ref.load_inventory(reg)
n36 = reg["native36_spoken_forms"]
n36_forms = set(n36["numerals"].values()) | set(n36["operators"].values())
core = {f.replace("-", "") for f in reg["core_phonemes"] if not f.startswith("_")}
core_compound = {f for f in core if f != "saian"}          # read sai-an as sai + an, as the source hyphen says
inventories = {"Native-36 spoken forms": n36_forms, "SpL core": core,
               "SpL core, sai-an as compound": core_compound, "merged flat inventory": set(inv),
               "merged, sai-an as compound": set(inv) - {"saian"}}
emit("P6b inventories", cases={
    name: {"size": len(code), "independent_ud": sp_closure(code)[0], "independent_witness": sp_closure(code)[1],
           "spl_checker_ud": their_ud(code),
           "shortest_ambiguous_string": shortest_ambiguity(code)}
    for name, code in inventories.items()})

sxpl = ROOT / "03_LAMAGUE_L1" / "26_SXP_L_RESEARCH" / "v2.0" / "baseline" / "runtime"
sys.path.insert(0, str(sxpl))
spoken = load("rv17_sxpl_spoken", sxpl / "spoken.py")
words = set(spoken.WORDS)
syll_code = {"".join(spoken.syllables(w)) for w in words}
emit("P6c SXP-L v2.0 spoken lexicon (module states words are separated; UD is informational)",
     words=len(words), ud_without_separators=sp_closure(words)[0], witness=sp_closure(words)[1],
     shortest_ambiguous_string=shortest_ambiguity(words), syllabification_is_identity=syll_code == words)
