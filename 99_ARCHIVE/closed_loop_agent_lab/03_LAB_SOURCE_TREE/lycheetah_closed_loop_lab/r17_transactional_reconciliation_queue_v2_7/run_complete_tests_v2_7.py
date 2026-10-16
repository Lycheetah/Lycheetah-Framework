"""Portable wrapper for the cumulative R10-R17 test runner."""
from pathlib import Path
import os
import sys
script = Path(__file__).with_name("run_complete_tests_v2_7.sh").resolve()
if not script.is_file():
    raise SystemExit("cumulative Bash test runner is missing")
if not Path("/bin/bash").exists():
    raise SystemExit("Bash at /bin/bash is required; invoke the .sh runner on a supported host")
os.execv("/bin/bash", ["/bin/bash", str(script)])
