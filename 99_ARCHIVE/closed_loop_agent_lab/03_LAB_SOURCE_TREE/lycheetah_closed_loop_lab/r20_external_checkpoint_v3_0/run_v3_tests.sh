#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"
python -W error::ResourceWarning -m py_compile external_checkpoint.py external_checkpoint_cli.py operation_ledger.py stripe_webhook_inbox.py integrity_key_rotation.py test_external_checkpoint.py
python -W error::ResourceWarning -m unittest -v test_external_checkpoint.py 2>&1 | tee focused_tests_v3.0.log
