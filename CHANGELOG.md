# Changelog

Notable changes to this repository. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

This file starts at the Unreleased section below. Everything before it is in the git
history, which was the only changelog until now.

## [Unreleased]

### Opus review corrections — 22 October 2026

Each correction below has a probe, a test that fails on the previous code, and a
ledger entry under `FOR-REVIEW/2026-10-22_OPUS_REVIEW/`.

- Compaction shield (`lycheetah/compaction/`):
  - Protection is now checked per unknown. A protected unknown must survive under
    the same id and stay protected. Previously a packet holding one protected and
    one unprotected unknown read as UNSAFE_COLLAPSE on an unrelated horizon edit,
    adding an unprotected unknown did the same, and swapping a protected unknown
    for a different protected one read only as DIVERGENT.
  - A candidate that breaks a packet rule is UNSAFE_COLLAPSE on both the packet
    and the digest reference paths, including when the reference broke it first.
    The packet path previously returned PARTIAL_EQUIVALENT (`is_safe` True) for
    an inherited violation and EXACT_EQUIVALENT for an exact copy, while the
    digest path refused it and `encode` would not compact it.
  - Every classification names `changed_fields`, so a PARTIAL_EQUIVALENT says
    what moved. A digest match names the fields it could not see in
    `unchecked_fields`. A reference digest that is not 64 lowercase hexadecimal
    characters is UNDECODABLE instead of DIVERGENT.
  - Unchanged boundary, now stated in `CompactionShield.verify_integrity`: risk,
    evidence, horizon, yield, id and operations are outside the critical
    projection. A risk downgrade or dropped evidence stays PARTIAL_EQUIVALENT,
    and a stale snapshot passes when only those fields moved on. The sovereign
    harness and the guarded handoff bind risk separately.
  - The committed reading copies `docs/lamague-handover-report.json` and
    `docs/lamague-handover.html` were regenerated through the demo's own flags.
    The summary is unchanged; controls now carry `changed_fields`.
  - Added 25 cases in `tests/test_compaction_drift_boundaries.py`; 14 fail on
    the previous code.
  - **Retracted with cause:** the compaction shield entry further down claimed
    "Guaranteed 36/36 exact round-trip preservation", a hash "allowing third
    parties to mathematically verify zero loss of safety constraints" and a demo
    "proving anti-amnesia protection under LLM summarization". A passing set of
    round-trip cases is evidence for those cases, not a guarantee. The hash shows
    that the critical projection changed or did not; it cannot show that the
    declared fields were complete or true, and it never covered risk or evidence.
    The package docstring no longer says "Provable".
- Compact wire (`lycheetah/compaction/codec.py`):
  - `decode` accepts only the exact wire `encode` emits for the decoded packet.
    Previously a repeated key was read with its last value, so a wire whose
    first `c` carried one claim decoded to another; an extra array item was
    dropped without notice; and added spacing, reordered keys, an escaped
    letter, 1.0 or true for a protected flag, and a codebook string written out
    in full all decoded, giving one packet many wires. A repeated key is now
    named in the error.
  - Text that is not valid Unicode, such as a lone surrogate, is a CodecError in
    validation. It previously passed validation and `encode`, then crashed
    `full_hash` and `classify` with UnicodeEncodeError.
  - Wires from the v1.0 encoder still decode: all 36 corpus packets encode to the
    same bytes in both modes. The CLI already strips surrounding whitespace from
    a wire it reads.
  - The literal consent repair (R, I and N refused on input) holds in both
    modes. The frozen v1.0 codec under `03_LAMAGUE_L1/22_REVERSIBLE_COMPRESSION_v1.0/`
    keeps every one of these defects as its recorded counterexample.
  - Added 14 cases in `tests/test_compaction_wire_canonical.py`; 11 fail on the
    previous code. The committed reading copies were regenerated again for the
    new codec digest.
- Guarded handoff bundle (`examples/guarded_handoff_risk_demo.py`):
  - The verifier compares the whole run report. A resealed bundle could drop
    the limits, set the mode to `PRODUCTION_ATTESTED`, report LOW risk against a
    HIGH permit, add a field such as `authenticated_human_approval`, or flip the
    risk-downgrade and workspace flags, and still verify as `SELF_CONSISTENT`.
    The report must now hold exactly the exporter's fields and statements, and
    the risk-downgrade flag is derived from the control it describes.
  - The three denied controls must belong to the run: the executed permit,
    consensus, scope and state; the declared action, or for substitution a
    different one; run order from the permit's issue time; and a risk-only change
    for the downgrade. Consensus may name only the task's recipient and
    authority. A control naming another permit or action, or a phantom consensus
    agent, previously passed with its public witness digest recomputed.
  - The completion's summary and evidence notes must be the ones the exporter
    writes. "Externally attested by an independent auditor" previously verified.
  - Evidence is opened without following a link or waiting on a FIFO, and the
    opened file must be a bounded regular file. Previously the type was checked
    by name and the file then read by name again.
  - Deeply nested JSON is an invalid bundle instead of an escaping
    RecursionError, and a number that overflows to infinity, such as `1e400`, is
    refused like `Infinity`.
  - Unchanged boundary: without a separately retained manifest digest, a
    complete and consistent replacement still verifies. The demo does not sign
    its receipt, and the verifier uses the same library that wrote the evidence.
  - Added 19 cases to `tests/test_guarded_handoff_bundle.py`; 18 fail on the
    previous code and the benign control passes on both.
