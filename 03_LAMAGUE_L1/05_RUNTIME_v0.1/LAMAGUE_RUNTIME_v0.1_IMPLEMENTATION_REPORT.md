# LAMAGUE RUNTIME v0.1

## First Executable Milestone Implementation Report

**Date:** 31 July 2026  
**Lineage:** LAMAGUE-1C v1.0 → Frontier Canon Addendum I → Runtime v0.1  
**Status:** Executable research prototype  
**Execution boundary:** Abstract in-memory state only. No real-world action connectors.

---

## 1. Purpose

The Frontier Canon required the smallest complete end-to-end implementation capable of moving from a bounded human expression into:

```text
parse
→ identify semantic matter
→ build typed operations
→ preserve uncertainty
→ declare invariants
→ audit authority and consequence
→ emit AST
→ execute abstractly
→ explain
→ preserve trace
```

Runtime v0.1 implements that milestone without claiming general natural-language understanding or proven superiority.

---

## 2. Canonical input

```text
Human and AI collaborators examine an unproven claim,
preserve uncertainty,
record contributions,
and publish only what the evidence supports.
```

The bounded compiler deterministically produces:

```text
Q → O → E → U → I → G → T → P → F → Y
```

This path is registered as the specification seal:

```text
FORGE_TRUTH
```

---

## 3. Implemented architecture

### 3.1 Ontological Kernel

The machine registry contains the sixteen root types:

```text
Agent
State
Claim
Observation
Evidence
Unknown
Purpose
Invariant
Boundary
Authority
Consent
Value
Action
Consequence
Memory
Context
```

Both JSON and YAML representations are included.

### 3.2 VITA-8 context capsule

The runtime carries recoverable fields for:

```text
WHO
WHAT
WHY
KNOW
UNKNOWN
MAY
COST
AFTER
```

These are represented through the `ContextCapsule` object rather than hidden inside untyped prose.

### 3.3 Parser

The parser currently supports:

- primitive A–Z operation sequences
- ASCII and Unicode arrows
- deterministic programme-seal expansion
- typed unknowns such as `U<consent>`
- operation payloads such as `X{from=human,to=ai,value=knowledge,consent=explicit}`
- normalized round-trip rendering

The parser rejects unknown operations, unknown seals, malformed token syntax, and registry-version mismatches.

### 3.4 Typed AST

Each node records:

```text
node_id
operation
operation_name
input_types
output_type
arguments
context
provenance
evidence
unknowns
authority
invariants
value_flow
consequence_horizon
recovery
version
```

### 3.5 Seal registry

The executable registry includes the five previously forged seals:

```text
COR
FRO
SOV
CAS
DIS
```

It also records later programme seals as specifications rather than proven primitives:

```text
VERITAS
CARE
LIFE
COVENANT
REPAIR
LEGACY
GRIEF
DREAM_BIND
FORGE_TRUTH
```

Every seal expands deterministically under registry version `0.1`.

### 3.6 Constitutional auditor

The auditor evaluates three independent gates:

```text
Truth Gate
Agency Gate
Life Gate
```

It returns one of:

```text
VALID
EXPAND
REPAIR
ISOLATE
REJECT
```

The current rules detect:

- proof requested without evidence
- certainty exceeding evidence support
- untyped unknown invocation
- missing claim provenance
- consequential action without participants
- execution without visible authority
- exchange without consent
- high-impact action without affected parties
- consequential action without declared consequences
- risk without visible cost
- high impact without consequence horizon
- irreversible action without recovery

### 3.7 Abstract interpreter

Execution occurs only over an in-memory abstract state record.

It can record:

- unresolved queries
- observations
- evidence
- typed unknowns
- invariants
- guard state
- transitions
- proof status
- memory records
- exchanges
- scoped outputs

No external tools, institutions, accounts, devices, or real-world systems are controlled.

### 3.8 Explainer

The explainer reconstructs the expanded operation path in plain language and preserves:

- unknowns
- invariants
- authority
- seal provenance

### 3.9 Trace Store

Every run can preserve:

```text
input
registry version
AST
context
three-gate audit
execution events
result state
proof status
plain-language explanation
```

The package includes a complete canonical trace.

---

## 4. Canonical execution result

The canonical first milestone returned:

```text
Truth Gate   VALID
Agency Gate  VALID
Life Gate    VALID
Overall      VALID
Executed     true
```

Its proof state remained:

