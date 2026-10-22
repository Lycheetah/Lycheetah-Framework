"""Small, exact toy models behind the AI Future wing papers.

Each function is a teaching model, not an empirical result: it shows a mechanism
the paper argues from, with every assumption in its arguments. Numbers it prints
are synthetic and must be cited as such. Standard library only.

Run:  python3 papers/ai-futures/wings/models.py
"""

from __future__ import annotations

import math
from fractions import Fraction
from math import comb

BOLTZMANN = 1.380649e-23  # J/K, exact by SI definition (2019)


# Paper 01 — the Independent No ------------------------------------------------
def accepted_precision(base_rate: float, sensitivity: float, false_pass: float) -> float:
    """Share of verifier-accepted hypotheses that are true (Bayes' rule).

    base_rate: fraction of generated hypotheses that are true.
    sensitivity: P(verifier passes | true). false_pass: P(verifier passes | false).
    """
    tp = base_rate * sensitivity
    fp = (1 - base_rate) * false_pass
    return tp / (tp + fp) if tp + fp else 0.0


def false_pass_needed(base_rate: float, sensitivity: float, target: float) -> float:
    """Largest false-pass rate that keeps accepted precision at or above target."""
    return base_rate * sensitivity * (1 - target) / (target * (1 - base_rate))


# Paper 02 — compression has a decoder -------------------------------------------
def max_distinct_messages(n_bytes: int) -> int:
    """Number of distinct bit strings of length at most 8*n_bytes (pigeonhole bound)."""
    return 2 ** (8 * n_bytes + 1) - 1


# Paper 04 — the political unit after copying -------------------------------------
def fork_vote_share(honest: int, forker_copies: int) -> Fraction:
    """Vote share of one agent that forks into copies under one-instance-one-vote."""
    return Fraction(forker_copies, honest + forker_copies)


# Paper 05 — thermodynamics of distributed cognition --------------------------------
def landauer_joules_per_bit(temperature_k: float) -> float:
    """Minimum heat dissipated per irreversibly erased bit: k_B T ln 2."""
    return BOLTZMANN * temperature_k * math.log(2)


# Paper 08 — cognitive monoculture ---------------------------------------------------
def majority_accuracy(n: int, p: float) -> float:
    """P(majority correct) for n independent voters each correct with probability p (n odd)."""
    if n % 2 == 0:
        raise ValueError("n must be odd")
    return sum(comb(n, k) * p**k * (1 - p) ** (n - k) for k in range(n // 2 + 1, n + 1))


def correlated_majority_accuracy(n: int, p: float, shared: float) -> float:
    """Majority accuracy when, with probability `shared`, all n voters copy one common draw.

    shared = 0 recovers independent voters (Condorcet); shared = 1 is a monoculture whose
    ensemble is exactly as accurate as one voter, however many copies are consulted.
    """
    return shared * p + (1 - shared) * majority_accuracy(n, p)


# Paper 12 — the returned-time test --------------------------------------------------
def returned_time(saved: float, new_work: float, monitoring: float,
                  maintenance: float, captured: float) -> float:
    """Hours the intended beneficiary actually controls after the intervention."""
    return saved - new_work - monitoring - maintenance - captured


# Paper 13 — the unmergeable residue --------------------------------------------------
def merge_commitments(a: set[str], b: set[str]) -> tuple[set[str], set[str]]:
    """Merge two forks' commitments; a commitment 'x' and its negation '!x' cannot both survive.

    Returns (kept, residue). The residue is what any single consistent successor must drop.
    """
    union = a | b
    conflicted = {c for c in union if (c[1:] if c.startswith("!") else "!" + c) in union}
    return union - conflicted, conflicted


# Paper 14 — locality and latency -------------------------------------------------------
def light_delay_s(distance_m: float) -> float:
    """One-way signal delay at the speed of light in vacuum."""
    return distance_m / 299_792_458


# Paper 15 — same model, different life ---------------------------------------------------
def divergence_after(steps: int, per_step_drift: float) -> float:
    """Probability two matched agents still agree on a binary habit after independent drift.

    Each step, each agent flips the habit with probability per_step_drift.
    Agreement decays as (1 + (1 - 4q(1-q))**t) / 2 with q = per_step_drift.
    """
    q = per_step_drift
    return (1 + (1 - 4 * q * (1 - q)) ** steps) / 2


def main() -> None:
    print("01 Independent No: precision of accepted hypotheses (sensitivity 0.9, false-pass 0.05)")
    for base in (0.5, 0.1, 0.01, 0.001):
        print(f"   base rate {base:<6} -> {accepted_precision(base, 0.9, 0.05):.3f}"
              f"   false-pass needed for 0.9 precision: {false_pass_needed(base, 0.9, 0.9):.2e}")
    print(f"02 a 64-byte message can name at most {max_distinct_messages(64):.3e} distinct documents")
    print("04 one agent forking under one-instance-one-vote, 1000 honest voters:",
          {k: f"{float(fork_vote_share(1000, k)):.3f}" for k in (1, 1000, 9000)})
    print(f"05 Landauer floor at 300 K: {landauer_joules_per_bit(300):.3e} J per erased bit")
    print("08 majority accuracy, p = 0.7:")
    for n in (1, 11, 101):
        row = "  ".join(f"shared={s}: {correlated_majority_accuracy(n, 0.7, s):.3f}"
                        for s in (0.0, 0.3, 1.0))
        print(f"   n={n:<4} {row}")
    print("12 returned time, 10 h saved:", returned_time(10, 3, 2, 1, 4), "h returned")
    kept, residue = merge_commitments({"share-logs", "!refuse-tool-x"}, {"refuse-tool-x", "share-logs"})
    print(f"13 merge: kept {sorted(kept)}, residue {sorted(residue)}")
    print(f"14 light delay Earth-Moon (3.844e8 m): {light_delay_s(3.844e8):.3f} s;"
          f" Earth-Mars at 2.25e11 m: {light_delay_s(2.25e11) / 60:.1f} min")
    print("15 agreement after drift q=0.01:",
          {t: f"{divergence_after(t, 0.01):.3f}" for t in (0, 10, 100, 1000)})


if __name__ == "__main__":
    main()