- Multi-Agent Chorus (`19_MULTI_AGENT_CHORUS/`), now explicitly a scaffold all the way down:
  - Sol Meridian's own `health_check()` returned "✅ CONSTITUTIONAL INTEGRITY
    MAINTAINED", `pcf_active` and `vip_routing_active` as constants. It now
    reports SCAFFOLD and NOT_MEASURED and counts the named hard guardrails that
    have any check: 2 of 9.
  - PCF read a missing flag as compliant, so an output that declared only its
    trinity and signature flags was approved. A missing flag now fails as
    `undeclared: <flag>`, and an approval says every flag was self-reported and
    names the 7 guardrails with no check.
  - 15 role methods returned 24 fixed `True` fields for any input, and
    `AlbedoSynthesizer.validate_structure({})` returned True. The methods now
    return `None` with `SCAFFOLD_NOT_COMPUTED`; validation returns False.
  - Protector passed an action that declared both consent and an override, and
    passed an action that declared nothing, for agency and for reversibility.
    All three now fail.
  - Harmonia rated a semitone (0.944) and an equal-tempered tritone (0.921)
    harmonic. It now measures cents from the Pythagorean consonances, with a
    10-cent tolerance.
  - Cascade returned infinite Π for S = 0 and for S = -1. It now raises.
  - Aurora returned a CRITICAL contradiction at `00_Sovereign_Index.md:line 42`
    whatever files it was given; that file exists and does not contain the words
    attributed to it. A scan with files now raises NotImplementedError, and the
    empty-list demo returns one ILLUSTRATIVE example that names no real file.
  - A decision log that was not valid JSON read as empty and the next decision
    overwrote it, losing every earlier entry; a corrupt coherence buffer read as
    empty. Both now raise and leave the file as it was. The log is written to a
    temporary file and swapped in.
  - The supervised menu printed the integrity verdict and "would be displayed"
    placeholders, and all 8 role scripts printed "online" or "Operational". The
    menu now shows Meridian's health and the real decision log; the scripts say
    "constructed" and that no behaviour was probed.
  - Docs: the manifest's "Fully operational" status and "✅ ALL AGENTS
    OPERATIONAL" are withdrawn and struck through but kept as the March 2026
    record, with the missing CI workflow, the missing agent READMEs and the
    ignored `--verify`/`--audit` flags marked. `THE_AI_ARCHITECTS_DOOR.md`,
    `THE_FOUR_PRINCIPLES.md` and `LAWS_COMPLETE.md` no longer call the chorus a
    working implementation.
  - Added 55 cases in `tests/test_chorus_scaffold_honesty.py`; 44 fail on the
    previous code, and the 11 that pass are benign controls.
  - Unchanged boundary: no agent reads or writes the coherence buffer, no
    message passes between agents, and nothing inspects content.

### Inspectable handoffs and stable context — 21 October 2026

- Extended the existing guarded-handoff example with an explicit new-directory
  export and a separate read-only verifier. Retain the task, full context, exact
  action, observed file, full Assurance Receipt and run report without private
  checkpoint keys. A separately retained manifest digest pins the bundle's bytes;
  local consistency remains distinct from issuer authentication.
- Context exports now detach nested collections from the live accumulator in
  both directions. Existing packet hashes and L1/L1D wire bytes are preserved.
- Gateway receipts retain the evaluated policy decision separately from the
  executor outcome and use schema-consistent event/subject records. Failed,
  uncertain and review-approved executions now produce verifiable receipts.
  Policy/rule constructor collections are detached into immutable tuples, and
  policy metadata is captured before executor callbacks.
- Added 90 regressions and feature cases; the focused integration run passed
  329 cases. Independent AI review found contradictory-report, omitted-write
  and nonregular-manifest gaps in the first export verifier; 12 failing controls
  were added before repairing them. The whole corpus was not revalidated.
- Replaced simulated-effect and unconditional safety language in the examples,
  connected the retained workflow from the main README/runtime guides, and
  clarified that an ACTIVE test marker records fixture behavior, not proof.

### Implementation boundaries and a clearer main README — 21 October 2026

- Rebuilt the main README around practical uses, an executable local gateway
  example, the component architecture, the nine foundational frameworks, current
  research, evidence limits and repository navigation.
- TRIAD now requires a small gradient as well as a small update, records coherence
  at the reported state and rejects invalid/nonfinite transitions before commit.
  Its stop condition is numerical stationarity, not a general convergence proof.
- TRI-AXIAL rejects nonfinite values, invalid violation counts, negative friction
  and incomplete vector pairs; scaled cosine avoids large-finite-vector overflow.
- Action Gateway now uses checkpoint-gated mutations, rejects uncheckpointed
  history, rechecks current policy, preserves an explicitly empty live action,
  and attributes the execution receipt to the policy actually evaluated.
  Result-checkpoint failure after execution reports UNKNOWN without a success receipt.
