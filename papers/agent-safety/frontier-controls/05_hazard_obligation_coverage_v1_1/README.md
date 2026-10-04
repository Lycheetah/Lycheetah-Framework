# Lycheetah Hazard Obligation Coverage Gate v1.1

**Evidence footing: [SCAFFOLD] research, proposal or source review. Supplied and local synthetic results retain their stated limits; no independent validation or production claim.**

**Status:** `SYNTHETIC_ENGINEERING_VALIDATED`  
**Deployment:** none  
**Dependencies:** Python standard library only

## Problem

v1.0 ensured evidence was still valid at finality.

That does not answer a harder question:

> Was the evidence set complete enough for the declared hazard policy?

A model can present several true green checks while omitting a mandatory check
entirely.

v1.1 removes the caller's ability to choose the checklist. A protected policy
maps an effect class to mandatory hazard-control groups.

## Closed-world policy semantics

For policy `P`, each group is an OR over allowed controls, while all groups are
required:

```text
SAFE(P,a,E)
iff
    for every mandatory group g:
        at least one allowed obligation o in g is currently satisfied
```

Production-deploy example:

```text
G_TESTS      = required CI PASS
G_SECURITY   = security scan PASS
G_REVERSIBLE = rollback plan PASS OR blue/green reversible PASS
G_CANARY     = canary health PASS
```

Thus:

```text
tests PASS + canary PASS
```

does not mean "all supplied checks passed." It means "mandatory groups are
missing" and is denied.

## Finality

The active policy version is captured at admission.

At finality, inside the same SQLite serialization transaction, the gate checks:

1. exact action identity;
2. live authority generation;
3. active policy version still equals admitted version;
4. every mandatory hazard-control group is still satisfied;
5. resource state remains coherent;
6. only then moves reservation to committed exposure and creates the outbox.

A policy upgrade before finality invalidates the old admission instead of silently
grandfathering it.

## Alternatives without score compensation

The gate is non-compensatory at the group level.

A security failure cannot be offset by two unrelated passing controls.

Within a hazard group, explicitly authorized alternatives are allowed:

```text
rollback-plan PASS
OR
bluegreen-ready PASS
```

This gives useful liveness without turning safety into a weighted average.

## Validation

Run:

```bash
python3 benchmark.py
```

Frozen validation includes:

- complete-policy success;
- explicit omitted-obligation counterexample against a caller-presented-check baseline;
- mandatory singleton failure;
- alternative-control success;
- all alternatives failing;
- policy-version change after admission;
- unrelated policy update;
- required obligation changing after admission;
- PASS for the wrong artifact;
- missing mandatory evidence;
- revocation remaining independent of coverage;
- all 32 Boolean states of the five evidence controls compared with an independent
  conventional closed-world checklist;
- 64 real policy-update versus finality races;
- all nonempty subsets of a four-group caller-presented checklist as an omission
  diagnostic.

## Practical use today

Use this pattern where an agent action has a known mandatory control matrix:

- production deployments;
- model releases;
- schema migrations;
- public publication;
- high-volume messaging;
- secrets rotation;
- sensitive data export.

The model proposes the action. The protected policy determines what must be true.

## What this does NOT solve

Policy-relative completeness is not real-world hazard completeness.

If the policy author forgot an important hazard, the runtime will faithfully
enforce an incomplete policy.

The next safety question therefore moves outside the runtime gate:

```text
How was the mandatory obligation set derived, challenged, reviewed, and updated?
```

That requires hazard analysis, independent challenge, incident feedback, and
versioned governance rather than another boolean runtime check.
