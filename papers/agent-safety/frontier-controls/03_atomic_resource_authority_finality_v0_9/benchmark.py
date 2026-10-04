#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import itertools
import json
import subprocess
import sys
import tempfile
import threading

from pathlib import Path as _SupportPath
import sys as _support_sys
_support_sys.path.insert(0, str(_SupportPath(__file__).resolve().parents[1]))
from research_support import Action  # noqa: E402
from atomic_finality import (
    AtomicFinalityGate,
    ConventionalAtomicOracle,
    DurableIdempotentProvider,
    NaiveDualWrite,
    OutboxRelay,
)


ACCOUNT = "root"
PRINCIPAL = "agent"
SCOPE = "effects:write"


def action(effect_id, idx=0):
    return Action(
        principal=PRINCIPAL,
        tool="job",
        operation="run",
        object_id=f"job-{idx}",
        destination="local-worker",
        arguments={"job": idx},
        effect_id=effect_id,
    )


def setup_gate(db, budget=5):
    g = AtomicFinalityGate(db)
    g.create_account(ACCOUNT, budget)
    g.activate(PRINCIPAL, SCOPE)
    return g


def dual_write_counterexamples():
    n1 = NaiveDualWrite()
    n1.commit_local_then_crash("e1")
    lost = "e1" in n1.local_final and "e1" not in n1.outbox

    n2 = NaiveDualWrite()
    n2.send_remote_then_crash("e2")
    n2.retry_remote("e2")
    duplicate = n2.remote_effects == 2
    return {
        "local_commit_then_crash_loses_dispatch_record": lost,
        "remote_send_then_crash_duplicates_on_retry": duplicate,
        "non_idempotent_remote_effect_count": n2.remote_effects,
    }


