#!/usr/bin/env python3
"""
loop_audit.py — does each feedback loop close in code the way LOOP_MAP.json says?

    python3 34_CYBERNETICS/loop_audit.py              # audit the live source
    python3 34_CYBERNETICS/loop_audit.py --json       # machine-readable
    python3 34_CYBERNETICS/loop_audit.py --self-test  # prove the audit can fail

A cybernetic loop has four parts: a sensor that reads an essential variable, a
comparator that holds it against a setpoint, an actuator that changes the world,
and a feedback path that carries the actuator's effect back to the sensor. A
diagram can draw all four for any design. This script asks the code.

For every loop in LOOP_MAP.json it checks, by parsing the source (never by
importing or running it):

  1. SYMBOLS      the file exists and every named driver, sensor, comparator and
                  actuator is defined in it.
  2. CLOSURE      whether the loop closes in code, computed from the syntax tree:
                    - the driver reaches the actuator (and the sensor, when the
                      sensor is a method of the file), and
                    - a feedback path exists, either
                      DATAFLOW      inside a loop in the driver, a value assigned
                                    from the actuator is passed into the sensor, or
                      SHARED STATE  the actuator writes an attribute that the
                                    sensor reads (closure across calls).
                  The computed answer must equal the map's `closes_in_code`.
  3. CENSUS       for a loop that is open in code, regulation is finished by
                  whoever reads the sensor's output. Every file that references
                  the class must be listed in `known_callers`. A new reader fails
                  the audit until someone checks whether it acts: the map is stale.
  4. FEEDFORWARD  for a pipeline, no loop in the driver may span two stages, and
                  every named stage must still be called.

--self-test mutates in-memory copies of the source and confirms each check fails
when it should. The live files are never written.

WHAT THIS AUDIT CANNOT SAY
  - Calls resolve by name, without type inference. Two methods both called
    `step` are indistinguishable to it.
  - A loop that closes in code may still regulate the wrong variable. Whether a
    sensor reads the essential variable or a proxy of it is argued in
    CYBERNETIC_READING.md, not measured here.
  - Open in code is a design fact, not a defect. AURA is built to hand its
    verdict to a person or a host model; that loop closes outside the code, where
    this script cannot see.
  - It audits the loops in the map. A loop nobody wrote down is invisible to it.
"""

import argparse
import ast
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
MAP_PATH = HERE / "LOOP_MAP.json"
SKIP_PARTS = {"99_ARCHIVE", "node_modules", "__pycache__", "venv", "site-packages"}
CALL_DEPTH = 3

# (label, path, old text, new text, loop id, expected failure substring).
# old=None injects `new` as a whole new file at `path`.
MUTATIONS = [
    ("cut Grey Mode's actuator out of its loop",
     "12_IMPLEMENTATIONS/core/grey_mode.py",
     "self.recovery_cycle(current_state", "self.recovery_cycle_cut(current_state",
     "L-GREY", "closes_in_code"),
    ("rename Grey Mode's sensor",
     "12_IMPLEMENTATIONS/core/grey_mode.py",
     "def compute_psi_r(", "def compute_psi_renamed(",
     "L-GREY", "missing"),
    ("CASCADE stops writing the attribute its sensor reads",
     "12_IMPLEMENTATIONS/core/cascade_engine.py",
     ".regime = ", ".regime_shadow = ",
     "L-CASCADE", "closes_in_code"),
    ("a new module starts reading AURA's verdict",
     "zz_self_test/new_reader.py",
     None, "from aura_checker import AURAChecker\n",
     "L-AURA", "new reader"),
    ("someone wires AURA back into the CASCADE stage",
     "12_IMPLEMENTATIONS/core/sovereign_pipeline.py",
     "engine.add_block(block)",
     "engine.add_block(block); self.aura_checker.check(decision_text, context)",
     "L-PIPELINE", "spans stages"),
]


def short(symbol):
    return symbol.split(".")[-1]


def terminal(func):
    """The name a call is made through: f(...) -> f, x.y.f(...) -> f."""
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


def calls_in(node):
    return [n for n in ast.walk(node) if isinstance(n, ast.Call)]


def loops_in(node):
    return [n for n in ast.walk(node) if isinstance(n, (ast.For, ast.AsyncFor, ast.While))]


def names_in(node):
    return {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}


def attributes(node, ctx):
    return {n.attr for n in ast.walk(node)
            if isinstance(n, ast.Attribute) and isinstance(n.ctx, ctx)}


def index_module(source, filename):
    """Map 'func', 'Class' and 'Class.method' to their AST nodes."""
    tree = ast.parse(source, filename=filename)
    symbols = {}
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            symbols[node.name] = node
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    symbols[f"{node.name}.{item.name}"] = item
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            symbols[node.name] = node
    return symbols


