"""Evidence pointers in the claims register and the CASCADE result verdicts (review RV19, 2026-10-22).

No register reference may die beyond the 23 already known dead, and the paradigm-shift run
may not call itself confirmed when it only ties the additive baseline.
"""
import ast
import copy
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
REGISTER = json.loads((ROOT / "28_DEFENSE" / "CLAIMS.json").read_text(encoding="utf-8"))
SIM = ROOT / "11_MATHEMATICAL_FOUNDATIONS" / "cascade_simulation.py"
STORED = json.loads((ROOT / "11_MATHEMATICAL_FOUNDATIONS" / "cascade_simulation_results.json").read_text(encoding="utf-8"))

# Dead on 2026-10-22. RV19_claims_pointer_repairs.patch leaves only the three TC_CATALOG ones.
KNOWN_MISSING = frozenset({
    ("ANA-002", "07_ANAMNESIS_L0/TC_CATALOG.md"), ("ANA-003", "07_ANAMNESIS_L0/TC_CATALOG.md"),
    ("ANA-004", "07_ANAMNESIS_L0/TC_CATALOG.md"), ("AUR-009", "02_AURA_L3/AURA_THEOREMS.md"),
    ("CAS-003", "01_CASCADE_L4/CASCADE_THEOREMS.md"), ("CAS-004", "01_CASCADE_L4/CASCADE_THEOREMS.md"),
    ("CAS-005", "01_CASCADE_L4/CASCADE_THEOREMS.md"), ("CAS-006", "01_CASCADE_L4/CASCADE_THEOREMS.md"),
    ("CAS-008", "01_CASCADE_L4/CASCADE_THEOREMS.md"), ("CAS-009", "01_CASCADE_L4/implementations/"),
    ("CAS-010", "01_CASCADE_L4/implementations/"), ("CAS-011", "01_CASCADE_L4/implementations/"),
    ("CRY-002", "08_CHRYSOPOEIA/CHRYSOPOEIA_THEOREMS.md"), ("CRY-003", "08_CHRYSOPOEIA/CHRYSOPOEIA_THEOREMS.md"),
    ("CRY-004", "08_CHRYSOPOEIA/CHRYSOPOEIA_THEOREMS.md"), ("LAM-003", "03_LAMAGUE_L1/LAMAGUE_THEOREMS.md"),
    ("LAM-004", "03_LAMAGUE_L1/LAMAGUE_THEOREMS.md"), ("MIC-003", "05_MICROORCIM_L5/MICROORCIM_THEOREMS.md"),
    ("TRI-003", "04_TRIAD_L2/TRIAD_THEOREMS.md"), ("TRI-004", "04_TRIAD_L2/TRIAD_THEOREMS.md"),
    ("TRI-005", "04_TRIAD_L2/TRIAD_THEOREMS.md"), ("TRI-006", "04_TRIAD_L2/TRIAD_THEOREMS.md"),
    ("TRI-007", "04_TRIAD_L2/TRIAD_THEOREMS.md"),
})


def missing_references(register):
    return {(c["claim_id"], ref.strip()) for c in register["claims"]
            for ref in c["evidence_path"].split(";") if ref.strip() and not (ROOT / ref.strip()).exists()}


def _classify_status():
    """The verdict function alone; importing the module would reconfigure stdout."""
    tree = ast.parse(SIM.read_text(encoding="utf-8"))
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "classify_status")
    namespace = {}
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(SIM), "exec"), namespace)
    return namespace["classify_status"]


def test_no_reference_dies_beyond_the_known_dead():
    assert missing_references(REGISTER) <= KNOWN_MISSING


def test_a_planted_dead_reference_is_caught():
    planted = copy.deepcopy(REGISTER)
    planted["claims"][0]["evidence_path"] += "; 01_CASCADE_L4/NO_SUCH_FILE.md"
    assert not missing_references(planted) <= KNOWN_MISSING


def test_the_empirical_results_carry_their_status_note():
    text = (ROOT / "TRUTH_PRESSURE" / "EMPIRICAL_RESULTS.md").read_text(encoding="utf-8")
    assert "**Status note (review 2026-10-22, RV19): UNVERIFIED.**" in text
    for name in ("50_belief_corpus.json", "annotator_labels.csv", "trial_results_200.csv", "analysis.py"):
        assert not list(ROOT.rglob(name)), name


@pytest.mark.parametrize("mean_pct, gain, expected", [
    (110.05, 0.0, "[NO GAIN OVER ADDITIVE]"),
    (110.05, 0.2, "[MISMATCH]"),
    (40.0, 0.2, "[CONFIRMED]"),
    (45.0, None, "[CONFIRMED]"),
    (20.0, 0.1, "[PARTIAL]"),
    (-2.0, None, "[NEUTRAL]"),
    (-10.0, None, "[REFUTED]"),
])
def test_a_verdict_confirms_only_near_the_claim_and_only_with_a_gain(mean_pct, gain, expected):
    assert _classify_status()(mean_pct, 40.3, gain) == expected


def test_the_stored_run_ties_the_additive_baseline():
    """Frozen counterexample: kept as stored, and the repaired verdict refuses it."""
    for domain in STORED["per_domain"]:
        raw = domain["raw"]["raw"]
        assert raw["cascade"]["coherence"] == raw["additive"]["coherence"], domain["domain"]
        assert domain["raw"]["stats"]["cascade_vs_additive"]["d"] == 0.0
    assert STORED["status"] == "[CONFIRMED]"
    assert _classify_status()(STORED["measured_pct"], STORED["claimed_pct"], 0.0) == "[NO GAIN OVER ADDITIVE]"
