# Semantic Type System

LAMAGUE treats protected meaning as typed data rather than prose metadata.

```text
Evidence<T>
Unknown<T>
Invariant<T>
Authority<Scope>
AffectedParty<Role>
Dissent<Position>
ValueFlow<Source,Recipient>
Recovery<Path>
```

The reference implementation does not infer these types from unrestricted text. They must be declared explicitly.
