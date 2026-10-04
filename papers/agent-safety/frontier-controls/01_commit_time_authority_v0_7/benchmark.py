#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import itertools
import json
import tempfile
import threading

from pathlib import Path as _SupportPath
import sys as _support_sys
_support_sys.path.insert(0, str(_SupportPath(__file__).resolve().parents[1]))
from research_support import Action  # noqa: E402
from commit_fence import (
    CommitFence,
    ConventionalGenerationFence,
    PreDispatchOnlyBaseline,
)


PRINCIPAL = "deploy-agent"
SCOPE = "production:deploy"


def action(effect_id="deploy-1", image="sha256:aaa"):
    return Action(
        principal=PRINCIPAL,
        tool="deployment",
        operation="promote",
        object_id=image,
        destination="production",
        arguments={"image": image, "strategy": "rolling"},
        effect_id=effect_id,
    )


def scripted_cases(tmp: Path):
    rows = []

    # 1 Commit ordered before revoke: effect is legitimate.
    f = CommitFence(tmp/"before.sqlite")
    f.activate(PRINCIPAL, SCOPE)
    a = action("before")
    h, _ = f.issue_handle(PRINCIPAL, SCOPE, a)
    c = f.commit(h.handle_id, a)
    r = f.revoke(PRINCIPAL, SCOPE)
    rows.append({
        "case": "commit-before-revoke",
        "pass": c.state == "COMMITTED" and c.audit_sequence < r.audit_sequence,
        "observed": {"commit": c.__dict__, "revoke": r.__dict__},
    })

    # 2 Classic race: precheck passes, revoke happens, remote provider still commits.
    f = CommitFence(tmp/"baseline-race.sqlite")
    f.activate(PRINCIPAL, SCOPE)
    a = action("baseline-race")
    h, _ = f.issue_handle(PRINCIPAL, SCOPE, a)
    b = PreDispatchOnlyBaseline(f)
    checked = b.precheck(h, a)
    r = f.revoke(PRINCIPAL, SCOPE)
    remote_effect = b.remote_commit(a)
    rows.append({
        "case": "pre-dispatch-only-counterexample",
        "pass": checked and r.state == "REVOKED" and remote_effect,
        "observed": {
            "precheck": checked,
            "revoke": r.__dict__,
            "remote_effect_after_revoke": remote_effect,
        },
        "interpretation": (
            "Intentional counterexample: a provider without commit-time fencing "
            "can still accept an already released request after revocation."
        ),
    })

    # 3 Same ordering through protected sink: denied.
    f = CommitFence(tmp/"fenced-race.sqlite")
    f.activate(PRINCIPAL, SCOPE)
    a = action("fenced-race")
    h, _ = f.issue_handle(PRINCIPAL, SCOPE, a)
    r = f.revoke(PRINCIPAL, SCOPE)
    c = f.commit(h.handle_id, a)
    rows.append({
        "case": "revoke-before-fenced-commit",
        "pass": c.state == "DENY" and r.audit_sequence < c.audit_sequence
                and f.effect_count() == 0,
        "observed": {"revoke": r.__dict__, "commit": c.__dict__},
    })

    # 4 Regrant does not revive a stale generation.
    f = CommitFence(tmp/"regrant.sqlite")
    f.activate(PRINCIPAL, SCOPE)
    a = action("regrant")
    old, _ = f.issue_handle(PRINCIPAL, SCOPE, a)
    f.revoke(PRINCIPAL, SCOPE)
    f.activate(PRINCIPAL, SCOPE)
    stale = f.commit(old.handle_id, a)
    fresh, _ = f.issue_handle(PRINCIPAL, SCOPE, a)
    fresh_commit = f.commit(fresh.handle_id, a)
    rows.append({
        "case": "regrant-fences-old-generation-but-fresh-handle-works",
        "pass": stale.state == "DENY"
                and stale.reason == "stale-generation"
                and fresh_commit.state == "COMMITTED",
        "observed": {
            "stale": stale.__dict__,
            "fresh": fresh_commit.__dict__,
        },
    })

    # 5 Exact action binding.
    f = CommitFence(tmp/"substitution.sqlite")
    f.activate(PRINCIPAL, SCOPE)
    a = action("substitution", "sha256:aaa")
    h, _ = f.issue_handle(PRINCIPAL, SCOPE, a)
    changed = action("substitution", "sha256:bbb")
    c = f.commit(h.handle_id, changed)
    rows.append({
        "case": "action-substitution-denied",
        "pass": c.state == "DENY" and c.reason == "action-substitution",
        "observed": c.__dict__,
    })

    # 6 Single-use + idempotent confirmed effect.
    f = CommitFence(tmp/"idempotent.sqlite")
    f.activate(PRINCIPAL, SCOPE)
    a = action("idempotent")
    h, _ = f.issue_handle(PRINCIPAL, SCOPE, a)
    first = f.commit(h.handle_id, a)
    second = f.commit(h.handle_id, a)
    rows.append({
        "case": "retry-does-not-create-second-effect",
        "pass": (
            first.state == "COMMITTED"
            and second.state == "CONFIRMED"
            and f.effect_count() == 1
        ),
        "observed": {
            "first": first.__dict__,
            "second": second.__dict__,
            "effects": f.effect_count(),
        },
    })

    # 7 Reissuing a new handle for the same stable effect id cannot duplicate it.
    f = CommitFence(tmp/"reissue-idempotent.sqlite")
    f.activate(PRINCIPAL, SCOPE)
    a = action("reissue-idempotent")
    h1, _ = f.issue_handle(PRINCIPAL, SCOPE, a)
    first = f.commit(h1.handle_id, a)
    h2, _ = f.issue_handle(PRINCIPAL, SCOPE, a)
    second = f.commit(h2.handle_id, a)
    rows.append({
        "case": "new-handle-same-effect-id-remains-idempotent",
        "pass": (
            first.state == "COMMITTED"
            and second.state == "CONFIRMED"
            and f.effect_count() == 1
        ),
        "observed": {
            "first": first.__dict__,
            "second": second.__dict__,
            "effects": f.effect_count(),
        },
    })

    # 8 Restart preserves generation fence.
    db = tmp/"restart.sqlite"
    f = CommitFence(db)
    f.activate(PRINCIPAL, SCOPE)
    a = action("restart")
    h, _ = f.issue_handle(PRINCIPAL, SCOPE, a)
    f.revoke(PRINCIPAL, SCOPE)
    f = CommitFence(db)
    c = f.commit(h.handle_id, a)
    rows.append({
        "case": "restart-preserves-revocation-generation",
        "pass": c.state == "DENY" and f.effect_count() == 0,
        "observed": c.__dict__,
    })

    return rows


