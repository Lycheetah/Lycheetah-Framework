# Verification Results v3.6

## Executed

- `python verify_source_pins_v3.5.py` — **PASS**; all retained source hashes matched their pinned values.
- `python -m py_compile *.py baseline_v3_2/*.py` — **PASS**.
- `python -W error::ResourceWarning -m unittest -v test_checkpoint_witness_quorum test_durable_freshness_verifier test_remote_monotonic_verifier test_registry_clock_monotonicity` — **82 test methods passed** in one invocation.
- `python reproduce_v3_2_findings.py` — all five frozen v3.2 baseline acceptance findings reproduced (intentional negative controls).
- `python demo_durable_freshness_v3_4.py` — passed; local reuse rejected after consumption.
- `python demo_primary_rollback_v3_5.py` — passed; primary-ledger-only rollback rejected while the registry ledger remains current.

## Count interpretation

- 37 retained checkpoint-quorum methods.
- 19 retained durable-freshness methods.
- 15 retained remote spent-registry methods.
- 11 new clock / request-cache methods.
- Total: **82 passing methods** in one local process invocation. These are reference-package tests, not full upstream Lycheetah CI.

## New behavior established by tests

- Backward wall-clock movement is detected against an authenticated persistent high-water mark, including after service object restart if the registry store remains current.
- An expired challenge is not resurrected by rewinding the injected wall clock.
- Clock record tampering and ordinary SQL deletion are refused.
- A live request-ID cache record cannot be deleted or changed through ordinary SQL.
- Old request IDs are pruned only after they are outside the current replay window; the same signed request then fails timestamp validation.
- Widening the timestamp window under existing stored state fails closed.
- A future-issued challenge cannot be consumed before its issue time.
- Clock sampling takes place inside the serialized transaction, preventing lock scheduling from creating a false rollback alarm.

## Negative controls and limitations

- The five v3.2 baseline accepts remain reproduced for audit continuity.
- The retained v3.5 coordinated-primary-and-registry rollback negative control remains in the suite: restoring the entire registry database also restores its old valid clock floor, so this is not a complete anti-rollback solution.
- The registry and its data are local test artifacts on one host; no genuinely independent service or administrative trust domain was provisioned.
- No hosted service or Stripe endpoint was contacted, no refund was created, no upstream file was changed, and upstream CI was not run.
