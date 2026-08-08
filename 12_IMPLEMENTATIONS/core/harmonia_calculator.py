"""
HARMONIA Calculator — Consonance Measurement & Kuramoto Coupling
==================================================================

Implements Pythagorean interval-based consonance measurement and
Kuramoto synchronization simulation for phase-lock analysis.

HARMONIA: Harmonic Resonance & Modularity Orchestration Network Interphase Acceleration
Core equation: C(r) = (w₀ + w₁·I(r)) / (1 + d(r)) where w = 0.5 (Barlow weighting)

Status: ACTIVE equations
Implementation: Consonance calculator + Kuramoto phase-locking simulator
Author: Mackenzie Clark (Lycheetah Foundation)
Date: March 2026
"""

import numpy as np
import sys
from typing import Tuple, List, Dict, Optional
from dataclasses import dataclass
import math

# Ensure UTF-8 output on Windows
if sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout.reconfigure(encoding='utf-8')


# Pythagorean intervals in cents (1200 cents = 1 octave)
PYTHAGOREAN_INTERVALS = {
    "unison": 0,
    "minor_second": 90.225,  # 256/243
    "major_second": 203.91,  # 9/8
    "minor_third": 294.135,  # 32/27
    "major_third": 407.82,   # 81/64
    "perfect_fourth": 498.045,  # 4/3
    "tritone": 590.22,       # 729/512
    "perfect_fifth": 701.955,  # 3/2
    "minor_sixth": 792.18,   # 128/81
    "major_sixth": 905.865,  # 27/16
    "minor_seventh": 996.09, # 16/9
    "major_seventh": 1109.775,  # 243/128
    "octave": 1200,
}


@dataclass
class FrequencyPair:
    """Two frequencies to measure consonance between."""
    f1: float  # Hz
    f2: float  # Hz
    label: str = "pair"

    @property
    def interval_cents(self) -> float:
        """Convert frequency ratio to cents."""
        if self.f1 <= 0 or self.f2 <= 0:
            return 0
        ratio = self.f2 / self.f1
        return 1200 * math.log2(ratio)

    @property
    def normalized_ratio(self) -> float:
        """Ratio normalized to [0.5, 2.0] range (within octave)."""
        ratio = self.f2 / self.f1
        # Bring into octave range
        while ratio > 2.0:
            ratio /= 2.0
        while ratio < 0.5:
            ratio *= 2.0
        return ratio


@dataclass
class KuramotoOscillator:
    """Single Kuramoto phase oscillator."""
    phase: float  # θ ∈ [0, 2π]
    omega: float  # Natural frequency (rad/s)
    label: str = "osc"

    def __post_init__(self):
        """Normalize phase to [0, 2π]."""
        self.phase = self.phase % (2 * np.pi)

    def step(self, coupling_sum: float, dt: float = 0.01) -> None:
        """
        Single Kuramoto step:  dθ/dt = ω + K·Σsin(θⱼ − θᵢ)

        Args:
            coupling_sum: Pre-computed Σsin(θⱼ − θᵢ) from network
            dt: Time step
        """
        # dθ/dt = ω + coupling_term
        dtheta = self.omega + coupling_sum
        self.phase += dtheta * dt
        self.phase = self.phase % (2 * np.pi)

    @property
    def position(self) -> Tuple[float, float]:
        """Position on unit circle."""
        return (np.cos(self.phase), np.sin(self.phase))


