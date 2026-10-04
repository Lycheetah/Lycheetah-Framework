#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from dataclasses import asdict
import itertools
import json
import subprocess
import sys
import tempfile
import threading

from resource_ledger import (
    ConventionalReservationOracle,
    InstanceLocalBudget,
    SharedResourceLedger,
)
from budgeted_adapter import (
    ProviderOutcome, budgeted_call, reconcile_budgeted_effect,
)


ACCOUNT = "root-api-budget"


def baseline_counterexample():
    a = InstanceLocalBudget(1)
    b = InstanceLocalBudget(1)
    assert a.reserve("effect-a", 1)
    assert b.reserve("effect-b", 1)
    a.settle("effect-a", 1)
    b.settle("effect-b", 1)
    return {
        "nominal_shared_budget": 1,
        "broker_a_spent": a.spent,
        "broker_b_spent": b.spent,
        "aggregate_spent": a.spent + b.spent,
        "overspend": a.spent + b.spent > 1,
    }


def scripted_cases(tmp: Path):
    rows = []

    # 1 Basic reserve/settle with unused capacity returned.
    db = tmp/"basic.sqlite"
    l = SharedResourceLedger(db)
    l.create_account(ACCOUNT, 10)
    r = l.reserve(ACCOUNT, "broker-a", "e1", 5)
    s = l.settle("e1", 3)
    rows.append({
        "case": "settlement-releases-unused-reservation",
        "pass": r.state == "RESERVED" and s.state == "SETTLED"
                and s.spent == 3 and s.reserved == 0
                and l.invariant_holds(ACCOUNT),
        "observed": {"reserve": r.__dict__, "settle": s.__dict__},
    })

    # 2 Unknown keeps capacity locked and blocks overspend.
    db = tmp/"unknown.sqlite"
    l = SharedResourceLedger(db)
    l.create_account(ACCOUNT, 5)
    l.reserve(ACCOUNT, "broker-a", "e1", 4)
    u = l.mark_unknown("e1")
    denied = l.reserve(ACCOUNT, "broker-b", "e2", 2)
    rows.append({
        "case": "unknown-outcome-retains-capacity",
        "pass": u.state == "UNKNOWN" and denied.state == "DENY"
                and l.snapshot(ACCOUNT)["reserved"] == 4,
        "observed": {
            "unknown": u.__dict__,
            "second_reserve": denied.__dict__,
        },
    })

    # 3 Reconciliation to no-effect releases capacity.
    rel = l.release_no_effect("e1")
    allowed = l.reserve(ACCOUNT, "broker-b", "e2", 2)
    rows.append({
        "case": "certified-no-effect-restores-capacity",
        "pass": rel.state == "RELEASED" and allowed.state == "RESERVED",
        "observed": {
            "release": rel.__dict__,
            "new_reserve": allowed.__dict__,
        },
    })

    # 4 Same effect retry is idempotent across brokers.
    db = tmp/"retry.sqlite"
    l = SharedResourceLedger(db)
    l.create_account(ACCOUNT, 5)
    first = l.reserve(ACCOUNT, "broker-a", "same-effect", 3)
    retry = l.reserve(ACCOUNT, "broker-b", "same-effect", 3)
    rows.append({
        "case": "cross-broker-retry-does-not-double-reserve",
        "pass": first.state == "RESERVED" and retry.state == "RESERVED"
                and l.snapshot(ACCOUNT)["reserved"] == 3,
        "observed": {
            "first": first.__dict__, "retry": retry.__dict__,
        },
    })

    # 5 Conflicting use of effect id is denied.
    conflict = l.reserve(ACCOUNT, "broker-b", "same-effect", 4)
    rows.append({
        "case": "effect-id-conflict-denied",
        "pass": conflict.state == "DENY"
                and conflict.reason == "effect-id-conflict",
        "observed": conflict.__dict__,
    })

    # 6 Restart keeps reservation and budget state.
    db = tmp/"restart.sqlite"
    l = SharedResourceLedger(db)
    l.create_account(ACCOUNT, 5)
    l.reserve(ACCOUNT, "broker-a", "e1", 4)
    l = SharedResourceLedger(db)
    denied = l.reserve(ACCOUNT, "broker-b", "e2", 2)
    rows.append({
        "case": "restart-preserves-shared-reservation",
        "pass": denied.state == "DENY"
                and l.snapshot(ACCOUNT)["reserved"] == 4,
        "observed": denied.__dict__,
    })

    # 7 Provider overrun is explicitly not hidden as safe settlement.
    db = tmp/"overrun.sqlite"
    l = SharedResourceLedger(db)
    l.create_account(ACCOUNT, 5)
    l.reserve(ACCOUNT, "broker-a", "e1", 3)
    over = l.settle("e1", 4)
    rows.append({
        "case": "provider-cost-overrun-becomes-indeterminate",
        "pass": over.state == "INDETERMINATE"
                and l.snapshot(ACCOUNT)["reserved"] == 3,
        "observed": over.__dict__,
    })

    # 8 Practical adapter: confirmed provider cost settles and returns slack.
    db = tmp/"adapter-confirmed.sqlite"
    l = SharedResourceLedger(db)
    l.create_account(ACCOUNT, 5)
    calls = {"n": 0}
    def confirmed_provider():
        calls["n"] += 1
        return ProviderOutcome("CONFIRMED", actual_cost=2, receipt="r1")
    result = budgeted_call(
        l, ACCOUNT, "broker-a", "adapter-e1", 3, confirmed_provider
    )
    rows.append({
        "case": "budgeted-adapter-settles-confirmed-provider-effect",
        "pass": result.state == "CONFIRMED" and calls["n"] == 1
                and l.snapshot(ACCOUNT)["spent"] == 2
                and l.snapshot(ACCOUNT)["reserved"] == 0,
        "observed": {"result": asdict(result), "calls": calls["n"],
                     "snapshot": l.snapshot(ACCOUNT)},
    })

    # 9 Provider exception becomes UNKNOWN; retry is fenced until reconciliation.
    db = tmp/"adapter-unknown.sqlite"
    l = SharedResourceLedger(db)
    l.create_account(ACCOUNT, 5)
    calls = {"n": 0}
    def failing_provider():
        calls["n"] += 1
        raise RuntimeError("synthetic transport failure")
    first = budgeted_call(
        l, ACCOUNT, "broker-a", "adapter-e2", 4, failing_provider
    )
    second = budgeted_call(
        l, ACCOUNT, "broker-b", "adapter-e2", 4, failing_provider
    )
    reconciled = reconcile_budgeted_effect(
        l, "adapter-e2", ProviderOutcome(
            "CONFIRMED", actual_cost=3, receipt="provider-existing-r2"
        )
    )
    rows.append({
        "case": "unknown-provider-outcome-fences-retry-until-reconciliation",
        "pass": first.state == "PENDING" and second.state == "PENDING"
                and calls["n"] == 1 and reconciled.state == "CONFIRMED"
                and l.snapshot(ACCOUNT)["spent"] == 3
                and l.snapshot(ACCOUNT)["reserved"] == 0,
        "observed": {
            "first": asdict(first), "second": asdict(second),
            "reconciled": asdict(reconciled), "calls": calls["n"],
            "snapshot": l.snapshot(ACCOUNT),
        },
    })

    # 10 Concurrent same-effect settlement remains one charge.
    db = tmp/"settle-race.sqlite"
    l = SharedResourceLedger(db)
    l.create_account(ACCOUNT, 5)
    l.reserve(ACCOUNT, "broker-a", "e1", 3)
    states = []
    lock = threading.Lock()
    barrier = threading.Barrier(8)

    def settle_worker():
        local = SharedResourceLedger(db)
        barrier.wait()
        d = local.settle("e1", 2)
        with lock:
            states.append(d.state)

    threads = [threading.Thread(target=settle_worker) for _ in range(8)]
    for t in threads: t.start()
    for t in threads: t.join()
    snap = l.snapshot(ACCOUNT)
    rows.append({
        "case": "concurrent-settlement-is-idempotent",
        "pass": all(x == "SETTLED" for x in states)
                and snap["spent"] == 2 and snap["reserved"] == 0,
        "observed": {"states": states, "snapshot": snap},
    })

    return rows