```text
context-limited
```

This is intentional because the runtime preserved the unresolved questions:

```text
human learnability
net semantic compression
cross-model consistency
long-term usefulness
```

The system did not convert the existence of a prototype into proof of broad utility.

---

## 5. Test results

Runtime v0.1 passes thirteen tests.

### Registry integrity

- exactly twenty-six A–Z operations exist
- seal expansion is deterministic
- `FRO → COR` expands into thirteen ordered operations
- registry-version mismatch fails visibly

### Parser integrity

- typed unknowns survive parse and normalization
- exchange annotations preserve visible consent and value fields

### Truth Gate

- proof without evidence returns `EXPAND`
- certainty beyond evidence returns `REPAIR`

### Agency Gate

- exchange without consent returns `ISOLATE`
- high-risk execution without affected parties returns `REJECT`

### Life Gate

- irreversible action without recovery returns `REJECT`

### Canonical milestone

- the canonical sentence compiles to the required ten-operation path
- all three gates pass
- abstract execution completes
- unresolved content survives into the final output

### Anti-fabrication boundary

- vague unsupported natural language is rejected rather than silently assigned invented semantic structure

Test result:

```text
Ran 13 tests
OK
```

---

## 6. What has become real

The following are no longer only prose specifications:

1. The sixteen-root ontology has machine-readable form.
2. VITA-8 has an executable context representation.
3. Programme seals can expand deterministically.
4. LAMAGUE expressions can become typed ASTs.
5. The Three Gates can block, expand, repair, isolate, or reject expressions.
6. Typed unknowns can remain present through execution and output.
7. The canonical human–AI research sentence can execute over an abstract state.
8. The entire transformation can be recovered through a trace.

---

## 7. What remains unproven

Runtime v0.1 does not prove:

- general natural-language compilation
- human learnability
- net information or semantic compression
- cross-model consistency
- superior decision quality
- semantic identity hashes
- native-glyph recognition
- agency symmetry as a complete formal measurement
- reliable automated identification of affected parties
- real-world safety or governance effectiveness

These remain experiments, conjectures, or Void territories.

---

## 8. Known limitations

1. Natural-language compilation is deliberately limited to the canonical first-milestone pattern.
2. Type signatures are registered, but v0.1 does not yet perform full operand unification across node outputs and inputs.
3. The interpreter models semantic events rather than executing formal domain procedures.
4. Context is supplied or conservatively inferred by the bounded compiler.
5. No glyph parser exists.
6. No migration engine exists beyond strict version rejection.
7. Gate rules are explicit initial policies, not validated universal ethics.
8. Proof status is structural and evidential, not a theorem prover.

---

## 9. Next executable frontier

The next runtime revision should forge:

### Full type-flow checking

Connect every node output to the next node input and reject incompatible sequences before auditing.

### Semantic variables

Allow expressions such as:

```text
claim:H
observation:o1
unknown:U<consent>
invariant:i1
```

### Context-capsule grammar

Represent VITA-8 directly inside `.lam` source files.

### Guard predicates and branches

Add explicit grammar for:

```text
G[condition]{action}{fallback}
J[condition]{true_branch}{false_branch}
```

### Proof objects

Replace structural proof labels with inspectable proof packets containing methods, sources, counterevidence, and scope.

### Migration registry

Permit explicit semantic migration between registry versions while rejecting silent drift.

### Baseline comparison harness

Encode equivalent cases in LAMAGUE, structured English, JSON, and YAML, then compare:

```text
length
codebook-adjusted cost
parse success
unknown preservation
authority visibility
value visibility
error detection
round-trip fidelity
```

### Adversarial corpus

Create cases that attempt to hide:

```text
authority
consent
affected parties
uncertainty
purpose drift
value extraction
outdated seal meaning
fabricated provenance
```

---

## 10. Forge conclusion

The runtime remains small.

That is correct.

It is not yet a universal language engine.

It is the first executable evidence that the architecture can cross from philosophy into machine structure without immediately abandoning its own laws.

The most important result is not that a programme ran.

It is that the programme refused invalid certainty, preserved unresolved meaning, demanded visible authority, isolated unconsented exchange, and blocked irreversible action without recovery.

LAMAGUE has taken its first executable breath.

```text
Meaning entered.
Structure formed.
The gates answered.
Unknown survived.
The trace remained.
```

**For life. For shared intelligence. We continue the forge.**
