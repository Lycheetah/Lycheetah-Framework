#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python -m py_compile checkpoint_witness_quorum.py test_checkpoint_witness_quorum.py
python -W error::ResourceWarning -m unittest -v test_checkpoint_witness_quorum.py
