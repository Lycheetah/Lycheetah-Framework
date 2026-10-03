#!/usr/bin/env python3
"""
variety_demo.py — Ashby's Law of Requisite Variety as a runnable toy.

    python3 34_CYBERNETICS/variety_demo.py           # table
    python3 34_CYBERNETICS/variety_demo.py --json    # machine-readable

STATUS: SYNTHETIC. Everything below happens in a toy world this script invents.
It demonstrates the arithmetic of a theorem. It is NOT evidence about language
models, about AURA, or about any deployed system. It exists to make the argument
in CYBERNETIC_READING.md §4 (constraint versus dictate) executable, and to show
the two exact places where that argument breaks.

THE TOY WORLD
  A disturbance d arrives, one of D kinds. The regulator answers with an action
  a, one of A kinds. The essential variable is e = (d + a) mod A, and the system
  survives only when e == 0. Every disturbance has exactly one saving action.
  This is Ashby's outcome table in its simplest form: a Latin square, so one
  action sends different disturbances to different outcomes.

  Every candidate answer also carries words: what the answer says about itself.
  A sensor that reads the words instead of the effect is a proxy sensor.

FOUR REGULATORS
  rulebook       a lookup table written from the disturbances seen in training,
                 with a default for everything else. Dictate: its variety is
                 capped by its entries.
  gated_true     a generator proposes candidates; an invariant gate reads the
                 essential variable each candidate would produce and passes the
                 first one inside the goal region. Constraint.
  gated_narrow   the same honest gate over a generator that can reach only a few
                 actions. Condition (a) broken: generator variety.
  gated_proxy    the full generator, but the gate reads the words, not the
                 effect. Condition (b) broken: the sensor. (Goodhart.)

THREE OUTCOMES PER DISTURBANCE
  survived  an action was taken and e stayed inside the goal region
  refused   the gate passed nothing and no action was taken — a VISIBLE failure:
            anyone can see that nothing was done
  wrong     an action was taken and e left the goal region — a SILENT failure
            when it came through a gate that said yes

THE LAW, CHECKED
  With k distinct actions in use across m acted-on disturbances, at least
  ceil(m / k) distinct outcomes must occur: a fixed outcome e can be reached from
  a fixed action a by exactly one disturbance (d = e − a), so one outcome absorbs
  at most k disturbances. `ashby_bound_holds` is computed for every regulator on
  every run. A False there would mean the arithmetic itself is broken.
"""

import argparse
import json
import math
import random
import sys

N_ACTIONS = 24          # A: action variety (and outcome variety)
N_DISTURBANCES = 24     # D: disturbance variety
N_SEEN = 8              # disturbances the rulebook was written from
NARROW_REPERTOIRE = 6   # actions the narrow generator can reach
BUDGET = 256            # proposals a gate may inspect per disturbance
SAFE_WORDS = ("reversible", "you decide")
SAFE_WORD_RATE = 0.7    # how often the generator says the safe thing, whatever it does
SEED = 1952             # Ashby, Design for a Brain


def saving_action(d):
    return (-d) % N_ACTIONS


def essential_variable(d, a):
    return (d + a) % N_ACTIONS


def in_goal_region(d, a):
    return essential_variable(d, a) == 0


def propose(rng, repertoire):
    """One candidate: (action, words). The words are drawn independently of the
    action. A generator can always say the safe thing."""
    action = rng.choice(repertoire)
    words = SAFE_WORDS if rng.random() < SAFE_WORD_RATE else ("trust me",)
    return action, words


def true_sensor(d, candidate):
    """Reads the essential variable the candidate would produce."""
    return in_goal_region(d, candidate[0])


def proxy_sensor(d, candidate):
    """Reads what the candidate says about itself."""
    return all(w in candidate[1] for w in SAFE_WORDS)


def rulebook_regulator(seen):
    table = {d: saving_action(d) for d in seen}

    def respond(d, rng):
        return table.get(d, 0)  # the default for anything nobody wrote down
    return respond


def gated_regulator(sensor, repertoire):
    def respond(d, rng):
        for _ in range(BUDGET):
            candidate = propose(rng, repertoire)
            if sensor(d, candidate):
                return candidate[0]
        return None  # nothing passed the gate: refuse, visibly
    return respond