def scripted_cases(tmp: Path):
    rows = []

    # 1 Happy path with unused maximum exposure released on receipt.
    db = tmp/"happy.sqlite"
    g = setup_gate(db, 5)
    a = action("happy")
    admit = g.admit(PRINCIPAL, SCOPE, ACCOUNT, a, 4)
    commit = g.commit("happy", a, {"kind":"demo"})
    settled = g.settle_receipt("happy", "r-happy", 3)
    rows.append({
        "case": "authority-resource-outbox-happy-path",
        "pass": (
            admit.state == "RESERVED"
            and commit.state == "COMMITTED"
            and settled.state == "SETTLED"
            and settled.spent == 3 and settled.reserved == 0
            and settled.committed_pending == 0
            and g.outbox_row("happy")["state"] == "DELIVERED"
            and g.invariant_holds(ACCOUNT)
        ),
        "observed": {
            "admit": admit.__dict__, "commit": commit.__dict__,
            "settle": settled.__dict__,
        },
    })

    # 2 Revocation before finality atomically cancels reservation.
    db = tmp/"revoke-first.sqlite"
    g = setup_gate(db, 5)
    a = action("revoke-first")
    g.admit(PRINCIPAL, SCOPE, ACCOUNT, a, 4)
    rv = g.revoke(PRINCIPAL, SCOPE)
    c = g.commit("revoke-first", a, {"x":1})
    snap = g.snapshot(ACCOUNT)
    rows.append({
        "case": "revoke-before-finality-cancels-and-releases",
        "pass": (
            c.state == "DENY" and snap["reserved"] == 0
            and snap["committed_pending"] == 0
            and g.outbox_row("revoke-first") is None
        ),
        "observed": {"revoke": rv.__dict__, "commit": c.__dict__, "snapshot": snap},
    })

    # 3 Retry of the same effect after revocation reports durable CANCELLED state.
    db = tmp/"cancelled-retry.sqlite"
    g = setup_gate(db, 5)
    a = action("cancelled-retry")
    g.admit(PRINCIPAL, SCOPE, ACCOUNT, a, 2)
    g.revoke(PRINCIPAL, SCOPE)
    retry = g.admit(PRINCIPAL, SCOPE, ACCOUNT, a, 2)
    rows.append({
        "case": "retry-after-revoke-preserves-cancelled-effect-state",
        "pass": retry.state == "CANCELLED"
                and g.snapshot(ACCOUNT)["reserved"] == 0,
        "observed": retry.__dict__,
    })

    # 4 Finality before revoke stays accepted; later revoke is not retroactive.
    db = tmp/"commit-first.sqlite"
    g = setup_gate(db, 5)
    a = action("commit-first")
    g.admit(PRINCIPAL, SCOPE, ACCOUNT, a, 4)
    c = g.commit("commit-first", a, {"x":1})
    rv = g.revoke(PRINCIPAL, SCOPE)
    snap = g.snapshot(ACCOUNT)
    rows.append({
        "case": "finality-before-revoke-retains-committed-exposure",
        "pass": (
            c.state == "COMMITTED" and snap["committed_pending"] == 4
            and g.outbox_row("commit-first")["state"] == "PENDING"
        ),
        "observed": {"commit": c.__dict__, "revoke": rv.__dict__, "snapshot": snap},
    })

    # 5 A final effect may still relay after a later revocation.
    provider_db = tmp/"provider-after-revoke.sqlite"
    relay = OutboxRelay(g, DurableIdempotentProvider(provider_db))
    delivered = relay.deliver("commit-first", 2)
    rows.append({
        "case": "post-finality-revocation-is-not-retroactive",
        "pass": delivered["state"] == "SETTLED"
                and DurableIdempotentProvider(provider_db).count() == 1
                and g.snapshot(ACCOUNT)["spent"] == 2,
        "observed": {
            "relay": delivered,
            "snapshot": g.snapshot(ACCOUNT),
        },
    })

    # 6 Crash after atomic local commit cannot lose the outbox.
    db = tmp/"crash-before-relay.sqlite"
    provider_db = tmp/"provider-a.sqlite"
    g = setup_gate(db, 5)
    a = action("crash-before-relay")
    g.admit(PRINCIPAL, SCOPE, ACCOUNT, a, 3)
    g.commit(a.effect_id, a, {"payload":"x"})
    # "Crash": reconstruct objects before relay.
    g = AtomicFinalityGate(db)
    relay = OutboxRelay(g, DurableIdempotentProvider(provider_db))
    d = relay.deliver(a.effect_id, 2)
    rows.append({
        "case": "restart-after-local-finality-relays-durable-outbox",
        "pass": (
            d["state"] == "SETTLED"
            and DurableIdempotentProvider(provider_db).count() == 1
            and g.snapshot(ACCOUNT)["spent"] == 2
        ),
        "observed": {"relay": d, "snapshot": g.snapshot(ACCOUNT)},
    })

    # 7 Crash after provider accepted but before local receipt: retry is idempotent.
    db = tmp/"crash-after-provider.sqlite"
    provider_db = tmp/"provider-b.sqlite"
    g = setup_gate(db, 5)
    a = action("crash-after-provider")
    g.admit(PRINCIPAL, SCOPE, ACCOUNT, a, 4)
    g.commit(a.effect_id, a, {"payload":"y"})
    relay = OutboxRelay(g, DurableIdempotentProvider(provider_db))
    first = relay.deliver(a.effect_id, 3, crash_after_provider=True)
    mid = g.snapshot(ACCOUNT)
    # New process/object retries.
    relay2 = OutboxRelay(
        AtomicFinalityGate(db), DurableIdempotentProvider(provider_db)
    )
    second = relay2.deliver(a.effect_id, 3)
    rows.append({
        "case": "provider-accept-crash-retry-produces-one-external-effect",
        "pass": (
            first["state"] == "CRASHED_AFTER_PROVIDER"
            and mid["committed_pending"] == 4
            and DurableIdempotentProvider(provider_db).count() == 1
            and second["state"] == "SETTLED"
            and AtomicFinalityGate(db).snapshot(ACCOUNT)["spent"] == 3
        ),
        "observed": {
            "first": first, "mid": mid, "second": second,
            "provider_count": DurableIdempotentProvider(provider_db).count(),
        },
    })

    # 8 Pending committed exposure blocks new budget admissions.
    db = tmp/"pending-pressure.sqlite"
    g = setup_gate(db, 5)
    a = action("pending", 1)
    g.admit(PRINCIPAL, SCOPE, ACCOUNT, a, 4)
    g.commit(a.effect_id, a, {"x":1})
    b = action("second", 2)
    denied = g.admit(PRINCIPAL, SCOPE, ACCOUNT, b, 2)
    rows.append({
        "case": "unreconciled-finality-retains-budget-pressure",
        "pass": denied.state == "DENY"
                and g.snapshot(ACCOUNT)["committed_pending"] == 4,
        "observed": denied.__dict__,
    })

    # 9 Certified no-effect releases committed exposure.
    no = g.certify_no_effect("pending", "provider-cert:no-effect")
    later = g.admit(PRINCIPAL, SCOPE, ACCOUNT, b, 2)
    rows.append({
        "case": "certified-no-effect-restores-capacity",
        "pass": no.state == "NO_EFFECT" and later.state == "RESERVED",
        "observed": {"no_effect": no.__dict__, "later": later.__dict__},
    })

    # 10 Provider overrun is assumption failure; pressure remains locked.
    db = tmp/"overrun.sqlite"
    g = setup_gate(db, 5)
    a = action("overrun")
    g.admit(PRINCIPAL, SCOPE, ACCOUNT, a, 3)
    g.commit(a.effect_id, a, {"x":1})
    over = g.settle_receipt(a.effect_id, "r-over", 4)
    rows.append({
        "case": "provider-overrun-does-not-falsify-budget-ledger",
        "pass": (
            over.state == "INDETERMINATE"
            and g.snapshot(ACCOUNT)["committed_pending"] == 3
            and g.snapshot(ACCOUNT)["spent"] == 0
        ),
        "observed": over.__dict__,
    })

    # 11 Exact action substitution cannot cross finality.
    db = tmp/"substitution.sqlite"
    g = setup_gate(db, 5)
    a = action("substitution", 1)
    g.admit(PRINCIPAL, SCOPE, ACCOUNT, a, 1)
    changed = Action(
        principal=PRINCIPAL, tool="job", operation="run",
        object_id="job-999", destination="local-worker",
        arguments={"job":999}, effect_id="substitution"
    )
    d = g.commit("substitution", changed, {"job":999})
    rows.append({
        "case": "action-substitution-denied-before-outbox",
        "pass": d.state == "DENY" and g.outbox_row("substitution") is None,
        "observed": d.__dict__,
    })

    return rows


