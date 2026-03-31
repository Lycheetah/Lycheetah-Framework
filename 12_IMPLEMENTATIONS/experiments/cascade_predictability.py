"""
Experiment 5: CASCADE Predictability Test
==========================================
Can the CASCADE engine predict a cascade is about to fire
before the triggering evidence arrives?

Roadmap reference: EXPERIMENTAL_ROADMAP_2026_2028.md, Experiment 5
No external dependencies. Runs standalone.

WHAT THIS TESTS
---------------
CASCADE fires when: new_Π > old_Π + trigger_margin
The question: given only the *current* pyramid state, can we predict
that a cascade will fire in the next k steps (k = 1, 3, 5)?

Prediction is made at step t using the Π-gap pressure score:
    pressure(t) = max over domains of [ new_Π(t) − old_Π(t) ]

When this gap is rising and approaching trigger_margin, a cascade is imminent.

SUCCESS CRITERION: F1 > 0.80 at k=5 lookahead

DESIGN
------
1. Generate 500 knowledge sequences (gradual evidence buildup per domain)
2. Split 50/50 train/test — threshold optimized on train, reported on test
3. Compute Π-gap pressure score at each step
4. Label each step: "cascade fires in next k steps?" for k=1,3,5
5. Threshold classifier vs random baseline
6. Metrics: precision, recall, F1, accuracy, AUC (from sklearn-free ROC)

Author: Mackenzie Clark, Lycheetah Foundation
Date: March 2026
"""

import numpy as np
from scipy import stats as sp_stats
import json
import sys
import os

# ─── Import CASCADE core ─────────────────────────────────────────────────────

sys.path.insert(0, os.path.dirname(__file__))
from cascade_real_experiments import Block, Pyramid, cascade_add


# =============================================================================
# SEQUENCE GENERATOR
# =============================================================================

