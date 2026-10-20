# Mathematical foundations — arguments, corrections and open work

**Creator:** Mackenzie Conor James Clark / Lycheetah Framework.  
**Current assessment:** 20 October 2026 · [SCAFFOLD] Research mathematics with reproduced counterexamples to several displayed guarantees.

Start with the [full Framework review](../28_DEFENSE/FULL_FRAMEWORK_REVIEW_2026-10-20.md)
and its [runnable probes](../28_DEFENSE/review_2026_10_20/README.md). The earlier
“Complete” introduction overstated the evidence. These manuscripts preserve
useful definitions and conditional results alongside invalid proof steps.

## Read the arguments with their corrections

| Source | Current assessment |
|---|---|
| [MATHEMATICS_FOUNDATIONS.md](MATHEMATICS_FOUNDATIONS.md) | The displayed entropy-Hessian stability inference has the wrong sign; the generator bound permits growth; claimed convexity and the implementation's unitary bridge fail. |
| [CASCADE_FORMAL_PROOFS.md](CASCADE_FORMAL_PROOFS.md) | Record retention does not prove Shannon entropy non-decrease. TES and VTR preservation conclusions do not follow from the stated premises. |
| [CASCADE_COMPLETE_SYNTHESIS.md](CASCADE_COMPLETE_SYNTHESIS.md) | Read as a synthesis of research claims, not certification of all constituent proofs. |
| [AGM_POSTULATE_VERIFICATION.md](AGM_POSTULATE_VERIFICATION.md) | The actual low-pressure update can retain conflicting universal claims. Logical closure and AGM revision require a separate implementation contract. |
| [THE_INCOMPLETENESS_PROOF.md](THE_INCOMPLETENESS_PROOF.md) | The displayed all-models/unprovability statement does not establish its universal theorem under ordinary first-order semantics. |
| [lyapunov_verification.py](lyapunov_verification.py) | Historical illustrative routines, including assigned Hessian constants and a separate averaging toy. The “11/11 verified” promotion is unsupported. Running it can overwrite its old results file; use a scratch copy. |

The review leaves the original mathematical bodies inspectable. Source positions
and hashes in its probes refer to the baseline commit, before dated notices.
A failed proof is an instruction to repair its premises and derivation, not
permission to silently substitute a different model.

## Results that retain a clear scope

- Ordinary well-typed function composition has associativity and identity.
- Banach's fixed-point theorem applies on a complete metric space with an
  established strict contraction. The presence of the theorem does not establish
  those hypotheses for the tracker or stochastic transformation pipeline.
- The narrow Pythagorean-comma arithmetic is distinct from broader Harmonia claims.
- The current [cellular sheaf implementation](../12_IMPLEMENTATIONS/core/sheaf_cohomology_factorial.py)
  provides numerical rank/projection certificates under a shared SVD cutoff;
  see the [experimental review](../TRUTH_PRESSURE/EXPERIMENTS/GLASS_TRANSITION/SHEAF_KNOWLEDGE_REVIEW.md).

## Next mathematical work

Name the state space, operators, uncertainty/entropy definitions and assumptions
for each result. Distinguish a theorem, a numerical fixture, a measured effect
and an interpretation. Reconcile proof statements with the actual maintained
implementation before promoting a status. Keep counterexamples as regression
inputs and preserve old runs as dated evidence.
