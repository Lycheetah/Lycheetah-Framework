# Agent-Safety Frontier Controls

**Status:** `RESEARCH / SYNTHETIC_ENGINEERING_VALIDATED COMPONENTS / NOT DEPLOYED`

This directory consolidates the post-v0.4 frontier experiments developed after
the public Agent Safety Research Packet exposed concrete accounting and temporal
limits.

It is deliberately separate from the shipped/scaffolded
`lycheetah.assurance` package.

## Read this first

1. `INTEGRATION_MAP.md` — reconciliation with the current public repository.
2. `CLAIM_LEDGER.json` — machine-readable epistemic boundaries.
3. `PROMOTION_GATES.md` — what must happen before any runtime promotion.
4. Component directories `01` through `08` — executable research packets.

## Research sequence

```text
commit-time authority
    ↓
shared resources
    ↓
atomic authority/resource finality
    ↓
dependency-scoped evidence finality
    ↓
hazard obligation coverage
    ↓
policy evolution
    ↓
assurance mutation / Failure Museum
    ↓
external threat boundary audit
```

The sequence should not be read as a cumulative production system. The
components were validated as local synthetic engineering prototypes under
different assumptions.

## Strongest immediate result

The live public agent-safety packet still documents admission-only evidence
freshness as an open counterexample. `04_dependency_scoped_evidence_finality_v1_0`
is therefore the strongest candidate for a native runtime integration experiment.

## Strongest reality gap

The external-threat audit identifies hostile execution containment,
authenticated inter-agent communication, and goal/outcome monitoring as outright
gaps in the current modeled coding-agent boundary. These should remain gaps until
implemented and tested.

## Integration evidence

Read [packaging reconciliation](PACKAGING_RECONCILIATION.md) and [local verification](LOCAL_VERIFICATION.md) before relying on supplied counts. The original eight packets are historical research; current integration edits and reruns are separate.
