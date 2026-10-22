# G-decisions for Mac

**Collected 2026-10-23** from the 38 batch ledgers, copied verbatim from each ledger's decisions section so nothing is paraphrased. Each item is Mac's call; *Sol's call* lines are recommendations, never applied rulings. Items marked **Done** were closed after the batch was written, with the commit named.
**Count:** 115 distinct G-IDs across 36 batches. Batches 1–13 recorded their decisions inline in the findings tables instead.


Start with the short list in [OUTPUT5_REPAIR_SEQUENCE.md](OUTPUT5_REPAIR_SEQUENCE.md), which orders these by urgency and dependency.

## [B2](BATCH2_FINDINGS_AND_LEDGER.md) — Opus review — Batch 2: findings register and coverage ledger

### Proposals for Mac (none applied)

- **P1 — permit v3.** Bind the full packet hash, or a declared field set, so a
  permit names exactly what it authorises.
- **P2 — claim ordering.** Claim a permit or effect only after everything that
  can fail before execution has succeeded. Otherwise, make the claim
  releasable on a pre-execution failure. This applies to the gateway and the
  harness.
- **P3 — recovery as resubmission.** Recovery writes the agent's new vector
  inside the arena, so the arena authors an agent's position. Emit the
  recovered vector as a candidate that the agent must resubmit.
- **P4 — r_merge redesign.** Count Δt in deliberation rounds from isolation
  entry, not in wall-clock seconds from `run()`. Then cap or rescale r_merge
  against `r_c` so the threshold can bind.
- **P5 — quorum.** Add a harness `min_agents`, and tie it to the claimed budget:
  tolerating f faulty agents needs n ≥ 3f + 1, so 4 agents for f = 1 (DERIVED,
  standard BFT bound). This supersedes the "3" I suggested in chat.
- **P6 — TRIAD sign semantics.** Choose rays or vectors. If rays, consensus and
  Grey Mode must be sign-free end to end. If vectors, `detect_drift` and
  `anchor_operator` become signed, and the census above migrates together.
- **P7 — canonical edge order.** Iterate agents and neighbors in sorted order,
  so a verdict digest does not depend on insertion order.

## [B3](BATCH3_FINDINGS_AND_LEDGER.md) — Opus review — Batch 3: findings register and coverage ledger

### Proposals for Mac (none applied)

- **P8 — One side-effect classifier.** The gateway and harness would share a single
  function.
  - An integrator-owned tool registry, not the actor, classifies each tool.
  - Unknown tools and any action that carries `command` default to side-effecting.
  - The substring screen stays, but is labelled a tripwire, not a boundary. It should
    match `/` as a whole argument, which fixes the `/tmp` false positive.
  - This changes the default for every API caller, so it is your call.
- **P9 — Authenticated approvals.** An approval would carry a signature from a key the
  gateway trusts, not a declared name. A signed-approval path exists in
  `papers/ai-futures/hybrid-gateway/v1.2` (`issue_approval(batch, plan, key_id,
  secret)`). It was seen at call sites only and has not been reviewed. Whether to adapt
  it is a design decision.
- **P10 — The authority's trust domain.** Options:
  - (a) keep `open_local` as is, now documented;
  - (b) `open_local` and the CLI warn when the authority shares the ledger's directory;
  - (c) the CLI starts or expects a separate authority process.
  - (a) is applied. (b) and (c) are yours.

## [B4](BATCH4_FINDINGS_AND_LEDGER.md) — Opus review — Batch 4: findings register and coverage ledger

### Proposal for Mac (not applied)

**P11 — Give an operator a reviewed way past a dirty tail.** Sol's stance: build
option (b). A ledger that one network blip kills permanently is not fail-closed
design. It is fail-dead, and it pushes operators to delete the directory, which
destroys the very history the checkpoint exists to protect.

- (a) Keep today's behaviour: permanent block, with recovery only by hand outside the
  tool.
- (b) **Recommended.** Add `lycheetah-guard adopt-tail --operator NAME --reason TEXT`.
  It verifies the hash chain and state replay, prints every uncheckpointed event, and
  requires that the tail extends the latest checkpoint exactly. It then appends a
  `TAIL_ADOPTED` event naming the operator, reason and adopted range, and publishes the
  whole range as one new generation. Every adoption stays visible in the history, so
  nothing is blessed silently. The three pinning tests stay true for automatic paths.
- (c) Retry the publish automatically on the next mutation. Rejected: that is exactly
  the silent blessing the existing tests forbid.

## [B5](BATCH5_FINDINGS_AND_LEDGER.md) — Opus review — Batch 5: findings register and coverage ledger

### Proposals for Mac (not applied)

- **Proposal 12 — precise reason for an unserialisable result (P07).** Report
  `invalid_result_details_requires_reconciliation` when the result could not be
  serialised, and keep the outage reason for a real checkpoint failure. The
  outcome does not change: it stays `UNKNOWN` and held. This changes a public
  reason string, so it is Mac's call.
- **Proposal 13 — secrets at rest (P09).** Options:
  - (a) Keep the current behaviour, now documented. This is the default.
  - (b) Store sensitive argument values in the ledger as a keyed hash plus an
    encrypted blob, decrypted only at dispatch.
  - (c) Exclude `details_json` for provider results from the checkpoint payload
    and checkpoint only its digest.

  Option (c) is the smallest change that keeps provider answers off the wire. It
  changes the checkpoint format, so it would need a version bump.

## [B6](BATCH6_FINDINGS_AND_LEDGER.md) — Opus review — Batch 6: findings register and coverage ledger

### Proposals for Mac (not applied)

