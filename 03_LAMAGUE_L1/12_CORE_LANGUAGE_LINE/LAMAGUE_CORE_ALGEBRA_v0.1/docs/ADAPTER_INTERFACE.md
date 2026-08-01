# LAMAGUE Adapter Interface v0.1

An adapter translates a validated core expression into a domain representation.

```python
class LamagueAdapter(Protocol):
    name: str
    version: str

    def supports_atom(self, atom: str) -> bool: ...
    def map_atom(self, atom: str) -> object: ...
    def map_operator(self, operator: str, operands: list[object]) -> object: ...
    def validate_invariant(self, name: str, expression: object) -> dict: ...
    def validate_requirement(self, expression: object) -> dict: ...
    def validate_prohibition(self, expression: object) -> dict: ...
```

## Mandatory adapter declaration

Every adapter must publish:

- domain name and version;
- atom mappings;
- operator mappings;
- extra assumptions;
- unsupported expressions;
- evaluation limitations;
- whether execution mutates state;
- whether any algebra law differs from core.

A differing law creates a dialect and must not be presented as canonical LAMAGUE.
