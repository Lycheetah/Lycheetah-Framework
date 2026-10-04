# Dispatch/Finality Evidence Revalidation v0.1

**Status:** `[SCAFFOLD]` — native integration candidate prepared against repository
commit `db36241ff1d88cf04f2cae4477db5d59e230d9ee`.

This handoff targets the still-reproduced admission-only evidence-freshness
counterexample in `papers/agent-safety/`.

## Boundary

The existing `AssuranceRuntime` remains a pure provider-neutral policy evaluator.
This addition introduces an optional `FinalityGate` beside it.

The caller:

```text
tool proposal
  -> FinalityGate.admit()
  -> persist AdmissionWitness
  -> immediately before irreversible execution intent:
     FinalityGate.finalize()
  -> proceed only when result.ready is true
```

The gate reruns the current Assurance Runtime and revalidates only the evidence
dependencies bound to the admitted action.

## Evidence modes

`SUBJECT_STATUS` allows a newer evidence revision when the declared predicate
still holds, e.g.:

```text
required-tests(artifact A) == PASS
```

`EXACT` requires the same exact evidence record that existed at admission.

## Evidence-capped behavior

This module is `SCAFFOLD`.

A gate-owned freshness, policy-change, witness-integrity, or action-substitution
failure returns `REVIEW`, not a new hard `BLOCK`. The caller must pause.

If the underlying current Assurance Runtime returns `BLOCK`, that `BLOCK` is
propagated.

This preserves the existing evidence-cap rule instead of promoting a frontier
mechanism by implementation accident.

## What it fixes

It can detect:

```text
evidence PASS at admission
-> evidence becomes FAIL
-> finalize()
-> REVIEW / not ready
```

It also detects:
- exact event mutation;
- policy id/version/digest changes;
- missing evidence at finality;
- exact evidence revision changes;
- wrong-subject evidence;
- current runtime REVIEW/BLOCK.

## What it does not fix

- remote-provider atomicity;
- provider cancellation;
- distributed state;
- crash-safe witness storage;
- authenticated external evidence producers;
- hostile-code containment;
- completeness of the evidence predicate;
- production deployment safety.

The finality call must occur at the actual protected boundary. Calling it early
and then performing unprotected work merely recreates the TOCTOU gap.


## Trust boundary clarified during integration

The witness digest is unkeyed SHA256. A caller that can substitute the witness and recompute its digest can forge it; the gate is not an authenticated admission authority. Protect the witness in trusted storage or add separately reviewed issuer authentication before accepting it from another party. Empty evidence and wrong-key provider records are refused, but those checks do not solve forged witnesses.

The evidence provider and runtime are trusted dependencies. A subject-specific check must set `required_subject_hash`; omitting it explicitly asks only for the declared key/status predicate. Finality is a recheck before a caller's execution boundary, not an atomic transaction with a remote effect. The real-runtime integration fixture checks re-evaluation after a changed record, without a remote provider call.
