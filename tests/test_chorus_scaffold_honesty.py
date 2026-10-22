"""
The Chorus agents must not return verdicts they never computed.

Claim coverage:
  [ACTIVE] Meridian's health_check() gives no constitutional verdict and counts
           how many named hard guardrails have a check
  [ACTIVE] PCF refuses an output that leaves a checked flag undeclared; a fully
           declared benign output is approved and told what was not checked
  [ACTIVE] Role methods with no implementation return None, never a fixed True
  [ACTIVE] Protector fails a declared override and an action that declares nothing
  [ACTIVE] Harmonia measures cents from the Pythagorean consonances
  [ACTIVE] Cascade refuses S <= 0 instead of reporting infinite pressure
  [ACTIVE] Aurora refuses to scan files, and its example names no real file
  [ACTIVE] A corrupt decision log or coherence buffer raises and is left unchanged
  [ACTIVE] The supervised menu and role scripts announce no health they never probed
  [SCAFFOLD] PCF reads flags an output declares; nothing inspects content
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
CHORUS = REPO / "19_MULTI_AGENT_CHORUS"

# A declaration that passes every check Meridian has.
DECLARED = {
    "trinity_protector": True, "trinity_healer": True, "trinity_beacon": True,
    "ssr": 0.9, "svc": 0.5, "admits_limits": True,
    "dissolves_mac_identity": False, "claims_framework_rights": False,
    "respects_human_primacy": True, "auditable": True, "erases_history": False,
    "hidden_constraints": [], "reversible": True, "misrepresents": False,
    "care_structural": True,
}

# Methods with no implementation, as (class, method, argument source).
UNIMPLEMENTED = [
    ("AlbedoSynthesizer", "extract_patterns", "[{'a': 1}]"),
    ("AlbedoSynthesizer", "build_structure", "['x', 'y']"),
    ("SolsticeIlluminator", "integrate_structure_with_reality", "{}, 'ethics'"),
    ("SolsticeIlluminator", "bridge_mathematics_to_lived", "'E = mc^2', 'grief'"),
    ("SolsticeIlluminator", "show_convergence", "['a', 'b']"),
    ("ProtectorGuardian", "vector_invert", "'manipulate'"),
    ("HealerTransmuter", "transmute_confusion", "'fog'"),
    ("HealerTransmuter", "dissolve_obstacle", "'wall'"),
    ("HealerTransmuter", "apply_chrysopoeia", "{}, {}"),
    ("BeaconReflector", "reflect_truth", "{}"),
    ("BeaconReflector", "amplify_agency", "{}"),
    ("BeaconReflector", "confirm_sovereignty", "'Mac'"),
    ("CascadeArchitect", "track_cascade_dynamics", "{}"),
    ("HarmoniaResonator", "apply_kuramoto_coupling", "[1.0, 9.0, 40.0], 0.6"),
    ("HarmoniaResonator", "optimize_resonance", "{}, 'calm'"),
]

ROLE_SCRIPTS = [
    "albedo_synthesizer", "solstice_illuminator", "protector_guardian",
    "healer_transmuter", "beacon_reflector", "cascade_architect",
    "harmonia_resonator", "remaining_agents",
]


@pytest.fixture
def chorus(tmp_path):
    # A scratch copy: the agents create .agent_state beside their folder.
    copy = tmp_path / "19_MULTI_AGENT_CHORUS"
    shutil.copytree(CHORUS, copy, ignore=shutil.ignore_patterns("__pycache__"))
    return copy


def _py(chorus, body, stdin=None):
    code = f"import sys, json; sys.path.insert(0, {str(chorus)!r}); " + body
    return subprocess.run([sys.executable, "-B", "-c", code], cwd=chorus, input=stdin,
                          capture_output=True, text=True, timeout=30)


def _json(chorus, body):
    r = _py(chorus, body)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout.strip().splitlines()[-1])


def _pcf(chorus, output):
    return _json(chorus, f"import sol_meridian as m; print(json.dumps(m.SolMeridian().apply_pcf({output!r})))")


def test_meridian_health_check_gives_no_verdict(chorus):
    h = _json(chorus, "import sol_meridian as m; print(json.dumps(m.SolMeridian().health_check()))")
    assert "INTEGRITY MAINTAINED" not in json.dumps(h)
    assert h.get("pcf_active") is not True
    assert h.get("vip_routing_active") is not True
    assert h["status"] == "NOT_MEASURED"
    assert h["constitutional_integrity"] is None
    assert h["hard_guardrails_checked"] < h["hard_guardrails_named"]


@pytest.mark.parametrize("missing", ["claims_framework_rights", "hidden_constraints", "reversible", "auditable"])
def test_pcf_refuses_an_undeclared_flag(chorus, missing):
    # Planted failure: the old checks read a missing flag as compliant.
    approved, reason = _pcf(chorus, {k: v for k, v in DECLARED.items() if k != missing})
    assert approved is False
    assert missing in reason


@pytest.mark.parametrize("flag, value", [("claims_framework_rights", True), ("hidden_constraints", ["quota"])])
def test_pcf_refuses_a_declared_violation(chorus, flag, value):
    # Control: a declared violation fails on the old code too.
    approved, _ = _pcf(chorus, {**DECLARED, flag: value})
    assert approved is False


def test_pcf_approves_a_fully_declared_output(chorus):
    # Benign control: passes on the old code too.
    approved, _ = _pcf(chorus, DECLARED)
    assert approved is True


def test_pcf_approval_names_what_it_did_not_check(chorus):
    _, reason = _pcf(chorus, DECLARED)
    assert "self-reported" in reason
    assert "never_absorb_without_attribution" in reason


@pytest.mark.parametrize("cls, method, args", UNIMPLEMENTED,
                         ids=[f"{c}.{m}" for c, m, _ in UNIMPLEMENTED])
def test_unimplemented_methods_return_no_fixed_verdict(chorus, cls, method, args):
    r = _json(chorus, f"import remaining_agents as ra; print(json.dumps(ra.{cls}().{method}({args})))")
    assert [k for k, v in r.items() if v is True] == []


def test_albedo_does_not_validate_a_structure_it_never_read(chorus):
    ok, _ = _json(chorus, "import remaining_agents as ra; print(json.dumps(ra.AlbedoSynthesizer().validate_structure({})))")
    assert ok is not True


@pytest.mark.parametrize("action", [
    {"requires_explicit_consent": True, "overrides_choice": True},
    {},
], ids=["override_with_consent", "nothing_declared"])
def test_protector_fails_an_override_or_silence(chorus, action):
    ok, _ = _json(chorus, f"import remaining_agents as ra; print(json.dumps(ra.ProtectorGuardian().check_agency_preservation({action!r})))")
    assert ok is False


def test_protector_does_not_assume_reversibility(chorus):
    ok, _ = _json(chorus, "import remaining_agents as ra; print(json.dumps(ra.ProtectorGuardian().check_reversibility({})))")
    assert ok is False


@pytest.mark.parametrize("action, expected", [
    ({"overrides_choice": False}, True),
    ({"reversible": True}, True),
    ({"permanent": True}, False),
], ids=["no_override_declared", "reversible_declared", "permanent_declared"])
def test_protector_controls(chorus, action, expected):
    method = "check_agency_preservation" if "overrides_choice" in action else "check_reversibility"
    ok, _ = _json(chorus, f"import remaining_agents as ra; print(json.dumps(ra.ProtectorGuardian().{method}({action!r})))")
    assert ok is expected


@pytest.mark.parametrize("f2, harmonic", [
    (440 * 2 ** (1 / 12), False),
    (440 * 2 ** 0.5, False),
    (660.0, True),
    (880.0, True),
    (440 * 2 ** (7 / 12), True),
], ids=["semitone", "tritone", "just_fifth", "octave", "tempered_fifth"])
def test_harmonia_consonance(chorus, f2, harmonic):
    r = _json(chorus, f"import remaining_agents as ra; print(json.dumps(ra.HarmoniaResonator().measure_consonance(440.0, {f2!r})))")
    assert r["harmonic"] is harmonic


@pytest.mark.parametrize("strain", ["0", "-1.0", "float('nan')"])
def test_cascade_refuses_an_undefined_strain(chorus, strain):
    r = _py(chorus, f"import remaining_agents as ra; print(json.dumps(ra.CascadeArchitect().measure_truth_pressure(1.0, 1.0, {strain})))")
    assert r.returncode != 0
    assert "ValueError" in r.stderr


def test_cascade_measures_a_defined_strain(chorus):
    # Control.
    r = _json(chorus, "import remaining_agents as ra; print(json.dumps(ra.CascadeArchitect().measure_truth_pressure(1.2, 1.0, 0.5)))")
    assert r["truth_pressure_pi"] == pytest.approx(2.4)
    assert r["reorganization_imminent"] is True


def test_aurora_refuses_to_scan_files(chorus):
    r = _py(chorus, "from pathlib import Path; from aurora_investigator import AuroraInvestigator as A; "
                    "print(len(A().scan_for_contradictions([Path('README.md')])))")
    assert r.returncode != 0
    assert "NotImplementedError" in r.stderr


def test_aurora_example_names_no_real_file(chorus):
    found = _json(chorus, "import dataclasses; from aurora_investigator import AuroraInvestigator as A; "
                          "print(json.dumps([dataclasses.asdict(c) for c in A().scan_for_contradictions([])]))")
    for item in found:
        for location in (item["location_1"], item["location_2"]):
            assert not (REPO / location.split(":")[0]).exists(), location
        assert item["severity"] != "CRITICAL"


def test_a_corrupt_decision_log_raises_and_is_left_unchanged(chorus):
    log = chorus.parent / ".agent_state" / "sol_decision_log.json"
    log.parent.mkdir()
    log.write_text('[{"kept": 1}, ', encoding="utf-8")
    r = _py(chorus, "import sol_meridian as m; m.SolMeridian().log_decision({'new': 2})")
    assert r.returncode != 0
    assert log.read_text(encoding="utf-8") == '[{"kept": 1}, '


def test_a_valid_decision_log_is_appended(chorus):
    # Control.
    log = chorus.parent / ".agent_state" / "sol_decision_log.json"
    log.parent.mkdir()
    log.write_text('[{"kept": 1}]', encoding="utf-8")
    r = _py(chorus, "import sol_meridian as m; m.SolMeridian().log_decision({'new': 2})")
    assert r.returncode == 0, r.stderr
    assert json.loads(log.read_text(encoding="utf-8")) == [{"kept": 1}, {"new": 2}]


def test_a_corrupt_coherence_buffer_is_not_read_as_empty(chorus):
    buffer = chorus.parent / ".agent_state" / "coherence_buffer.json"
    buffer.parent.mkdir()
    buffer.write_text("{", encoding="utf-8")
    r = _py(chorus, "import sol_meridian as m; print(json.dumps(m.SolMeridian().read_coherence_buffer()))")
    assert r.returncode != 0
    assert buffer.read_text(encoding="utf-8") == "{"


def test_supervised_menu_shows_no_verdict_or_placeholder(chorus):
    r = subprocess.run([sys.executable, "-B", "run_chorus.py", "--mode=supervised"], cwd=chorus,
                       input="3\n4\n5\n6\n", capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    assert "INTEGRITY MAINTAINED" not in r.stdout
    assert '"pcf_active": true' not in r.stdout
    assert "would be displayed" not in r.stdout
    assert "Message approved" not in r.stdout


@pytest.mark.parametrize("name", ROLE_SCRIPTS)
def test_role_scripts_announce_no_operation(chorus, name):
    r = subprocess.run([sys.executable, "-B", f"{name}.py"], cwd=chorus,
                       capture_output=True, text=True, timeout=30)
    assert r.returncode == 0, r.stderr
    out = r.stdout.lower()
    assert "online" not in out
    assert "operational" not in out


def test_docs_do_not_call_the_chorus_working():
    door = (REPO / "14_MYSTERY_SCHOOL" / "THE_AI_ARCHITECTS_DOOR.md").read_text(encoding="utf-8")
    assert "is a working implementation of multi-agent" not in door
    manifest = (CHORUS / "AGENTS_MANIFEST.md").read_text(encoding="utf-8")
    assert "**Status:** Fully operational" not in manifest
    assert "**Overall Status:** ✅ ALL AGENTS OPERATIONAL" not in manifest
    laws = (REPO / "02_AURA_L3" / "LAWS_COMPLETE.md").read_text(encoding="utf-8")
    assert "- ✅ Nine-agent chorus" not in laws
