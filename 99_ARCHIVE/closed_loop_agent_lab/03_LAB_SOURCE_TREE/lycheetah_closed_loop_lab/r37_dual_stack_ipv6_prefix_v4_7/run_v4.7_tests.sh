#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python verify_source_pins_v4.7.py
python -m py_compile *.py
python differential_probe_v4.7.py
suite="${1:-all}"
case "$suite" in
  checks) echo "Source pins, syntax and v4.6/v4.7 differential probe passed." ;;
  ingress) python -W error::ResourceWarning -m unittest -v test_shared_ingress_quota ;;
  coordinator) python -W error::ResourceWarning -m unittest -v test_shared_coordinator_quota ;;
  quorum) python -W error::ResourceWarning -m unittest -v test_registry_checkpoint_quorum ;;
  gateway)
    for shard in 1/14 2/14 3/14 4/14 5/14 6/14 7/14 8/14 9/14 10/14 11/14 12/14 13/14 14/14; do
      python -u -W error::ResourceWarning run_gateway_suite_v4.7.py "$shard"
    done
    ;;
  all)
    python -W error::ResourceWarning -m unittest -v test_shared_ingress_quota
    python -W error::ResourceWarning -m unittest -v test_shared_coordinator_quota
    python -W error::ResourceWarning -m unittest -v test_registry_checkpoint_quorum
    for shard in 1/14 2/14 3/14 4/14 5/14 6/14 7/14 8/14 9/14 10/14 11/14 12/14 13/14 14/14; do
      python -u -W error::ResourceWarning run_gateway_suite_v4.7.py "$shard"
    done
    ;;
  *) echo "Usage: $0 [checks|ingress|coordinator|quorum|gateway|all]" >&2; exit 2 ;;
esac