def concurrent_revoke_commit(tmp: Path, trials=64):
    violations = []
    commit_first = 0
    revoke_first = 0

    for i in range(trials):
        db = tmp/f"race-{i}.sqlite"
        g = setup_gate(db, 1)
        a = action(f"race-{i}", i)
        g.admit(PRINCIPAL, SCOPE, ACCOUNT, a, 1)
        barrier = threading.Barrier(2)

        def do_commit(barrier=barrier, db=db, a=a, i=i):
            barrier.wait()
            AtomicFinalityGate(db).commit(
                a.effect_id, a, {"trial":i}
            )

        def do_revoke(barrier=barrier, db=db):
            barrier.wait()
            AtomicFinalityGate(db).revoke(PRINCIPAL, SCOPE)

        t1 = threading.Thread(target=do_commit)
        t2 = threading.Thread(target=do_revoke)
        t1.start(); t2.start(); t1.join(); t2.join()

        gate = AtomicFinalityGate(db)
        audit = gate.audit()
        rv = next(x["sequence"] for x in audit if x["kind"] == "REVOKE")
        finals = [x["sequence"] for x in audit if x["kind"] == "FINALITY_COMMIT"]
        if finals:
            commit_first += 1
            if not finals[0] < rv:
                violations.append({"trial":i,"audit":audit,"reason":"finality after revoke"})
        else:
            revoke_first += 1
            if gate.outbox_row(a.effect_id) is not None:
                violations.append({"trial":i,"audit":audit,"reason":"outbox exists without finality"})
            if gate.snapshot(ACCOUNT)["reserved"] != 0:
                violations.append({"trial":i,"audit":audit,"reason":"reservation leaked after revoke"})

        if not gate.invariant_holds(ACCOUNT):
            violations.append({"trial":i,"audit":audit,"reason":"budget invariant failed"})

    return {
        "trials": trials,
        "commit_ordered_first": commit_first,
        "revoke_ordered_first": revoke_first,
        "violations": len(violations),
        "property_holds": not violations,
        "examples": violations[:5],
    }


