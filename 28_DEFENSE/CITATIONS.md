# D-1.0 | 2026-04-26 | Status: Active

# Citations — Lycheetah Framework

*How to cite the framework, individual components, and papers in preparation.*


> **RV30 review note (Sol, 2026-10-22). Footing: [DERIVED] for the repairs below, [UNVERIFIED] for the papers in preparation.**
>
> - **Nine component URLs repaired.** They pointed to `tree/main/` and to folder names that the
>   D-1.1 rename retired (for example `08_CHRYSOPOEIA`). The repository's default branch is `master`
>   and the folders now carry layer suffixes (`09_CHRYSOPOEIA_L4`). Every old link was dead.
> - **Two titles state guarantees wider than the proofs.** TRIAD's Banach argument covers its model's
>   update rule under its contraction condition. Nothing shows real human–AI correction follows that
>   update. CHRYSOPOEIA's coherence guarantee holds only for c ≤ 13/30, and Ξ is stochastic (earlier
>   finding F21, measured). The titles are kept as the author's; whether to retitle is Mac's call.
> - **"Nine Formal Frameworks"** means nine formally specified models. It does not mean nine
>   peer-reviewed results.
> - **Papers in preparation.** The July 2026 and October 2026 targets have passed. This review found no
>   submission record. Cite them as unpublished drafts only if a draft exists.
> - **The canonical-body counts** ("105 claims", "219 tests") are April 2026 figures. For current
>   counts run `python3 tools/verify-claims.py --register` and the test suite.

---

## Preferred Citation — Full Framework (BibTeX)

```bibtex
@software{clark2026lycheetah,
  author    = {Clark, Mackenzie Conor James},
  title     = {The Lycheetah Framework: Nine Formal Frameworks for AI Alignment and Epistemology},
  version   = {C-1.1},
  year      = {2026},
  month     = {5},
  doi       = {10.5281/zenodo.20020828},
  url       = {https://doi.org/10.5281/zenodo.20020828},
  note      = {Nine formal frameworks for AI alignment and epistemology.
               Canonical body C-1.1 (reforged from C-1.0).
               Defense layer D-1.2. TIANXIA module v0.3 (Classical Triad complete).
               Zenodo DOI minted 2026-05-04.}
}
```

---

## Individual Framework Citations

### CASCADE

```bibtex
@techreport{clark2026cascade,
  author      = {Clark, Mackenzie Conor James},
  title       = {CASCADE: Bayesian Belief Revision with Truth Pressure Dynamics},
  institution = {Lycheetah Foundation},
  year        = {2026},
  type        = {Framework Specification},
  note        = {Lycheetah Framework C-1.0, Framework 1.
                 Theorems C1--C4. Empirical results: +40.3\% coherence (synthetic),
                 +110\% coherence (real data), -95.2\% catastrophic forgetting.
                 URL: https://github.com/Lycheetah/Lycheetah-Framework/tree/master/01_CASCADE_L4}
}
```

### AURA

```bibtex
@techreport{clark2026aura,
  author      = {Clark, Mackenzie Conor James},
  title       = {AURA: Seven Constitutional Invariants for AI Governance},
  institution = {Lycheetah Foundation},
  year        = {2026},
  type        = {Framework Specification},
  note        = {Lycheetah Framework C-1.0, Framework 2.
                 Invariants I1--I7. Runtime compliance predicate aura\_compliant(a).
                 URL: https://github.com/Lycheetah/Lycheetah-Framework/tree/master/02_AURA_L3}
}
```

### LAMAGUE

```bibtex
@techreport{clark2026lamague,
  author      = {Clark, Mackenzie Conor James},
  title       = {LAMAGUE: Formal Grammar for Encoding Ethical Constraints},
  institution = {Lycheetah Foundation},
  year        = {2026},
  type        = {Framework Specification},
  note        = {Lycheetah Framework C-1.0, Framework 3.
                 Four-tier language stack. Theorems L1--L2. Cross-cultural convergence draft v0.1.
                 URL: https://github.com/Lycheetah/Lycheetah-Framework/tree/master/03_LAMAGUE_L1}
}
```

### TRIAD

```bibtex
@techreport{clark2026triad,
  author      = {Clark, Mackenzie Conor James},
  title       = {TRIAD: Convergent Correction Cycle with Banach Fixed-Point Guarantee},
  institution = {Lycheetah Foundation},
  year        = {2026},
  type        = {Framework Specification},
  note        = {Lycheetah Framework C-1.0, Framework 4.
                 Theorems T1--T4. Lyapunov verification 11/11 claims, 0 failures.
                 URL: https://github.com/Lycheetah/Lycheetah-Framework/tree/master/04_TRIAD_L2}
}
```

### MICROORCIM

