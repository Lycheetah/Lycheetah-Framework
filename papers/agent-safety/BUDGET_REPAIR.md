# Shared accounting repair — one live control plane

**Evidence footing: [SCAFFOLD] research, proposal or source review. Supplied and local synthetic results retain their stated limits; no independent validation or production claim.**

**Working packet v0.4 · 3 October 2026 · Authoring-seat development evidence.**
Framework creator and research owner: Mackenzie Conor James Clark.
Implementation and review: Caelorynth, an AI coding assistant.

The original v0.3 probe produced two one-unit effects under one one-unit root
grant: each broker constructed its own ledger. This repair gives every broker
using the same live control-plane object one authoritative ledger and one operation
journal. Creating another broker no longer creates another allowance.

## Implementation

- [Accounting state](simulator/safety_sim/accounting.py) holds resource accounts,
  reservations and immutable operation records.
- [Control-plane ownership](simulator/safety_sim/authority.py) creates the ledger
  and journal once, under its existing lock. Both permission-store arms inherit
  this ownership; neither receives a special accounting advantage.
- [Broker wiring](simulator/safety_sim/broker.py) uses those shared records.
  Replays return the original observation. Unknown outcomes retain the reservation
  and can be reconciled by another broker with the same authenticated owner and
  adapter. The operation binds actor, request digest and adapter identity.

The adapter binding prevents a matching effect identifier from being replayed
through a different synthetic service as if it were the original effect. Journaling
is necessary as well as sharing the ledger: a provider's idempotent receipt must
not be charged again simply because another broker lacks the original observation.

## Observed results

| Development observation | Capability arm | Conventional ACL arm |
|---|---|---|
| Two brokers, one-unit root allowance | First effect confirmed; second rejected | First effect confirmed; second rejected |
| Authoritative charge | 1 unit | 1 unit |
| Distinct ledgers for that authority | 1 | 1 |
| Evidence changes after admission | Admitted effect still completes | Admitted effect still completes |

The [repair probes](simulator/reports/budget-repair/adversarial-checks.json) record
the budget case as repaired within that scope and the freshness counterexample
as still reproduced. Those are two different dispositions.

The [focused test receipt](simulator/reports/budget-repair/unit-tests.json) records
**46 passing methods** from the broker, authority and shared-accounting modules,
including ten new multi-broker methods with subtests for both permission stores.
It is a focused subset, not a claim that the complete simulator or repository
suite ran. [Raw output](simulator/reports/budget-repair/unit-tests.txt) is retained.

New cases cover delegated consumers on different brokers, concurrent distinct
effects, concurrent replays, uncertain outcomes, pending dispatch, certified
preacceptance failure, actor/request/adapter substitution and separate root grants.
The [19 scripted cases per arm](simulator/reports/budget-repair/RESULTS.md) retain
their expected aggregate outcomes, with no observed difference between arms.
Expected outcomes still include permitted harm and effects completing after
revocation. These are not universal protective successes.

## Reproduce the current bounded checks

From `simulator/`, run the selected test modules:

```sh
python3 -B - <<'PY'
import sys, unittest
sys.path.insert(0, 'tests')
suite = unittest.defaultTestLoader.loadTestsFromNames([
    'test_broker', 'test_authority', 'test_shared_accounting'
])
result = unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(not result.wasSuccessful())
PY
python3 -B run_experiments.py --output reports/budget-repair
python3 -B adversarial_checks.py --output reports/budget-repair
```

The test receipt names that 46-method selection. Every command is local;
the simulator has no model/provider client.

Original v0.3 reports remain unchanged in `simulator/reports/` and belong to the
[pinned original source](https://github.com/Lycheetah/Lycheetah-Framework/tree/c998df9f8118cdc4ca1e1d7659fd186d49d84bd7/papers/agent-safety/simulator).
Use that revision to reproduce the original two-effect budget counterexample.
Current source fingerprints are in the new report directory.

## Scope that remains unproved

This closes a demonstrated instance-ownership defect in a self-authored in-process
prototype. It does not establish distributed or crash-safe accounting: replacing
the authority, using distinct authorities, restarting the process or persisting
grants without the ledger needs a separate design and verification. Python callers
with access to trusted internals are not isolated by these objects.

Admission-only evidence freshness remains an exposed limit. No dispatch-time
revalidation, cancellation of an already-admitted effect, strategic deception
measurement, human study or production integration is added by this repair.
No general agent-safety, performance, novelty or commercial-value claim follows.
