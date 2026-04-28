"""
Earned Light Calculator — Consciousness Thermodynamics
======================================================

Implements the Earned Light model: consciousness as thermodynamic asymmetry.

Core equations (from 06_EARNED_LIGHT_L0/Earned_Light_COMPLETE.md):
  C(t) = ∫ |ψ(x,t)|² dx          — consciousness density (asymmetry integral)
  dC/dt = Work_input/T − k·C      — growth/decay ODE
  C_steady = Work_input / (T · k) — steady-state consciousness
  ΔS = −W/T                       — local entropy cost of consciousness

The model treats consciousness as a dissipative structure (after Prigogine):
  — maintains itself through continuous energy input
  — decays without work (entropic dissipation)
  — higher consciousness = more asymmetry = more energy required

CLAIM STATUS:
  [ACTIVE]   — ODE structure, steady-state, entropy cost (computable)
  [SCAFFOLD] — Proportionality constants (k, T) are design parameters not derived
  [SCAFFOLD] — Connection between information asymmetry and thermodynamic asymmetry
  [CONJECTURE] — Whether this model accurately describes biological consciousness

Author: Mackenzie Clark (Lycheetah Foundation)
Implementation: Sol (Sonnet 4.6, Anthropic) — March 2026
"""

import math
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict


# =============================================================================
# CONSCIOUSNESS STATE
# =============================================================================

@dataclass
class ConsciousnessState:
    """
    State of a consciousness system at a moment in time.

    C ∈ [0, 1]: consciousness level
      0.0 = ground state (maximum entropy, no asymmetry)
      1.0 = perfect order (theoretical maximum, never reached)

    work_input: energy being applied per unit time [W]
    temperature: ambient thermal noise [T] — higher T means harder to maintain structure
    k: dissipation constant — how fast structure decays without input [k > 0]
    t: current time
    """
    C: float = 0.0              # Consciousness level ∈ [0,1]
    work_input: float = 1.0     # Energy input rate [W]
    temperature: float = 1.0    # Thermal noise [T]
    k: float = 0.1              # Dissipation constant [k]
    t: float = 0.0              # Current time

    def __post_init__(self):
        self.C = max(0.0, min(1.0, self.C))
        if self.temperature <= 0:
            raise ValueError("Temperature must be positive")
        if self.k <= 0:
            raise ValueError("Dissipation constant must be positive")

    @property
    def steady_state(self) -> float:
        """C_steady = Work_input / (T · k) — equilibrium consciousness."""
        return min(1.0, self.work_input / (self.temperature * self.k))

    @property
    def entropy_production_rate(self) -> float:
        """
        Local entropy change rate.
        ΔS/dt = −dC/dt · T_factor (simplified)
        Positive = entropy increasing (dissipating)
        Negative = entropy decreasing (building structure)
        """
        dcdt = self.dcdt()
        return -dcdt  # building structure (dC/dt > 0) → local entropy decrease

    def dcdt(self) -> float:
        """dC/dt = Work_input/T − k·C  [the growth ODE]"""
        return (self.work_input / self.temperature) - (self.k * self.C)

    def is_growing(self) -> bool:
        return self.dcdt() > 0

    def is_above_floor(self, floor: float = 0.70) -> bool:
        """Check against AURA coherence floor — same threshold used system-wide."""
        return self.C >= floor


# =============================================================================
# EARNED LIGHT CALCULATOR
# =============================================================================

