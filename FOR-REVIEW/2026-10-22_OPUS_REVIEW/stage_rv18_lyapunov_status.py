"""Stage RV18_lyapunov_honest_status.patch for 11_MATHEMATICAL_FOUNDATIONS/lyapunov_verification.py.

Usage: python3 -B stage_rv18_lyapunov_status.py <framework-root> <scratch-dir>

The committed lyapunov_verification_results.json was produced with sympy, which this
machine lacks, so the results cannot be regenerated faithfully here. The status logic is
therefore staged as a patch, not edited in place (decision G-LYAP). Four records claim
more than their evidence shows:
  - the CASCADE Lyapunov condition is numerical, but is recorded [VERIFIED] ("symbolic
    proof confirmed by sympy") and passes even when sympy is absent;
  - the Theorem 2.3 Hessian record reads a fixed table and prints "CONFIRMED";
  - the CHRYSOPOEIA entropy record passes at mean final entropy 1.09 nats (max ln 8 = 2.08);
  - the PSI record passes although its known-bad 44% case also converges.
Each swap is exact-one against the HEAD bytes, and the patch is checked by applying it to
a HEAD copy.
"""
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
WORK = Path(sys.argv[2]).resolve() / "rv18_patch"
OUT = ROOT / "FOR-REVIEW" / "2026-10-22_OPUS_REVIEW" / "RV18_lyapunov_honest_status.patch"
REL = "11_MATHEMATICAL_FOUNDATIONS/lyapunov_verification.py"

SWAPS = [
    ("All results tagged: [VERIFIED], [NUMERICAL], or [PENDING].\n",
     "All results tagged: [VERIFIED], [NUMERICAL], [ASSIGNED], [INCONCLUSIVE], [PENDING]\n"
     "or [FAILED]. Only [VERIFIED] and [NUMERICAL] count as passing.\n"),
    ('FAIL = "[FAILED]"\n',
     'FAIL = "[FAILED]"\n'
     'ASSIGNED = "[ASSIGNED]"          # value set by the script, not computed\n'
     'INCONCLUSIVE = "[INCONCLUSIVE]"  # the run does not separate the claim from its known-bad case\n'),
    ('            "[FAILED]": "FAIL"}.get(status, "????")\n',
     '            "[FAILED]": "FAIL", "[ASSIGNED]": "ASGN",\n'
     '            "[INCONCLUSIVE]": "INCL"}.get(status, "????")\n'),
    ('    record("CASCADE: Hessian eigenvalue decrease (Theorem 2.3)",\n'
     '           NUMERICAL,\n',
     '    record("CASCADE: Hessian eigenvalue decrease (Theorem 2.3)",\n'
     '           ASSIGNED,\n'),
    ('           f"Delta: {lam_after - lam_before:+.2f} < 0 CONFIRMED",\n',
     '           f"Delta: {lam_after - lam_before:+.2f} (read from a fixed table, not computed)",\n'),
    ('           PASS if lyapunov_holds else FAIL,\n',
     '           NUMERICAL if lyapunov_holds else FAIL,\n'),
    ('           f"Verified across {N_TRIALS} random knowledge states\\n"\n',
     '           f"Checked numerically across {N_TRIALS} random knowledge states,\\n"\n'
     '           f"on this script\'s cascade_step, not the engine; no symbolic proof\\n"\n'),
    ('            record("CHRYSOPOEIA: entropy convergence (real seven_phase.py)",\n'
     '                   NUMERICAL,\n'
     '                   f"Trials: {n_trials}, Mean final entropy: {mean_H:.4f}\\n"\n'
     '                   f"Mean crystallisation (1 - H_f/H_i): {mean_C:.4f}" if mean_C else "N/A",\n',
     '            # Convergence to the crystallised fixed point means final entropy near 0.\n'
     '            record("CHRYSOPOEIA: entropy convergence (real seven_phase.py)",\n'
     '                   NUMERICAL if mean_H < 0.01 else FAIL,\n'
     '                   f"Trials: {n_trials}, Mean final entropy: {mean_H:.4f} "\n'
     '                   f"(converged means < 0.01; maximum ln 8 = {np.log(8):.4f})\\n"\n'
     '                   + (f"Mean crystallisation (1 - H_f/H_i): {mean_C:.4f}" if mean_C is not None else "N/A"),\n'),
    ('    record("PSI-CONSENSUS: 33% Byzantine — honest agents converge",\n'
     '           NUMERICAL,\n',
     '    # The claim is a threshold: it needs the 44% case to diverge as well as 33% to converge.\n'
     '    separates = spread_33pct < 0.15 and spread_40pct > 0.15\n'
     '    record("PSI-CONSENSUS: 33% Byzantine — honest agents converge",\n'
     '           NUMERICAL if separates else INCONCLUSIVE,\n'),
    ('    counts = {PASS: 0, NUMERICAL: 0, PENDING: 0, FAIL: 0}\n',
     '    counts = {PASS: 0, NUMERICAL: 0, ASSIGNED: 0, INCONCLUSIVE: 0, PENDING: 0, FAIL: 0}\n'),
    ('    print(f"  [PENDING]  Needs more work: {counts[PENDING]}")\n',
     '    print(f"  [ASSIGNED] Set, not computed: {counts[ASSIGNED]}")\n'
     '    print(f"  [INCONCLUSIVE] No separation: {counts[INCONCLUSIVE]}")\n'
     '    print(f"  [PENDING]  Needs more work: {counts[PENDING]}")\n'),
    ('    print("  [PENDING] = requires additional work (dependency missing)")\n',
     '    print("  [ASSIGNED] = value set by the script, not computed; not passing")\n'
     '    print("  [INCONCLUSIVE] = known-bad case passes too; not passing")\n'
     '    print("  [PENDING] = requires additional work (dependency missing)")\n'),
]

if WORK.exists():
    shutil.rmtree(WORK)
text = subprocess.run(["git", "show", f"HEAD:{REL}"], cwd=ROOT, capture_output=True, check=True).stdout.decode()
(WORK / "a" / REL).parent.mkdir(parents=True)
(WORK / "a" / REL).write_bytes(text.encode())
for old, new in SWAPS:
    assert text.count(old) == 1, (old[:60], text.count(old))
    text = text.replace(old, new)
compile(text, REL, "exec")
(WORK / "b" / REL).parent.mkdir(parents=True)
(WORK / "b" / REL).write_bytes(text.encode())

diff = subprocess.run(["diff", "-ruN", "a", "b"], cwd=WORK, capture_output=True).stdout
assert diff and b"\r" not in diff
OUT.write_bytes(diff)
check = WORK / "check"
shutil.copytree(WORK / "a", check)
subprocess.run(["patch", "-p1", "--quiet", "-i", str(OUT)], cwd=check, check=True)
same = (check / REL).read_bytes() == (WORK / "b" / REL).read_bytes()
print(f"patch {OUT.name}: {len(diff)} bytes, {len(SWAPS)} swaps, applies to HEAD and matches: {same}, CR bytes: 0")
assert same