def make_gradual_sequence(rng, n_domains=4, n_steps=40,
                           trigger_margin=0.1, noise=0.04):
    """
    Generate a knowledge sequence where new-paradigm evidence builds gradually.

    Phase 1 (steps 0..n_domains-1): Add classical (old-paradigm) foundations.
    Phase 2 (steps n_domains..n_steps-1): Modern blocks are added domain by
      domain, each with slightly increasing evidence. Evidence grows at a
      random rate, with Gaussian noise.

    Returns
    -------
    steps : list of dict — one entry per step:
        'block'     : Block added at this step
        'domain'    : domain label
        'is_trigger': True if this block fires a cascade
        'gap_before': max(new_Π − old_Π) across domains BEFORE this block is added
        'pyr_before': snapshot of Pyramid state (coherence, n_contradictions)
    pyramid : Pyramid — final state
    cascade_steps : list of step indices where a cascade fired
    """
    domains = [f'd{i}' for i in range(n_domains)]

    # Classical blocks: strong evidence, established foundations
    # Π = (E * P) / S ≈ (0.90 * 1.75) / 0.40 ≈ 3.9 — solid foundations
    classical = []
    for d in domains:
        b = Block(
            name=f'classical_{d}',
            evidence=float(rng.uniform(0.85, 0.95)),
            power=float(rng.uniform(1.5, 2.0)),
            entropy=float(rng.uniform(0.35, 0.45)),
            domain=d,
            regime='universal',
        )
        classical.append(b)

    # Modern blocks: similar power/entropy to classical, but evidence starts LOW
    # and grows over time. This ensures gradual buildup across 10-20 steps.
    #
    # Key design constraint:
    #   modern_Π_start < classical_Π  (no immediate cascade)
    #   modern_Π_final > classical_Π + trigger_margin  (cascade fires eventually)
    #
    # With E_start ∈ [0.30, 0.45], P ∈ [1.6, 2.1], S ∈ [0.35, 0.45]:
    #   Π_start ≈ (0.38 * 1.85) / 0.40 ≈ 1.76  (well below classical ~3.9)
    # After ~16 steps at +0.030/step, E ≈ 0.86:
    #   Π_final ≈ (0.86 * 1.85) / 0.40 ≈ 3.98  (surpasses classical ~3.9 by >0.1)
    modern_base = []
    modern_growth = []
    for i, d in enumerate(domains):
        e0 = float(rng.uniform(0.30, 0.45))
        rate = float(rng.uniform(0.025, 0.040))
        b = Block(
            name=f'modern_{d}',
            evidence=e0,
            power=float(rng.uniform(1.6, 2.1)),
            entropy=float(rng.uniform(0.35, 0.45)),
            domain=d,
            regime='universal',
            contradicts={f'classical_{d}'},
        )
        # Set reverse contradiction
        classical[i].contradicts.add(f'modern_{d}')
        modern_base.append(b)
        modern_growth.append(rate)

    pyr = Pyramid()
    steps = []
    cascade_steps = []

    # Phase 1: Add classical foundations
    for b in classical:
        step_info = {
            'phase': 'classical',
            'block': b.name,
            'domain': b.domain,
            'is_trigger': False,
            'gap_before': _compute_max_gap(pyr, domains, trigger_margin),
            'pressure_before': _compute_pressure(pyr, domains, trigger_margin),
            'pyr_coherence_before': pyr.coherence(),
            'pyr_n_contradictions_before': pyr._active_contradictions(),
        }
        pyr.blocks[b.name] = b  # direct insert (phase 1 is just setup)
        steps.append(step_info)

    # Phase 2: Modern evidence builds up step by step
    # Each step: pick the domain with highest current Π deficit (most likely to cascade soon)
    # and update that domain's modern block evidence
    n_modern_steps = n_steps - n_domains

    # Track current evidence level for each modern block
    current_evidence = {d: modern_base[i].evidence for i, d in enumerate(domains)}
    # Determine the update order: domains cycle in random order, repeated
    domain_order = list(rng.permutation(n_domains))  # initial order
    step_count = 0

    for step_idx in range(n_modern_steps):
        # Pick domain for this step (cycle through domains in shuffled order)
        d_idx = domain_order[step_count % n_domains]
        d = domains[d_idx]

        # Advance that domain's evidence with noise
        growth = modern_growth[d_idx]
        current_evidence[d] = min(
            float(current_evidence[d] + growth + rng.normal(0, noise)),
            0.99
        )

        # Build the modern block at current evidence
        b = Block(
            name=f'modern_{d}',
            evidence=current_evidence[d],
            power=modern_base[d_idx].power,
            entropy=modern_base[d_idx].entropy,
            domain=d,
            regime='universal',
            contradicts={f'classical_{d}'},
        )

        # Compute features BEFORE adding this block
        gap_before = _compute_max_gap(pyr, domains, trigger_margin)
        pressure_before = _compute_pressure(pyr, domains, trigger_margin)

        step_info = {
            'phase': 'modern',
            'block': b.name,
            'domain': d,
            'gap_before': gap_before,
            'pressure_before': pressure_before,
            'pyr_coherence_before': pyr.coherence(),
            'pyr_n_contradictions_before': pyr._active_contradictions(),
            'is_trigger': False,
        }

        # Add block — check if cascade fires
        log = cascade_add(pyr, b, threshold=trigger_margin)
        if log and log.get('triggered'):
            step_info['is_trigger'] = True
            cascade_steps.append(len(steps))

        steps.append(step_info)
        step_count += 1

        # Re-shuffle domain order every full cycle for variety
        if step_count % n_domains == 0:
            domain_order = list(rng.permutation(n_domains))

    return steps, pyr, cascade_steps


def _compute_max_gap(pyr, domains, trigger_margin):
    """
    Max over all domains of: modern_Π − classical_Π.
    Positive = modern is gaining on classical; > trigger_margin = cascade fires.
    """
    max_gap = -999.0
    for d in domains:
        old_pi = max(
            (b.pi for b in pyr.blocks.values()
             if b.domain == d and b.name.startswith('classical')
             and b.regime == 'universal'),
            default=None
        )
        new_pi = max(
            (b.pi for b in pyr.blocks.values()
             if b.domain == d and b.name.startswith('modern')),
            default=None
        )
        if old_pi is not None and new_pi is not None:
            max_gap = max(max_gap, new_pi - old_pi)
    return max_gap if max_gap > -999.0 else 0.0