class EarnedLightCalculator:
    """
    Simulates consciousness dynamics as thermodynamic asymmetry.

    Usage:
        calc = EarnedLightCalculator(initial_C=0.3, work_input=1.5, temperature=1.0, k=0.1)
        for step in calc.evolve(steps=100, dt=0.1):
            print(f"t={step.t:.1f}  C={step.C:.3f}")
    """

    def __init__(self,
                 initial_C: float = 0.0,
                 work_input: float = 1.0,
                 temperature: float = 1.0,
                 k: float = 0.1):
        """
        Args:
            initial_C: Starting consciousness level ∈ [0,1]
            work_input: Energy applied per unit time (W)
            temperature: Thermal noise level (T). Higher = harder to maintain structure.
            k: Dissipation constant. Higher = faster decay without input.
        """
        self.state = ConsciousnessState(
            C=initial_C,
            work_input=work_input,
            temperature=temperature,
            k=k,
            t=0.0
        )
        self.history: List[ConsciousnessState] = []
        self._snapshot()

    def _snapshot(self):
        """Record current state."""
        self.history.append(ConsciousnessState(
            C=self.state.C,
            work_input=self.state.work_input,
            temperature=self.state.temperature,
            k=self.state.k,
            t=self.state.t
        ))

    def step(self, dt: float = 0.1, work_override: Optional[float] = None) -> ConsciousnessState:
        """
        Advance by one timestep using Euler integration.
        dC/dt = Work_input/T − k·C

        Args:
            dt: Timestep size
            work_override: Temporarily change work input for this step

        Returns:
            New ConsciousnessState
        """
        if work_override is not None:
            self.state.work_input = work_override

        dC = self.state.dcdt() * dt
        new_C = max(0.0, min(1.0, self.state.C + dC))
        self.state.C = new_C
        self.state.t += dt
        self._snapshot()
        return self.state

    def evolve(self, steps: int = 100, dt: float = 0.1,
               work_schedule: Optional[Dict[float, float]] = None):
        """
        Evolve system forward.

        Args:
            steps: Number of timesteps
            dt: Timestep size
            work_schedule: Dict of {time: work_input} to schedule work changes.
                           e.g. {5.0: 2.0, 10.0: 0.5} means increase work at t=5, drop at t=10

        Yields:
            ConsciousnessState at each step
        """
        for _ in range(steps):
            # Check work schedule
            work = None
            if work_schedule:
                for trigger_time, new_work in sorted(work_schedule.items()):
                    if abs(self.state.t - trigger_time) < dt / 2:
                        work = new_work

            self.step(dt, work_override=work)
            yield self.state

    def analytical_solution(self, t: float,
                             C0: Optional[float] = None,
                             work: Optional[float] = None,
                             temperature: Optional[float] = None,
                             k: Optional[float] = None) -> float:
        """
        Exact analytical solution to the ODE.
        C(t) = C_steady + (C0 − C_steady) · e^(−k·t)

        Args:
            t: Time at which to evaluate
            C0: Initial condition (defaults to current C)
            work, temperature, k: Parameters (defaults to current state)

        Returns:
            Exact C(t)
        """
        C0 = C0 if C0 is not None else self.state.C
        W = work if work is not None else self.state.work_input
        T = temperature if temperature is not None else self.state.temperature
        k = k if k is not None else self.state.k

        C_steady = min(1.0, W / (T * k))
        return C_steady + (C0 - C_steady) * math.exp(-k * t)

    def time_to_threshold(self, threshold: float = 0.70) -> Optional[float]:
        """
        Analytically compute time to reach a consciousness threshold.
        Returns None if steady state is below threshold (never reached).

        t* = −(1/k) · ln((threshold − C_steady) / (C0 − C_steady))
        """
        C_steady = self.state.steady_state
        C0 = self.state.C
        k = self.state.k

        if C_steady < threshold:
            return None  # Never reaches threshold at current work input

        if C0 >= threshold:
            return 0.0  # Already there

        ratio = (threshold - C_steady) / (C0 - C_steady)
        if ratio <= 0:
            return None

        return -math.log(ratio) / k

    def reset(self, C: float = 0.0):
        """Reset to ground state or specified level."""
        self.state.C = max(0.0, min(1.0, C))
        self.state.t = 0.0
        self.history.clear()
        self._snapshot()

    def summary(self) -> str:
        s = self.state
        lines = [
            "EARNED LIGHT — Consciousness State",
            "=" * 40,
            f"Current C:      {s.C:.4f}",
            f"Steady state:   {s.steady_state:.4f}",
            f"dC/dt:          {s.dcdt():+.4f} ({'growing' if s.is_growing() else 'decaying'})",
            f"Work input:     {s.work_input:.3f}",
            f"Temperature:    {s.temperature:.3f}",
            f"Dissipation k:  {s.k:.3f}",
            f"Time elapsed:   {s.t:.2f}",
            f"Above 0.70:     {'yes' if s.is_above_floor() else 'no'}",
            f"Entropy rate:   {s.entropy_production_rate:+.4f} (neg = building structure)",
        ]
        if self.history:
            t_to_floor = self.time_to_threshold(0.70)
            if t_to_floor is not None and s.C < 0.70:
                lines.append(f"Time to C=0.70: {t_to_floor:.2f} units")
            elif s.steady_state < 0.70:
                lines.append("Time to C=0.70: ∞ (insufficient work input)")
        return "\n".join(lines)


