"""
Calibrate Master Equation — Parameter Fitting from CASCADE Data
==============================================================

Master equation:
    dΨ/dt = k₁·(Π − Π_th) − k₂·(Ψ − Ψ_inv) − k₃·I_violations + k₄·(E_avail/E_need)

This module fits coupling constants k₁, k₂, k₃, k₄ from empirical CASCADE data.

Status: SCAFFOLD — Structure is real, parameters empirically TBD
Implementation: Least-squares fitting of master equation to CASCADE trials

Author: Mackenzie Clark (Lycheetah Foundation)
Date: March 2026
"""

import numpy as np
import sys
from typing import Tuple, List, Dict, Optional
from dataclasses import dataclass
import json
from pathlib import Path

# Ensure UTF-8 output on Windows
if sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout.reconfigure(encoding='utf-8')


@dataclass
class MasterEquationParams:
    """Master equation coupling constants."""
    k1: float  # Truth pressure drive
    k2: float  # Identity restoration
    k3: float  # Invariant penalty
    k4: float  # Energy constraint
    pi_threshold: float = 1.2  # THEORY threshold
    psi_inv: float = 0.70  # AURA coherence floor
    rms_error: float = 0.0  # Fit quality

    def to_dict(self) -> Dict:
        return {
            "k1": self.k1,
            "k2": self.k2,
            "k3": self.k3,
            "k4": self.k4,
            "pi_threshold": self.pi_threshold,
            "psi_inv": self.psi_inv,
            "rms_error": self.rms_error,
        }


@dataclass
class CascadeObservation:
    """Single observation from CASCADE experiment."""
    time: float  # Time point
    truth_pressure: float  # Π
    coherence: float  # Ψ
    aura_violations: int  # Count of I violations
    energy_ratio: float  # E_avail / E_need
    coherence_derivative: Optional[float] = None  # dΨ/dt observed

    def to_dict(self) -> Dict:
        return {
            "time": self.time,
            "truth_pressure": self.truth_pressure,
            "coherence": self.coherence,
            "aura_violations": self.aura_violations,
            "energy_ratio": self.energy_ratio,
            "coherence_derivative": self.coherence_derivative,
        }


