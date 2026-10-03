# Agent-safety packet changes

## Working packet v0.4 — 3 October 2026

- Shared one in-memory ledger and operation journal across brokers attached to the
  same control plane. Cross-broker retries and reconciliation retain effect identity
  and bind the original adapter.
- Added ten multi-broker regression methods. The selected broker, authority and
  shared-accounting modules passed 46 methods; the 19 scripted cases per arm retain
  their expected aggregate outcomes.
- The one-unit/two-broker probe now produces one confirmed effect in both arms.
  Admission-only evidence freshness still reproduces as a counterexample.
- Preserved original v0.3 reports; repair evidence lives in `simulator/reports/budget-repair/`.
- Highest witness: local self-authored simulator checks and source/report readback.
  No provider/model call, independent security review or production deployment.

## Original public v0.3 — 3 October 2026

- Published the working paper, simulator, 53-method receipt and 19 scripted cases
  per arm, with two additional counterexamples reproduced in each arm.
- Exposed separate-broker budget multiplication and admission-time freshness
  rather than representing fixture counts as proof of deployment safety.
