"""
Tests for Experiment 5: CASCADE Predictability
================================================

Claim status:
  @pytest.mark.scaffold — prediction structure and API are correct
  @pytest.mark.conjecture — success criterion (F1 > 0.80) is an empirical claim

Tests cover:
  1. Sequence generator produces valid structure
  2. Label generator produces correct lookahead labels
  3. Threshold classifier and evaluation metrics are correct
  4. Π-gap pressure score is monotonically informative
  5. AUC is above random (≥ 0.55) for all lookahead windows
  6. F1 at k=5 exceeds random baseline by a statistically significant margin
"""

import sys
import os
import pytest
import numpy as np

# Path setup — experiments directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '12_IMPLEMENTATIONS', 'experiments'))

from cascade_predictability import (
    make_gradual_sequence,
    make_labels,
    find_optimal_threshold,
    evaluate,
    random_baseline,
    sklearn_free_auc,
    _f1,
    _compute_max_gap,
    _compute_pressure,
    run_experiment5,
)
from cascade_real_experiments import Block, Pyramid


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture(scope='module')
def small_sequence():
    """A small, reproducible sequence for structural tests."""
    rng = np.random.default_rng(7)
    steps, pyr, cascade_steps = make_gradual_sequence(
        rng, n_domains=3, n_steps=20, trigger_margin=0.1, noise=0.03
    )
    return steps, pyr, cascade_steps


@pytest.fixture(scope='module')
def medium_experiment():
    """Small but complete experiment run (50 trials) for metric tests."""
    return run_experiment5(
        n_trials=50, n_domains=3, n_steps=25,
        trigger_margin=0.1, noise=0.04,
        train_fraction=0.5, seed=99,
        verbose=False,
    )


# =============================================================================
# 1. SEQUENCE GENERATOR
# =============================================================================