class MasterEquationCalibrator:
    """Fit master equation parameters from CASCADE data."""

    def __init__(self):
        """Initialize calibrator."""
        self.observations: List[CascadeObservation] = []
        self.fit_params: Optional[MasterEquationParams] = None

    def add_observation(
        self,
        time: float,
        truth_pressure: float,
        coherence: float,
        aura_violations: int,
        energy_ratio: float,
        coherence_derivative: Optional[float] = None,
    ) -> None:
        """Add single observation to dataset."""
        obs = CascadeObservation(
            time=time,
            truth_pressure=truth_pressure,
            coherence=coherence,
            aura_violations=aura_violations,
            energy_ratio=energy_ratio,
            coherence_derivative=coherence_derivative,
        )
        self.observations.append(obs)

    def add_observations_batch(self, observations: List[CascadeObservation]) -> None:
        """Add multiple observations at once."""
        self.observations.extend(observations)

    def estimate_derivatives(self, smoothing_window: int = 3) -> None:
        """
        Estimate dΨ/dt using finite differences with smoothing.

        If observations lack derivative, compute from coherence differences.
        """
        if not self.observations:
            return

        for i in range(len(self.observations)):
            if self.observations[i].coherence_derivative is not None:
                continue

            # Use central differences where possible
            if 0 < i < len(self.observations) - 1:
                dt = self.observations[i+1].time - self.observations[i-1].time
                if dt > 0:
                    dpsi = (
                        self.observations[i+1].coherence
                        - self.observations[i-1].coherence
                    )
                    self.observations[i].coherence_derivative = dpsi / dt
            elif i == 0 and len(self.observations) > 1:
                dt = self.observations[1].time - self.observations[0].time
                if dt > 0:
                    dpsi = self.observations[1].coherence - self.observations[0].coherence
                    self.observations[0].coherence_derivative = dpsi / dt
            elif i == len(self.observations) - 1 and len(self.observations) > 1:
                dt = self.observations[-1].time - self.observations[-2].time
                if dt > 0:
                    dpsi = (
                        self.observations[-1].coherence
                        - self.observations[-2].coherence
                    )
                    self.observations[-1].coherence_derivative = dpsi / dt

    def build_design_matrix(
        self,
        pi_threshold: float = 1.2,
        psi_inv: float = 0.70,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Build linear system for least-squares fitting.

        dΨ/dt = k₁·(Π − Π_th) − k₂·(Ψ − Ψ_inv) − k₃·I_viol + k₄·(E_avail/E_need)

        Rearranged:
        [Π−Π_th, −(Ψ−Ψ_inv), −I_viol, E_avail/E_need] · [k₁, k₂, k₃, k₄]ᵀ = dΨ/dt

        Returns:
            (A, b) where A @ [k1, k2, k3, k4] = b
        """
        # Filter observations with derivatives
        valid_obs = [
            obs for obs in self.observations
            if obs.coherence_derivative is not None
        ]

        if not valid_obs:
            raise ValueError("No valid observations with derivatives")

        n = len(valid_obs)
        A = np.zeros((n, 4))
        b = np.zeros(n)

        for i, obs in enumerate(valid_obs):
            # Build row of A matrix (features)
            A[i, 0] = obs.truth_pressure - pi_threshold  # k₁ term
            A[i, 1] = -(obs.coherence - psi_inv)  # k₂ term (negative because we subtract)
            A[i, 2] = -obs.aura_violations  # k₃ term (negative)
            A[i, 3] = obs.energy_ratio  # k₄ term

            # Build b vector (target: dΨ/dt)
            b[i] = obs.coherence_derivative

        return A, b

    def fit_least_squares(
        self,
        pi_threshold: float = 1.2,
        psi_inv: float = 0.70,
        regularization: float = 0.001,
    ) -> MasterEquationParams:
        """
        Fit master equation parameters using least-squares with optional regularization.

        Returns:
            MasterEquationParams with fitted k₁, k₂, k₃, k₄
        """
        # Estimate derivatives if missing
        self.estimate_derivatives()

        # Build design matrix
        A, b = self.build_design_matrix(pi_threshold, psi_inv)

        # Add L2 regularization to encourage reasonable parameter values
        # Regularization encourages parameters toward 0 (stability)
        if regularization > 0:
            A_reg = np.vstack([A, regularization * np.eye(4)])
            b_reg = np.hstack([b, np.zeros(4)])
            coeffs, residuals, rank, s = np.linalg.lstsq(A_reg, b_reg, rcond=None)
        else:
            coeffs, residuals, rank, s = np.linalg.lstsq(A, b, rcond=None)

        k1, k2, k3, k4 = coeffs

        # Compute RMS error
        predicted = A @ coeffs
        rms_error = np.sqrt(np.mean((predicted - b) ** 2))

        params = MasterEquationParams(
            k1=float(k1),
            k2=float(k2),
            k3=float(k3),
            k4=float(k4),
            pi_threshold=pi_threshold,
            psi_inv=psi_inv,
            rms_error=rms_error,
        )

        self.fit_params = params
        return params

    def predict_coherence_change(
        self,
        pi: float,
        psi: float,
        i_violations: int,
        e_ratio: float,
    ) -> float:
        """
        Predict dΨ/dt using fitted master equation.

        dΨ/dt = k₁·(Π − Π_th) − k₂·(Ψ − Ψ_inv) − k₃·I_violations + k₄·(E_avail/E_need)
        """
        if self.fit_params is None:
            raise ValueError("Must fit parameters first")

        p = self.fit_params
        dPsi = (
            p.k1 * (pi - p.pi_threshold)
            - p.k2 * (psi - p.psi_inv)
            - p.k3 * i_violations
            + p.k4 * e_ratio
        )
        return dPsi

    def validate_predictions(self) -> Dict:
        """
        Validate fitted parameters against observations.

        Returns:
            Dictionary with validation metrics
        """
        if self.fit_params is None:
            raise ValueError("Must fit parameters first")

        valid_obs = [
            obs for obs in self.observations
            if obs.coherence_derivative is not None
        ]

        predictions = []
        targets = []

        for obs in valid_obs:
            pred = self.predict_coherence_change(
                obs.truth_pressure,
                obs.coherence,
                obs.aura_violations,
                obs.energy_ratio,
            )
            predictions.append(pred)
            targets.append(obs.coherence_derivative)

        predictions = np.array(predictions)
        targets = np.array(targets)

        # Metrics
        mse = np.mean((predictions - targets) ** 2)
        rmse = np.sqrt(mse)
        mae = np.mean(np.abs(predictions - targets))
        r2 = 1.0 - (np.sum((targets - predictions) ** 2) /
                    np.sum((targets - np.mean(targets)) ** 2))

        return {
            "num_observations": len(valid_obs),
            "mse": float(mse),
            "rmse": float(rmse),
            "mae": float(mae),
            "r2": float(r2),
            "k1": self.fit_params.k1,
            "k2": self.fit_params.k2,
            "k3": self.fit_params.k3,
            "k4": self.fit_params.k4,
        }

    def report(self) -> str:
        """Generate calibration report."""
        if not self.fit_params:
            return "No fit performed yet."

        p = self.fit_params
        metrics = self.validate_predictions()

        lines = [
            "",
            "╔═══════════════════════════════════════════════════════════╗",
            "║         MASTER EQUATION CALIBRATION REPORT                ║",
            "╚═══════════════════════════════════════════════════════════╝",
            "",
            "dΨ/dt = k₁·(Π − Π_th) − k₂·(Ψ − Ψ_inv) − k₃·I_violations + k₄·(E_avail/E_need)",
            "",
            "─ Fitted Parameters ──────────────────────────────────────────",
            f"k₁ (truth pressure drive):     {p.k1:>10.6f}",
            f"k₂ (identity restoration):     {p.k2:>10.6f}",
            f"k₃ (invariant penalty):        {p.k3:>10.6f}",
            f"k₄ (energy constraint):        {p.k4:>10.6f}",
            "",
            f"Π_threshold (THEORY):          {p.pi_threshold:>10.4f}",
            f"Ψ_inv (AURA floor):            {p.psi_inv:>10.4f}",
            "",
            "─ Validation Metrics ─────────────────────────────────────────",
            f"Observations:                  {metrics['num_observations']:>10d}",
            f"RMSE:                          {metrics['rmse']:>10.6e}",
            f"MAE:                           {metrics['mae']:>10.6e}",
            f"R² (coefficient of determination): {metrics['r2']:>15.6f}",
            "",
            "─ Interpretation ─────────────────────────────────────────────",
        ]

        # Interpret parameters
        if p.k1 > 0:
            lines.append(f"✓ k₁ > 0: System is driven toward higher truth pressure")
        else:
            lines.append(f"✗ k₁ ≤ 0: System opposes higher truth pressure (unusual)")

        if p.k2 > 0:
            lines.append(f"✓ k₂ > 0: System restores coherence back to anchor Ψ_inv")
        else:
            lines.append(f"✗ k₂ ≤ 0: System drifts away from anchor (destabilizing)")

        if p.k3 > 0:
            lines.append(f"✓ k₃ > 0: Invariant violations reduce coherence (as expected)")
        else:
            lines.append(f"✗ k₃ ≤ 0: Invariant violations increase coherence (contradicts AURA)")

        if p.k4 > 0:
            lines.append(f"✓ k₄ > 0: Energy availability increases coherence")
        else:
            lines.append(f"⚠ k₄ ≤ 0: Energy effects are negative (verify biological plausibility)")

        # Overall assessment
        r2_quality = (
            "EXCELLENT (>0.9)" if metrics['r2'] > 0.9 else
            "GOOD (0.7-0.9)" if metrics['r2'] > 0.7 else
            "FAIR (0.5-0.7)" if metrics['r2'] > 0.5 else
            "POOR (<0.5)"
        )

        lines.extend([
            "",
            f"Model fit quality (R²):        {r2_quality}",
            "",
        ])

        return "\n".join(lines)

    def save(self, filepath: str) -> None:
        """Save fitted parameters to JSON."""
        if not self.fit_params:
            raise ValueError("No fit to save")

        data = {
            "fit_parameters": self.fit_params.to_dict(),
            "validation_metrics": self.validate_predictions(),
            "num_observations": len(self.observations),
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)


def example_calibration():
    """Example: calibrate from synthetic CASCADE data."""

    print("MASTER EQUATION CALIBRATION EXAMPLE")
    print("=" * 60)

    # Create synthetic data: generate observations with known k values
    # True parameters (unknown to calibrator)
    k1_true, k2_true, k3_true, k4_true = 0.5, 0.3, 0.1, 0.2

    calibrator = MasterEquationCalibrator()

    # Generate synthetic observations
    np.random.seed(42)
    for t in np.linspace(0, 10, 50):
        pi = 2.0 + 0.3 * np.sin(t)
        psi = 0.7 + 0.1 * np.cos(t)
        i_violations = int(max(0, 2 - 0.3*t))
        e_ratio = 0.8 + 0.2 * np.sin(0.5*t)

        # Compute true derivative using known parameters
        dPsi = (
            k1_true * (pi - 1.2)
            - k2_true * (psi - 0.70)
            - k3_true * i_violations
            + k4_true * e_ratio
        )

        # Add small noise
        dPsi += np.random.normal(0, 0.01)

        calibrator.add_observation(
            time=t,
            truth_pressure=pi,
            coherence=psi,
            aura_violations=i_violations,
            energy_ratio=e_ratio,
            coherence_derivative=dPsi,
        )

    # Fit parameters
    print("Fitting master equation parameters...")
    params = calibrator.fit_least_squares()

    print(calibrator.report())

    print("\nTrue parameters (hidden from calibrator):")
    print(f"  k₁ = {k1_true:.6f}  (fitted: {params.k1:.6f})")
    print(f"  k₂ = {k2_true:.6f}  (fitted: {params.k2:.6f})")
    print(f"  k₃ = {k3_true:.6f}  (fitted: {params.k3:.6f})")
    print(f"  k₄ = {k4_true:.6f}  (fitted: {params.k4:.6f})")


if __name__ == "__main__":
    example_calibration()
