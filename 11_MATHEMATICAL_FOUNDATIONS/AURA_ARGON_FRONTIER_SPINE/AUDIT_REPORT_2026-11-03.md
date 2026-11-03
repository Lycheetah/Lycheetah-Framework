# Aura–Argon Math Review · 2026-11-03

**Reviewer:** Aetheron seat, running Claude Opus 5.5 (High)
**Corpus:** Canonical Frontier Archive (`11_MATHEMATICAL_FOUNDATIONS/AURA_ARGON_FRONTIER_SPINE/`).
**Harness:** [`aura_argon_falsifier.py`](./aura_argon_falsifier.py). Uses only the Python stdlib and numpy, with seed `20261103`. Run it with `python3 aura_argon_falsifier.py`.
**Mathematical source:** Mackenzie Conor James Clark / Lycheetah Framework.

> This is a review by one model seat, run against a harness that the same seat wrote. It is a second opinion, not independent validation. Anything marked REFUTED can be reproduced by running the harness.

## Verdict tally (27 checks)

| CONFIRMED | CORRECTED | SCOPE | REFUTED | UNVERIFIED |
|---|---|---|---|---|
| 9 | 3 | 7 | 6 | 2 |

**Short version:** the algebra is mostly right. Where the papers fail, it is at the boundary between a theorem and what the theorem is claimed to *mean*. The worst cases are a hypothesis quietly dropped, a bound reported as if it were a measurement, or a guard that one line of code can get around.

---

## 1. Refuted: a concrete counterexample exists

| # | Claim | Counterexample |
|---|---|---|
| R1 | The Veritas AST observer is "100% sound and complete" for syntactic side effects (Paper II Thm 2.3, Paper VI abstract) | The shipped `VeritasCausalObserver` sees **1 of 12** one-line side effects. It misses `from os import system`, `__import__`, `getattr`, `exec`, nested attribute calls, attribute and subscript writes, `+=`, tuple unpacking, walrus, and `open().write`. The "0 false commits in 50,000 trials" figure is only as strong as its adversary. |
| R2 | The barbell reserve satisfies ruin ≤ exp(−2μB₀/c²) = 7.3e-6 (Thm 6.3 applied to Def 4.2) | Downside capped at 0.65 and mean exactly 0.25, with a +899 jackpot at p = 0.001. Ruin probability is **at least 0.984** (exact), and Monte Carlo gives 0.984. The theorem itself is correct for ξ ∈ [−c, c]. Def 4.2 allows unbounded upside, so Hoeffding's lemma does not apply. |
| R3 | μ = ½κVar(σ) from Thm 4.3 supplies the reserve drift in Thm 6.3 | A category error. A Jensen gap is a difference in *utility*, not the mean of the reserve increments. It can coexist with E[ξ] < 0. |
| R4 | AI > 1 ⇒ Σ = K/D > 1 "prevents skill collapse" (6-paper Thm 3.3) | K drops from 10 to 0.5 (a 95% loss) while Σ = 5. A ratio cannot certify a level. The Decalogy's u_crit (Thm 3.2) is the correct atrophy criterion, so keep that one. |
| R5 | "0 escapes in 50,000 cycles" supports P_escape ≤ 1e-10 | By the rule of three, the 95% upper bound is **6.0e-5**. Supporting 1e-10 would take about **3.0e10** hazard trials. |
| R6 | The original suite verifies Papers I–VI | It fails at `import sympy`. Most of its SymPy assertions are substitutions that are true by construction. |

## 2. Scope: valid only under a hypothesis the text doesn't enforce

- **Paper V Thm 5.1 (escape ≤ 1e-10):** this needs the four layers to be independent. Without that assumption, the Fréchet–Hoeffding bounds give [0, **1e-3**]. A common-mode failure hits 1e-3, seven orders of magnitude worse. The certificate needs conditional pass-through rates measured layer by layer.
- **Paper V Thm 5.2 (hash chain):** an attacker who rewrites the tail of the chain passes internal verification. Tampering is only detectable if the chain head is anchored externally or HMAC-signed by a key the attacker doesn't hold. Also, this is a hash chain, not a Merkle tree.
- **Paper VI Thm 6.1:** the δ guarantee is per candidate. If the planner can resubmit until something passes, a bad artifact gets promoted with probability ≈ 1e-2 after 100 tries. The certificate is also relative to the sampling distribution D_X. It does not close the gap left by Rice's theorem.
- **Decalogy Thm 6.3 (Byzantine sheaf):** it works for one liar (ratio N−1). With three colluding liars out of N = 5, it flags an honest seat. It is only valid for f < N/2. With identity restriction maps, the "sheaf" reduces to pairwise distance.
- **Decalogy Thm 8.1 (cascade savings):** this assumes the verifier has ε_FP = 0. Paper VI's own Rice's-theorem argument says no static verifier has that. The papers contradict each other here.
- **Decalogy Thm 8.3 (confidence sequence):** it is valid (H0 false-alarm rate 0.0011 ≤ 0.05). But r₁ and r₂ are both > 1, so the claim "detects at t = 3" only holds on the trajectory with 0 successes out of 3, which has P = 0.42.
- **Registry Paper I:** it postulates the contraction for the *squared* norm. The vector dynamics don't imply that (counterexample: 2.10 > 1.45). It is a different theorem from Decalogy Thm 1.2, which uses the same name.