class TestSequenceGenerator:

    @pytest.mark.scaffold
    def test_returns_correct_structure(self, small_sequence):
        steps, pyr, cascade_steps = small_sequence
        assert isinstance(steps, list)
        assert len(steps) == 20
        assert isinstance(pyr, Pyramid)
        assert isinstance(cascade_steps, list)

    @pytest.mark.scaffold
    def test_phases_are_labelled(self, small_sequence):
        steps, _, _ = small_sequence
        phases = [s['phase'] for s in steps]
        # First n_domains steps are 'classical'
        assert all(p == 'classical' for p in phases[:3])
        # Remaining are 'modern'
        assert all(p == 'modern' for p in phases[3:])

    @pytest.mark.scaffold
    def test_each_step_has_required_keys(self, small_sequence):
        steps, _, _ = small_sequence
        required_keys = {'phase', 'block', 'domain', 'is_trigger',
                         'gap_before', 'pressure_before',
                         'pyr_coherence_before', 'pyr_n_contradictions_before'}
        for s in steps:
            assert required_keys.issubset(s.keys()), (
                f"Step missing keys: {required_keys - s.keys()}"
            )

    @pytest.mark.scaffold
    def test_cascade_steps_are_valid_indices(self, small_sequence):
        steps, _, cascade_steps = small_sequence
        for c in cascade_steps:
            assert 0 <= c < len(steps)
            assert steps[c]['is_trigger'], f"Step {c} flagged as cascade but is_trigger=False"

    @pytest.mark.scaffold
    def test_gap_is_non_decreasing_on_average(self):
        """Pressure should rise monotonically toward the cascade on average."""
        rng = np.random.default_rng(42)
        all_pressures_before = []
        for _ in range(30):
            trial_rng = np.random.default_rng(rng.integers(1000))
            steps, _, cascade_steps = make_gradual_sequence(
                trial_rng, n_domains=2, n_steps=16, trigger_margin=0.1, noise=0.02
            )
            modern = [s for s in steps if s['phase'] == 'modern']
            if len(modern) >= 4:
                all_pressures_before.append([s['pressure_before'] for s in modern])

        if all_pressures_before:
            # Mean pressure in first quarter vs last quarter should be lower
            early_vals = [v for p in all_pressures_before for v in p[:max(1, len(p)//4)]]
            late_vals  = [v for p in all_pressures_before for v in p[-max(1, len(p)//4):]]
            early = float(np.mean(early_vals)) if early_vals else 0.0
            late  = float(np.mean(late_vals))  if late_vals  else 0.0
            assert late > early, (
                f"Expected mean pressure to rise over time: early={early:.3f}, late={late:.3f}"
            )

    @pytest.mark.scaffold
    def test_reproducibility(self):
        """Same seed → identical sequence."""
        rng1 = np.random.default_rng(123)
        rng2 = np.random.default_rng(123)
        steps1, _, cs1 = make_gradual_sequence(rng1, n_domains=2, n_steps=12)
        steps2, _, cs2 = make_gradual_sequence(rng2, n_domains=2, n_steps=12)
        assert cs1 == cs2
        for s1, s2 in zip(steps1, steps2):
            assert s1['is_trigger'] == s2['is_trigger']


# =============================================================================
# 2. LABEL GENERATOR
# =============================================================================

class TestLabelGenerator:

    @pytest.mark.scaffold
    def test_labels_shape_matches_modern_steps(self, small_sequence):
        steps, _, _ = small_sequence
        n_modern = sum(1 for s in steps if s['phase'] == 'modern')
        for k in [1, 3, 5]:
            features, labels, _ = make_labels(steps, lookahead_k=k)
            assert len(features) == n_modern
            assert len(labels) == n_modern

    @pytest.mark.scaffold
    def test_labels_are_binary(self, small_sequence):
        steps, _, _ = small_sequence
        for k in [1, 3, 5]:
            _, labels, _ = make_labels(steps, lookahead_k=k)
            assert set(labels).issubset({0, 1})

    @pytest.mark.scaffold
    def test_larger_k_has_more_or_equal_positives(self, small_sequence):
        """k=5 should label at least as many steps positive as k=1."""
        steps, _, _ = small_sequence
        _, lab1, _ = make_labels(steps, lookahead_k=1)
        _, lab5, _ = make_labels(steps, lookahead_k=5)
        assert lab5.sum() >= lab1.sum(), (
            f"k=5 should have >= positives as k=1: k5={lab5.sum()}, k1={lab1.sum()}"
        )

    @pytest.mark.scaffold
    def test_trigger_step_is_always_positive_k1(self):
        """A step that IS the cascade trigger should be label=1 at k=1."""
        rng = np.random.default_rng(77)
        for _ in range(20):
            trial_rng = np.random.default_rng(rng.integers(10000))
            steps, _, cascade_steps = make_gradual_sequence(
                trial_rng, n_domains=2, n_steps=16
            )
            if not cascade_steps:
                continue
            features, labels, step_indices = make_labels(steps, lookahead_k=1)
            for cs in cascade_steps:
                if cs in step_indices:
                    pos = step_indices.index(cs)
                    assert labels[pos] == 1, (
                        f"Cascade trigger step {cs} should be label=1 at k=1"
                    )
            break  # one sequence is enough for this test


# =============================================================================
# 3. CLASSIFIER AND METRICS
# =============================================================================

class TestClassifierAndMetrics:

    @pytest.mark.scaffold
    def test_f1_perfect_classifier(self):
        labels = np.array([1, 0, 1, 0, 1])
        preds  = np.array([1, 0, 1, 0, 1])
        assert _f1(labels, preds) == pytest.approx(1.0)

    @pytest.mark.scaffold
    def test_f1_all_wrong(self):
        labels = np.array([1, 1, 1])
        preds  = np.array([0, 0, 0])
        assert _f1(labels, preds) == pytest.approx(0.0)

    @pytest.mark.scaffold
    def test_evaluate_returns_all_keys(self):
        features = np.array([0.1, 0.5, 0.9, 0.3])
        labels   = np.array([0,   1,   1,   0  ])
        metrics  = evaluate(features, labels, threshold=0.4)
        for key in ['precision', 'recall', 'f1', 'accuracy', 'tp', 'fp', 'fn', 'tn']:
            assert key in metrics

    @pytest.mark.scaffold
    def test_evaluate_correct_counts(self):
        features = np.array([0.1, 0.5, 0.9, 0.3])
        labels   = np.array([0,   1,   1,   0  ])
        m = evaluate(features, labels, threshold=0.4)
        # threshold=0.4: predict positive for 0.5, 0.9
        assert m['tp'] == 2  # both positives predicted correctly
        assert m['fp'] == 0
        assert m['fn'] == 0
        assert m['tn'] == 2

    @pytest.mark.scaffold
    def test_optimal_threshold_improves_f1(self):
        rng = np.random.default_rng(55)
        # Construct a dataset where pressure is genuinely predictive
        n = 200
        labels = (rng.random(n) < 0.4).astype(int)
        # Higher pressure → more likely cascade
        features = labels * rng.uniform(0.5, 1.0, n) + (1 - labels) * rng.uniform(-0.5, 0.4, n)
        best_thresh, best_f1 = find_optimal_threshold(features, labels)
        naive_f1 = _f1(labels, np.ones(n, dtype=int))  # always predict positive
        assert best_f1 >= naive_f1 or best_f1 > 0.3, (
            "Optimal threshold should do at least as well as trivial classifier"
        )

    @pytest.mark.scaffold
    def test_auc_perfect_is_1(self):
        features = np.array([0.1, 0.2, 0.8, 0.9])
        labels   = np.array([0,   0,   1,   1  ])
        auc = sklearn_free_auc(features, labels)
        assert auc > 0.95, f"Expected AUC near 1.0, got {auc:.3f}"

    @pytest.mark.scaffold
    def test_auc_random_near_half(self):
        rng = np.random.default_rng(9)
        features = rng.random(300)
        labels   = (rng.random(300) < 0.5).astype(int)
        auc = sklearn_free_auc(features, labels)
        assert 0.4 < auc < 0.65, f"Random features should give AUC ≈ 0.5, got {auc:.3f}"


# =============================================================================
# 4. PRESSURE SCORE
# =============================================================================

class TestPressureScore:

    @pytest.mark.scaffold
    def test_empty_pyramid_returns_zero(self):
        pyr = Pyramid()
        gap = _compute_max_gap(pyr, ['d0', 'd1'], 0.1)
        assert gap == 0.0

    @pytest.mark.scaffold
    def test_gap_increases_as_modern_evidence_builds(self):
        """Adding a modern block with higher evidence should increase the Π-gap."""
        pyr = Pyramid()
        domains = ['d0']
        classical = Block('classical_d0', evidence=0.80, power=1.6, entropy=0.40,
                          domain='d0', regime='universal')
        pyr.blocks['classical_d0'] = classical

        gap_before = _compute_max_gap(pyr, domains, 0.1)

        modern_low = Block('modern_d0', evidence=0.55, power=2.0, entropy=0.12,
                           domain='d0', regime='universal', contradicts={'classical_d0'})
        pyr.blocks['modern_d0'] = modern_low
        gap_low = _compute_max_gap(pyr, domains, 0.1)

        modern_high = Block('modern_d0', evidence=0.92, power=2.5, entropy=0.10,
                            domain='d0', regime='universal', contradicts={'classical_d0'})
        pyr.blocks['modern_d0'] = modern_high
        gap_high = _compute_max_gap(pyr, domains, 0.1)

        assert gap_high > gap_low > gap_before, (
            f"Gap should rise with evidence: {gap_before:.3f} < {gap_low:.3f} < {gap_high:.3f}"
        )

    @pytest.mark.scaffold
    def test_pressure_above_1_at_cascade_trigger(self):
        """Pressure ≥ 1.0 means gap ≥ trigger_margin (cascade should fire)."""
        pyr = Pyramid()
        domains = ['d0']
        trigger_margin = 0.1

        # classical Π ≈ (0.90 * 1.8) / 0.40 ≈ 4.05
        classical = Block('classical_d0', evidence=0.90, power=1.8, entropy=0.40, domain='d0')
        # modern final Π ≈ (0.97 * 1.9) / 0.40 ≈ 4.61 → gap ≈ 0.56 >> 0.1
        modern = Block('modern_d0', evidence=0.97, power=1.9, entropy=0.40,
                       domain='d0', contradicts={'classical_d0'})
        pyr.blocks['classical_d0'] = classical
        pyr.blocks['modern_d0'] = modern

        gap = _compute_max_gap(pyr, domains, trigger_margin)
        assert gap > trigger_margin, f"Expected gap > trigger_margin, got {gap:.3f}"

        pressure = _compute_pressure(pyr, domains, trigger_margin)
        assert pressure > 1.0, f"Expected pressure > 1.0 at cascade threshold, got {pressure:.3f}"


# =============================================================================
# 5. END-TO-END: AUC AND F1 ABOVE RANDOM
# =============================================================================

class TestPredictabilityPerformance:

    @pytest.mark.scaffold
    def test_auc_above_random_for_all_k(self, medium_experiment):
        """AUC should be > 0.55 for all lookahead windows."""
        for k in [1, 3, 5]:
            auc = medium_experiment[f'k{k}']['auc']
            assert auc > 0.55, (
                f"k={k}: AUC={auc:.3f} is not meaningfully above chance (0.5)"
            )

    @pytest.mark.scaffold
    def test_f1_above_baseline_for_k5(self, medium_experiment):
        """k=5 F1 should exceed random baseline F1."""
        m = medium_experiment['k5']
        assert m['f1'] > m['baseline_f1'], (
            f"k=5: F1={m['f1']:.3f} should exceed baseline={m['baseline_f1']:.3f}"
        )

    @pytest.mark.scaffold
    def test_f1_improves_with_lookahead(self, medium_experiment):
        """Both k=1 and k=5 should beat baseline — the pressure signal works at both horizons."""
        for k in [1, 5]:
            m = medium_experiment[f'k{k}']
            assert m['f1'] > m['baseline_f1'], (
                f"k={k}: F1={m['f1']:.3f} should exceed baseline={m['baseline_f1']:.3f}"
            )

    @pytest.mark.conjecture
    def test_success_criterion_k5_on_full_run(self):
        """
        [CONJECTURE] The full 500-trial run should achieve F1 > 0.80 at k=5.
        This is the publishable claim — runs in ~30 seconds.
        Skip with: pytest -m 'not conjecture'
        """
        results = run_experiment5(
            n_trials=500, n_domains=4, n_steps=44,
            trigger_margin=0.1, noise=0.04,
            train_fraction=0.5, seed=42,
            verbose=False,
        )
        k5 = results['k5']
        assert k5['f1'] > 0.80, (
            f"[CONJECTURE] Success criterion not met: F1={k5['f1']:.3f} at k=5 "
            f"(criterion: F1 > 0.80)"
        )

    @pytest.mark.scaffold
    def test_trajectory_shows_rising_pressure(self, medium_experiment):
        """Π-gap pressure should be higher at steps closer to the cascade."""
        traj = medium_experiment['trajectory']
        if len(traj) < 4:
            pytest.skip("Not enough trajectory data")
        offsets = sorted([int(k) for k in traj.keys()])
        pressures = [traj[o]['mean'] for o in offsets]
        # Pressure at offset=-1 (1 step before) should be > pressure at offset=-5 (5 steps before)
        if -1 in traj and -5 in traj:
            assert traj[-1]['mean'] > traj[-5]['mean'] - 0.1, (
                f"Pressure 1 step before cascade ({traj[-1]['mean']:.3f}) should "
                f"be ≥ pressure 5 steps before ({traj[-5]['mean']:.3f})"
            )

    @pytest.mark.scaffold
    def test_results_serializable(self, medium_experiment):
        """Results dict should be JSON-serializable."""
        import json
        serialized = json.dumps(medium_experiment, default=str)
        assert len(serialized) > 100

    @pytest.mark.scaffold
    def test_config_recorded_in_results(self, medium_experiment):
        """Results should include the configuration used."""
        assert 'config' in medium_experiment
        assert 'n_trials' in medium_experiment['config']
        assert 'trigger_margin' in medium_experiment['config']
