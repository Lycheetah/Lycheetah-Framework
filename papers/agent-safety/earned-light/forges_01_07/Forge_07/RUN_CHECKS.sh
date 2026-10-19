#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python -m unittest discover -s tests -v
python -u lab.py
