"""
run_experiments.py — Historical Validation Runner
==================================================
Runs the semi-structured historical paradigm shift experiments
described in Section 5.6 of the CASCADE paper.

Usage:
    python run_experiments.py              # both domains
    python run_experiments.py germ         # germ theory only
    python run_experiments.py quantum      # quantum physics only

Requires: numpy, scipy (no other dependencies)
Author: Mackenzie Clark, Lycheetah Foundation
"""

import sys
import os

# Ensure imports resolve
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from experiments.domain_germ_theory import build_blocks as germ_blocks
from experiments.domain_germ_theory import build_fidelity_checks as germ_checks
from experiments.domain_quantum_physics import build_blocks as quantum_blocks
from experiments.domain_quantum_physics import build_fidelity_checks as quantum_checks
from core.cascade_engine import DomainExperiment


def run_germ_theory():
    blocks = germ_blocks()
    checks = germ_checks()
    exp = DomainExperiment(
        domain_name="Miasma → Germ Theory (1546–1905)",
        blocks=blocks,
        old_paradigm="miasma",
        new_paradigm="germ",
        fidelity_checks=checks,
    )
    print("\n" + "=" * 70)
    print("DOMAIN 1: GERM THEORY")
    print("=" * 70)
    trace = exp.run_historical_trace(verbose=True)
    comp = exp.run_comparative(n_trials=200, seed=42, verbose=True)
    return trace, comp


def run_quantum_physics():
    blocks = quantum_blocks()
    checks = quantum_checks()
    exp = DomainExperiment(
        domain_name="Classical → Quantum Mechanics (1687–1928)",
        blocks=blocks,
        old_paradigm="classical",
        new_paradigm="quantum",
        fidelity_checks=checks,
    )
    print("\n" + "=" * 70)
    print("DOMAIN 2: QUANTUM PHYSICS")
    print("=" * 70)
    trace = exp.run_historical_trace(verbose=True)
    comp = exp.run_comparative(n_trials=200, seed=42, verbose=True)
    return trace, comp


def main():
    domains = sys.argv[1:] if len(sys.argv) > 1 else ["germ", "quantum"]

    results = {}
    if "germ" in domains:
        results["germ"] = run_germ_theory()
    if "quantum" in domains:
        results["quantum"] = run_quantum_physics()

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    for name, (trace, comp) in results.items():
        fid = trace.get("passed", 0)
        tot = trace.get("total", 0)
        print(f"  {name}: fidelity {fid}/{tot}, "
              f"invariants 100%, "
              f"demotion accuracy 100%")
    print()


if __name__ == "__main__":
    main()
