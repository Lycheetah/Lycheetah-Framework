# Sheaf certificates and factorial work accounting

Author: Mackenzie Conor James Clark / Lycheetah Framework.
Knowledge review: Caelorynth / Codex, 18 October 2026.
Status: local research note. Code observations and analytic derivations; no new
numerical runs, empirical result or theorem of agent truth is claimed.

## Decision for the next implementation batch

Keep the explicit sheaf operators and full factorial design. Tighten their claim
and numerical contracts before using their results to justify a memory governor.

| Priority | Finding | Required successor evidence |
|---|---|---|
| 1 | Nonidentity holonomy can preserve a fixed direction | State the common-fixed-subspace condition; retain the reflection counterexample below |
| 1 | Rank and pseudoinverse apply different singular-value cutoffs | One declared cutoff per operator, with consistent rank, projection and spectral interpretation |
| 2 | Lookahead can change work after service duration was scheduled | Per-job planned work, actual work, elapsed capacity and discrepancy |
| Interpretation | The local identity-map residual reduces to parent-vector variance | Describe the certificate's added information without claiming a new natural law |

These are acceptance conditions for a successor. They are not a claim that a
successor has been built or that its checks have run.

## Reviewed source identity

Revision: `d4a65ff64efa0a512c5c07ca64f6ec76242dd775`.

| Source at that revision | SHA-256 |
|---|---|
| `12_IMPLEMENTATIONS/core/sheaf_cohomology_factorial.py` | `6db52350ecba35f486cb5c9556bf560837660f578c0badf13f97d8fd0e8b0a58` |
| `tests/test_sheaf_cohomology_factorial.py` | `c73315fbdb3a6268f7ecb23e8c767b3d3c5483ef159c23abdaca459691190812` |

Existing tests were read, not executed in this review. The source revision and
hashes identify the reviewed object even if another seat changes the working tree.
The earlier experiment records remain governed by
[their reproduction note](REPRODUCING_RECORDED_RUNS.md).

## 1. The precise global-section condition