- Fixed empty/unrelated JSON keys satisfying every LAMAGUE accountability field.
  The maintained compaction codec rejects ambiguous literal consent wire codes;
  frozen supplied research sources remain unchanged.
- Added 64 boundary cases; 42 counterexamples failed before their corresponding
  repairs. Focused runs passed 167 implementation/sheaf/gateway cases, seven alias
  cases and 92 compaction/integration cases, with overlap explicitly recorded.
  The whole maintained suite was not rerun for this extension.
- Recorded the incomplete deeper pass across 606 folders, service-interrupted
  parallel reviewers, additional prototype defects and the archive-log portability
  gap. Added direct corrections to unsupported clinical/validation claims while
  preserving original source bodies. Published for draft review in PR18;
  no release or master merge is implied.

### Full Framework review and demonstrated corrections — 20 October 2026

- Added a substantive review of the mathematics, maintained software, research,
  governance and evidence, with 18 runnable mathematical observations and a
  complete 71-claim/107-pointer baseline audit. Preserved original author statuses.
- Recompute consensus verdict integrity at permit issuance and execution; bind
  the anchor and complete outcome in the v2 digest. Reject nonfinite vectors.
  Existing unverifiable verdicts and their permits require re-deliberation/reissue.
- Corrected runtime descriptions that equated connectivity with H¹ or a
  quarantine fraction with proven Byzantine fault tolerance.
- Fixed desktop parallel scoring changing the user's selected provider; added
  three offline regressions, including a preference edit during scoring.
- Repaired 14 moved-source evidence references; retained 23 unresolved pointers
  explicitly. Added dated corrections to source entry points instead of
  silently replacing historical mathematical arguments.
- Recorded 997 maintained-test passes, one intentional dependency-state skip
  and one strict expected failure. Whole-corpus lint and footing gates remain
  unresolved; the report does not describe the repository as release-clean.

### Current corpus entrances and synthesis — 19–20 October 2026

- Rebuilt the main README, five-minute brief and complete 50-area repository map;
  added a current whole-framework synthesis connecting knowledge revision,
  meaning/continuity, bounded action, learning and creative work.
- Refreshed foundational, implementation, paper, AI-reading and website guides.
  Added archive, package, examples, evidence, tests and empirical-design READMEs.
  Source ownership, historical plans, generated exports and component versions
  now have explicit routes and distinct statuses.
- Reconciled all 37 top-level NZ Markdown documents with the current six-rights
  proposal: 26 historical notices, nine background candidates, one current proposal
  and its guide. Corrected unestablished certification/adoption/endorsement claims,
  conditional convergence language and the repealed Therapeutic Products Act link.
  Refreshed homepage/NZ website sources; these source changes await normal merge.
- Replaced contradictory August capability summaries with the actual dated
  dataset distinctions and boundaries. Preserved original research, failures,
  stories and all 225 intake-manifest destinations. Three compatibility pages
  repair original handoff navigation without changing imported bytes or weakening
  the ordinary link gate.
- The 71-row claim register and 22 count mirrors agree; its two existing tests
  pass, including deliberately incorrect-count detection. A parallel AI patch
  review challenged source routes, metadata, evidence language and preservation.
  Full scope, browser witness and limits are in
  `28_DEFENSE/REPO_ENTRY_AUDIT_2026-10-19.md`.

### Public reading site — 19 October 2026

- Published a public reading page for Earned Light and Sovereign Will, with
  complete Lighthouse and Ninth Road stories, the earlier Lighthouse edition,
  a plain-language research introduction and two downloadable full bundles.
- Added maintained source and deterministic source-checked packaging under
  `examples/earned_light_reading/`; the existing story manuscripts stay canonical.
- Fifteen local Chromium checks passed, including direct story navigation,
  desktop/390px layout, text sizing and night reading. Screenshots were inspected.
  The public Sites deployment succeeded with public access; its source is separate
  from the pending Framework PR. No outside reader result is claimed.

### Earned Light, Sovereign Will and original narratives — 19 October 2026

- Imported two research/story handoffs with a 225-file provenance manifest,
  retaining Forge code, failures, historical results, charters and seven source
  ZIPs. Added guides and working temporary-copy replay commands; the original
  Sovereign Choice extracted tree lacks the nested ZIPs its old runners expect.
- Reproduced 207 Earned Light and 207 Sovereign Choice test executions, with
  historical overlap explicitly stated. The latter includes separate Forge
  II/III checks omitted by the original 142-test replay. Two deliberately broken
  controls failed as expected. These are authored local fixtures, without a
  production safety, free-will or independent-validation claim.
- Registered the expanded and earlier Lighthouse stories and Ninth Road in the
  existing stories collection; rebuilt its Markdown, browser and portable ZIP
  editions. Linked the philosophical proposals and engineering research from
  their existing parent guides. Fiction remains distinct from research and
  unapproved as epic canon. Eleven local Chromium reader checks passed and
  desktop/390px screenshots were inspected; no physical-device or outside-reader
  result is claimed. See `28_DEFENSE/RELEASE_AUDIT_2026-10-19.md`.

