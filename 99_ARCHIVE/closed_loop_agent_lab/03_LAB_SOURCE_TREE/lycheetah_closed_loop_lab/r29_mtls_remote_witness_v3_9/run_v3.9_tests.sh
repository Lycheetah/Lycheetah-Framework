#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python -u verify_source_pins_v3.9.py | tee source_pin_verify_v3.9.log
python -u -m py_compile *.py > python_compile_v3.9.log 2>&1
python -u -W error::ResourceWarning -m unittest -v test_registry_checkpoint_quorum > retained_quorum_test_v3.9.log 2>&1
python -u -W error::ResourceWarning -m unittest -v test_remote_witness_process > mtls_remote_process_test_v3.9.log 2>&1
printf 'Source pin: PASS\nCompile: PASS\n'
grep -E '^Ran [0-9]+ tests|^OK$' retained_quorum_test_v3.9.log | tail -n 2
grep -E '^Ran [0-9]+ tests|^OK$' mtls_remote_process_test_v3.9.log | tail -n 2
