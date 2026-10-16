"""Sequential isolated test groups for the full research pack.

Default runs the current v3.2 suite only (quick). Pass --retained to run v3.1
regression groups sequentially, or --group NAME to run a single historical group.
"""
from __future__ import annotations
import argparse, os, signal, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
R21 = ROOT / "r21_remote_anchor_protocol_v3_1"
GROUPS = {
    "v3.2": (HERE, [sys.executable, "-W", "error::ResourceWarning", "-m", "unittest", "-v", "test_checkpoint_witness_quorum.py"], 25),
    "external": (R21, [sys.executable, "-W", "error::ResourceWarning", "-m", "unittest", "-v", "test_external_checkpoint.py"], 35),
    "http1": (R21, [sys.executable, "-W", "error::ResourceWarning", "run_remote_group1.py"], 35),
    "http2": (R21, [sys.executable, "-W", "error::ResourceWarning", "run_remote_group2.py"], 35),
    "http3": (R21, [sys.executable, "-W", "error::ResourceWarning", "run_remote_group3.py"], 35),
}
parser = argparse.ArgumentParser()
parser.add_argument("--retained", action="store_true", help="also run all retained v3.1 groups")
parser.add_argument("--group", choices=tuple(GROUPS), help="run exactly one group")
args = parser.parse_args()
selected = [args.group] if args.group else (list(GROUPS) if args.retained else ["v3.2"])
if any(name != "v3.2" for name in selected) and not R21.exists():
    parser.error("retained v3.1 groups require the full historical lab pack; this standalone bundle only includes r22_checkpoint_quorum_v3_2/")
all_ok = True
for name in selected:
    cwd, command, timeout = GROUPS[name]
    started = time.monotonic()
    try:
        proc = subprocess.Popen(command, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                text=True, start_new_session=True)
        try:
            output, _ = proc.communicate(timeout=timeout)
            ok = proc.returncode == 0
        except subprocess.TimeoutExpired:
            try: os.killpg(proc.pid, signal.SIGTERM)
            except ProcessLookupError: pass
            try: output, _ = proc.communicate(timeout=2)
            except subprocess.TimeoutExpired:
                try: os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError: pass
                output, _ = proc.communicate()
            output += f"\nRUNNER_TIMEOUT after {timeout}s; process group terminated.\n"
            ok = False
    except Exception as exc:
        output = f"Runner error: {type(exc).__name__}: {exc}\n"
        ok = False
    elapsed = time.monotonic() - started
    print(f"{'PASS' if ok else 'FAIL'} {name}: {elapsed:.2f}s")
    print(output[-5000:])
    all_ok = all_ok and ok
sys.exit(0 if all_ok else 1)