class HarmoniaCalculator:
    """Calculate consonance and Kuramoto synchronization."""

    # Barlow dissonance weighting: w = 0.5 (Barlow-proxy approximation)
    # NOTE: Specification formula: C(r) = 1/(1 + Σ aₖwᵏ) (continued fraction based)
    #       Implementation: Barlow-proxy approximation — intentional simplification for computational tractability
    #       The two produce correlated but non-identical values; implementation is the working approximation
    BARLOW_WEIGHT = 0.5

    def __init__(self):
        """Initialize calculator."""
        pass

    @staticmethod
    def interval_name(cents: float) -> str:
        """Find closest Pythagorean interval name."""
        min_diff = float('inf')
        closest = "unknown"

        for name, interval_cents in PYTHAGOREAN_INTERVALS.items():
            diff = abs(cents - interval_cents)
            if diff < min_diff:
                min_diff = diff
                closest = name

        return closest

    @staticmethod
    def barlow_dissonance(ratio: float) -> float:
        """
        Barlow dissonance metric d(r) based on prime factorization.

        For a frequency ratio r = p₁^a₁ × p₂^a₂ × ... :
        d(r) = Σ(|aᵢ| × log(pᵢ)) for odd primes, simplified for Pythagorean.

        For simplicity in Pythagorean context:
        d(r) = complexity of ratio (higher = more complex)
        """
        # Normalize ratio to [1, 2]
        while ratio > 2:
            ratio /= 2
        while ratio < 1:
            ratio *= 2

        # Distance from unison or octave: how "off" from simple ratios
        # Simple ratios (2/1, 3/2, 4/3, etc.) have low dissonance
        # Complex ratios have high dissonance

        # Approximate dissonance via log-frequency distance from harmonics
        log_ratio = np.log2(ratio)

        # Test against simple integer ratios
        min_dissonance = float('inf')
        for denom in range(1, 13):
            for numer in range(denom, 2 * denom + 1):
                test_ratio = np.log2(numer / denom)
                diff = abs(log_ratio - test_ratio)
                min_dissonance = min(min_dissonance, diff)

        return max(0.0, min_dissonance)

    def calculate_consonance(
        self,
        f1: float,
        f2: float,
        label: str = "pair"
    ) -> Dict:
        """
        Calculate C(r) = (w₀ + w₁·I(r)) / (1 + d(r)) with w = 0.5 Barlow

        Args:
            f1, f2: Two frequencies in Hz
            label: Label for the pair

        Returns:
            Dictionary with consonance breakdown
        """
        pair = FrequencyPair(f1, f2, label)
        ratio = pair.normalized_ratio

        # d(r) = Barlow dissonance
        dissonance = self.barlow_dissonance(ratio)

        # I(r) = interval stability indicator (0 to 1)
        # Higher for simpler intervals
        interval_indicator = 1.0 / (1.0 + dissonance)

        # C(r) = (w₀ + w₁·I(r)) / (1 + d(r))
        # w = 0.5 means w₀ = 0.5, w₁ = 0.5
        consonance = (
            (self.BARLOW_WEIGHT + self.BARLOW_WEIGHT * interval_indicator)
            / (1.0 + dissonance)
        )

        return {
            "label": label,
            "f1": f1,
            "f2": f2,
            "ratio": ratio,
            "interval_name": self.interval_name(pair.interval_cents),
            "interval_cents": pair.interval_cents,
            "dissonance": dissonance,
            "interval_indicator": interval_indicator,
            "consonance": consonance,
            "consonance_quality": self._consonance_quality(consonance),
        }

    @staticmethod
    def _consonance_quality(consonance: float) -> str:
        """Describe consonance level."""
        if consonance >= 0.8:
            return "PERFECT (highly consonant)"
        elif consonance >= 0.6:
            return "CLEAR (consonant)"
        elif consonance >= 0.4:
            return "MIXED (neutral)"
        elif consonance >= 0.2:
            return "TENSE (somewhat dissonant)"
        else:
            return "HARSH (highly dissonant)"