```bibtex
@techreport{clark2026microorcim,
  author      = {Clark, Mackenzie Conor James},
  title       = {MICROORCIM: Continuous Drift Detection Between Intent and Behavior},
  institution = {Lycheetah Foundation},
  year        = {2026},
  type        = {Framework Specification},
  note        = {Lycheetah Framework C-1.0, Framework 5.
                 mu\_drift metric. Sovereignty score S\_score. Theorem M2.
                 URL: https://github.com/Lycheetah/Lycheetah-Framework/tree/master/05_MICROORCIM_L5}
}
```

### EARNED LIGHT

```bibtex
@techreport{clark2026earnedlight,
  author      = {Clark, Mackenzie Conor James},
  title       = {EARNED LIGHT: Thermodynamic Model of Consciousness as Maintained Asymmetry},
  institution = {Lycheetah Foundation},
  year        = {2026},
  type        = {Framework Specification},
  note        = {Lycheetah Framework C-1.0, Framework 6.
                 C\_psi(t) = integral of A(psi,x,t)dx. Hard problem explicitly out of scope.
                 URL: https://github.com/Lycheetah/Lycheetah-Framework/tree/master/06_EARNED_LIGHT_L0}
}
```

### ANAMNESIS

```bibtex
@techreport{clark2026anamnesis,
  author      = {Clark, Mackenzie Conor James},
  title       = {ANAMNESIS: Attractor Dynamics for Convergent Discovery},
  institution = {Lycheetah Foundation},
  year        = {2026},
  type        = {Framework Specification},
  note        = {Lycheetah Framework C-1.0, Framework 7.
                 TC(S,n) metric. TC(phi,3), TC(pi,4), TC(symmetry,4) measured.
                 URL: https://github.com/Lycheetah/Lycheetah-Framework/tree/master/07_ANAMNESIS_L0}
}
```

### CHRYSOPOEIA

```bibtex
@techreport{clark2026chrysopoeia,
  author      = {Clark, Mackenzie Conor James},
  title       = {CHRYSOPOEIA: Seven-Phase Transformation Operator with Banach Fixed-Point Convergence},
  institution = {Lycheetah Foundation},
  year        = {2026},
  type        = {Framework Specification},
  note        = {Lycheetah Framework C-1.0, Framework 8.
                 Non-commutativity proven. Theorem X1. Fourier structural parallel.
                 URL: https://github.com/Lycheetah/Lycheetah-Framework/tree/master/09_CHRYSOPOEIA_L4}
}
```

### HARMONIA

```bibtex
@techreport{clark2026harmonia,
  author      = {Clark, Mackenzie Conor James},
  title       = {HARMONIA: Consonance Functions, Kuramoto Coupling, Frequency-Ratio Dynamics},
  institution = {Lycheetah Foundation},
  year        = {2026},
  type        = {Framework Specification},
  note        = {Lycheetah Framework C-1.0, Framework 9.
                 C(r) = 1/(1 + sum of ak*(0.5)^k). EWM interval table. Pythagorean comma engine.
                 URL: https://github.com/Lycheetah/Lycheetah-Framework/tree/master/10_HARMONIA_L6}
}
```

---

## Papers in Preparation

These papers are in active preparation. Cite as unpublished until DOI is available.

```bibtex
@unpublished{clark2026lamague_crosscultural,
  author = {Clark, Mackenzie Conor James},
  title  = {Cross-Cultural Convergence in Ethical Grammar: Evidence from
            Maori, Confucian, and Western Traditions},
  year   = {2026},
  note   = {Draft v0.1 complete. Target: AI and Ethics (Springer), July 2026 submission.
            Preprint: pending arXiv submission.}
}

@unpublished{clark2026cascade_jair,
  author = {Clark, Mackenzie Conor James},
  title  = {CASCADE: Bayesian Knowledge Reorganization with Truth Pressure Dynamics},
  year   = {2026},
  note   = {In preparation. Target: Journal of Artificial Intelligence Research (JAIR),
            October 2026. Gates on k1--k4 calibration.}
}

@unpublished{clark2026triad_chi,
  author = {Clark, Mackenzie Conor James},
  title  = {TRIAD Protocol: User Study of a Convergent Human-AI Correction Cycle},
  year   = {2026},
  note   = {In preparation. Target: CHI 2027. N=20 user study, 30 days. February 2027 deadline.}
}
```

---

## Canonical Body Citation

```bibtex
@techreport{clark2026codex,
  author      = {Clark, Mackenzie Conor James},
  title       = {CODEX AURA PRIME: Canonical Body C-1.0 of the Lycheetah Framework},
  institution = {Lycheetah Foundation},
  year        = {2026},
  month       = {4},
  type        = {Canonical Archive},
  note        = {22-Act Codex Elevation completed 2026-04-25.
                 105 indexed load-bearing claims. 34 Python implementations.
                 219 automated tests. Adversarial audit and failure museum included.
                 URL: https://github.com/Lycheetah/Lycheetah-Framework}
}
```

---

*This document is part of Codex Defense Protocol D-1.0, defending canonical body C-1.0 (2026-04-25).*
