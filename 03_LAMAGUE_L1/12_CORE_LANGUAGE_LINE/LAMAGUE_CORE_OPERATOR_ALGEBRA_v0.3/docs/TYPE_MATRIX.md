# LAMAGUE v0.2 Type Matrix

## Atom types

| Expression | Exact type | Accepted as Field | Accepted as Invariant | StateLike |
|---|---:|---:|---:|---:|
| `Ao` | Field | yes | no | yes |
| `Φ` | Field | yes | no | yes |
| `Φ↑` | ModifiedField | yes | no | yes |
| `Ψ` | Field | yes | no | yes |
| `S` | Field | yes | no | yes |
| `Δ` | Field | yes | no | yes |
| `⟟` | InvariantMarker | no | yes | yes |
| `∅` | NullState | no | yes | yes |
| `⟐` | InvariantMarker | no | yes | yes |
| `⟁` | InvariantMarker | no | yes | yes |
| `∞` | InvariantMarker | no | yes | yes |
| `Ψ_inv` | InvariantField | yes | yes | yes |

## Operator results

| Expression | Result |
|---|---|
| `A ⊗ B` | Fusion |
| `A → B` | Path |
| `A ⇌ B` | Exchange |
| `A ⟲ B` | Recurrence |
| `A ↯ B` | Collapse |
| `A ↗ B` | Ascent |

All result types are subtypes of `Composite` and `StateLike`.