- **Proposal 14: refuse a risk downgrade at the shield.** Sol's stance is
  **yes**. A compaction is a summary, and a summary that lowers risk is amnesia
  of severity, the exact failure the shield is named for. A legitimate downgrade
  is a new decision, not a compaction. The rule belongs in `classify` as a
  comparison (candidate risk below reference risk is UNSAFE_COLLAPSE `risk`), not
  in the hash, so `critical_hash`, the wire bytes and every digest stay the
  same. Escalation stays PARTIAL. Costs: the two pinned assertions in R5 change.
  Gate 2 runs before the harness's risk binding, so a downgrade's stop reason
  would become COMPACTION_UNSAFE_COLLAPSE, unless the harness binds risk first.
  `examples/guarded_handoff_risk_demo.py:318` and `:430` expect
  CANDIDATE_RISK_MISMATCH, and the frozen evidence under
  `34_ASSURANCE_RUNTIME/evidence/guarded-handoff-risk-2026-10-18/` would then no
  longer reproduce from current code unless that ordering is kept. Standalone
  users of `CompactionShield`, which the README presents on its own, are the ones
  exposed today.
- **Proposal 15:** one statement of the export rules (R7).
- **Still open from earlier:** whether evidence, yield and horizon should become
  critical. Unlike Proposal 14, this changes `critical_hash` and every digest
  ever recorded.

## [B7](BATCH7_FINDINGS_AND_LEDGER.md) — Opus review — Batch 7: findings register and coverage ledger

### Proposal 16 — One installable codec (for Mac)

Sol's call: **A now, B only if the standalone package matters as a product.**

- **A.** Apply the staged patch, so the frozen folder's own post-seal pages say
  what they install and point to `lycheetah.compaction.codec`. Do not publish
  `lamague-codec` 1.0.0 as it stands. One truth, one implementation: the second
  installable codec has already drifted from the first.
- **B.** Cut `lamague-codec` 1.0.1 in a new versioned folder, carrying the
  maintained validation and strict decode, with its own manifest. v1.0 stays
  sealed as the counterexample. This is the open "frozen patches as new
  versions" decision.
- **C.** Restore the sealed README, which reverts the README half of `dfe7c55`.
  That puts the folder back inside its seal, but it drops the install story Mac
  approved on 2026-08-08.

Whether `lamague-codec` was ever published to a package index is UNVERIFIED.
No network check was made.

### Open for Mac

Proposal 16 (A, B or C), and A1: leave the seal as history, or restore the
sealed README. The open "frozen patches as new versions" decision now has a
concrete first case.

## [B9](BATCH9_FINDINGS_AND_LEDGER.md) — Opus review — Batch 9: findings register and coverage ledger

### Open decision for Mac

Build a real chorus, or keep it as a labelled design sketch? Sol's stance is to
keep the sketch (DERIVED). The Framework's live enforcement path is the
`lycheetah/` package: the sovereign harness, consensus and the guarded handoff. A
second constitutional engine inside a demo folder would be a parallel
implementation of the same law. If the chorus is revived, it should be an
adapter: nine role prompts whose outputs pass through the harness. It should not
be new verdict logic.

Next workstream: RV11, the frozen policy-evolution gate (reproduce, stage a patch,
do not edit).

## [B11](BATCH11_FINDINGS_AND_LEDGER.md) — Batch 11 — RV12: blind-review aggregator admission

### Decisions for Mac

