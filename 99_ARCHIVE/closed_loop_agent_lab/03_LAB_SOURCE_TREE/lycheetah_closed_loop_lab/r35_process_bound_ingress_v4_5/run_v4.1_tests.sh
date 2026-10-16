#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python verify_source_pins_v4.1.py
python -m py_compile *.py
suite="${1:-checks}"
case "$suite" in
  checks)
    echo "Source pins and Python compilation passed. Run './run_v4.1_tests.sh quorum' and './run_v4.1_tests.sh gateway' as separate invocations for the full test set."
    ;;
  quorum)
    python -W error::ResourceWarning -m unittest -v test_registry_checkpoint_quorum
    ;;
  gateway)
    python -W error::ResourceWarning -m unittest -v test_remote_witness_process
    ;;
  *)
    echo "Usage: $0 [checks|quorum|gateway]" >&2
    exit 2
    ;;
esac
