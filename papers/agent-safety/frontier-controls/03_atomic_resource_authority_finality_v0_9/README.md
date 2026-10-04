# Lycheetah Atomic Resource + Authority Finality Gate v0.9

**Evidence footing: [SCAFFOLD] research, proposal or source review. Supplied and local synthetic results retain their stated limits; no independent validation or production claim.**

**Status:** `SYNTHETIC_ENGINEERING_VALIDATED`  
**Deployment:** none  
**Dependencies:** Python standard library only

## Problem closed in this round

v0.7 serialized **authority generation + local effect commit**.

v0.8 serialized **shared budget reservation + reconciliation**.

Those were still independent control planes.

A consequential action should not be accepted under one authority transaction
while its resource commitment lives in an unrelated transaction.

v0.9 fuses:

```text
authority generation
resource commitment
exact action/effect identity
local finality state
durable outbox intent
```

inside one SQLite write transaction.

## Resource state

Define:

```text
P = spent + reserved + committed_pending
```

and require:

```text
P <= budget
```

The three terms have different temporal meanings:

- `reserved`: admitted but not final;
- `committed_pending`: final locally, remote outcome not reconciled;
- `spent`: provider receipt reconciled.

At local finality:

```text
reserved -= max_cost
committed_pending += max_cost
```

so total pressure does not fall merely because a request crossed the finality
boundary.

At receipt with `actual <= max_cost`:

```text
committed_pending -= max_cost
spent += actual
```

Only the unused difference becomes available again.

## Atomic finality

A successful commit transaction does all of this or none of it:

1. re-check authority generation;
2. verify exact action binding;
3. move the resource reservation to committed exposure;
4. mark the attempt `COMMITTED`;
5. insert the durable outbox record.

If revocation wins the serialization race first, it:

1. advances authority generation;
2. marks authority inactive;
3. cancels all still-`RESERVED` attempts in that scope;
4. releases their reservations.

Thus:

```text
COMMIT < REVOKE -> accepted finality may relay later
REVOKE < COMMIT -> no outbox and no leaked reservation
```

## Why an outbox

A database transaction cannot usually atomically mutate local state and make an
arbitrary remote SaaS effect.

The conventional transactional-outbox pattern solves the local half:

```text
local final state + dispatch intent
```

commit together.

A relay then delivers the durable outbox at least once. The downstream provider
must use a stable effect ID / idempotency key so retries cannot duplicate the
external consequence.

This packet includes an idempotent synthetic provider and crash injection both
before and after remote acceptance.

## Frozen validation

Run:

```bash
python3 benchmark.py
```

The frozen packet checks:

- 11/11 scripted integration cases;
- classic naive dual-write lost-dispatch counterexample;
- classic send-before-record duplicate-on-retry counterexample;
- crash after local finality but before relay;
- crash after provider accept but before local receipt;
- committed exposure blocking later budget admissions;
- no-effect reconciliation;
- provider upper-bound violation fail-closed behavior;
- exact action binding;
- 64 real concurrent revoke-vs-finality races;
- 16 concurrent broker threads against budget 5;
- 20 independent Python broker processes against budget 6;
- all 259 bounded traces over a two-effect authority/budget/finality model,
  compared with an independently coded conventional atomic state machine.

## Conventional baseline

Nothing primitive here is claimed as new:

- transactional outbox;
- stable idempotency keys;
- transactional resource reservations;
- generation fencing;
- serializable state transitions.

The contribution of this packet is the executable composition and explicit
semantic boundary between admission, local finality, remote delivery, and
reconciliation.

## Practical use today

This pattern fits an agent gateway controlling a local durable boundary:

```text
agent workers
      |
      v
atomic finality DB
  - authority
  - resource exposure
  - exact effect
  - outbox
      |
      v
idempotent relay
      |
      v
provider
```

Examples:

- deployment gateway;
- bounded cloud-job launcher;
- outbound messaging gateway;
- paid API proxy;
- local transaction executor;
- repository/action queue.

## Limits

- one-node SQLite, not distributed consensus;
- no real SaaS provider;
- no remote cancellation after local finality;
- provider idempotency is required for safe at-least-once relay;
- actual cost must obey reserved maximum;
- no malicious broker bypass of the database;
- no authenticated cross-host principals;
- no network partitions / replica lag;
- no model-agent test;
- no external audit.


## Benchmark correction

The first bounded trace run returned `257/259`. The two mismatches were:

```text
ADMIT A -> REVOKE -> retry ADMIT A
ADMIT B -> REVOKE -> retry ADMIT B
```

The independent oracle preserved the durable terminal state `CANCELLED`, while
the implementation checked current authority first and returned generic `DENY`.
The implementation was tightened so stable effect identity is inspected before
a new admission decision. A dedicated regression case was added and the full
suite was rerun before this packet was frozen. The final bounded result is
`259/259`.