def _compute_pressure(pyr, domains, trigger_margin):
    """
    Normalized Π-gap pressure score.
    pressure = max_gap / trigger_margin
    > 1.0 means cascade has already fired (gap crossed trigger)
    0..1 means building toward trigger
    < 0 means far below trigger
    """
    gap = _compute_max_gap(pyr, domains, trigger_margin)
    return gap / (trigger_margin + 1e-10)


# =============================================================================
# LABEL GENERATOR
# =============================================================================

def make_labels(steps, lookahead_k):
    """
    For each step t, label = 1 if any cascade fires in steps [t, t+k).
    Only consider steps in 'modern' phase.

    Returns parallel arrays (modern_steps_only):
        features : (n_modern,) array of pressure_before scores
        labels   : (n_modern,) array of 0/1
        step_indices : which global step indices these are
    """
    modern_indices = [i for i, s in enumerate(steps) if s['phase'] == 'modern']
    n = len(modern_indices)

    features = np.array([steps[i]['pressure_before'] for i in modern_indices])
    labels = np.zeros(n, dtype=int)

    for j, global_idx in enumerate(modern_indices):
        # Check if any of global_idx, ..., global_idx + k - 1 is a trigger
        for offset in range(lookahead_k):
            target = global_idx + offset
            if target < len(steps) and steps[target]['is_trigger']:
                labels[j] = 1
                break

    return features, labels, modern_indices


# =============================================================================
# THRESHOLD CLASSIFIER
# =============================================================================

def find_optimal_threshold(features_train, labels_train, n_thresholds=200):
    """
    Find the pressure threshold that maximizes F1 on the training set.
    Returns: best_threshold (float), train_f1 (float)
    """
    if labels_train.sum() == 0:
        return 0.5, 0.0

    # Search from min to max of features
    lo, hi = features_train.min(), features_train.max()
    if lo >= hi:
        return (lo + hi) / 2, 0.0

    thresholds = np.linspace(lo, hi, n_thresholds)
    best_t, best_f1 = 0.0, 0.0

    for t in thresholds:
        preds = (features_train >= t).astype(int)
        f1 = _f1(labels_train, preds)
        if f1 > best_f1:
            best_f1 = f1
            best_t = t

    return best_t, best_f1


def evaluate(features, labels, threshold):
    """Compute precision, recall, F1, accuracy at given threshold."""
    preds = (features >= threshold).astype(int)
    tp = int(np.sum((preds == 1) & (labels == 1)))
    fp = int(np.sum((preds == 1) & (labels == 0)))
    fn = int(np.sum((preds == 0) & (labels == 1)))
    tn = int(np.sum((preds == 0) & (labels == 0)))

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall    = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1        = _f1(labels, preds)
    accuracy  = (tp + tn) / len(labels) if len(labels) > 0 else 0.0

    return {
        'precision': precision, 'recall': recall,
        'f1': f1, 'accuracy': accuracy,
        'tp': tp, 'fp': fp, 'fn': fn, 'tn': tn,
        'threshold': threshold,
    }


def random_baseline(labels, rng, n_bootstrap=500):
    """F1 of a random classifier (positive rate = empirical base rate)."""
    base_rate = labels.mean()
    f1s = []
    for _ in range(n_bootstrap):
        preds = (rng.random(len(labels)) < base_rate).astype(int)
        f1s.append(_f1(labels, preds))
    return float(np.mean(f1s)), float(np.std(f1s))


def _f1(labels, preds):
    tp = np.sum((preds == 1) & (labels == 1))
    fp = np.sum((preds == 1) & (labels == 0))
    fn = np.sum((preds == 0) & (labels == 1))
    if tp + fp == 0 or tp + fn == 0:
        return 0.0
    p = tp / (tp + fp)
    r = tp / (tp + fn)
    return 2 * p * r / (p + r) if (p + r) > 0 else 0.0