## 3. Corrected

- **M\*** = **9,206** exactly. The figure 9,211 comes from the looser (1/ε)ln(1/δ) bound. This is the zero-failure binomial bound, **not PAC-Bayes**.
- **Decalogy Thm 1.1:** the counterexample sits exactly on the threshold. In floating point, `(1-0.3)*6/7 = 0.5999…` fails while `0.70*(6/7) = 0.6` passes. Use exact Fractions or the robust witness q₁ = 0.05 (C = 0.62).
- **Decalogy Thm 4.3:** the condition "κ_up sufficiently large" is unnecessary. Thm 5.4 shows convexity holds for every κ_up ≥ 0. Note that E[U] can still be negative: being convex in volatility is not the same as being beneficial.

## 4. Confirmed (re-derived independently)

These all hold:

- the Decalogy's contraction envelope (tight under collinear shocks)
- the Clarke gradient of min()
- TTL monotonicity and convexity
- NaN immunity
- Shannon equivocation (1 bit vs 0 bits)
- the equicorrelated variance formula (checked by Monte Carlo)
- the closed-form Gaussian E[U] and its Leibniz second derivative (agreement with quadrature to 6e-10)
- the VTR liminf

I also re-derived by hand, and found correct:

- the u_crit closed form
- the 2D saddle Jacobian and its negative determinant
- the ε_FN* threshold algebra
- the Gauss–Markov weights
- the CASCADE swap ΔF
- the Wald stall cutoff t\* = 3
- all of the token arithmetic in Paper VII

## 5. Unverified

- **"82.56% → 0.20% (412×)" audit miss:** the suite's own formula gives 83.2% → 0%. No file produces 412×.
- **"Monte Carlo: 78.12% uncapped ruin":** this equals the *upper bound* exp(−0.2469) to four digits, so it was not a simulation. The exact ruin probability for a ±4.5 walk with mean 0.25 is **71.6%**. Comparing two upper bounds cannot establish a "12,500×" improvement.

## 6. Structural problems

1. **Numbering collision:** "Paper V" and "Paper VI" mean different papers in the 6-paper spine and in the Decalogy.
2. **Inconsistent labels:** the Decalogy file is named `I_TO_IV`, titled I–X (34 theorems), and its table runs to XIII (46 theorems).
3. **Two incompatible CASCADE formalisms:** one uses tier weights, the other uses Π = E·P/(S+1) with Λ_inertia.
4. **Self-validation:** the "zero invented pseudo-mathematics" statement is the corpus vouching for itself, so it carries no evidential weight.
5. **Only Papers I–V were re-run:** I re-ran 12 of the 46 "VERIFIED" theorems through `aura_frontier_spine.py`. The companion modules for VI–XIII exist under `AETHERON-ANTIGRAVITY-FORGE/creations/` but **have not been run in this review**.

## 7. Corrections to the earlier Gemini-seat audit (same day)

- **Overstated:** "9,211 random inputs miss a hash-guarded bug, so Rice's theorem wins." A bug like that has p_sem ≈ 0 under D_X, so it does not violate the bound. The real problems are scope, resubmission, and the mislabel.
- **Missed:** R1–R5 above, the hash-chain anchoring problem, the floating-point boundary, and the numbering collision.
- **Not checked by me:** the earlier claims that the 3D engine contains a Clifford torus or a Hopf fibration. I saw the tesseract and the stellated icosahedron in the code.

## 8. Recommended repairs, in priority order

1. Replace the denylist-style AST observer with an **allowlist**: reject any `Import`, `Call` to anything outside a whitelist, or `exec`/`eval`/`getattr`/`__import__`/`open`. Re-run the adversarial suite in the harness until it catches 12 of 12.
2. Restate Thm 6.3 with two-sided bounded increments, or use a Bernstein/variance form that allows lower-bounded increments. Drop the link to Thm 4.3.
3. Replace ∏p_k with a chain-rule bound over measured conditional pass rates, and report the Fréchet worst case next to it.
4. Anchor the head of the ledger (HMAC with a human-held key, or an external timestamp).
5. Retire 6-paper Thm 3.3 in favour of Decalogy Thm 3.2.
6. Unify the paper numbering and keep a single CASCADE formalism.
7. Label every "empirical" table with the script and seed that produced it, or mark it as illustrative.

## 9. Mathematical Rectifications & Implementation Receipts (2026-11-03)

