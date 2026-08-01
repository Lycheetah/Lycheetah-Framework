# Migration from v0.1 to v0.2

## Source compatibility

Ordinary v0.1 source remains valid.

```lamague
Ao → Φ↑ → Ψ_inv;
```

## New optional annotations

```lamague
let anchor: Field = Ao;
invariant stable: Path = Ao → Ψ_inv;
macro Z₁ RETURN: Path = Ao → Φ↑ → Ψ_inv;
```

## Output change

v0.1:

```json
"bindings": {"anchor": "Ao"}
```

v0.2:

```json
"bindings": {
  "anchor": {
    "type": "Field",
    "normal_form": "Ao"
  }
}
```

## Internal AST change

`Φ↑` and `Ψ_inv` are now `ModifiedAtom` nodes.

Their surface spelling and normalized rendering remain unchanged.

## Removed compatibility

Code importing the old `Sort` enumeration must migrate to `CoreType`.

## Stable laws

No v0.1 algebra law was changed.
