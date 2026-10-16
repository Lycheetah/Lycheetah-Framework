#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python verify_source_pins_v4.8.py
python -m py_compile *.py
python differential_probe_v4.8.py > differential_probe_v4.8.json
suite="${1:-all}"
case "$suite" in
  checks) echo "Source pins, syntax and v4.7/v4.8 hierarchical quota differential probe passed." ;;
  ingress) python -W error::ResourceWarning -m unittest -v test_shared_ingress_quota ;;
  coordinator) python -W error::ResourceWarning -m unittest -v test_shared_coordinator_quota ;;
  quorum) python -W error::ResourceWarning -m unittest -v test_registry_checkpoint_quorum ;;
  gateway)
    for shard in 1/15 2/15 3/15 4/15 5/15 6/15 7/15 8/15 9/15 10/15 11/15 12/15 13/15 14/15 15/15; do
      python -u -W error::ResourceWarning run_gateway_suite_v4.8.py "$shard"
    done
    ;;
  all)
    python -W error::ResourceWarning -m unittest -v test_shared_ingress_quota
    python -W error::ResourceWarning -m unittest -v test_shared_coordinator_quota
    python -W error::ResourceWarning -m unittest -v test_registry_checkpoint_quorum
    for shard in 1/15 2/15 3/15 4/15 5/15 6/15 7/15 8/15 9/15 10/15 11/15 12/15 13/15 14/15 15/15; do
      python -u -W error::ResourceWarning run_gateway_suite_v4.8.py "$shard"
    done
    ;;
  *) echo "Usage: $0 [checks|ingress|coordinator|quorum|gateway|all]" >&2; exit 2 ;;
esac