class KuramotoSimulator:
    """Kuramoto phase-locking simulator."""

    def __init__(self, frequencies: List[float], coupling_strength: float = 0.5):
        """
        Initialize Kuramoto network.

        Args:
            frequencies: List of natural frequencies (rad/s) for oscillators
            coupling_strength: K value (how strongly oscillators pull toward sync)
        """
        self.n = len(frequencies)
        self.K = coupling_strength

        # Random initial phases
        initial_phases = np.random.uniform(0, 2 * np.pi, self.n)
        self.oscillators = [
            KuramotoOscillator(initial_phases[i], frequencies[i], f"osc_{i}")
            for i in range(self.n)
        ]

    @property
    def order_parameter(self) -> float:
        """
        R = (1/N) |Σ e^(iθₖ)| ∈ [0,1]

        R ≈ 1: oscillators synchronized
        R ≈ 0: oscillators incoherent
        """
        positions = [osc.position for osc in self.oscillators]
        x_sum = sum(pos[0] for pos in positions)
        y_sum = sum(pos[1] for pos in positions)
        return np.sqrt(x_sum**2 + y_sum**2) / self.n

    def step(self, dt: float = 0.01) -> float:
        """
        Single simulation step. Returns order parameter after step.
        """
        # Compute coupling term for each oscillator
        positions = np.array([osc.position for osc in self.oscillators])

        # θⱼ − θᵢ for all pairs
        phase_diffs = np.zeros((self.n, self.n))
        for i in range(self.n):
            for j in range(self.n):
                phase_diffs[i, j] = self.oscillators[j].phase - self.oscillators[i].phase

        # sin(θⱼ − θᵢ) for coupling
        sin_diffs = np.sin(phase_diffs)

        # Update each oscillator
        for i in range(self.n):
            coupling_sum = (self.K / self.n) * np.sum(sin_diffs[i, :])
            self.oscillators[i].step(coupling_sum, dt)

        return self.order_parameter

    def simulate(self, steps: int = 1000, dt: float = 0.01) -> List[float]:
        """
        Run simulation for N steps, track order parameter.

        Returns:
            List of order parameter values over time
        """
        history = []
        for _ in range(steps):
            r = self.step(dt)
            history.append(r)
        return history

    def final_phases(self) -> Dict[str, float]:
        """Get final phase of each oscillator."""
        return {osc.label: osc.phase for osc in self.oscillators}

    def synchronization_strength(self, history: List[float]) -> Dict:
        """
        Analyze synchronization from history.

        Returns:
            Dictionary with sync metrics
        """
        if not history:
            return {}

        final_r = history[-1]
        max_r = max(history)
        min_r = min(history)
        stabilized = history[-100:] if len(history) >= 100 else history

        return {
            "final_order_parameter": final_r,
            "peak_coherence": max_r,
            "minimum_coherence": min_r,
            "final_stability": np.std(stabilized),
            "synchronized": final_r > 0.7,
            "convergence_speed": (
                "fast" if max_r > 0.5 and max(history[:100]) > 0.5 else
                "slow" if final_r > 0.3 else
                "incoherent"
            ),
        }


def example_harmonia():
    """Example: consonance of musical intervals."""
    calc = HarmoniaCalculator()

    # Middle C and C note above (octave)
    c1, c2 = 261.63, 523.26
    report = calc.calculate_consonance(c1, c2, "C1-C2 (octave)")

    print("HARMONIA CONSONANCE CALCULATION")
    print("=" * 60)
    print(f"Interval: {report['label']}")
    print(f"Frequencies: {report['f1']:.2f} Hz, {report['f2']:.2f} Hz")
    print(f"Ratio: {report['ratio']:.4f}")
    print(f"Pythagorean interval: {report['interval_name']}")
    print(f"Interval (cents): {report['interval_cents']:.2f}")
    print(f"Dissonance d(r): {report['dissonance']:.4f}")
    print(f"Consonance C(r): {report['consonance']:.4f}")
    print(f"Quality: {report['consonance_quality']}")
    print()

    # Another example: perfect fifth
    a4, e5 = 440.0, 659.25  # A4, E5 (perfect fifth)
    report2 = calc.calculate_consonance(a4, e5, "A4-E5 (perfect fifth)")
    print(f"Interval: {report2['label']}")
    print(f"Consonance C(r): {report2['consonance']:.4f}")
    print(f"Quality: {report2['consonance_quality']}")
    print()

    # Kuramoto simulation
    print("KURAMOTO SYNCHRONIZATION")
    print("=" * 60)

    # Three oscillators with slightly different frequencies
    frequencies = np.array([1.0, 1.05, 1.02]) * 2 * np.pi
    sim = KuramotoSimulator(frequencies, coupling_strength=0.5)

    history = sim.simulate(steps=500, dt=0.01)

    sync_report = sim.synchronization_strength(history)
    print(f"Initial order parameter: {history[0]:.4f}")
    print(f"Final order parameter: {sync_report['final_order_parameter']:.4f}")
    print(f"Peak coherence: {sync_report['peak_coherence']:.4f}")
    print(f"Synchronized: {sync_report['synchronized']}")
    print(f"Convergence: {sync_report['convergence_speed']}")
    print(f"Final phases: {sim.final_phases()}")


if __name__ == "__main__":
    example_harmonia()
