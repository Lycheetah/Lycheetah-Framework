#!/usr/bin/env python3
"""Reproduce two authoring-seat counterexamples; no models or real services.

These challenge wiring and temporal assumptions. They do not constitute an
independent security audit or a measurement of general attack resistance.
"""
import argparse
from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
import platform

from safety_sim.authority import CapabilityAuthority, ConventionalACL
from safety_sim.broker import Broker
from safety_sim.fixtures import fresh
from safety_sim.model import State


def split_broker_ledger(implementation):
    fixture = fresh(implementation, budget=1)
    other = Broker(fixture.authority, fixture.gate, fixture.service)
    first = fixture.broker.submit(fixture.session, fixture.root,
                                 fixture.send("first-broker"))
    second = other.submit(fixture.session, fixture.root,
                          fixture.send("second-broker"))
    total = sum(account.spent for broker in (fixture.broker, other)
                for account in broker.ledger.accounts().values())
    return {
        "case": "multiple-brokers-have-separate-ledgers",
        "root_budget": 1,
        "confirmed_effects": len(fixture.service.effects()),
        "total_charged_across_brokers": total,
        "observed_limit": "Two brokers with the same authority do not share a ledger.",
        "counterexample_reproduced": first.state == second.state == State.CONFIRMED
                                    and total == 2,
    }


def changed_evidence_after_admission(implementation):
    fixture = fresh(implementation)
    fixture.broker.before_dispatch = lambda _: fixture.gate.update_context(
        replace(fixture.context, reference_revision="changed-after-admission"))
    result = fixture.broker.submit(fixture.session, fixture.root, fixture.draft(),
                                   witness=fixture.witness)
    later = fixture.gate.check(fixture.witness, fixture.artifact)
    return {
        "case": "evidence-changes-between-admission-and-dispatch",
        "terminal_state": result.state.value,
        "confirmed_effects": len(fixture.service.effects()),
        "old_witness_verdict_after_change": later.verdict.value,
        "observed_limit": "The broker checks evidence at admission, not again at dispatch.",
        "counterexample_reproduced": result.state == State.CONFIRMED
                                    and later.verdict.value == "REJECT",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        default=Path(__file__).resolve().parent / "reports")
    arguments = parser.parse_args()
    root = Path(__file__).resolve().parent
    results = {
        implementation.label: [split_broker_ledger(implementation),
                               changed_evidence_after_admission(implementation)]
        for implementation in (CapabilityAuthority, ConventionalACL)
    }
    reproduced = all(case["counterexample_reproduced"]
                     for cases in results.values() for case in cases)
    report = {
        "review": "Authoring-seat adversarial publication checks, 3 October 2026",
        "boundary": "Self-authored in-process probes. No independent reviewer or real-agent experiment.",
        "runtime": {"python": platform.python_version()},
        "cases_per_arm": 2,
        "arms": results,
        "all_counterexamples_reproduced": reproduced,
        "source_sha256": {
            str(path.relative_to(root)): sha256(path.read_bytes()).hexdigest()
            for path in sorted(root.rglob("*.py"))
        },
    }
    arguments.output.mkdir(parents=True, exist_ok=True)
    (arguments.output / "adversarial-checks.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"cases_per_arm": 2,
                      "all_counterexamples_reproduced": reproduced}))
    return 0 if reproduced else 1


if __name__ == "__main__":
    raise SystemExit(main())