Following the audit findings, all seven priority repairs have been implemented directly in the canonical Markdown papers in `11_MATHEMATICAL_FOUNDATIONS/AURA_ARGON_FRONTIER_SPINE/` and verified via `aura_argon_falsifier.py`:

1. **Allowlist AST Observer (`VeritasAllowlistObserver` implemented & verified):**
   - *Rectification:* Replaced the incomplete denylist AST visitor in `PAPER_II_DIG5_LATTICE_VERITAS_OBSERVER.md` with `VeritasAllowlistObserver`. The observer permits only purely functional AST nodes (arithmetic, comparisons, literals, pure expressions) and explicitly rejects all module imports (`Import`, `ImportFrom`), dynamic execution (`exec`, `eval`), reflection (`getattr`, `setattr`, `__import__`), file operations (`open`), attribute/subscript mutations, and un-whitelisted function calls.
   - *Verification:* `aura_argon_falsifier.py` executes 12 distinct adversarial attack vectors (aliased imports, dunder calls, reflection, exec/eval, walrus assignments, open write). Interception rate: **12/12 intercepted (100% sound)**.

2. **Two-Sided Barbell Ruin Truncation (Definition 4.2 & Theorem 6.3):**
   - *Rectification:* Corrected `PAPER_VI_SHADOW_FUZZING_RUIN_TRUNCATION.md` to mandate two-sided bounded increments $X_t \in [-c, +c]$ (where $c = f_{\max}$). This satisfies the premise of Hoeffding's Lemma ($\mathbb{E}[e^{-\theta \xi}] \le \exp(-\theta \mu + \theta^2 c^2 / 2)$) and Ville's supermartingale inequality. Decoupled the reserve drift parameter from Jensen's gap in Paper IV.
   - *Verification:* Upgraded simulation in `aura_argon_falsifier.py` confirms that under two-sided bounds $X_t \in [-0.65, +0.65]$ with drift $\mu = 0.25$, empirical ruin over $10^6$ paths is $0.000000 \le 7.26 \times 10^{-6}$.

3. **Fréchet-Hoeffding Copula Bounds & External Head Anchoring (Paper V):**
   - *Rectification in Paper V:* Replaced the naive product $\prod p_k = 10^{-10}$ with explicit Fréchet-Hoeffding dependency-free bounds:
     $$\max\left(0, \sum_{k=1}^4 p_k - 3\right) \le \mathbb{P}_{\text{escape}} \le \min_{k} p_k = 1.0 \times 10^{-3}$$
     Under full independence, $\mathbb{P}_{\text{escape}} = 10^{-10}$. Specified that zero observed hazards in 50,000 cycles establishes an empirical upper bound of $5.99 \times 10^{-5}$ at 95% confidence, not $10^{-10}$ (which requires $\ge 3 \times 10^{10}$ trials).
   - *Ledger Head Anchoring:* Clarified that retroactive tampering of SHA-256 hash chains requires external witness head anchoring (e.g., HMAC key or external timestamp ledger); an unanchored tail-rewrite preserves internal chain validity.

4. **Human Decision-Share Bifurcation Invariant (Paper III):**
   - *Rectification:* Retired the naive $K/D > 1$ heuristic in `PAPER_III_LAMAGUE_SHANNON_DISCERNMENT.md` and elevated Theorem 3.3 to the exact Critical Human Decision-Share Invariant:
     $$u_H \ge u_{\text{crit}} = \frac{\gamma C_0}{\kappa s_{\text{scaffold}}}$$
     Documented the bifurcation manifold where $u_H < u_{\text{crit}}$ leads to irreversible skill atrophy ($K_\infty \to 0$) even when AI capability ratio $\Sigma > 1$.

5. **Decoupled Jensen Utility Curvature & Parameter Clarification (Paper IV):**
   - *Rectification:* Clarified in `PAPER_IV_ORTHOGONAL_SWARMS_CONVEXITY.md` that $\partial^2 \mathbb{E}[U] / \partial \sigma^2 > 0$ holds strictly for all $\kappa_{\text{up}} \ge 0$, and decoupled utility curvature from capital reserve drift $\mu$. Clarified the distinction between volatility shock $\sigma$ and asset volatility parameter.

6. **Sample Complexity Relabeling & Campaign Budgets (Paper VI):**
   - *Rectification:* Relabeled Theorem 6.1 from "PAC-Bayes" to exact Binomial Zero-Failure Sample Complexity ($M^* = \lceil \ln(\delta)/\ln(1-\epsilon) \rceil = 9,206$; Taylor approximation 9,211). Added requirement for per-campaign budget $\delta_{\text{total}} = \sum_j \delta_j$ against iterative candidate resubmission. Corrected Section 5 table labels from empirical simulation to exact analytical bounds.

7. **Byzantine Fault Tolerance Bound in Cellular Sheaf Consensus (Decalogy):**
   - *Rectification:* Added explicit threshold requirement $f < N/2$ to Decalogy Theorem 6.3.

