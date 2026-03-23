# MASTER EQUATION CALIBRATION
## From Theory to Empirical k₁–k₄ Values
**Status:** Ready for real CASCADE data fitting
**Method:** Bayesian optimization + sensitivity analysis
**Date:** March 21, 2026

---

## THE MASTER EQUATION (Current)

```
dΨ/dt = k₁·(Π − Π_th)           [CASCADE drive: truth pressure]
        − k₂·(Ψ − Ψ_inv)         [AURA pull: return to stable minimum]
        − k₃·I_violations        [Invariant penalty: resist violating AURA]
        + k₄·(E_avail/E_need)    [EARNED LIGHT: energy budget allows change]

where:
  Ψ ∈ [0, 1]                 [System coherence (0=fragmented, 1=perfect)]
  Π = (E·P)/S                [Truth pressure formula]
  Π_th ≈ 1.2                 [Critical reorganization threshold]
  Ψ_inv ≈ 0.70               [AURA minimum coherence floor]
  I_violations ∈ {0,...,7}   [AURA invariants broken]
  k₁, k₂, k₃, k₄             [Unknown coupling constants — CALIBRATE THESE]
```

---

## THE UNKNOWNS

### k₁ — CASCADE Pressure Coefficient
**What it controls:** How fast truth pressure drives reorganization

Current estimate: k₁ ≈ 0.5 (guess)
- If k₁ too low: Systems reorganize too slowly (theory predicts no change)
- If k₁ too high: Systems reorganize instantly (unrealistic)

**To calibrate:** Measure how fast Ψ changes when Π exceeds Π_th in real systems
- Organizational CASCADE: Track meeting topics, decision changes over time
- Language: Track word usage changes when new terms arrive (e-commerce → "cloud")
- Market: Track price reorganization speed after news shocks

### k₂ — AURA Stability Coefficient
**What it controls:** How strongly the system returns to stable state

Current estimate: k₂ ≈ 0.3 (guess)
- If k₂ too low: System doesn't stabilize (becomes unstable)
- If k₂ too high: System too resistant to change (frozen)

**To calibrate:** Measure relaxation time after reorganization
- How long until system reaches new stable point after cascade?
- Organizations: Measure time to new culture formation after major change
- Ecosystems: Measure recovery time after intervention

### k₃ — Invariant Penalty Coefficient
**What it controls:** How much violating AURA constraints resists change

Current estimate: k₃ ≈ 0.2 (guess)
- If k₃ too low: Invariants don't matter (organization becomes unethical)
- If k₃ too high: Invariants prevent all change (system freezes)

**To calibrate:** Measure how much systems slow down when approaching invariant violations
- Organizations: Track how ethical constraints slow decisions
- AI systems: Measure how safety constraints affect performance
- Humans: Measure how values slow behavior change

### k₄ — Energy Budget Coefficient
**What it controls:** How much available energy enables change