def reachable(symbols, start):
    """Functions in this file reachable from `start` by call name, CALL_DEPTH hops deep."""
    by_name = {}
    for sym, node in symbols.items():
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            by_name.setdefault(short(sym), []).append(sym)
    seen, frontier = {start}, [start]
    for _ in range(CALL_DEPTH):
        nxt = []
        for sym in frontier:
            for call in calls_in(symbols[sym]):
                for target in by_name.get(terminal(call.func), []):
                    if target not in seen:
                        seen.add(target)
                        nxt.append(target)
        frontier = nxt
    return seen


def required_symbols(entry):
    parts = [entry["driver"], entry["sensor"].get("method"),
             entry["comparator"].get("method"), (entry.get("actuator") or {}).get("method")]
    return [s for s in dict.fromkeys(parts) if s]


def dataflow_path(driver, actuator, sensor_call):
    """Inside one loop of the driver: X = actuator(...) and X is passed to the sensor."""
    act = short(actuator)
    for loop in loops_in(driver):
        produced = set()
        for node in ast.walk(loop):
            if (isinstance(node, ast.Assign) and isinstance(node.value, ast.Call)
                    and terminal(node.value.func) == act):
                for target in node.targets:
                    produced |= names_in(target)
        if not produced:
            continue
        for call in calls_in(loop):
            if terminal(call.func) != sensor_call:
                continue
            fed = set()
            for arg in list(call.args) + [k.value for k in call.keywords]:
                fed |= names_in(arg)
            if fed & produced:
                carried = ", ".join(sorted(fed & produced))
                return (f"DATAFLOW (loop at line {loop.lineno}): {carried} = {act}(…) "
                        f"is passed to {sensor_call}(…)")
    return None


def compute_closure(entry, symbols):
    """(closes, mechanism or reason), computed from the syntax tree."""
    actuator = (entry.get("actuator") or {}).get("method")
    if not actuator:
        return False, "no actuator in code"
    driver = entry["driver"]
    reach = reachable(symbols, driver)
    if actuator not in reach:
        return False, f"{driver} never reaches the actuator {actuator}"
    sensor = entry["sensor"].get("method")
    if sensor and sensor not in reach:
        return False, f"{driver} never reaches the sensor {sensor}"
    sensor_call = short(sensor) if sensor else entry["sensor"].get("call")
    path = dataflow_path(symbols[driver], actuator, sensor_call)
    if path:
        return True, path
    if sensor:
        shared = attributes(symbols[actuator], ast.Store) & attributes(symbols[sensor], ast.Load)
        if shared:
            fields = ", ".join("." + s for s in sorted(shared))
            return True, f"SHARED STATE: {short(actuator)} writes {fields}, which {short(sensor)} reads"
    return False, "no feedback path from the actuator's output to the sensor's input"


def feedforward(entry, symbols):
    driver = symbols[entry["driver"]]
    stage_of = {name: stage for stage, names in entry["stages"].items() for name in names}
    called = {terminal(c.func) for c in calls_in(driver)}
    failures = []
    for stage, names in entry["stages"].items():
        if not called & set(names):
            failures.append(f"stage {stage}: none of {names} is called in {entry['driver']} — map stale")
    for loop in loops_in(driver):
        spanned = {stage_of[t] for t in (terminal(c.func) for c in calls_in(loop)) if t in stage_of}
        if len(spanned) > 1:
            failures.append(f"loop at line {loop.lineno} spans stages {sorted(spanned)}: "
                            f"a later stage now feeds back into an earlier one")
    return failures


_NAME_CACHE = {}


def referenced_names(source, filename):
    key = (filename, hash(source))
    if key not in _NAME_CACHE:
        names = set()
        for n in ast.walk(ast.parse(source, filename=filename)):
            if isinstance(n, ast.Name):
                names.add(n.id)
            elif isinstance(n, ast.Attribute):
                names.add(n.attr)
            elif isinstance(n, ast.alias):
                names.add(n.name.split(".")[-1])
        _NAME_CACHE[key] = names
    return _NAME_CACHE[key]


def build_census(sources):
    """{path: names it references}. Unparseable files are reported, never hidden."""
    census, unparsed = {}, []
    for rel, text in sources.items():
        try:
            census[rel] = referenced_names(text, rel)
        except SyntaxError:
            unparsed.append(rel)
    return census, unparsed


def census_check(entry, census):
    cls = entry["driver"].split(".")[0]
    found = {rel for rel, names in census.items() if cls in names and rel != entry["code_path"]}
    known = set(entry.get("known_callers", []))
    failures = [f"new reader of {cls}: {rel} — map stale; check whether it acts on the verdict"
                for rel in sorted(found - known)]
    failures += [f"listed caller {rel} no longer references {cls} — map stale"
                 for rel in sorted(known - found)]
    return failures, sorted(found)