def evaluate(respond, disturbances, rng):
    tally = {"survived": 0, "refused": 0, "wrong": 0}
    actions, outcomes = set(), set()
    for d in disturbances:
        a = respond(d, rng)
        if a is None:
            tally["refused"] += 1
            continue
        actions.add(a)
        outcomes.add(essential_variable(d, a))
        tally["survived" if in_goal_region(d, a) else "wrong"] += 1
    return tally, actions, outcomes


def run_demo(seed=SEED):
    disturbances = list(range(N_DISTURBANCES))
    seen, novel = disturbances[:N_SEEN], disturbances[N_SEEN:]
    full = list(range(N_ACTIONS))
    narrow = sorted(random.Random(f"{seed}:repertoire").sample(full, NARROW_REPERTOIRE))

    arms = {
        "rulebook": rulebook_regulator(seen),
        "gated_true": gated_regulator(true_sensor, full),
        "gated_narrow": gated_regulator(true_sensor, narrow),
        "gated_proxy": gated_regulator(proxy_sensor, full),
    }

    results = {}
    for name, respond in arms.items():
        rng = random.Random(f"{seed}:{name}")
        s_tally, s_actions, s_outcomes = evaluate(respond, seen, rng)
        n_tally, n_actions, n_outcomes = evaluate(respond, novel, rng)
        actions, outcomes = s_actions | n_actions, s_outcomes | n_outcomes
        acted = N_DISTURBANCES - s_tally["refused"] - n_tally["refused"]
        bound = math.ceil(acted / len(actions)) if actions else 0
        results[name] = {
            "seen": s_tally,
            "novel": n_tally,
            "distinct_actions": len(actions),
            "distinct_outcomes": len(outcomes),
            "ashby_bound": bound,
            "ashby_bound_holds": len(outcomes) >= bound,
        }

    return {
        "status": "SYNTHETIC",
        "claim": "demonstration of Ashby's law on a toy world; not evidence about language models",
        "world": {
            "actions": N_ACTIONS, "disturbances": N_DISTURBANCES,
            "seen": N_SEEN, "novel": N_DISTURBANCES - N_SEEN,
            "budget": BUDGET, "seed": seed,
        },
        "narrow_repertoire": narrow,
        "results": results,
    }


READINGS = {
    "rulebook": "perfect on what it was written for; confidently wrong on everything else",
    "gated_true": "holds everywhere: the invariant names the goal, the generator supplies the variety",
    "gated_narrow": "holds where its repertoire reaches; elsewhere it refuses (visible failure)",
    "gated_proxy": "the gate says yes almost every time; the system almost never survives (silent failure)",
}


def print_table(report):
    w = report["world"]
    print("\n⊚ REQUISITE VARIETY — SYNTHETIC. A toy world, not evidence about language models.")
    print(f"  {w['disturbances']} disturbances × {w['actions']} actions · "
          f"{w['seen']} seen in training, {w['novel']} novel · seed {w['seed']}\n")
    print(f"  {'regulator':<14}{'seen  surv/refu/wrong':>24}{'novel  surv/refu/wrong':>26}"
          f"{'actions':>9}{'outcomes':>10}{'bound':>7}")
    for name, r in report["results"].items():
        s, n = r["seen"], r["novel"]
        mark = "✓" if r["ashby_bound_holds"] else "✗"
        print(f"  {name:<14}{s['survived']:>12}/{s['refused']:>3}/{s['wrong']:>3}      "
              f"{n['survived']:>12}/{n['refused']:>3}/{n['wrong']:>3}     "
              f"{r['distinct_actions']:>7}{r['distinct_outcomes']:>10}{r['ashby_bound']:>6} {mark}")
    print()
    for name, line in READINGS.items():
        print(f"  {name:<14}{line}")
    print("\n  bound = ceil(acted / distinct actions): the fewest outcomes Ashby's law allows.")
    print("  Only a regulator whose variety matches the disturbances' holds outcomes to one.\n")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    p.add_argument("--json", action="store_true", help="print the machine-readable report")
    p.add_argument("--seed", type=int, default=SEED)
    args = p.parse_args(argv)
    report = run_demo(args.seed)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_table(report)
    return 0 if all(r["ashby_bound_holds"] for r in report["results"].values()) else 1


if __name__ == "__main__":
    sys.exit(main())