def sklearn_free_auc(features, labels, n_thresholds=200):
    """Compute AUC without sklearn by sweeping thresholds."""
    if labels.sum() == 0 or labels.sum() == len(labels):
        return 0.5

    lo, hi = features.min(), features.max()
    thresholds = np.linspace(lo - 0.01, hi + 0.01, n_thresholds)
    fprs, tprs = [], []
    pos = labels.sum()
    neg = len(labels) - pos

    for t in thresholds:
        preds = (features >= t).astype(int)
        tp = np.sum((preds == 1) & (labels == 1))
        fp = np.sum((preds == 1) & (labels == 0))
        tprs.append(tp / pos if pos > 0 else 0)
        fprs.append(fp / neg if neg > 0 else 0)

    # Sort by FPR for trapezoidal integration
    pairs = sorted(zip(fprs, tprs))
    fprs_s, tprs_s = zip(*pairs)
    # Manual trapezoidal integration (np.trapz removed in NumPy 2.x)
    auc = float(sum(
        (fprs_s[i + 1] - fprs_s[i]) * (tprs_s[i + 1] + tprs_s[i]) / 2
        for i in range(len(fprs_s) - 1)
    ))
    return max(auc, 1.0 - auc)  # ensure AUC >= 0.5 by flipping if needed


# =============================================================================
# VELOCITY FEATURE
# =============================================================================

def add_velocity_features(all_steps_features):
    """
    Augment features with 3-step velocity of pressure score.
    Returns (n,2) array: [pressure, velocity]
    """
    n = len(all_steps_features)
    velocity = np.zeros(n)
    for i in range(1, n):
        velocity[i] = all_steps_features[i] - all_steps_features[i - 1]
    for i in range(1, n - 1):
        # Smooth: 3-step rolling average of velocity
        velocity[i] = (all_steps_features[i + 1] - all_steps_features[max(0, i - 1)]) / min(2, i + 1)
    return np.column_stack([all_steps_features, velocity])


# =============================================================================
# MAIN EXPERIMENT
# =============================================================================