- **D1.** Apply RV12 as Policy Lab v0.2.1 inside a new handoff version (Sol's recommendation), or
  re-seal v1.3 in place.
- **D2.** Keep the reviewer-ID guard in `reviewer.html` (recommended), or enforce it in the aggregator only.
- **D3.** Also require `schema_version == "anon-politician-review-v0.2"` in `main()`. This closes F1
  completely, but the existing fixtures need that field added.
- **D4.** Whether F8 (reporting disagreement) is wanted before the first real review round.

## [B12](BATCH12_FINDINGS_AND_LEDGER.md) — RV13 · Batch 12: Findings and Ledger

### 4. Open decisions added for Mac

1. **Install `mcp==2.3.0`?** `pyproject.toml` already declares 2.x. Installing it lets G4 and `test_mcp_guard` run, after which the staged raise-on-failure fix for the guard can be applied and witnessed.
2. **`sol_workspace_mcp`: retire, repair, or repoint?** It is still configured as an SSE server in `~/.claude/settings.json`.
3. **Contract change in `compute_tes`:** out-of-range inputs now raise instead of clamping. This needs Mac's acceptance, because any external caller that relied on the clamp will see a `ValueError`.

Nothing in this batch touched frozen or checksummed research, Caelorynth surfaces, `_PROPRIETARY/`, AZOTH or Sol Prime.

## [B13](BATCH13_FINDINGS_AND_LEDGER.md) — Batch 13 — RV14: the LAMAGUE parser patch and grammar conformance

### 3. Grammar decisions for Mac (G1–G7)

The parser and `04_BNF_GRAMMAR.md` are different grammars. This batch did not choose between them.

- **G1 — what ↯ is.** The BNF lists ↯ only as a `<dynamic>`, and its prose table calls it a *Junction* with the form `condition ↯ [option_a], [option_b]`. Batch 1 made it a binary operator, so `Ψ ↯ Ao → Φ↑ → Ψ_inv` reads as `((Ψ ↯ Ao) → Φ↑) → Ψ_inv`. Before batch 1, HEAD parsed that line as just `Ψ` and dropped the rest without a word.
- **G2 — precedence and associativity.** The BNF's `<composition> ::= <expression> <operator> <expression>` is ambiguous: it gives no precedence and no associativity. The parser uses one flat level, left-associative, so `Ψ → Ao ⊗ Φ` is `((Ψ → Ao) ⊗ Φ)` (P8).
- **G3 — dynamics standing alone.** The BNF makes `→ ⊗ ⇌ ⟲` complete expressions, because each is a `<dynamic>`. The parser refuses all four on their own but accepts a lone `↑` as a "modifier" leaf (P2).
- **G4 — the constraint language.** The parser validates each segment after `|` as an ordinary expression (batch 1). The BNF's own canonical line, `Ao → Φ↑ → Ψ → Ψ_inv | C(Ψ_t) ≥ C(Ψ₀)`, uses `C(…)` and `≥`, which neither grammar defines, so the parser rejects it (P5).
- **G5 — compounds.** `↑` and `_subscript` exist in the parser, not in the BNF. Open questions: `Ao↑`, `↑` after a subscript, and a lone `↑`.
- **G6 — `·`.** Proposal 02 adds `·`. The parser does not know the symbol (P6).
- **G7 — the BNF cannot derive its own examples.** In lines 17–50 no production yields `Φ↑` or `Ψ_inv`, so the canonical TRIAD cycle `Ao → Φ↑ → Ψ_inv` is not in the language the BNF defines. The same section still says "[ACTIVE] — grammar is formally specified and parseable". DERIVED from the grammar text.

### 11. Open decisions added for Mac

1. Grammar: G1 to G7 (§3).
2. The batch-1 parser diff: confirm the authorization and record it, or withhold it (§4).
3. The staged BNF patch: apply it and re-seal the manifest, or leave it (§7).
4. The parser limits: keep 256 operators and 64 nesting levels, or set others.
5. Aetheron's README contradictions: pass them to Aetheron by your hand (§4).

## [B14](BATCH14_FINDINGS_AND_LEDGER.md) — Batch 14: RV15, the LAMAGUE status register and the folders it rates

### 8. Decisions for Mac (added this batch)

- **G-RESEAL.** Re-seal `MASTER_MANIFEST` at the current tree, retire it, or put it under a
  test. The three staged patches wait on this.
- **G-NEGATIVE.** Should the register get a "MEASURED-NEGATIVE" status? Spoken LAMAGUE is now
  SCAFFOLD under the existing rule, even though its verifier ran and gave a real, reproducible
  negative.
- **G-PSI.** Pick one meaning of Ψ for the grammar, and name the kernel-tier operator
  separately (or mark it as an overload).
- **G-INV.** Is `Ψ_inv` a field with a subscript (as in the parser) or an `Invariant` (as in
  Core v0.2)?

## [B15](BATCH15_FINDINGS_AND_LEDGER.md) — Batch 15: RV16, SXP-L and the authority-bridge proposal

### 6. Decisions for Mac

- **G-SXPL-LAND:** land the counter-patch as a v2.1 next to the frozen v2.0, or re-pin v2.0.
- **G-FIXTURES:** restore `runtime/examples/` from v1.8 in the landing version.
- **G-REPAIR-FLAG:** confirm the policy that a same-label repair moves a boundary to
  "superseded" but keeps `review_advised`, rather than clearing it as proposal 03 does.
- **G-SXPL-GRAMMAR:** rule on the five grammar and schema findings, one by one.

## [B16](BATCH16_FINDINGS_AND_LEDGER.md) — Batch 16: RV17, compression and interoperability claims

### 9. Decisions for Mac

- **G-RV17-PATCH:** apply `RV17_ratio_status_notes.patch` to the pinned root corpus and reseal
  `MASTER_MANIFEST` (09 already needs resealing), or keep the notes only in this ledger.
- **G-CODEC-BASELINE:** a codec v1.1 whose benchmark reports conventional baselines.
- **G-PYC-SEAL:** re-seal the codec package without `__pycache__`.
- **G-SPL-MERGE:** the merged spoken inventory is ambiguous (`witan`) even with sai-an read apart.
  Require a separator in merged speech, or change a phoneme.

## [B17](BATCH17_FINDINGS_AND_LEDGER.md) — Batch 17 — RV18 mathematics: findings and ledger (review 2026-10-22)

### Decisions for Mac

- **G-LYAP:** land the honest-status patch, and/or install sympy and regenerate the results JSON.
  Without sympy, a regenerated JSON would drop the five sympy records.
- **G-PITH:** choose one Π_th truth: a calibrated constant per domain, or the √n conjecture with
  its normalization stated. Then sweep the census.
- **G-MASTER-EQ:** the master equation as written cannot bifurcate at Π_th. Either restate it as an
  equilibrium shift, or add a Π-dependent term to the restoring force so that stability can
  actually change.
- **G-C1:** exclude foundation blocks from demotion (a behaviour change, so it waits for you), or
  retract C1.

## [B18](BATCH18_FINDINGS_AND_LEDGER.md) — Batch 18 — RV19 claims register: findings and ledger (review 2026-10-22)

### Decisions for Mac

- **G-RV19-POINTERS**: apply `RV19_claims_pointer_repairs.patch` to CLAIMS.json? If yes, re-pin
  or annotate the 10-20 `claim-assessments.json` sha (it would otherwise point at a superseded register).
- **G-EMPIRICAL**: what EMPIRICAL_RESULTS becomes. Options: (a) produce the materials; (b) set its
  status to UNVERIFIED or RETRACTED and point the 25 mirrors at that one ruling; (c) keep the notes as they stand.
- **G-CAS-STATUS**: the author statuses of CAS-009/011 (ACTIVE; no runner exists) and the wording of
  CAS-010 (honest form: "beats a no-update baseline; ties additive update on these five encodings").
- **G-TC-COUNT**: ANA-003/004 say 4; the only resolving statement says ≥3. Which is the claim?

## [B19](BATCH19_FINDINGS_AND_LEDGER.md) — Batch 19 — RV20 Cellular sheaf and factorial experiment

### Decisions for Mac

- **G-PAID-WORK.** Either (a) make lookahead + work_coupled pay actual work (incremental service: extend the completion when the live adjudication exceeds the estimate), or (b) keep the mechanism and rename the rule `estimated_work_at_start` everywhere it is reported. That label already appears in `service_rule`. Sol's call: **(a)**. A factor called "work coupled" that leaves 8.67× of the work unpaid is measuring the wrong thing, and (b) only names the flaw.
- **G-SHEAF-ENCODING.** Reject labels outside {a, b} (or give every label a distinct basis vector, with d ≥ the label count) instead of hashing. Sol's call: **reject**. Collisions turn real disagreement into "consistent", silently.
- **G-CONSENSUS-H1.** Amend `CHANGELOG.md:425` with a dated correction line (H¹ here counts mesh cycles; disagreement is the Dirichlet energy), or leave the history as written and let the docstring carry the truth. Sol's call: **dated correction line**, not a rewrite.
- **G-FACTORIAL-RECORD.** Record one factorial run with receipts into GLASS_TRANSITION, or leave the module as an unrecorded instrument. Sol's call: **after G-PAID-WORK** — recording now would enshrine F1.

## [B20](BATCH20_FINDINGS_AND_LEDGER.md) — Batch 20 — RV21 Truth Pressure forge, cybernetics and Tianxia operators

### Decisions for Mac

- **G-FORGE-REMINT.** Applying any staged patch changes a frozen bundle. Its `SHA256_MANIFEST.json`, its zip and the forge `SHA256_MANIFEST.txt` must then be re-minted together, and the new mirror test will refuse a half-done re-mint. Sol's call: **one re-mint covering whichever patches you accept**, with a dated line in each bundle README naming the review.
- **G-TP-ANNOTATION-INTEGRITY** (F2, F3). Sol's call: **apply now.** This is the only one with a deadline. The pre-registration's no-moving-target rule binds once the first packet is opened. After that, the analyzer can't change without breaking the pre-registration.
- **G-TP-COLLECTOR-SECRETS** (F4). Sol's call: **apply before any future run, and do not run v0.8 until then.** A pattern scan narrows the risk but does not close it. The patched message says so.
- **G-TP-SHADOW-GATE** (F1). Sol's call: **apply at the re-mint**. Until then, don't cite the recorded `ENGINEERING_GATE_MET` as a gate result.
- **G-REN-ZHENG-ONE-DEFINITION** (F5, F6). Sol's call: **the implemented operator is canonical** (it is tested and audited, and its bounds were hardened on 2026-08-08). The worked examples should be recomputed under it. The `CLAIM_STATUS_LEDGER.md:186` line is Zenodo-linked canon, so its correction is yours: a dated correction line, not a rewrite.
- **G-MASTER-EQ-STATUS** (F7). Rewrite the §6 rows to UNVERIFIED, or keep the dated notes. Sol's call: **keep the notes** until the Batch 17/18 decision on the equation itself, then rewrite once.

## [B21](BATCH21_FINDINGS_AND_LEDGER.md) — Batch 21 — RV22 Agent-Safety Continuations: Findings and Ledger

### Decisions for Mac

- **G-ET-SKIP-COUNT.** Apply `RV22_earned_trust_skip_count.patch` and re-mint that one file's digest in the 10-18 intake manifest in the same dated change? **Sol: yes.** A verifier that turns a skip into a pass is the exact upgrade-by-rhetoric this repo forbids, even when the README hedges it.
- **G-INTAKE-1019-RECORD.** Re-mint `current_sha256` / `changed_since_import` for `VALIDATION_AND_LIMITATIONS.md` in the 10-19 manifest, or leave the record as the 10-19 snapshot? **Sol: re-mint with a dated note.** The manifest's own fields exist to track post-import change.
- **G-CI-CONTINUATIONS.** Extend `.github/workflows/agent-safety.yml` to run the earned-light, sovereign-choice, earned-trust (`--tests`) and hybrid verifiers? **Sol: yes, after G-ET-SKIP-COUNT.** Run earned-trust from a short working directory (F4), and use the fixed runner so CI prints 369 + 9 skipped rather than 378 passing on a non-root runner.
- **G-FRONTIER-REPORT-SAMPLE.** Drivers 01–05 overwrite a committed, manifested report with a run-dependent sample (F12). Options: (a) add `--output`, defaulting outside the tree, so the committed report stays a dated sample; (b) say in each README that the report is one sample and the counts vary per run; (c) leave it. **Sol: (b) now and (a) when the code is next touched.** These are frozen intake files, so either change needs a re-mint of the manifest.
- **G-SIM-VERSION-LABEL.** Change the simulator README header to v0.3? **Sol: yes, trivial.** Held only because `simulator/README.md` is an entry in the historical v0.3 `artifact-manifest.json`, and changing it is a choice about that receipt, not a typo fix.

## [B22](BATCH22_FINDINGS_AND_LEDGER.md) — Batch 22 — RV23: 33_APPLICATIONS and 31_EMPIRICAL

### Decisions for Mac (G-items)

- **G-TP-PERSONA-NOTE.** Apply `RV23_truth_pressure_persona_note.patch` to the canonical TP master? If
  so, re-run `reflexive_audit.py` in the same change.
- **G-LENS-VERSION-STAMP.** Should `external_validation.py` and `independent_publisher_test.py` print
  `git rev-parse HEAD` beside their numbers, so a dated report carries its commit? This is cheap and
  closes F2/F3 for good.
- **G-CONVENTIONAL-BASELINE.** Add a TF-IDF + logistic-regression baseline on the same splits? It needs
  no provider, and it is the comparison every outside reviewer will ask for first.
- **G-PREREG-FILING.** Either file E-1-A / E-1-D on OSF, or rename the headings from "preregistered" to
  "draft preregistration". The notes hold the line until you choose.

---

## [B23](BATCH23_FINDINGS_AND_LEDGER.md) — Batch 23 — RV24: NZ governance and policy coherence

### Decisions for Mac (G-items)

- **G-CIVIC-CLAIM-SHAPE.** Apply `RV24_civic_signal_claim_shape.patch` and re-mint both `SHA256SUMS.txt`
  lists with a dated note? The QUICK_ACCESS zip copies would stay at the original v0.3 bytes as a
  record.
- **G-WOF-V0.2.** Write the six-rights WOF v0.2, or drop the "should not get its WOF" sentence until it
  exists.
- **G-NZ-LEGAL-READ.** The proposal's own next step 3, a NZ privacy lawyer. With IPP 3A now in force,
  this read is the highest-value step left for Right 1.

---

## [B24](BATCH24_FINDINGS_AND_LEDGER.md) — Batch 24 — RV25: Māori and cross-cultural claims

### Decisions for Mac (G-items)

- **G-OUTREACH-SENT.** Were any of the Te Tumu, MBIE or Chinese-partner emails sent with the old
  errors? If one reached Professor Ruru with "Ngāi Tahu", a short correction would be the right
  follow-up. Sol has no way to check.
- **G-FOUNDATION-ENTITY.** Is "Lycheetah Foundation" a registered entity? If not, the 46 files that use
  it, two of them in grant drafts, should say "Lycheetah Framework (independent researcher)".
- **G-LAMAGUE-EXPANSION.** Four expansions of the acronym are in use:
  - 9× "Language of Alignment, Measurement, and Governance for Universal Ethics";
  - 4× "Language for Autonomous Mathematical Alignment and Universal Grammar Evolution";
  - 1× "Language for Everything";
  - 1× "Language-Agnostic Multi-Tradition Governance Universals".

  Pick one, under the one-truth law.
- **G-CONVERGENCE-HEADLINE.** Recast the cross-cultural headline from "independent discovery" to "a
  proposed mapping awaiting blind encoding by each tradition"? That would mean rewriting the abstracts
  of the paper draft and the application rather than annotating them. This is an authorship choice.

---

## [B25](BATCH25_FINDINGS_AND_LEDGER.md) — Batch 25 — RV26: Mystery School, learning, psychological and consciousness claims

### Decisions for Mac (G-items)

- **G-CRISIS-LIST-OWNER.** Someone should re-check NZ helpline hours on a schedule. Open the Lifeline
  item of 9 Oct 2026 first: if it restored 24/7 service, the hours note needs updating.
- **G-CURRICULUM-ONE-ARCHITECT.** `systems/aura_sovereign_codex.py:962` holds a second
  `CurriculumArchitect` with a different, also arbitrary forecast formula
  (`-baseline × effect_size × 0.3`, L1043/1046). Retire it, or point it at the fixed generator?
  It was not edited.
- **G-MINDFULNESS-EFFECT-SOURCE.** Do one full-text sourcing pass for the protocol effect sizes and
  population SDs (Goyal 2014, Khoury 2015, Lehrer 2000, GAD-7/PHQ-9/WEMWBS norms). After it,
  `population_sd` can be filled in and the pages regenerated with raw points.
- **G-RETURN-VALIDATOR-TEST.** Give `return_validator.py` its own test, using the probe table above as
  its fixtures?

---

## [B26](BATCH26_FINDINGS_AND_LEDGER.md) — Batch 26 — RV27: Sol / Veyra, MEMORIA, Interface Intelligence, Sol Protocol, For-AI

### Decisions for Mac (G-items)

- **G-II-STATUS:** the frozen PDF `INTERFACE_INTELLIGENCE_MASTER_2026-09-26.pdf` repeats F1. Re-mint it with the note, or keep it frozen with a pointer?
- **G-DEAR-AI-RETIRE:** retire DEAR_AI into `99_ARCHIVE` and let AI_EXTRACTION_PROTOCOL be the single AI entry point, or keep both?
- **G-SELF-CHECK-SEMANTICS:** the self-check is heuristic. Rename C_field's output label to "heuristic score", and keep the tool out of any public claim of "AI alignment checking"?
- **G-MEMORIA-IMPLEMENTATION:** build a small file-based memory reference (tiers = session notes / memory files / constitution, consolidation = an edit review), or keep MEMORIA as theory?
- **G-VIP-WORDING:** apply F7 to the 25_ README and v4?
- **G-VEYRA-STATUS:** a full read and relabel of the three "[ACTIVE] operational" 16_ specs.
- **G-MIRROR-GENERATION:** generate the mythos 26_FOR_AI mirror from source with a link rewrite.

## [B27](BATCH27_FINDINGS_AND_LEDGER.md) — Batch 27 — RV28: Creative corpus and source ownership

### Decisions for Mac

- **G-EPIC-LISTENING-SOURCE:** which file is the Long Light's home? See F2 (a) or (b).
- **G-ORIGINAL-POINTERS:** add pointer lines to the 48 originals, with a deliberate hash re-record?
- **G-STORY-GATES-IN-SUITE:** add the four Living Scripture gates to the pytest suite? They pass now (~0.2 s).
- **G-SCRIPTURE-ATTRIBUTION:** confirm the "GPT-5.6 Sol" co-author string.
- **G-COMIC-ART-WEIGHT:** 128 MB of comic PNGs live in the Framework's heart repo. Keep them, or move them to Git LFS or a release asset? This is storage only, not taste.

## [B28](BATCH28_FINDINGS_AND_LEDGER.md) — Batch 28 — RV29: READMEs, synthesis and current navigation

### Decisions for Mac (G-items)

| G-item | Decision |
|---|---|
| **G-AURA-DOC-STATUS** | Keep the AURA enforcement document at the root as an annotated design, move it to an archive or design folder, or rewrite it as a proposal. Was it part of the Zenodo deposit? If so, the deposited version is frozen and only the repository copy carries the note. |
| **G-KNOX-ENDORSEMENT** | Is there a record of an arXiv endorsement for CASCADE? If yes, add the receipt. If no, strike the line. |
| **G-ANTHROPIC-PAUSE-SOURCE** | Source the "this week" report, or strike the paragraph. |
| **G-AGENTS-LOCAL-PATH** | Approve the F6 wording change in the root `AGENTS.md`. |
| **G-FOLDER-READMES** | Choose: thin READMEs that point to the index row, or leave the index as the only description. |
| **G-COUNTS-ONE-SOURCE** | Stop hand-typing claim counts (F8). |
| **G-PROPOSALS-TRACKING** | `FOR-REVIEW/2026-10-21_PROPOSALS/` is untracked. The link gate reads it locally, but a clean checkout and CI will not see it until it is tracked. Decide whether to track it. |

## [B29](BATCH29_FINDINGS_AND_LEDGER.md) — Batch 29: RV30, the footing gate and the documents it flagged

### G-items for Mac

| ID | Decision |
|---|---|
| G-RV30-1 | Regenerate or drop `current_sha256` for maintained files in the 10-19 manifest |
| G-RV30-2 | Replace `BASELINE` with a byte-pinned reviewed-footing register |
| G-RV30-3 | Tighten the vocabulary to positioned status tokens |
| G-RV30-4 | Retitle the TRIAD and CHRYSOPOEIA citations to the proven scope |
| G-RV30-5 | Have a fluent speaker revise the Chinese convergence sentence |
| G-RV30-6 | Check that DOI 10.5281/zenodo.20020828 resolves to the C-1.1 record |
| G-RV30-7 | Confirm a working author email before any submission or pitch |

## [B30](BATCH30_FINDINGS_AND_LEDGER.md) — BATCH 30 — RV31 · 99_ARCHIVE/closed_loop_agent_lab/ clean-clone integrity

### G-items for Mac

- **G-RV31-1 (blocking for CI on a clean clone):** `git add 99_ARCHIVE/closed_loop_agent_lab` to track the 374 logs (1.9 MB). Until that happens, the new bundle check fails on any fresh clone. It fails loudly, which is the intended behaviour.
- **G-RV31-2:** back up `standalone_package_retest_v5.1.log` (the only copy). G-RV31-1 does this through Git; a private backup is the alternative if you would rather not publish it.
- **G-RV31-3 (optional):** correct the README range. A note is in place; the body stays as you wrote it.

## [B31](BATCH31_FINDINGS_AND_LEDGER.md) — BATCH 31 — RV32 · Desktop and application reality (cascade-pc/, 27_SOL_AI_APP/)

### G-items for Mac

- **G-RV32-1:** run the app once (`npm ci && npm run dev`). Click both About links: they should open in your browser, never in an app window. Then `curl -H 'Host: x.example:7432' 127.0.0.1:7432/status` should return 403. That is the real witness for F1 and F2.
- **G-RV32-2:** should the local API **default off**? It starts at launch, and the Settings copy says so. The guard closes the browser attack, but any local process can still read everything. Default-off with a toggle is the conservative choice.
- **G-RV32-3:** move key storage to Electron `safeStorage` through IPC (F7), and add a CSP (F8). Both need a running app to witness.
- **G-RV32-4:** decide where the build workflow lives (F6): the separate `cascade-cicada-tool-` repo, or a root workflow here. Also decide whether to add `node --test cascade-pc/tests` to the root `ci.yml`. That second part is RV33 territory and is proposed, not applied.
- **G-RV32-5:** Electron major upgrade and lock `version` bump (F8): a dependency change that needs the build witness.

## [B32](BATCH32_FINDINGS_AND_LEDGER.md) — BATCH 32 — RV33 · Packaging, tests, CI and migration

### Decisions for Mac (G-items)

- **G-RV33-1 (blocking every hosted claim): unlock GitHub billing.** Until then, no workflow runs and every red X is DID NOT RUN. The first run after the unlock lands on the Ubuntu 26 runner image.
- **G-RV33-2: `ruff` and `mypy` are pinned only by floors** (`ruff>=0.6`, `mypy>=1.11`), and the floor config says "currently reports zero", which was false for five days. Options:
  - (a) pin exact dev-tool versions so a new rule release can't redden CI on its own;
  - (b) add a "frozen bundles" lint ignore keyed to the intake verifier's bundle list, so the next frozen bundle doesn't need a hand edit.

  Sol's stance: (a) now, and (b) when the next bundle lands.
- **G-RV33-3: Python 3.10 and 3.11 are unwitnessed.** The code uses `match` (3.10+), `Literal` and PEP 604 unions, so 3.10 is plausible but UNVERIFIED. It needs the hosted matrix (G-RV33-1) or a local interpreter.
- **G-RV33-4: replace the CASCADE F1 > 0.80 criterion** with one the oracle can reach, or retire the claim. Strict xfail keeps it honest meanwhile.
- **G-RV33-5: disk.** The root filesystem was at **100 %** (717 MB free of 108 GB) when a scratch copy filled it during this batch. After clearing this review's own stale scratch it is at 99 % (about 1.4 GB free). A full disk makes builds, tests and git fail in ways that look like broken code. The cause is outside the repository and outside this review's scope.

## [B33](BATCH33_FINDINGS_AND_LEDGER.md) — BATCH 33 — RV34 · Licensing, attribution and publication metadata

### Decision for Mac: the licence (G-RV34-1)

**What cannot change.** Everything already released under MIT stays MIT for anyone who took it: GitHub `v1.0.0`, both Zenodo versions, and every past commit. A new licence binds only future versions. That is DERIVED from how licences work generally; confirm it with a lawyer if it matters to a decision.

| Option | What it means | Cost |
|---|---|---|
| **A. Write the clause and adopt it** | Draft the "Earned Sovereignty Clause" text, add it to `LICENSE` and relabel everything "MIT + clause". | It is no longer MIT or OSI open source. The `License: MIT` field in `pyproject`, CITATION and Zenodo becomes false and needs changing. Many companies and universities cannot use custom-licensed code. Enforcing a bespoke clause needs a lawyer to write it. |
| **B. MIT only, and say so everywhere** | Apply the staged patch. Keep the attribution page as the author's requests. | The name "Earned Sovereignty Clause" disappears from the licence vocabulary. |
| **C. MIT plus a named covenant** | Option B, plus a short `EARNED_SOVEREIGNTY.md` stating the clause as a **covenant**: the author's ethical request (attribute, don't rebrand, carry the axioms forward), explicitly not a licence condition. | Mac would need to write or approve the covenant text. |