### LAMAGUE handover research preview — 18–19 October 2026

- Added an own-task form to the offline page, exporting readable handovers and
  LAMAGUE packet JSON without inference, autosave or submission. Author review,
  permission boundaries, risk and recovery are explicit; editing invalidates
  the preview and clear removes it.
- Added separate feedback downloads with optional timing: unmeasured values
  stay null, explicit zero stays zero, and self-reports establish no independence.
  Added a short tester card; no task content is attached automatically.

- Added an offline browser demonstration of permission, uncertainty, attribution
  and other declared-record changes, with downloadable records and results.
- Compared compact JSON, LAMAGUE L1 and gzip/base64 JSON on the same constructed
  packet and common byte budgets. All restore 17 fields; compressed JSON is
  smallest in this example. No human-understanding advantage is claimed.
- Added a full-record comparison CLI, twelve explicit failure/unchanged controls,
  reproducible source digests and a proposed independent usability trial.
- Focused verification: 60 runner/comparator and existing compaction tests
  passed. The expanded offline page passed 64 Chromium checks covering controls,
  budgets, keyboard selection, builder validation, export/clear behaviour,
  feedback separation and desktop/narrow layouts; screenshots
  were inspected. Firefox, physical devices and independent users are untested.
  A browser-exported record also passed Python validation and an exact codec
  round trip. Prepared for the existing master/docs Pages site; no release tag,
  model calls or outside participants.

### LAMAGUE language guide and synthesis — 18 October 2026

- Replaced the language folder's mixed historical introduction with a current
  guide to its formal, visual, spoken, conversational, packet and runtime lines.
- Added `03_LAMAGUE_L1/LAMAGUE_SYNTHESIS.md`, connecting the root canon,
  operator contracts, glyphs and seals, dialogue and perspective, compression,
  model-decoding pilot, temporal evidence and the wider research extensions.
- Distinguished dated software results, the operator-run pilot, open defects
  and unrun human studies; removed unsupported production/universal-validation
  claims from the folder's entry point. Linked the full language from the main
  README and SXP-L guide. Documentation only; original releases are unchanged.

### Core engine reading guide — 18 October 2026

- Added `12_IMPLEMENTATIONS/core/README.md`, explaining all 29 modules by job,
  their Python entry points, storage side effects and research boundaries.
- Linked the guide from the implementation overview and corrected its stale
  CASCADE example and blanket proof/validation wording. Documentation only.

### Research release integration and audit — 18 October 2026

- Preserved Earned Trust cycles 001–009, Hybrid Gateway v1.2 and the SXP-L
  v0.1–v2.0 handoff in distinct research homes. The 444 original/copied release
  files have a checked provenance manifest; all 20 SXP-L ZIPs remain intact.
- Reproduced 264 gateway tests and 83 focused SXP-L tests. Recorded nine
  privileged Earned Trust checks as skipped here, rather than counting them as
  reproduced passes. Published eight open inherited SXP-L defect reproducers.
- Executed previously unrun native Earned Trust bridges: Cycle 004 passed four
  tests; original Cycle 005 had two failures. A separate fixture correction
  aligns approval IDs and passes five boundary-aware tests, retaining the
  original failure and the provider's refusal rule.
- Hardened declared handoff comparison, corrected misleading verification
  labels and removed manufactured authority/recovery defaults. Added portable
  Sol/CASCADE wrappers and an explicit source-checkout boundary for Alexandria.
- Corrected the sheaf holonomy claim and unified numerical rank/projection
  cutoffs. Historical experiment rows remain unchanged. See the dated release
  audit for actual gate results and open scientific limitations.

### Guarded handoff risk binding — 18 October 2026

- New sovereign permits bind the issuing reference packet's declared risk into
  a versioned v2 permit payload. Both reference and incoming candidate risk must
  match before nonce consumption, and the high-risk authority rule uses that
  bound value.
- Legacy unbound permits remain representable for inspection but are refused
  for new registration, claim and execution. Existing SQLite rows and the codec's
  ten-field critical projection remain unchanged. Low-level permit issuance now
  requires `bound_risk`; high-level harness issuance derives it from its reference.
- Added the admission/legacy contract and source-grounded signed-grant/publisher
  integration boundaries in `34_ASSURANCE_RUNTIME/GUARDED_HANDOFF_ADMISSION_v0.1.md`.
  Synthetic runtime/regression checks and a disposable handoff demonstration
  followed the initial source review. Authenticated human consent and restricted
  physical effects remain separate integration work.

### Frontier integration and cross-seat review — 17 October 2026

- Added `SovereignExecutionHarness` and the `lycheetah-sovereign demo` CLI, binding
  consensus/context witnesses to an exact action, scope, state version, expiry and
  durable single-use permit. Empty authority grants and read-only grants used for
  deployment fail before consuming the permit. Declared identity metadata is not
  external human authentication; the harness is not an OS sandbox.
- Added Aetheron's experimental dependency propagation model and preserved its
  original 768-row result. Corrected the claim register: programmed parent-label
  conflict and finite tests do not establish cohomology or glass-law theorems.
  Snapshot and queue-visibility changes remain confounded in the three-arm design.
