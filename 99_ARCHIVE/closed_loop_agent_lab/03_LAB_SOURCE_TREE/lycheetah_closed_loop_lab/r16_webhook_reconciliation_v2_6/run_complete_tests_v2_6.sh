#!/usr/bin/env bash
# Run each historical test suite from its own directory so imports stay version-pinned.
set -uo pipefail

HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
LAB="$(cd -- "$HERE/.." && pwd)"
COMBINED_LOG="$HERE/combined_tests_v2.6.log"
: > "$COMBINED_LOG"
TOTAL=0
FAILED=0

run_group() {
  local label="$1" dir="$2" logfile="$3"
  shift 3
  local rc=0 count=0
  printf '===== %s =====\n' "$label" | tee -a "$COMBINED_LOG"
  if (cd -- "$dir" && python -m unittest -v "$@") > "$logfile" 2>&1; then
    rc=0
  else
    rc=$?
    FAILED=1
  fi
  cat "$logfile" | tee -a "$COMBINED_LOG"
  if [[ "$rc" -eq 0 ]]; then
    count="$(grep -Eo '^Ran [0-9]+ tests? in ' "$logfile" | grep -Eo '[0-9]+' | head -1 || true)"
    count="${count:-0}"
    TOTAL=$((TOTAL + count))
    printf 'GROUP_STATUS=PASS count=%s\n' "$count" | tee -a "$COMBINED_LOG"
  else
    printf 'GROUP_STATUS=FAIL rc=%s\n' "$rc" | tee -a "$COMBINED_LOG"
  fi
}

run_group "R10 durable outbox/evidence lease" "$LAB/r10_evidence_lease_v2_0" "$HERE/combined_group_1_r10_durable_outbox_evidence_lease.log" test_r9_baseline_regression test_evidence_lease_integration
run_group "R11 provider contract" "$LAB/r11_provider_contracts_v2_1" "$HERE/combined_group_2_r11_provider_contract.log" test_provider_contract test_recovery_policy
run_group "R12 Stripe refund policy" "$LAB/r12_stripe_refund_contract_v2_2" "$HERE/combined_group_3_r12_stripe_refund_policy.log" test_stripe_refund_recovery
run_group "R15 Stripe HTTP adapter" "$LAB/r15_stripe_privacy_state_hardening_v2_5" "$HERE/combined_group_4_r15_stripe_http_adapter.log" test_stripe_test_adapter
run_group "R16 webhook inbox and loopback receiver" "$HERE" "$HERE/combined_group_5_r16_webhook_inbox_and_loopback_receiver.log" test_stripe_webhook_inbox test_webhook_http_receiver

if [[ "$FAILED" -eq 0 ]]; then STATUS=PASS; else STATUS=FAIL; fi
printf '\nTOTAL_TEST_METHODS=%s\nOVERALL_STATUS=%s\n' "$TOTAL" "$STATUS" | tee -a "$COMBINED_LOG"
[[ "$FAILED" -eq 0 ]]