Current estimate: k₄ ≈ 0.1 (guess)
- If k₄ too low: Energy doesn't matter (change happens anyway)
- If k₄ too high: Change stops without energy (can't happen)

**To calibrate:** Measure how resource availability affects reorganization
- Organizations: Does funding speed/slow organizational change?
- Humans: Does sleep/nutrition affect belief change capacity?
- Ecosystems: Does nutrient availability affect species turnover?

---

## CALIBRATION DATA SOURCES

### Real CASCADE Data (Ready to Use)
**Location:** `.agent_state/cascade_real_results.json` (committed)

```
6 experiments × 1000 cascades each = 6000 data points
- Experiment 1: Organizational belief cascades (company pivots)
- Experiment 2: Market price reorganizations (shock responses)
- Experiment 3: Team decision cascades (group dynamics)
- Experiment 4: Language borrowing cascades (new terms)
- Experiment 5: Ecosystem species shifts (invasive species)
- Experiment 6: Learning reorganizations (aha! moments)

Each cascade records:
  - Initial Ψ (coherence)
  - Π measured (evidence, prior, strain)
  - Time to reorganization
  - Final Ψ (new coherence)
  - Invariant violations observed
  - Energy/resources available
```

### How to Extract k₁–k₄

```
For each cascade:
  1. Measure dΨ/dt (rate of coherence change over time)
  2. Observe (Π − Π_th) magnitude
  3. Note (Ψ − Ψ_inv) value
  4. Count I_violations (how many AURA invariants broken)
  5. Estimate E_avail/E_need (resources available vs. needed)

Then: Fit master equation to measured dΨ/dt

  dΨ/dt_measured ≈ k₁·(Π − Π_th) − k₂·(Ψ − Ψ_inv) − k₃·I + k₄·(E/En)

Solve for k₁, k₂, k₃, k₄ using least-squares optimization
```

---

## BAYESIAN CALIBRATION METHOD

### Step 1: Prior Distributions (Current Guesses)
```
k₁ ~ Normal(μ=0.5, σ=0.3)    [CASCADE pressure, range 0-1]
k₂ ~ Normal(μ=0.3, σ=0.2)    [AURA stability, range 0-1]
k₃ ~ Normal(μ=0.2, σ=0.15)   [Invariant penalty, range 0-0.7]
k₄ ~ Normal(μ=0.1, σ=0.1)    [Energy coefficient, range 0-0.3]
```

### Step 2: Likelihood Function
```
L(k₁, k₂, k₃, k₄ | data) =

  Product over all cascades of:
    P(observed dΨ/dt | predicted dΨ/dt from master equation)

  Using Gaussian error model:
    error ~ Normal(μ=0, σ=0.05)  [5% measurement noise]
```

### Step 3: Posterior Inference
```
Use Markov Chain Monte Carlo (MCMC) to sample from:
  P(k₁, k₂, k₃, k₄ | cascade_data)

Output: Posterior distributions (mean ± credible interval for each k)
```

### Step 4: Validation
```
Hold out 20% of cascades (test set)
- Train on 80% of data (fit k₁–k₄)
- Test on 20% held-out data
- Measure prediction error (RMSE)
- Iterate if error > 10%
```

---

## SENSITIVITY ANALYSIS

### Partial Derivatives (What affects change most?)

```
∂Ψ/∂k₁ = (Π − Π_th) / dt        [sensitivity to CASCADE]
∂Ψ/∂k₂ = −(Ψ − Ψ_inv) / dt      [sensitivity to AURA]
∂Ψ/∂k₃ = −I_violations / dt     [sensitivity to Invariants]
∂Ψ/∂k₄ = (E_avail/E_need) / dt  [sensitivity to Energy]
```

**Interpretation:**
- If ∂Ψ/∂k₁ >> others: CASCADE pressure dominates (k₁ is load-bearing)
- If ∂Ψ/∂k₂ >> others: Stability matters more than pressure
- If ∂Ψ/∂k₃ >> others: Invariants are key constraint
- If ∂Ψ/∂k₄ >> others: Energy availability critical

**Prediction:** k₁ will be largest (CASCADE is primary driver)

---

## EXPECTED RESULTS (Pre-Calibration Guess)

### Domain 1: Organizations
```
Predicted k₁ ≈ 0.6  (organizations respond to pressure, but resist)
Predicted k₂ ≈ 0.25 (organizations stabilize slowly, inertia high)
Predicted k₃ ≈ 0.15 (ethics matter, but profit-driven systems ignore it)
Predicted k₄ ≈ 0.2  (well-funded organizations change faster)
```

### Domain 2: Languages
```
Predicted k₁ ≈ 0.3  (languages resist pressure; change is slow)
Predicted k₂ ≈ 0.5  (languages stabilize fast once reorganized)
Predicted k₃ ≈ 0.1  (gram invariants are hard, don't resist much)
Predicted k₄ ≈ 0.05 (language change doesn't depend on energy)
```

### Domain 3: Markets
```
Predicted k₁ ≈ 0.9  (markets respond instantly to pressure)
Predicted k₂ ≈ 0.2  (prices don't return to equilibrium easily)
Predicted k₃ ≈ 0.3  (regulation adds drag; slows reorganization)
Predicted k₄ ≈ 0.15 (liquidity matters; affects response speed)
```

### Domain 4: Ecosystems
```
Predicted k₁ ≈ 0.4  (ecosystems resist but eventually reorganize)
Predicted k₂ ≈ 0.35 (recovery is slow; new equilibrium takes years)
Predicted k₃ ≈ 0.25 (biodiversity adds constraints; slows reorganization)
Predicted k₄ ≈ 0.05 (energy (nutrients) doesn't directly drive species change)
```

---

## IMPLEMENTATION

### Python Code Structure

```python
import numpy as np
from scipy.optimize import least_squares
from emcee import EnsembleSampler  # Bayesian MCMC

class MasterEquationCalibrator:

    def __init__(self, cascade_data):
        self.data = cascade_data
        self.k_params = {'k1': 0.5, 'k2': 0.3, 'k3': 0.2, 'k4': 0.1}

    def master_equation(self, psi, k1, k2, k3, k4, pi, psi_inv, i_violations, e_ratio):
        """Compute dΨ/dt from master equation"""
        dpsidt = (k1 * (pi - 1.2)
                  - k2 * (psi - psi_inv)
                  - k3 * i_violations
                  + k4 * e_ratio)
        return dpsidt

    def likelihood(self, k_values):
        """Bayesian likelihood: how well do k-values fit data?"""
        k1, k2, k3, k4 = k_values
        predictions = []

        for cascade in self.data:
            pred = self.master_equation(
                cascade['psi'], k1, k2, k3, k4,
                cascade['pi'], cascade['psi_inv'],
                cascade['i_violations'], cascade['e_ratio']
            )
            predictions.append(pred)

        error = np.array(predictions) - np.array([c['measured_dpsidt'] for c in self.data])
        log_likelihood = -0.5 * np.sum((error / 0.05) ** 2)  # Gaussian error
        return log_likelihood

    def calibrate(self):
        """Run Bayesian MCMC to fit k1–k4"""
        sampler = EnsembleSampler(
            nwalkers=32,
            ndim=4,
            lnpostfn=self.likelihood,
            args=[]
        )

        # Run 1000 iterations, discard first 500 (burn-in)
        sampler.run_mcmc(p0=[0.5, 0.3, 0.2, 0.1], N=1000)

        # Extract posterior means and credible intervals
        k1_posterior = sampler.chain[:, 500:, 0].flatten()
        k2_posterior = sampler.chain[:, 500:, 1].flatten()
        k3_posterior = sampler.chain[:, 500:, 2].flatten()
        k4_posterior = sampler.chain[:, 500:, 3].flatten()

        return {
            'k1': (np.mean(k1_posterior), np.std(k1_posterior)),
            'k2': (np.mean(k2_posterior), np.std(k2_posterior)),
            'k3': (np.mean(k3_posterior), np.std(k3_posterior)),
            'k4': (np.mean(k4_posterior), np.std(k4_posterior)),
        }

# Usage:
calibrator = MasterEquationCalibrator(cascade_real_results)
k_calibrated = calibrator.calibrate()
print(f"k1 = {k_calibrated['k1'][0]:.3f} ± {k_calibrated['k1'][1]:.3f}")
```

---

## NEXT STEPS

1. **Load CASCADE data** (6000 cascades committed)
2. **Extract features** (Π, Ψ, violations, energy for each)
3. **Run calibration** (MCMC, 2-4 hours on laptop)
4. **Validate** (hold-out test set, measure RMSE)
5. **Report** (k₁–k₄ values + credible intervals)
6. **Publish** (update master equation with real parameters)
7. **Apply** (use calibrated equation for predictions)

---

## EXPECTED TIMELINE

- Data extraction: 1-2 hours
- MCMC calibration: 2-4 hours
- Validation: 1 hour
- Total: 1 day of computation

**Result:** Master equation with empirically measured k₁–k₄ values

---

**See also:**
- `cascade_real_results.json` — Real CASCADE data
- `MASTER_EQUATION_COMPONENT.md` — Theoretical derivation
- `PI_DERIVATION.md` — Π formula background

READY FOR REAL DATA. Let's find the true parameters.
