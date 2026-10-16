#!/usr/bin/env bash
# Diagnostic runner with per-suite watchdog. It intentionally runs each historical
# suite in a separate process to prevent same-named Python modules from colliding.
set -uo pipefail
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
LAB="$(cd -- "$HERE/.." && pwd)"
COMBINED_LOG="$HERE/combined_tests_v2.7.log"
: > "$COMBINED_LOG"
TOTAL=0
FAILED=0
TIMEOUT_SECONDS="${LYCHEETAH_TEST_GROUP_TIMEOUT_SECONDS:-30}"
run_group() {
  local label="$1" dir="$2" logfile="$3"
  shift 3
  local rc=0 count=0
  printf '===== %s =====\n' "$label" | tee -a "$COMBINED_LOG"
  if (cd -- "$dir" && timeout --foreground "${TIMEOUT_SECONDS}s" python -m unittest -v "$@") > "$logfile" 2>&1; then rc=0; else rc=$?; FAILED=1; fi
  cat "$logfile" >> "$COMBINED_LOG"
  if [[ "$rc" -eq 0 ]]; then
    count="$(grep -Eo '^Ran [0-9]+ tests? in ' "$logfile" | grep -Eo '[0-9]+' | head -1 || true)"
    count="${count:-0}"
    TOTAL=$((TOTAL + count))
    printf 'GROUP_STATUS=PASS count=%s\n' "$count" | tee -a "$COMBINED_LOG"
  elif [[ "$rc" -eq 124 ]]; then
    printf 'GROUP_STATUS=TIMEOUT limit=%ss\n' "$TIMEOUT_SECONDS" | tee -a "$COMBINED_LOG"
    tail -n 35 "$logfile"
  else
    printf 'GROUP_STATUS=FAIL rc=%s\n' "$rc" | tee -a "$COMBINED_LOG"
    tail -n 35 "$logfile"
  fi
}
run_script_group() {
  local label="$1" dir="$2" logfile="$3" script="$4"
  local rc=0 count=0
  printf '===== %s =====\n' "$label" | tee -a "$COMBINED_LOG"
  if (cd -- "$dir" && timeout --foreground "${TIMEOUT_SECONDS}s" python "$script") > "$logfile" 2>&1; then rc=0; else rc=$?; FAILED=1; fi
  cat "$logfile" >> "$COMBINED_LOG"
  if [[ "$rc" -eq 0 ]]; then
    count="$(grep -Eo '^Ran [0-9]+ tests? in ' "$logfile" | grep -Eo '[0-9]+' | head -1 || true)"
    count="${count:-0}"
    TOTAL=$((TOTAL + count))
    printf 'GROUP_STATUS=PASS count=%s\n' "$count" | tee -a "$COMBINED_LOG"
  elif [[ "$rc" -eq 124 ]]; then
    printf 'GROUP_STATUS=TIMEOUT limit=%ss\n' "$TIMEOUT_SECONDS" | tee -a "$COMBINED_LOG"
    tail -n 35 "$logfile"
  else
    printf 'GROUP_STATUS=FAIL rc=%s\n' "$rc" | tee -a "$COMBINED_LOG"
    tail -n 35 "$logfile"
  fi
}
run_group "R10 evidence lease/durable outbox" "$LAB/r10_evidence_lease_v2_0" "$HERE/combined_group_1_r10.log" test_r9_baseline_regression test_evidence_lease_integration
run_group "R11 provider contract" "$LAB/r11_provider_contracts_v2_1" "$HERE/combined_group_2_r11.log" test_provider_contract test_recovery_policy
run_group "R12 refund recovery policy" "$LAB/r12_stripe_refund_contract_v2_2" "$HERE/combined_group_3_r12.log" test_stripe_refund_recovery
run_group "R15 Stripe HTTP adapter" "$LAB/r15_stripe_privacy_state_hardening_v2_5" "$HERE/combined_group_4_r15.log" test_stripe_test_adapter
run_script_group "R16+R17 inbox, HTTP receiver and transactional queue" "$HERE" "$HERE/combined_group_5_r17.log" run_webhook_tests_v2_7.py
if [[ "$FAILED" -eq 0 ]]; then STATUS=PASS; else STATUS=FAIL_OR_TIMEOUT; fi
printf '\nTOTAL_TEST_METHODS_IN_THIS_INVOCATION=%s\nOVERALL_STATUS=%s\n' "$TOTAL" "$STATUS" | tee -a "$COMBINED_LOG"
[[ "$FAILED" -eq 0 ]]
