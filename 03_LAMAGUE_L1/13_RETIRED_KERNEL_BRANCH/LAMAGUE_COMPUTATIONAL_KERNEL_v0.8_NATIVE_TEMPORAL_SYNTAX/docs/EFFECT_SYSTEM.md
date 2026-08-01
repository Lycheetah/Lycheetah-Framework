# Effect System

```text
MayAffect<T>
TransfersValue<S,R>
CompressesMeaning
ChangesAuthority
CreatesReversibleRisk
CreatesIrreversibility
ResolvesUnknown<T>
SuppressesDissent
ForksIdentity
CallsExternalSystem<T>
```

Compiler obligations make the effects executable rather than decorative. `MayAffect` requires affected parties. `TransfersValue` requires visible value flow. `CreatesReversibleRisk` requires recovery. `CreatesIrreversibility` requires recovery, Guard, and all four gates. `ResolvesUnknown<T>` requires named evidence. `SuppressesDissent` is fatal when dissent exists.
