# TIANXIA operator audit — decision geometry, and one defect closed

**Status: MEASURED, 2026-08-08.** Reproduce with one command:

```bash
python3 32_TIANXIA/implementations/operator_audit.py --n 100000
```

The module had not been worked since v0.3 in May 2026. **2026-08-07 happened in
between**, and its lesson had not reached here.

That finding was structural, not local: *constructs defined from theory,
illustrated with examples written to fit, and validated against those examples*
scored ROC-AUC 0.940 internally and at chance externally. `wang_dao.py` is built
that way. It is a three-class classifier whose only inputs to date have been
`_make_wang_trajectory()` and `_make_ba_trajectory()` — fixtures written by the
same author, with the expected verdict already inside them.

External governance data would settle whether the operators track anything real.
It remains the right next step and is **not** claimed here. What follows needs no
external data: it measures the classifier's own decision geometry, which is where
a degenerate classifier becomes visible without labels.

---

## 0. A third of the state space was impossible — `[MEASURED]`

`R(s) = (W + V + F)/3` with `W, V ∈ [0,1]`, so force restraint alone pins R:

```
R_min = F/3          R_max = (2 + F)/3          width = 2/3 for every F
```

Nothing enforced that. `TrajectoryPoint.ren_zheng_score` was a free float bound
to no `GovernanceState`, so a trajectory could declare an R its own coercion made
arithmetically impossible.

```
of a naive uniform [0,1]^4 sample, 66.6% is reachable governance
```

The first run of this audit sampled the naive cube, so **a third of its input
space was states no governance could occupy.** Both the audit and the operator
are corrected below; the original numbers are kept beside the new ones because
the correction strengthens the main finding rather than softening it.

---

## 1. The three-axis diagnostic is mostly a one-axis gate — `[MEASURED]`

Over the **reachable** space, n = 100,000:

```
Wang            5,585    5.6%
Ba             74,101   74.1%
Indeterminate  20,314   20.3%
   └─ of all Ba verdicts, 91.5% decided by the Ren Zheng gate alone
                          (first run, naive cube: 85.1%)
```

`WANG_DAO_OPERATOR.md` presents WD(τ) as a three-axis diagnostic over legitimacy
(minxin), force restraint, and long-cycle stability. For the class covering 74%
of the reachable space, those three axes decide **8.5%** of the verdicts. The
rest are settled before the axes are consulted, by one threshold on one scalar.

Decision-flip rates agree:

```
ren_zheng_score        31.36%
long_cycle_stability   12.76%
minxin                 12.16%
force_restraint        11.70%
```

One input moves the verdict ~2.5× more than any other. The three nominal Wang Dao
axes are near-interchangeable, which follows directly from `WD_score` being their
unweighted mean — no axis can dominate when all three carry weight 1/3.

This is not necessarily wrong. Mengzi's position is arguably that benevolent
governance *is* the precondition and the rest is commentary, in which case a
dominant Ren Zheng gate is faithful rather than degenerate. But the module
documents a three-axis diagnostic and implements a gate with a tiebreak, and that
gap should be named by the module rather than discovered by a reader.

**Open decision for the author:** either weight the axes so they carry different
force, or restate WD(τ) honestly as a Ren Zheng gate with a tiebreak. Both are
defensible; the current mismatch is not.

---

## 2. The two-stage gate shares a term — `[MEASURED]`

```
R(s)     = (welfare_baseline + voice_coverage + force_restraint) / 3
WD_score = (minxin + force_restraint + long_cycle_stability) / 3
```

`force_restraint` enters both stages. The gate is presented as two independent
checks and they are not. Any calibration of θ_r and θ_wang treating them as
separable is calibrating against a correlation it has not modelled.

---

## 3. Self-contradicting trajectories were accepted — `[FIXED 2026-08-08]`

The defect, as found:

```
force_restraint               0.0     (total coercion)
max reachable R given F=0     0.6667
declared R                    0.95    (impossible)
Ren Zheng gate passed         True    ← accepted without complaint
```

