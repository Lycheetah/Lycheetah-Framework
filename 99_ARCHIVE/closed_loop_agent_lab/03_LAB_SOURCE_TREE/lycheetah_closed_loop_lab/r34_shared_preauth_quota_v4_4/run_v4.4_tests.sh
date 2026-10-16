#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python verify_source_pins_v4.4.py
python -m py_compile *.py
suite="${1:-checks}"
case "$suite" in
  checks) echo "Source pins and Python compilation passed." ;;
  ingress) python -W error::ResourceWarning -m unittest -v test_shared_ingress_quota ;;
  coordinator) python -W error::ResourceWarning -m unittest -v test_shared_coordinator_quota ;;
  quorum) python -W error::ResourceWarning -m unittest -v test_registry_checkpoint_quorum ;;
  gateway) python -W error::ResourceWarning run_gateway_suite_v4.4.py ;;
  all)
    python -W error::ResourceWarning -m unittest -v test_shared_ingress_quota
    python -W error::ResourceWarning -m unittest -v test_shared_coordinator_quota
    python -W error::ResourceWarning -m unittest -v test_registry_checkpoint_quorum
    python -W error::ResourceWarning run_gateway_suite_v4.4.py
    ;;
  *) echo "Usage: $0 [checks|ingress|coordinator|quorum|gateway|all]" >&2; exit 2 ;;
esac