- Preserved the original experiment revisions and documented why the new CASCADE
  diagnostics change work calibration. Recorded data have not been relabelled as
  results from the integrated engine.
- Included the regulation callback threshold/trace fix and the harness authority
  scope fix found through cross-seat review. See the experiment reproduction note
  for integrated checks and source identities.

### Load-aware snapshot/commit falsifier — 17 October 2026

- Added a separate measured-work CASCADE/FIFO model with frozen service snapshots,
  delayed partial commits, preservation of later arrivals, and explicit in-flight
  work accounting. The earlier fixed-service source/data remain the control.
- Ran a second matched 864-row sweep. The observed CASCADE conflict-reduction
  advantage shrinks from 9.80 to 5.49 percentage points under the combined timing
  and cost correction; this remains synthetic evidence, not a validated glass law.
- Sixteen focused checks passed, including a deliberately false work receipt and
  a cut-commit witness. Added raw JSON/CSV, comparison figure and result limits.
- Aetheron's cross-seat check passed alongside v1; queue-visibility limitations
  and exact recorded source revisions are documented with the results.

### CASCADE synthetic glass-transition experiment — 17 October 2026

- Added an executable comparison of CASCADE batch adjudication and FIFO pairwise
  adjudication, with independent work calibration, a full arrival/processing
  intervention grid, compatible-overload controls and separate drain recovery.
- Recorded 864 synthetic runs, a fixed protocol, complete JSON/CSV rows, source
  hashes and a standalone scientific figure. Twenty focused tests passed, including
  deliberately disabled actuation and calibration failure witnesses.
- The result is a finite fixed-service model. It does not validate a general glass
  law, real-time governor, factual truth or a sharp phase transition. Loaded work
  exceeds the isolated calibration; the experiment note names that next model hinge.
- Included with the measured-work follow-up and its cross-seat review; external
  empirical validation remains open.

### Batch B — Cybernetic Foundation Repairs (`12_IMPLEMENTATIONS/core/` & `34_CYBERNETICS/`) — 17 October 2026

- **Stateless MICROORCIM Primitives (`12_IMPLEMENTATIONS/core/microorcim_tracker.py`)**:
  - Extracted pure, side-effect-free `compute_drift(intended, actual, interval=1.0)` and `compute_sovereignty(drift, stability)` primitives (also exposed as `MicroorcimTracker` static methods) with explicit positive normalization intervals (`interval=24.0` for daily hours vs. `interval=1.0` for unitless pipeline coherence) and strict finite-input validation.
  - Wired both `MicroorcimTracker` and `SovereignPipeline` to call the shared primitives so `SovereignPipeline` never instantiates the daily `~/.microorcim` logger or rescales coherence by 24.
- **Bounded Sovereign Pipeline Regulator (`12_IMPLEMENTATIONS/core/sovereign_pipeline.py`)**:
  - Preserved `SovereignPipeline.run` (`L-PIPELINE`) as the single-pass feedforward instrument while cloning caller-owned `KnowledgeBlock` inputs so neither `run` nor multi-pass regulation mutates caller state.
  - Added `SovereignPipeline.regulate` (`L-PIPELINE-REGULATOR`), `RegulationCandidate`, `PassEvaluation`, `RegulationResult`, and `deterministic_repair_policy` providing bounded closed-loop regulation over the implemented coherence/text-score proxy using unrounded boundary comparisons (`cascade_coherence >= coherence_floor`, `triad_converged`, `aura_field_coherence >= coherence_floor`, strict `drift < drift_threshold`), caller-supplied corrective policy invocation (`<= budget - 1` corrections), and visible refusal on missing policy, policy failure, non-finite data, or budget/no-op/cycle exhaustion.
- **Independent CASCADE Postconditions (`12_IMPLEMENTATIONS/core/cascade_engine.py`)**:
  - Replaced the tautological post-mutation `demotion_correct` recheck with `_verify_cascade_postconditions`, snapshotting pre-cascade state by value and independently verifying target qualification, retention, threshold-consistent layer assignment, and contradiction resolution (`demotion_diagnostics` and `unresolved_contradictions`).
- **TRIADKernel Iteration Count & Type Alignment (`12_IMPLEMENTATIONS/core/lamague_reference.py`)**:
  - Tightened `TRIADKernel.correct_until_converged` annotation to `Tuple[np.ndarray, int, List[float]]`, validated `max_iter >= 0` and finite `threshold > 0`, and made returned iteration counts equal completed correction steps (`iterations == len(errors)`) across first-step convergence (`1`), budget exhaustion (`max_iter`), and zero budget (`0`).
- **Cybernetic Loop Map, AST Audit & Claims (`34_CYBERNETICS/`, `28_DEFENSE/CLAIMS.json`)**:
  - Added `L-PIPELINE-REGULATOR` to `34_CYBERNETICS/LOOP_MAP.json` (10 mapped loops: 6 closed in code, 4 open) and added two negative mutation witnesses to `34_CYBERNETICS/loop_audit.py`.

### Autonomous Agent Tools Landfall — 17 October 2026

