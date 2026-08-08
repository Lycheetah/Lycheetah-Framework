"""
TRIAD Tracker — Gradient Ascent & Convergence Monitoring
========================================================

Implements TRIAD cycle: Anchor (Ao) → Observe (Ψ) → Correct (Φ↑) → back to Ao
With convergence condition: bounded step size α < 1/(2L) prevents divergence

TRIAD: Transformation, Reintegration, Iteration, Adaptive Development
Core iteration: Ψ_(n+1) = Ψ_n + α·∇C(Ψ_n) where α = learning rate, C = coherence

Convergence guarantee: Banach fixed-point theorem (λ < 1 required)
Conditions: α < 1/(2L) where L is Lipschitz constant of coherence gradient

Status: ACTIVE equation with scaffold parameter (α empirically TBD per domain)
Implementation: Gradient ascent stepper with convergence tracking
Author: Mackenzie Clark (Lycheetah Foundation)
Date: March 2026
"""

import numpy as np
import sys
from typing import Callable, Tuple, List, Dict, Optional
from dataclasses import dataclass
import json
from pathlib import Path

# Ensure UTF-8 output on Windows
if sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout.reconfigure(encoding='utf-8')


@dataclass
class TriadStep:
    """Single TRIAD iteration record."""
    iteration: int
    state: float  # Ψ value
    coherence: float  # C(Ψ)
    gradient: float  # ∇C(Ψ)
    step_size: float  # α used
    delta: float  # Change in state
    converged: bool = False

    def to_dict(self) -> Dict:
        return {
            "iteration": self.iteration,
            "state": self.state,
            "coherence": self.coherence,
            "gradient": self.gradient,
            "step_size": self.step_size,
            "delta": self.delta,
            "converged": self.converged,
        }


