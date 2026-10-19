#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")"
python -m pytest -q
python experiment_bridge.py