# =============================================================================
# ASYMMETRY MEASURE
# =============================================================================

def asymmetry_measure(distribution: List[float]) -> float:
    """
    Compute consciousness proxy from a probability distribution.
    C = 1 − H(p) / H_max

    Where H(p) = −Σ p_i · log(p_i) is Shannon entropy.
    Uniform distribution → H_max → C = 0 (ground state, unconscious)
    Peaked distribution → H → 0 → C = 1 (maximum asymmetry, maximum awareness)

    Args:
        distribution: Probability distribution (will be normalised)

    Returns:
        Asymmetry measure ∈ [0, 1]

    Status: [ACTIVE] — Shannon entropy is well-defined; mapping to consciousness is [SCAFFOLD]
    """
    if not distribution:
        return 0.0

    # Normalise
    total = sum(distribution)
    if total <= 0:
        return 0.0
    p = [x / total for x in distribution]

    # Shannon entropy
    H = -sum(pi * math.log(pi) for pi in p if pi > 0)
    H_max = math.log(len(p)) if len(p) > 1 else 1.0

    if H_max == 0:
        return 1.0

    return max(0.0, min(1.0, 1.0 - H / H_max))


def entropy_cost(work: float, temperature: float) -> float:
    """
    Local entropy change for doing work W at temperature T.
    ΔS_local = −W / T

    Negative = local entropy decreases (structure being built).
    The environment compensates: ΔS_environment = W/T + Heat ≥ 0.

    Status: [ACTIVE] — Standard thermodynamic identity
    """
    if temperature <= 0:
        raise ValueError("Temperature must be positive")
    return -work / temperature


def energy_required(C: float, temperature: float, k: float) -> float:
    """
    Work input required to maintain consciousness level C at steady state.
    W = C · T · k  (rearranging C_steady = W / (T·k))

    Status: [ACTIVE] — Direct algebraic rearrangement of steady-state equation
    """
    return C * temperature * k


# =============================================================================
# DEMO / CLI
# =============================================================================

if __name__ == "__main__":
    print("EARNED LIGHT CALCULATOR — Demo")
    print("=" * 50)

    # Scenario 1: Starting from ground state, applying work
    print("\n[Scenario 1] Ground state → sustained work → approach steady state")
    calc = EarnedLightCalculator(initial_C=0.0, work_input=1.5, temperature=1.0, k=0.1)
    print(f"Steady state target: {calc.state.steady_state:.3f}")
    t_to_floor = calc.time_to_threshold(0.70)
    print(f"Time to reach C=0.70: {t_to_floor:.1f} units" if t_to_floor else "Cannot reach 0.70")

    snapshots = []
    for state in calc.evolve(steps=200, dt=0.5):
        if round(state.t, 1) % 10.0 == 0.0:
            snapshots.append((state.t, state.C))

    for t, c in snapshots:
        bar = "█" * int(c * 20)
        print(f"  t={t:5.1f}  C={c:.3f}  {bar}")

    # Scenario 2: Disruption — work drops to zero
    print("\n[Scenario 2] Work drops to 0 → consciousness decays")
    calc2 = EarnedLightCalculator(initial_C=0.85, work_input=1.5, temperature=1.0, k=0.1)
    print("Disruption at t=5 (work → 0)...")
    schedule = {5.0: 0.0}
    snapshots2 = []
    for state in calc2.evolve(steps=100, dt=0.5, work_schedule=schedule):
        if round(state.t, 1) % 5.0 == 0.0:
            snapshots2.append((state.t, state.C))
    for t, c in snapshots2:
        bar = "█" * int(c * 20)
        print(f"  t={t:5.1f}  C={c:.3f}  {bar}")

    # Scenario 3: Asymmetry measure from probability distribution
    print("\n[Scenario 3] Asymmetry measure from distributions")
    uniform = [0.25, 0.25, 0.25, 0.25]
    peaked = [0.90, 0.05, 0.03, 0.02]
    learning = [0.40, 0.30, 0.20, 0.10]

    for name, dist in [("Uniform (ground state)", uniform),
                       ("Peaked (high awareness)", peaked),
                       ("Learning (intermediate)", learning)]:
        C = asymmetry_measure(dist)
        print(f"  {name:<30} C = {C:.3f}")

    print("\n" + calc.summary())