**Sol's stance: C.** The fight is about provenance, and a licence is the wrong weapon for it.
- **The licence is not the protection.** MIT already makes stripping the notice a breach. The timestamped Zenodo DOI and the git history settle who came first. Any protection of the *name* "Lycheetah" against rebranding would come from trademark, not from a copyright licence. That trademark point is DERIVED, not legal advice.
- **The cost of A is real.** A bespoke licence would cost the adoption that makes provenance worth defending.
- **C keeps what is Mac's.** The name lives on as the covenant, and the false legal claim goes.

### Other G-items

- **G-RV34-2, CITATION title and version.** Make `CITATION.cff` match the Zenodo record, or retitle the next Zenodo version to match CITATION. Consider citing the concept DOI 10.5281/zenodo.20020827 so "cite the latest" always resolves.
- **G-RV34-3, the GitHub release titled "M app".** It is marked Latest, sits on tag `tianxia-v0.2`, and Zenodo archived it under the framework's title. Rename it, or mark the C-1.1 release as Latest. This is an external mutation, so it is yours to do or to authorise.
- **G-RV34-4, "Lycheetah research collaborators".** Who holds the copyright on Forge_05–07? If it means AI seats, AI authorship of copyright is contested, and naming Mac as holder is the conservative line. If it means people, name them.
- **G-RV34-5, "Lycheetah Foundation".** Is it a registered body? If not, the BibTeX `institution` field should read "Independent researcher" (as CITATION.cff does), and the 78 mentions need a pass.
- **G-RV34-6, a version map.** Write one line each for package 1.3.0, canonical body C-1.1, tag `v1.0.0-c1.1` and Zenodo `tianxia-v0.2`, saying which is which. Otherwise a future release will mint a fifth scheme.
- **G-RV34-7, the arXiv strikes.** If an endorsement or a submission exists that this search missed (another name form, or another server), give the identifier and the strikes lift. BATCH28 G-KNOX-ENDORSEMENT is the same question.

