# Lycheetah Framework — substantive review, 20 October 2026

**Creator:** Mackenzie Conor James Clark / Lycheetah Framework.
**Review:** Caelorynth / Codex, with a separate mathematical reviewer and primary-agent reproduction.
**Status:** [INTERPRETIVE] Technical assessment with measured software checks and derived counterexamples. This is AI-assisted project review, not independent scientific peer review.
**Updated:** 21 October 2026 with implementation repairs and an incomplete deeper folder pass.

## Assessment

Lycheetah contains substantial executable work: policy receipts, permission and
replay controls, restricted language tooling, revision models and reproducible
failure cases. Its philosophical and fictional branches also have coherent
purposes of their own. The corpus does **not** currently establish its older
claim of one proven, universally applicable mathematical system.

The main credibility problem is evidence being promoted beyond its scope.
Definitions become empirical measurements; a conditional theorem becomes an
implementation guarantee; a fixture becomes validation; a cultural analogy
becomes an identity. Later research often states these limits much more carefully
than the foundational summaries that still introduce it.

The strongest defensible direction is specific, inspectable instruments for
preserving evidence, meaning, permission and recovery through change. Establish
their benefit in an outside workflow before promoting the whole framework.

## Scope and receipts

The baseline is commit `6ba483af3f125ec725eb4e0f44074d0887183255`:
4,822 tracked files across 50 top-level directories, including 35 root files.
The review examined all nine foundational summaries, the 71-row claims register,
its 107 evidence references, the formal spine, principal proof arguments,
maintained software and tests, research continuations, NZ governance and the
relationships between these branches. This is not a line-by-line certification
of every archived file or a literary edit of every story.

The deeper pass began from the staged review tree: **4,837 tracked files in
606 folders**. Three high-reasoning reviewers started separate lanes but all
were interrupted by a service usage limit. Their preliminary messages are leads,
not completed reviews. The primary independently reproduced the specific
counterexamples described below. The [folder receipt](review_2026_10_20/folder-coverage.json)
accounts for every folder while distinguishing targeted source readings from
ZIP metadata and census-only entries. **The deeper semantic review is incomplete.**

Evidence is retained beside this report:

- [Runnable mathematical probes and reproduction instructions](review_2026_10_20/README.md).
- [18 probe results, controls and 36 pinned source identities](review_2026_10_20/math-probes.json).
- [Baseline audit of every claims-register evidence pointer](review_2026_10_20/claim-evidence-audit.json).
- [Source-location repairs and remaining missing references](review_2026_10_20/evidence-path-repairs.json).
- [Explicit assessment of all 71 register rows](review_2026_10_20/claim-assessments.json), preserving author classifications separately.
- [Dated source notices](review_2026_10_20/source-review-notices.json), with before/after hashes and original bodies retained.
- [All 50 area coverage records](review_2026_10_20/coverage.json), distinguishing executed contracts, source review and census-only areas; the [repository map](../00_Sovereign_Index.md) locates their current homes.
- [Deeper counterexamples reproduced by the primary](review_2026_10_20/deeper-reproductions.json), with unchanged research-source hashes.

`REPRODUCED` in the mathematical receipt means the **reviewer's observation**
reproduced. It does not mean the author's theorem passed. Source line positions
in those receipts refer to the pinned baseline, before review notices were added.

## Software defects and corrections

### R1 — a bound consensus digest did not bind the decision actually executed

**Priority: P1. Corrected in this branch.** A disconnected three-agent arena
produced a failed verdict. The unmodified verdict was denied. Changing only its
`converged` and `obstruction_free` flags, while retaining the original digest and
permit, caused the fixture executor to run. The harness compared stored digest
strings but never recomputed the verdict's digest.

The v2 digest now binds the anchor and complete reported outcome, without lossy
float rounding. Permit issuance and execution verify it. Mutated or legacy
unverifiable verdicts are rejected before nonce consumption or executor dispatch.
Legacy permits/verdicts require re-deliberation and reissue. This is an integrity
repair inside the local harness; an unkeyed digest does not authenticate an
external issuer or constrain arbitrary code controlling the Python process.

Sources: [arena](../lycheetah/consensus/arena.py),
[harness](../lycheetah/sovereign_harness.py),
[regressions](../tests/test_consensus_integrity.py).
The bypass regression failed before the correction and passes after it.

