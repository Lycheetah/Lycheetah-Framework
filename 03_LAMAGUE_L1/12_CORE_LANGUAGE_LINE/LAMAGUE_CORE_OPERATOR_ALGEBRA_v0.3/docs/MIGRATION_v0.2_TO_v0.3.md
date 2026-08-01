# Migration from v0.2 to v0.3

## Source compatibility

All valid v0.2 source remains valid.

## New syntax

```lamague
describe operator ⊗;
check law(⊗, associative);
check composition(⊗, →);
```

## Output changes

- version becomes `0.3.0`;
- equivalence checks include rewrite traces;
- expression descriptions include rewrite traces;
- results include `operator_contract_lock`.

## No changed algebra laws

The v0.1/v0.2 normalization laws remain intact.

v0.3 documents their exact scope and adds explicit non-laws.
