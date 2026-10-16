#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python verify_source_pins_v3.5.py
python -m py_compile *.py baseline_v3_2/*.py
python -m unittest -v test_checkpoint_witness_quorum test_durable_freshness_verifier test_remote_monotonic_verifier
python reproduce_v3_2_findings.py
python demo_durable_freshness_v3_4.py
python demo_primary_rollback_v3_5.py
