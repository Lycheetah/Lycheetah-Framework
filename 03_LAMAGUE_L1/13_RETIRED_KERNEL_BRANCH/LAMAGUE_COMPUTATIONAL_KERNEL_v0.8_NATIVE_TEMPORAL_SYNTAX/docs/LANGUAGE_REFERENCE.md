# Source Language Reference

## Required

```text
program NAME
path OP -> OP -> ...
```

## Metadata

```text
version 0.5
identity NAME
purpose "TEXT"
claim "TEXT"
risk low|medium|high|critical
irreversible true|false
confidence 0.0
limit max_steps=128
horizon VALUE
compress requested
yield "TEXT"
```

## Typed declarations

```text
evidence NAME "TEXT"
unknown NAME protected required_for=DECISION
invariant NAME "TEXT"
authority NAME scope=SCOPE "TEXT"
participant NAME
affected NAME
boundary NAME "TEXT"
dissent PARTY "POSITION"
valueflow SOURCE RECIPIENT consent=VALUE "KIND"
recovery NAME "TEXT"
effect EffectName<arg,arg>
resolve UNKNOWN with=EVIDENCE
gate affected_party|expert|operator|silent_witness
```

## Standard seals

```text
@Correction
@Frontier
@Sovereignty
@Cascade
@ProtectedDissent
```
