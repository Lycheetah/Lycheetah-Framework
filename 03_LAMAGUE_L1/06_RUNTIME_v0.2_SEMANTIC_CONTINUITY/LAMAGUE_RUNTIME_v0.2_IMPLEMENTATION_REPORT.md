# LAMAGUE Runtime v0.2 — Implementation Report

## Milestone

Runtime v0.2 is the first LAMAGUE prototype designed to test **semantic continuity under change**.

It does not merely ask whether an expression can be parsed and executed. It asks:

- Does the same meaning receive the same identity?
- Does compression expand when the decoder or context is unsafe?
- Can disagreement survive coordination?
- Can value movement remain visible?
- Can a state evolve without falsely claiming to be unchanged?

## Implemented mechanisms

### Semantic identity hash

A canonical representation excludes random programme and node IDs while retaining operation order, context, invariants, unknowns, authority, value flow, and lineage.

```text
semantic object
→ canonical form
→ SHA-256
→ lamague:<digest>
```

### Breathing compression

```text
Z↓  shared context + low risk + verified decoder
Z↑  uncertainty, dissent, hidden extraction, high stakes, or weak decoder
```

The interpreter refuses `Z` execution when the compression policy requires expansion.

### Protected dissent

The canonical protected-dissent path remains:

```text
W → U → G → V → Y
```

A merge over unresolved dissent without this preservation route triggers `ISOLATE`.

### Visible value ledger

Each consequential value entry records source, recipient, kind, amount, declaration status, consent, affected parties, and reversibility.

Hidden or unconsented extraction triggers `ISOLATE`.

### Semantic memory and migration

Each memory record carries a semantic hash, parent hash, purpose, invariants, unknowns, operation path, and version.

Migration classification:

```text
CONTINUATION
DESCENDANT
FORK
IMPOSTOR
```

Removing a protected invariant while claiming continuity is classified as `IMPOSTOR`.

Losing an unresolved unknown produces a visible `FORK`.

## Constitutional gates

Runtime v0.2 evaluates:

```text
Truth Gate
Agency Gate
Life Gate
Continuity Gate
```

All must pass before abstract execution.

## Validation

The v0.2 suite tests registry integrity, seal expansion, stable semantic identity, hash sensitivity, breathing compression, dissent preservation, merge isolation, hidden extraction, declared exchange, memory records, descendant migration, impostor detection, unknown-loss forking, and full continuity execution.

The implementation remains a bounded research prototype. Human decoding, cross-model equivalence, net compression after codebook cost, and real-world benefit remain unproven.
