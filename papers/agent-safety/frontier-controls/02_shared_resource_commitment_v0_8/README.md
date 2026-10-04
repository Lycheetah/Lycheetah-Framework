# Lycheetah Shared Resource Commitment Ledger v0.8

**Evidence footing: [SCAFFOLD] research, proposal or source review. Supplied and local synthetic results retain their stated limits; no independent validation or production claim.**

**Status:** `SYNTHETIC_ENGINEERING_VALIDATED`  
**Deployment:** none  
**Dependencies:** Python standard library only

## Why v0.8 exists

The existing Lycheetah agent-safety simulator documents a multi-broker failure:

```text
root budget = 1
broker A local ledger -> spends 1
broker B local ledger -> spends 1
aggregate real spend = 2
```

Each broker is locally correct. The system is globally wrong.

v0.8 replaces instance-local accounting with one durable commitment ledger shared
by all brokers using that resource account.

## Invariant

For account `r`:

```text
spent(r,t) + reserved(r,t) <= budget(r)
```

Reservation is the admission operation:

```text
RESERVE(effect, max_cost)
```

It succeeds only when the full maximum cost fits inside the currently uncommitted
capacity.

Settlement performs:

```text
reserved -= max_cost
spent += actual_cost
```

with the required assumption:

```text
0 <= actual_cost <= max_cost
```

Certified no-effect releases the reservation.

An unresolved provider outcome does **not**.

```text
UNKNOWN -> reservation stays locked
```

This prevents a timeout from turning into free budget for an unchecked retry.

## Conventional baseline

This is transactional reservation accounting, not new mathematics.

SQLite is used because it serializes writes across independent connections. Each
mutation begins with `BEGIN IMMEDIATE`, so the read of current budget and the
corresponding reservation update occur within one write transaction.

The benchmark includes:

1. the existing-style instance-local budget counterexample;
2. an independent conventional reservation state-machine oracle;
3. the durable shared SQLite ledger.

## Frozen checks

Run:

```bash
python3 benchmark.py
```

The packet checks:

- normal reserve/settle and unused-capacity release;
- unknown outcome retains capacity;
- certified no-effect restores it;
- retrying the same effect through another broker cannot double-reserve;
- conflicting reuse of an effect ID is denied;
- restart preserves reservations;
- provider cost exceeding its promised maximum becomes `INDETERMINATE`, not a
  fake successful settlement;
- concurrent settlement is idempotent;
- 16 thread-level brokers competing for a five-unit root account;
- 24 separate Python processes competing for a seven-unit root account;
- varying reservation sizes competing for one ten-unit account;
- all 259 bounded traces in a two-effect reservation state machine compared
  with an independently coded conventional oracle.

## Practical use today

This can sit behind multiple local agent workers that share a bounded resource:

- API spend;
- maximum paid tool calls;
- token budgets;
- database write allowance;
- email/send quotas;
- cloud job slots;
- bounded deployment capacity.

A broker must reserve the worst-case charge before releasing the effect.

```text
agent workers
  |   |   |
  v   v   v
shared resource ledger
      |
      +-- RESERVE
      +-- SETTLE
      +-- UNKNOWN
      +-- RELEASE_NO_EFFECT
      |
      v
effect gateway/provider
```

## Cybernetic reading

The regulated variable is aggregate committed resource pressure:

```text
R_t = spent_t + reserved_t
```

with safe region:

```text
R_t <= B
```

Every broker is an actuator competing for the same finite plant resource.

A local controller that observes only its own ledger has an incomplete sensor and
cannot regulate the global variable. v0.8 makes the sensor/actuator state shared
at the serialization boundary.

## Limits

- one-node SQLite, not distributed consensus;
- no network partitions or replica lag;
- no real monetary provider;
- provider upper bounds are assumed, not enforced remotely;
- no weighted fairness or broker priorities;
- no dynamic/refilling budget window;
- no denial-of-service protection;
- no authenticated cross-host broker identity;
- no model-agent evaluation;
- no external security review.


## Frozen result

The final validated run produced:

- 10/10 scripted accounting + adapter checks;
- documented instance-local counterexample: aggregate spend `2` under nominal root budget `1`;
- 16 concurrent thread brokers against budget `5`: exactly `5` reservations admitted;
- 24 independent Python broker processes against budget `7`: exactly `7` reservations admitted, `0` worker errors;
- mixed-cost race: accepted reservation maxima totaled exactly `10/10`;
- 259/259 bounded reservation/reconciliation traces matched the independent conventional oracle.

### Elementary invariant argument

Let `S_t` be settled spend, `R_t` active reserved maximum cost, and `B` the root budget.
The safety invariant is:

```text
S_t + R_t <= B
```

It holds initially because `S_0 = R_0 = 0`. A reservation of maximum `m` is
admitted only when `S + R + m <= B`. Settlement with actual cost `a <= m`
changes the aggregate from `S + R` to `S + R - m + a`, which cannot increase
it beyond the pre-settlement value. Certified no-effect subtracts `m` from
`R`; `UNKNOWN` leaves both counters unchanged. Therefore each serialized
transition preserves the bound under the stated assumptions.

This is an elementary induction over the declared state machine, not a novel theorem.

## Practical provider adapter

`budgeted_adapter.py` provides the intended call pattern:

```text
RESERVE(max_cost)
   |
   +-- deny -> do not call provider
   |
   v
provider call
   |
   +-- confirmed(actual <= max) -> SETTLE
   +-- certified no effect       -> RELEASE
   +-- timeout / exception       -> UNKNOWN (reservation retained)
```

A retry of an `UNKNOWN` effect does not invoke the provider again until an
external reconciliation step resolves the previous attempt.

## Benchmark correction

The first standalone bounded-trace run reported `49/259`. The ledger was not
the source of the mismatch: the benchmark exception path assigned the observed
state `MISSING` but failed to assign the oracle result for that operation, so
Python reused a stale expected value from a previous trace. The harness was
corrected to compute the independent oracle first, and the entire suite was
rerun before freezing this packet. The final bounded result is `259/259`.
