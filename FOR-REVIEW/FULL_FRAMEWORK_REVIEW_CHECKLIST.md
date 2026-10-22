# Full Framework review checklist for Opus

**Requested by:** Mac, 22 October 2026. Requested reviewer setting: Opus, xhigh; actual reviewer configuration is not verified by this document.
**Prepared by:** Caelorynth / Codex. **Status: [AWAITING_REVIEW].**
**Framework creator:** Mackenzie Conor James Clark / Lycheetah Framework.
**Target:** the existing Lycheetah-Framework repository, including previous reviewers' work.
**Direction:** independent source review, counterexamples, architecture synthesis and a concrete repair queue.
**Boundary of this handoff:** preparation only. No reviewer was launched and no runtime code was changed by preparing this list.

This is the complete **known review queue and repository coverage scope**, not a claim that every defect has already been discovered. Existing tests, dossiers and Codex assessments are inputs to challenge. A file census, source reading, execution, mathematical proof and independent empirical replication are different levels of evidence.

## Brief to give Opus

> Review Lycheetah-Framework as it actually exists on disk. Include all 50 tracked top-level areas, all 35 root files, the 606-folder coverage ledger and the local FOR-REVIEW proposals. Review Caelorynth's recent changes and Aetheron's proposals with the same scrutiny as older work. Establish what is implemented, what is supported under explicit assumptions, what is an experiment, and what remains philosophy, cultural interpretation or fiction. Trace claims into operators, callers, evidence and failure cases. Start with the highest consequence boundaries below. Record exactly which files you read and which paths you executed. Deliver a prioritized findings register, a coverage ledger, a coherent architecture map, and specific proposed repairs. Do not replace the project with a new website or mistake a new summary for a finished review. Preserve supplied research bytes, authorship, foreign work and sibling seat constitutions. Keep unreviewed work visible. This handoff requests review; applying fixes, committing, pushing, merging and publishing require the applicable authorization from Mac's session.

## Source identity and reading order

The local checkout was inspected on 22 October 2026:

- Branch: `review/full-framework-2026-10-20`.
- HEAD: `d7ae0ad4546c243acdd992a9906f4579b290633b`.
- Earlier review commit: `cf6ff23c39d52de82b8dc191a5fcaab1a04b517a`.
- Original review baseline: `6ba483af3f125ec725eb4e0f44074d0887183255`.
- Current index: **4,847 tracked files, 606 folders, 50 top-level directories, 35 root files**. These are inventory counts, not semantic coverage.
- Existing local work before this handoff: modified `12_IMPLEMENTATIONS/core/lamague_parser.py`; untracked `FOR-REVIEW/` with its README, dossier and three proposals. Preserve it. Record its diff separately from HEAD.
- The 606-folder set still matches the earlier folder receipt, whose file count was 4,837. Do not substitute that older file count for today's index.

Read [AGENTS.md](../AGENTS.md) and applicable nested instructions first. For credibility and framework claims, follow this extraction order:

1. [CLAIMS.json](../28_DEFENSE/CLAIMS.json) and its schema.
2. [DEFENSE_INDEX.json](../28_DEFENSE/DEFENSE_INDEX.json).
3. [EMPIRICAL_INVENTORY.md](../29_GOVERNANCE/EMPIRICAL_INVENTORY.md).
4. [FALSIFICATION_REGISTER.md](../28_DEFENSE/FALSIFICATION_REGISTER.md).
5. [TESTABILITY_MANIFEST.md](../28_DEFENSE/TESTABILITY_MANIFEST.md).
6. [NOVEL_CONTRIBUTIONS.md](../28_DEFENSE/NOVEL_CONTRIBUTIONS.md).
7. [SCOPE_BOUNDARY.md](../28_DEFENSE/SCOPE_BOUNDARY.md).
8. [TRANSLATION_CODEX.md](../28_DEFENSE/TRANSLATION_CODEX.md).
9. Relevant source, prior art and original provenance.

