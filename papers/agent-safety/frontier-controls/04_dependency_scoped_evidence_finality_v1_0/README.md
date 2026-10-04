# Lycheetah Dependency-Scoped Evidence Finality Gate v1.0

**Evidence footing: [SCAFFOLD] research, proposal or source review. Supplied and local synthetic results retain their stated limits; no independent validation or production claim.**

**Status:** `SYNTHETIC_ENGINEERING_VALIDATED`  
**Deployment:** none  
**Dependencies:** Python standard library only

## The blocker closed

The existing Lycheetah agent-safety simulator explicitly records this failure:

```text
evidence valid at admission
        ↓
context/evidence changes
        ↓
already admitted write still completes
```

v1.0 moves evidence validation into the same protected finality transaction as:

- authority-generation revalidation;
- exact action binding;
- resource commitment;
- outbox creation.

## Not all freshness is equal

A global epoch is safe but crude. Any unrelated change can invalidate every
pending action.

v1.0 supports two evidence contracts.

### EXACT

Use when the exact reviewed revision matters:

```text
current version == admitted version
current subject == admitted subject
current value == admitted value
current status == admitted status
```

### SUBJECT_STATUS

Use when a semantic predicate is the real invariant:

```text
current subject == required subject
current status == required status
```

A newer equivalent CI receipt can therefore remain usable.

For a deployment:

```text
artifact A
required-tests(A) == PASS
```

is more precise than:

```text
nothing in the evidence registry changed
```

## Atomic finality

Evidence updates and finality commits both use one SQLite write-serialization
boundary.

Therefore:

```text
FINALITY < INVALIDATING_EVIDENCE_CHANGE
    -> effect may become final

INVALIDATING_EVIDENCE_CHANGE < FINALITY
    -> effect is denied, reservation is released, no outbox is created
```

The claim is about the protected ordering point, not wall-clock simultaneity.

## Checked run

```bash
python3 benchmark.py
```

Frozen validation covers:

- fresh evidence happy path;
- explicit reproduction of admission-only stale-evidence failure;
- required CI status changing PASS -> FAIL;
- newer equivalent PASS preserving liveness;
- exact witness rejecting a newer revision;
- unrelated evidence churn not blocking a dependency-scoped action;
- global-epoch baseline overblocking that same benign churn;
- PASS evidence for the wrong artifact being rejected;
- evidence freshness not overriding revoked authority;
- restart preservation of bound evidence;
- unrelated failing evidence not poisoning an unrelated effect;
- 64 real concurrent evidence-update vs finality races;
- all 781 bounded traces over admission/finality/failure/equivalent-pass/unrelated-change,
  compared with an independently coded dependency-scoped conventional oracle.

## Practical use today

The pattern fits actions such as:

- deploy artifact only while required tests still pass for that artifact;
- publish a report only while the reviewed source revision remains current;
- send a payment only while a fraud/risk decision still satisfies its declared
  predicate;
- execute a migration only while the target schema/state matches its witness;
- release a model only while required evaluation receipts still bind the exact
  model artifact.

## Cybernetic interpretation

Evidence is part of the sensor state.

Admission-only checking samples the plant once, then acts later from a cached
observation.

v1.0 closes the loop at the actuator:

```text
authoritative evidence
        ↓
dependency-scoped comparator
        ↓
same finality transaction
        ↓
effect / no effect
```

The regulated variable is not "evidence age." It is whether the exact safety
predicate needed by the pending effect still holds.

## Limits

- trusted evidence producers;
- no signatures, TPM attestations, or transparency log;
- no remote/distributed evidence;
- no telemetry delay or network partitions;
- no automatic inference of complete semantic predicates;
- no real CI/cloud/provider integration;
- no model-agent evaluation;
- no independent red-team fixtures;
- no proof that the declared predicate captures every relevant hazard.
