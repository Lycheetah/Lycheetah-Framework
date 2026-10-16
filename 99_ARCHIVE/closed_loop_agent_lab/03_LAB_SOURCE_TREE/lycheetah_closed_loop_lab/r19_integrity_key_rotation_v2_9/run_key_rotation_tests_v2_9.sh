#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd -- "$HERE"
exec python -W error::ResourceWarning -m unittest -v test_integrity_key_rotation