A polity under total coercion was admitted as Wang-eligible because it declared a
virtue score its own coercion made unreachable.

**Repair:** `ren_zheng.reachable_r_bounds(F)` returns the admissible band, and
`TrajectoryPoint.__post_init__` now rejects any R outside it. Every pre-existing
fixture in the module satisfies the constraint — the Wang trajectory at F=0.89
admits R ∈ [0.297, 0.963] and declares 0.83; the Ba trajectory at F=0.20 admits
R ∈ [0.067, 0.733] and declares 0.50. Only impossible states are rejected.

The audit's probe now asserts the rejection and is kept as a live regression,
because the defect is absent only for as long as the constraint stays in place.

```
4. GATE CONSISTENCY PROBE
   ✓ REJECTED at construction — the band check holds
     ren_zheng_score=0.9500 is unreachable at force_restraint=0.0000
```

---

## 4. Both thresholds are uncalibrated and the verdict moves with them — `[SCAFFOLD]`

```
 θ_wang   θ_ba     Wang       Ba    Indet
   0.70   0.40    5.4%   74.2%   20.3%   ← current
   0.60   0.40   11.8%   74.2%   14.0%
   0.80   0.40    1.6%   74.2%   24.2%
   0.70   0.30    5.4%   70.4%   24.2%
   0.70   0.50    5.4%   80.7%   13.9%
```

Across a plausible range for a value nobody has calibrated, the Wang fraction
moves by roughly 7×. θ_wang and θ_ba are both SCAFFOLD pending E-1-H, which has
not been executed. θ_r = 0.618 is φ−1 — chosen for elegance, fitted to nothing.

Other operator thresholds, for reference:

```
Five-Fold Hexie H₅ ≥ 0.65     35.0% of input space
Ren Zheng R(s) ≥ 0.618        24.9% of input space
```

---

## What this audit cannot say

**Nothing about whether Wang/Ba corresponds to real governance.** Every number
here describes behaviour on uniform random input over a reachable space, which is
not a distribution any real polity is drawn from. A classifier can have clean
internal geometry and track nothing — precisely what happened to the AURA lens on
2026-08-07, where no amount of internal measurement caught it.

Quoting any of this as evidence *for* the operators would repeat the exact error
the audit exists to avoid.

---

## Also closed today

TIANXIA had **zero pytest coverage** — nine operator implementations, a 274-test
suite, no overlap. Self-tests lived in `__main__` blocks so they ran only by hand,
and three used bare `assert False`, which `python -O` strips entirely. The
README's "all self-tests passing" was true and ungated — the same defect class as
the `lycheetah-guard` entry point.

`tests/test_tianxia_operators.py` now covers all nine modules, the core arithmetic
of Ren Zheng / Wang Dao / Five-Fold Hexie, the measured geometry as
characterisation tests, and the reachable-band constraint as a regression.

---

## What would actually move this module

Not v0.4. Not another operator.

1. ~~**Fix the gate consistency defect.**~~ **Done** — §3 above.
2. **Decide what WD(τ) is.** Weight the three axes so they carry different force,
   or document it as a Ren Zheng gate with a tiebreak. Author's call; the
   mismatch is the problem, not either resolution.
3. **Score the operators against external governance data.** V-Dem publishes
   near-direct analogues in [0,1] for all three Ren Zheng components:
   `voice_coverage` ↔ participatory component index, `force_restraint` ↔ physical
   violence index, `welfare_baseline` ↔ egalitarian component. Polity5 supplies
   `long_cycle_stability` as regime durability. This is the filter-3 step and the
   only thing that can promote any TIANXIA claim above SCAFFOLD.
4. Only then reconsider the thresholds, with something to calibrate against.

The end-2028 falsifier in `POSITION_PAPER_v0.1.md` stands unchanged: no
substantive engagement from within the tradition by 31 December 2028 and the
primary-partnership claim falls. Step 3 is what would make that engagement worth
a serious reader's time.
