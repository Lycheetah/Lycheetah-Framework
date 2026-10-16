#!/usr/bin/env bash
set -euo pipefail
python -m py_compile *.py baseline_v3_2/*.py
python -m unittest -v test_checkpoint_witness_quorum test_durable_freshness_verifier
python demo_durable_freshness_v3_4.py
python reproduce_v3_2_findings.py
