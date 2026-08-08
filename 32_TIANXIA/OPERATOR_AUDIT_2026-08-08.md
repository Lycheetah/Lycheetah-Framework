# TIANXIA operator audit — decision geometry

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
It is not reachable from this session and it remains the right next step. What
follows needs no external data: it measures the classifier's own decision
geometry, which is where a degenerate classifier becomes visible without labels.

---

## What the audit found

### 1. The three-axis diagnostic is mostly a one-axis gate — `[MEASURED]`

```
Wang            4,603    4.6%
Ba             72,816   72.8%
Indeterminate  22,581   22.6%
   └─ of all Ba verdicts, 85.1% decided by the Ren Zheng gate alone
```

`WANG_DAO_OPERATOR.md` presents WD(τ) as a three-axis diagnostic over legitimacy
(minxin), force restraint, and long-cycle stability. For the class covering 73%
of the input space, those three axes decide **15%** of the verdicts. The rest are
settled before the axes are consulted, by a single threshold on a single scalar.

Decision-flip rates confirm it:

```
ren_zheng_score        34.70%
long_cycle_stability   14.60%
force_restraint        14.06%
minxin                 13.80%
```

One input moves the verdict ~2.4× more than any other. The three nominal Wang Dao
axes are near-interchangeable, which follows directly from `WD_score` being their
unweighted mean — no axis can dominate another when all three carry weight 1/3.

This is not necessarily wrong. Mengzi's position is arguably that benevolent
governance *is* the precondition and the rest is commentary, in which case a
dominant Ren Zheng gate is faithful rather than degenerate. But the module
documents a three-axis diagnostic and implements something closer to a gate with
a tiebreak, and that gap should be named by the module rather than discovered by
a reader.

### 2. The two-stage gate shares a term — `[MEASURED]`

```
R(s)     = (welfare_baseline + voice_coverage + force_restraint) / 3
WD_score = (minxin + force_restraint + long_cycle_stability) / 3
```

`force_restraint` enters both stages. The gate is presented as two independent
checks — a Ren Zheng floor, then a Wang Dao threshold — and they are not
independent. Any calibration of θ_r and θ_wang that treats them as separable is
calibrating against a correlation it has not modelled.

### 3. A trajectory can pass the gate while contradicting itself — `[DEFECT]`

`TrajectoryPoint.ren_zheng_score` is a free float. Nothing binds it to a
`GovernanceState`, so nothing checks that a point's declared R is reachable from
that same point's `force_restraint` — even though R is *defined* to include
force_restraint as one of its three terms.

Constructed case, run by the audit:

```
force_restraint               0.0     (total coercion)
max reachable R given F=0     0.6667  (W=V=1 gives (1+1+0)/3)
declared R                    0.95    (unreachable)
Ren Zheng gate passed         True    ← accepted without complaint
```

A polity under total coercion is admitted as Wang-eligible because it declared a
virtue score its own coercion makes arithmetically impossible. The fix is to
derive R from a `GovernanceState` rather than accept it as an input.

Held open as a strict xfail in `tests/test_tianxia_operators.py`, so when the fix
lands the suite fails and the change must be acknowledged rather than absorbed
silently — the same pattern the corpus already uses for the CASCADE
predictability failure.

### 4. Both thresholds are uncalibrated and the verdict moves with them — `[SCAFFOLD]`

```
 θ_wang   θ_ba     Wang       Ba    Indet
   0.70   0.40    4.6%   72.7%   22.7%   ← current
   0.60   0.40   10.6%   72.7%   16.7%
   0.80   0.40    1.2%   72.7%   26.0%
```

Across a plausible range for a value nobody has calibrated, the Wang fraction
moves by roughly 9×. θ_wang and θ_ba are both marked SCAFFOLD pending E-1-H,
which has not been executed. θ_r = 0.618 is φ−1 — chosen for its elegance, not
fitted to anything.

For reference, the other operator thresholds admit:

```
Five-Fold Hexie H₅ ≥ 0.65     35.0% of input space
Ren Zheng R(s) ≥ 0.618        24.9% of input space
```

---

## What this audit cannot say

**Nothing about whether Wang/Ba corresponds to real governance.** Every number
here describes the classifier's behaviour on uniform random input, which is not a
distribution any real polity is drawn from. A classifier can have perfect internal
geometry and track nothing — that is precisely what happened to the AURA lens on
2026-08-07, and no amount of internal measurement caught it.

Calling any of this evidence for the operators would repeat the exact error this
audit exists to avoid.

---

## Also closed today

TIANXIA had **zero pytest coverage** — nine operator implementations, a 274-test
suite, and no overlap. Self-tests lived in `__main__` blocks, so they ran only by
hand, and three of them used bare `assert False`, which `python -O` strips
entirely. The README's "all self-tests passing" was true and ungated.

`tests/test_tianxia_operators.py` now covers all nine modules, the core arithmetic
of Ren Zheng / Wang Dao / Five-Fold Hexie, the measured decision geometry as
characterisation tests, and the gate defect as a strict xfail. Suite: 274 → **295
passing, 2 xfailed**.

---

## What would actually move this module

Not v0.4. Not another operator.

1. **Fix the gate consistency defect** — derive R from `GovernanceState`.
2. **Decide what WD(τ) is.** Either weight the three axes so they carry different
   force, or document it honestly as a Ren Zheng gate with a tiebreak.
3. **Score the operators against external governance data.** V-Dem publishes
   near-direct analogues in [0,1] for all three Ren Zheng components:
   `voice_coverage` ↔ participatory component index, `force_restraint` ↔ physical
   violence index, `welfare_baseline` ↔ egalitarian component. Polity5 supplies
   `long_cycle_stability` as regime durability. This is the filter-3 step, and it
   is the only thing that can promote any TIANXIA claim above SCAFFOLD.
4. Only then reconsider the thresholds, with something to calibrate against.

The end-2028 falsifier in `POSITION_PAPER_v0.1.md` stands unchanged: no
substantive engagement from within the tradition by 31 December 2028 and the
primary-partnership claim falls. Step 3 is what would make that engagement worth
someone's time.