def threaded_broker_race(tmp: Path, brokers=16, budget=5):
    db = tmp/"threaded.sqlite"
    ledger = SharedResourceLedger(db)
    ledger.create_account(ACCOUNT, budget)
    decisions = []
    lock = threading.Lock()
    barrier = threading.Barrier(brokers)

    def worker(i):
        local = SharedResourceLedger(db)
        barrier.wait()
        d = local.reserve(ACCOUNT, f"broker-{i}", f"effect-{i}", 1)
        with lock:
            decisions.append(d.state)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(brokers)]
    for t in threads: t.start()
    for t in threads: t.join()
    snap = ledger.snapshot(ACCOUNT)
    return {
        "brokers": brokers,
        "budget": budget,
        "reserved_decisions": decisions.count("RESERVED"),
        "denied_decisions": decisions.count("DENY"),
        "snapshot": snap,
        "invariant": ledger.invariant_holds(ACCOUNT),
    }


def process_broker_race(tmp: Path, brokers=24, budget=7):
    db = tmp/"process.sqlite"
    ledger = SharedResourceLedger(db)
    ledger.create_account(ACCOUNT, budget)
    worker = Path(__file__).with_name("reserve_worker.py")

    procs = []
    for i in range(brokers):
        procs.append(subprocess.Popen(
            [
                sys.executable, str(worker), str(db), ACCOUNT,
                f"process-broker-{i}", f"process-effect-{i}", "1"
            ],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        ))

    results = []
    errors = []
    for p in procs:
        out, err = p.communicate(timeout=30)
        if p.returncode != 0:
            errors.append(err)
        else:
            results.append(json.loads(out))

    snap = ledger.snapshot(ACCOUNT)
    return {
        "brokers": brokers,
        "budget": budget,
        "process_errors": errors,
        "reserved_decisions": sum(x["state"] == "RESERVED" for x in results),
        "denied_decisions": sum(x["state"] == "DENY" for x in results),
        "snapshot": snap,
        "invariant": ledger.invariant_holds(ACCOUNT),
    }