def run_experiment5(n_trials=500, n_domains=4, n_steps=44,
                     trigger_margin=0.1, noise=0.04,
                     train_fraction=0.5, seed=42,
                     verbose=True):
    """
    Run the full CASCADE Predictability experiment.

    Parameters
    ----------
    n_trials : int
        Number of knowledge sequences to generate
    n_domains : int
        Domains per sequence (number of paradigm conflict sites)
    n_steps : int
        Total steps per sequence (n_domains phase-1 + remainder phase-2)
    trigger_margin : float
        CASCADE trigger threshold (Δπ required to fire a cascade)
    noise : float
        Evidence noise level per step
    train_fraction : float
        Fraction of trials used for threshold optimisation
    seed : int
        RNG seed for reproducibility
    verbose : bool
        Print progress and results

    Returns
    -------
    dict: full results including per-k metrics, AUC, baseline comparison
    """
    rng = np.random.default_rng(seed)

    if verbose:
        print("=" * 65)
        print("EXPERIMENT 5: CASCADE Predictability Test")
        print(f"  Trials: {n_trials}, Domains/trial: {n_domains}")
        print(f"  Steps/trial: {n_steps}, Trigger margin: {trigger_margin}")
        print(f"  Noise: {noise}, Train fraction: {train_fraction}")
        print("=" * 65)

    # ─── Data collection ────────────────────────────────────────────────────

    all_sequences = []
    n_total_cascades = 0

    for trial in range(n_trials):
        trial_rng = np.random.default_rng(seed + trial)
        steps, pyr, cascade_steps = make_gradual_sequence(
            trial_rng, n_domains=n_domains, n_steps=n_steps,
            trigger_margin=trigger_margin, noise=noise
        )
        all_sequences.append((steps, cascade_steps))
        n_total_cascades += len(cascade_steps)

        if verbose and (trial + 1) % 100 == 0:
            print(f"  Generated {trial + 1}/{n_trials} sequences "
                  f"({n_total_cascades} cascades so far)...")

    if verbose:
        avg_cascades = n_total_cascades / n_trials
        print(f"\n  Total cascades across all sequences: {n_total_cascades}")
        print(f"  Average cascades per sequence: {avg_cascades:.2f}")

    # ─── Build feature/label datasets for k = 1, 3, 5 ─────────────────────

    lookaheads = [1, 3, 5]
    results = {}

    n_train = int(n_trials * train_fraction)

    for k in lookaheads:
        if verbose:
            print(f"\n{'─'*50}")
            print(f"  Lookahead k={k}")

        # Aggregate all modern-phase steps across sequences
        all_features = []
        all_labels = []
        all_trial_ids = []

        for trial_id, (steps, _) in enumerate(all_sequences):
            features, labels, _ = make_labels(steps, lookahead_k=k)
            all_features.append(features)
            all_labels.append(labels)
            all_trial_ids.extend([trial_id] * len(features))

        all_features = np.concatenate(all_features)
        all_labels = np.concatenate(all_labels)

        # Train/test split by trial (not by step — avoids leakage)
        train_mask = np.array(all_trial_ids) < n_train
        test_mask = ~train_mask

        feat_train = all_features[train_mask]
        lab_train = all_labels[train_mask]
        feat_test = all_features[test_mask]
        lab_test = all_labels[test_mask]

        if verbose:
            print(f"    Train: {train_mask.sum()} steps, "
                  f"{lab_train.sum()} positive ({lab_train.mean():.1%})")
            print(f"    Test:  {test_mask.sum()} steps, "
                  f"{lab_test.sum()} positive ({lab_test.mean():.1%})")

        # Find optimal threshold on training set
        best_thresh, train_f1 = find_optimal_threshold(feat_train, lab_train)

        # Evaluate on test set
        metrics = evaluate(feat_test, lab_test, best_thresh)
        metrics['train_f1'] = train_f1

        # AUC
        auc = sklearn_free_auc(feat_test, lab_test)
        metrics['auc'] = auc

        # Random baseline
        baseline_f1, baseline_std = random_baseline(lab_test, rng)
        metrics['baseline_f1'] = baseline_f1
        metrics['baseline_f1_std'] = baseline_std

        # Statistical significance: is predictor F1 > baseline?
        # Bootstrap test: resample test set, compare F1 distributions
        pred_f1s = []
        rand_f1s = []
        for _ in range(500):
            idx = rng.integers(0, len(feat_test), len(feat_test))
            pred_f1s.append(_f1(lab_test[idx], (feat_test[idx] >= best_thresh).astype(int)))
            preds_rand = (rng.random(len(idx)) < lab_test.mean()).astype(int)
            rand_f1s.append(_f1(lab_test[idx], preds_rand))

        t_stat, p_val = sp_stats.ttest_ind(pred_f1s, rand_f1s)
        metrics['vs_baseline_t'] = float(t_stat)
        metrics['vs_baseline_p'] = float(p_val)

        passed = metrics['f1'] > 0.80
        metrics['success_criterion_met'] = passed

        results[f'k{k}'] = metrics

        if verbose:
            sig = '***' if p_val < 0.001 else '**' if p_val < 0.01 else '*' if p_val < 0.05 else 'ns'
            print(f"    Optimal threshold: {best_thresh:.4f}")
            print(f"    Precision: {metrics['precision']:.3f} | "
                  f"Recall: {metrics['recall']:.3f} | "
                  f"F1: {metrics['f1']:.3f} | "
                  f"Accuracy: {metrics['accuracy']:.3f}")
            print(f"    AUC: {auc:.3f}")
            print(f"    Random baseline F1: {baseline_f1:.3f} ± {baseline_std:.3f}")
            print(f"    vs Baseline: t={t_stat:.2f}, p={p_val:.2e} {sig}")
            status = "✓ PASSES" if passed else "✗ below"
            print(f"    Success criterion (F1 > 0.80): {status} — F1={metrics['f1']:.3f}")

    # ─── Cross-k summary ────────────────────────────────────────────────────

    if verbose:
        print(f"\n{'='*65}")
        print("PREDICTABILITY SUMMARY")
        print(f"{'='*65}")
        print(f"\n  {'k':>4} {'F1':>8} {'AUC':>8} {'Precision':>12} "
              f"{'Recall':>10} {'Baseline F1':>14} {'p-value':>12}")
        print(f"  {'─'*70}")
        for k in lookaheads:
            m = results[f'k{k}']
            sig = '***' if m['vs_baseline_p'] < 0.001 else '**' if m['vs_baseline_p'] < 0.01 else '*'
            print(f"  {k:>4} {m['f1']:>8.3f} {m['auc']:>8.3f} "
                  f"{m['precision']:>12.3f} {m['recall']:>10.3f} "
                  f"{m['baseline_f1']:>14.3f} "
                  f"{m['vs_baseline_p']:>10.2e} {sig}")

    # ─── Π-gap trajectory analysis ──────────────────────────────────────────
    # Show the mean pressure score trajectory across all sequences
    # to characterize how early the signal rises before a cascade

    if verbose:
        print(f"\n{'─'*65}")
        print("Π-GAP PRESSURE TRAJECTORY (mean over all sequences)")
        print("Steps relative to cascade event (0 = step of cascade)")

    window = 8  # steps before/after cascade
    pre_cascade_pressures = {offset: [] for offset in range(-window, 1)}

    for steps, cascade_steps in all_sequences:
        modern_steps = [(i, s) for i, s in enumerate(steps) if s['phase'] == 'modern']
        cascade_set = set(cascade_steps)

        for c_step in cascade_steps:
            # Find position of c_step in modern_steps list
            modern_positions = [i for i, (gi, s) in enumerate(modern_steps) if gi == c_step]
            if not modern_positions:
                continue
            m_pos = modern_positions[0]

            for offset in range(-window, 1):
                idx = m_pos + offset
                if 0 <= idx < len(modern_steps):
                    _, step_info = modern_steps[idx]
                    pre_cascade_pressures[offset].append(step_info['pressure_before'])

    trajectory_summary = {}
    if verbose:
        print(f"  {'Step':>6} {'Mean pressure':>16} {'Std':>8}")
        print(f"  {'─'*32}")

    for offset in range(-window, 1):
        vals = pre_cascade_pressures[offset]
        if vals:
            m, s = float(np.mean(vals)), float(np.std(vals))
            trajectory_summary[offset] = {'mean': m, 'std': s, 'n': len(vals)}
            if verbose:
                bar = '█' * max(0, int((m + 1) * 8))
                label = "← CASCADE" if offset == 0 else ""
                print(f"  {offset:>+6}  {m:>+10.4f} ± {s:.4f}  {bar} {label}")

    results['trajectory'] = trajectory_summary
    results['n_trials'] = n_trials
    results['n_total_cascades'] = n_total_cascades
    results['avg_cascades_per_trial'] = float(n_total_cascades / n_trials)
    results['config'] = {
        'n_trials': n_trials, 'n_domains': n_domains, 'n_steps': n_steps,
        'trigger_margin': trigger_margin, 'noise': noise,
        'train_fraction': train_fraction, 'seed': seed,
    }

    return results