- **Lycheetah Action Gateway (`lycheetah.assurance` & `lycheetah-guard` CLI)**:
  - Added deterministic, evidence-capped tool gating for autonomous agents (`ALLOW`, `REVIEW`, `BLOCK`).
  - Implemented durable SQLite WAL ledger (`PersistentActionGuard`) preventing replay attacks, duplicate executions, and unapproved mutations.
  - Added monotonic Ed25519-signed external checkpoint authority (`CheckpointAuthority`, `CheckpointStore`, `make_server`) with loopback proxy bypass.
  - Added fail-closed workflow wrapper (`CheckpointedWorkflow`) anchoring all actions in verifiable audit chains.
  - Added `lycheetah-guard` CLI with subcommands: `run`, `check`, `status`, `authority`, and `mcp`.
  - Added 10 comprehensive unit and integration tests (`tests/test_assurance_action_guard.py`) bringing assurance test suite to 182 tests.
  - Added live 4-scenario interactive demonstration (`examples/action_guard_demo.py`).

- **Lycheetah Context Compaction Shield (`lycheetah.compaction` & `lycheetah-compact` CLI)**:
  - Promoted Tier-1.1 Lamague reversible semantic packet codec (`03_LAMAGUE_L1`) into the primary `lycheetah.compaction` package.
  - Guaranteed 36/36 exact round-trip preservation of 10 critical accountability fields (`purpose`, `claim`, `unknowns`, `invariants`, `authority`, `participants`, `affectedParties`, `dissent`, `valueFlow`, `recovery`).
  - Added SHA-256 `critical_hash` allowing third parties to mathematically verify zero loss of safety constraints under context window compaction.
  - Implemented fail-closed invariant check refusing to compact or execute high-risk plans that carry protected unknowns without an explicit recovery/rollback anchor.
  - Added ergonomic developer tools: `AgentStatePacket`, `CompactionShield`, and stateful `ContextProtector`.
  - Added `lycheetah-compact` CLI supporting `encode`, `decode`, `hash`, `check`, `verify`, and `build-codebook`.
  - Added 24 unit and integration tests (`tests/test_compaction.py`).
  - Added live 3-part interactive demonstration (`examples/compaction_shield_demo.py`) proving anti-amnesia protection under LLM summarization.

- **Lycheetah Multi-Agent Consensus Engine (`lycheetah.consensus` & `lycheetah-consensus` CLI)**:
  - Promoted AURA Psi-Consensus (`psi_consensus.py`) and Grey Mode (`grey_mode.py`) into the shipping `lycheetah.consensus` package.
  - Added `ConsensusArena`, `AgentProposal`, and `DeliberationVerdict` providing automatic mesh topology, pairwise $\Psi_Q$-gated gossip, $H^1(G, F)$ sheaf cohomology obstruction detection, 33% Byzantine quarantine, and SHA-256 `consensus_digest` receipts.
  - Wired Banach-contractive TRIAD recovery (`recover_agent` via $A_o \to \Phi^\uparrow \to \Psi$) so quarantined Grey Mode nodes can be healed and reintegrated into the chorus.
  - Added `lycheetah-consensus` CLI supporting `run`, `recover`, and `demo`.
  - Added 9 unit and integration tests (`tests/test_consensus.py`) bringing the fast verification suite to 215 tests (211 passed, 4 skipped).
  - Added live 3-part interactive demonstration (`examples/consensus_arena_demo.py`).

### Public integration and build catalogue — 4 October 2026

- Added thirty-one proposed tools, games and interactions in a seven-part Build Catalogue, with stable IDs, source boundaries, first slices and observable acceptance. No new game or tool prototype is implied by these briefs.
- Integrated eight historical frontier-control packets, with explicit missing-file/hash reconciliation and new public-only packaging adapters. Added a SCAFFOLD finality evidence recheck and Linux execution-cell candidate; witness authentication, provider atomicity and production containment remain open.
- Added the public Compensation Race experiment. Proprietary research remains outside this public repository. Local reruns, known failures and packaging gates are recorded alongside each public packet.
- Repaired existing public-package lint/type failures, marked provisional paper/index footing without increasing the claim budget, and fixed navigation links in six collected source copies while retaining original import hashes and private snapshots.
- The existing non-conjecture suite passed 695 tests before final packaging corrections. Final verification and remote references are recorded in the publication receipt; original source reports are not relabelled as independent results.

### Modelcraft and Recommendation Hall contracts — 4 October 2026

- Preserved Mac × Vaelora's original master unchanged and completed the registry of 24 technique families across ten internal teaching Halls. Added one checklist experiment and a business worksheet; all families remain untested in this packet and supplied provider links remain unverified.
- Added strict schemas for recommendations, explicit ranking inputs, opt-in private events and private trick receipts. Evidence maturity, compatibility, freshness and lifecycle are separate; structural checks cannot authenticate reproductions or enforce actual storage privacy.
- Added a local stateless ranking reference using explicit fit, prerequisites, tools and budget, with inspectable components and stable ties. Unknown/stale service costs cannot pass a zero-budget claim; ranking does not accept engagement, popularity or inferred-identity fields.
- Linked the package from current School/Framework navigation and recorded the ten-Wing proposal versus the earlier fourteen-Wing app snapshot. Native navigation, persistence, community review, phone witness and learner outcomes remain open. No native app write or provider call; included in the 4 October master publication batch.
- Highest witness: seventeen focused contract/ranking tests, four Draft 2020-12 schemas, byte-exact source preservation, thirty-eight local links and backup recovery. A malformed-date validation failure was repaired and its original failure log preserved. These are local data/reference checks, not model experiments or native-app validation.