class TriadTracker:
    """Track TRIAD gradient ascent iterations and convergence."""

    def __init__(
        self,
        coherence_fn: Callable[[float], float],
        gradient_fn: Callable[[float], float],
        initial_state: float = 0.5,
        step_size: Optional[float] = None,
        lipschitz_constant: float = 2.0,
        convergence_threshold: float = 1e-6,
        max_iterations: int = 1000,
    ):
        """
        Initialize TRIAD tracker.

        Args:
            coherence_fn: C(Ψ) — coherence function to maximize
            gradient_fn: ∇C(Ψ) — gradient of coherence
            initial_state: Starting Ψ₀
            step_size: α learning rate. If None, use bounded value: α = 0.5 / L
            lipschitz_constant: L for Lipschitz condition α < 1/(2L)
            convergence_threshold: Stop when |Ψ_(n+1) − Ψ_n| < threshold
            max_iterations: Safety limit
        """
        self.coherence_fn = coherence_fn
        self.gradient_fn = gradient_fn
        self.state = initial_state
        self.lipschitz_constant = lipschitz_constant

        # Bounded step size: α < 1/(2L)
        self.max_step_size = 1.0 / (2.0 * lipschitz_constant)
        self.step_size = step_size if step_size is not None else self.max_step_size * 0.5

        if self.step_size >= self.max_step_size:
            print(
                f"⚠️  WARNING: step_size {self.step_size:.4f} >= max safe {self.max_step_size:.4f}\n"
                f"   Convergence not guaranteed. Consider reducing step_size."
            )

        self.convergence_threshold = convergence_threshold
        self.max_iterations = max_iterations

        self.history: List[TriadStep] = []
        self.anchor_state = initial_state  # Ao: anchor baseline
        self.iteration_count = 0

    def reset_anchor(self, new_anchor: Optional[float] = None) -> None:
        """
        Reset anchor point (Ao) to current state or specified value.

        This completes one TRIAD cycle: Ao → Ψ → Φ↑ → Ao (new)
        """
        if new_anchor is not None:
            self.anchor_state = new_anchor
        else:
            self.anchor_state = self.state
        print(f"✓ Anchor reset to {self.anchor_state:.6f}")

    def single_step(self) -> TriadStep:
        """
        Execute one TRIAD iteration:
        Ψ_(n+1) = Ψ_n + α·∇C(Ψ_n)

        Returns:
            TriadStep record
        """
        # Observe current coherence and gradient
        coherence = self.coherence_fn(self.state)
        gradient = self.gradient_fn(self.state)

        # Correct: ascend gradient
        delta = self.step_size * gradient
        new_state = self.state + delta

        # Check convergence
        is_converged = abs(delta) < self.convergence_threshold

        step = TriadStep(
            iteration=self.iteration_count,
            state=new_state,
            coherence=coherence,
            gradient=gradient,
            step_size=self.step_size,
            delta=delta,
            converged=is_converged,
        )

        self.state = new_state
        self.history.append(step)
        self.iteration_count += 1

        return step

    def run_until_convergence(self) -> Tuple[List[TriadStep], bool]:
        """
        Run TRIAD iterations until convergence or max iterations.

        Returns:
            (history, converged) tuple
        """
        converged = False
        for i in range(self.max_iterations):
            step = self.single_step()
            if step.converged:
                converged = True
                break

        return self.history, converged

    def get_history(self) -> List[TriadStep]:
        """Get all steps recorded so far."""
        return self.history

    def save_history(self, filepath: str) -> None:
        """Save step history to JSON."""
        data = {
            "initial_state": self.anchor_state,
            "final_state": self.state,
            "step_size": self.step_size,
            "max_step_size": self.max_step_size,
            "convergence_threshold": self.convergence_threshold,
            "total_iterations": len(self.history),
            "converged": len(self.history) > 0 and self.history[-1].converged,
            "steps": [step.to_dict() for step in self.history],
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    def report(self) -> str:
        """Generate convergence report."""
        if not self.history:
            return "No iterations yet."

        first = self.history[0]
        last = self.history[-1]

        lines = [
            "",
            "╔═══════════════════════════════════════════════════════════╗",
            "║            TRIAD CONVERGENCE REPORT                       ║",
            "╚═══════════════════════════════════════════════════════════╝",
            "",
            f"Anchor (Ao):              {self.anchor_state:.6f}",
            f"Initial state (Ψ₀):       {first.state:.6f}",
            f"Final state (Ψ_final):    {last.state:.6f}",
            f"Change:                   {last.state - first.state:.6f}",
            "",
            f"Step size (α):            {self.step_size:.6f}",
            f"Max safe step:            {self.max_step_size:.6f}",
            f"Lipschitz constant (L):   {self.lipschitz_constant:.4f}",
            f"Convergence criterion:    α < 1/(2L) = {1.0/(2*self.lipschitz_constant):.6f}",
            "",
            "─ Convergence Status ─────────────────────────────────────────",
            f"Total iterations:         {len(self.history)}",
            f"Converged:                {'✓ YES' if last.converged else '✗ NO'}",
            f"Final coherence C(Ψ):     {last.coherence:.6f}",
            f"Final gradient ∇C(Ψ):     {last.gradient:.6e}",
            f"Final step delta:         {abs(last.delta):.6e}",
            "",
        ]

        # Find iteration with max coherence
        max_idx = max(range(len(self.history)), key=lambda i: self.history[i].coherence)
        max_step = self.history[max_idx]

        lines.extend([
            "─ Best Coherence ─────────────────────────────────────────────",
            f"Iteration:                {max_step.iteration}",
            f"State:                    {max_step.state:.6f}",
            f"Coherence:                {max_step.coherence:.6f}",
            "",
        ])

        # Gradient trend
        early_grads = [self.history[i].gradient for i in range(min(5, len(self.history)))]
        late_grads = [self.history[i].gradient for i in range(max(0, len(self.history)-5), len(self.history))]

        if early_grads and late_grads:
            early_mean = np.mean(early_grads)
            late_mean = np.mean(late_grads)
            lines.extend([
                "─ Gradient Trend ─────────────────────────────────────────────",
                f"Early avg gradient:       {early_mean:.6e}",
                f"Late avg gradient:        {late_mean:.6e}",
                f"Trend:                    {'Decreasing ✓' if abs(late_mean) < abs(early_mean) else 'Increasing ✗'}",
                "",
            ])

        lines.append("─ Iteration Samples ──────────────────────────────────────────")
        # Show first, middle, and last few iterations
        samples = []
        samples.append(self.history[0])
        if len(self.history) > 2:
            samples.append(self.history[len(self.history) // 2])
        if len(self.history) > 1:
            samples.append(self.history[-1])

        for step in samples:
            lines.append(
                f"Iter {step.iteration:>4d}: Ψ={step.state:.6f}  C={step.coherence:.6f}  "
                f"∇C={step.gradient:.6e}  Δ={step.delta:.6e}"
            )

        lines.append("")
        return "\n".join(lines)


# Example usage: minimize Rosenbrock-like function (for testing)
def example_triad():
    """Example: gradient ascent on a test function."""

    # Test function: simple quadratic with maximum at 1.0
    def coherence_fn(psi: float) -> float:
        # C(Ψ) = 1 - (Ψ - 1)² = peak at Ψ=1
        return 1.0 - (psi - 1.0) ** 2

    def gradient_fn(psi: float) -> float:
        # ∇C = -2(Ψ - 1) = 2(1 - Ψ)
        return 2.0 * (1.0 - psi)

    print("TRIAD TRACKER EXAMPLE")
    print("=" * 60)
    print("Objective: Maximize C(Ψ) = 1 - (Ψ - 1)²")
    print("Optimum at Ψ = 1.0 with C = 1.0")
    print()

    tracker = TriadTracker(
        coherence_fn=coherence_fn,
        gradient_fn=gradient_fn,
        initial_state=0.2,
        lipschitz_constant=2.0,
        convergence_threshold=1e-6,
        max_iterations=100,
    )

    print("Starting TRIAD cycle...")
    history, converged = tracker.run_until_convergence()
    print(tracker.report())

    # Visualize as ASCII plot
    if len(history) > 0:
        print("\n─ State Trajectory ───────────────────────────────────────────")
        min_state = min(s.state for s in history)
        max_state = max(s.state for s in history)
        state_range = max_state - min_state
        if state_range == 0:
            state_range = 1

        for i in range(0, len(history), max(1, len(history) // 20)):
            step = history[i]
            # Normalize state to 0-40 for display
            pos = int(40 * (step.state - min_state) / state_range)
            bar = "█" * pos + " " * (40 - pos)
            print(f"Iter {step.iteration:>3d} [{bar}] Ψ={step.state:.4f} C={step.coherence:.6f}")


if __name__ == "__main__":
    example_triad()
