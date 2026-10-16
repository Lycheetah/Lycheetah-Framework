#!/usr/bin/env bash
# Watchdog-bounded cumulative tests; each suite runs in its own process.
set -uo pipefail
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
LAB="$(cd -- "$HERE/.." && pwd)"
LOG="$HERE/combined_tests_v2.8.log"
: > "$LOG"
TOTAL=0
FAILED=0
TIMEOUT_SECONDS="${LYCHEETAH_TEST_GROUP_TIMEOUT_SECONDS:-45}"
run_group() {
  local label="$1" dir="$2" logfile="$3"; shift 3
  local rc=0 count=0
  printf '===== %s =====\n' "$label" | tee -a "$LOG"
  if (cd -- "$dir" && timeout --foreground "${TIMEOUT_SECONDS}s" python -W error::ResourceWarning -m unittest "$@") >"$logfile" 2>&1; then rc=0; else rc=$?; FAILED=1; fi
  cat "$logfile" >> "$LOG"
  if [[ "$rc" -eq 0 ]]; then
    count="$(grep -Eo '^Ran [0-9]+ tests? in ' "$logfile" | grep -Eo '[0-9]+' | head -1 || true)"; count="${count:-0}"
    TOTAL=$((TOTAL + count)); printf 'GROUP_STATUS=PASS count=%s\n' "$count" | tee -a "$LOG"
  elif [[ "$rc" -eq 124 ]]; then printf 'GROUP_STATUS=TIMEOUT limit=%ss\n' "$TIMEOUT_SECONDS" | tee -a "$LOG"; tail -n 30 "$logfile"
  else printf 'GROUP_STATUS=FAIL rc=%s\n' "$rc" | tee -a "$LOG"; tail -n 30 "$logfile"; fi
}
run_script() {
  local label="$1" dir="$2" logfile="$3" script="$4"; local rc=0 count=0
  printf '===== %s =====\n' "$label" | tee -a "$LOG"
  if (cd -- "$dir" && timeout --foreground "${TIMEOUT_SECONDS}s" python -W error::ResourceWarning "$script") >"$logfile" 2>&1; then rc=0; else rc=$?; FAILED=1; fi
  cat "$logfile" >> "$LOG"
  if [[ "$rc" -eq 0 ]]; then
    count="$(grep -Eo '^Ran [0-9]+ tests? in ' "$logfile" | grep -Eo '[0-9]+' | head -1 || true)"; count="${count:-0}"
    TOTAL=$((TOTAL + count)); printf 'GROUP_STATUS=PASS count=%s\n' "$count" | tee -a "$LOG"
  elif [[ "$rc" -eq 124 ]]; then printf 'GROUP_STATUS=TIMEOUT limit=%ss\n' "$TIMEOUT_SECONDS" | tee -a "$LOG"; tail -n 30 "$logfile"
  else printf 'GROUP_STATUS=FAIL rc=%s\n' "$rc" | tee -a "$LOG"; tail -n 30 "$logfile"; fi
}
run_group "R10 evidence lease/durable outbox" "$LAB/r10_evidence_lease_v2_0" "$HERE/group_r10.log" test_r9_baseline_regression test_evidence_lease_integration
run_group "R11 provider contract" "$LAB/r11_provider_contracts_v2_1" "$HERE/group_r11.log" test_provider_contract test_recovery_policy
run_group "R12 refund recovery policy" "$LAB/r12_stripe_refund_contract_v2_2" "$HERE/group_r12.log" test_stripe_refund_recovery
run_group "R15 Stripe HTTP adapter" "$LAB/r15_stripe_privacy_state_hardening_v2_5" "$HERE/group_r15.log" test_stripe_test_adapter
run_script "R16+R17+R18 inbox, worker and transactional queue" "$HERE" "$HERE/group_r18.log" run_worker_tests_v2_8.py
python -m py_compile "$HERE/stripe_webhook_inbox.py" "$HERE/operation_ledger.py" "$HERE/reconciliation_worker.py" "$HERE/webhook_http_receiver.py"
printf '\nTOTAL_TEST_METHODS_IN_THIS_INVOCATION=%s\nOVERALL_STATUS=%s\n' "$TOTAL" "$(if [[ $FAILED -eq 0 ]]; then echo PASS; else echo FAIL_OR_TIMEOUT; fi)" | tee -a "$LOG"
[[ "$FAILED" -eq 0 ]]