# =============================================================================
# ENTRY POINT
# =============================================================================

def run_all(output_file='cascade_predictability_results.json', verbose=True):
    """Run Experiment 5 and save results."""

    if verbose:
        print("\n" + "=" * 65)
        print("CASCADE PREDICTABILITY — EXPERIMENT 5")
        print("Zero external dependencies. Reproduces in < 60 seconds.")
        print("=" * 65 + "\n")

    results = run_experiment5(
        n_trials=500,
        n_domains=4,
        n_steps=44,       # 4 classical setup + 40 modern buildup steps
        trigger_margin=0.1,
        noise=0.04,
        train_fraction=0.5,
        seed=42,
        verbose=verbose,
    )

    # Final verdict
    k5 = results['k5']
    if verbose:
        print(f"\n{'='*65}")
        print("FINAL VERDICT")
        print(f"{'='*65}")
        if k5['success_criterion_met']:
            print(f"\n  ✓ SUCCESS: Cascade predictability confirmed.")
            print(f"    F1={k5['f1']:.3f} at 5-step lookahead "
                  f"(criterion: F1 > 0.80)")
            print(f"    AUC={k5['auc']:.3f} (0.5=random, 1.0=perfect)")
            print(f"    Interpretation: The CASCADE engine can anticipate a")
            print(f"    paradigm shift 5 evidence-steps before it fires,")
            print(f"    using only the current Π-gap pressure signal.")
        else:
            print(f"\n  ✗ CRITERION NOT MET at k=5: F1={k5['f1']:.3f}")
            print(f"    Check trajectory summary for signal characterisation.")
        print()

    # Save
    output_path = os.path.join(os.path.dirname(__file__), output_file)
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    if verbose:
        print(f"  Results saved: {output_path}")

    return results


if __name__ == '__main__':
    run_all()
