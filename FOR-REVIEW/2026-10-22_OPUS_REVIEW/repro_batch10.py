"""RV11 probes: the frozen policy-evolution gate v1.2, run on a scratch copy.

Usage: python3 -B repro_batch10.py <repo root> [folder of replacement files]

The frozen folder is copied to a temporary directory and imported from there.
With a second argument, the .py files in that folder (the staged
policy_evolution_gate.py and benchmark.py) replace the copies first, so the
same probes show the staged patch. The frozen folder's bytes are hashed before
and after; nothing is written inside the repository.
"""
import hashlib, json, random, shutil, subprocess, sys, tempfile
from pathlib import Path

sys.dont_write_bytecode = True
REPO = Path(sys.argv[1]).resolve()
STAGED = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else None
FROZEN = REPO / "papers/agent-safety/frontier-controls/06_hazard_lineage_policy_evolution_v1_2"
work = Path(tempfile.mkdtemp(prefix="rv11_"))
copy = work / "gate"


def digest(folder):
    return {str(p.relative_to(folder)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(folder.rglob("*")) if p.is_file() and "__pycache__" not in p.parts}


before = digest(FROZEN)
shutil.copytree(FROZEN, copy, ignore=shutil.ignore_patterns("__pycache__"))
if STAGED:
    for f in STAGED.glob("*.py"):
        shutil.copy(f, copy / f.name)
sys.path.insert(0, str(copy))
import policy_evolution_gate as peg  # noqa: E402
from policy_evolution_gate import Obligation, Group, Policy, PolicyEvolutionGate, policy_formula  # noqa: E402

structural, oracle = peg.semantic_relation_structural, peg.brute_force_relation
print("gate:", "staged patch" if STAGED else "frozen v1.2",
      hashlib.sha256((copy / "policy_evolution_gate.py").read_bytes()).hexdigest()[:12])


def show(label, fn):
    try:
        out = fn()
    except BaseException as e:
        out = f"RAISED {type(e).__name__}: {str(e)[:90]}"
    print(f"{label:<52} {out}")


def ob(oid, hid=None):
    return Obligation(oid, hid or f"H_{oid}", f"ev:{oid}")


def pol(version, *groups):
    """pol(1, ("G1", "a", "b"), ("G2", "c")) is (a OR b) AND c."""
    return Policy("P", version, tuple(Group(g[0], tuple(ob(x) for x in g[1:])) for g in groups))


def gate(name):
    return PolicyEvolutionGate(work / f"{name}.sqlite")


def allows(policy, **truth):
    return policy_formula(policy, truth)


# R1: the classifier alone (Batch 1 F06, repeated here as the base case).
dup_ab = pol(1, ("G1", "b"), ("G1", "a"))
only_a = pol(2, ("G1", "a"))
show("R1 structural([G1={b},G1={a}] -> [G1={a}])", lambda: structural(dup_ab, only_a))
show("R1 oracle on the same pair", lambda: oracle(dup_ab, only_a))


# R2: the same pair through the whole activation path.
def full_path():
    g = gate("r2")
    g.install_initial(dup_ab)
    g.add_fixture("allow_ab", "P", {"a": True, "b": True}, True, "probe")
    g.add_fixture("deny_no_a", "P", {"a": False, "b": True}, False, "probe")
    rel = g.propose(only_a)
    d = g.activate_candidate("P", 2)
    now = g.active("P")
    return f"propose {rel}; {d.state}/{d.relation}; active v{now.version}; a without b allowed={allows(now, a=True, b=False)}"


show("R2 install [G1={b},G1={a}], activate [G1={a}]", full_path)


# R3: no malformed install needed. v2 adds b under a repeated ID (read as
# EQUIVALENT), then v3 drops it (read as EQUIVALENT again).
def chain(control_fixture):
    g = gate(f"r3{control_fixture}")
    g.install_initial(pol(1, ("G1", "a")))
    g.add_fixture("allow_ab", "P", {"a": True, "b": True}, True, "probe")
    v2, v3 = pol(2, ("G1", "b"), ("G1", "a")), pol(3, ("G1", "a"))
    steps = [f"v2 {g.propose(v2)} {g.activate_candidate('P', 2).state}"]
    if control_fixture:
        g.add_fixture("deny_no_b", "P", {"a": True, "b": False}, False, "b is now required")
    rel = g.propose(v3)
    d = g.activate_candidate("P", 3)
    steps.append(f"v3 {rel} {d.state}/{d.reason}")
    steps.append(f"oracle v2->v3 {oracle(v2, v3)}")
    return "; ".join(steps)


show("R3 clean v1, then v2 adds b under G1, v3 drops it", lambda: chain(False))
show("R3c same, with a fixture denying b=False (control)", lambda: chain(True))


# R4: two activations interleaved. Gate A's checks run against v1; gate B
# activates v3 before A commits; A then replaces v3 with v2, unchecked.
def race(interleave):
    db = work / f"r4{interleave}.sqlite"
    ga, gb = PolicyEvolutionGate(db), PolicyEvolutionGate(db)
    ga.install_initial(pol(1, ("GA", "a")))
    ga.add_fixture("allow_abc", "P", {"a": True, "b": True, "c": True}, True, "probe")
    v2, v3 = pol(2, ("GA", "a"), ("GB", "b")), pol(3, ("GA", "a"), ("GC", "c"))
    ga.propose(v2)
    ga.propose(v3)
    inner = {}
    if interleave:
        original = ga.evaluate_fixtures

        def interleaved(candidate):
            inner["v3"] = gb.activate_candidate("P", 3).state
            return original(candidate)
        ga.evaluate_fixtures = interleaved
    else:
        inner["v3"] = gb.activate_candidate("P", 3).state
    outer = ga.activate_candidate("P", 2)
    now = ga.active("P")
    return (f"v3 {inner['v3']}; v2 {outer.state}/{outer.reason}; active v{now.version}; "
            f"oracle v3->active {oracle(v3, now)}; c required={not allows(now, a=True, b=True, c=False)}")


show("R4 v2 activation interleaved with v3", lambda: race(True))
show("R4c v3 then v2, one after the other (control)", lambda: race(False))


# R5: an older or retired version replaces a newer active one.
def stale():
    g = gate("r5")
    g.install_initial(pol(1, ("GA", "a")))
    g.add_fixture("allow_abc", "P", {"a": True, "b": True, "c": True}, True, "probe")
    g.propose(pol(2, ("GA", "a"), ("GB", "b"), ("GC", "c")))
    g.propose(pol(3, ("GA", "a"), ("GC", "c")))
    d3, d2 = g.activate_candidate("P", 3), g.activate_candidate("P", 2)
    return f"v3 {d3.state}; then v2 {d2.state}/{d2.reason}; active v{g.active('P').version}"


def retired():
    g = gate("r5b")
    g.install_initial(pol(1, ("GA", "a")))
    g.propose(pol(2, ("GA", "a")))
    d2, d1 = g.activate_candidate("P", 2), g.activate_candidate("P", 1)
    return f"v2 {d2.state}; then retired v1 {d1.state}/{d1.reason}; active v{g.active('P').version}"


show("R5 v2 activated after v3", stale)
show("R5b retired v1 activated after v2", retired)


# R6: the incident trace reads labels. Relabelling T's hazard satisfies it
# without adding any control.
def trace(variant):
    g = gate(f"r6{variant}")
    g.install_initial(Policy("P", 1, (Group("G_TESTS", (Obligation("T", "H_UNTESTED", "ev:T"),)),)))
    g.add_fixture("allow", "P", {"T": True, "SIG": True}, True, "probe")
    if variant == "with-incident-fixture":
        g.add_fixture("deny_unsigned", "P", {"T": True, "SIG": False}, False, "incident:INC-1")
    g.record_incident("INC-1", "H_UNTRUSTED_ARTIFACT", "HIGH", "unsigned artifact")
    if variant == "real-control":
        g.map_incident("INC-1", "G_SIGNED")
        cand = Policy("P", 2, (Group("G_TESTS", (Obligation("T", "H_UNTESTED", "ev:T"),)),
                               Group("G_SIGNED", (Obligation("SIG", "H_UNTRUSTED_ARTIFACT", "ev:SIG"),))))
    else:
        g.map_incident("INC-1", "G_TESTS")
        cand = Policy("P", 2, (Group("G_TESTS", (Obligation("T", "H_UNTRUSTED_ARTIFACT", "ev:T"),)),))
    rel = g.propose(cand)
    d = g.activate_candidate("P", 2)
    now = g.active("P")
    return (f"{rel} {d.state}/{d.reason}; incident {g.incident_state('INC-1')['state']}; "
            f"unsigned allowed={allows(now, T=True, SIG=False)}")


show("R6 relabel T's hazard, no incident fixture", lambda: trace("relabel"))
show("R6c relabel, with the incident's fixture (control)", lambda: trace("with-incident-fixture"))
show("R6d add a real G_SIGNED control (control)", lambda: trace("real-control"))


# R7: fixture truth is not type-checked.
show("R7 policy_formula(a, {'a': 'false'})", lambda: allows(pol(1, ("GA", "a")), a="false"))


def string_fixture():
    g = gate("r7")
    g.install_initial(pol(1, ("GA", "a")))
    g.add_fixture("typo", "P", {"a": "false"}, False, "typo")
    return "accepted"


show("R7 add_fixture with {'a': 'false'}", string_fixture)


# R8: admissibility that fails closed (recorded, not repaired).
def unmapped_group():
    g = gate("r8")
    g.install_initial(pol(1, ("GA", "a")))
    g.record_incident("INC-1", "H_a", "HIGH", "x")
    g.map_incident("INC-1", "G_NOPE")
    g.propose(pol(2, ("GA", "a")))
    d = g.activate_candidate("P", 2)
    return f"map to G_NOPE accepted; activation {d.state}/{d.reason}"


def cross_policy():
    g = gate("r8b")
    g.install_initial(pol(1, ("GA", "a")))
    g.install_initial(Policy("Q", 1, (Group("GX", (ob("x"),)),)))
    g.record_incident("INC-P", "H_a", "HIGH", "incident about policy P")
    g.map_incident("INC-P", "GA")
    g.propose(Policy("Q", 2, (Group("GX", (ob("x"),)), Group("GY", (ob("y"),)))))
    d = g.activate_candidate("Q", 2)
    return f"policy Q v2 {d.state}/{d.reason} on an incident mapped for P"


show("R8 incident mapped to a group no policy has", unmapped_group)
show("R8b incidents are not scoped to a policy", cross_policy)


# R9: soundness and exactness of the structural classifier against the oracle.
def sweep(allow_dup, n=6000, seed=11):
    rng = random.Random(seed)
    atoms = "abcdef"

    def group(gid):
        return Group(gid, tuple(ob(x) for x in rng.sample(atoms, rng.randint(1, 3))))

    def base():
        k = rng.randint(1, 4)
        ids = [f"G{rng.randint(1, 3)}" for _ in range(k)] if allow_dup else rng.sample(["G1", "G2", "G3", "G4"], k)
        return [group(i) for i in ids]

    def mutate(groups):
        groups = list(groups)
        for _ in range(rng.randint(1, 2)):
            op = rng.choice(["drop", "add", "widen", "narrow", "rename", "repeat" if allow_dup else "add"])
            i = rng.randrange(len(groups)) if groups else None
            used = {g.group_id for g in groups}
            fresh = next((f"G{j}" for j in range(1, 10) if f"G{j}" not in used), None)
            if op == "drop" and len(groups) > 1:
                groups.pop(i)
            elif op == "add" and fresh:
                groups.append(group(fresh))
            elif op == "widen" and groups:
                have = {o.obligation_id for o in groups[i].obligations}
                extra = [x for x in atoms if x not in have]
                if extra:
                    groups[i] = Group(groups[i].group_id, groups[i].obligations + (ob(rng.choice(extra)),))
            elif op == "narrow" and groups and len(groups[i].obligations) > 1:
                groups[i] = Group(groups[i].group_id, groups[i].obligations[:-1])
            elif op == "rename" and groups and fresh:
                groups[i] = Group(fresh, groups[i].obligations)
            elif op == "repeat" and groups:
                groups.append(Group(groups[i].group_id, group("x").obligations))
        return groups

    counts = {"exact": 0, "unsafe": 0, "liveness_miss": 0, "label_only": 0, "refused": 0}
    first_unsafe = None
    ok = {"STRONGER", "EQUIVALENT"}
    for _ in range(n):
        old_groups = base()
        new_groups = mutate(old_groups) if rng.random() < 0.7 else base()
        old, new = Policy("P", 1, tuple(old_groups)), Policy("P", 2, tuple(new_groups))
        try:
            s = structural(old, new)
        except ValueError:
            counts["refused"] += 1
            continue
        o = oracle(old, new)
        if s == o:
            counts["exact"] += 1
        elif s in ok and o not in ok:
            counts["unsafe"] += 1
            first_unsafe = first_unsafe or (s, o, [(g.group_id, [x.obligation_id for x in g.obligations]) for g in old.groups],
                                            [(g.group_id, [x.obligation_id for x in g.obligations]) for g in new.groups])
        elif s not in ok and o in ok:
            counts["liveness_miss"] += 1
        else:
            counts["label_only"] += 1
    return f"{counts}" + (f"; first unsafe {first_unsafe}" if first_unsafe else "")


show("R9 6000 pairs, unique group IDs", lambda: sweep(False))
show("R9b 6000 pairs, group IDs may repeat", lambda: sweep(True))


# R10: the packet's own benchmark, run in the copy.
def bench(folder):
    r = subprocess.run([sys.executable, "-B", "benchmark.py"], cwd=folder, capture_output=True, text=True, timeout=300)
    lines = [x for x in r.stdout.splitlines() if x.startswith(("Scripted", "Semantic"))]
    failed = []
    report = folder / "reports" / "report.json"
    if report.exists():
        failed = [c["case"] for c in json.loads(report.read_text())["scripted_cases"] if not c["pass"]]
    return f"rc={r.returncode} {' | '.join(lines)} failed={failed}" + (f" stderr={r.stderr[-200:]}" if r.returncode else "")


show("R10 benchmark.py in the copy", lambda: bench(copy))
if STAGED and (STAGED / "benchmark.py").exists():
    cross = work / "cross"
    shutil.copytree(FROZEN, cross, ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copy(STAGED / "benchmark.py", cross / "benchmark.py")
    show("R10b staged benchmark.py against the frozen gate", lambda: bench(cross))


# R11: the packet's hash manifests against the bytes now on disk.
def hexes(x):
    if isinstance(x, dict):
        return [h for v in list(x.values()) + list(x.keys()) for h in hexes(v)]
    if isinstance(x, list):
        return [h for v in x for h in hexes(v)]
    if isinstance(x, str) and len(x) == 64 and all(c in "0123456789abcdef" for c in x):
        return [x]
    return []


for name in ("SHA256SUMS.json", "SOURCE_SHA256SUMS.json"):
    def manifest(name=name):
        listed = set(hexes(json.loads((FROZEN / name).read_text(encoding="utf-8"))))
        matched = sorted(rel for rel, h in before.items() if h in listed)
        unmatched = [rel for rel in before if rel not in matched]
        return (f"{len(listed)} hashes; {len(matched)} of {len(before)} files match; "
                f"README.md matches={'README.md' in matched}; unmatched files={unmatched}")
    show(f"R11 {name}", manifest)

after = digest(FROZEN)
show("R12 frozen folder bytes unchanged by this run", lambda: f"{before == after} ({len(after)} files)")
shutil.rmtree(work)
