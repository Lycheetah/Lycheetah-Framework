# Lycheetah Hazard Lineage + Policy Evolution Gate v1.2

**Evidence footing: [SCAFFOLD] research, proposal or source review. Supplied and local synthetic results retain their stated limits; no independent validation or production claim.**

**Status:** `SYNTHETIC_ENGINEERING_VALIDATED`  
**Deployment:** none

## Why this exists

v1.1 guarantees that every obligation in the declared runtime policy is enforced.

It cannot guarantee that policy updates preserve those obligations or assimilate
lessons from incidents.

v1.2 moves one level up:

```text
incident / near miss
      ↓
hazard identity
      ↓
mandatory control group
      ↓
frozen regression fixture
      ↓
candidate policy
      ↓
semantic change-impact analysis
      ↓
activate / STOP
```

## Policy semantics

A policy is:

```text
AND over mandatory groups
OR over explicitly allowed controls inside each group
```

That lets us reason about policy changes semantically:

- adding a mandatory group = stronger;
- deleting a mandatory group = weaker;
- adding an alternative inside an OR group = weaker;
- removing an alternative = stronger;
- replacing alternatives in both directions = incomparable.

v1.2 automatically activates only `EQUIVALENT` or `STRONGER` candidates.

`WEAKER` and `INCOMPARABLE` revisions are stopped for an external review process
that this prototype deliberately does not automate.

## Incident assimilation

HIGH and CRITICAL incidents must be mapped to a candidate policy group whose
obligations trace to the same hazard ID.

The incident also gets a frozen regression scenario.

Activation fails if:

- the incident is unmapped;
- the mapping points at a group that does not control that hazard;
- the candidate fails the frozen incident regression.

This does not mean the incident is solved. `COVERED` means only that the active
runtime policy now contains a traced control for the known hazard.

## Regression

A policy can be structurally stronger and still break legitimate operation.

Therefore activation also evaluates frozen positive and negative fixtures.

This is deliberately analogous to change-impact assessment in maintained safety
cases: a change can damage one part of the assurance argument even when its local
intent sounds safer.

## Validation

The frozen packet includes:

- 10/10 scripted change-management cases;
- incident-derived addition of a signed-artifact requirement;
- wrong and missing incident mappings;
- silent mandatory-group deletion;
- weakening by adding an OR alternative;
- strengthening by removing an alternative;
- incomparable control replacement;
- regression failure despite structural strengthening;
- restart persistence;
- exhaustive comparison of the structural semantic classifier against a
  brute-force truth-table implication oracle over 64 candidate policies;
- a weak baseline showing that "version number increased" accepts semantically
  weaker policies.

## Practical use today

This can sit upstream of v1.1:

```text
Failure Museum / incident report
        ↓
policy evolution gate
        ↓
ACTIVE policy version
        ↓
v1.1 runtime obligation gate
        ↓
v1.0 evidence finality
        ↓
effect finality
```

Useful domains include CI/CD, model release, data export, database migrations,
and any high-impact agent workflow with an explicit obligation matrix.

## Limits

The strongest remaining limitation is fundamental:

```text
known hazards covered != all hazards known
```

A policy-evolution gate can stop accidental weakening and force known incidents
into the control model. It cannot discover every unknown hazard.

That next problem requires independent challenge, diverse analysis methods,
real incident feedback, and empirical red-teaming rather than stronger runtime
bookkeeping alone.