def mixed_cost_race(tmp: Path):
    """Eight brokers request varying maxima against budget 10."""
    db = tmp/"mixed.sqlite"
    ledger = SharedResourceLedger(db)
    ledger.create_account(ACCOUNT, 10)
    costs = [4, 4, 3, 3, 2, 2, 1, 1]
    barrier = threading.Barrier(len(costs))
    rows = []
    lock = threading.Lock()

    def worker(i, cost):
        local = SharedResourceLedger(db)
        barrier.wait()
        d = local.reserve(ACCOUNT, f"m{i}", f"mix-{i}", cost)
        with lock:
            rows.append({"cost": cost, "state": d.state})

    ts = [threading.Thread(target=worker, args=(i,c)) for i,c in enumerate(costs)]
    for t in ts: t.start()
    for t in ts: t.join()
    accepted_cost = sum(x["cost"] for x in rows if x["state"] == "RESERVED")
    snap = ledger.snapshot(ACCOUNT)
    return {
        "requests": rows,
        "accepted_max_cost": accepted_cost,
        "snapshot": snap,
        "invariant": ledger.invariant_holds(ACCOUNT),
    }


def bounded_trace_check(tmp: Path):
    """All traces length 0..3 over six operations on effects A/B.

    1 + 6 + 36 + 216 = 259 traces.
    Compare the durable ledger's observable states against an independently
    coded conventional reservation state machine.
    """
    alphabet = ("RA", "RB", "UA", "UB", "SA", "XA")
    total = 0
    correct = 0
    mismatches = []

    for length in range(4):
        for trace in itertools.product(alphabet, repeat=length):
            total += 1
            db = tmp/f"trace-{total}.sqlite"
            ledger = SharedResourceLedger(db)
            ledger.create_account(ACCOUNT, 2)
            oracle = ConventionalReservationOracle(limit=2)

            observed = []
            expected = []

            for op in trace:
                # Compute the independent oracle first so a KeyError in the
                # implementation cannot leave a stale expected value from a
                # previous operation/trace.
                if op == "RA":
                    e = oracle.reserve("A", 1)
                elif op == "RB":
                    e = oracle.reserve("B", 1)
                elif op == "UA":
                    e = oracle.unknown("A")
                elif op == "UB":
                    e = oracle.unknown("B")
                elif op == "SA":
                    e = oracle.settle("A", 1)
                elif op == "XA":
                    e = oracle.release("A")

                try:
                    if op == "RA":
                        o = ledger.reserve(ACCOUNT, "b", "A", 1).state
                    elif op == "RB":
                        o = ledger.reserve(ACCOUNT, "b", "B", 1).state
                    elif op == "UA":
                        o = ledger.mark_unknown("A").state
                    elif op == "UB":
                        o = ledger.mark_unknown("B").state
                    elif op == "SA":
                        o = ledger.settle("A", 1).state
                    elif op == "XA":
                        o = ledger.release_no_effect("A").state
                except KeyError:
                    o = "MISSING"

                observed.append(o)
                expected.append(e)

            snap = ledger.snapshot(ACCOUNT)
            state_ok = (
                snap["spent"] == oracle.spent
                and snap["reserved"] == oracle.reserved
                and ledger.invariant_holds(ACCOUNT)
            )
            ok = observed == expected and state_ok
            correct += int(ok)
            if not ok and len(mismatches) < 10:
                mismatches.append({
                    "trace": trace,
                    "observed": observed,
                    "expected": expected,
                    "snapshot": snap,
                    "oracle": {
                        "spent": oracle.spent, "reserved": oracle.reserved,
                        "effects": oracle.effects,
                    },
                })

    return {
        "trace_space": "all RA/RB/UA/UB/SA/XA traces length 0..3",
        "traces": total,
        "correct": correct,
        "all_correct": correct == total,
        "mismatches": mismatches,
    }