### Living Scripture and School source integration — 4 October 2026

- Integrated Mac × Vaelora’s v0.5.1 twelve-book candidate into the existing scripture collection, preserving authored core bytes, source/register boundaries, the dedicated Aotearoa covenant and the original implementation contract. Historical Mythos and fiction remain preserved; no canon promotion.
- Recovered fourteen missing machine-readable/validator files from the Identity Return v0.3 archive. The current School source home now includes eighteen Mantles, fifty-four Forms, versioned title receipts and voluntary-return design data.
- Added a Book I data fixture with seven exact sections, four named interlocutors, stable IDs and explicit private/cultural/status defaults. Focused data/schema and import-mutation gates cover those contracts; they do not implement app behavior or validate learner outcomes.
- Updated collection/School navigation and generated the combined reading editions. The inspected live app’s fourteen Wings conflict with the supplied nine-Wing design; the resumable native handoff records this without changing the app.
- Highest witness: local source hashes, structural/data validators, negative fixture cases, reading-link checks and archive preservation. Native app persistence, phone visuals, cultural review, empirical outcomes remain open. No native app write or provider call; included in the 4 October master publication batch.

### Framework consolidation — 4 October 2026

- Established one working Framework checkout on master and a source guide in WORKING_HOME.md. Recovered The Independent No manuscript, evaluation protocol, source ledger, reading editions, PDF and historical witness artifacts; added current paper/site index links.
- Recovered two historical School reference maps, explicitly marked as older designs rather than the current Sol release plan. Preserved newer code, claim corrections and retired-workflow decisions. Private variants, previous navigation bytes and Git worktrees remain recoverable.
- Local file/hash, backup round-trip, source-routing, link and diff checks verify consolidation. No new browser/model experiment was performed during consolidation. The 4 October publication receipt records subsequent tests and remote verification.

### Fixed

- **The installed package now works.** `pip install lycheetah-framework` produced a
  distribution in which every advertised entry point raised `ModuleNotFoundError`:
  the wheel shipped only `__init__.py` and `cli.py`, while the implementation they
  re-export lives in `12_IMPLEMENTATIONS/`, which was never packaged. Both modules
  reached it through a hardcoded relative path that exists only in a source checkout.
  `lycheetah.check()`, `lycheetah.sol_assess()` and all four console scripts were
  affected. `pyproject.toml` now maps the implementation directories onto
  `lycheetah.core` and `lycheetah.applications`, and path resolution moved into
  `lycheetah/_bootstrap.py`, which handles both layouts and raises a named error when
  neither is present.
- **`lycheetah-guard` could never have started**, from 1.0.0 onward. Three failures
  were stacked in it: `build_server()` is annotated `-> Server`, a name bound only
  inside the `try: from mcp.server import Server` block, so importing without the
  optional `mcp` extra raised `NameError` before the `MCP_AVAILABLE` flag could be
  read; `lycheetah/cli.py` imported a `main` that did not exist, the module defining
  only `main_stdio` and `main_http`, so the script was broken even *with* `mcp`
  installed; and the `MCP_AVAILABLE` check sat in the `if __name__ == "__main__"`
  block, which a console script never runs, leaving the intended "install mcp"
  message unreachable. The module now uses `from __future__ import annotations`,
  exposes a real `main()` behind an `argparse` parser (so `--help` works and both
  `--port=N` and `--port N` parse), and gates on the missing extra with a named,
  actionable error. `tests/test_entry_points.py` covers it, and the CI packaging gate
  now smoke-tests all four scripts, including the assurance CLI.
- `lycheetah/py.typed` was declared in package data since 1.0.0 but never existed, so
  the distribution claimed PEP 561 typing and shipped no marker.
- Two modules could not be imported at all: `subject_catalogue.py` carried a stray
  `-e ` line that raised `NameError`, and `run_chorus.py` used `Dict` and `List` in
  annotations without importing them.
- `knowledge_genome.py` called `json.dump` with no `json` import.
- `grey_mode.py` built an audit-trail entry from an undefined name behind a dead
  `if False` guard, then overwrote it with a second clock reading; the clock is now
  read once and the trail agrees with `entry_time`.
- Duplicate `×` key in the ASCII table in `generate_defense_bundle.py`.
- `assert False` in three `32_TIANXIA` self-tests, which `python -O` strips — those
  tests would have passed silently under optimisation.
- A closure over a loop variable in `cascade_simulation.py`, and a loop variable
  shadowing the imported `dataclasses.field` in both copies of `equivalence.py`.