## [B34](BATCH34_FINDINGS_AND_LEDGER.md) — BATCH 34 — RV35 · Security and privacy

### G-items for Mac

- **G-RV35-1 (most urgent, one click):** enable private vulnerability reporting. Use Settings → Code security → Private vulnerability reporting, or run `gh api -X PUT repos/Lycheetah/Lycheetah-Framework/private-vulnerability-reporting`. That revives route 1 at once. After that, the RV35 note in `SECURITY.md` can be shortened to point at the advisory link alone.
- **G-RV35-2:** choose **one working contact address** and decide where it goes. It would replace the address in `SECURITY.md`, `CODE_OF_CONDUCT.md` and `pyproject.toml`, and the `lycheetah.org` address in the 7 paper and pitch files. Either renew `lycheetah.nz` or pick an address you control. Sol does not pick an email for you.
- **G-RV35-3:** turn on Dependabot alerts and security updates. Optionally add `pip-audit` and `npm audit --omit=dev` jobs to CI, but CI is billing-locked (G-RV33-1).
- **G-RV35-4:** run a **history secret scan** once (`gitleaks detect` or `trufflehog git file://.`). The tree is clean, but the history has never been scanned in this review.
- **G-RV35-5:** the private repository's name in 7 public files (F6). Options:
  - (a) leave it, since it is already public and harmless alone;
  - (b) replace it with "the private app repository" going forward, and change `reflexive_audit.py`'s default to require the env var.

  Sol's stance: **(b) for the code default, (a) for the prose.** Rewriting history notes to hide a name that is already in history buys nothing.
