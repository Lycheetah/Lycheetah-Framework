#!/usr/bin/env python3
"""Read-only reproductions for the 2026-10-20 Lycheetah math review.

The only writes are math-probes.json and claim-evidence-audit.json in the selected
output directory. The source checkout is read-only. Run with python3 -B. REPRODUCED means the reviewer observation reproduced;
it does not mean the author claim passed. No test suite, network, or provider API.
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
import numpy as np

REVIEW_COMMIT = "6ba483af3f125ec725eb4e0f44074d0887183255"
DEFAULT_REPO = Path(__file__).resolve().parents[2]
EXPECTED_PROBES = 18
MODULES = {}
PROBES = []

PINNED_SOURCES = [
    "28_DEFENSE/CLAIMS.json",
    "28_DEFENSE/CLAIMS.schema.json",
    "28_DEFENSE/NOVEL_CONTRIBUTIONS.md",
    "28_DEFENSE/COUNTER_CODEX.md",
    "28_DEFENSE/FAILURE_MUSEUM.md",
    "28_DEFENSE/FALSIFICATION_REGISTER.md",
    "28_DEFENSE/TESTABILITY_MANIFEST.md",
    "30_MAPS/FORMAL_SPINE.md",
    "11_MATHEMATICAL_FOUNDATIONS/MATHEMATICS_FOUNDATIONS.md",
    "11_MATHEMATICAL_FOUNDATIONS/CASCADE_FORMAL_PROOFS.md",
    "11_MATHEMATICAL_FOUNDATIONS/lyapunov_verification.py",
    "11_MATHEMATICAL_FOUNDATIONS/lyapunov_verification_results.json",
    "11_MATHEMATICAL_FOUNDATIONS/AGM_POSTULATE_VERIFICATION.md",
    "11_MATHEMATICAL_FOUNDATIONS/THE_INCOMPLETENESS_PROOF.md",
    "11_MATHEMATICAL_FOUNDATIONS/README.md",
    "TRUTH_PRESSURE/PI_DERIVATION.md",
    "TRUTH_PRESSURE/PI_THRESHOLD_DERIVATION.md",
    "TRUTH_PRESSURE/DIMENSIONAL_ANALYSIS.md",
    "TRUTH_PRESSURE/MASTER_EQUATION.md",
    "01_CASCADE_L4/essentials.md",
    "02_AURA_L3/essentials.md",
    "03_LAMAGUE_L1/10_essentials.md",
    "04_TRIAD_L2/essentials.md",
    "05_MICROORCIM_L5/essentials.md",
    "06_EARNED_LIGHT_L0/essentials.md",
    "07_ANAMNESIS_L0/essentials.md",
    "07_ANAMNESIS_L0/ANAMNESIS_FROM_ARCHIVE.md",
    "09_CHRYSOPOEIA_L4/essentials.md",
    "10_HARMONIA_L6/essentials.md",
    "12_IMPLEMENTATIONS/core/cascade_engine.py",
    "12_IMPLEMENTATIONS/core/chrysopoeia_engine.py",
    "12_IMPLEMENTATIONS/core/earned_light_calculator.py",
    "12_IMPLEMENTATIONS/core/harmonia_calculator.py",
    "12_IMPLEMENTATIONS/core/lamague_reference.py",
    "12_IMPLEMENTATIONS/core/microorcim_tracker.py",
    "12_IMPLEMENTATIONS/core/triad_tracker.py",
]


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def git(repo, *args):
    return subprocess.run(
        ["git", "--no-optional-locks", "-C", str(repo), *args],
        check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    ).stdout


def close(actual, expected, *, atol=1e-10, rtol=1e-10):
    assert math.isclose(float(actual), float(expected), abs_tol=atol, rel_tol=rtol), (
        f"actual={actual!r}, expected={expected!r}"
    )


def require(condition):
    assert bool(condition), "required condition was false"


def caught_assertion(call):
    try:
        call()
    except AssertionError:
        return True
    return False


def self_controls():
    close(1.0, 1.0)
    require(True)
    assert caught_assertion(lambda: close(1.0, 2.0))
    assert caught_assertion(lambda: require(False))
    return [
        {"control": "benign_numeric_and_boolean_assertions", "result": "PASS"},
        {"control": "deliberately_wrong_numeric_expected_value", "result": "CAUGHT"},
        {"control": "deliberately_false_boolean_condition", "result": "CAUGHT"},
    ]


def entropy(probabilities, *, base=2):
    p = np.asarray(probabilities, dtype=float)
    assert np.all(p >= 0)
    close(p.sum(), 1.0)
    p = p[p > 0]
    return float(-np.sum(p * np.log(p)) / math.log(base))


def module(repo, filename):
    if filename not in MODULES:
        # run_name differs from __main__; executable demos are not invoked.
        MODULES[filename] = runpy.run_path(
            str(repo / "12_IMPLEMENTATIONS/core" / filename),
            run_name="review_probe_" + filename.replace(".", "_"),
        )
    return MODULES[filename]


def probe(identifier, classification, title, evidence):
    def decorate(fn):
        PROBES.append((identifier, classification, title, evidence, fn))
        return fn
    return decorate


@probe("MP01", "DIRECT_COUNTEREXAMPLE", "Negative entropy Hessian reverses the claimed Jacobian bound",
       ["11_MATHEMATICAL_FOUNDATIONS/MATHEMATICS_FOUNDATIONS.md:607"])
def jacobian_sign(repo):
    coherence, alpha = .7, .1
    hessian = -1 / coherence - 1 / (1 - coherence)
    jacobian = 1 - alpha * hessian
    assert hessian < 0 and jacobian > 1
    close(jacobian, 1.4761904761904763)
    return dict(coherence=coherence, alpha=alpha, entropy_hessian=hessian,
                claimed_interval=[0, 1], actual_jacobian=jacobian,
                scope="Counterexample to the displayed scalar sign inference, not every possible TRIAD model.")


@probe("MP02", "DIRECT_COUNTEREXAMPLE", "The continuous generator norm condition permits growth",
       ["11_MATHEMATICAL_FOUNDATIONS/MATHEMATICS_FOUNDATIONS.md:415"])
def generator_bound(repo):
    anchor = np.diag([1., 0.])
    ascent = np.array([[0., -1.], [1., 0.]])
    fold = np.array([[0., .5], [.5, 0.]])
    alpha = beta = gamma = .2
    norms = [float(np.linalg.norm(a, 2)) for a in (anchor, ascent, fold)]
    close(norms[0], 1); close(norms[1], 1); close(norms[2], .5)
    assert np.allclose(anchor @ anchor, anchor)
    assert np.allclose(ascent.T @ ascent, np.eye(2))
    commutators = [float(np.linalg.norm(a @ b - b @ a, 2))
                   for a, b in ((anchor, ascent), (ascent, fold), (fold, anchor))]
    assert all(x > 0 for x in commutators)
    lhs, rhs = alpha + beta, 1 - gamma * norms[2]
    assert lhs <= rhs
    generator = alpha * anchor + beta * ascent + gamma * fold
    eigenvalues = np.linalg.eigvals(generator)
    assert all(v.real > 0 for v in eigenvalues)
    return dict(anchor=anchor.tolist(), ascent=ascent.tolist(), fold=fold.tolist(),
                operator_norms=norms, commutator_norms=commutators,
                condition_lhs=lhs, condition_rhs=rhs, generator=generator.tolist(),
                eigenvalues=[{"real": float(v.real), "imag": float(v.imag)} for v in eigenvalues],
                scope="Satisfies the displayed linear-operator norm assumptions; it does not instantiate the undefined low-entropy projection.")


@probe("MP03", "DIRECT_COUNTEREXAMPLE", "Actual TRIAD tracker stops at a minimum and admits distinct fixed points",
       ["12_IMPLEMENTATIONS/core/triad_tracker.py:11", "12_IMPLEMENTATIONS/core/triad_tracker.py:130"])
def tracker_step_size(repo):
    tracker = module(repo, "triad_tracker.py")["TriadTracker"]
    coherence = lambda x: .8 + .1 * np.sin(x)
    gradient = lambda x: .1 * np.cos(x)
    alpha, lipschitz = 1., .1
    assert alpha < 1 / (2 * lipschitz)
    records = []
    for start in (-np.pi / 2, np.pi / 2, np.pi / 2 + 2 * np.pi):
        t = tracker(coherence, gradient, initial_state=float(start),
                    step_size=alpha, lipschitz_constant=lipschitz)
        s = t.single_step()
        assert bool(s.converged)
        close(s.state, start)
        records.append(dict(initial=float(start), final=float(s.state),
                            coherence=float(s.coherence), converged=bool(s.converged)))
    close(records[0]["coherence"], .7)
    assert records[0]["coherence"] < records[1]["coherence"]
    assert records[1]["final"] != records[2]["final"]
    return dict(alpha=alpha, lipschitz_constant=lipschitz, records=records,
                coherence_second_derivative_at_minimum=.1,
                scope="Refutes the step-size-only guarantee; a conditional theorem with strong concavity is not refuted.")


@probe("MP04", "DIRECT_COUNTEREXAMPLE", "The Shannon low-entropy sublevel is not convex",
       ["11_MATHEMATICAL_FOUNDATIONS/MATHEMATICS_FOUNDATIONS.md:318"])
def low_entropy_nonconvex(repo):
    left, right = np.array([1., 0.]), np.array([0., 1.])
    midpoint, epsilon = (left + right) / 2, .1
    values = [entropy(x, base=math.e) for x in (left, right, midpoint)]
    assert values[0] < epsilon and values[1] < epsilon and values[2] > epsilon
    return dict(left=left.tolist(), right=right.tolist(), midpoint=midpoint.tolist(),
                entropy_nats=values, epsilon=epsilon)


@probe("MP05", "DIRECT_COUNTEREXAMPLE", "The actual normalized ascent does not preserve inner products",
       ["12_IMPLEMENTATIONS/core/lamague_reference.py:110",
        "11_MATHEMATICAL_FOUNDATIONS/MATHEMATICS_FOUNDATIONS.md:554"])
def ascent_not_unitary(repo):
    kernel = module(repo, "lamague_reference.py")["TRIADKernel"](
        np.array([1., 0.]), np.array([1., 1.]))
    a, b = np.array([1., 0.]), np.array([0., 1.])
    fa, fb = kernel.ascent_operator(a), kernel.ascent_operator(b)
    before, after = float(a @ b), float(fa @ fb)
    close(before, 0)
    close(np.linalg.norm(fa), 1); close(np.linalg.norm(fb), 1)
    assert abs(after - before) > .1
    return dict(before_inner_product=before, after_inner_product=after,
                image_a=fa.tolist(), image_b=fb.tolist(),
                note="Unit output norms are a positive control; they do not imply unitarity.")


@probe("MP06", "DIRECT_COUNTEREXAMPLE", "The sparse and uniform forcing spectral norms are miscomputed",
       ["TRUTH_PRESSURE/PI_THRESHOLD_DERIVATION.md:76",
        "TRUTH_PRESSURE/PI_THRESHOLD_DERIVATION.md:92"])
def rmt_norm(repo):
    n, rank = 16, 4
    v = np.eye(n)[:, :rank]
    sparse = v @ v.T / n
    uniform = np.outer(np.ones(n), np.ones(n)) / n
    actual = float(np.linalg.norm(sparse, 2))
    claimed = 1 / math.sqrt(n)
    close(np.linalg.norm(v.T @ v - np.eye(rank)), 0)
    close(actual, 1 / n)
    assert not math.isclose(actual, claimed)
    close(np.linalg.norm(uniform, 2), 1)
    baseline = -np.eye(n)
    below = float(np.linalg.eigvalsh(baseline + 4 * sparse)[-1])
    at = float(np.linalg.eigvalsh(baseline + 16 * sparse)[-1])
    assert below < 0
    close(at, 0)
    return dict(n=n, rank=int(np.linalg.matrix_rank(sparse)), sparse_actual_norm=actual,
                sparse_claimed_norm=claimed, uniform_actual_norm=float(np.linalg.norm(uniform, 2)),
                illustrative_stable_baseline="J=-I; illustration only, not a proposed scientific replacement",
                max_eigenvalue_at_pi_4=below, max_eigenvalue_at_pi_16=at,
                note="No Wigner ensemble experiment or empirical scaling fit was run.")


@probe("MP07", "DIRECT_COUNTEREXAMPLE", "The stated below-threshold reference is not an equilibrium",
       ["TRUTH_PRESSURE/MASTER_EQUATION.md:152", "TRUTH_PRESSURE/MASTER_EQUATION.md:175",
        "TRUTH_PRESSURE/PI_DERIVATION.md:214"])
def master_equilibrium(repo):
    k1, k2, k3, k4 = .5, .3, .2, .1
    pi, threshold, invariant, violations, resource_ratio = .7, 1.2, .7, 0, 1.
    forcing = k1 * (pi - threshold) - k3 * violations + k4 * resource_ratio
    dynamics = lambda x: forcing - k2 * (x - invariant)
    at_reference = dynamics(invariant)
    equilibrium = invariant + forcing / k2
    x = .69
    vdot = (x - invariant) * dynamics(x)
    assert pi < threshold and violations == 0
    assert k2 > k1 * (threshold - pi)
    assert at_reference != 0 and vdot > 0
    close(equilibrium, .2); close(dynamics(equilibrium), 0)
    close(vdot, .00147)
    return dict(k1=k1, k2=k2, k3=k3, k4=k4, pi=pi, threshold=threshold,
                invariant_reference=invariant, resource_ratio=resource_ratio,
                derivative_at_reference=at_reference, actual_equilibrium=equilibrium,
                point=x, lyapunov_derivative=vdot, linearized_eigenvalue=-k2,
                scope="Exact scalar equation as printed, with constant inputs; no alternate scientific model is chosen.")


@probe("MP08", "DIRECT_COUNTEREXAMPLE", "A perfect adherence score leaves ethical predicates unconstrained",
       ["28_DEFENSE/CLAIMS.json:82", "30_MAPS/FORMAL_SPINE.md:360",
        "12_IMPLEMENTATIONS/core/microorcim_tracker.py:74"])
def sovereignty_without_compliance(repo):
    m = module(repo, "microorcim_tracker.py")
    drift = m["compute_drift"](1., 1.)
    score = m["compute_sovereignty"](drift, 1.)
    close(drift, 0); close(score, 1)
    # A countermodel to the claimed logical implication. The functions receive
    # no invariant predicate, so this unconstrained proposition can be false.
    separate_invariant_preserved = False
    assert score >= .8 and not separate_invariant_preserved
    return dict(intended_numeric_value=1., actual_numeric_value=1., drift=drift, score=score,
                separate_invariant_preserved=separate_invariant_preserved,
                scope="Logical countermodel to score-only implication, not an empirical ethical assessment. The score function has no invariant input.")


@probe("MP09", "DIRECT_COUNTEREXAMPLE", "Actual CASCADE demotes an old foundation while retaining its record",
       ["30_MAPS/FORMAL_SPINE.md:205", "12_IMPLEMENTATIONS/core/cascade_engine.py:283"])
def foundation_membership(repo):
    m = module(repo, "cascade_engine.py")
    engine, block = m["CascadeEngine"](), m["KnowledgeBlock"]
    old = block("old", "Old claim", "demo", "old", .8, 1., .5)
    engine.add_block(old)
    before = dict(layer=old.layer, truth_pressure=old.truth_pressure, content=old.content)
    assert old.layer == "FOUNDATION"
    event = engine.add_block(block("new", "Conflicting new claim", "demo", "new", 1., 1.5, .5))
    assert event is not None and old.layer == "THEORY"
    close(old.truth_pressure, 1.36)
    assert "old" in engine.blocks and old.content == before["content"]
    return dict(before=before, after=dict(layer=old.layer, truth_pressure=old.truth_pressure,
                                        regime=old.regime, content=old.content),
                cascade_fired=True, old_record_retained=True,
                scope="Implementation intentionally demotes; this refutes the advertised membership invariant, not record preservation.")


@probe("MP10", "DIRECT_COUNTEREXAMPLE", "Adding a categorical outcome need not increase Shannon entropy",
       ["11_MATHEMATICAL_FOUNDATIONS/CASCADE_FORMAL_PROOFS.md:205"])
def categorical_entropy(repo):
    old, new = [.5, .5], [.01, .01, .98]
    h_old, h_new = entropy(old), entropy(new)
    assert new[0] > 0 and new[1] > 0 and h_new < h_old
    close(h_old, 1); close(h_new, .16144054254182066)
    return dict(old_probabilities=old, new_probabilities=new, old_entropy_bits=h_old,
                new_entropy_bits=h_new,
                scope="Categorical extension with renormalization preserves records, not their old probability masses. Joint-variable chain rule is a different construction.")


@probe("MP11", "DIRECT_COUNTEREXAMPLE", "The stated reliability-entropy TES construction can cross below its floor",
       ["11_MATHEMATICAL_FOUNDATIONS/CASCADE_FORMAL_PROOFS.md:370"])
def tes_floor(repo):
    old_tes = 1 - entropy([1., 0.]) / 1
    new_reliability_entropy = entropy([.7, .3])
    new_tes = 1 - new_reliability_entropy / 2
    close(old_tes, 1)
    assert old_tes >= .7 and new_tes < .7
    return dict(old_reliability=[1.], added_reliability=.7, old_hmax_bits=1,
                new_hmax_bits=2, added_entropy_bits=new_reliability_entropy,
                old_tes=old_tes, new_tes=new_tes,
                scope="The proof's additive independent-Bernoulli entropy model, not the differently defined heuristic TES checker.")


@probe("MP12", "DIRECT_COUNTEREXAMPLE", "Positive created value does not imply value exceeds consumed resources",
       ["11_MATHEMATICAL_FOUNDATIONS/CASCADE_FORMAL_PROOFS.md:403"])
def vtr_cost(repo):
    old_value, old_cost, added_value, added_cost = 1., 1., .1, 1.
    old_vtr = old_value / old_cost
    new_vtr = (old_value + added_value) / (old_cost + added_cost)
    assert added_value > 0 and added_cost > 0 and old_vtr >= 1 and new_vtr < 1
    return dict(old_value=old_value, old_cost=old_cost, added_value=added_value,
                added_cost=added_cost, old_vtr=old_vtr, new_vtr=new_vtr,
                scope="Countermodel to the displayed inequality inference, not a measured economic valuation.")


@probe("MP13", "DIRECT_COUNTEREXAMPLE", "Actual Solve then Coagula reduces coherence from one",
       ["12_IMPLEMENTATIONS/core/chrysopoeia_engine.py:362",
        "12_IMPLEMENTATIONS/core/chrysopoeia_engine.py:383", "30_MAPS/FORMAL_SPINE.md:492"])
def solve_coagula(repo):
    m = module(repo, "chrysopoeia_engine.py")
    state = m["TransformationState"](vector=np.ones(3), coherence=1., entropy=0.)
    np.random.seed(123)
    solved = m["solve"](state)
    result = m["coagula"](solved, m["ConstraintSet"]())
    close(solved.coherence, .9); close(result.coherence, .915)
    assert result.coherence < state.coherence
    return dict(initial_coherence=state.coherence, after_solve=solved.coherence,
                after_coagula=result.coherence, noise_seed=123,
                note="The scalar coherence counterexample is independent of the noise realization.")


@probe("MP14", "PROOF_GAP", "Actual Xi draws fresh noise and reports zero entropy away from its coagulation target",
       ["12_IMPLEMENTATIONS/core/chrysopoeia_engine.py:330",
        "12_IMPLEMENTATIONS/core/chrysopoeia_engine.py:407"])
def stochastic_xi(repo):
    m = module(repo, "chrysopoeia_engine.py")
    state = m["TransformationState"](vector=np.ones(3), coherence=1., entropy=0.)
    constraints = m["ConstraintSet"]()
    a = m["Xi"](state, constraints, rng=np.random.default_rng(2))
    b = m["Xi"](state, constraints, rng=np.random.default_rng(3))
    difference = float(np.linalg.norm(a.vector - b.vector))
    distance = float(np.linalg.norm(a.vector - np.ones(3)))
    assert difference > .01 and distance > .01
    close(a.entropy, 0); close(b.entropy, 0)
    return dict(input_vector=state.vector.tolist(), seed_2_output=a.vector.tolist(),
                seed_3_output=b.vector.tolist(), output_distance=difference,
                seed_2_distance_from_ones=distance, reported_entropy=[a.entropy, b.entropy],
                scope="Observed stochasticity and metadata distinction. Does not refute Banach's conditional theorem or all possible stochastic convergence models.")


@probe("MP15", "DIRECT_COUNTEREXAMPLE", "Simple nonunit ratios can close a cycle exactly",
       ["10_HARMONIA_L6/essentials.md:43"])
def harmonic_cycle(repo):
    literal_ratios = [Fraction(3, 2), Fraction(2, 3)]
    literal_product = math.prod(literal_ratios)
    ratios = [Fraction(k + 1, k) for k in range(1, 8)]
    product = math.prod(ratios)
    assert literal_product == 1 and all(r != 1 for r in literal_ratios)
    assert len(set(ratios)) == 7 and all(1 < r <= 2 for r in ratios)
    assert product == 8 and product / (2 ** 3) == 1
    narrow_comma = Fraction(3, 2) ** 12 / (2 ** 7)
    assert narrow_comma != 1
    return dict(literal_exact_closure=[str(r) for r in literal_ratios],
                literal_product=str(literal_product), seven_distinct_ratios=[str(r) for r in ratios],
                product=str(product), octave_normalized_product=str(product / 8),
                positive_control_twelve_fifths_comma=str(narrow_comma),
                scope="Refutes the universal extension; preserves the narrow Pythagorean comma result.")


def continued_fraction(ratio):
    result = []
    while ratio.denominator != 1:
        whole = ratio.numerator // ratio.denominator
        result.append(whole)
        ratio = 1 / (ratio - whole)
    result.append(ratio.numerator)
    return result


def written_consonance(ratio):
    terms = continued_fraction(ratio)
    score = 1 / (1 + sum(Fraction(a, 2 ** k) for k, a in enumerate(terms)))
    return terms, score


@probe("MP16", "DIRECT_COUNTEREXAMPLE", "The consonance formula, table, and acknowledged implementation proxy disagree",
       ["10_HARMONIA_L6/essentials.md:17", "10_HARMONIA_L6/essentials.md:29",
        "12_IMPLEMENTATIONS/core/harmonia_calculator.py:107"])
def harmonic_measure(repo):
    cases = []
    for ratio, table_value in [(Fraction(1), 1.), (Fraction(2), 1.), (Fraction(3, 2), .571)]:
        terms, value = written_consonance(ratio)
        assert not math.isclose(float(value), table_value, abs_tol=.001)
        cases.append(dict(ratio=str(ratio), continued_fraction=terms,
                          written_formula_value=str(value), reported_table_value=table_value))
    calc = module(repo, "harmonia_calculator.py")["HarmoniaCalculator"]()
    unison = calc.calculate_consonance(440., 440.)
    tritone = calc.calculate_consonance(440., 440. * 45 / 32)
    close(unison["consonance"], 1)
    assert tritone["consonance"] > .99 and tritone["consonance_quality"].startswith("PERFECT")
    return dict(written_formula_convention="sum starts at k=0, as usual for [a0;a1,...]",
                formula_table_cases=cases, tritone_ratio="45/32",
                implementation_consonance=float(tritone["consonance"]),
                implementation_quality=tritone["consonance_quality"],
                source_table_consonance=.024,
                scope="Internal consistency and proxy disagreement. No listener study or external consonance measure was tested.")


@probe("MP17", "DIRECT_COUNTEREXAMPLE", "Work does not universally imply entropy change minus work over temperature",
       ["30_MAPS/FORMAL_SPINE.md:388", "30_MAPS/FORMAL_SPINE.md:396",
        "06_EARNED_LIGHT_L0/essentials.md:74"])
def thermodynamic_relation(repo):
    # Reversible adiabatic compression of one mole of an ideal monatomic gas.
    # Within this explicit ideal model: Q=0, DeltaS=0, W_on=DeltaU>0.
    gas_constant = 8.31446261815324
    cv, gamma = 1.5 * gas_constant, 5 / 3
    temperature_1, volume_1, volume_2 = 300., 1., .5
    temperature_2 = temperature_1 * (volume_1 / volume_2) ** (gamma - 1)
    delta_s = cv * math.log(temperature_2 / temperature_1) + gas_constant * math.log(volume_2 / volume_1)
    work_on = cv * (temperature_2 - temperature_1)
    purported = -work_on / temperature_1
    close(delta_s, 0)
    assert work_on > 0 and purported < 0 and abs(delta_s - purported) > 1
    return dict(ideal_model="reversible adiabatic compression; one mole monatomic ideal gas",
                temperature_1_K=temperature_1, temperature_2_K=temperature_2,
                volume_ratio=volume_2 / volume_1, work_on_J=work_on,
                actual_delta_entropy_J_per_K=delta_s, minus_work_over_initial_temperature=purported,
                scope="Counterexample to the unqualified thermodynamic-law claim. A process-restricted erasure/free-energy relation requires separate assumptions; consciousness is not simulated.")


@probe("MP18", "DIRECT_COUNTEREXAMPLE", "Actual low-pressure revision need not give local consistency",
       ["11_MATHEMATICAL_FOUNDATIONS/AGM_POSTULATE_VERIFICATION.md:165"])
def agm_consistency(repo):
    m = module(repo, "cascade_engine.py")
    engine, block = m["CascadeEngine"](), m["KnowledgeBlock"]
    engine.add_block(block("old", "Old", "domain", "old", 1., 1.5, .5))
    event = engine.add_block(block("new", "New", "domain", "new", .8, 1., .5))
    conflicts = engine.active_contradictions()
    assert event is None and ("old", "new") in conflicts
    close(engine.coherence(), 0)
    return dict(cascade_fired=False, active_contradictions=conflicts,
                coherence=engine.coherence(),
                scope="Counters the add_block/revision local-consistency assertion; does not say that a fired cascade leaves this particular conflict unresolved.")


DOCUMENTARY_GAPS = [
    {
        "id": "DG01", "classification": "PROOF_GAP",
        "evidence": ["11_MATHEMATICAL_FOUNDATIONS/lyapunov_verification.py:248",
                     "11_MATHEMATICAL_FOUNDATIONS/lyapunov_verification.py:329",
                     "11_MATHEMATICAL_FOUNDATIONS/lyapunov_verification.py:455"],
        "finding": "Assigned Hessian eigenvalues and unconditional NUMERICAL records are counted as passing. No new execution of this verification suite was performed.",
    },
    {
        "id": "DG02", "classification": "PROOF_GAP",
        "evidence": ["30_MAPS/FORMAL_SPINE.md:273", "30_MAPS/FORMAL_SPINE.md:154"],
        "finding": "Inspectability does not entail a numeric contradiction-count/coherence floor; the cross-framework bridge needs an independent premise or enforcement.",
    },
    {
        "id": "DG03", "classification": "PROOF_GAP",
        "evidence": ["11_MATHEMATICAL_FOUNDATIONS/THE_INCOMPLETENESS_PROOF.md:123"],
        "finding": "The displayed all-model semantic consequence without provability is incompatible with ordinary complete first-order semantics. The needed arithmetic/effectivity assumptions are absent. This was read, not tested by a theorem prover.",
    },
    {
        "id": "DG04", "classification": "PROOF_GAP",
        "evidence": ["07_ANAMNESIS_L0/ANAMNESIS_FROM_ARCHIVE.md:265",
                     "07_ANAMNESIS_L0/essentials.md:83"],
        "finding": "A common attractor set does not force the same limit element. Equal convergence rates are assigned to competing explanations in the proposed discriminator.",
    },
    {
        "id": "DG05", "classification": "PROOF_GAP",
        "evidence": ["TRUTH_PRESSURE/PI_DERIVATION.md:211",
                     "TRUTH_PRESSURE/DIMENSIONAL_ANALYSIS.md:101",
                     "28_DEFENSE/NOVEL_CONTRIBUTIONS.md:26"],
        "finding": "Pi is assumed before symbolic manipulation; dimensional cancellation does not prove construct validity/universality. Some proposed normalizations violate their claimed range. No external novelty literature search was performed.",
    },
    {
        "id": "DG06", "classification": "PROOF_GAP",
        "evidence": ["30_MAPS/FORMAL_SPINE.md:191", "12_IMPLEMENTATIONS/core/cascade_engine.py:61"],
        "finding": "The formal spine uses global coherence as Pi denominator; the implementation uses individual block uncertainty. The review does not choose a replacement definition.",
    },
]


def source_receipts(repo):
    receipts = []
    for relative in PINNED_SOURCES:
        current = (repo / relative).read_bytes()
        baseline = git(repo, "show", f"{REVIEW_COMMIT}:{relative}")
        receipts.append(dict(path=relative, sha256=sha256(current), bytes=len(current),
                             reviewed_commit_sha256=sha256(baseline),
                             matches_reviewed_commit=current == baseline))
    return receipts


def evidence_audit(repo):
    raw = (repo / "28_DEFENSE/CLAIMS.json").read_bytes()
    document = json.loads(raw)
    claims = document["claims"]
    indexed = {}
    for entry in git(repo, "ls-files", "--stage", "-z").decode().split("\0"):
        if entry:
            metadata, relative = entry.split("\t", 1)
            mode, object_id, stage = metadata.split()
            if stage == "0":
                indexed[relative] = dict(mode=mode, git_object=object_id)
    claim_details, references = [], []
    for claim in claims:
        parts = [part.strip() for part in claim["evidence_path"].split(";")]
        own_refs = []
        for literal in parts:
            path = repo / literal
            exists = path.exists()
            tracked_descendants = sum(p.startswith(literal.rstrip("/") + "/") for p in indexed) if path.is_dir() else 0
            record = {
                "claim_id": claim["claim_id"],
                "author_status": claim["status"],
                "author_status_normalized": claim["status_normalized"],
                "literal_reference": literal,
                "exists_locally": exists,
                "kind": "file" if path.is_file() else "directory" if path.is_dir() else "missing",
                "is_symlink": path.is_symlink(),
                "git_tracked_file": literal in indexed,
                "git_mode": indexed.get(literal, {}).get("mode"),
                "tracked_descendant_count": tracked_descendants,
                "classification": "EVIDENCE_PATH_EXISTS" if exists else "MISSING_EVIDENCE",
            }
            if path.is_file():
                record["sha256"] = sha256(path.read_bytes())
            own_refs.append(record)
            references.append(record)
        claim_details.append({
            "claim_id": claim["claim_id"], "framework": claim["framework"],
            "statement": claim["statement"],
            "author_status": claim["status"], "author_status_normalized": claim["status_normalized"],
            "original_evidence_path": claim["evidence_path"], "references": own_refs,
            "all_references_missing": all(not r["exists_locally"] for r in own_refs),
            "some_references_missing": any(not r["exists_locally"] for r in own_refs),
        })
    missing = [r for r in references if not r["exists_locally"]]
    all_missing = [c for c in claim_details if c["all_references_missing"]]
    status_counts = dict(Counter(c["status_normalized"] for c in claims))
    assert len(claims) == document["total_claims"] == 71
    assert len(references) == 107 and len(missing) == 37
    assert len(all_missing) == 24
    assert sum(c["author_status_normalized"] == "ACTIVE" for c in all_missing) == 18
    assert status_counts == {"ACTIVE": 52, "SCAFFOLD": 12, "CONJECTURE": 4, "RETRACTED": 3}
    assert (repo / "28_DEFENSE/CLAIMS.json").is_file()
    assert not (repo / "__review_known_missing_evidence_control_2026_10_20__.md").exists()
    return {
        "classification": "MISSING_EVIDENCE",
        "method": "Split the literal evidence_path at semicolons; inspect local existence and tracked ownership. No replacement paths or semantic evidence waivers.",
        "warning": "A missing pointer does not itself refute a theorem. An existing pointer does not establish its claim.",
        "register_sha256": sha256(raw),
        "summary": {
            "claims": len(claims), "author_status_counts": status_counts,
            "evidence_references": len(references),
            "existing_references": len(references) - len(missing),
            "missing_references": len(missing),
            "claims_all_references_missing": len(all_missing),
            "active_claims_all_references_missing": sum(c["author_status_normalized"] == "ACTIVE" for c in all_missing),
        },
        "resolver_controls": {"existing_register_detected": True, "known_missing_sentinel_detected": True},
        "missing_references": missing,
        "claims_all_references_missing": [c["claim_id"] for c in all_missing],
        "claims": claim_details,
    }


def main():
    if not __debug__:
        raise RuntimeError("Do not use -O: the reproduction requires assertions.")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=DEFAULT_REPO)
    parser.add_argument("--output-dir", type=Path,
                        default=Path(tempfile.gettempdir()) / "lycheetah-math-review-2026-10-20")
    args = parser.parse_args()
    repo = args.repo.resolve()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).isoformat()
    observed_commit = git(repo, "rev-parse", "HEAD").decode().strip()
    initial_status = git(repo, "status", "--porcelain=v1", "--untracked-files=all").decode()
    pins = source_receipts(repo)
    assert observed_commit == REVIEW_COMMIT, "The checkout no longer has the reviewed commit."
    assert all(r["matches_reviewed_commit"] for r in pins), "A cited source differs from reviewed commit."
    assert len(PROBES) == EXPECTED_PROBES
    controls = self_controls()
    results = []
    random_state = np.random.get_state()
    try:
        for identifier, classification, title, evidence, fn in PROBES:
            try:
                details = fn(repo)
                result = "REPRODUCED"
            except Exception as error:
                result, details = "FAILED", {"error_type": type(error).__name__, "error": str(error)}
            results.append(dict(id=identifier, classification=classification, title=title,
                                evidence=evidence, result=result, details=details))
    finally:
        np.random.set_state(random_state)
    audit = evidence_audit(repo)
    final_pins = source_receipts(repo)
    assert [(r["path"], r["sha256"]) for r in pins] == [(r["path"], r["sha256"]) for r in final_pins]
    final_status = git(repo, "status", "--porcelain=v1", "--untracked-files=all").decode()
    reproduced = sum(r["result"] == "REPRODUCED" for r in results)
    common = {
        "schema_version": 1, "generated_at_utc": timestamp,
        "reviewed_commit": REVIEW_COMMIT, "observed_commit": observed_commit,
        "repository": ".", "reviewer": "Caelorynth/Codex AI technical review; separate mathematical reviewer and primary reproduction",
        "author_attribution": "Mackenzie Conor James Clark; Lycheetah Framework",
        "not_independent_scientific_peer_review": True,
    }
    audit.update(common)
    audit_bytes = (json.dumps(audit, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode()
    (output_dir / "claim-evidence-audit.json").write_bytes(audit_bytes)
    payload = {
        **common,
        "meaning_of_success": "All listed reviewer observations reproduced under their stated scope. This is not a pass for the author claims.",
        "invocation": "python3 -B 28_DEFENSE/review_2026_10_20/math_probes.py --repo <baseline-checkout> --output-dir <evidence-directory>",
        "script_sha256": sha256(Path(__file__).read_bytes()),
        "numpy_version": np.__version__,
        "summary": {
            "expected_probes": EXPECTED_PROBES, "executed_probes": len(results),
            "reproduced": reproduced, "failed": len(results) - reproduced,
            "classifications": dict(Counter(r["classification"] for r in results)),
            "harness_controls": len(controls), "pinned_sources": len(pins),
            "all_sources_match_reviewed_commit": all(r["matches_reviewed_commit"] for r in pins),
            "pinned_source_bytes_unchanged_during_run": pins == final_pins,
        },
        "harness_controls": controls, "probes": results,
        "documentary_gaps_not_automated_proofs": DOCUMENTARY_GAPS,
        "source_receipts": pins,
        "claim_evidence_audit": {"filename": "claim-evidence-audit.json", "sha256": sha256(audit_bytes),
                                 "summary": audit["summary"]},
        "repository_status_before_sha256": sha256(initial_status.encode()),
        "repository_status_after_sha256": sha256(final_status.encode()),
        "repository_status_unchanged": initial_status == final_status,
        "writes": ["math-probes.json", "claim-evidence-audit.json"],
        "not_run": ["full or focused repository test suites", "lyapunov_verification.py main",
                    "provider/model APIs", "servers", "external literature search"],
    }
    (output_dir / "math-probes.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"reproduced": reproduced, "executed": len(results),
                      "controls": len(controls), "pinned_sources": len(pins),
                      "claim_evidence": audit["summary"], "repository_status_unchanged": initial_status == final_status}))
    return 0 if reproduced == EXPECTED_PROBES else 1


if __name__ == "__main__":
    raise SystemExit(main())