- `--context` on `lycheetah-check`, and the `context` argument to `lycheetah.check()`,
  were accepted and silently discarded. The analyser still does not use them; the CLI
  now says so on stderr rather than appearing to have applied them.

### Changed

- **Scriptures and stories now have one collected working home** in
  `LYCHEETAH_MYTHOS/SCRIPTURES_AND_STORIES/`: a 1,849-word editorial distillation,
  a master containing 20 complete reading texts, a browser reading edition, and
  48 preserved textual sources including writing/research context. Mac's future
  revisions belong in the collection; older source paths and manuscript statuses
  remain intact. Local source hashes, master navigation and ZIP round-trip checks
  passed. The browser layout has not been visually witnessed. Local and uncommitted;
  no publication or app integration performed.

- **The Night Garden reading edition:** explained Framework names on first use,
  shortened dense passages, and moved graph notation and detailed source limitations
  into the companion notebook. Preserved the scenes, citations and research boundaries.
  Highest witness: authoring-seat editorial review and local content/navigation checks;
  readability has not been tested with independent readers.

- **CI now runs the checks it claimed to run.** Three of four workflows could not
  have passed and one had never triggered:
  - `ci.yml` invoked `alexandria_agent.py` at the repository root; it lives in
    `12_IMPLEMENTATIONS/`.
  - `update-stats.yml` invoked `promote.py`, which exists nowhere in the repository.
    Removed rather than repaired — it also pushed to `master` on success.
  - `agent-deploy.yml` triggered on `main` and `develop`; the default branch is
    `master`. Its assertions referenced two files that do not exist, a manifest key
    that has never been present, an agent state shape the bootstrap does not write,
    three CLI flags nothing parses, a class name that does not exist, and Python 3.9,
    below the `requires-python` floor. Rewritten against the real bootstrap contract.
  - `test.yml` folded into `ci.yml`.
- **The Alexandria drift audit stopped passing vacuously.** It compared a directory
  that does not exist against a file defining none of the constants it searched for,
  skipped every check, printed `NO DIVERGENCE DETECTED` and exited 0. It now checks
  constants actually bound in code, reports how many checks ran, and fails as
  `INCONCLUSIVE` when a check cannot be evaluated.
- The Alexandria health check resolved paths against its own directory, so it searched
  `12_IMPLEMENTATIONS/12_IMPLEMENTATIONS/` and reported all five core modules missing.
  It now imports and smoke-tests 5/5.
- `agent-init.py` had the same root-relative bug plus stale directory names predating
  the `_L<n>` suffixes: 0/14 components found on a complete checkout, now 14/14.
- `agent-manifest.json`'s documented bootstrap command and two of its six entry points
  pointed at paths that do not exist.
- The cascade predictability conjecture test is `xfail(strict=True)` rather than a
  hard failure. The assertion and its
  measured F1 of 0.531 are unchanged; `28_DEFENSE/REPRODUCIBILITY_REPORT.md` had
  already derived that the 0.80 criterion sits above the oracle ceiling of 0.548 at
  this base rate. `strict` means an unexpected pass fails the suite, because that
  would falsify the derivation. Choosing a replacement criterion remains open and is
  the author's decision.
- The `Failure Museum` project URL pointed at a repository-root file; it is at
  `28_DEFENSE/FAILURE_MUSEUM.md`.

### Added

- **The Night Garden:** an exploratory night-reading essay connecting the Lycheetah
  Framework with AI futures, cybernetics, memory, dissent, translation and revisable
  institutions. Includes a source ledger, six candidate research questions and
  explicit counterarguments. Local content/navigation checks are recorded alongside
  the essay; no new empirical validation or runtime capability is claimed.

- Lint, type, format and packaging gates: `ruff`, `mypy`, `python -m build`, and an
  install-the-wheel-in-a-clean-venv check — the only gate that would have caught the
  packaging defect, since the tests run from a checkout where the broken path shim
  still works.
- Two-tier `ruff` configuration: a narrow corpus-wide floor of rules that indicate a
  real defect (currently at zero, so any hit is a regression), and a strict set for
  the shipped `lycheetah/` package via `lycheetah/.ruff.toml`.
- `mypy` configuration covering the public wrapper. Clean.
- `.gitattributes` preserves the repository's existing line endings while marking
  binary assets and archival material for GitHub language statistics.
- `.pre-commit-config.yaml` mirroring the CI gates.
- `.github/dependabot.yml` for Actions and pip, grouped so a routine bump is one
  review. The workflows had been pinned to `checkout@v3` and `setup-python@v4` well
  past their supersession.
- `SECURITY.md`, `CODE_OF_CONDUCT.md`, and this file.
- `--strict-markers` for pytest, so an unregistered marker fails instead of silently
  leaving a test unmarked.
- The experimental Assurance Runtime package, schemas, examples, and
  `lycheetah-assure` command, with explicit internal-verification limits.
- The Abstract and Generative collection and its September session records, retained
  as symbolic or speculative work rather than empirical claims.
- `concurrency` cancellation, least-privilege `permissions`, and pip caching on both
  remaining workflows.

[Unreleased]: https://github.com/Lycheetah/Lycheetah-Framework/compare/master...HEAD