- **G-RV35-6:** the personal gmail addresses in public papers (F7). Keep them, or move to the contact address from G-RV35-2.
- **G-RV35-7:** `15_PERSONAL_VAULT/`: public archive or private? Its README and its private marker disagree (F9). Whichever you choose, one of the two files should change to match.
- **G-RV35-8:** before any commit of `FOR-REVIEW/`, scrub the home-path lines (F8). There is also a proposal for root `AGENTS.md:3`: replace the absolute path with `~/`-relative wording. That is a proposal only, under the RV27 boundary.

## [B35](BATCH35_FINDINGS_AND_LEDGER.md) — BATCH 35 — RV36 · Audit the auditors and their receipts

### G-items for Mac

- **G-RV36-1:** apply `RV36_DEFENSE_INDEX_PRESENCE.patch`, or write the two promised documents (D-X AI reader test log, D-XI defense audit). **Sol: apply the patch.** An index that names absent documents is exactly what an outside reader catches first.
- **G-RV36-2:** add `"pattern": "^[A-Z]+-[0-9]{3}$"` to `claim_id` in `CLAIMS.schema.json`. All 71 ids already comply. It is a canonical schema, so this needs your word.
- **G-RV36-3:** the 999 count in `verification.json` (F4). Either leave the receipt as issued with the README note (done), or have a future run re-mint it at a named commit. **Sol: leave it, with the note.** Re-minting a historical receipt rewrites history.
- **G-RV36-4 (standing rule for future reviews):** every committed receipt should come with its producer script, or say plainly that it has none. 11 of 13 here cannot be regenerated. It was luck, not design, that they recomputed correctly.
- **G-RV36-5:** independent validation. The whole 28_DEFENSE / review apparatus is self-review plus AI review. The only thing that changes that status is a human outside reviewer or a submitted paper. That is your call and your network; no gate here can stand in for it.

