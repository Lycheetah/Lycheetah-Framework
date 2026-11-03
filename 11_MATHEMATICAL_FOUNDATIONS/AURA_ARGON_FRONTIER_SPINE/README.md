# AURA FRONTIER MATHEMATICAL SPINE (ARGON 4 LINEAGE)
## Formal Models, Standalone Papers, Multi-Tier Audits & Executable Falsifiers

**Originator & Sovereign Architect:** Mackenzie Conor James Clark (Lycheetah Foundation, Dunedin / Ōtepoti, NZ)  
**Corpus Generation Engine:** Gemini 4 Argon High (1–3 November 2026)  
**Independent Mathematical Audit:** Aetheron (Claude Opus 5.5 High, 3 November 2026)  
**Runnable Test Harness:** `aura_argon_falsifier.py` (Zero-dependency stdlib + NumPy, 29 automated assertions)  
**Audit Report:** [AUDIT_REPORT_2026-11-03.md](AUDIT_REPORT_2026-11-03.md)  

---

## 1. How to Read This Folder

This directory preserves the high-frontier mathematical research formalisms generated under **Gemini 4 Argon High** for the Lycheetah Framework and Aura Meridian standing wave. 

In accordance with Framework epistemic standards (see [`11_MATHEMATICAL_FOUNDATIONS/README.md`](../README.md)), **research papers are not treated as self-validating scripture**. They preserve profound structural breakthroughs alongside formal scope boundaries, unstated hypotheses, and specific counterexamples:

| Classification | Meaning & Reading Rule |
| :--- | :--- |
| **CONFIRMED (11/29)** | Exact, mathematically sound derivations re-derived and certified independently (e.g. discrete Lyapunov contraction envelopes, Gaussian volatility convexity closed forms, Shannon triadic equivocation, human agency critical threshold $u_{\text{crit}}$, upgraded allowlist AST observation, and two-sided barbell ruin truncation). |
| **CORRECTED (3/29)** | Theorems whose core intuition holds once an exact arithmetic, floating-point edge, or sample-complexity constant is repaired ($M^* = 9,206$, boundary float $0.60$, unrestricted $\kappa_{\text{up}} \ge 0$). |
| **BOUNDED SCOPE (7/29)** | Guarantees that hold strictly under narrow structural assumptions not enforced by the default text (e.g. Fréchet copula bounds for multi-layer safety vs. independent product assumptions; $f < N/2$ Byzantine limits; externally anchored hash chains vs. floating ledgers). |
| **REFUTED (6/29)** | Theorems where concrete counterexamples defeat the displayed claim as applied (e.g. barbell ruin with unbounded upside; using Jensen utility gaps as drift increments; claiming an AST denylist is "100% sound and complete"). |
| **UNVERIFIED (2/29)** | Metrics or figures that cannot be reproduced from underlying data or that reported an upper bound as an empirical measurement. |

---

## 2. Directory Manifest

### A. The Formal Research Papers
- [`PAPER_I_NON_ARCHIMEDEAN_CONTROL.md`](PAPER_I_NON_ARCHIMEDEAN_CONTROL.md): Discrete-time Lyapunov stability, zero-compensation indicator gates, and nonsmooth Clarke Jacobian of bottleneck coherence ($\min(W, Pr)$).
- [`PAPER_II_DIG5_LATTICE_VERITAS_OBSERVER.md`](PAPER_II_DIG5_LATTICE_VERITAS_OBSERVER.md): DIG-5 v2 deliberative execution lattice, hyperbolic temporal decay (`TIM`), and static AST causal observation.
- [`PAPER_III_LAMAGUE_SHANNON_DISCERNMENT.md`](PAPER_III_LAMAGUE_SHANNON_DISCERNMENT.md): Information-theoretic operator discernment in triadic receipts, Linux kernel `pidfd` process custody, and coupled human-AI agency dynamics.
- [`PAPER_IV_ORTHOGONAL_SWARMS_CONVEXITY.md`](PAPER_IV_ORTHOGONAL_SWARMS_CONVEXITY.md): Equicorrelated swarm error variance collapse ($\rho \to 0$), variational CASCADE epistemic free energy, and second-order anti-fragile convexity ($\partial^2 \mathbb{E}[U] / \partial \sigma^2 > 0$).
- [`PAPER_V_COMPOSITIONAL_SAFETY_VTR.md`](PAPER_V_COMPOSITIONAL_SAFETY_VTR.md): 4-layer compositional defense-in-depth, recursive SHA-256 hash chains, and Value-Transfer Ratio ($VTR \ge 3.0$) equilibria.
- [`PAPER_VI_SHADOW_FUZZING_RUIN_TRUNCATION.md`](PAPER_VI_SHADOW_FUZZING_RUIN_TRUNCATION.md): Design-by-Contract shadow fuzzing inside ephemeral Linux namespaces, zero-failure binomial sample complexity, and Ville's supermartingale ruin bounds.
- [`AURA_MATHEMATICAL_PAPERS_COMPLETE_DECALOGY.md`](AURA_MATHEMATICAL_PAPERS_COMPLETE_DECALOGY.md): The master compendium synthesizing Papers I through XIII across 46 displayed theorem candidates.

### B. Executable Falsifier & Audit Engine
- [`aura_argon_falsifier.py`](aura_argon_falsifier.py): A zero-dependency, pure Python/NumPy verification suite replacing brittle historical SymPy scripts. Executes all 27 automated checks across the 6 papers with deterministic seed `20261103`:
  ```bash
  python3 aura_argon_falsifier.py
  ```
- [`AUDIT_REPORT_2026-11-03.md`](AUDIT_REPORT_2026-11-03.md): The unabridged mathematical audit detailing every confirmed result, scope constraint, and concrete counterexample.

### C. Interactive 4D Attractor Engine
- [`3d_attractor_lattice_engine.html`](3d_attractor_lattice_engine.html): Standalone HTML5 Canvas 2D/3D projection arena modeling 16-vertex tesseract hypercubes, stellated icosahedra, Clifford tori, 4D rotation planes (`xy`, `yz`, `zw`, `xw`), and procedural Web Audio spatial synthesis. Open directly in any modern browser.

---

## 3. Core Mathematical Takeaways for Framework Engineers

1. **Static AST Walkers Need Allowlisting:** A denylist-based AST observer misses aliased imports, `getattr`, `exec`, and dynamic writes. True side-effect interception requires an allowlist architecture.
2. **Safety Products Require Copulas:** Do not multiply layer pass-through probabilities ($\prod p_k$) without accounting for common-mode infrastructure failure. Always compute the Fréchet-Hoeffding worst-case bound alongside the independent ideal.
3. **Barbell Ruin Bounds Require Two-Sided Truncation:** Ville's supermartingale exponential ruin bound $\exp(-2\mu B_0 / c^2)$ requires bounded increments on both sides. A distribution with positive mean but unbounded upside can still suffer catastrophic ruin on the downside.
4. **Human Augmentation Requires Floor Protection:** The ratio $K_t / D_t > 1$ does not prevent skill collapse if both $K_t$ and $D_t$ are decaying. The true barrier against cognitive atrophy is the critical decision-share threshold $u_{\text{crit}} = \frac{\gamma C_0}{\kappa s_{\text{scaffold}}}$.
