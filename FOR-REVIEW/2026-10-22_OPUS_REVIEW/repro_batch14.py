"""Batch 14 repro (RV15): LAMAGUE status register, decision-record checker, Native-36 validator.

Usage: python3 -B repro_batch14.py <framework-root>

Copies what it mutates into a temp directory and never writes to <root>. Prints
one JSON line per probe, keyed by "id", so a BEFORE run (on a `git archive HEAD`
copy) and an AFTER run (on the working tree) can be diffed.
"""
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
L = ROOT / "03_LAMAGUE_L1"
SKIP = shutil.ignore_patterns("*.docx", "*.png", "*.pdf", "*.zip", "*.mp4", "__pycache__",
                              "26_SXP_L_RESEARCH", "10_PACKAGED_RELEASES", "09_ARTICLE_AND_VISUAL_ASSETS")


def emit(pid, **data):
    print(json.dumps({"id": pid, **data}, ensure_ascii=False, default=str))


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod  # dataclasses resolve their module by name
    spec.loader.exec_module(mod)
    return mod


with tempfile.TemporaryDirectory(prefix="rv15-") as tmp:
    copy = Path(tmp) / "03_LAMAGUE_L1"
    shutil.copytree(L, copy, ignore=SKIP)
    reg = load(copy / "lamague_register.py", "register_probe")
    view = lambda: {e.path: (e.register, e.evidence) for e in reg.derive()
                    if e.path in ("02_NATIVE36", "23_SPOKEN_LAMAGUE", "22_REVERSIBLE_COMPRESSION_v1.0")
                    or e.path.startswith("13_RETIRED")}
    emit("C1 control: register as committed", entries=view())

    reg_json = copy / "02_NATIVE36" / "LAMAGUE_NATIVE36_v0.3_MACHINE_CANON_REGISTRY.json"
    good = reg_json.read_text(encoding="utf-8")
    data = json.loads(good)
    data["base_glyphs"].reverse()
    reg_json.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    out = subprocess.run([sys.executable, "-B", reg_json.parent / "validate_lamague_native36_v0.3.py", reg_json],
                         capture_output=True, text=True)
    emit("P1 Native-36 registry with base glyphs reversed", validator_exit=out.returncode,
         validator_says=out.stdout.splitlines()[0], register_says=view()["02_NATIVE36"])
    reg_json.write_text(good, encoding="utf-8")

    planted = copy / "22_REVERSIBLE_COMPRESSION_v1.0" / "tests" / "test_zz_planted.py"
    planted.write_text("import unittest\n\n\nclass P(unittest.TestCase):\n"
                       "    def test_planted(self):\n        self.fail('TOKEN mismatch')\n")
    emit("P2 22 suite with one planted failure whose message contains OK",
         register_says=view()["22_REVERSIBLE_COMPRESSION_v1.0"])
    planted.unlink()

    out = subprocess.run([sys.executable, "-B", "spl.py", "verify"], cwd=copy / "23_SPOKEN_LAMAGUE",
                         capture_output=True, text=True)
    emit("P3 spoken verifier versus its register entry", verify_exit=out.returncode,
         verify_result=[x.strip() for x in out.stdout.splitlines() if "RESULT" in x],
         register_says=view()["23_SPOKEN_LAMAGUE"])

    validator = copy / "02_NATIVE36" / "validate_lamague_native36_v0.3.py"
    gaps = {}
    for name, mutate in {
        "all compound seals deleted": lambda d: d.__setitem__("compound_seals", []),
        "a compound seal duplicated": lambda d: d["compound_seals"].append(dict(d["compound_seals"][0])),
        "every glyph name and description blanked": lambda d: [g.update(name="", description="") for g in d["base_glyphs"]],
    }.items():
        d = json.loads(good)
        mutate(d)
        reg_json.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
        gaps[name] = subprocess.run([sys.executable, "-B", validator, reg_json],
                                    capture_output=True, text=True).returncode
    reg_json.write_text(good, encoding="utf-8")
    emit("P4 Native-36 validator exit on registry damage it does not check (0 = accepted)", cases=gaps)

chk = load(L / "24_LAMAGUE_CHECK" / "lamague_check.py", "checker_probe")
cases = {
    "rollback: false": ({"rollback": False}, "recovery"),
    "dissent: ['TBD', '']": ({"dissent": ["TBD", ""]}, "dissent"),
    "dissent: {who: '', why: null}": ({"dissent": {"who": "", "why": None}}, "dissent"),
    "no_rollback: 'irreversible'": ({"no_rollback": "irreversible"}, "recovery"),
    "without_dissent: true": ({"without_dissent": True}, "dissent"),
    "disclaim: 'x'": ({"disclaim": "x"}, "claim"),
    "meta.owner '' beside owner 'alice'": ({"meta": {"owner": ""}, "owner": "alice"}, "authority"),
    "dependencies[0].owner only": ({"dependencies": [{"owner": "bob"}]}, "authority"),
    "control owner 'alice'": ({"owner": "alice"}, "authority"),
}
emit("P5 decision-record checker", cases={k: [(r["status"], r["found_as"]) for r in chk.check(rec) if r["field"] == f][0]
                                          for k, (rec, f) in cases.items()},
     demo_present=sum(r["status"] == "PRESENT" for r in chk.check(chk.DEMO)))