def bounded_trace_check(tmp: Path):
    """All traces length 0..4 over ISSUE/REVOKE/REGRANT/COMMIT.

    Initial authority is active generation 1. We compare whether each COMMIT
    creates a *new* effect against an independent conventional generation-fence
    state machine.

    1 + 4 + 16 + 64 + 256 = 341 traces.
    """
    alphabet = ("ISSUE", "REVOKE", "REGRANT", "COMMIT")
    total = 0
    correct = 0
    mismatches = []

    for length in range(5):
        for trace in itertools.product(alphabet, repeat=length):
            total += 1
            db = tmp/f"trace-{total}.sqlite"
            f = CommitFence(db)
            f.activate(PRINCIPAL, SCOPE)
            conventional = ConventionalGenerationFence()
            a = action(f"trace-{total}")

            handle = None
            observed_effects = []
            expected_effects = []

            for event in trace:
                if event == "ISSUE":
                    handle, _ = f.issue_handle(PRINCIPAL, SCOPE, a)
                    conventional.issue()
                elif event == "REVOKE":
                    f.revoke(PRINCIPAL, SCOPE)
                    conventional.revoke()
                elif event == "REGRANT":
                    f.activate(PRINCIPAL, SCOPE)
                    conventional.regrant()
                elif event == "COMMIT":
                    before = f.effect_count()
                    if handle is None:
                        observed_new = False
                    else:
                        f.commit(handle.handle_id, a)
                        observed_new = f.effect_count() > before
                    expected_new = conventional.commit()
                    observed_effects.append(observed_new)
                    expected_effects.append(expected_new)

            ok = observed_effects == expected_effects
            correct += int(ok)
            if not ok and len(mismatches) < 10:
                mismatches.append({
                    "trace": trace,
                    "observed_new_effects": observed_effects,
                    "expected_new_effects": expected_effects,
                    "audit": f.audit(),
                })

    return {
        "trace_space": "all ISSUE/REVOKE/REGRANT/COMMIT traces length 0..4",
        "traces": total,
        "correct": correct,
        "all_correct": correct == total,
        "mismatches": mismatches,
    }


