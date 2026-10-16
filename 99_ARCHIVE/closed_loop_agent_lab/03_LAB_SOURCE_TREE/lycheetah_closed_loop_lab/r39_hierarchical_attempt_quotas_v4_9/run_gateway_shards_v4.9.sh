#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
: > gateway_v4.9.log
for shard in 1/15 2/15 3/15 4/15 5/15 6/15 7/15 8/15 9/15 10/15 11/15 12/15 13/15 14/15 15/15; do
  name=$(echo "$shard" | tr / _)
  echo "START $shard" >> gateway_v4.9.log
  if python -u -W error::ResourceWarning run_gateway_suite_v4.9.py "$shard" > "gateway_shard_${name}_v4.9.log" 2>&1; then
    grep '^Ran ' "gateway_shard_${name}_v4.9.log" | tail -1 >> gateway_v4.9.log || true
    grep '^LIFECYCLE_SUMMARY' "gateway_shard_${name}_v4.9.log" >> gateway_v4.9.log
  else
    echo "FAILED $shard" >> gateway_v4.9.log
    tail -80 "gateway_shard_${name}_v4.9.log" >> gateway_v4.9.log
    exit 1
  fi
done
