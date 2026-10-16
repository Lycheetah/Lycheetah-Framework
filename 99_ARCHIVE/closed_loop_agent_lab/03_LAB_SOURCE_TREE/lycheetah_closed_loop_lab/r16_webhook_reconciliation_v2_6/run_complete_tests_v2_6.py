"""Portable entry point for the Bash-based cumulative regression runner.

Each historical suite runs directly in its own shell process/directory. This
avoids Python module-name collisions and preserves each version's imports.
Requires Bash on Linux/macOS, as used by this research lab.
"""
from pathlib import Path
import os
import sys

script = Path(__file__).with_name("run_complete_tests_v2_6.sh").resolve()
if not script.is_file():
    raise SystemExit("cumulative Bash test runner is missing")
if not Path("/bin/bash").exists():
    raise SystemExit("Bash at /bin/bash is required; invoke the .sh runner on a supported host")
os.execv("/bin/bash", ["/bin/bash", str(script)])
