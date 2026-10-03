"""
Tests for 34_CYBERNETICS: the loop audit (does each feedback loop close in code the
way LOOP_MAP.json says?) and the requisite-variety demo (SYNTHETIC: a toy world).
"""

import importlib.util
import json
import os

import pytest

CYB = os.path.join(os.path.dirname(__file__), "..", "34_CYBERNETICS")


def _load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(CYB, f"{name}.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


loop_audit = _load("loop_audit")
variety_demo = _load("variety_demo")

CLOSED_IN_CODE = {"L-GREY", "L-CASCADE", "L-TRIAD", "L-TRIADKERNEL", "L-KURAMOTO"}


@pytest.fixture(scope="module")
def audit_inputs():
    loop_map = json.loads(loop_audit.MAP_PATH.read_text(encoding="utf-8"))
    return loop_map, loop_audit.load_sources()


# ── loop audit ────────────────────────────────────────────────────────────────

@pytest.mark.active
def test_every_loop_matches_the_map(audit_inputs):
    rows, unparsed = loop_audit.audit(*audit_inputs)
    assert unparsed == []
    assert {r["id"]: r["failures"] for r in rows if r["failures"]} == {}


@pytest.mark.active
def test_the_closed_loops_are_exactly_the_claimed_ones(audit_inputs):
    rows, _ = loop_audit.audit(*audit_inputs)
    assert {r["id"] for r in rows if r.get("computed")} == CLOSED_IN_CODE


@pytest.mark.active
@pytest.mark.parametrize("mutation", loop_audit.MUTATIONS, ids=lambda m: m[0])
def test_the_audit_catches_each_mutation(audit_inputs, mutation):
    result, failure = loop_audit.run_mutation(*audit_inputs, mutation)
    assert result == "caught", f"{mutation[0]}: {result}"


# ── requisite variety (SYNTHETIC) ─────────────────────────────────────────────

@pytest.mark.conjecture
def test_variety_demo_is_deterministic():
    assert variety_demo.run_demo() == variety_demo.run_demo()


@pytest.mark.conjecture
def test_variety_demo_shows_both_failure_modes():
    r = variety_demo.run_demo()["results"]
    # dictate: perfect where written, wrong everywhere else
    assert r["rulebook"]["seen"]["survived"] == variety_demo.N_SEEN
    assert r["rulebook"]["novel"]["wrong"] == variety_demo.N_DISTURBANCES - variety_demo.N_SEEN
    # constraint with enough variety and an honest sensor: holds on novel disturbances
    assert r["gated_true"]["novel"]["wrong"] == 0
    assert r["gated_true"]["novel"]["refused"] == 0
    # too little generator variety: fails visibly (refuses), never silently
    for split in ("seen", "novel"):
        assert r["gated_narrow"][split]["wrong"] == 0
    assert r["gated_narrow"]["novel"]["refused"] > 0
    # proxy sensor: says yes, fails silently
    assert r["gated_proxy"]["novel"]["refused"] == 0
    assert r["gated_proxy"]["novel"]["survived"] <= 2


@pytest.mark.conjecture
def test_ashby_bound_holds_for_every_regulator():
    for seed in (1952, 1956, 1970):
        results = variety_demo.run_demo(seed)["results"]
        assert all(x["ashby_bound_holds"] for x in results.values()), seed
