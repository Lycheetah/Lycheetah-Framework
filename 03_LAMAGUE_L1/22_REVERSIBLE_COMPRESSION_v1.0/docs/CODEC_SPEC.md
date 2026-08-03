# LAMAGUE Reversible Semantic Codec Specification v1.0

## Purpose

The codec compresses a **declared structured semantic packet** into a smaller
canonical textual envelope while preserving every field required for recovery.

It does not infer structured meaning from unrestricted prose.

## Baseline packet fields

```text
purpose
claim
risk
operation path
evidence + provenance
protected unknowns
invariants
authority
participants
affected parties
dissent
value flow
recovery
horizon
yield
```

## Wire forms

### `L1`

```text
L1 + compact positional JSON
```

`L1` removes repeated field names, encodes risk and consent as one-character
values, joins the operation path, and stores repeated record shapes positionally.

### `L1D`

```text
L1D + compact positional JSON + separately shared codebook
```

The codebook contains exact strings learned from the training split only.
Integer values in declared string positions reference that codebook.

## Reversibility

The required invariant is:

```text
canonical(packet) == canonical(decode(encode(packet)))
```

The benchmark also compares full and critical SHA-256 hashes.

## Critical semantic projection

```text
purpose
claim
unknowns
invariants
authority
participants
affected parties
dissent
value flow
recovery
```

## Compression safety

The codec rejects packets when:

```text
protected unknowns exist without U
authority or affected parties exist without G
dissent exists without V
recovery exists without F
yield exists without Y
value flow exists without affected parties
protected unknowns exist without recovery
```

## Boundary

This is schema compression, not universal natural-language compression.