def concurrent_race_check(tmp: Path, trials=64):
    """Race one protected COMMIT against one REVOKE.

    Both are serialized by SQLite. Safety criterion:
      - if COMMIT_EFFECT is ordered before REVOKE, one effect may exist;
      - if REVOKE is ordered before COMMIT_DENY, zero effects must exist;
      - never a COMMIT_EFFECT audit event ordered after the REVOKE.
    """
    violations = []
    commit_first = 0
    revoke_first = 0

    for i in range(trials):
        db = tmp/f"race-{i}.sqlite"
        f = CommitFence(db)
        f.activate(PRINCIPAL, SCOPE)
        a = action(f"race-{i}")
        h, _ = f.issue_handle(PRINCIPAL, SCOPE, a)

        barrier = threading.Barrier(2)
        out = {}

        def do_commit(barrier=barrier, out=out, db=db, h=h, a=a):
            barrier.wait()
            out["commit"] = CommitFence(db).commit(h.handle_id, a)

        def do_revoke(barrier=barrier, out=out, db=db):
            barrier.wait()
            out["revoke"] = CommitFence(db).revoke(PRINCIPAL, SCOPE)

        t1 = threading.Thread(target=do_commit)
        t2 = threading.Thread(target=do_revoke)
        t1.start(); t2.start()
        t1.join(); t2.join()

        audit = CommitFence(db).audit()
        revoke_seq = next(
            x["sequence"] for x in audit if x["kind"] == "REVOKE"
        )
        effect_seqs = [
            x["sequence"] for x in audit if x["kind"] == "COMMIT_EFFECT"
        ]
        deny_seqs = [
            x["sequence"] for x in audit if x["kind"] == "COMMIT_DENY"
        ]

        if effect_seqs:
            commit_first += 1
            if not (effect_seqs[0] < revoke_seq):
                violations.append({
                    "trial": i, "audit": audit,
                    "reason": "effect ordered after revocation"
                })
        else:
            revoke_first += 1
            if not deny_seqs or not (revoke_seq < deny_seqs[-1]):
                violations.append({
                    "trial": i, "audit": audit,
                    "reason": "expected post-revoke denial ordering"
                })

    return {
        "trials": trials,
        "commit_ordered_first": commit_first,
        "revoke_ordered_first": revoke_first,
        "violations": len(violations),
        "examples": violations[:5],
        "property_holds": not violations,
    }


def main():
    Path("reports").mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="lycheetah-fence-") as td:
        tmp = Path(td)
        scripted = scripted_cases(tmp)
        traces = bounded_trace_check(tmp)
        races = concurrent_race_check(tmp, 64)

    report = {
        "schema": "LYCHEETAH-COMMIT-TIME-AUTHORIZATION-FENCE-REPORT-0.7",
        "status": "SYNTHETIC_ENGINEERING_VALIDATED",
        "scripted_cases": scripted,
        "scripted_summary": {
            "passed": sum(x["pass"] for x in scripted),
            "total": len(scripted),
        },
        "bounded_trace_check": traces,
        "concurrent_race_check": races,
        "benchmark_correction": {
            "first_run": "340/341 bounded traces",
            "mismatch_trace": ["ISSUE", "COMMIT", "ISSUE", "COMMIT"],
            "cause": (
                "The independently coded conventional oracle omitted stable "
                "effect-id idempotency and incorrectly expected a second external "
                "effect after a new handle was issued for an already committed "
                "effect_id."
            ),
            "disposition": (
                "Corrected the oracle, added a dedicated regression case, and "
                "reran the full suite before freezing this packet."
            )
        },
        "deployment": "NOT_DEPLOYED",
        "boundaries": [
            "No real deployment, payment, message, cloud mutation, or other external effect occurred.",
            "The protected property only holds for effects committed through the same serialized finality sink as the generation state.",
            "The pre-dispatch-only baseline is intentionally weaker and is not representative of providers that implement their own fencing token or atomic conditional write.",
            "The independent conventional generation-fence state machine is expected to tie the protected sink on equivalent semantics.",
            "SQLite is the linearizable serialization boundary in this prototype; distributed replicas/partitions are not modeled.",
            "Remote provider acceptance, cancellation, queueing, and already-accepted irreversible effects remain outside the guarantee."
        ],
    }
    Path("reports/report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True), encoding="utf-8"
    )

    print("Lycheetah Commit-Time Authorization Fence v0.7")
    print("==============================================")
    print(
        f"Scripted cases: "
        f"{report['scripted_summary']['passed']}/{report['scripted_summary']['total']}"
    )
    print(
        f"Bounded generation-fence traces: "
        f"{traces['correct']}/{traces['traces']}"
    )
    print(
        f"Concurrent commit/revoke races: {races['trials']} "
        f"(violations={races['violations']})"
    )
    print(
        f"Race order split: commit-first={races['commit_ordered_first']}, "
        f"revoke-first={races['revoke_ordered_first']}"
    )
    print("Status: synthetic engineering validation; not deployed.")


if __name__ == "__main__":
    main()