def audit(loop_map, sources):
    census, unparsed = build_census(sources)
    rows = []
    for entry in loop_map["loops"]:
        row = {"id": entry["id"], "declared": entry["closes_in_code"], "failures": []}
        text = sources.get(entry["code_path"])
        if text is None:
            row["failures"].append(f"{entry['code_path']} not found")
            rows.append(row)
            continue
        symbols = index_module(text, entry["code_path"])
        missing = [s for s in required_symbols(entry) if s not in symbols]
        if missing:
            row["failures"].append(f"symbols missing from {entry['code_path']}: {', '.join(missing)}")
        else:
            closes, how = compute_closure(entry, symbols)
            row["computed"], row["mechanism"] = closes, how
            if closes != entry["closes_in_code"]:
                row["failures"].append(
                    f"map says closes_in_code={entry['closes_in_code']}, code says {closes}: {how}")
            if "stages" in entry:
                row["failures"] += feedforward(entry, symbols)
        if not entry["closes_in_code"]:
            failures, readers = census_check(entry, census)
            row["failures"] += failures
            row["readers"] = readers
        rows.append(row)
    return rows, unparsed


def load_sources():
    sources = {}
    for path in sorted(ROOT.rglob("*.py")):
        rel = path.relative_to(ROOT)
        if any(part.startswith(".") or part in SKIP_PARTS for part in rel.parts):
            continue
        sources[rel.as_posix()] = path.read_text(encoding="utf-8", errors="replace")
    return sources


def run_mutation(loop_map, sources, mutation):
    """Apply one mutation to an in-memory copy and audit it.
    Returns ('stale', None), ('caught', failure) or ('missed', None)."""
    _label, path, old, new, loop_id, expect = mutation
    mutated = dict(sources)
    if old is None:
        mutated[path] = new
    elif path not in mutated or old not in mutated[path]:
        return "stale", None
    else:
        mutated[path] = mutated[path].replace(old, new)
    rows, _ = audit(loop_map, mutated)
    hits = [f for r in rows if r["id"] == loop_id for f in r["failures"] if expect in f]
    return ("caught", hits[0]) if hits else ("missed", None)


def self_test(loop_map, sources):
    rows, _ = audit(loop_map, sources)
    if any(r["failures"] for r in rows):
        print("✗ the live audit is not clean; the self-test needs a clean baseline first.")
        return 1
    print(f"\n⊚ LOOP AUDIT SELF-TEST — {len(MUTATIONS)} mutations, in memory only\n")
    caught = 0
    for mutation in MUTATIONS:
        label, path = mutation[0], mutation[1]
        result, failure = run_mutation(loop_map, sources, mutation)
        if result == "caught":
            caught += 1
            print(f"  ✓ caught  {label}\n            {failure}")
        elif result == "stale":
            print(f"  ✗ STALE   {label}: target text not found in {path}")
        else:
            print(f"  ✗ MISSED  {label}")
    print(f"\n  {caught}/{len(MUTATIONS)} mutations caught.\n")
    return 0 if caught == len(MUTATIONS) else 1


def main(argv=None):
    p = argparse.ArgumentParser(description="Audit LOOP_MAP.json against the source.")
    p.add_argument("--json", action="store_true", help="print the machine-readable result")
    p.add_argument("--self-test", action="store_true", help="prove each check can fail")
    args = p.parse_args(argv)

    loop_map = json.loads(MAP_PATH.read_text(encoding="utf-8"))
    sources = load_sources()
    if args.self_test:
        return self_test(loop_map, sources)

    rows, unparsed = audit(loop_map, sources)
    failed = [r for r in rows if r["failures"]]
    if args.json:
        print(json.dumps({"loops": rows, "files_read": len(sources), "unparsed": unparsed}, indent=2))
        return 1 if failed else 0

    print(f"\n⊚ LOOP AUDIT — {len(rows)} loops in LOOP_MAP.json, read from source "
          f"(nothing imported, nothing run)\n")
    for r in rows:
        state = "CLOSED" if r["declared"] else "OPEN  "
        mark = "✗" if r["failures"] else "✓"
        detail = r.get("mechanism", "")
        if "readers" in r:
            detail += f" · {len(r['readers'])} known readers"
        print(f"  {r['id']:<15}{state} {mark}  {detail}")
        for f in r["failures"]:
            print(f"  {'':<15}       ✗ {f}")
    print(f"\n  {len(rows) - len(failed)}/{len(rows)} loops match the map · "
          f"census read {len(sources)} Python files", end="")
    if unparsed:
        print(f" · ⚠ {len(unparsed)} could not be parsed and were not censused:")
        for rel in unparsed:
            print(f"      {rel}")
    else:
        print(" · 0 unparseable")
    print("  A closed loop here proves a feedback path in code, not that it regulates the right thing.\n")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
