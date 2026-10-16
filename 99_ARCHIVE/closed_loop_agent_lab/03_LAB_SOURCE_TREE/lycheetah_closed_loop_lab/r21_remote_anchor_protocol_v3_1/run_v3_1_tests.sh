#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python -W error::ResourceWarning -m unittest -v test_external_checkpoint.py
python -W error::ResourceWarning run_remote_group1.py
python -W error::ResourceWarning run_remote_group2.py
python -W error::ResourceWarning run_remote_group3.py
