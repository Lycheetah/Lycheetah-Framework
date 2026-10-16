#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"
TERM=xterm python verify_source_pins_v3.7.py > source_pin_verify_v3.7.log
python -m py_compile *.py > python_compile_v3.7.log 2>&1
TERM=xterm python -W error::ResourceWarning -m unittest -v test_registry_checkpoint_quorum > focused_registry_quorum_tests_v3.7.log 2>&1
printf 'Source pins: '; grep '"status"' source_pin_verify_v3.7.log | head -1
printf 'Focused tests: '; grep -E '^Ran [0-9]+ tests' focused_registry_quorum_tests_v3.7.log | tail -1