### R2 — nonfinite vectors could produce a nominally converged outcome

**Priority: P1 at an execution boundary. Corrected in this branch.** NaN and
infinite anchors were accepted, and a resulting verdict could report convergence
with NaN drift. Public arena/protocol vector admission now rejects nonfinite,
empty, wrongly shaped and zero-norm inputs. The MCP network formatter also
rejects invalid vectors visibly. Strict digest serialization provides a further
barrier against nonfinite outcome evidence.

### R3 — connectivity was labelled as exact first cohomology

**Priority: P1 for the advertised guarantee. Runtime labels corrected.** The
legacy `ObstructionDetector` checks connectivity and neighboring vector distance.
It does not compute H¹. A consistent triangle with two-dimensional constant
stalks passes that proxy while `dim H¹ = 2`; two isolated vertices fail the proxy
while `dim H¹ = 0`. Requiring H¹ to vanish would therefore be the wrong repair.

The proxy remains an explicit policy, and `CellularSheaf` remains a separate
numerical diagnostic. Global sections are in H⁰. The reported one-third
quarantine budget also does not establish Byzantine fault tolerance against
equivocation. Public module descriptions, audit messages and formatter output
now distinguish these claims. The legacy stop-reason string
`COHOMOLOGY_OBSTRUCTION` remains for caller compatibility.
See [Hansen and Ghrist's cellular-sheaf treatment](https://arxiv.org/abs/1808.01513).

### R4 — parallel desktop scoring changed the user's provider preference

**Priority: P2. Corrected in this branch.** `consensusScore` temporarily rewrote
shared `localStorage` while parallel requests were outstanding. With OpenAI
selected, completion could leave DeepSeek selected, including after a provider
failure. The two original regressions both failed before the correction.

Each request now receives its provider explicitly. Three mocked tests pass:
successful scoring, provider failure, and the user changing preference while
scoring is in progress. No real provider request or credential was used.
Sources: [scoring](../cascade-pc/src/scoring/ai.js),
[tests](../cascade-pc/tests/scoring-provider.test.mjs).

### R5 — Chorus health and audit results are canned

**Priority: P1 for reliance on the result; historical scaffold, not live assurance.**
`MultiAgentChorus.health_check` assigns every entry `ONLINE` without testing its
agent. Supplying nine `None` entries still reports nine online and
`all_constitutional=true`. Its truth audit supplies an empty file list and
returns zero findings and coherence 1.0. Those outputs cannot establish health,
constitutional compliance or a corpus audit. The source remains available as a
scaffold; its revised entry guide identifies this limitation.
Source: [runner](../19_MULTI_AGENT_CHORUS/run_chorus.py).

### R6 — a tiny TRIAD step could be reported as convergence

**Priority: P2. Corrected on 21 October.** With a constant gradient of 1 and
step size `1e-12`, the tracker stopped after one step despite being far from a
stationary point. Its step receipt paired the new state with the previous
state's coherence. It now requires a small gradient as well as a small update,
records coherence at the reported state, and rejects invalid configuration or
nonfinite transitions before committing state/history. The stop flag still does
not distinguish a minimum from a maximum or prove global uniqueness; the old
general Banach-guarantee wording was removed.
Sources: [tracker](../12_IMPLEMENTATIONS/core/triad_tracker.py),
[boundary regressions](../tests/test_implementation_boundaries.py).

### R7 — incomplete metric inputs could become passing scores

**Priority: P2. Corrected on 21 October.** Mismatched purpose vectors silently
fell back to the no-violation score of 0.9. Negative violation counts could
inflate that score above 1, and negative value divided by negative friction
could appear beneficial. Nonfinite inputs were accepted; large finite vectors
overflowed the cosine calculation. The maintained checker now validates these
boundaries and computes cosine after scaling. The fallback requires that neither
vector is supplied. These repairs do not calibrate the metrics or their thresholds.
Source: [TRI-AXIAL checker](../12_IMPLEMENTATIONS/core/tri_axial_checker.py).

### R8 — gateway checks diverged from the guarded workflow

**Priority: P1. Corrected on 21 October.** Six new regressions failed against the
old gateway: uncheckpointed history could be published by a later proposal or
dispatch; reopening did not reject that history; `{}` as a live action was
silently replaced by the intended action; a newly denied tool could execute;
and a receipt could name a policy changed by the executor rather than the one
evaluated. The gateway now uses `CheckpointedWorkflow` for each ledger mutation,
rejects dirty history, checks the current policy at dispatch and captures the
evaluated policy for the receipt. An uncheckpointed dispatch claim does not reach
the executor. A result-checkpoint failure after execution returns `UNKNOWN`
without a success receipt. This remains a local control: caller-supplied approver
metadata does not authenticate a human or prove what an arbitrary callback does.
Sources: [gateway](../lycheetah/assurance/gateway.py),
[regressions](../tests/test_gateway_boundaries.py).

### R9 — an unrelated JSON key could satisfy all ten accountability fields

**Priority: P1 for relying on a clean result. Corrected on 21 October.**
`lamague_check` treated an empty normalized key as a suffix of every alias.
`{"☃":"unrelated"}` could therefore receive ten present fields. Reverse suffix
matching also accepted short fragments such as `pose`. The matcher now rejects
empty normalized keys and the reverse comparison. Seven regressions cover the
counterexamples, supported nested aliases, single fields and empty placeholders.
Sources: [checker](../03_LAMAGUE_L1/24_LAMAGUE_CHECK/lamague_check.py),
[tests](../tests/test_lamague_check_aliases.py).

### R10 — literal consent abbreviations changed during compression

**Priority: P1 for exact permission preservation. Maintained boundary corrected.**
Both the supplied codec and its maintained copy admitted literal `R`, `I` and
`N`, then decoded them as `REVOCABLE`, `IRREVOCABLE` and `NONE`. The full packet
and protected hash changed. The maintained codec now rejects these ambiguous
input values and requires the explicit intended consent; it does not silently
choose permission on the author's behalf. Both wire modes preserve supported
values. The frozen supplied codec retains its original bytes and counterexample.
Sources: [maintained codec](../lycheetah/compaction/codec.py),
[regressions](../tests/test_compaction_consent_roundtrip.py).

### Additional research and archive findings remain open

- The frontier policy-evolution prototype collapses duplicate group IDs into a
  dictionary for comparison while evaluating every group in the actual formula.
  A two-step change can be labelled equivalent while removing a real condition.
  The primary reproduced the classifier counterexample, not remote execution.
  [Source](../papers/agent-safety/frontier-controls/06_hazard_lineage_policy_evolution_v1_2/policy_evolution_gate.py).
- Anon Politician's supplied review aggregator accepts different case IDs within
  an experiment and counts duplicated reviews as extra ratings, even when its
  unique reviewer count remains one. Separation and deduplication need admission
  checks before a real review study uses it. [Source](../23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/07_POLICY_LAB_v0.2/Anon_Politician_Policy_Lab_v0_2/evaluation/aggregate_reviews.py).
- The closed-loop vault's 1,788-entry manifest passes against the local full
  vault, but **374 `.log` references are absent from the Git index**. Latest
  tracked ZIPs contain matching bytes for 373; one companion retest log was not
  found there. A local checksum pass does not establish clean-checkout availability.
  Its guide identifies this portability gap. No archives were executed.
- Directly addressable School essays claimed diagnostic certainty, necessary
  suffering and guaranteed psychological recovery through Banach's theorem.
  Those claims are now explicitly withdrawn in notices on the pages themselves;
  original bodies remain as historical text. They do not establish a clinical
  method or justify withholding support. See [The First Map](../14_MYSTERY_SCHOOL/THE_FIRST_MAP.md),
  [The Therapist's Door](../14_MYSTERY_SCHOOL/THE_THERAPISTS_DOOR.md) and the
  [NHS guidance on urgent support](https://www.nhs.uk/nhs-services/mental-health-services/where-to-get-urgent-help-for-mental-health/).

## Mathematical findings

These findings concern the displayed statements and their implementation
bridges. A failed proof does not refute every possible successor model. The
probe receipt supplies the actual values and scope for each observation.

| Finding | Reproduction or source problem | Consequence |
|---|---|---|
| M1 — TRIAD Jacobian sign | MP01: a negative binary-entropy Hessian and `DG = I − α Hess(S)` give a multiplier **1.47619**, not a value in `(0,1)`. | The displayed local-stability inference is reversed. |
| M2 — generator bound | MP02 satisfies the displayed norm bound with noncommuting operators yet has eigenvalues with real part **+0.1**. | The stated condition does not guarantee stability. This does not by itself refute a separately worded *necessary* condition. |
| M3 — actual tracker | MP03 reaches a stationary coherence minimum and admits distinct fixed points. | A small step is not evidence of a maximum, global uniqueness or Banach contraction. |
| M4 — convexity/unitarity | MP04: two zero-entropy endpoints have a maximum-entropy midpoint. MP05: the implemented ascent changes an inner product from 0 to about **0.19802**. | The claimed low-entropy convexity and unitary-operator bridge fail as stated. |
| M5 — √n threshold derivation | MP06: for the given orthonormal-column matrix, spectral norm is **1/n**, not rank/n; the normalized uniform rank-one matrix has norm 1. | The displayed derivation does not establish a universal threshold law. A real symmetric matrix also cannot supply the claimed nonreal Hopf pair. |
| M6 — master equation | MP07: the proposed reference is not an equilibrium; a stated below-threshold case has **positive** Lyapunov derivative. | For fixed inputs the displayed linear ODE has a shifted equilibrium and eigenvalue `−k₂`; crossing Π_th alone does not create the advertised stability change. |
| M7 — sovereignty ⇒ ethics | MP08: identical intended and actual violating actions give zero drift and score 1. | MICROORCIM's score alone cannot imply the seven AURA predicates. An assumed compliant intention cannot be dropped from the conclusion. |
| M8 — foundation preservation | MP09: actual CASCADE demotes an old foundation to THEORY while preserving its record. | Preserving a record and preserving its layer membership are different properties; the formal spine promises the latter. |
| M9 — information preservation | MP10: retaining old outcomes while adding one can reduce Shannon entropy from **1 bit to 0.16144 bits**. | Record retention does not prove Shannon entropy non-decrease. The engine's sum of uncertainty metadata is another quantity. |
| M10 — AURA metric preservation | MP11: the written TES construction can fall from 1 to **0.55935**. MP12: positive value can still be less than cost. | The advertised TES floor and VTR conclusion do not follow from the given premises. |
| M11 — Chrysopoeia | MP13: Solve then Coagula takes coherence **1 → 0.9 → 0.915**. MP14: the actual pipeline draws fresh noise. | The stated monotonicity fails, and a final contracting stage does not prove the whole stochastic composition is a deterministic contraction. |
| M12 — Harmonia | MP15: simple ratios telescope to an exact octave multiple. MP16: the formula, table and implementation proxy disagree. | Preserve the narrow Pythagorean-comma result; withdraw the broader universal claim and calibrate any perceptual instrument separately. |
| M13 — thermodynamics | MP17: reversible adiabatic compression permits nonzero work with zero entropy change. | `ΔS = −W/T` is not a general thermodynamic law. Dimensionless Shannon entropy also needs an explicit bridge to physical units. |
| M14 — AGM | MP18: a low-pressure conflicting block can remain without revision, leaving the actual represented store inconsistent. | Layer organization is not logical closure or a proof that the implementation satisfies all AGM postulates. |
| M15 — incompleteness | The written formal statement combines `F ⊨ G` in **all models** with `F ⊬ G`, without the required Gödel hypotheses. | Under ordinary first-order semantics this conflicts with completeness. An analogy about limits is not the displayed universal theorem. |
| M16 — Anamnesis | A global attracting set is assumed before the metaphysical conclusion; proposed competing predictions are not consistently distinguished. | Recurrence may motivate inquiry but does not establish realism, universal attractors or historical independence. |
| M17 — “11/11 verified” | The Hessian routine returns a fixed layer table. The 5,000-trial routine uses a separate toy; numerical observations are included in the passing total. | LYV-001 cannot be cited as verification of the maintained engines or the entire proof chain. |
| M18 — novelty/normalization | Dimensionless quantities and repeated terminology are offered as evidence of universality and “first/only” contributions. | Dimensional consistency does not establish construct validity, empirical equivalence or historical priority. No exhaustive novelty search was performed. |

Relevant source homes: [mathematics](../11_MATHEMATICAL_FOUNDATIONS/README.md),
[formal spine](../30_MAPS/FORMAL_SPINE.md),
[Truth Pressure](../TRUTH_PRESSURE/README.md), and the pinned probe receipt.
For the entropy/work distinction see
[MIT's second-law notes](https://ocw.mit.edu/courses/10-40-chemical-engineering-thermodynamics-fall-2003/aea59133e5a4de8675700ec04eef57fc_suppnotes_ch04.pdf).
Banach's theorem remains valid under a complete metric space and a strict
contraction; see the [MIT contraction formulation](https://math.mit.edu/~larsh/teaching/F2003_099/ps7/ps7.pdf).
What fails is the automatic transfer of those hypotheses to these implementations.

## What survives this review

Ordinary well-typed function composition has associativity and identity.
Conditional fixed-point results remain useful when their hypotheses are actually
established. The narrow Pythagorean-comma arithmetic is sound. Explicit retention
of knowledge records is an inspectable software property, even where an entropy
theorem was overstated.

The newer sheaf code explicitly assembles δ⁰ and uses a shared SVD cutoff for
rank and projection. It already distinguishes partial loss of global sections
from their complete elimination. Its certificates describe floating-point
truncated operators, not exact algebraic ranks for arbitrary ill-conditioned
inputs. Boundary-pinned residuals depend on the chosen vector encoding; they do
not identify factual contradictions without that modeling assumption.

The eight-cell factorial is a useful sensitivity design. Its `work_coupled`
service estimates work at start and recomputes work on the later live store.
It lacks a receipt proving that every completion paid its actual work. Retain
the [existing sheaf/experimental review](../TRUTH_PRESSURE/EXPERIMENTS/GLASS_TRANSITION/SHEAF_KNOWLEDGE_REVIEW.md)
and treat equal-paid-work causal claims as unresolved.

The maintained assurance implementation has substantive local controls:
canonical action binding, single-use SQLite claims, approval/actor separation,
policy/evidence binding, receipt verification and checkpoints. Its documented
dispatch linearization boundary is real: later revocation cannot undo an effect
already dispatched. Receipt logs declare a single-writer boundary. Execution
cells explicitly remain a Linux-isolation scaffold. None of these mechanisms
certifies policy correctness, complete observation or external identity.

## Claims register and evidence repair

The baseline register contains **71 claims**, of which **52 are author-labelled
ACTIVE**. Its 107 literal evidence references contained **37 missing pointers**;
24 claims had no existing pointer, including 18 ACTIVE claims. Missing evidence
does not itself refute a theorem; an existing file does not prove one.

This branch repairs **14** identifiable moved-source references, preserving
every claim statement and author-assigned status. **23 missing references remain**,
and **16 claims still have no existing pointer**. These include nonexistent
theorem files, an implementations directory and a transcultural catalogue.
No placeholder evidence or unrelated substitute proof has been invented.

The register's ACTIVE labels remain the author's classifications, including where
this review disputes the advertised proof. They must not be used as a count of
results verified by this review. See the baseline audit and repair receipt for
the distinction between author status, pointer existence and mathematical support.

## Research continuations and empirical limits

| Branch | Supported reading now |
|---|---|
| LAMAGUE CORE / runtime / codec | Distinct versioned formal languages and instruments. Software conformance and exact packet round trips do not establish arbitrary-language meaning preservation. The maintained suite includes shelf checks; naming/version boundaries remain essential. |
| SXP-L v2.0 | A restricted study instrument with zero genuine participant results. The dated integration records 12 new and 71 inherited passes alongside eight reproduced open defects. Linguistic consent/repair defects must be resolved before treating this language as an authorization gate. |
| Truth Pressure v0.3/v0.5/v0.7 | Fresh local verification reproduced **24, 14, 11 and 11** engineering checks. Weights, semantic interpretation and decision thresholds remain uncalibrated. The published 100-record shadow report explicitly uses synthetic records. |
| Earned Trust / Hybrid Gateway | Frozen experimental continuations, not automatic replacements for the installed runtime. Their counterexamples and conventional temporal/recovery baseline ties are material findings. |
| Earned Light / Sovereign Choice | The 19 October replay records 207 + 207 test executions, with historical overlap. Source identities were checked again here; those suites were not redundantly rerun. Trust-root failures, recovery/export ties, the 18/18 goal-aware baseline tie and fictional reachability cases remain part of the result. |
| Text scoring | Dated project-run external-data evaluations show a small assistant-text effect, null social-engineering separation and failure to transfer the AURA lens to the independent-publisher human-comment corpus. They are not independently executed studies or general alignment verification. See the [capability guide](../33_APPLICATIONS/README.md). |
| Empirical programme | Seven study-design documents do not equal seven executed or externally registered studies. No new participant recruitment, clinical use, provider experiment or paid model call occurred in this review. |
| Mystery School / Mythos / Abstract and Generative | Learning designs, philosophy and fiction retain their value and source ownership. Source-fidelity contracts do not establish learning benefit, consciousness, cultural endorsement or literary canon approval. |

The October intake checker freshly matched 444 frozen files, and a separate
current-hash check matched the later 225-file manifest. The automatic checker
still covers only the earlier manifest; wiring the later intake into that gate
remains necessary. Anon Politician's checksum list matched **121 files**, not
the 59 claimed by its older README. These counts are preservation checks.

## NZ governance, culture and ownership

The current NZ direction is the [six-rights proposal](../23_NZ_AI_GOVERNANCE/DATA_SOVEREIGNTY_FOR_NEW_ZEALANDERS.md).
The 26 earlier cultural-policy drafts remain historical; they must not be
presented as today's adopted standard. Related claims also remain in the
cross-cultural and TIANXIA branches, so changing the NZ index alone is insufficient.
Those branches are research mappings, not proof of cultural identity, historical
independence, community endorsement or an institutional partnership.

There is already a government [Public Service AI Framework](https://www.digital.govt.nz/standards-and-guidance/technology-and-architecture/artificial-intelligence/public-service-artificial-intelligence-framework)
covering transparency, human oversight, safety and accountability. Lycheetah
should specify the operational addition it proposes rather than imply no such
framework exists. Existing [access rights](https://www.privacy.org.nz/privacy-principles/6/)
have a legal scope and exceptions; [overseas disclosure rules](https://www.privacy.org.nz/privacy-principles/12/)
are not a universal requirement that all data stay in New Zealand. The proposed
future-use withdrawal, human-review route and location receipt need separate
implementation and legal assessment. No legal compliance result is claimed here.

Anon Politician's civic validator expressly checks **declared metadata**, not
actual sampling execution or representativeness. Its separation of opt-in voice,
population measurement and deliberation is valuable. Its policy-review machinery
does not yet demonstrate improved real policy outcomes. Fresh tests passed:
16 civic, 16 policy-lab and 11 audit-kit checks.

Ownership documentation conflicts: the root LICENSE contains plain MIT text,
CONTRIBUTING names an additional Earned Sovereignty Clause, and the attribution
guide states mandatory conditions absent from that LICENSE. The owner needs to
reconcile these texts and preserve supplied subproject licences. This review does
not choose a new licence or remove attribution to Mackenzie Conor James Clark.

## Verification and remaining release blockers

The [verification receipt](review_2026_10_20/verification.json) records executed
counts and remaining failures. Separate receipts preserve the
[Chorus counterexamples](review_2026_10_20/chorus-probe.json),
[225 imported-file hashes](review_2026_10_20/oct19-preservation.json) and
[lint baseline comparison](review_2026_10_20/lint-baseline-comparison.json).

The maintained Python 3.12 suite completed with **997 passed, 1 skipped and
1 strict expected failure**, across 999 collected cases. The skip tests an absent
MCP installation while MCP was installed. The expected failure retains an
unattainable CASCADE predictive criterion, not a hidden pass. Localhost and async
execution required an allowed run; restricted socket failures and a sandbox MCP
hang were diagnosed separately. The five MCP 2 integration checks passed.

Additional fresh checks: 17 Modelcraft tests; 10 Book I tests plus its validator;
43 Anon Politician tests; 60 Truth Pressure engineering checks; and three mocked
desktop-scoring tests. These counts overlap neither scientific studies nor
independent validation. Mathematical controls caught deliberately wrong numeric
and Boolean assertions before recording the 18 reviewer observations.

The package built an sdist and wheel. A clean base-wheel installation outside
the source checkout exercised all 11 declared commands, two domain demos and
the optional-extra/source-only boundaries. Public-package mypy checked 30 source
files successfully; it does not typecheck all implementation modules.

The clean optional-extras wheel check also passed packaged-schema, web-health,
evaluation/regression, OTel event and ten-tool MCP registration contracts. It
does not establish production integration with an external provider.

On 21 October, focused runs passed **167 implementation/sheaf/gateway cases**,
**seven alias cases**, and **92 compaction/harness cases**. These runs overlap;
there are **64 distinct new boundary cases**, with 42 counterexamples shown to
fail before their corresponding repairs. The earlier whole maintained suite was
not rerun for this extension. All 55 Python implementation sources passed AST
syntax inventory; that is not a claim of executing every module. Changed-code
lint, public-package formatting and mypy's 30 source files passed. The main
README's Python example was executed verbatim: its local action succeeded and
the proposed write returned `REVIEW` with `allowed=False`.

**The repository is not release-clean.** Whole-corpus lint reported 46 findings
in six unchanged research/version files. All six match the review baseline;
these are existing defects, not a reason to weaken the lint gate. The footing
gate initially reported 80 unmarked documents; the updated guides reduce this
to 79, still above its fixed budget of 30. The internal
link check found zero dead links outside the archive and 22 inside the frozen
archive. Those are different gates and different outcomes.

Desktop scoring's numerical unit tests do not establish the Electron app's
rendering or full build. Its automatically started unauthenticated localhost
read API and browser-local API-key storage need an explicit distribution threat
model. No hosted CI pass, new website, deployment, public post, branch merge or
production safety result follows from this local review. Python 3.10/3.11 and
other desktop platforms were not rerun.

## Swarm follow-through: inspectable handoffs — 21 October

Three newly authorised AI reviewers completed a bounded architecture, execution
and first-use pass. This does not complete the earlier 606-folder semantic review.
The [swarm receipt](review_2026_10_20/swarm-hardening.json) identifies the source
base, changed components, test counts and limits.

The pass reproduced two linked reference-integrity defects: exported context
packets shared mutable collections with their live accumulator, and supposedly
frozen policies retained caller-owned lists. Mutating either could silently
change the reference used for a later comparison or the policy digest recorded
after execution. Context exports now produce independent validated snapshots;
policy/rule collections are detached into tuples and policy metadata is captured
before callbacks. Packet hashes and L1/L1D wire compatibility remain unchanged.

Gateway receipts also mixed execution outcomes with policy decisions, producing
receipts that failed their own verifier for ordinary failure, timeout and
review-approved cases. The receipt now retains the evaluated policy decision
and records execution status separately. Its event uses the runtime's subject,
privacy and replay shape plus the declared actor, scope and action digest.

The existing [guarded handoff example](../examples/guarded_handoff_risk_demo.py)
now optionally exports a new directory containing task/completion capsules, full
context, exact action, actual output bytes, full receipt and run report. A separate
read-only verifier checks their relationships and manifests. A retained digest
pins bundle bytes; without it, a self-consistent replacement is outside detection.
It remains a synthetic-consensus fixture with declared approval labels and a
trusted writer. No private checkpoint keys, model calls, authenticated human
issuer or independent filesystem witness are introduced.

Independent AI review caught contradictory run reports, omitted completion paths
and a nonregular-manifest read hazard in the first verifier. Twelve controls
failed before those repairs. The final focused run passed **329 cases**, including
**90 new cases**: 36 snapshot cases, 18 gateway/policy cases and 36 bundle cases.
These are local engineering results, not external replication. The earlier
whole-suite result remains separately dated; no fresh whole-corpus proof or
release-clean claim is made.

## Repair sequence

1. Publish the dated corrections beside the claims they qualify. Replace the
   “11/11 verified” promotion with real operator-specific calculations and
   explicit incomplete results. Preserve the old run as historical evidence.
2. Finish the evidence register: resolve or explicitly retire the remaining
   23 pointers; separate definitions, conditional theorems, measurements,
   proposals and refuted statements. A source-location repair is not promotion.
3. Close the software release gates without rewriting frozen records to obtain
   a green result. Extend intake verification, resolve the lint/footing backlog,
   and document the consensus v2 migration and desktop trust boundary.
4. Choose one operational workflow for the existing permission/receipt tools.
   Compare it with a conventional baseline and measure real user benefit,
   failure handling and review burden under a fixed protocol.
5. Advance mathematical successors only with explicit state spaces, operators,
   invariant definitions and assumptions. Keep cultural inquiry, philosophical
   authorship and fiction first-class without using them as experimental proof.

The immediate task is a credible, usable framework with visible limitations.
Recognition can then attach to a demonstrated contribution rather than the
number of files or the strength of a self-assigned status label.
