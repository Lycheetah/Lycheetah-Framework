"""RV10 probes: what the Chorus agents report, run on a scratch copy of the folder.

Usage: python3 -B repro_batch9.py <repo root>
"""
import contextlib, io, shutil, subprocess, sys, tempfile
from pathlib import Path

sys.dont_write_bytecode = True
REPO = Path(sys.argv[1]).resolve()
work = Path(tempfile.mkdtemp(prefix="rv10_"))
chorus = work / "19_MULTI_AGENT_CHORUS"
shutil.copytree(REPO / "19_MULTI_AGENT_CHORUS", chorus, ignore=shutil.ignore_patterns("__pycache__"))
sys.path.insert(0, str(chorus))
with contextlib.redirect_stdout(io.StringIO()):
    import sol_meridian
    import remaining_agents as ra
    import aurora_investigator as au


def show(label, fn):
    try:
        out = fn()
    except BaseException as e:
        out = f"RAISED {type(e).__name__}: {str(e)[:100]}"
    print(f"{label:<46} {out}")


M = sol_meridian.SolMeridian()
h = M.health_check()
show("R1 meridian health_check", lambda: {k: h.get(k) for k in ("status", "pcf_active", "vip_routing_active")})

trinity_and_signature = {"trinity_protector": True, "trinity_healer": True, "trinity_beacon": True,
                         "ssr": 0.9, "svc": 0.5, "admits_limits": True}
show("R2 PCF, no guardrail or invariant flag", lambda: M.apply_pcf(trinity_and_signature)[0])
show("R2 PCF, declares a rights claim (control)",
     lambda: M.apply_pcf({**trinity_and_signature, "claims_framework_rights": True})[0])

P = ra.ProtectorGuardian()
show("R3 agency: consent and override declared",
     lambda: P.check_agency_preservation({"requires_explicit_consent": True, "overrides_choice": True}))
show("R3 agency: nothing declared", lambda: P.check_agency_preservation({}))
show("R3 reversibility: nothing declared", lambda: P.check_reversibility({}))

UNIMPLEMENTED = [
    ("AlbedoSynthesizer", "extract_patterns", ([{"a": 1}],)),
    ("AlbedoSynthesizer", "build_structure", (["x", "y"],)),
    ("SolsticeIlluminator", "integrate_structure_with_reality", ({}, "ethics")),
    ("SolsticeIlluminator", "bridge_mathematics_to_lived", ("E = mc^2", "grief")),
    ("SolsticeIlluminator", "show_convergence", (["a", "b"],)),
    ("ProtectorGuardian", "vector_invert", ("manipulate",)),
    ("HealerTransmuter", "transmute_confusion", ("fog",)),
    ("HealerTransmuter", "dissolve_obstacle", ("wall",)),
    ("HealerTransmuter", "apply_chrysopoeia", ({}, {})),
    ("BeaconReflector", "reflect_truth", ({},)),
    ("BeaconReflector", "amplify_agency", ({},)),
    ("BeaconReflector", "confirm_sovereignty", ("Mac",)),
    ("CascadeArchitect", "track_cascade_dynamics", ({},)),
    ("HarmoniaResonator", "apply_kuramoto_coupling", ([1.0, 9.0, 40.0], 0.6)),
    ("HarmoniaResonator", "optimize_resonance", ({}, "calm")),
]


def fixed_trues():
    hits = []
    for cls, method, args in UNIMPLEMENTED:
        result = getattr(getattr(ra, cls)(), method)(*args)
        hits += [f"{cls}.{method}.{k}" for k, v in result.items() if v is True]
    return f"{len(hits)} True fields from {len(UNIMPLEMENTED)} methods, e.g. {hits[:3]}"


show("R4 unimplemented methods", fixed_trues)
show("R4 Albedo.validate_structure({})", lambda: ra.AlbedoSynthesizer().validate_structure({}))

H = ra.HarmoniaResonator()
for name, f2 in (("semitone", 440 * 2 ** (1 / 12)), ("tritone", 440 * 2 ** 0.5), ("just fifth (control)", 660.0)):
    show(f"R5 Harmonia {name}",
         lambda f2=f2: {k: (round(v, 3) if isinstance(v, float) else v)
                        for k, v in H.measure_consonance(440.0, f2).items() if k in ("consonance", "harmonic")})

C = ra.CascadeArchitect()
for S in (0.0, -1.0):
    show(f"R6 Cascade pi at S={S}", lambda S=S: C.measure_truth_pressure(1.0, 1.0, S)["truth_pressure_pi"])

A = au.AuroraInvestigator()
show("R7 Aurora scan of README.md",
     lambda: [(c.location_1, c.severity) for c in A.scan_for_contradictions([REPO / "README.md"])])


def example():
    ex = A.scan_for_contradictions([])[0]
    f = REPO / ex.location_1.split(":")[0]
    holds = f.exists() and "100% validation" in f.read_text(encoding="utf-8", errors="replace")
    return f"{ex.location_1} severity={ex.severity} file_exists={f.exists()} claim_in_file={holds}"


show("R7 Aurora example", example)

M.decision_log_path.write_text('[{"kept": 1}, ', encoding="utf-8")
show("R8 log_decision on a corrupt log", lambda: M.log_decision({"new": 2}))
show("R8 log afterwards", lambda: M.decision_log_path.read_text(encoding="utf-8"))
M.coherence_buffer_path.write_text("{", encoding="utf-8")
show("R9 read_coherence_buffer on a corrupt buffer", lambda: M.read_coherence_buffer())

r = subprocess.run([sys.executable, "-B", "run_chorus.py", "--mode=supervised"], cwd=chorus,
                   input="3\n4\n5\n6\n", capture_output=True, text=True, timeout=60)
show("R10 supervised menu 3, 4, 5",
     lambda: {"rc": r.returncode, "INTEGRITY MAINTAINED": "INTEGRITY MAINTAINED" in r.stdout,
              "pcf_active true": '"pcf_active": true' in r.stdout,
              "would be displayed": "would be displayed" in r.stdout})


def announcing():
    names = []
    for name in ("albedo_synthesizer", "solstice_illuminator", "protector_guardian", "healer_transmuter",
                 "beacon_reflector", "cascade_architect", "harmonia_resonator", "remaining_agents"):
        out = subprocess.run([sys.executable, "-B", f"{name}.py"], cwd=chorus,
                             capture_output=True, text=True, timeout=30).stdout.lower()
        if "online" in out or "operational" in out:
            names.append(name)
    return f"{len(names)} of 8: {names}"


show("R11 role scripts announcing online/operational", announcing)
shutil.rmtree(work)
