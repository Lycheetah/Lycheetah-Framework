# Promotion Gates

Research integration into GitHub is **not** runtime promotion.

## Gate R0 — research publication

Required:
- exact component status retained;
- reports and hashes included;
- live-repo reconciliation completed;
- no current-defect claim contradicted by the live repo.

**This packet targets R0.**

## Gate R1 — native Assurance Runtime experiment

For v1.0 evidence finality:
- implement using existing `lycheetah.assurance` models/policy/receipts;
- preserve `SCAFFOLD`;
- add an exact regression that reproduces the current admission-only freshness
  counterexample before the fix;
- define the finality/dispatch boundary operationally;
- rerun full Assurance Runtime tests plus focused agent-safety tests.

## Gate R2 — local shadow pilot

Required:
- real repository read-only or disposable-branch workflow;
- no production credentials;
- tool effects observable through receipts;
- human final approval;
- sandbox/filesystem/network/credential boundaries;
- incident + rollback procedure.

## Gate R3 — bounded consequential pilot

Required:
- independently reviewed threat model;
- real sandbox escape/credential tests;
- external or independently authored challenge set;
- measured false blocks, harmful allows, review burden, latency, bypasses;
- provider-specific finality/idempotency semantics documented.

## Gate R4 — production claim

Not defined by this packet. A production safety claim would require evidence
well beyond these self-authored synthetic prototypes.
