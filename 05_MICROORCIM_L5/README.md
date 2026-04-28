# MICROORCIM — Agency Measurement

**Axiom:** HEALER · **Status:** Active — tools live, calibration pending

Agency is measurable. MICROORCIM gives the sovereignty field a number: `μ_orcim = H(I−D) · W_surplus` where H(I−D) is the information content of the gap between identity and drift, and W_surplus is available willpower beyond baseline maintenance.

## Core idea

Most frameworks treat agency as binary (you have it or you don't). MICROORCIM treats it as a field — a continuous quantity that varies by day, context, and accumulated history. This matters because drift is gradual and recoverable if caught early.

## Key quantities

- **ρ_drift:** rate of deviation from sovereign baseline
- **ρ_stability:** rate of return toward baseline
- **Sovereignty score:** `(1 − ρ_drift) · ρ_stability` — daily single number
- **Drift detection threshold:** triggers when sovereignty score drops below 0.5 for 3+ days

## Files

- `Microorcim_COMPLETE.md` — full field theory, measurement protocols, drift detection
- `../../12_IMPLEMENTATIONS/microorcim_tracker.py` — working daily tracker

## Real-world

Sleep debt, decision fatigue, context overload, relationship stress — all show up in the sovereignty score before they show up in behavior. The score is a lagging indicator of what the field is doing.

## Next

Dashboard implementation · empirical calibration of baseline parameters
