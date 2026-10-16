#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
OLD="$(cd "$HERE/.." && pwd)/r26_registry_clock_monotonicity_v3_6"
cd "$OLD"
TERM=xterm python -W error::ResourceWarning -m unittest -v \
  test_checkpoint_witness_quorum \
  test_durable_freshness_verifier \
  test_remote_monotonic_verifier \
  test_registry_clock_monotonicity