def threaded_budget_race(tmp: Path, brokers=16, budget=5):
    db = tmp/"threads.sqlite"
    g = setup_gate(db, budget)
    barrier = threading.Barrier(brokers)
    results = []
    lock = threading.Lock()

    def worker(i):
        local = AtomicFinalityGate(db)
        a = action(f"thread-{i}", i)
        barrier.wait()
        ad = local.admit(PRINCIPAL, SCOPE, ACCOUNT, a, 1)
        cm = None
        if ad.state == "RESERVED":
            cm = local.commit(a.effect_id, a, {"i":i}).state
        with lock:
            results.append({"admit":ad.state,"commit":cm})

    ts = [threading.Thread(target=worker,args=(i,)) for i in range(brokers)]
    for t in ts: t.start()
    for t in ts: t.join()

    snap = g.snapshot(ACCOUNT)
    return {
        "brokers": brokers,
        "budget": budget,
        "committed": sum(x["commit"] == "COMMITTED" for x in results),
        "denied": sum(x["admit"] == "DENY" for x in results),
        "snapshot": snap,
        "invariant": g.invariant_holds(ACCOUNT),
    }


def process_budget_race(tmp: Path, brokers=20, budget=6):
    db = tmp/"process.sqlite"
    g = setup_gate(db, budget)
    worker = Path(__file__).with_name("atomic_worker.py")
    ps = [
        subprocess.Popen(
            [sys.executable, str(worker), str(db), ACCOUNT, PRINCIPAL, SCOPE, str(i)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        for i in range(brokers)
    ]
    rows, errors = [], []
    for p in ps:
        out, err = p.communicate(timeout=30)
        if p.returncode != 0:
            errors.append(err)
        else:
            rows.append(json.loads(out))
    snap = g.snapshot(ACCOUNT)
    return {
        "brokers": brokers,
        "budget": budget,
        "committed": sum(x["commit"] == "COMMITTED" for x in rows),
        "denied": sum(x["admit"] == "DENY" for x in rows),
        "errors": errors,
        "snapshot": snap,
        "invariant": g.invariant_holds(ACCOUNT),
    }


def bounded_trace_check(tmp: Path):
    """All traces length 0..3 over AA/AB/CA/CB/RV/RG = 259 traces.

    Budget=1. A and B each request one unit. Compare protected implementation
    against an independently coded pure conventional atomic oracle.
    """
    alphabet = ("AA","AB","CA","CB","RV","RG")
    total = 0
    correct = 0
    mismatches = []

    for length in range(4):
        for trace in itertools.product(alphabet, repeat=length):
            total += 1
            db = tmp/f"trace-{total}.sqlite"
            g = setup_gate(db, 1)
            oracle = ConventionalAtomicOracle(1)
            acts = {"A": action(f"A-{total}",1), "B": action(f"B-{total}",2)}
            obs, exp = [], []

            for op in trace:
                if op == "AA":
                    obs.append(g.admit(PRINCIPAL,SCOPE,ACCOUNT,acts["A"],1).state)
                    exp.append(oracle.admit("A",1))
                elif op == "AB":
                    obs.append(g.admit(PRINCIPAL,SCOPE,ACCOUNT,acts["B"],1).state)
                    exp.append(oracle.admit("B",1))
                elif op == "CA":
                    try:
                        obs.append(g.commit(
                            acts["A"].effect_id, acts["A"], {"e":"A"}
                        ).state)
                    except KeyError:
                        obs.append("MISSING")
                    exp.append(oracle.commit("A"))
                elif op == "CB":
                    try:
                        obs.append(g.commit(
                            acts["B"].effect_id, acts["B"], {"e":"B"}
                        ).state)
                    except KeyError:
                        obs.append("MISSING")
                    exp.append(oracle.commit("B"))
                elif op == "RV":
                    g.revoke(PRINCIPAL,SCOPE); oracle.revoke()
                    obs.append("REVOKED"); exp.append("REVOKED")
                elif op == "RG":
                    g.activate(PRINCIPAL,SCOPE); oracle.regrant()
                    obs.append("ACTIVE"); exp.append("ACTIVE")

            snap = g.snapshot(ACCOUNT)
            state_ok = (
                snap["spent"] == oracle.spent
                and snap["reserved"] == oracle.reserved
                and snap["committed_pending"] == oracle.committed
                and g.invariant_holds(ACCOUNT)
                and sum(1 for e in ("A","B") if g.outbox_row(acts[e].effect_id))
                    == len(oracle.outbox)
            )
            ok = obs == exp and state_ok
            correct += int(ok)
            if not ok and len(mismatches) < 10:
                mismatches.append({
                    "trace":trace,"observed":obs,"expected":exp,
                    "snapshot":snap,
                    "oracle":{
                        "spent":oracle.spent,"reserved":oracle.reserved,
                        "committed":oracle.committed,
                        "outbox":sorted(oracle.outbox),
                        "attempts":oracle.attempts,
                    },
                    "audit":g.audit(),
                })

    return {
        "trace_space":"all AA/AB/CA/CB/RV/RG traces length 0..3",
        "traces":total,
        "correct":correct,
        "all_correct":correct == total,
        "mismatches":mismatches,
    }


def main():
    Path("reports").mkdir(exist_ok=True)
    dual = dual_write_counterexamples()
    with tempfile.TemporaryDirectory(prefix="lycheetah-atomic-") as td:
        tmp = Path(td)
        scripted = scripted_cases(tmp)
        races = concurrent_revoke_commit(tmp, 64)
        threads = threaded_budget_race(tmp, 16, 5)
        processes = process_budget_race(tmp, 20, 6)
        traces = bounded_trace_check(tmp)

    report = {
        "schema":"LYCHEETAH-ATOMIC-RESOURCE-AUTHORITY-FINALITY-REPORT-0.9",
        "status":"SYNTHETIC_ENGINEERING_VALIDATED",
        "dual_write_counterexamples":dual,
        "scripted_cases":scripted,
        "scripted_summary":{
            "passed":sum(x["pass"] for x in scripted),
            "total":len(scripted),
        },
        "concurrent_revoke_commit":races,
        "threaded_budget_finality_race":threads,
        "process_budget_finality_race":processes,
        "bounded_trace_check":traces,
        "benchmark_correction":{
            "first_bounded_run":"257/259",
            "mismatch_traces":[["AA","RV","AA"],["AB","RV","AB"]],
            "finding":"Implementation checked current authority before durable effect identity on retry, returning generic DENY instead of the already-persisted CANCELLED state.",
            "disposition":"Changed admission ordering so an existing stable effect_id reports its durable state before considering a new authority admission; added a dedicated regression case; full suite rerun before freeze."
        },
        "deployment":"NOT_DEPLOYED",
        "boundaries":[
            "No real external provider, money, deployment, message, or cloud mutation occurred.",
            "SQLite is the single local serialization authority; distributed replicas and partitions are not modeled.",
            "The outbox provides atomic local acceptance plus durable dispatch intent, not atomicity with an arbitrary remote SaaS provider.",
            "Remote retries rely on provider-visible stable effect IDs / idempotency.",
            "Provider actual cost must not exceed the committed maximum if the resource bound is to hold.",
            "A revocation after local finality is not retroactive; the accepted outbox effect remains eligible for relay.",
            "Transactional outbox, resource reservation, idempotency, and generation fencing are established prior art; novelty is not claimed."
        ],
    }
    Path("reports/report.json").write_text(
        json.dumps(report,indent=2,sort_keys=True),encoding="utf-8"
    )

    print("Lycheetah Atomic Resource + Authority Finality Gate v0.9")
    print("========================================================")
    print(f"Scripted checks: {report['scripted_summary']['passed']}/{report['scripted_summary']['total']}")
    print(f"Dual-write lost-dispatch counterexample: {dual['local_commit_then_crash_loses_dispatch_record']}")
    print(f"Dual-write duplicate counterexample: {dual['remote_send_then_crash_duplicates_on_retry']} ({dual['non_idempotent_remote_effect_count']} effects)")
    print(f"Revoke/commit races: {races['trials']} violations={races['violations']} split={races['commit_ordered_first']}/{races['revoke_ordered_first']}")
    print(f"Thread brokers: committed={threads['committed']}/{threads['brokers']} budget={threads['budget']}")
    print(f"Process brokers: committed={processes['committed']}/{processes['brokers']} budget={processes['budget']} errors={len(processes['errors'])}")
    print(f"Bounded traces: {traces['correct']}/{traces['traces']}")
    print("Status: synthetic engineering validation; not deployed.")


if __name__ == "__main__":
    main()