For a finite graph with the declared stalk inner products, put
`D = delta^0` and `L0 = D.T @ D`. The degree-zero identities are
`H0 = ker(D) = ker(L0)`. Relative cohomology uses the subcomplex that vanishes on
the chosen boundary. These are established sheaf-theoretic constructions, not
new Lycheetah results. See Hansen and Ghrist, sections 2.2.2 and 3.2,
[Toward a Spectral Theory of Cellular Sheaves](https://arxiv.org/abs/1808.01513).

**Derived here from the reviewed edge equations:** assume a connected graph with
equal stalk dimension `d` and invertible edge restriction maps. Choose a root and
a spanning tree. The root value uniquely determines all other vertex values by
transport along that tree. Every remaining edge imposes a return condition
`T_j v = v` on the root value. Therefore

```text
H0 is isomorphic to the intersection of ker(T_j - I).
```

A tree has no remaining-edge conditions, so `dim H0 = d`. With equal vertex and
edge stalk dimensions, rank-nullity also gives `dim H1 = 0` on a connected tree.
For multiple connected components, sum over their root spaces instead.

A cycle transformation being different from identity does not say its fixed
subspace is zero. The stronger condition needed for `dim H0 = 0` is that all
cycle transports have no common nonzero fixed vector. Since `L0` is positive
semidefinite, it is positive definite precisely when this kernel is zero.

### Analytic counterexample

Use the reviewed four-vertex graph with edges `0->1`, `0->2`, `1->3`, `2->3`.
Give every stalk dimension two. Use identity restrictions except a tail twist
`T = diag(1, -1)` on edge `2->3`.

The first three edge equations imply `x0 = x1 = x2 = x3 = v`. The last requires
`T v = v`, which holds exactly when `v = (a, 0)`. Hence:

```text
dim H0 = 1
dim H1 = 1        (four edges and four vertices imply equal C0/C1 dimensions)
lambda_min(L0) = 0
```

`T` is orthogonal and nonidentity. This disproves the module introduction's
unqualified nontrivial-holonomy claim. Its existing `-I` fixture has no nonzero
fixed vector and remains a valid special case. The field
`holonomy_obstructed = (dim_h0 == 0)` currently detects complete elimination of
nonzero global sections, not every reduction in their dimension.

## 2. A numerical certificate needs a shared cutoff

**Observed:** the reviewed source estimates rank using `s > 1e-9`, but calls
`np.linalg.pinv(..., rcond=1e-9)`. NumPy defines that `rcond` cutoff relative to
the largest singular value. Equal numeric arguments therefore need not select
equal subspaces. See the primary documentation for
[pinv](https://numpy.org/doc/stable/reference/generated/numpy.linalg.pinv.html).

### Analytic scale counterexample

The constructor accepts general square maps, including the same invertible map
`R = diag(1e12, 1)` at both ends of one edge. Then `D = [-R, R]` has singular
values `sqrt(2)*1e12` and `sqrt(2)`.

The absolute rank cutoff keeps both. The pseudoinverse cutoff discards the
second, since its relative threshold is about 1414. For `z = (0, 1)`, that
truncated projection leaves a residual of norm one, despite `D` being onto.
The exact cohomology is `H1 = 0`; the residual is numerical truncation, not an
intrinsic obstruction. This is an analytic prediction, not a reported runtime
probe. The fixture lies outside an orthogonal-only theorem, but inside the
constructor's currently accepted input class.

**Proposed contract:** declare `epsilon_D = max(atol, rtol * sigma_max(D))` and
use one SVD mask for that operator's rank and truncated pseudoinverse. An interior
operator `D_I` needs its own recorded spectrum and cutoff under the same policy.
Relate retained eigenvalues of `D.T @ D` to squared singular values, allowing for
floating-point error in forming the normal matrix. Reusing a linear threshold
unchanged on squared quantities does not establish consistency.

Return the cutoff, numerical rank, retained/discarded singular values or margins,
and projection residuals. Distinguish a numerical result from an exact algebraic
statement. NumPy's [matrix-rank documentation](https://numpy.org/doc/stable/reference/generated/numpy.linalg.matrix_rank.html)
explains the role of floating-point and data uncertainty in rank thresholds.
If a theorem requires orthogonal maps, name or validate that input condition.

## 3. What the local relative certificate adds

**Observed:** `local_sheaf_certificate` builds a parent-child star with identity
maps and pins parent vectors `p_1, ..., p_k`. Its free child vector `z` solves

```text
min_z sum_i ||z - p_i||^2.
```

**Derived here:** differentiating yields `z = mean(p_i)`, and the squared
obstruction is `sum_i ||p_i - mean(p_i)||^2`. For one-hot paradigm vectors with
encoded-basis counts `n_j`, this becomes

```text
obstruction^2 = k - sum_j(n_j^2) / k.
```

For two distinct one-hot parents the obstruction norm is one; for two equal
parents it is zero. A positive threshold also makes scale and encoding relevant.

The certificate gives an explicit residual, minimizer and consistency equation.
For the binary `a`/`b` fixtures with `d >= 2`, its positivity has the same
parent-label disagreement condition as the earlier policy. This equivalence needs
the encoding assumption: the code hashes other labels into basis positions, so
distinct strings can collide. Encoded-basis counts are therefore not automatically
counts of distinct semantic claims.

**Correction, 18 October 2026:** the earlier version of this note said that `a`
and `b` coincide at `d = 1`. That was a source-reading error. The implementation
maps `a` to `+1` and every other label to `-1` in one dimension. Thus `a` and `b`
remain distinct there, while distinct non-`a` labels coincide. The one-hot count
formula above applies to its stated `d >= 2` encoding, not this signed case.
The decision to suspend adjudication when the residual is positive remains an
application policy. Neither the encoding nor that rule follows from topology alone.

## 4. Eight cells also need eight valid execution contracts

Three binary factors produce eight combinations. The design can report balanced
main effects and interactions when all intended cells are present. This standard
design structure is described in the NIST handbook's
[two-level full factorial designs](https://www.itl.nist.gov/div898/handbook/pri/section3/pri3331.htm).

The reviewed Yates formulas use contrasts divided by four, consistent with
high-minus-low effects averaged over the other two factors. Path-edge differences
sum to the endpoint difference algebraically; that identity alone supplies no
independent validation of physical work accounting or causal interpretation.

**Observed in `simulate_orthogonal`:** `start()` probes the store at service
start to estimate `current_work` and schedule completion. `complete()` recomputes
`actual_work` on the live store. In lookahead cells, intervening arrivals can alter
the candidate set and operation count. There is no equality check between those
two work values and no per-job capacity receipt in the returned rows.

Thus the label `work_coupled` does not by itself establish that each job paid its
completion-time work. This is a missing invariant, not a measured failure count.
The FIFO branch also hides every other pending job, so the queue-scope and
lookahead factors primarily intervene on CASCADE; comparisons must state that.

### Successor receipt contract

For each service, expose:

- start/finish time, input snapshot identity, and declared timing policy;
- planned work, completion-time work and the processing capacity actually spent;
- the residual `actual_work - processing_rate * busy_duration`, including in-flight
  partial work at the observation horizon;
- actual factor treatment, trace identity and retained arrivals.

For a true paid-work claim, define a causal service rule that pays changes in
required work, or explicitly classify an oracle/noncausal sensitivity arm. If
scheduled work remains an estimate, label it estimated-work service and expose
its prediction error.

**Decision for the immediate successor:** preserve the eight combinations as
descriptive sensitivity conditions, add the work receipts, and label estimated
service honestly. Reserve an equal-paid-work interpretation for conditions whose
execution contract actually enforces it. A causal incremental-service model is a
later extension, not an assumption to hide inside the current factor names.

Match every cell and policy by explicit condition keys, not only by list position.
Record raw outcomes and interactions per matched block. Seed/topology variation
and uncertainty claims require their own scope; a balanced cube alone does not
establish empirical generalization.

## Scope of this review

The useful advance is a more explicit, inspectable model. Agreement of encoded
vectors is not factual correctness of claims. A boundary-pinned residual is not
intrinsic cycle obstruction, and neither establishes a general glass law.

The current batch ends with this source-linked review and an implementation
handoff. Numerical reproduction, successor integration and publication are
separate evidence states. Historical raw data and manifests are unchanged.