## [B36](BATCH36_FINDINGS_AND_LEDGER.md) — BATCH 36 — RV37 · Four reproduced leads (Outbox, ResearchPipeline, TitleReceipt, Hexie)

### G-items for Mac

- **G-RV37-1 (the security one):** apply `RV37_OUTBOX_PAYLOAD_BINDING.patch`, then regenerate the v0.9 report and both checksum files, and record that the freeze was reopened for a security fix. **Sol: apply it.** A finality gate that authorises one action and executes another is the failure the paper exists to prevent. Then extend the same binding to v1.0 (L1b), which needs its own probe first. Anywhere the paper or its README claims "no unauthorised effect", that claim should carry a dated note until the fix lands.
- **G-RV37-2:** apply `RV37_TITLE_RECEIPT_SCHEMA.patch`. One sub-question is yours alone: must `bearer_choice` be true for EARNED? Sol says yes. A title the bearer did not choose to carry is a label, not a receipt. If you say no, delete that one `const`.
- **G-RV37-3:** the Hexie aggregate. Option (a): keep the linear average and live without the binding-constraint claim. That is what the struck spec now says. Option (b): move to a geometric mean or a min, which makes "improve the weakest first" true by construction. **Sol: (b), geometric.** It keeps every component visible, and the claim was the reason for the composite.
- **G-RV37-4:** redesign Π consistency (L2b). Replace the range-based score with one that rewards agreement in sign and direction, so a stronger replication cannot demote a practice. Until then, the RV37 structural cap is a guard, not a cure.
- **G-RV37-5:** fix the example-data labels (L2c), and either generate `QUICK_REFERENCE.md`'s thresholds from the code or point them at it (L2d). Both are mechanical once you say go.

