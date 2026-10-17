# Load-aware snapshot/commit experiment — protocol v2

Author: Mackenzie Conor James Clark / Lycheetah Framework.
Design and implementation: Caelorynth / Codex, 2026-10-17.
Register: SYNTHETIC. Fixed before the v2 sweep.

The fixed-budget v1 source, protocol and raw results remain the comparison control.
Its loaded work exceeded isolated calibration by 2.42–5.35 times. That observation
motivates this separate variant; the original hypothesis and outcomes are retained.

## Changes to the model

1. At service start, clone the currently admitted store and pending set. Execute
   the actual CASCADE/FIFO adjudication on that frozen snapshot. Measure its
   contradiction comparisons and layer assignments, using the same declared work
   metric as v1. Duration is measured work / independently chosen processing rate.
2. Keep the live store unchanged until completion. At completion, commit only the
   snapshot's changed blocks. Arrivals during service retain their identities and
   state; they cannot influence that adjudication or receive resolution credit.
3. Count completed work and the partially consumed budget of an in-flight job at
   the observation horizon. Charged work must not exceed processing rate * elapsed
   time, and total charged work / processing rate must equal total busy duration.
4. Keep both adjudication policies, all input traces, the calibration method,
   12 concepts, 96 proposals, three topologies, four seeds, nine offered-rate
   reference points, two processing rates, negative control and separate drain
   recovery. Neither arm consults V to generate its outcome.

The counter remains a synthetic semantic-work metric, not CPU seconds: copying,
winner selection, observation and dependency reasoning are not charged. Snapshot
timing and work-budget conservation are stronger model properties, not a claim
of physical timing accuracy or a production governor.

## Questions and fixed outcome screens

- Do the v1 directional load responses survive measured service costs and frozen
  input snapshots? Retain the same descriptive low/high groups and 0.05 screen.
- Does the paired CASCADE–FIFO difference change when extra batch work is charged?
  Report the signed difference; do not tune the policy to preserve an advantage.
- How much semantic conflict remains at nominal V <= 0.5? A clean-store tau may
  poorly predict the capacity of a growing store. Report actual work ratios.
- Does compatible overload still have g = 0 while queueing, and does draining
  still clear all conflicts? These remain distinct from irreversible freezing.
- Do newly arrived blocks survive an older snapshot commit unchanged, and can
  a future arrival affect an earlier service plan? Focused negative witnesses
  must establish both boundaries before interpreting the sweep.

No thermodynamic transition, universal exponent, natural-language truth,
dependency-aware reasoning or substrate independence is inferred from this model.