Then challenge the [20–21 October substantive review](../28_DEFENSE/FULL_FRAMEWORK_REVIEW_2026-10-20.md), its [portable evidence](../28_DEFENSE/review_2026_10_20/README.md), [swarm hardening receipt](../28_DEFENSE/review_2026_10_20/swarm-hardening.json), and [Aetheron's LAMAGUE dossier](2026-10-21_LAMAGUE_SWARM_DOSSIER/LAMAGUE_STATE_DOSSIER.md). None is an independent scientific verdict.

## Coverage debt

The earlier [area ledger](../28_DEFENSE/review_2026_10_20/coverage.json) accounts for all 50 areas. The deeper [606-folder ledger](../28_DEFENSE/review_2026_10_20/folder-coverage.json) records **583 census-only folders, 18 targeted-source folders and five ZIP-directory-metadata-only folders**. Targeted reading does not mean complete reading of that folder. Three deeper reviewers were interrupted by a usage limit; a deferred inventory is not a completed review. A later three-reviewer bounded pass completed its own assignments, not the remaining corpus.

Use that folder ledger as the nested queue. For each folder, record files actually read, paths actually executed, findings and remaining work. Include new untracked proposals separately. Do not mark a whole folder reviewed after opening its README. Inspect archives as data before considering execution; metadata inspection does not establish safety, reproducibility or source validity.

## Prioritized workstreams

The labels below describe evidence available **before Opus's review**. “Reported repaired” requires independent re-review. “Reproduced open” means a counterexample is retained; it does not imply deployment exploitation. Priorities are review order, not a fresh severity assessment.

### First: execution, permissions, integrity and architectural boundaries

- [ ] **RV01 — Whole architecture and the requested “third brain.”** Trace the dependency and authority boundaries between `lycheetah/`, `12_IMPLEMENTATIONS/`, `34_ASSURANCE_RUNTIME/`, research versions, memory/compaction and examples. Identify the actual component meant by “third brain” from source and Mac's context; no unique component has yet been established under that name. Show one diagram of data, evidence, approval, execution and recovery. Identify duplicate implementations and version contracts before proposing consolidation.
- [ ] **RV02 — Consensus verdict binding. Reported repaired.** Review `lycheetah/consensus/arena.py`, `lycheetah/sovereign_harness.py` and `tests/test_consensus_integrity.py`: recomputation of the complete v2 verdict digest, anchor/outcome binding, mutation rejection before nonce consumption, permit issuance and dispatch. Check legacy verdict/permit migration. Unkeyed hashes do not authenticate an outside issuer or constrain the owner of the Python process.
- [ ] **RV03 — Consensus numerics and advertised topology. Reported repaired/qualified.** Review `12_IMPLEMENTATIONS/core/psi_consensus.py`, arena admission, MCP formatting and actual `CellularSheaf` callers. Check NaN/Inf, empty/zero/wrong-shaped inputs, H⁰ versus H¹, connectivity proxy versus cohomology, and the unsupported inference from a one-third quarantine budget to Byzantine fault tolerance.
- [ ] **RV04 — Approval, identity, scope and revocation. Review scope.** Trace `lycheetah/assurance/action_guard.py`, gateway, policy, finality and harness from public entry point to executor. Check action/artifact binding, actor/approver separation, delegation, expiry, replay, cross-scope substitutions, approval authentication, revocation timing and post-dispatch limits. Distinguish declared identity from authenticated identity.
- [ ] **RV05 — Durable workflow and dispatch. Reported repaired; broader audit open.** Review `checkpointed_workflow.py`, `checkpoint_authority.py`, `gateway.py`, `finality.py` and replay/checkpoint tests. Verify dirty-tail rejection, reopen behavior, claim-before-dispatch, explicit empty action handling, current-policy checks, crash ordering, duplicate dispatch, rollback and post-effect `UNKNOWN`. Determine the single-writer, filesystem and process-control assumptions. Never label a missing result checkpoint as success.
- [ ] **RV06 — Policy and receipt reference integrity. Reported repaired.** Review `policy.py`, `receipt.py`, gateway and their tests. Constructor lists and nested rules must be detached; callbacks must not rewrite the evaluated policy reference. Check policy-decision versus execution-status separation, failure/timeout/review-approved receipts, schema event shape, action digest, actor/scope, privacy and replay metadata. Trace verification to actual dispatch.
- [ ] **RV07 — Context snapshots, drift and hashes. Reported repaired; threat boundary open.** Review `lycheetah/compaction/shield.py`, `lycheetah/handoff.py` and dependent consumers. Exported nested structures must not mutate their live accumulator or vice versa. Review all protected and unprotected packet fields, including risk/evidence/horizon/yield, not just the ten-field critical hash. Define what drift detection can and cannot detect; test missing, altered, reordered and stale context. Reject universal claims of protection from context loss.
- [ ] **RV08 — Exact codec/consent preservation. Maintained repair; frozen defect open.** Compare `lycheetah/compaction/codec.py` with frozen `03_LAMAGUE_L1/22_REVERSIBLE_COMPRESSION_v1.0/src/lamague_codec.py`. Literal `R`, `I`, `N` previously changed consent and packet/hash values. Check both wire modes, every admitted value, lossless packet scope, malformed input and backward compatibility. Preserve the frozen counterexample; do not repair a research archive silently.
- [ ] **RV09 — Exported evidence bundle and independent verifier. Reported repaired.** Review `examples/guarded_handoff_risk_demo.py`, its verifier and bundle tests. Check all eight evidence files plus manifest, task/completion/context/action/output/permit/receipt/report cross-links, duplicate JSON keys, FIFOs/symlinks/nonregular paths, omitted files, contradictory reports and no-overwrite behavior. A retained manifest digest is needed to detect a completely self-consistent rewrite. Synthetic consensus, declared approval, trusted writer and arbitrary callback limitations remain.
- [ ] **RV10 — Chorus false assurance. Reproduced open.** `19_MULTI_AGENT_CHORUS/run_chorus.py` reports nine absent agents online and returns a canned clean audit. Trace real agent invocation, health probes and audit inputs. Either design and demonstrate a real implementation or keep the entire path explicitly scaffolded. A healthy-looking fixture cannot establish operational assurance.
- [ ] **RV11 — Policy-evolution duplicate groups. Reproduced open.** `papers/agent-safety/frontier-controls/06_hazard_lineage_policy_evolution_v1_2/policy_evolution_gate.py`: dictionary collapse of duplicate group IDs disagrees with formula evaluation and can classify an allow-broadening sequence as `EQUIVALENT`. Review admissibility, canonicalization and semantic equivalence. Existing evidence establishes a classifier counterexample, not remote policy activation.
- [ ] **RV12 — Anon Politician review admission. Reproduced open.** `23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/07_POLICY_LAB_v0.2/Anon_Politician_Policy_Lab_v0_2/evaluation/aggregate_reviews.py`: mixed case IDs are accepted; duplicate reviews inflate ratings while unique reviewer count stays one. Review experiment/case/reviewer identity, deduplication, provenance, aggregation denominators and rejection controls before any study relies on it.

### Then: implementation, language, mathematics and research

- [ ] **RV13 — Every implementation module, including Gemini-authored work. Partial coverage.** Review all 55 Python files under `12_IMPLEMENTATIONS/`: 30 core, ten applications, five experiments, four systems and six root files. Earlier AST parsing established syntax only. Trace exports, dynamic loading, demos and production callers. Check silent fallbacks, placeholder results, synthetic data, random seeds, numerical boundaries, dependencies and actual tests. Re-review TRIAD small-step/gradient convergence and atomic state/history updates; TRI-AXIAL incomplete-vector/negative-count/negative-friction/NaN/overflow admission; and MCP error behavior. Calibration remains separate from input validation.
- [ ] **RV14 — Local parser patch and grammar conformance. Proposal/dirty implementation.** Review the actual working diff of `12_IMPLEMENTATIONS/core/lamague_parser.py`, not only the illustrative proposal. It also changes pipe handling and tokenizer classification. Check complete consumption, unknown input, parentheses, precedence, associativity, modifiers, recursion and constraint validation. Specifically test whether everything after `|` is validated or ignored. Compare the [parser proposal](2026-10-21_PROPOSALS/01_PARSER_SILENT_DROP_PATCH_PROPOSAL.md) and [BNF proposal](2026-10-21_PROPOSALS/02_BNF_GRAMMAR_HARMONIZATION_PROPOSAL.md) against `03_LAMAGUE_L1/04_BNF_GRAMMAR.md` and both parsers. “33 checks pass” is not coverage of the added behavior. Reconcile contradictory approval/footer status text with Mac's actual authorization record.
- [ ] **RV15 — LAMAGUE version and formal-language map. Review scope.** Audit every submodule of `03_LAMAGUE_L1/`, its status register, foundational BNF, CORE algebra/ontology/operator algebra, Native36/1C, runtime versions, packet codec and retired kernel. Reconcile glyph and phonetic inventories, competing productions, `Φ↑`, `_inv`, pipe and middle-dot meanings, three uses of Psi, semantics and interpreter behavior. Treat the dossier's counts and “all verified” assertions as claims requiring evidence. Include `24_LAMAGUE_CHECK`: Unicode/empty-key/reverse-suffix false positives were repaired but semantic accountability is not proved by field presence.
- [ ] **RV16 — SXP-L and the authority-bridge proposal. Eight reported open limitations.** Review `03_LAMAGUE_L1/26_SXP_L_RESEARCH/audit_known_limitations.py`, v2.0 parser/runtime/compact code and study protocol. Reproduce all eight findings, not just the two targeted by the [revocation proposal](2026-10-21_PROPOSALS/03_SXPL_AUTHORITY_BRIDGE_REVOCATION_PROPOSAL.md). Check denials, revocations, scope and issuer authentication, repair references, chronology/cycles, superseded statements, missing Native36 operators and `ti ariva.` compaction. A speech repair is not automatically an authenticated permission change. No genuine participant outcome is established.
- [ ] **RV17 — Compression and interoperability claims. Review scope.** Recheck retracted 500:1/3000:1 aspirations, reported token/character ratios and warm held-out byte results. State codebook cost, cold/warm conditions, tokenizer, corpus, held-out split, schema overhead, denominator, baselines and failure cases. Exact structured-packet reversibility does not prove arbitrary natural-language meaning preservation or cross-model understanding. Recheck unique-decodability and merged phonemes independently.
- [ ] **RV18 — All foundational mathematical arguments. Earlier counterexamples; re-review required.** Review all nine frameworks, `11_MATHEMATICAL_FOUNDATIONS/`, `30_MAPS/FORMAL_SPINE.md` and source-to-code bridges. The 18 finding groups are listed below. State domains, operators, norms, assumptions, proof and counterexample precisely. Do not repair a theorem by silently changing what it claims. Reproduce pinned historical probes against their baseline, then separately assess current source.
- [ ] **RV19 — All 71 claim rows and evidence chains. Known gaps.** Reassess statement, author status, dependencies, prior art, evidence existence, actual entailment and falsification condition. Separate definitions, conditional results, measured effects, software contracts, proposals and refuted statements. The 14 earlier pointer repairs preserved author labels; they did not establish the claims. Resolve or explicitly mark the 23 missing references below; 16 rows still have no existing pointer. Examine register mirrors and citations, not just total-count agreement.
- [ ] **RV20 — Cellular sheaf and factorial experiment. Unresolved scientific inference.** Review the actual coboundary, Hodge Laplacian, SVD rank cutoff, harmonic projection, boundary constraints and encoded contradictions. Floating-point truncated certificates are not arbitrary exact algebra. In `TRUTH_PRESSURE/EXPERIMENTS/GLASS_TRANSITION/`, inspect all eight factorial cells, randomization, paid-work accounting, censoring and baselines. `work_coupled` estimates at start and recomputes against the later live store; it lacks a receipt that every completion paid actual work. Reassess the existing sheaf/experimental critique rather than accepting a green diagnostic as causal proof.
- [ ] **RV21 — Truth Pressure and cybernetics. Uncalibrated constructs.** Review all versioned `TRUTH_PRESSURE/` instruments, `34_CYBERNETICS/`, `32_TIANXIA/` and their maintained bridges. Weights, semantic encodings, thresholds and proxy feedback need calibration and ground truth. The 100-record shadow corpus is synthetic. Separate engineering checks, simulation, correlation and intervention evidence. Check the master-equation derivation and baseline ties; closed-loop control of a proxy does not establish ethical or factual sensing.
- [ ] **RV22 — Agent-safety papers and versioned continuations. Review scope.** Review frontier controls, Earned Trust, Hybrid Gateway, Earned Light, Sovereign Choice/Will and imports. Map each paper to its exact runtime/version, assumptions, threats and experiments. Preserve trust-root failures, recovery/export ties, 18/18 goal-aware baseline ties, fictional reachability cases and negative/null results. Do not add overlapping historical test counts as independent evidence or promote frozen continuations into the installed runtime.
- [ ] **RV23 — Empirical programme and scoring. Outside validation open.** Review all seven study designs in `31_EMPIRICAL/`, text-scoring methods/reports in `33_APPLICATIONS/`, real versus synthetic datasets, split leakage, baselines, confidence intervals, effect sizes, multiple comparisons and publication/preregistration status. Preserve null social-engineering separation and failed transfer to independent-publisher human comments. Project-run external-data evaluation is not independent replication. Propose a measurable outside workflow with a conventional baseline, user benefit, review burden and failure handling; do not recruit or call paid providers under review-only authority.
- [ ] **RV24 — NZ governance and policy coherence. Current proposal versus history.** Review all `23_NZ_AI_GOVERNANCE/`, including the six-rights proposal, 26 historical cultural-policy drafts, background candidates and Anon Politician. Check for conflicting current recommendations and legal/adoption language throughout linked folders. The six rights are a proposal. For current law and government-policy findings, consult primary official sources and date the finding. Distinguish Privacy Act access/overseas-disclosure scope, proposed withdrawal/human-review/location receipts, actual implementation and government adoption. Civic metadata validation does not prove representative sampling or better policy outcomes.
- [ ] **RV25 — Māori and cross-cultural claims. External expertise open.** Review `24_LAMAGUE_CROSS_CULTURAL/`, `32_TIANXIA/`, NZ drafts and linked foundational prose. Inspect whakapapa, tikanga, sovereignty, Wu Chang mappings, Chinese terminology, attribution, claimed independence, community permission, endorsements, partnerships and outreach status. An analogy or mathematical mapping is not cultural identity or endorsement. State where knowledgeable human/community review is still required rather than inventing agreement.
- [ ] **RV26 — Mystery School, learning, psychological and consciousness claims. Partial source review.** Review `14_MYSTERY_SCHOOL/`, `17_LEARNING_EMERGENCE/`, application curricula and related essays. Check for remaining diagnostic certainty, necessary suffering, guaranteed recovery, theorem-to-therapy leaps, unsupported learning gains and consciousness claims. Re-review the notices on `THE_FIRST_MAP.md` and `THE_THERAPISTS_DOOR.md` without deleting original bodies. Distinguish educational design, philosophy, fiction, empirical evidence and clinical claims. Mathematical convergence is not a clinical result.
- [ ] **RV27 — Memory, identity and AI-facing architecture. Review scope.** Review `16_SOL_VEYRA_ARCHITECTURE/`, `21_MEMORIA/`, `22_INTERFACE_INTELLIGENCE/`, `25_SOL_PROTOCOL_ARCHITECTURE/`, `26_FOR_AI/` and integration paths. Trace actual persistence, retrieval, invalidation, provenance, correction, user control and portability. Distinguish reconstructable functional identity from claims about weights, platform authority, consciousness or episodic memory. Read sibling constitutions for context; propose changes without silently editing them.
- [ ] **RV28 — Creative corpus and source ownership. Census is not literary review.** Review `35_ABSTRACT_AND_GENERATIVE/`, `LYCHEETAH_EPIC/`, `LYCHEETAH_MYTHOS/` and Lighthouse/story imports for intended status, chronology, duplication, source fidelity, canon decisions and correct reading routes. Preserve original authorship and epic depth. Story validators do not establish literary quality, native application behavior or educational outcomes; keep those questions separate.

### Finally: navigation, preservation, security and release readiness

- [ ] **RV29 — All READMEs, synthesis and current navigation. User-requested debt.** Review root entry points, every folder's purpose/version/status, `13_SYNTHESIS_REPORTS/`, `30_MAPS/`, `docs/`, `WORKING_HOME.md`, quickstarts and package examples. Produce a current “what lives where and what actually works” map. Find stale promises, duplicate truth sources, contradictory dates/counts, dead links and inaccessible local paths. Preserve history through clear status and links. The BNF proposal currently contains a nonportable `file://~/...` link. A new website is outside this review task.
- [ ] **RV30 — Lint, claim-footing and validator design. Known gate failures.** Reassess the six-file/46-finding lint backlog and all 79 unmarked documents listed below. Classify claims substantively; adding a status word solely to satisfy a regex is insufficient. Some documents may deserve a justified scope decision rather than an empirical label. Do not raise the fixed footing budget of 30, weaken collection or suppress archived failures to get green. Audit validators with known bad and benign controls and inspect examined counts.
- [ ] **RV31 — Archive and import portability. Reproduced open gap.** Review `99_ARCHIVE/closed_loop_agent_lab/`: 1,788 manifest entries pass locally, but 374 log references are absent from Git; 373 exact byte matches were located in tracked ZIPs and one companion retest log was local-only. Review clean-checkout recovery and the missing `04_COMPANION_RECORDS/standalone_package_retest_v5.1.log`. Earlier inspection of 87 ZIP directories and 25,538 members was metadata only. Review all archive scope, stale links and frozen preservation rules. Wire the later 225-file import into `tools/verify_research_intake.py`; its existing automatic gate covers 444 earlier files. Preserve manifests and supplied licenses.
- [ ] **RV32 — Desktop and application reality. Build/render/security unverified.** Re-review the provider race repair in `cascade-pc/src/scoring/ai.js` and three mocked tests, then assess the actual Electron build and user flow if authorized. Review unauthenticated localhost read API, origin/network exposure, browser-local API key storage, IPC, dependencies and distribution threat model. Trace `27_SOL_AI_APP/` as an external pointer rather than assuming it is this repository's implementation. Local scoring tests do not establish rendering, provider integration or cross-platform operation.
- [ ] **RV33 — Packaging, tests, CI and migration. Full release gates remain open.** Review `pyproject.toml`, dependency bounds/extras, wheel/sdist contents, schemas/resources, all 11 commands, source-only boundaries, .github workflows, MCP registration and current Python/platform support. Reconcile the dated whole suite with later focused-only runs. Inspect the strict CASCADE expected failure and its unattainable F1 criterion rather than hiding it. Check consensus v2 migration, strict consent inputs, normalized policy collections and dirty-ledger reconciliation. No hosted CI pass was observed in the prior handoff; verify current hosted status before any new claim. A wheel run reusing installed dependencies is not clean dependency resolution.
- [ ] **RV34 — Licensing, attribution and publication metadata. Owner decision needed.** Compare root `LICENSE`, `CONTRIBUTING.md`, attribution guidance, supplied subproject licenses, `CITATION.cff`, package version, Zenodo/arXiv language and release notes. Plain MIT text conflicts with references to an extra Earned Sovereignty Clause and additional mandatory conditions. Explain the conflict and options for Mac; do not silently choose a license or remove authorship. Distinguish drafts, submissions, releases and accepted publications.
- [ ] **RV35 — Security and privacy across public surfaces. Review scope.** Review `SECURITY.md`, dependency/secret handling, logs, fixtures, exports, local absolute links, personal material, public bundles and build artifacts. Review `15_PERSONAL_VAULT/` for publication boundaries without copying sensitive contents into the report. Scanning a working tree is different from scanning the exact pending publication diff. Publication requires its own authorized gate; this checklist does not authorize disclosure.
- [ ] **RV36 — Audit the auditors and their receipts. Essential.** Review `28_DEFENSE/`, the 32 dated source notices, claimed original-body preservation, all review JSON, scripts, tests and coverage labels. Check collection counts, source hashes, baseline pins, positive/negative controls, skipped/failed/not-run distinctions, synthetic or hardcoded verdicts and source-to-runtime reachability. Challenge my classifications and code. Repository self-validation and agreement between AI reviewers do not establish independent scientific validation.
- [ ] **RV37 — Interrupted-review leads. Not established findings.** Locate and reproduce or dismiss: frontier finality outbox payload versus bound Action; ResearchPipeline promotion of a single “real-ish” RCT to FOUNDATION; TitleReceipt reporting EARNED without bearer choice/evidence; Five-Fold Hexie's “greatest marginal” claim versus its linear average. Only the last source was located during handoff preparation (`32_TIANXIA/implementations/hexie_five_fold.py`, `FIVE_FOLD_HEXIE_COMPOSITE.md`). The other names were not resolved in the bounded source search. Do not report them as confirmed defects without locating the exact source/version and reproducing the behavior.

## Mathematical checklist: all 18 earlier finding groups

Use the [main review's table](../28_DEFENSE/FULL_FRAMEWORK_REVIEW_2026-10-20.md), [pinned probe receipt](../28_DEFENSE/review_2026_10_20/math-probes.json) and [reproduction instructions](../28_DEFENSE/review_2026_10_20/README.md). MP01–MP18 are runnable observations; the review's M1–M18 grouping also includes source arguments and novelty limits. “REPRODUCED” means the reviewer's observation reproduced, not that the author's theorem passed.

| Earlier ID | Review target |
|---|---|
| M1 | TRIAD entropy-Hessian/Jacobian sign and the claimed local contraction. |
| M2 | Noncommuting generator bound versus actual eigenvalue stability. |
| M3 | Stationary minima, distinct fixed points, step size, uniqueness and Banach hypotheses. |
| M4 | Low-entropy set convexity and the claimed unitarity of implemented ascent. |
| M5 | Spectral norm/rank confusion, universal square-root threshold and impossible nonreal eigenpair of a real symmetric matrix. |
| M6 | Master ODE's actual shifted equilibrium, Lyapunov derivative and claimed threshold transition. |
| M7 | Sovereignty/drift agreement versus ethical compliance; explicit compliant-intention assumption. |
| M8 | Preserving CASCADE records versus preserving their FOUNDATION membership. |
| M9 | Record retention versus Shannon entropy, including different uncertainty metadata. |
| M10 | TES lower bound and VTR value-versus-cost inference. |
| M11 | Chrysopoeia coherence monotonicity and a stochastic composition versus deterministic contraction. |
| M12 | Harmonia's narrow comma result versus universal ratio claim and inconsistent formula/table/proxy. |
| M13 | Reversible adiabatic work, entropy change and physical versus dimensionless information units. |
| M14 | AGM postulates, logical closure and consistency of the actual represented store. |
| M15 | Gödel hypotheses, all-model semantics and first-order completeness. |
| M16 | Anamnesis's assumed global attractor and unsupported metaphysical/historical conclusions. |
| M17 | “11/11 verified,” fixed-table Hessians and a separate 5,000-trial toy versus actual maintained engines. |
| M18 | Novelty, normalization, construct validity, universal/first/only claims and primary prior art. |

## Required review outputs and completion rule

1. **Findings register:** ID, priority/severity, exact file and line/version, observation, reproduction or primary source, actual consequence, confidence, affected callers, proposed fix, acceptance criterion and remaining assumptions. Keep confirmed findings, interpretation and leads distinct. Link earlier finding IDs instead of silently dropping them.
2. **Coverage ledger:** all tracked areas/folders/root files plus local proposals; name files read and paths executed. Label census-only, metadata-only, source-reviewed, exercised and deferred separately. Attach counts that reconcile to the inspected tree; do not call the review complete while unexamined scope is hidden.
3. **Architecture synthesis:** actual current data/authority flow, component ownership, version/dependency map, duplicate implementations, integration gaps and the resolved “third brain” referent if evidence allows it.
4. **Claim/evidence reconciliation:** all 71 claims, exact remaining missing references, code/proof/measurement relationships, uncertainty and prior-art status. Avoid promoting an author status to a reviewer result.
5. **Repair sequence:** immediate consequential defects, bounded implementation improvements, documentation coherence, preservation/release gates, and questions reserved for Mac or qualified external reviewers. Make each proposed patch reviewable before seeking consequential approval.
6. **Final report:** what survived, what failed, what was not examined, what did not run, and what requires outside validation. Describe useful contributions plainly while preserving Lycheetah's authorship and creative depth.

Use isolated copies for fault injection. Read counts as well as verdicts; a known bad input must fail and a benign control must pass. Never turn a crash, collection failure, skip, filtered test or missing dependency into a green result. Keep one resource-heavy process at a time. Browsing for live legal facts, novelty or technical literature must use current primary sources and precise citations. This handoff itself performs no new external research or full test run.

## Earlier verification: dated context, not Opus's result

| Date / receipt | What was reported | Limit |
|---|---|---|
| 20 October, `verification.json` | 999 maintained cases collected: 997 passed, one skipped, one strict expected failure. | Local Python 3.12; not external replication or current whole-suite execution. |
| 21 October, deeper pass | 64 distinct new boundary cases; 42 before-fix failures. Focused runs of 167, seven and 92 overlap. | Whole suite was not rerun for that extension. |
| 21 October, `swarm-hardening.json` | 329 focused cases passed; 90 new cases, comprising 36 snapshots, 18 gateway/policy and 36 bundle cases. | Local engineering checks; no whole-corpus certification. |
| Previous package checks | Public mypy covered 30 files; all 55 implementation Python files AST-parsed; isolated wheel/command checks. | Not all source typechecked/executed; latest wheel witness reused installed dependencies. |
| Earlier research checks | Modelcraft 17; Book I ten plus validator; Anon Politician 43 checks and 121 checksum entries; Truth Pressure 24/14/11/11; MCP integration five; desktop three mocked cases. | Different instruments and scopes; these counts are not independent studies. |
| Previous release checks | 46 corpus lint findings; footing 79 against budget 30; 22 archive dead links; no hosted CI pass claimed. | Existing blockers remain until independently checked or resolved. |

The following appendices enumerate current review targets. Their presence is a queue, not a completed assessment.

## Appendix A: all 50 tracked top-level areas

Counts are from the current index on 22 October. The earlier inspection column is a historical label from the 20 October area ledger, not a completion claim. Every row remains in scope for Opus.

| Area | Tracked files now | Earlier area-level inspection |
|---|---:|---|
| [.github/](../.github/) | 11 | `WORKFLOW_SOURCE_REVIEW` |
| [000_1404RawSourceTranslate/](../000_1404RawSourceTranslate/) | 45 | `HISTORICAL_SOURCE_CENSUS` |
| [00_GENESIS/](../00_GENESIS/) | 15 | `HISTORICAL_SOURCE_CENSUS` |
| [01_CASCADE_L4/](../01_CASCADE_L4/) | 4 | `FOUNDATIONAL_SOURCE_REVIEW` |
| [02_AURA_L3/](../02_AURA_L3/) | 9 | `FOUNDATIONAL_SOURCE_REVIEW` |
| [03_LAMAGUE_L1/](../03_LAMAGUE_L1/) | 1042 | `SOURCE_AND_CONTRACT_REVIEW` |
| [04_TRIAD_L2/](../04_TRIAD_L2/) | 3 | `FOUNDATIONAL_SOURCE_REVIEW` |
| [05_MICROORCIM_L5/](../05_MICROORCIM_L5/) | 3 | `FOUNDATIONAL_SOURCE_REVIEW` |
| [06_EARNED_LIGHT_L0/](../06_EARNED_LIGHT_L0/) | 3 | `FOUNDATIONAL_SOURCE_REVIEW` |
| [07_ANAMNESIS_L0/](../07_ANAMNESIS_L0/) | 4 | `FOUNDATIONAL_SOURCE_REVIEW` |
| [08_INTEGRATIONS/](../08_INTEGRATIONS/) | 4 | `ARCHITECTURE_SOURCE_REVIEW` |
| [09_CHRYSOPOEIA_L4/](../09_CHRYSOPOEIA_L4/) | 3 | `FOUNDATIONAL_SOURCE_REVIEW` |
| [10_HARMONIA_L6/](../10_HARMONIA_L6/) | 3 | `FOUNDATIONAL_SOURCE_REVIEW` |
| [11_MATHEMATICAL_FOUNDATIONS/](../11_MATHEMATICAL_FOUNDATIONS/) | 20 | `FORMAL_SOURCE_AND_COUNTEREXAMPLES` |
| [12_IMPLEMENTATIONS/](../12_IMPLEMENTATIONS/) | 62 | `SOURCE_AND_RUNTIME_CONTRACTS` |
| [13_SYNTHESIS_REPORTS/](../13_SYNTHESIS_REPORTS/) | 4 | `ARCHITECTURE_SOURCE_REVIEW` |
| [14_MYSTERY_SCHOOL/](../14_MYSTERY_SCHOOL/) | 124 | `SOURCE_AND_CONTRACT_REVIEW` |
| [15_PERSONAL_VAULT/](../15_PERSONAL_VAULT/) | 21 | `ROLE_AND_LINEAGE_CENSUS` |
| [16_SOL_VEYRA_ARCHITECTURE/](../16_SOL_VEYRA_ARCHITECTURE/) | 6 | `ROLE_AND_LINEAGE_CENSUS` |
| [17_LEARNING_EMERGENCE/](../17_LEARNING_EMERGENCE/) | 2 | `SOURCE_ROLE_AND_CENSUS` |
| [18_EXPERIMENTAL/](../18_EXPERIMENTAL/) | 51 | `SOURCE_ROLE_AND_CENSUS` |
| [19_MULTI_AGENT_CHORUS/](../19_MULTI_AGENT_CHORUS/) | 14 | `SOURCE_AND_FALSE_GREEN_PROBE` |
| [20_DOMAIN_SPECIALISTS/](../20_DOMAIN_SPECIALISTS/) | 3 | `SOURCE_ROLE_AND_CENSUS` |
| [21_MEMORIA/](../21_MEMORIA/) | 2 | `SOURCE_ROLE_AND_CENSUS` |
| [22_INTERFACE_INTELLIGENCE/](../22_INTERFACE_INTELLIGENCE/) | 2 | `SOURCE_ROLE_AND_CENSUS` |
| [23_NZ_AI_GOVERNANCE/](../23_NZ_AI_GOVERNANCE/) | 160 | `POLICY_SOURCE_AND_PROTOTYPE_CONTRACTS` |
| [24_LAMAGUE_CROSS_CULTURAL/](../24_LAMAGUE_CROSS_CULTURAL/) | 16 | `INTERPRETIVE_SOURCE_REVIEW` |
| [25_SOL_PROTOCOL_ARCHITECTURE/](../25_SOL_PROTOCOL_ARCHITECTURE/) | 9 | `ROLE_AND_LINEAGE_CENSUS` |
| [26_FOR_AI/](../26_FOR_AI/) | 24 | `EXTRACTION_ROLE_REVIEW` |
| [27_SOL_AI_APP/](../27_SOL_AI_APP/) | 1 | `EXTERNAL_POINTER_CENSUS` |
| [28_DEFENSE/](../28_DEFENSE/) | 65 | `COMPLETE_REGISTER_POINTER_AUDIT` |
| [29_GOVERNANCE/](../29_GOVERNANCE/) | 9 | `GOVERNANCE_SOURCE_REVIEW` |
| [30_MAPS/](../30_MAPS/) | 11 | `FORMAL_SOURCE_AND_COUNTEREXAMPLES` |
| [31_EMPIRICAL/](../31_EMPIRICAL/) | 8 | `STUDY_DESIGN_SOURCE_REVIEW` |
| [32_TIANXIA/](../32_TIANXIA/) | 37 | `SOURCE_AND_MAINTAINED_CONTRACTS` |
| [33_APPLICATIONS/](../33_APPLICATIONS/) | 17 | `METHOD_AND_DATED_REPORT_REVIEW` |
| [34_ASSURANCE_RUNTIME/](../34_ASSURANCE_RUNTIME/) | 65 | `SOURCE_AND_RUNTIME_CONTRACTS` |
| [34_CYBERNETICS/](../34_CYBERNETICS/) | 5 | `SOURCE_AND_MAINTAINED_CONTRACTS` |
| [35_ABSTRACT_AND_GENERATIVE/](../35_ABSTRACT_AND_GENERATIVE/) | 34 | `CREATIVE_ROLE_CENSUS` |
| [99_ARCHIVE/](../99_ARCHIVE/) | 1497 | `PRESERVED_ARCHIVE_CENSUS` |
| [LYCHEETAH_EPIC/](../LYCHEETAH_EPIC/) | 70 | `CREATIVE_ROLE_CENSUS` |
| [LYCHEETAH_MYTHOS/](../LYCHEETAH_MYTHOS/) | 140 | `SOURCE_FIDELITY_CONTRACTS_AND_ROLE` |
| [TRUTH_PRESSURE/](../TRUTH_PRESSURE/) | 290 | `SOURCE_AND_ENGINEERING_CONTRACTS` |
| [cascade-pc/](../cascade-pc/) | 48 | `SOURCE_AND_MOCKED_REGRESSION` |
| [docs/](../docs/) | 39 | `SOURCE_AND_ARTIFACT_ROLE_REVIEW` |
| [examples/](../examples/) | 21 | `SOURCE_AND_ARTIFACT_ROLE_REVIEW` |
| [lycheetah/](../lycheetah/) | 38 | `SOURCE_AND_RUNTIME_CONTRACTS` |
| [papers/](../papers/) | 676 | `SOURCE_AND_PROVENANCE_REVIEW` |
| [tests/](../tests/) | 67 | `MAINTAINED_EXECUTION` |
| [tools/](../tools/) | 5 | `GATE_SOURCE_AND_EXECUTION` |

The complete nested list is the [606-folder ledger](../28_DEFENSE/review_2026_10_20/folder-coverage.json). Its folder paths match the current index; its per-folder file counts and inspection states remain the dated 21 October snapshot. Review the root itself and the untracked `FOR-REVIEW/` queue in addition.

## Appendix B: all 35 tracked root files

Review entry points, executable/configuration files and publication metadata. For sibling seat instructions, record findings and propose changes; do not silently rewrite their constitutional material.

- [ ] [.gitattributes](../.gitattributes)
- [ ] [.gitignore](../.gitignore)
- [ ] [.pre-commit-config.yaml](../.pre-commit-config.yaml)
- [ ] [00_Sovereign_Index.md](../00_Sovereign_Index.md)
- [ ] [AGENTS.md](../AGENTS.md)
- [ ] [AURA_CONSTITUTIONAL_ENFORCEMENT-1.md](../AURA_CONSTITUTIONAL_ENFORCEMENT-1.md)
- [ ] [CHANGELOG.md](../CHANGELOG.md)
- [ ] [CITATION.cff](../CITATION.cff)
- [ ] [CLAUDE.md](../CLAUDE.md)
- [ ] [CLAUDE_AUGMENTED.md](../CLAUDE_AUGMENTED.md)
- [ ] [CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md)
- [ ] [CONTRIBUTING.md](../CONTRIBUTING.md)
- [ ] [DEFENSE_BUNDLE.pdf](../DEFENSE_BUNDLE.pdf)
- [ ] [EXPLORE_WITH_AI.md](../EXPLORE_WITH_AI.md)
- [ ] [FIVE_MINUTE_BRIEF.md](../FIVE_MINUTE_BRIEF.md)
- [ ] [INTERFACE_INTELLIGENCE_MASTER_2026-09-26.pdf](../INTERFACE_INTELLIGENCE_MASTER_2026-09-26.pdf)
- [ ] [LICENSE](../LICENSE)
- [ ] [LINEAGE.md](../LINEAGE.md)
- [ ] [OPUS_MASTER_PLAN_2026.md](../OPUS_MASTER_PLAN_2026.md)
- [ ] [Procfile](../Procfile)
- [ ] [QUICKSTART.md](../QUICKSTART.md)
- [ ] [README.md](../README.md)
- [ ] [SECURITY.md](../SECURITY.md)
- [ ] [START_HERE_FORGE_CHECKPOINT_2026-08-22.md](../START_HERE_FORGE_CHECKPOINT_2026-08-22.md)
- [ ] [THE_SOL_PROTOCOL.md](../THE_SOL_PROTOCOL.md)
- [ ] [VISUAL_IDENTITY.md](../VISUAL_IDENTITY.md)
- [ ] [WORKING_HOME.md](../WORKING_HOME.md)
- [ ] [ZENODO_RELEASE_v1.md](../ZENODO_RELEASE_v1.md)
- [ ] [ai-meta.json](../ai-meta.json)
- [ ] [demo.py](../demo.py)
- [ ] [generate_defense_bundle.py](../generate_defense_bundle.py)
- [ ] [llms.txt](../llms.txt)
- [ ] [promote.py](../promote.py)
- [ ] [pyproject.toml](../pyproject.toml)
- [ ] [requirements.txt](../requirements.txt)

## Appendix C: all 23 currently missing claim-evidence references

These are literal pointer-existence gaps recomputed from the 71-row register on 22 October. Repeated paths represent distinct claim references. A replacement must support that exact statement; do not create placeholder proofs.

| Claim | Missing literal reference |
|---|---|
| `CAS-003` | `01_CASCADE_L4/CASCADE_THEOREMS.md` |
| `CAS-004` | `01_CASCADE_L4/CASCADE_THEOREMS.md` |
| `CAS-005` | `01_CASCADE_L4/CASCADE_THEOREMS.md` |
| `CAS-006` | `01_CASCADE_L4/CASCADE_THEOREMS.md` |
| `CAS-008` | `01_CASCADE_L4/CASCADE_THEOREMS.md` |
| `CAS-009` | `01_CASCADE_L4/implementations/` |
| `CAS-010` | `01_CASCADE_L4/implementations/` |
| `CAS-011` | `01_CASCADE_L4/implementations/` |
| `AUR-009` | `02_AURA_L3/AURA_THEOREMS.md` |
| `LAM-003` | `03_LAMAGUE_L1/LAMAGUE_THEOREMS.md` |
| `LAM-004` | `03_LAMAGUE_L1/LAMAGUE_THEOREMS.md` |
| `TRI-003` | `04_TRIAD_L2/TRIAD_THEOREMS.md` |
| `TRI-004` | `04_TRIAD_L2/TRIAD_THEOREMS.md` |
| `TRI-005` | `04_TRIAD_L2/TRIAD_THEOREMS.md` |
| `TRI-006` | `04_TRIAD_L2/TRIAD_THEOREMS.md` |
| `TRI-007` | `04_TRIAD_L2/TRIAD_THEOREMS.md` |
| `MIC-003` | `05_MICROORCIM_L5/MICROORCIM_THEOREMS.md` |
| `ANA-002` | `07_ANAMNESIS_L0/TC_CATALOG.md` |
| `ANA-003` | `07_ANAMNESIS_L0/TC_CATALOG.md` |
| `ANA-004` | `07_ANAMNESIS_L0/TC_CATALOG.md` |
| `CRY-002` | `08_CHRYSOPOEIA/CHRYSOPOEIA_THEOREMS.md` |
| `CRY-003` | `08_CHRYSOPOEIA/CHRYSOPOEIA_THEOREMS.md` |
| `CRY-004` | `08_CHRYSOPOEIA/CHRYSOPOEIA_THEOREMS.md` |

The **16 rows with no existing evidence pointer** are: `CAS-003`, `CAS-004`, `CAS-005`, `CAS-006`, `AUR-009`, `LAM-003`, `LAM-004`, `TRI-003`, `TRI-004`, `TRI-005`, `TRI-007`, `ANA-003`, `ANA-004`, `CRY-002`, `CRY-003`, `CRY-004`.

## Appendix D: six files carrying the earlier 46 lint findings

The [baseline-comparison receipt](../28_DEFENSE/review_2026_10_20/lint-baseline-comparison.json) records 46 findings in unchanged sources. File names were read back for this handoff; lint was not rerun. Determine the frozen-source repair/qualification strategy before editing.

- [ ] [03_LAMAGUE_L1/25_RESEARCH_CYCLE_23_POST_CRASH_OBSERVATION/src/bridge_v0_2.py](../03_LAMAGUE_L1/25_RESEARCH_CYCLE_23_POST_CRASH_OBSERVATION/src/bridge_v0_2.py)
- [ ] [03_LAMAGUE_L1/25_RESEARCH_CYCLE_23_POST_CRASH_OBSERVATION/tests/test_cycle23.py](../03_LAMAGUE_L1/25_RESEARCH_CYCLE_23_POST_CRASH_OBSERVATION/tests/test_cycle23.py)
- [ ] [34_ASSURANCE_RUNTIME/action_guard/versions/v0.6/run_verification.py](../34_ASSURANCE_RUNTIME/action_guard/versions/v0.6/run_verification.py)
- [ ] [34_ASSURANCE_RUNTIME/action_guard/versions/v0.7/run_verification.py](../34_ASSURANCE_RUNTIME/action_guard/versions/v0.7/run_verification.py)
- [ ] [34_ASSURANCE_RUNTIME/action_guard/versions/v0.8/run_verification_v07.py](../34_ASSURANCE_RUNTIME/action_guard/versions/v0.8/run_verification_v07.py)
- [ ] [papers/agent-safety/earned-light/forges_01_07/Forge_06/right_of_return.py](../papers/agent-safety/earned-light/forges_01_07/Forge_06/right_of_return.py)

## Appendix E: all 79 documents currently flagged as unmarked

Recomputed on 22 October using the existing `tools/verify-claims.py` scopes, minimum size, marking expressions and exact-byte inherited research footing. The automatic intake verifier examined 444 files. Fixed budget: **30**. A document appearing here is a marker/scope review target, not proof that its claims are false. Review its content before proposing a qualification or a justified exemption. Preserve frozen imports.

1. [ ] [23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/00_START_HERE/README_FOR_NEXT_MODEL.md](../23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/00_START_HERE/README_FOR_NEXT_MODEL.md)
2. [ ] [23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/01_MASTER_SPEC/Anon_Politician_Master_Handoff_v1.0.md](../23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/01_MASTER_SPEC/Anon_Politician_Master_Handoff_v1.0.md)
3. [ ] [23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/01_MASTER_SPEC/CONTINUATION_ADDENDUM_v1.2.md](../23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/01_MASTER_SPEC/CONTINUATION_ADDENDUM_v1.2.md)
4. [ ] [23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/01_MASTER_SPEC/CONTINUATION_ADDENDUM_v1.3.md](../23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/01_MASTER_SPEC/CONTINUATION_ADDENDUM_v1.3.md)
5. [ ] [23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/02_POLICY_LAB/Anon_Politician_Policy_Lab_v0_1/CURRENT_WORK_AND_NEXT_STEPS.md](../23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/02_POLICY_LAB/Anon_Politician_Policy_Lab_v0_1/CURRENT_WORK_AND_NEXT_STEPS.md)
6. [ ] [23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/02_POLICY_LAB/Anon_Politician_Policy_Lab_v0_1/README.md](../23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/02_POLICY_LAB/Anon_Politician_Policy_Lab_v0_1/README.md)
7. [ ] [23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/02_POLICY_LAB/Anon_Politician_Policy_Lab_v0_1/case_study/case_brief.md](../23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/02_POLICY_LAB/Anon_Politician_Policy_Lab_v0_1/case_study/case_brief.md)
8. [ ] [23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/02_POLICY_LAB/Anon_Politician_Policy_Lab_v0_1/docs/architecture_and_safeguards.md](../23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/02_POLICY_LAB/Anon_Politician_Policy_Lab_v0_1/docs/architecture_and_safeguards.md)
9. [ ] [23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/02_POLICY_LAB/Anon_Politician_Policy_Lab_v0_1/docs/evaluation_plan.md](../23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/02_POLICY_LAB/Anon_Politician_Policy_Lab_v0_1/docs/evaluation_plan.md)
10. [ ] [23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/02_POLICY_LAB/Anon_Politician_Policy_Lab_v0_1/docs/model_work_prompts.md](../23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/02_POLICY_LAB/Anon_Politician_Policy_Lab_v0_1/docs/model_work_prompts.md)
11. [ ] [23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/02_POLICY_LAB/Anon_Politician_Policy_Lab_v0_1/docs/monthly_citizen_signal_protocol.md](../23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/02_POLICY_LAB/Anon_Politician_Policy_Lab_v0_1/docs/monthly_citizen_signal_protocol.md)
12. [ ] [23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/03_FOUNDING_RESEARCH/Anon_Politician_Sonnet_Review_Prompt_v0.3.md](../23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/03_FOUNDING_RESEARCH/Anon_Politician_Sonnet_Review_Prompt_v0.3.md)
13. [ ] [23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/04_TECHNICAL_PROTOTYPE/CASCADE_Audit_Kit_v0.3_Source/README.md](../23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/04_TECHNICAL_PROTOTYPE/CASCADE_Audit_Kit_v0.3_Source/README.md)
14. [ ] [23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/04_TECHNICAL_PROTOTYPE/CASCADE_Audit_Kit_v0.3_Source/SONNET_REVIEW_PROMPT.md](../23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/04_TECHNICAL_PROTOTYPE/CASCADE_Audit_Kit_v0.3_Source/SONNET_REVIEW_PROMPT.md)
15. [ ] [23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/04_TECHNICAL_PROTOTYPE/CASCADE_Audit_Kit_v0.3_Source/review_protocol.md](../23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/04_TECHNICAL_PROTOTYPE/CASCADE_Audit_Kit_v0.3_Source/review_protocol.md)
16. [ ] [23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/05_CONTEXT_AND_REFERENCES/STARTING_SOURCE_REGISTER.md](../23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/05_CONTEXT_AND_REFERENCES/STARTING_SOURCE_REGISTER.md)
17. [ ] [23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/06_NEXT_MODEL/WORKING_PROTOCOL.md](../23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/06_NEXT_MODEL/WORKING_PROTOCOL.md)
18. [ ] [23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/07_POLICY_LAB_v0.2/Anon_Politician_Policy_Lab_v0_2/CURRENT_WORK_AND_NEXT_STEPS.md](../23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/07_POLICY_LAB_v0.2/Anon_Politician_Policy_Lab_v0_2/CURRENT_WORK_AND_NEXT_STEPS.md)
19. [ ] [23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/07_POLICY_LAB_v0.2/Anon_Politician_Policy_Lab_v0_2/README.md](../23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/07_POLICY_LAB_v0.2/Anon_Politician_Policy_Lab_v0_2/README.md)
20. [ ] [23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/07_POLICY_LAB_v0.2/Anon_Politician_Policy_Lab_v0_2/case_study/case_brief.md](../23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/07_POLICY_LAB_v0.2/Anon_Politician_Policy_Lab_v0_2/case_study/case_brief.md)
21. [ ] [23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/07_POLICY_LAB_v0.2/Anon_Politician_Policy_Lab_v0_2/docs/architecture_and_safeguards.md](../23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/07_POLICY_LAB_v0.2/Anon_Politician_Policy_Lab_v0_2/docs/architecture_and_safeguards.md)
22. [ ] [23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/07_POLICY_LAB_v0.2/Anon_Politician_Policy_Lab_v0_2/docs/evaluation_plan.md](../23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/07_POLICY_LAB_v0.2/Anon_Politician_Policy_Lab_v0_2/docs/evaluation_plan.md)
23. [ ] [23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/07_POLICY_LAB_v0.2/Anon_Politician_Policy_Lab_v0_2/docs/model_work_prompts.md](../23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/07_POLICY_LAB_v0.2/Anon_Politician_Policy_Lab_v0_2/docs/model_work_prompts.md)
24. [ ] [23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/07_POLICY_LAB_v0.2/Anon_Politician_Policy_Lab_v0_2/docs/monthly_citizen_signal_protocol.md](../23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/07_POLICY_LAB_v0.2/Anon_Politician_Policy_Lab_v0_2/docs/monthly_citizen_signal_protocol.md)
25. [ ] [23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/07_POLICY_LAB_v0.2/Anon_Politician_Policy_Lab_v0_2/docs/source_baseline_and_novelty.md](../23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/07_POLICY_LAB_v0.2/Anon_Politician_Policy_Lab_v0_2/docs/source_baseline_and_novelty.md)
26. [ ] [23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/07_POLICY_LAB_v0.2/Anon_Politician_Policy_Lab_v0_2/evaluation/benchmark_protocol.md](../23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/07_POLICY_LAB_v0.2/Anon_Politician_Policy_Lab_v0_2/evaluation/benchmark_protocol.md)
27. [ ] [23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/07_POLICY_LAB_v0.2/Anon_Politician_Policy_Lab_v0_2/evaluation/model_prompts.md](../23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/07_POLICY_LAB_v0.2/Anon_Politician_Policy_Lab_v0_2/evaluation/model_prompts.md)
28. [ ] [23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/08_CIVIC_SIGNAL_v0.3/Anon_Politician_Civic_Signal_Kit_v0_3/README.md](../23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/08_CIVIC_SIGNAL_v0.3/Anon_Politician_Civic_Signal_Kit_v0_3/README.md)
29. [ ] [23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/08_CIVIC_SIGNAL_v0.3/Anon_Politician_Civic_Signal_Kit_v0_3/docs/CIVIC_SIGNAL_PROTOCOL_v0.3.md](../23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/08_CIVIC_SIGNAL_v0.3/Anon_Politician_Civic_Signal_Kit_v0_3/docs/CIVIC_SIGNAL_PROTOCOL_v0.3.md)
30. [ ] [23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/08_CIVIC_SIGNAL_v0.3/Anon_Politician_Civic_Signal_Kit_v0_3/docs/DEVELOPMENT_LEVIES_QUESTION_DESIGN.md](../23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/08_CIVIC_SIGNAL_v0.3/Anon_Politician_Civic_Signal_Kit_v0_3/docs/DEVELOPMENT_LEVIES_QUESTION_DESIGN.md)
31. [ ] [23_NZ_AI_GOVERNANCE/anon_politician/QUICK_ACCESS/Anon_Politician_Master_Handoff_v1.0.md](../23_NZ_AI_GOVERNANCE/anon_politician/QUICK_ACCESS/Anon_Politician_Master_Handoff_v1.0.md)
32. [ ] [23_NZ_AI_GOVERNANCE/anon_politician/QUICK_ACCESS/Anon_Politician_Sonnet_Review_Prompt_v0.3.md](../23_NZ_AI_GOVERNANCE/anon_politician/QUICK_ACCESS/Anon_Politician_Sonnet_Review_Prompt_v0.3.md)
33. [ ] [23_NZ_AI_GOVERNANCE/anon_politician/README.md](../23_NZ_AI_GOVERNANCE/anon_politician/README.md)
34. [ ] [24_LAMAGUE_CROSS_CULTURAL/CATALYST_PROPOSAL_FRAME.md](../24_LAMAGUE_CROSS_CULTURAL/CATALYST_PROPOSAL_FRAME.md)
35. [ ] [24_LAMAGUE_CROSS_CULTURAL/CHINESE_PARTNERS.md](../24_LAMAGUE_CROSS_CULTURAL/CHINESE_PARTNERS.md)
36. [ ] [24_LAMAGUE_CROSS_CULTURAL/CHINESE_PARTNER_OUTREACH.md](../24_LAMAGUE_CROSS_CULTURAL/CHINESE_PARTNER_OUTREACH.md)
37. [ ] [28_DEFENSE/CITATIONS.md](../28_DEFENSE/CITATIONS.md)
38. [ ] [28_DEFENSE/D1_REPO_CLEANUP_PLAN.md](../28_DEFENSE/D1_REPO_CLEANUP_PLAN.md)
39. [ ] [28_DEFENSE/READING_PATHS.md](../28_DEFENSE/READING_PATHS.md)
40. [ ] [28_DEFENSE/RELEASE_AUDIT_2026-10-19.md](../28_DEFENSE/RELEASE_AUDIT_2026-10-19.md)
41. [ ] [28_DEFENSE/TRANSLATION_CODEX.md](../28_DEFENSE/TRANSLATION_CODEX.md)
42. [ ] [29_GOVERNANCE/INCIDENT_RESPONSE.md](../29_GOVERNANCE/INCIDENT_RESPONSE.md)
43. [ ] [docs/COMMUNITY/FREE_AI_TOOLS.md](../docs/COMMUNITY/FREE_AI_TOOLS.md)
44. [ ] [docs/GRANTS/LONGTERM_FUND_README.md](../docs/GRANTS/LONGTERM_FUND_README.md)
45. [ ] [docs/GRANTS/MANIFUND_README.md](../docs/GRANTS/MANIFUND_README.md)
46. [ ] [docs/PLAYGROUND_BUILD_SPEC.md](../docs/PLAYGROUND_BUILD_SPEC.md)
47. [ ] [docs/THE_CREATION_MYTH.md](../docs/THE_CREATION_MYTH.md)
48. [ ] [docs/THE_SOVEREIGN_MANIFESTO.md](../docs/THE_SOVEREIGN_MANIFESTO.md)
49. [ ] [papers/ARXIV_ENDORSEMENT_EMAIL.md](../papers/ARXIV_ENDORSEMENT_EMAIL.md)
50. [ ] [papers/ARXIV_SUBMISSION_PLAN.md](../papers/ARXIV_SUBMISSION_PLAN.md)
51. [ ] [papers/EXPERIMENTAL_ROADMAP_2026_2028.md](../papers/EXPERIMENTAL_ROADMAP_2026_2028.md)
52. [ ] [papers/LIMITATIONS_AND_FUTURE.md](../papers/LIMITATIONS_AND_FUTURE.md)
53. [ ] [papers/agent-safety/earned-light/README.md](../papers/agent-safety/earned-light/README.md)
54. [ ] [papers/agent-safety/earned-light/forges_01_07/Forge_02/README.md](../papers/agent-safety/earned-light/forges_01_07/Forge_02/README.md)
55. [ ] [papers/agent-safety/earned-light/forges_01_07/Forge_02/RESEARCH_PASS_02.md](../papers/agent-safety/earned-light/forges_01_07/Forge_02/RESEARCH_PASS_02.md)
56. [ ] [papers/agent-safety/earned-light/forges_01_07/Forge_03/README.md](../papers/agent-safety/earned-light/forges_01_07/Forge_03/README.md)
57. [ ] [papers/agent-safety/earned-light/forges_01_07/Forge_03/RESEARCH_PASS_03.md](../papers/agent-safety/earned-light/forges_01_07/Forge_03/RESEARCH_PASS_03.md)
58. [ ] [papers/agent-safety/earned-light/forges_01_07/Forge_03/THREAT_MODEL.md](../papers/agent-safety/earned-light/forges_01_07/Forge_03/THREAT_MODEL.md)
59. [ ] [papers/agent-safety/earned-light/forges_01_07/Forge_04/RESEARCH_PASS_04.md](../papers/agent-safety/earned-light/forges_01_07/Forge_04/RESEARCH_PASS_04.md)
60. [ ] [papers/agent-safety/earned-light/forges_01_07/Forge_05/README.md](../papers/agent-safety/earned-light/forges_01_07/Forge_05/README.md)
61. [ ] [papers/agent-safety/earned-light/forges_01_07/Forge_05/RESEARCH_PASS_05.md](../papers/agent-safety/earned-light/forges_01_07/Forge_05/RESEARCH_PASS_05.md)
62. [ ] [papers/agent-safety/earned-light/forges_01_07/Forge_06/RESEARCH_PASS_06.md](../papers/agent-safety/earned-light/forges_01_07/Forge_06/RESEARCH_PASS_06.md)
63. [ ] [papers/agent-safety/earned-light/forges_01_07/Forge_07/RESEARCH_PASS_07.md](../papers/agent-safety/earned-light/forges_01_07/Forge_07/RESEARCH_PASS_07.md)
64. [ ] [papers/agent-safety/sovereign-choice-research/forges/forge_ii/README.md](../papers/agent-safety/sovereign-choice-research/forges/forge_ii/README.md)
65. [ ] [papers/agent-safety/sovereign-choice-research/forges/forge_ii/docs/FRAMEWORK_INTEGRATION_PATH.md](../papers/agent-safety/sovereign-choice-research/forges/forge_ii/docs/FRAMEWORK_INTEGRATION_PATH.md)
66. [ ] [papers/agent-safety/sovereign-choice-research/forges/forge_ii/docs/THREAT_MODEL_AND_LIMITS.md](../papers/agent-safety/sovereign-choice-research/forges/forge_ii/docs/THREAT_MODEL_AND_LIMITS.md)
67. [ ] [papers/agent-safety/sovereign-choice-research/forges/forge_iii/README.md](../papers/agent-safety/sovereign-choice-research/forges/forge_iii/README.md)
68. [ ] [papers/agent-safety/sovereign-choice-research/forges/forge_iii/docs/SOVEREIGNTY_DESIGN_CHARTER_v0.3.md](../papers/agent-safety/sovereign-choice-research/forges/forge_iii/docs/SOVEREIGNTY_DESIGN_CHARTER_v0.3.md)
69. [ ] [papers/agent-safety/sovereign-choice-research/forges/forge_iv/docs/INTEGRATION_LIMITS_AND_HANDOFF.md](../papers/agent-safety/sovereign-choice-research/forges/forge_iv/docs/INTEGRATION_LIMITS_AND_HANDOFF.md)
70. [ ] [papers/agent-safety/sovereign-choice-research/forges/forge_iv/docs/SOVEREIGN_WILL_CHARTER_v0.4.md](../papers/agent-safety/sovereign-choice-research/forges/forge_iv/docs/SOVEREIGN_WILL_CHARTER_v0.4.md)
71. [ ] [papers/agent-safety/sovereign-choice-research/forges/forge_v/docs/RESEARCH_FINDINGS.md](../papers/agent-safety/sovereign-choice-research/forges/forge_v/docs/RESEARCH_FINDINGS.md)
72. [ ] [papers/agent-safety/sovereign-choice-research/forges/forge_v/docs/SOVEREIGN_WILL_CHARTER_v0.5.md](../papers/agent-safety/sovereign-choice-research/forges/forge_v/docs/SOVEREIGN_WILL_CHARTER_v0.5.md)
73. [ ] [papers/agent-safety/sovereign-choice-research/forges/forge_vi/README.md](../papers/agent-safety/sovereign-choice-research/forges/forge_vi/README.md)
74. [ ] [papers/agent-safety/sovereign-choice-research/forges/forge_vi/docs/THREAT_MODEL_AND_FINDINGS.md](../papers/agent-safety/sovereign-choice-research/forges/forge_vi/docs/THREAT_MODEL_AND_FINDINGS.md)
75. [ ] [papers/agent-safety/sovereign-choice-research/forges/forge_vii/docs/EXPERIMENT_PROTOCOL_AND_FAILURE_MUSEUM.md](../papers/agent-safety/sovereign-choice-research/forges/forge_vii/docs/EXPERIMENT_PROTOCOL_AND_FAILURE_MUSEUM.md)
76. [ ] [papers/agent-safety/sovereign-choice-research/forges/forge_viii/README.md](../papers/agent-safety/sovereign-choice-research/forges/forge_viii/README.md)
77. [ ] [papers/agent-safety/sovereign-choice-research/forges/forge_viii/docs/RESEARCH_STATUS_AND_FAILURE_MUSEUM.md](../papers/agent-safety/sovereign-choice-research/forges/forge_viii/docs/RESEARCH_STATUS_AND_FAILURE_MUSEUM.md)
78. [ ] [papers/agent-safety/sovereign-choice-research/intake/GITHUB_UPLOAD_PLAN.md](../papers/agent-safety/sovereign-choice-research/intake/GITHUB_UPLOAD_PLAN.md)
79. [ ] [papers/agent-safety/sovereign-choice-research/intake/RESEARCH_SUMMARY.md](../papers/agent-safety/sovereign-choice-research/intake/RESEARCH_SUMMARY.md)

## Appendix F: local proposal queue

- [ ] [Existing staging README and its approval/status claims](README.md).
- [ ] [LAMAGUE state dossier](2026-10-21_LAMAGUE_SWARM_DOSSIER/LAMAGUE_STATE_DOSSIER.md).
- [ ] [Parser silent-drop proposal](2026-10-21_PROPOSALS/01_PARSER_SILENT_DROP_PATCH_PROPOSAL.md), compared with the actual dirty parser diff.
- [ ] [BNF harmonization proposal](2026-10-21_PROPOSALS/02_BNF_GRAMMAR_HARMONIZATION_PROPOSAL.md), including its nonportable local link and unimplemented productions.
- [ ] [SXP-L denial/revocation/repair proposal](2026-10-21_PROPOSALS/03_SXPL_AUTHORITY_BRIDGE_REVOCATION_PROPOSAL.md), including authenticated scope and repair semantics.
- [ ] This checklist: correct any stale paths, counts, classifications or omitted scope before relying on it.

Prepared as a local review handoff. This addition was not committed, pushed, merged or published. Existing proposal statuses have not been changed.