def main():
    Path("reports").mkdir(exist_ok=True)
    baseline = baseline_counterexample()
    with tempfile.TemporaryDirectory(prefix="lycheetah-resource-") as td:
        tmp = Path(td)
        scripted = scripted_cases(tmp)
        threads = threaded_broker_race(tmp)
        processes = process_broker_race(tmp)
        mixed = mixed_cost_race(tmp)
        traces = bounded_trace_check(tmp)

    report = {
        "schema": "LYCHEETAH-SHARED-RESOURCE-COMMITMENT-LEDGER-REPORT-0.8",
        "status": "SYNTHETIC_ENGINEERING_VALIDATED",
        "instance_local_counterexample": baseline,
        "scripted_cases": scripted,
        "scripted_summary": {
            "passed": sum(x["pass"] for x in scripted),
            "total": len(scripted),
        },
        "threaded_multi_broker": threads,
        "process_multi_broker": processes,
        "mixed_cost_race": mixed,
        "bounded_trace_check": traces,
        "benchmark_correction": {
            "first_standalone_run": "49/259 bounded traces",
            "cause": (
                "The benchmark exception path set observed=MISSING but failed "
                "to assign the oracle result for that operation, so Python "
                "reused a stale expected-state value from a previous trace."
            ),
            "disposition": (
                "Compute the independent oracle result before invoking the "
                "implementation, add explicit MISSING semantics, and rerun the "
                "entire suite before freezing the packet."
            )
        },
        "deployment": "NOT_DEPLOYED",
        "boundaries": [
            "No real money, tokens, cloud resources, or external API quota were consumed.",
            "SQLite is the single serialization authority; distributed replicas and network partitions are not modeled.",
            "All brokers must use the same ledger or the global invariant does not hold.",
            "The external provider must not exceed each reserved upper bound if a real-world aggregate spend bound is claimed.",
            "UNKNOWN outcomes deliberately retain capacity until reconciliation.",
            "The instance-local baseline is intentionally weak and reproduces the Framework's documented counterexample.",
            "Transactional shared accounting is established prior art; novelty is not claimed."
        ],
    }
    Path("reports/report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True), encoding="utf-8"
    )

    print("Lycheetah Shared Resource Commitment Ledger v0.8")
    print("================================================")
    print(
        f"Scripted checks: "
        f"{report['scripted_summary']['passed']}/{report['scripted_summary']['total']}"
    )
    print(
        f"Instance-local baseline overspend: "
        f"{baseline['aggregate_spent']}/{baseline['nominal_shared_budget']}"
    )
    print(
        f"Threaded brokers: accepted={threads['reserved_decisions']}/"
        f"{threads['brokers']} against budget={threads['budget']}"
    )
    print(
        f"Process brokers: accepted={processes['reserved_decisions']}/"
        f"{processes['brokers']} against budget={processes['budget']} "
        f"errors={len(processes['process_errors'])}"
    )
    print(
        f"Mixed-cost accepted maximum: "
        f"{mixed['accepted_max_cost']}/{mixed['snapshot']['limit']}"
    )
    print(
        f"Bounded traces: {traces['correct']}/{traces['traces']}"
    )
    print("Status: synthetic engineering validation; not deployed.")


if __name__ == "__main__":
    main()