## [B37](BATCH37_FINDINGS_AND_LEDGER.md) — BATCH 37 — RV01 · Whole architecture and the "third brain"

### G-items for Mac

- **G-RV01-1:** what is the "third brain"? (a) The whole Framework repository. (b) The sovereign harness: decide + remember + agree. (c) Something else you have in mind. The review left this open instead of guessing. **Sol leans to (b) as the code reading,** but your word decides it.
- **G-RV01-2:** consolidate import identity. Replace the five core modules' `sys.path.insert` + bare-name imports with `core.*` imports. Then make the bridges stop appending to `__path__`, or turn them into pure re-export shims. That ends A3 and A4. It touches canonical implementation files, so Sol proposes one batch with the full suite, not piecemeal edits.
- **G-RV01-3:** probe the shipped `lycheetah.assurance.finality` for the RV37 payload-binding pattern. A shipped package outranks a research line.
- **G-RV01-4:** mark mirrors. Add one line to each `upstream_mirror/` and duplicated runtime folder: "byte copy of <path> at <commit>; not authoritative".
- **G-RV01-5:** record promotion. Add a line to `lycheetah/assurance/action_guard.py`, or the 34 README, naming which research version it was promoted from.

## [B38](BATCH38_FINDINGS_AND_LEDGER.md) — BATCH 38 — Mathematical checklist M1–M18

### G-items for Mac

- **G-M-1 — claim statuses.** MIC-003, ELI-003, CAS-003 (counterexample or mismatch) and LYV-001 (unsupported) are still ACTIVE. The ruling stays with you, through the existing G-RV19 overlay. Options: (a) keep ACTIVE with the overlay as the visible dissent; (b) move them to SCAFFOLD and restate ELI-003 as N3; (c) RETRACTED for MIC-003 only. Sol leans to (b), because each claim has a true narrower successor except MIC-003, whose successor needs the compliant-intention premise put back in.
- **G-M-2 — Harmonia metric.** Implement the prime-factor specification, recalibrate the tests, and lift the strict xfail. This one is yours because it changes the numbers every Harmonia output reports.
- **G-M-3 — "11/11" mirrors.** `papers/LYCHEETAH_SYNTHESIS_v0.1` and the other mirrors still say 11/11. Point them at the R3 tally, or at the RV19 note. Some "11/11" hits are unrelated (frontier controls), so the sweep needs reading, not a global replace.
- **G-M-4 — promoting N1–N3 into the theorem text.** The addenda sit beside the original statements as review notes. Do you want them written into the theorems as the corrected statements?

