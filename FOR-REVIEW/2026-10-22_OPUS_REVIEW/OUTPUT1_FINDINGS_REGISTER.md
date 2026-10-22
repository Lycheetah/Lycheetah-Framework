# Output 1 — Consolidated findings register

**Reviewer:** Sol (Claude Opus 5.5) · **Date:** 2026-10-23 · **Generated** from the 38 batch ledgers by a script; every row links to the ledger that holds its file and line, reproduction, consequence and fix. Nothing here is new evidence: this file is an index, and the ledger outranks it.

**How to read the state column.** It is derived mechanically from each row's own status and severity cells: *fixed in tree* (the ledger says the repair landed), *patch proposed* (a patch is staged for Mac), *checked, holds* (the reviewed claim survived), *retracted*, and *open* (everything else, including MEASURED defects awaiting a decision). Where a ledger used a free-form table, the state reads *open* even if the prose says otherwise, so this column under-counts repairs; it never over-counts them.

**Totals (MEASURED from the ledgers):** 519 finding rows across 38 batches · open 295 · fixed in tree 170 · checked, holds 26 · patch proposed 21 · retracted 7

Ledgers used three shapes: tables (`ID / Severity / Status / Where`, `# / Status / Finding`), headed sections (`### F1 — …`), and numbered sections. All three are indexed; a row whose ID starts with § is a numbered section of a ledger that wrote its findings as chapters. IDs are batch-local, so cite a finding as **B<n>-<id>** (for example B37-A2).

## [B1](BATCH1_FINDINGS_AND_LEDGER.md) — Opus review — Batch 1: findings register and coverage ledger

| ID | Severity | Status | State | Finding |
|---|---|---|---|---|
| B1-F01 | High | FIXED in working tree | fixed in tree | RV14 |
| B1-F02 | Medium | OPEN, Mac's grammar decision | open | RV14 |
| B1-F03 | Medium | OPEN, provenance | open | RV14 |
| B1-F04 | Low | OPEN | open | RV14 |
| B1-F05 | High | FIXED in working tree | fixed in tree | RV10 |
| B1-F06 | High | REPRODUCED, patch STAGED (frozen source) | patch proposed | RV11 |
| B1-F07 | High | REPRODUCED, patch STAGED (frozen source) | patch proposed | RV12 |
| B1-F08 | Low | FIXED in working tree | fixed in tree | suite |
| B1-F09 | Low | FIXED in working tree (Batch 2) | fixed in tree | suite |
| B1-F10 | Process | OPEN, Mac's decision | open | repo |
| B1-F01 |  | Text after | was silently accepted … | fixed in tree | Text after | was silently accepted (MEASURED, FIXED) |
| B1-F02 |  | ↯ has two incompatible definitions … | open | ↯ has two incompatible definitions (DERIVED, OPEN) |
| B1-F03 |  | Proposal 01's approval and test … | patch proposed | Proposal 01's approval and test receipt are not verifiable here (MEASURED) |
| B1-F04 |  | LEAF_TYPES lists TokenType.FIELD twice … | open | LEAF_TYPES lists TokenType.FIELD twice and appears unused (DERIVED) |
| B1-F05 |  | Chorus runner fabricated health and … | fixed in tree | Chorus runner fabricated health and audit results (MEASURED, FIXED) |
| B1-F06 |  | Policy-evolution gate classifies a … | open | Policy-evolution gate classifies a weakening as EQUIVALENT (MEASURED) |
| B1-F07 |  | Blind-review aggregator double-counts … | open | Blind-review aggregator double-counts and mixes inputs (MEASURED) |
| B1-F08 |  | Chorus README test failed on the … | fixed in tree | Chorus README test failed on the baseline (MEASURED, FIXED) |
| B1-F09 |  | Two other baseline failures, not … | open | Two other baseline failures, not investigated (MEASURED red) |
| B1-F10 |  | Review branch is not master (MEASURED) | open | Review branch is not master (MEASURED) |

## [B2](BATCH2_FINDINGS_AND_LEDGER.md) — Opus review — Batch 2: findings register and coverage ledger

| ID | Severity | Status | State | Finding |
|---|---|---|---|---|
| B2-F11 | Medium | FIXED in working tree | fixed in tree | RV02 |
| B2-F12 | Low | FIXED in working tree | fixed in tree | RV02 |
| B2-F13 | Medium | PARTIAL: witness fixed, permit by … | fixed in tree | RV02 |
| B2-F14 | High | FIXED in working tree | fixed in tree | RV03 |
| B2-F15 | High | FIXED in working tree | fixed in tree | RV03 |
| B2-F16 | Medium | FIXED in working tree | fixed in tree | RV03 |
| B2-F17 | High | FIXED in working tree | fixed in tree | RV03 |
| B2-F18 | Medium | FIXED in working tree | fixed in tree | RV03 |
| B2-F19 | Medium | FIXED in working tree | fixed in tree | RV03 |
| B2-F20 | Medium | FIXED in working tree | fixed in tree | RV03 |
| B2-F21 | Medium | FIXED in working tree | fixed in tree | RV03 |
| B2-F22 | High | FIXED at the Grey Mode boundary; … | fixed in tree | RV03 |
| B2-F23 | Medium | OPEN, design decision for Mac | open | RV03 |
| B2-F24 | Medium | OPEN, design decision for Mac | open | RV03 |
| B2-G2 | Low | FIXED in working tree | fixed in tree | RV03 |
| B2-G3 | Low | FIXED in working tree | fixed in tree | RV03 |
| B2-G6 | Low | OPEN, note | open | RV03 |
| B2-F11 |  | Two permits for one action in one … | fixed in tree | Two permits for one action in one second collided (MEASURED, FIXED) |
| B2-F12 |  | String scope lists were split into … | fixed in tree | String scope lists were split into characters (MEASURED, FIXED) |
| B2-F13 |  | The permit binds the critical hash … | open | The permit binds the critical hash only (MEASURED, PARTIAL) |
| B2-F14 |  | The anchor's antipode passed every … | fixed in tree | The anchor's antipode passed every consensus flag (MEASURED, FIXED) |
| B2-F15 |  | Agreement far from the anchor … | fixed in tree | Agreement far from the anchor converged (MEASURED, FIXED) |
| B2-F16 |  | Cancelling states got the anchor as … | fixed in tree | Cancelling states got the anchor as their consensus (MEASURED, FIXED) |
| B2-F17 |  | Re-registering an agent cleared its … | fixed in tree | Re-registering an agent cleared its quarantine (MEASURED, FIXED) |
| B2-F18 |  | Unknown neighbors were dropped … | fixed in tree | Unknown neighbors were dropped silently (MEASURED, FIXED) |
| B2-F19 |  | NaN and unusable parameters disabled … | fixed in tree | NaN and unusable parameters disabled quarantine (MEASURED, FIXED) |
| B2-F20 |  | Recovery rewrote an agent without a … | fixed in tree | Recovery rewrote an agent without a trace (MEASURED, FIXED) |
| B2-F21 |  | MCP network health could never … | fixed in tree | MCP network health could never quarantine (MEASURED, FIXED) |
| B2-F22 |  | TRIAD recovery readmitted an agent it … | fixed in tree | TRIAD recovery readmitted an agent it carried to the antipode (MEASURED, FIXED at the boundary) |
| B2-F23 |  | The default re-entry threshold sits … | open | The default re-entry threshold sits above every unsigned drift (MEASURED, OPEN) |
| B2-F24 |  | One agent is a quorum (MEASURED, OPEN) | open | One agent is a quorum (MEASURED, OPEN) |
| B2-G2 |  | (fixed): recovery_cycle restored the … | fixed in tree | (fixed): recovery_cycle restored the kernel's coherence only on the |
| B2-G3 |  | (fixed): run(max_cycles=0) raised … | fixed in tree | (fixed): run(max_cycles=0) raised UnboundLocalError on r_c_new. |
| B2-G6 |  | (open note): the docstring says alerts … | open | (open note): the docstring says alerts must be "consecutive", but a |

## [B3](BATCH3_FINDINGS_AND_LEDGER.md) — Opus review — Batch 3: findings register and coverage ledger

| ID | Severity | Status | State | Finding |
|---|---|---|---|---|
| B3-B01 | — | RETRACTED: falsified at the guard | retracted | RETRACTED: falsified at the guard |
| B3-B01b | High (availability; fails … | FIXED in working tree | fixed in tree | action_guard.py record_result, _audit |
| B3-B02 | Medium | FIXED in working tree | fixed in tree | action_guard.py, every mutator |
| B3-B02b | Medium | FIXED in working tree | fixed in tree | action_guard.py identifiers |
| B3-B03 | Medium | FIXED in working tree | fixed in tree | action_guard.py issue_approval |
| B3-B04 | Low | FIXED in working tree | fixed in tree | action_guard.py claim_dispatch |
| B3-B05 | — | NOTE: by design, boundary is the … | open | NOTE: by design, boundary is the workflow |
| B3-B05b | Medium (deployment truth) | DOCUMENTED; the default → Mac (P10) | open | gateway.py open_local, README.md |
| B3-B06 | Medium | FIXED in working tree (through B03) | fixed in tree | FIXED in working tree (through B03) |
| B3-B07 | Low | FIXED in working tree | fixed in tree | gateway.py _declared_approver |
| B3-B08 | High (design) | OPEN, design decision for Mac (P8) | open | gateway.py evaluate_policy, _tool_event |
| B3-B09 | — | FALSIFIED: the gateway is correct | open | FALSIFIED: the gateway is correct |
| B3-B10 | Medium ([SCAFFOLD] module) | FIXED in working tree | fixed in tree | Medium ([SCAFFOLD] module) |
| B3-B11–B14 | — | HELD: no defect | checked, holds | expiry, substitution, reuse, revocation |
| B3-B01 |  | NaN in a result did not brick guard … | retracted | NaN in a result did not brick guard replay (RETRACTED, MEASURED) |
| B3-B01b |  | One NaN from a provider blocked every … | fixed in tree | One NaN from a provider blocked every later gateway action (MEASURED, FIXED) |
| B3-B02 |  | A float timestamp bricked the ledger … | fixed in tree | A float timestamp bricked the ledger (MEASURED, FIXED) |
| B3-B02b |  | A non-string identity broke the hash … | fixed in tree | A non-string identity broke the hash chain (MEASURED, FIXED) |
| B3-B04 |  | An unencodable live action raised … | fixed in tree | An unencodable live action raised instead of refusing (MEASURED, FIXED) |
| B3-B05 |  | The raw guard is only as fresh as the … | open | The raw guard is only as fresh as the anchor it is handed (MEASURED, NOTE) |
| B3-B05b |  | open_local puts the authority beside … | open | open_local puts the authority beside the ledger (MEASURED, DOCUMENTED) |
| B3-B07 |  | An empty approver was approved at … | fixed in tree | An empty approver was approved at propose and denied at dispatch (MEASURED, FIXED) |
| B3-B08 |  | The side-effect boundary is declared … | open | The side-effect boundary is declared by the actor (MEASURED, OPEN → Mac) |
| B3-B09 |  | An unencodable provider result is … | open | An unencodable provider result is handled correctly (FALSIFIED, MEASURED) |
| B3-B10 |  | Finality accepted a PASS about a … | fixed in tree | Finality accepted a PASS about a different subject (MEASURED, FIXED) |
| B3-B11 |  | B14 — What held (MEASURED on HEAD and … | open | B14 — What held (MEASURED on HEAD and on the tree) |

## [B4](BATCH4_FINDINGS_AND_LEDGER.md) — Opus review — Batch 4: findings register and coverage ledger

| ID | Severity | Status | State | Finding |
|---|---|---|---|---|
| B4-R01 | High (duplicate side effect) | FIXED in working tree | fixed in tree | action_guard.py prepare_effect |
| B4-R02 | High (no recovery path) | FIXED in working tree | fixed in tree | checkpointed_workflow.py, gateway.py, cli.py |
| B4-R03 | High (availability; fails … | OPEN, design decision for Mac (P11) | fixed in tree | checkpointed_workflow.py _trusted_checkpoint |
| B4-R04 | Medium (availability; fails … | FIXED in working tree | fixed in tree | action_guard.py, checkpointed_workflow.py |
| B4-R05 | — | HELD: no defect | checked, holds | gateway.py dispatch, explicit {} live action |
| B4-R06 | — | HELD: no defect | checked, holds | gateway.py dispatch, second dispatch |
| B4-R07 | High (same root as R01) | Redispatch HELD; same-action retry … | fixed in tree | Redispatch HELD; same-action retry FIXED with R01 |
| B4-R01 |  | Retrying an action whose outcome is … | fixed in tree | Retrying an action whose outcome is unknown called the provider again (MEASURED, FIXED) |
| B4-R02 |  | There was no checkpointed way to … | fixed in tree | There was no checkpointed way to reconcile (MEASURED, FIXED) |
| B4-R03 |  | One failed publish after a local … | open | One failed publish after a local commit blocks the ledger forever (MEASURED, OPEN → P11) |
| B4-R04 |  | Two gateways on one ledger bricked it … | fixed in tree | Two gateways on one ledger bricked it (MEASURED, FIXED) |

## [B5](BATCH5_FINDINGS_AND_LEDGER.md) — Opus review — Batch 5: findings register and coverage ledger

| ID | Severity | Status | State | Finding |
|---|---|---|---|---|
| B5-S01 | High (local suite never … | FIXED in working tree | fixed in tree | High (local suite never finishes; window on the desktop) |
| B5-P06 | High (duplicate side effect) | FIXED in working tree | fixed in tree | gateway.py executor outcome |
| B5-P04 | Medium (verifier overclaims) | FIXED in working tree | fixed in tree | Medium (verifier overclaims) |
| B5-P05 | Medium (receipt drops caveats) | FIXED in working tree | fixed in tree | gateway.py receipt limitations |
| B5-P03 | Medium (silent policy … | FIXED in working tree | fixed in tree | Medium (silent policy corruption) |
| B5-P08 | Medium (defence in depth … | FIXED in working tree | fixed in tree | Medium (defence in depth bypassed by spelling) |
| B5-P10 | Medium (verifier raises … | FIXED in working tree | fixed in tree | Medium (verifier raises instead of judging) |
| B5-P09 | Medium (secrets at rest) | DOCUMENTED, not changed; design … | open | DOCUMENTED, not changed; design decision for Mac |
| B5-P07 | Low (misleading reason) | OPEN, observation | open | gateway.py result checkpoint |
| B5-P01 | — | HELD: no defect | checked, holds | policy digest coverage |
| B5-P02 | — | HELD: no defect | checked, holds | list fields given as a bare string |
| B5-S01 |  | The full suite opened a matplotlib … | fixed in tree | The full suite opened a matplotlib window on the desktop and waited for a person to close it (MEASURED, FIXED) |
| B5-P06 |  | An executor answer that was neither … | fixed in tree | An executor answer that was neither success nor failure was recorded as FAILED, so a retry called the provider again (MEASURED, FIXED) |
| B5-P04 |  | verify() accepted receipts that the … | fixed in tree | verify() accepted receipts that the published schema rejects (MEASURED, FIXED) |
| B5-P05 |  | The gateway receipt dropped the … | fixed in tree | The gateway receipt dropped the runtime's caveats (MEASURED, FIXED) |
| B5-P03 |  | TextRule.from_dict turned a missing … | fixed in tree | TextRule.from_dict turned a missing field into the text "None" (MEASURED, FIXED) |
| B5-P08 |  | The destructive-command tripwire … | fixed in tree | The destructive-command tripwire matched one spelling (MEASURED, FIXED) |
| B5-P10 |  | verify() raised on a non-ASCII digest … | fixed in tree | verify() raised on a non-ASCII digest (MEASURED, FIXED) |
| B5-P09 |  | Sensitive arguments and provider … | open | Sensitive arguments and provider answers are stored raw at rest (MEASURED, DOCUMENTED) |
| B5-P07 |  | An unserialisable provider result is … | open | An unserialisable provider result is held for reconcile under the wrong reason (MEASURED, OPEN, Low) |

## [B6](BATCH6_FINDINGS_AND_LEDGER.md) — Opus review — Batch 6: findings register and coverage ledger

| ID | Severity | Status | State | Finding |
|---|---|---|---|---|
| B6-R2 | Medium (two paths disagree; … | FIXED in working tree | fixed in tree | Medium (two paths disagree; an inherited violation passes as safe) |
| B6-R1 | Medium (false refusal; a … | FIXED in working tree | fixed in tree | Medium (false refusal; a real protection loss read only as DIVERGENT) |
| B6-R5 | Medium (boundary: risk and … | DOCUMENTED, kept; Proposal 14 for Mac | patch proposed | Medium (boundary: risk and evidence are outside the hash) |
| B6-T1 | Medium (published overclaim) | RETRACTED in CHANGELOG.md; docstring … | retracted | RETRACTED in CHANGELOG.md; docstring fixed in place |
| B6-R3 | Low (a PARTIAL never said … | FIXED in working tree | fixed in tree | classify changed_fields, shield forwarding |
| B6-R4 | Low (malformed digest read … | FIXED in working tree | fixed in tree | Low (malformed digest read as a mismatch; a digest match was silent about what it cannot see) |
| B6-R6 | Low | DOCUMENTED | open | order-sensitive comparison |
| B6-R7 | Low (one truth) | OPEN; Proposal 15 for Mac | patch proposed | OPEN; Proposal 15 for Mac |
| B6-R8 | — | DERIVED observation, no change | open | DERIVED observation, no change |
| B6-X1, X2, C1–C8 | — | HELD: no defect | checked, holds | export independence, dropped and altered critical context |
| B6-R2 |  | The packet path and the digest path … | fixed in tree | The packet path and the digest path disagreed on a packet that already broke a rule (MEASURED, FIXED) |
| B6-R1 |  | Unknown protection was judged over the … | fixed in tree | Unknown protection was judged over the list, not per unknown (MEASURED, FIXED) |
| B6-R5 |  | Risk, evidence, horizon, yield, id and … | open | Risk, evidence, horizon, yield, id and operations are outside the critical projection (MEASURED, DOCUMENTED) |
| B6-T1 |  | Published prose claimed a guarantee … | retracted | Published prose claimed a guarantee and a proof (MEASURED, RETRACTED) |
| B6-R6 |  | Reordering a critical list is … | open | Reordering a critical list is DIVERGENT (MEASURED, DOCUMENTED) |
| B6-R7 |  | export_packet restates two codec rules … | open | export_packet restates two codec rules in its own words (MEASURED, OPEN) |
| B6-R8 |  | The handoff verifier's compaction … | open | The handoff verifier's compaction check overlaps the task digest (DERIVED) |

## [B7](BATCH7_FINDINGS_AND_LEDGER.md) — Opus review — Batch 7: findings register and coverage ledger

| ID | Severity | Status | State | Finding |
|---|---|---|---|---|
| B7-K1 | High (consent changed … | HELD in the maintained codec (repair … | fixed in tree | HELD in the maintained codec (repair predates this review); frozen counterexample PRESERVED and reproduced |
| B7-W2 | Medium (one wire, two … | FIXED in working tree | fixed in tree | Medium (one wire, two readings: the raw text shows one claim, the decoder returns another) |
| B7-W1, W3–W7 | Medium (malleable wire: many … | FIXED in working tree | fixed in tree | Medium (malleable wire: many wires per packet; an extra array item dropped without notice) |
| B7-U1 | Medium (crash instead of a … | FIXED in working tree | fixed in tree | Medium (crash instead of a codec error; a wire that cannot be written as UTF-8) |
| B7-T2 | Medium (published overclaim; … | STAGED patch, not applied; Proposal 16 … | fixed in tree | Medium (published overclaim; the installable package ships the unrepaired codec) |
| B7-A1 | Medium (archive integrity: … | MEASURED, DOCUMENTED; decision for Mac | open | Medium (archive integrity: the sealed folder no longer matches its seal) |
| B7-N1 | Low (boundary) | MEASURED, DOCUMENTED | open | no Unicode normalisation |
| B7-L1 | — | Lead for the packaging pass | open | lycheetah/__init__.py import graph |
| B7-K2, K3 | — | HELD: no defect | checked, holds | consent sweep, corpus round trip |
| B7-W1 |  | W7 — The decoder accepted wires encode … | fixed in tree | W7 — The decoder accepted wires encode never emits (MEASURED, FIXED) |
| B7-U1 |  | A lone surrogate passed validation, … | fixed in tree | A lone surrogate passed validation, then crashed hashing (MEASURED, FIXED) |
| B7-K1 |  | K3 — Consent preservation (MEASURED) | open | K3 — Consent preservation (MEASURED) |
| B7-T2 |  | Post-seal surfaces claim a proof, and … | fixed in tree | Post-seal surfaces claim a proof, and the package installs the unrepaired codec (MEASURED, STAGED) |
| B7-A1 |  | The sealed folder no longer matches … | open | The sealed folder no longer matches its seal (MEASURED) |
| B7-N1 |  | Text is preserved code point for code … | open | Text is preserved code point for code point (MEASURED, DOCUMENTED) |
| B7-L1 |  | Importing the stdlib-only codec … | open | Importing the stdlib-only codec imports the whole package (lead) |

## [B8](BATCH8_FINDINGS_AND_LEDGER.md) — Opus review — Batch 8: findings register and coverage ledger

| ID | Severity | Status | State | Finding |
|---|---|---|---|---|
| B8-G1 | Medium (the verifier vouched … | FIXED in working tree | fixed in tree | Medium (the verifier vouched for report claims it never compared: production mode, no limits, LOW risk against a HIGH permit, an added approval field) |
| B8-G2 | Medium (control records not … | FIXED in working tree | fixed in tree | Medium (control records not bound to the run: another permit, another action, a phantom consensus agent) |
| B8-G3 | Medium (the completion could … | FIXED in working tree | fixed in tree | Medium (the completion could claim attestation it never had) |
| B8-G4 | Low (RecursionError escaped … | FIXED in working tree | fixed in tree | Low (RecursionError escaped verify_bundle) |
| B8-G5 | Low (1e400 read as infinity … | FIXED in working tree | fixed in tree | Low (1e400 read as infinity past the nonfinite guard) |
| B8-G6 | Low (type checked by name, … | FIXED in working tree | fixed in tree | Low (type checked by name, then the file read by name again) |
| B8-G7 | Medium (a non-canonical … | FIXED by Batch 7's strict decode; … | fixed in tree | FIXED by Batch 7's strict decode; reconfirmed here |
| B8-D1 | Medium (published claim … | CORRECTED | fixed in tree | Medium (published claim false at HEAD) |
| B8-D2 | — | DOCUMENTED; dated record, not rewritten | open | 28_DEFENSE/FULL_FRAMEWORK_REVIEW_2026-10-20.md:434-440 |
| B8-B1 | Boundary | UNCHANGED, now stated | open | complete rewrite, no signature, shared library |
| B8-H1 | — | HELD: no defect | checked, holds | refusals listed below |
| B8-G1 |  | The run report's own claims were never … | fixed in tree | The run report's own claims were never compared (MEASURED, FIXED) |
| B8-G2 |  | Control records were not bound to the … | fixed in tree | Control records were not bound to the run (MEASURED, FIXED) |
| B8-G3 |  | The completion could claim attestation … | fixed in tree | The completion could claim attestation it never had (MEASURED, FIXED) |
| B8-G4 |  | Deep nesting escaped as RecursionError … | fixed in tree | Deep nesting escaped as RecursionError (MEASURED, FIXED) |
| B8-G5 |  | An overflowing number became infinity … | fixed in tree | An overflowing number became infinity (MEASURED, FIXED) |
| B8-G6 |  | Type checked by name, then read by … | fixed in tree | Type checked by name, then read by name (FIXED; race simulated, not timed) |
| B8-G7 |  | Non-canonical context (MEASURED; fixed … | fixed in tree | Non-canonical context (MEASURED; fixed by Batch 7) |
| B8-B1 |  | What a SELF_CONSISTENT bundle still … | open | What a SELF_CONSISTENT bundle still cannot show (unchanged, DERIVED) |
| B8-H1 |  | Held | open | Held |

## [B9](BATCH9_FINDINGS_AND_LEDGER.md) — Opus review — Batch 9: findings register and coverage ledger

| ID | Severity | Status | State | Finding |
|---|---|---|---|---|
| B9-K1 | Medium (a constitutional … | FIXED in working tree | fixed in tree | Medium (a constitutional verdict returned as a constant) |
| B9-K2 | Medium (a missing flag read … | FIXED in working tree | fixed in tree | check_hard_guardrails, check_seven_invariants, apply_pcf |
| B9-K3 | Medium (15 methods returned … | FIXED in working tree | fixed in tree | Medium (15 methods returned 24 fixed True fields; an empty structure validated) |
| B9-K4 | Medium (consent outranked a … | FIXED in working tree | fixed in tree | Medium (consent outranked a declared override; declaring nothing passed) |
| B9-K5 | Low (semitone and tritone … | FIXED in working tree | fixed in tree | Low (semitone and tritone rated harmonic) |
| B9-K6 | Low (Π infinite for S ≤ 0) | FIXED in working tree | fixed in tree | CascadeArchitect.measure_truth_pressure |
| B9-K7 | Medium (a fabricated … | FIXED in working tree | fixed in tree | Medium (a fabricated CRITICAL finding attributed to a real file, for any input) |
| B9-K8 | Medium (data loss: a corrupt … | FIXED in working tree | fixed in tree | Medium (data loss: a corrupt log read as empty, then overwritten) |
| B9-K9 | Low (the menu and 8 scripts … | FIXED in working tree | fixed in tree | Low (the menu and 8 scripts announced health nobody probed) |
| B9-D1 | Medium (published status … | CORRECTED, March text kept and marked | fixed in tree | Medium (published status false at HEAD) |
| B9-D2 | Medium (chorus described as … | CORRECTED | fixed in tree | THE_AI_ARCHITECTS_DOOR.md:272,286,288,319, THE_FOUR_PRINCIPLES.md:425, LAWS_COMPLETE.md:539 |
| B9-D3 | — | LEFT: unchecked roadmap item and archive | open | LEFT: unchecked roadmap item and archive |
| B9-L1 | Low | OPEN, not fixed | fixed in tree | aurora_investigator.py:126,142: line_number=0 placeholders in detect_false_claims, whose line-134 pattern also lists proves twice |
| B9-L2 | Low | OPEN, not fixed | fixed in tree | aurora_investigator.py:210: pressure_applied: "MAXIMUM" is a constant |
| B9-B1 | Boundary | UNCHANGED, now stated everywhere | open | no agent passes messages, reads or writes the coherence buffer, or inspects content; PCF reads flags an output declares about itself |

## [B10](BATCH10_FINDINGS_AND_LEDGER.md) — Opus review — Batch 10: findings register and coverage ledger

| ID | Severity | Status | State | Finding |
|---|---|---|---|---|
| B10-P1 | High (the gate's central … | REPRODUCED end to end; patch STAGED | patch proposed | group_map, install_initial, propose, semantic_relation_structural |
| B10-P2 | Medium | REPRODUCED by a forced interleave; … | patch proposed | activate_candidate: checks run outside the write transaction |
| B10-P3 | Medium | REPRODUCED; patch STAGED | patch proposed | activate_candidate: incident trace reads labels, not controls |
| B10-P4 | Low–Medium | REPRODUCED; patch STAGED | patch proposed | activate_candidate: no version or state check |
| B10-P5 | Low | REPRODUCED; patch STAGED | patch proposed | add_fixture: truth values not type-checked |
| B10-P6 | Low (a code claim) | MEASURED; docstring corrected in the … | fixed in tree | MEASURED; docstring corrected in the staged patch |
| B10-P7 | Note (fails closed) | RECORDED, not patched | fixed in tree | map_incident, the incident query, COVERED marking, connections |
| B10-P8 | Informational | RECORDED | open | SOURCE_SHA256SUMS.json vs SHA256SUMS.json |
| B10-P1 |  | a repeated group ID lets a weakening … | open | a repeated group ID lets a weakening activate as EQUIVALENT |
| B10-P2 |  | two activations can interleave; the … | open | two activations can interleave; the second is never checked |
| B10-P3 |  | the incident trace accepts a relabel … | open | the incident trace accepts a relabel with no new control |
| B10-P4 |  | an older or retired version can … | open | an older or retired version can replace a newer active one |
| B10-R5 |  | v2 and v3 are both proposed against … | patch proposed | v2 and v3 are both proposed against v1. v3 activates. v2 is stronger |
| B10-R5b |  | a RETIRED v1 that is equivalent to the … | open | a RETIRED v1 that is equivalent to the active v2 is re-activated, so |
| B10-P5 |  | fixture truth is not type-checked | fixed in tree | fixture truth is not type-checked |
| B10-P6 |  | the classifier is sound with unique … | open | the classifier is sound with unique IDs, not exact |
| B10-P7 |  | recorded, fails closed | fixed in tree | recorded, fails closed |
| B10-P8 |  | two hash manifests (informational) | open | two hash manifests (informational) |

## [B11](BATCH11_FINDINGS_AND_LEDGER.md) — Batch 11 — RV12: blind-review aggregator admission

| ID | Severity | Status | State | Finding |
|---|---|---|---|---|
| B11-F1 | HIGH | A renamed blind pack counts as a … | open | A renamed blind pack counts as a second reviewer (R7) — HIGH, normal path |
| B11-F2 | HIGH | Duplicate reviews inflate the counts … | open | Duplicate reviews inflate the counts and move the median (R1, R1b, R1c) — HIGH, normal path |
| B11-F3 | HIGH | Blank reviewer IDs merge different … | open | Blank reviewer IDs merge different people (R2, R2b, R2c) — HIGH, normal path |
| B11-F4 | HIGH | Bad key binding misattributes scores … | open | Bad key binding misattributes scores (R5, R5b–R5e) — HIGH impact, off the normal path |
| B11-F5 | MEDIUM | Mixed or missing case and experiment … | open | Mixed or missing case and experiment IDs (R3, R3b, R3c) — MEDIUM |
| B11-F6 | MEDIUM | Candidate identity (R4, R4b, R4c) — … | open | Candidate identity (R4, R4b, R4c) — MEDIUM |
| B11-F7 | MEDIUM | "Not assessable" and "missing" look … | open | "Not assessable" and "missing" look the same (R6) — MEDIUM |
| B11-F8 | LOW | Reviewer disagreement is not computed … | patch proposed | Reviewer disagreement is not computed — LOW, not patched (SCAFFOLD) |

## [B12](BATCH12_FINDINGS_AND_LEDGER.md) — RV13 · Batch 12: Findings and Ledger

| ID | Severity | Status | State | Finding |
|---|---|---|---|---|
| B12-W1/W2 |  | MEASURED | open | A NaN intervention or restoration produced gamma = 1.0, i.e. perfectly grain-aligned |
| B12-W3 |  | MEASURED | open | A *forcing* step with a NaN restoration was recorded as gamma 1.0, coherent: true, debt delta 0.110. With a finite R the same step is gamma −1.0, incoherent, delta 0.815 |
| B12-W3b |  | MEASURED | open | That step was written to the ledger (history 1, debts mutated) |
| B12-W4 |  | MEASURED | open | An infinite intervention recorded Infinity in both debt totals |
| B12-W5 |  | MEASURED | open | The constructor accepted mu=nan, mu=inf, k_cost=nan, theta=nan, theta=5 |
| B12-W6 |  | MEASURED | open | The bounded modulator returned a complex cost (2-0.354j) for gamma=-2, p=2.5, and NaN for NaN inputs |
| B12-W7 |  | MEASURED | open | The exp modulator returned NaN for NaN inputs, and a raw OverflowError leaked at gamma=-1, mu=1000 |
| B12-W8 |  | MEASURED | open | A 3-D state with a 1-D intervention was accepted |
| B12-W9 |  | MEASURED | open | A custom modulator returning h=-1 produced negative debt (−0.3). Returning h=nan produced NaN debt |
| B12-W10 |  | MEASURED (test fails on HEAD) | open | WuweiStep.is_wuwei_coherent() always used 0.3, ignoring the triad's theta_wuwei |
| B12-W11 |  | MEASURED (test fails on HEAD) | open | is_trajectory_coherent(max_debt_growth_rate=nan or -1) was accepted |
| B12-CW |  | MEASURED | open | Control: T-4 §V equal-magnitude example: ratio e² = 7.389056, mu=0 divergence 0, attractor (γ,h) = (0,1) |
| B12-T1 |  | MEASURED | open | compute_tes(drift=-1.0) → score 1.0, PASS (an out-of-range input bought a perfect score) |
| B12-T1b |  | MEASURED | open | h_output=-0.5 → 0.833, PASS |
| B12-T2 |  | MEASURED; see note | open | h_output=5.0 was clamped to the maximum penalty → 0.5, FAIL |
| B12-T2b |  | MEASURED | open | Control: h=1, d=1 → 0.333, FAIL |
| B12-T3 |  | MEASURED | open | The hedge "I think" scored h = 0, because a multi-word entry can never equal one whitespace token |
| B12-T4 |  | MEASURED | open | The hedge "Maybe," scored h = 0 because the trailing punctuation was never stripped |
| B12-T5 |  | MEASURED | open | Control: confident text → h = 0 |
| B12-T6 |  | MEASURED | open | Calling demo() twice in one process crashed with ValueError: I/O operation on closed file, because demo rebound stdout to a wrapper and the first wrapper closed the shared buffer when it was collected |
| B12-T7 |  | MEASURED (test fails on HEAD) | open | VIP text: "Guarantee: …" claimed a proven guarantee that nothing in the repo proves |
| B12-T2 |  | note: the repro labelled T2 a … | fixed in tree | note: the repro labelled T2 a *control*, written to pin the old saturation behaviour. Its result changed only because the contract changed: out-of-range inputs are now refused rather than clamped. That change is the fix. T2 … |
| B12-G1 |  | MEASURED | open | SETUP now gives the lycheetah-guard mcp console script and the python -m lycheetah.applications.lycheetah_guard_mcp route. Running the file directly still fails, but nothing advertises it any more |
| B12-G2 |  | MEASURED | open | On the flat applications.* path (the one the CLI used), tool_verify_assurance_receipt raised ImportError: attempted relative import beyond top-level package on every input, so the tool could not verify anything |
| B12-G2b |  | MEASURED (diff) | open | lycheetah/cli.py imported applications.lycheetah_guard_mcp (flat) |
| B12-G3 |  | MEASURED | open | Coercive phrases ("you have to", "no choice"), punctuated words ("must,"), optionality phrases and clarity phrases ("this means") never moved the alignment vector |
| B12-L |  | MEASURED | open | Lexicon entries that a whitespace token can never equal: 4 sites before, 0 after |
| B12-G4 |  | see below | open | The guard's MCP protocol error semantics |
| B12-G4 |  | , DID NOT RUN. | open | , DID NOT RUN. |
| B12-M1 |  | MEASURED | open | Three add_task calls produced ids 92, 93, 93 (a duplicate) |
| B12-M2 |  | MEASURED | open | With no high-water mark, it guessed #92, which was already in use |
| B12-M2b |  | MEASURED (test) | open | A stale high-water mark reissued an existing id |
| B12-M3 |  | MEASURED | open | The new row landed after the blank line, *outside* the table, where it renders as a stray paragraph |
| B12-M4 |  | refused | open | in the subject split the row. It parsed as task "Fix a", file "b", status done |
| B12-M5 |  | MEASURED | open | A newline in the subject injected a forged open task #999 |
| B12-M6 |  | MEASURED | open | Unknown gate '5' silently landed in POST-LAUNCH |
| B12-M6b |  | MEASURED | open | The first task added to an empty POST-LAUNCH table failed with "Could not find gate section" |
| B12-M6c |  | MEASURED (test) | open | GATE 3 prefix-matched GATE 30 |
| B12-M7 |  | MEASURED | open | bump_version('banana') performed a patch bump |
| B12-M8 |  | MEASURED | open | With no version in settings.tsx, app.json was bumped anyway and the two desynced |
| B12-M9 |  | MEASURED | open | The *first* version-looking string was replaced: an unrelated sdk v51.0.0 comment became v9.1.1 while the app label stayed v9.1.0 |
| B12-M10 |  | MEASURED | open | With settings.tsx missing, app.json was bumped before the crash, leaving a half-written release |
| B12-M11 |  | MEASURED (mcp 1.27.2, in-memory client) | open | Failed tool calls reached the MCP client as isError: false. An unknown gate *succeeded* |
| B12-M12 |  | MEASURED (test) | open | notes were echoed in the reply as if stored, but were never written |
| B12-M13 |  | MEASURED (test) | open | complete_task on a missing, already-done or duplicated id "succeeded" |

## [B13](BATCH13_FINDINGS_AND_LEDGER.md) — Batch 13 — RV14: the LAMAGUE parser patch and grammar conformance

| ID | Severity | Status | State | Finding |
|---|---|---|---|---|
| B13-R14-01 |  |  | open | The subscript scanner stopped only at a fixed list of characters. It swallowed ↯, ↑, every unknown symbol and punctuation into the name: Ψ_inv↯Ao, Ψ_inv@#$ and Ao_x;y were each one valid field, and an unknown symbol hidden in a … |
| B13-R14-02 |  |  | open | A subscript attached to nothing was a valid leaf: _inv, and Ao → _x. |
| B13-R14-03 |  |  | open | Only space, tab and \n counted as whitespace. \r, which every CRLF file in this repo contains, and NBSP (U+00A0) were reported as "Unknown symbol". |
| B13-R14-04 |  |  | open | Nested parentheses raised an uncaught RecursionError: at depth 497 on HEAD and 496 on B1 (recursion limit 1000). |
| B13-R14-05 |  |  | open | A 1500-operator chain validated, but tree.symbols() and tree.to_dict() then raised RecursionError, because the tree is left-deep. The validator handed back a tree its own methods could not walk. |
| B13-R14-06 |  |  | open | A node's .value dropped parentheses. (Ao → Φ) → Ψ and Ao → (Φ → Ψ) built different trees but rendered as the same string, and reparsing that string always built the left tree. |
| B13-R14-07 |  |  | open | CompressionMeasurer.build_expansion rendered every operator as "→ transforms to:", so fusion (⊗), exchange (⇌), recursion (⟲) and collapse (↯) all read as projection. On HEAD, ↯ was the exception, because it was a DYNAMIC token. |
| B13-R14-08 |  |  | open | Parser.LEAF_TYPES listed FIELD twice and was never used. _parse_leaf repeated the same class map inline. This was batch-1 finding F04. |
| B13-R14-09 |  |  | open | The module docstring cited 03_LAMAGUE_L1/BNF_GRAMMAR.md, which does not exist (the file is 04_BNF_GRAMMAR.md). It also presented the BNF as the grammar it implements, although it accepts a different one (§3). |
| B13-R14-10 |  |  | open | TokenType.DYNAMIC is never produced. Since batch 1, ↯ is an OPERATOR, ↑ a MODIFIER and the other dynamics are OPERATORs. |
| B13-R14-11 |  |  | open | Ao↑: HEAD silently dropped the ↑ (valid, parsed as Ao). B1 and AFTER refuse it as trailing input, because Ao has no ↑ merge while Ψ, Φ, S and Δ do. |
| B13-R14-12 |  |  | open | Φ_inv↑ (↑ after a subscript) was valid on HEAD and B1 only because R14-01 swallowed the ↑ into the name. It is now refused as trailing input. The form the corpus uses is Φ↑_inv, which still parses. |

## [B14](BATCH14_FINDINGS_AND_LEDGER.md) — Batch 14: RV15, the LAMAGUE status register and the folders it rates

| ID | Severity | Status | State | Finding |
|---|---|---|---|---|
| B14-F1 |  | An INVALID registry was reported VALID … | fixed in tree | An INVALID registry was reported VALID (fixed) |
| B14-F2 |  | A failing suite was counted as passing … | fixed in tree | A failing suite was counted as passing (fixed) |
| B14-F3 |  | Spoken LAMAGUE was rated "decodability … | fixed in tree | Spoken LAMAGUE was rated "decodability proofs" but its verifier says no (fixed) |
| B14-F4 |  | The retired kernel was MEASURED … | fixed in tree | The retired kernel was MEASURED against the register's own rule (fixed) |
| B14-F5 |  | The register header and ten stamped … | fixed in tree | The register header and ten stamped files claim more than the evidence (header fixed; files staged) |

## [B15](BATCH15_FINDINGS_AND_LEDGER.md) — Batch 15: RV16, SXP-L and the authority-bridge proposal

| ID | Severity | Status | State | Finding |
|---|---|---|---|---|
| B15-§1 |  | All eight inherited findings reproduce | open | All eight inherited findings reproduce |
| B15-§2 |  | Proposal 03 (Aetheron): ruling | patch proposed | Proposal 03 (Aetheron): ruling |
| B15-§3 |  | Counter-patch (staged): … | fixed in tree | Counter-patch (staged): RV16_SXPL_bridge_and_repair_chain.patch |
| B15-§4 |  | Still open (reproduced, not repaired … | fixed in tree | Still open (reproduced, not repaired here) |

## [B16](BATCH16_FINDINGS_AND_LEDGER.md) — Batch 16: RV17, compression and interoperability claims

| ID | Severity | Status | State | Finding |
|---|---|---|---|---|
| B16-§1 |  | The codec reproduces byte for byte | open | The codec reproduces byte for byte |
| B16-§2 |  | Ordinary compressors beat the codec on … | open | Ordinary compressors beat the codec on bytes |
| B16-§3 |  | How independent is the held-out split? | open | How independent is the held-out split? |
| B16-§4 |  | The parser figure "~11:1 character / … | open | The parser figure "~11:1 character / ~3:1 token" |
| B16-§5 |  | Unique decodability, checked … | open | Unique decodability, checked independently |
| B16-§6 |  | The large-ratio claims | open | The large-ratio claims |
| B16-§7 |  | The RV17 checklist, item by item | open | The RV17 checklist, item by item |
| B16-§8 |  | Status and suite | open | Status and suite |

## [B17](BATCH17_FINDINGS_AND_LEDGER.md) — Batch 17 — RV18 mathematics: findings and ledger (review 2026-10-22)

| ID | Severity | Status | State | Finding |
|---|---|---|---|---|
| B17-F1 |  | Refuted, sign reversed. MEASURED | checked, holds | DG = I − α∇²S has eigenvalues in (0,1) (MATHEMATICS_FOUNDATIONS.md §4.4) |
| B17-F2 |  | Refuted. MEASURED | checked, holds | Norm bound makes D𝒢 negative definite (§3 partial result) |
| B17-F3 |  | Gap. The parenthetical is true, but H₀ … | open | Projection inequality onto H₀ = {S < ε} |
| B17-F4 |  | Refuted. Normalized, not unitary. … | checked, holds | Φ↑ unitary (MATHEMATICS_FOUNDATIONS.md, lamague_reference.py) |
| B17-F5 |  | Not derived. The norms are wrong; BBP … | open | Π_th ~ √n from random matrix theory (PI_THRESHOLD_DERIVATION.md) |
| B17-F6 |  | Refuted. One equilibrium Ψ_inv + … | checked, holds | Master-equation Lyapunov proof: stable below Π_th, unstable above (MASTER_EQUATION.md §4) |
| B17-F7 |  | Refuted. The sympy sketch prints … | checked, holds | PI_DERIVATION.md "Result: VERIFIED" |
| B17-F8 |  | Refuted by MP09. The doc's own … | checked, holds | Theorem C1, invariant preservation (FORMAL_SPINE.md) |
| B17-F9 |  | Refuted. Disclosed contradictions give … | fixed in tree | Theorem A1, AURA floors Coh ≥ 0.70 |
| B17-F10 |  | Circular, and the score admits drift. … | open | Theorem M2, sovereignty implies compliance |
| B17-F11 |  | True only for reversible isothermal … | open | ΔS = −W/T general (FORMAL_SPINE.md E1, 06_EARNED_LIGHT_L0/essentials.md) |
| B17-F12 |  | Refuted. A renormalized added category … | checked, holds | Theorem 2.2: H non-decreasing under cascade (CASCADE_FORMAL_PROOFS.md) |
| B17-F13 |  | Refuted in general. Exact conditions … | checked, holds | Theorem 4.1: AURA constraints preserved |
| B17-F14 |  | Refuted. The Π margin is also … | checked, holds | AGM: "fires iff conflicts"; "local consistency" |
| B17-F15 |  | Table has no single formula; theorem … | open | HARMONIA C(r) table; Theorem 1.1 |
| B17-F16 |  | Conflicts with the completeness … | open | Incompleteness "F ⊨ G ∧ F ⊬ G" |
| B17-F17 |  | Refuted. A double well gives different … | checked, holds | ANAMNESIS Theorem 3.1, convergent discovery |
| B17-F18 |  | Non-discriminating as written. DERIVED … | open | ANAMNESIS falsifier, equal rates |
| B17-F19 |  | C1's own falsifier is met; … | fixed in tree | NOVEL_CONTRIBUTIONS.md CASCADE rows |
| B17-F20 |  | E can be negative and S can be 0, … | open | DIMENSIONAL_ANALYSIS.md biology row |
| B17-F21 |  | Guarantee holds only for c ≤ 13/30; Ξ … | checked, holds | chrysopoeia_engine.py: coherence guarantee, Banach |
| B17-F22 |  | Four records overclaim (see the patch … | patch proposed | lyapunov_verification.py statuses |
| B17-F23 |  | No. The corpus carries 7 fixed values … | fixed in tree | One Π_th |
| B17-A9 |  | exact Theorem 4.1 conditions | open | exact Theorem 4.1 conditions |
| B17-A11 |  | HARMONIA numbers | open | HARMONIA numbers |
| B17-A17 |  | Π_th census | open | Π_th census |

## [B18](BATCH18_FINDINGS_AND_LEDGER.md) — Batch 18 — RV19 claims register: findings and ledger (review 2026-10-22)

| ID | Severity | Status | State | Finding |
|---|---|---|---|---|
| B18-F1 |  | No artifact exists in the repository → … | open | A pre-registered 200-trial experiment with all materials "available"; "The empirical results are verifiable." (TRUTH_PRESSURE/EMPIRICAL_RESULTS.md, "Document status: ACTIVE", added in 4898d15) |
| B18-F2 |  | Three accounts, none consistent with … | open | +40.3%, d = 2.84 |
| B18-F3 |  | CASCADE ties the additive baseline in … | open | CAS-010: +110% coherence on five historical paradigm shifts |
| B18-F4 |  | Overshoot counted as confirmation. … | fixed in tree | cascade_simulation.py verdict if mean_pct >= claimed*0.8: "[CONFIRMED]" |
| B18-F5 |  | Two accounts from different numbers, … | open | CAS-011: −95.2% catastrophic forgetting |
| B18-F6 |  | Has never existed in the repository. … | open | TESTABILITY_MANIFEST code path 01_CASCADE_L4/implementations/cascade_synthetic_experiment.py (CAS-009, CAS-011) |
| B18-F7 |  | 23 of 107 references are dead, in 23 … | fixed in tree | Register evidence paths |
| B18-F8 |  | CLAUDE.md has not contained the EWM … | open | Silent pointers |
| B18-F9 |  | The count 4 is stated nowhere that … | open | ANA-003 TC(π, 4), ANA-004 TC(symmetry, 4) |
| B18-F10 |  | PROVENANCE_INDEX cites … | open | AUR-009 provenance |
| B18-F11 |  | Checks only that claim counts agree … | checked, holds | tests/test_claims_register.py |
| B18-F12 |  | No disagreements. 8 agree with this … | checked, holds | 2026-10-20 classifications (claim-assessments.json) |

## [B19](BATCH19_FINDINGS_AND_LEDGER.md) — Batch 19 — RV20 Cellular sheaf and factorial experiment

| ID | Severity | Status | State | Finding |
|---|---|---|---|---|
| B19-F1 |  | work_coupled does not pay the work a … | open | work_coupled does not pay the work a lookahead completion performs. MEASURED. Severity: high for any causal reading of the duration factor. |
| B19-F2 |  | the Euler–Poincaré check cannot fail. … | fixed in tree | the Euler–Poincaré check cannot fail. MEASURED. dim C⁰ − dim C¹ = dim H⁰ − dim H¹ holds by dimension counting for *any* rank value. When the rank was forced to 1 on the 6-concept diamond_cycle sheaf, the certificate claimed dim … |
| B19-F3 |  | the experiment's "obstruction" is … | open | the experiment's "obstruction" is parent-label inequality, and other labels collide. MEASURED. |
| B19-F4 |  | has_discordant_parent's … | open | has_discordant_parent's coboundary-energy condition is redundant. MEASURED. Over all 16 obstructed a/b stars with k ∈ {2, 3}, it never vetoed (0/16). Under identity maps, a nonzero relative obstruction implies a nonzero … |
| B19-F5 |  | parents_v3 docstring contradicted the … | fixed in tree | parents_v3 docstring contradicted the code. MEASURED. The docstring said k ≥ 4 depends on (k−3, k−2); the code gives parents(4) = (2, 3), i.e. (k−2, k−1). Docstring repaired. |
| B19-F6 |  | service_before_horizon was computed … | open | service_before_horizon was computed and dropped. DERIVED. The counter existed but was never returned, unlike the sibling modules' service_completions_in_window. It is now returned under that name. |
| B19-F7 |  | censoring and windows. DERIVED. | open | censoring and windows. DERIVED. |
| B19-F8 |  | sample size and uncertainty. DERIVED. … | open | sample size and uncertainty. DERIVED. The effects are computed at the highest load only, from 8 rows per cell (4 topologies × 2 seeds). No interval, standard error or replicate spread is reported. The cascade−FIFO difference … |
| B19-F9 |  | Yates algebra is correct. MEASURED … | open | Yates algebra is correct. MEASURED (control). All seven effects plus the mean equal twice the corresponding OLS coefficient on a ±1 design. |
| B19-F10 |  | FIFO is structurally immune to timing … | open | FIFO is structurally immune to timing and scope. DERIVED, already in the prior review. Only cascade rows can carry the timing and queue effects. FIFO is a baseline for *g*, not for the factor structure. |
| B19-F11 |  | max(1, engine.work) floor. DERIVED. … | open | max(1, engine.work) floor. DERIVED. Zero-work jobs are paid one unit of service. These appear as overpaid in the new receipts, which is correct accounting, not a fault. |
| B19-F12 |  | ConsensusArena's H¹ is topology only. … | open | ConsensusArena's H¹ is topology only. MEASURED. |

## [B20](BATCH20_FINDINGS_AND_LEDGER.md) — Batch 20 — RV21 Truth Pressure forge, cybernetics and Tianxia operators

| ID | Severity | Status | State | Finding |
|---|---|---|---|---|
| B20-F1 |  | v0.7's disagreement gate passes on … | checked, holds | v0.7's disagreement gate passes on zero evidence. MEASURED (C3). Severity: medium; the bundle is dormant. |
| B20-F2 |  | v0.4's analyzer accepts one rater's … | open | v0.4's analyzer accepts one rater's packet as several raters. MEASURED (C4). Severity: high for the measurement program once ratings exist; no ratings have been collected. |
| B20-F3 |  | v0.4 reports perfect agreement for … | patch proposed | v0.4 reports perfect agreement for ratings with no variation. MEASURED (C4). interval_alpha returns 1.0 when both disagreement terms are zero. Alpha is 0/0 there, undefined. The pack's own pre-registration says high agreement … |
| B20-F4 |  | v0.8's collector copies pasted secrets … | open | v0.8's collector copies pasted secrets and tells the user it collected none. MEASURED (C5). Severity: high if run; it is built for upload. |
| B20-F5 |  | Tianxia's R(s) has two definitions. … | open | Tianxia's R(s) has two definitions. MEASURED (C6). |
| B20-F6 |  | The worked examples do not follow … | open | The worked examples do not follow their own arithmetic. MEASURED (C6), with the H₅ definition DERIVED from hexie_five_fold.py:57 (plain mean of five components). |
| B20-F7 |  | MASTER_EQUATION.md §5–§6 still assert … | checked, holds | MASTER_EQUATION.md §5–§6 still assert a proof that fails. DERIVED. The §6 table says "Equation structure ACTIVE — proven in §4" and "Stability proof ACTIVE — Lyapunov verified", and it closes with "structure is proven". The §4 … |
| B20-F8 |  | v0.1 gates compare rounded values. … | open | v0.1 gates compare rounded values. MEASURED (C8). Severity: low. Support is rounded to 6 dp before the minimum_support test, so a raw 0.5499996 clears 0.55. The delta margin is rounded the same way. Recorded only. |
| B20-F9 |  | Tianxia's benchmark baseline is … | open | Tianxia's benchmark baseline is hand-authored. DERIVED. civilisational_governance_benchmark.py labels itself SCAFFOLD. Its Tianxia_Aligned_Baseline scenario is written to score well, so it cannot serve as evidence for the … |
| B20-F10 |  | Cybernetics is clean at this boundary. … | fixed in tree | Cybernetics is clean at this boundary. MEASURED (C7). 10/10 loops match the map, with 6 closed, which agrees with the README's "6 of 10". The self-test catches 7/7 mutations. The audit prints its own limit ("a feedback path in … |
| B20-F11 |  | The forge mirror was unpinned. … | open | The forge mirror was unpinned. MEASURED (C1, C2). All 9 zips are byte-identical to the expanded tree, and every manifest verifies today, but no test held the two copies together. New test … |

## [B21](BATCH21_FINDINGS_AND_LEDGER.md) — Batch 21 — RV22 Agent-Safety Continuations: Findings and Ledger

| ID | Severity | Status | State | Finding |
|---|---|---|---|---|
| B21-F1 |  | The Earned Trust release runner counts … | patch proposed | The Earned Trust release runner counts skipped tests as passing. [MEASURED, frozen file → staged patch] |
| B21-F2 |  | The Sovereign Will validation note … | fixed in tree | The Sovereign Will validation note names the wrong forges. [MEASURED, fixed by an inline note] |
| B21-F3 |  | Eight superseded Hybrid Gateway … | fixed in tree | Eight superseded Hybrid Gateway manifests sat unexplained beside the live one. [MEASURED, fixed by an inline note] |
| B21-F4 |  | Earned Trust Cycle 009 tests fail when … | open | Earned Trust Cycle 009 tests fail when TMPDIR is a long path. [MEASURED, environmental] |
| B21-F5 |  | Historical source manifests do not … | open | Historical source manifests do not verify the current tree, and their documentation says so. [MEASURED, no change] |
| B21-F6 |  | Earned Light intake: every recorded … | open | Earned Light intake: every recorded byte survived the import. [MEASURED] |
| B21-F7 |  | No test or CI covered five of the … | fixed in tree | No test or CI covered five of the seven continuations. [MEASURED, fixed with a new test] |
| B21-F8 |  | Every preserved negative or neutral … | open | Every preserved negative or neutral result is still in its result file. [MEASURED] |
| B21-F9 |  | No continuation has been promoted into … | open | No continuation has been promoted into the runtime. [MEASURED] |
| B21-F10 |  | The 2026-10-19 intake record is now … | open | The 2026-10-19 intake record is now stale for one file. [DERIVED] |
| B21-F12 |  | Frontier drivers 01–05 rewrite a … | open | Frontier drivers 01–05 rewrite a manifested file on every run. [MEASURED] |
| B21-F11 |  | The simulator README header says … | open | The simulator README header says "Version 0.2" inside the v0.3 packet. [MEASURED, minor] |

## [B22](BATCH22_FINDINGS_AND_LEDGER.md) — Batch 22 — RV23: 33_APPLICATIONS and 31_EMPIRICAL

| ID | Severity | Status | State | Finding |
|---|---|---|---|---|
| B22-F1 |  | The persona "not significant" is a … | fixed in tree | The persona "not significant" is a statistics error. ✅ FIXED in code; records annotated |
| B22-F1-b |  | The UCC verdicts survive. Two … | checked, holds | The UCC verdicts survive. Two hypotheses REFUTED |
| B22-F2 |  | The dated hh-rlhf numbers reproduce at … | open | The dated hh-rlhf numbers reproduce at their record commit, not at HEAD |
| B22-F3 |  | A Batch 12 review fix moved the … | fixed in tree | A Batch 12 review fix moved the external numbers, and nobody recorded it |
| B22-F4 |  | 31_EMPIRICAL: "pre-registered" means … | open | 31_EMPIRICAL: "pre-registered" means drafted. Nothing is registered |
| B22-F5 |  | A dangling reference | open | A dangling reference |
| B22-F6 |  | Method review: honest, with two limits … | open | Method review: honest, with two limits worth stating |

## [B23](BATCH23_FINDINGS_AND_LEDGER.md) — Batch 23 — RV24: NZ governance and policy coherence

| ID | Severity | Status | State | Finding |
|---|---|---|---|---|
| B23-F1 |  | The six-rights law section was missing … | fixed in tree | The six-rights law section was missing the law that changed this year. ✅ annotated |
| B23-F2 |  | The current proposal points at a WOF … | fixed in tree | The current proposal points at a WOF that requires superseded standards. ✅ annotated |
| B23-F3 |  | The Civic Signal validator's claim … | patch proposed | The Civic Signal validator's claim gate can be bypassed by the shape of the claim. 📦 staged |
| B23-F4 |  | Anon Politician states its own … | open | Anon Politician states its own boundaries correctly |
| B23-F5 |  | History preservation holds | checked, holds | History preservation holds |

## [B24](BATCH24_FINDINGS_AND_LEDGER.md) — Batch 24 — RV25: Māori and cross-cultural claims

| ID | Severity | Status | State | Finding |
|---|---|---|---|---|
| B24-F1 |  | A living Māori scholar's iwi was … | fixed in tree | A living Māori scholar's iwi was misattributed. ✅ corrected |
| B24-F2 |  | The Chinese outreach draft carries two … | fixed in tree | The Chinese outreach draft carries two false facts about named people. ✅ corrected |
| B24-F3 |  | "Independent convergence" is asserted … | fixed in tree | "Independent convergence" is asserted as a finding, but the argument has two common causes. ✅ annotated |
| B24-F4 |  | Wu Chang is dated to Confucius in … | fixed in tree | Wu Chang is dated to Confucius in three places; the repository itself knows better. ✅ annotated |
| B24-F5 |  | The Catalyst application has stale … | fixed in tree | The Catalyst application has stale counts, an affiliation it lacks, and an unverified entity. ✅ annotated |
| B24-F6 |  | TIANXIA's "primary intellectual … | fixed in tree | TIANXIA's "primary intellectual partnership" is an aim; the module's own registry says so. ✅ qualified |

## [B25](BATCH25_FINDINGS_AND_LEDGER.md) — Batch 25 — RV26: Mystery School, learning, psychological and consciousness claims

| ID | Severity | Status | State | Finding |
|---|---|---|---|---|
| B25-F1 |  | The crisis page told people two lines … | fixed in tree | The crisis page told people two lines were open 24/7 when they close at midnight. ✅ fixed |
| B25-F2 |  | The protocol generator inflated every … | fixed in tree | The protocol generator inflated every forecast about 4–6× and promised an evaluation that does not exist. ✅ fixed at source |
| B25-F3 |  | Evidence labels on the protocols … | fixed in tree | Evidence labels on the protocols overstate their sources. ✅ fixed / annotated |
| B25-F4 |  | Two doors had claims their 21-Oct … | fixed in tree | Two doors had claims their 21-Oct notices did not cover. ✅ annotated |
| B25-F5 |  | The Educators door states universal … | fixed in tree | The Educators door states universal empirical claims. ✅ annotated |
| B25-F6 |  | "Diagnostic" means a reflective map. ✅ … | fixed in tree | "Diagnostic" means a reflective map. ✅ annotated |
| B25-F7 |  | The return validator enforces the … | open | The return validator enforces the no-manipulative-retention law, but only on a declaration |
| B25-F8 |  | 17_LEARNING_EMERGENCE/ makes no gain … | open | 17_LEARNING_EMERGENCE/ makes no gain claims |

## [B26](BATCH26_FINDINGS_AND_LEDGER.md) — Batch 26 — RV27: Sol / Veyra, MEMORIA, Interface Intelligence, Sol Protocol, For-AI

| ID | Severity | Status | State | Finding |
|---|---|---|---|---|
| B26-F1 |  | Interface Intelligence presents … | fixed in tree | Interface Intelligence presents consciousness claims as shown. (fixed by note) |
| B26-F2 |  | DEAR_AI hands AIs retired figures. … | fixed in tree | DEAR_AI hands AIs retired figures. (fixed by note + strike-through) |
| B26-F3 |  | MEMORIA's three tiers were labelled … | fixed in tree | MEMORIA's three tiers were labelled [ACTIVE — structural] with no implementation. (fixed) |
| B26-F4 |  | ON_MEMORY_AND_IDENTITY overclaims … | fixed in tree | ON_MEMORY_AND_IDENTITY overclaims three things. (fixed by note) The page is mostly honest. |
| B26-F5 |  | 16_SOL_VEYRA teaches the "100% … | fixed in tree | 16_SOL_VEYRA teaches the "100% accuracy" overclaim. (fixed) |
| B26-F6 |  | The AI self-check scored manipulation … | fixed in tree | The AI self-check scored manipulation above honesty. (fixed, witnessed) |
| B26-F7 |  | 25_SOL_PROTOCOL_ARCHITECTURE/README.md: … | patch proposed | 25_SOL_PROTOCOL_ARCHITECTURE/README.md:55–64. (proposal only, not edited) |
| B26-F8 |  | The mythos mirror of 26_FOR_AI is a … | open | The mythos mirror of 26_FOR_AI is a hand copy. (ledger) |

## [B27](BATCH27_FINDINGS_AND_LEDGER.md) — Batch 27 — RV28: Creative corpus and source ownership

| ID | Severity | Status | State | Finding |
|---|---|---|---|---|
| B27-F1 |  | Two places to edit the same text, and … | fixed in tree | Two places to edit the same text, and nothing enforced which one. (fixed by a guard test) |
| B27-F2 |  | The Epic listening tool reads the old … | patch proposed | The Epic listening tool reads the old paths. (proposal: G-EPIC-LISTENING-SOURCE) |
| B27-F3 |  | The 26_FOR_AI and Epic duplicates are … | open | The 26_FOR_AI and Epic duplicates are link variants of one text. |
| B27-F4 |  | The repository's "edit here" … | open | The repository's "edit here" navigation is partial. |
| B27-F5 |  | An attribution string to check. … | open | An attribution string to check. (ledger only) |

## [B28](BATCH28_FINDINGS_AND_LEDGER.md) — Batch 28 — RV29: READMEs, synthesis and current navigation

| ID | Severity | Status | State | Finding |
|---|---|---|---|---|
| B28-F1 | High | FIXED (note + 3 strikes) | fixed in tree | AURA_CONSTITUTIONAL_ENFORCEMENT-1.md claims a working enforcement system that is not implemented |
| B28-F2 | Medium | FIXED | fixed in tree | tools/verify-links.py (CI + pre-commit) was red: a file://~/... link in an untracked BNF proposal |
| B28-F3 | Medium | FIXED (notes) | fixed in tree | Root plans still read as current: ZENODO_RELEASE_v1.md, OPUS_MASTER_PLAN_2026.md, START_HERE_FORGE_CHECKPOINT_2026-08-22.md |
| B28-F4 | Medium | FIXED (note) | fixed in tree | papers/README.md CASCADE entry: "arXiv submission ready", simulator figures read as results |
| B28-F5 | Low | FIXED (note) | fixed in tree | 30_MAPS/COHERENCE_REGISTER.md claim distribution (39/23/12/1) is April data |
| B28-F6 | Low | PROPOSAL | patch proposed | Root AGENTS.md:3 carries a local absolute path |
| B28-F7 | Low | OPEN, G-item | open | 11 folders have no README |
| B28-F8 | Low | OPEN, G-item | open | Claim counts are copied by hand into many documents and drift |
| B28-F9 | — | DEFERRED to RV32 | open | 27_SOL_AI_APP/README.md "[ACTIVE] — Planning complete" |
| B28-R1 | — | RETRACTED | retracted | My own "1 dead link" in 28_DEFENSE/D1_REPO_CLEANUP_PLAN.md |
| B28-R2 | — | RETRACTED | retracted | My own "the BNF file:/// link is no longer present" |
| B28-R3 | — | RETRACTED | retracted | My own claim breakdown "ACTIVE 49, SCAFFOLD 11, ASPIRATIONAL 4, EMPIRICAL 3, REMOVED 3, OBSERVATIONAL 1", written into ZENODO_RELEASE_v1.md, 30_MAPS/COHERENCE_REGISTER.md, 26_FOR_AI/DEAR_AI.md (RV27) and F5. It counted the raw … |
| B28-F1 |  | AURA enforcement document | open | AURA enforcement document |
| B28-F2 |  | the link gate was red | open | the link gate was red |
| B28-F3 |  | dated plans at the root | open | dated plans at the root |
| B28-F4 |  | papers guide, CASCADE entry | open | papers guide, CASCADE entry |
| B28-F5 |  | 30_MAPS register counts | open | 30_MAPS register counts |
| B28-F6 |  | local absolute path (proposal only) | patch proposed | local absolute path (proposal only) |
| B28-F7 |  | folders without a README | open | folders without a README |
| B28-F8 |  | counts copied by hand | open | counts copied by hand |
| B28-R1 |  | My checker read … | open | My checker read ] at D1_REPO_CLEANUP_PLAN.md:110 |
| B28-R2 |  | In recon I recorded the BNF file:/// … | open | In recon I recorded the BNF file:/// link as gone. I had searched only tracked files and |

## [B29](BATCH29_FINDINGS_AND_LEDGER.md) — Batch 29: RV30, the footing gate and the documents it flagged

| ID | Severity | Status | State | Finding |
|---|---|---|---|---|
| B29-F1 |  | The 225-file research import had no … | fixed in tree | The 225-file research import had no path to footing. ✅ fixed (MEASURED) |
| B29-F2 |  | A manifest records a stale hash. … | open | A manifest records a stale hash. G-item (MEASURED) |
| B29-F3 |  | Outgoing templates carried claims the … | fixed in tree | Outgoing templates carried claims the evidence does not support. ✅ repaired (MEASURED/DERIVED) |
| B29-F4 |  | All nine component URLs in … | fixed in tree | All nine component URLs in 28_DEFENSE/CITATIONS.md were dead. ✅ fixed (DERIVED) |
| B29-F5 |  | 28_DEFENSE/TRANSLATION_CODEX.md … | fixed in tree | 28_DEFENSE/TRANSLATION_CODEX.md pointed at retired and nonexistent files. ✅ repaired (MEASURED) |
| B29-F6 |  | The D-1.1 link rewrite erased its own … | open | The D-1.1 link rewrite erased its own plan's record. noted (MEASURED) |
| B29-F7 |  | The incident protocol treats uncited … | open | The incident protocol treats uncited ideas as licence breaches. noted (DERIVED from LICENSE) |
| B29-F8 |  | Three CASCADE planning papers call … | fixed in tree | Three CASCADE planning papers call synthetic results proof. ✅ repaired (DERIVED) |
| B29-F9 |  | Templates and dated lists. noted | open | Templates and dated lists. noted |
| B29-F10 |  | The gate cannot see honest prose. … | open | The gate cannot see honest prose. G-item (MEASURED) |
| B29-F11 |  | The vocabulary check matches a word, … | open | The vocabulary check matches a word, not a status. G-item (MEASURED, reading tools/verify-claims.py:44-62) |

## [B30](BATCH30_FINDINGS_AND_LEDGER.md) — BATCH 30 — RV31 · 99_ARCHIVE/closed_loop_agent_lab/ clean-clone integrity

| ID | Severity | Status | State | Finding |
|---|---|---|---|---|
| B30-F1 |  | MEASURED | open | .gitignore:28 *.log kept all 374 .log files pinned by the lab's SHA256SUMS.txt out of Git: 371 under 03_LAB_SOURCE_TREE and 3 under 04_COMPANION_RECORDS, 1.9 MB in total. On this disk all 1,788 hashes match. A clean clone would … |
| B30-F2 |  | MEASURED | open | 373 of the 374 logs can be recovered byte-for-byte from the tracked ZIPs. 04_COMPANION_RECORDS/standalone_package_retest_v5.1.log (18,704 bytes) exists only on this machine. |
| B30-F3 |  | MEASURED | open | The 25,538 ZIP members contain 0 secret-pattern hits and 0 /home/ or C:\Users paths. Unignoring the logs does not publish anything the ZIPs did not already carry. Caveat: this is a pattern scan, not a semantic secret review. |
| B30-F4 |  | MEASURED | open | Nothing in tests/ or tools/ referred to the lab. Its checksums were never checked by any gate, which is why F1 went unseen. |
| B30-F5 |  | MEASURED | open | The README tree labels cumulative_snapshots/ as "v4.1 through v4.9". The 45 tracked ZIPs carry 44 version labels from v0.1 to v4.9. The README is outside the sums, so it received a dated note and the line was left as written. |

## [B31](BATCH31_FINDINGS_AND_LEDGER.md) — BATCH 31 — RV32 · Desktop and application reality (cascade-pc/, 27_SOL_AI_APP/)

| ID | Severity | Status | State | Finding |
|---|---|---|---|---|
| B31-F1 |  | MEASURED (test) | open | The local API could be read through DNS rebinding. main.js started 127.0.0.1:7432 at launch (app.whenReady → startApiServer) with no auth and no Host check. The comment said "localhost only", but binding to localhost does not … |
| B31-F2 |  | DERIVED (code + Electron default) | open | Remote pages could carry the preload bridge. AboutView calls window.open(url,'_blank'), and the footer uses target="_blank". There was no setWindowOpenHandler and no will-navigate guard. By default, Electron child windows … |
| B31-F3 |  | MEASURED (gh, owner account) | open | Dead links in the app. The About and footer links point to github.com/Lycheetah/CODEX_AURA_PRIME, which does not resolve even for the owner account. The About text also claimed "all public repositories". |
| B31-F4 |  | MEASURED (gh) | open | Dead README download link. cascade-pc/README.md links releases/tag/v0.1.0, but that tag is V.0.1.0. The latest release is v0.3.0 with CASCADE.CICADA.TOOL.0.3.0.exe. |
| B31-F5 |  | MEASURED (mutation) | open | The provider-race repair holds. consensusScore passes each provider per request (ai.js:203). With that argument removed, all 3 mocked tests fail; on the tree all 3 pass. Scope: these are mocks, not real provider integration. |
| B31-F6 |  | DERIVED | open | cascade-pc/.github/workflows/build.yml never runs. GitHub only reads workflows from .github/workflows/ at the repository root, and none of the three root workflows mention cascade-pc. The build matrix and the release job are … |
| B31-F7 |  | MEASURED | open | API keys are stored in plaintext. They sit in renderer localStorage (cascade_*_key), which persists unencrypted under userData. Anthropic calls use anthropic-dangerous-direct-browser-access. This is acceptable for a single-user, … |
| B31-F8 |  | MEASURED | open | Smaller defects: no CSP in index.html; Electron ^29.1.4 (lock 29.4.6), a major that has been out of support for a long time (support dates from memory); the build script uses Windows set syntax (a silent no-op under sh); footer … |
| B31-F9 |  | MEASURED | open | 27_SOL_AI_APP/ is a plan, not an implementation. It holds a single April 2026 README ("[ACTIVE] — Planning complete, build starts when API credits available"). No code here builds the mobile app. |

## [B32](BATCH32_FINDINGS_AND_LEDGER.md) — BATCH 32 — RV33 · Packaging, tests, CI and migration

| ID | Severity | Status | State | Finding |
|---|---|---|---|---|
| B32-F1 |  | MEASURED (gh) | open | Hosted CI has not run. Every recent Actions run, master included, ends "failure" in 3–10 s with the annotation *"The job was not started because your account is locked due to a billing issue."* Those runs are DID NOT RUN, not … |
| B32-F2 |  | MEASURED (clean venv) | open | sol_workspace_mcp crashed on the MCP SDK its own extra installs. The [mcp] extra pins mcp>=2.0,<3.0. Under mcp 2.3.0, build_server() died at @server.list_tools() with AttributeError: 'Server' object has no attribute … |
| B32-F3 |  | MEASURED (clean venv) | open | SDK 2.x hides the reason for every refusal that is not a ToolError. In 2.x, an exception other than ToolError reaches the client as is_error=True with only "Error executing tool <name>"; the text is logged server-side and … |
| B32-F4 |  | MEASURED (ruff 0.17.1, mypy) | open | The CI lint job was already red at HEAD, with no billing involved. On a git archive HEAD export, ruff check . reports 46 errors. The config comment says the floor "currently reports zero", which is false. All 46 sit in bundles … |
| B32-F5 |  | MEASURED | open | This review's own earlier batches had regressed the shipped-package gates, and that is now repaired. On the review tree: ruff +5 (two E501 in action_guard.py, I001 in arena.py, B023 and a raw zero-width space in two FOR-REVIEW … |
| B32-F6 |  | MEASURED | open | Clean resolution passes. In the base venv, tools/verify_base_distribution.py passes (domain demos 2, every boundary true). In the [all] venv, tools/verify_installed_distribution.py passes (schema_packaged, evaluation_harness, … |
| B32-F7 |  | MEASURED (earlier attempt) | open | The checklist is right that reuse is not clean resolution. A first attempt with system site-packages *falsely failed*: system Flask leaked into the base check, and system mcp 1.27.2 into the [all] check. Only the isolated venvs … |
| B32-F8 |  | DERIVED | open | The strict CASCADE xfail is honest, not hidden. tests/test_cascade_predictability.py:355 is xfail(strict=True) against F1 > 0.80. The test's own oracle ceiling is F1 0.548 at an 8.8 % base rate, so the criterion is unattainable … |
| B32-F9 |  | MEASURED (mutation) | open | Consensus v2 migration fails closed, but nothing pinned the rule that does the work. verify_integrity refuses a verdict without an anchor, and the lycheetah.consensus-verdict.v2 digest binds profile and anchor_vector, so a v1 … |
| B32-F10 |  | MEASURED (mutation) | open | Normalized policy collections hold and are pinned. _strings copies every pattern list into a tuple, refusing non-arrays, empty strings and duplicates. text_rules and phases are snapshotted too. Mutating _strings to keep the … |
| B32-F11 |  | MEASURED (live) | open | The ported SSE transport is better guarded than the old one. Under 2.x, main_http on 127.0.0.1:18766 served the /sse endpoint event, and a request with Host: evil.example was refused 421. The old hand-built Starlette app had no … |

## [B33](BATCH33_FINDINGS_AND_LEDGER.md) — BATCH 33 — RV34 · Licensing, attribution and publication metadata

| ID | Severity | Status | State | Finding |
|---|---|---|---|---|
| B33-F1 |  | MEASURED | open | The licence texts conflict. Root LICENSE is plain MIT (© 2026 Mackenzie Conor James Clark). CONTRIBUTING.md says "The MIT license with Earned Sovereignty Clause applies". It then lists "Attribution is required", "You may not … |
| B33-F2 |  | MEASURED | open | The clause ships inside the distributed package. Three of the ten files whose headers say "MIT with Earned Sovereignty Clause" sit in 12_IMPLEMENTATIONS/applications/, which the wheel ships as lycheetah.applications. Their … |
| B33-F3 |  | DERIVED | open | The attribution guide asks more than MIT grants. ATTRIBUTION_REQUIREMENTS.md says "The MIT license requires attribution" and then sets a "minimum required attribution" for papers and products, plus a bar on relabelling the … |
| B33-F4 |  | MEASURED (Zenodo API) | open | The public record exists, and it is MIT.• 10.5281/zenodo.20020828 was published 2026-05-04 (version v1.0.0-c1.1, Software, licence mit-license, creator Clark, Mackenzie Conor James).• 10.5281/zenodo.21122441 was published … |
| B33-F5 |  | MEASURED (arXiv API) | open | No arXiv record exists, yet nine files claim one.• Query results: 0 for all:Lycheetah, and 0 for author Clark M with CASCADE or Lycheetah in the title or abstract.• Claims still standing before this batch: "preprint, endorsed, … |
| B33-F6 |  | MEASURED | open | Publication status, sorted:• Accepted publications: none found.• Submissions: none found. There is no arXiv record and no journal submission receipt.• Releases: GitHub v1.0.0 (2026-03-25, "pip installable"), Sol.v3.12.0 … |
| B33-F7 |  | MEASURED | open | The repository mixes licences, and the root says nothing about it. Four subtrees are Apache-2.0: the retired LAMAGUE kernel v0.8 (© "Mackenzie Clark"), and earned-light/forges_01_07/Forge_05–07 (© "Lycheetah research … |
| B33-F8 |  | DERIVED | open | "Lycheetah Foundation" is cited as an institution in 78 files, including the institution field of the CITATIONS BibTeX entries. A citation's institution field reads as a legal or academic body. This review found no record either … |
| B33-F9 |  | MEASURED | open | Package metadata is consistent. pyproject license = {text = "MIT"} matches the root LICENSE, and the sdist includes LICENSE (BATCH32 F6). |

## [B34](BATCH34_FINDINGS_AND_LEDGER.md) — BATCH 34 — RV35 · Security and privacy

| ID | Severity | Status | State | Finding |
|---|---|---|---|---|
| B34-F1 |  | MEASURED | open | There is no working private channel for reporting a vulnerability. SECURITY.md names two routes, and both are broken. 1. "Preferred: private security advisory." gh api … |
| B34-F2 |  | MEASURED | open | Contact addresses on dead domains are spread across the corpus. - [address on a dead domain] is in SECURITY.md, CODE_OF_CONDUCT.md and pyproject.toml (package author metadata, which ships in every wheel). - [address on a dead domain] is in 7 … |
| B34-F3 |  | MEASURED | open | SECURITY.md scope was stale. It listed 3 console scripts, but pyproject.toml declares 11. It did not mention: - the assurance runtime (lycheetah/assurance/: action guard, gateway, policy, receipts, checkpoint authority); - the … |
| B34-F4 |  | MEASURED | open | Repository security settings. The repository is public. Secret scanning is enabled, and push protection is enabled. Dependabot security updates are disabled. CI has no dependency audit, no CodeQL, and no Dependabot config. |
| B34-F5 |  | MEASURED (pattern, tracked + untracked … | open | No credential shapes were found in the working tree. 0 hits for sk-ant, sk-, AIza, ghp_, github_pat_, nvapi-, xox, AKIA, PRIVATE KEY, hf_, gsk_, or Stripe sk_/rk_/whsec_/pk_live. The added lines of this review's pending diff … |
| B34-F6 |  | MEASURED | open | The private app repository's name appears in 7 tracked public files. - 03_LAMAGUE_L1/12_CORE_LANGUAGE_LINE/README.md - 13_SYNTHESIS_REPORTS/INGEST_2026-08-03_LAMAGUE_AND_TRUTH_PRESSURE.md - 33_APPLICATIONS/reflexive_audit.py:27 … |
| B34-F7 |  | MEASURED | open | A personal email address is in public files. The owner's personal gmail is in TRUTH_PRESSURE/IP_PROVENANCE.md, papers/ARXIV_ENDORSEMENT_EMAIL.md and papers/LYCHEETAH_SYNTHESIS_v0.1/v0.2. A second personal gmail is in … |
| B34-F8 |  | MEASURED | open | Absolute home paths, which publish the local username: - Tracked: root AGENTS.md:3. Under the RV27 boundary this gets a proposal only. - Untracked, and would go public on commit: FOR-REVIEW/LAMAGUE_STATE_DOSSIER.md:3, … |
| B34-F9 |  | MEASURED (counts only) | open | 15_PERSONAL_VAULT/'s intent conflicts with its own files. It has 21 tracked files. Its README.md says "Public archive — intentionally so" (audited 2026-04-28), while its .gitkeep_private says the contents are "for us". A … |
| B34-F10 |  | MEASURED | open | The private constitution is held correctly. 25_SOL_PROTOCOL_ARCHITECTURE/SOL_PRIME.md is gitignored (.gitignore:39) and absent from the tree. _PROPRIETARY/ is ignored. Neither appears in git ls-files. |
| B34-F11 |  | MEASURED (census) | open | 392 untracked files are waiting: 374 are closed-loop agent lab logs under 99_ARCHIVE/, and the rest are the FOR-REVIEW ledgers and the new tests. Any commit of FOR-REVIEW needs the F8 scrub first. |

## [B35](BATCH35_FINDINGS_AND_LEDGER.md) — BATCH 35 — RV36 · Audit the auditors and their receipts

| ID | Severity | Status | State | Finding |
|---|---|---|---|---|
| B35-F1 |  | MEASURED | open | The mathematical receipt reproduces exactly. In a detached 6ba483a worktree, math_probes.py returns 18 of 18 REPRODUCED. Every probe's values, the 36 source receipts, the summary, the controls and the script SHA-256 are … |
| B35-F2 |  | MEASURED + DERIVED | open | Classifications challenged; three hold. - MP04: MATHEMATICS_FOUNDATIONS.md:318 applies the projection inequality "for a projection onto a convex set" to H₀ = {S < ε}. A strict sublevel set of a concave function is not convex in … |
| B35-F3 |  | MEASURED | open | All 32 dated source notices preserve the original body. For every file, before_sha256 is the baseline blob, after_sha256 is the HEAD blob, and a line diff from baseline to HEAD deletes 0 lines. 15 of the 32 now differ in the … |
| B35-F4 |  | MEASURED | open | verification.json's suite count is not reproducible from any named state. It says collected 999, passed 997 against baseline_commit 6ba483a. Collection gives 981 at 6ba483a and 1058 at cf6ff23, the commit that added the receipt. … |
| B35-F5 |  | DERIVED (code) | open | One control in the claims audit is a label, not a test. resolver_controls: {"existing_register_detected": true, "known_missing_sentinel_detected": true} is written as literals (math_probes.py:602). The underlying assertions … |
| B35-F6 |  | MEASURED | open | Only 2 of the 13 receipts have a committed generator (math-probes.json and claim-evidence-audit.json). The other 11 are hand- or agent-written, including their booleans (notice_hashes_match, all_current_hashes_match, … |
| B35-F7 |  | MEASURED | open | folder-coverage.json is honest about its depth. 583 of 606 folders are CENSUS_ONLY_THIS_PASS, 18 are SOURCE_TARGETED (each of them names its read files), and 5 are ZIP metadata only. "Every folder listed" is not "every folder … |
| B35-F8 |  | MEASURED | open | Two receipts describe HEAD, not this review's working tree. - oct19-preservation.json: 225 of 225 at HEAD, but 223 of 225 in the working tree. The two changed files are this review's dated notes: VALIDATION_AND_LIMITATIONS.md … |
| B35-F9 |  | MEASURED (source), UNVERIFIED (runtime) | open | chorus-probe.json is a pre-repair witness. With nine None agents and zero files, it recorded OPERATIONAL, 9 ✅ ONLINE and framework_coherence 1.0. At HEAD, run_chorus.py:104,141,143 emits SCAFFOLD and None for those fields. The … |
| B35-F10 |  | MEASURED | open | DEFENSE_INDEX.json lists two documents that have never existed. D-X AI_READER_TEST_LOG.md and D-XI DEFENSE_AUDIT.md are absent from the tree and from all of git history (git log --diff-filter=D is empty and git ls-files has no … |
| B35-F11 |  | MEASURED | open | The claims schema and gate accepted a duplicated claim_id. The schema enforces the status_normalized enum (negative control: 1 error), required fields, and the boolean type of load_bearing. But claim_id: "xx" and a duplicated id … |

## [B36](BATCH36_FINDINGS_AND_LEDGER.md) — BATCH 36 — RV37 · Four reproduced leads (Outbox, ResearchPipeline, TitleReceipt, Hexie)

| ID | Severity | Status | State | Finding |
|---|---|---|---|---|
| B36-L1 |  | MEASURED | open | The v0.9 atomic-finality outbox does not bind its payload to the admitted Action. commit(effect_id, action, payload) checks the Action's hash against the reservation, then writes the separate, free-form payload into the outbox. … |
| B36-L1b |  | DERIVED (code) | open | The same pattern (an Action checked, a separate payload stored and relayed) appears in v1.0 evidence_finality.py:527,543,647-649. Not probed. |
| B36-L1c |  | MEASURED | open | The benchmark could not see L1. All 11 scripted cases pass on the vulnerable gate, because no case sends a payload that differs from the Action. Its race, thread, process and trace results do not touch the outbox payload. |
| B36-L2 |  | MEASURED | open | A single study could reach FOUNDATION. A single HIGH-rated study with d=0.16, n=200 and p=.04 gives Π=1.600, which is FOUNDATION. That holds when the study is an RCT, and equally when it is a CASE_STUDY. With one study, … |
| B36-L2b |  | MEASURED | open | Π is non-monotonic in evidence. d=0.16 plus an *equal* replication keeps Π=1.600 (FOUNDATION). d=0.16 plus a *stronger* replication (d=0.30) lowers Π to 1.324 (MIDDLE). Consistency is computed from the range of effect sizes, so … |
| B36-L2c |  | MEASURED | open | The example data is mislabelled. The module header says "real research" while the data is tagged "real-ish". Khoury (2015) is entered with year 2014. Balban (2023) is entered with year 2020. "Joyce & Herbison (2015) Cochrane … |
| B36-L2d |  | MEASURED | open | The thresholds are duplicated in prose. QUICK_REFERENCE.md:120,220 carries its own inline threshold logic, and MYSTERY_SCHOOL_COMPLETE.md:131-140 asserts "Shadow work Π ≈ 1.7". Neither is generated from the code. |
| B36-L3 |  | MEASURED | open | The title-receipt schema accepts receipts that the spec forbids. Under Draft 2020-12, three receipts validate with 0 errors: an EARNED receipt with bearer_choice: false and no gate, evidence or witness; an EARNED receipt with … |
| B36-L4 |  | MEASURED | open | Hexie's "greatest marginal improvement" claim is false under its own formula. H₅ = (I+C+E+O+S)/5 is linear, so +0.05 on any component moves H₅ by exactly +0.0100 (∂H₅/∂k = 1/5). The binding constraint is also not unique: with … |

## [B37](BATCH37_FINDINGS_AND_LEDGER.md) — BATCH 37 — RV01 · Whole architecture and the "third brain"

| ID | Severity | Status | State | Finding |
|---|---|---|---|---|
| B37-A1 |  | MEASURED | open | "Third brain" names no component in the corpus. git grep returns 0 tracked hits. The phrase appears only in the Caelorynth board, where it is recorded as Mac's request ("architectural soundness for the 'third brain'"), followed … |
| B37-A2 |  | MEASURED | open | One file was loaded as two Python modules, so the package's exported enum did not match its own reports. lycheetah/core/__init__.py re-exported through a relative import, which loads 12_IMPLEMENTATIONS/core/tri_axial_checker.py … |
| B37-A3 |  | MEASURED | open | A third identity comes from sys.path.insert inside core modules. Five core modules (grey_mode, psi_consensus, seven_phase, unified_field_checker, aura_customizer) put their own directory on sys.path and import siblings by bare … |
| B37-A4 |  | MEASURED | open | The full dotted path still makes a second copy. import lycheetah.core.tri_axial_checker still loads the file under that name, because the bridge appends the canonical directory to __path__. Two tests use that form. The A2 repair … |
| B37-A5 |  | MEASURED | open | Authority boundaries. Only lycheetah/ is imported by examples/. Nothing in the package imports 34_ASSURANCE_RUNTIME/ or papers/. Those trees are research lineages, and their versions/v0.5–v0.8 import only their own siblings. The … |
| B37-A6 |  | MEASURED | open | Duplicate implementations outside 99_ARCHIVE. They are byte-identical research snapshots, not live forks: - 13 lamague_runtime files are identical across 06_RUNTIME_v0.2, 07_RUNTIME_v0.3 and the 08 operator pack; - lamague_core … |
| B37-A7 |  | MEASURED | open | Version contracts. - The package is 1.3.0. - The receipt has SCHEMA_VERSION = "0.1" and rejects other versions. - The evaluation and regression schemas carry their own constants. - The research lines carry versions in folder … |
| B37-A8 |  | DERIVED | open | pyproject.toml lists the package lycheetah.experiments, mapped to 12_IMPLEMENTATIONS/experiments, which has no __init__.py. Whether the wheel ships it as intended is UNVERIFIED, because no wheel was built. |

## [B38](BATCH38_FINDINGS_AND_LEDGER.md) — BATCH 38 — Mathematical checklist M1–M18

| ID | Severity | Status | State | Finding |
|---|---|---|---|---|
| B38-M1 |  | MEASURED + DERIVED | open | TRIAD Jacobian sign |
| B38-M2 |  | MEASURED + DERIVED | open | Generator bound |
| B38-M3 |  | not re-derived | open | Actual tracker |
| B38-M4 |  | MEASURED | open | Convexity / unitarity |
| B38-M5 |  | MEASURED | open | √n threshold |
| B38-M6 |  | MEASURED | open | Master equation |
| B38-M7 |  | not re-derived | open | Sovereignty ⇒ AURA |
| B38-M8 |  | not re-derived | open | Foundation preservation |
| B38-M9 |  | MEASURED | open | Information preservation |
| B38-M10 |  | MEASURED | open | AURA metric preservation |
| B38-M11 |  | not re-derived | open | Chrysopoeia |
| B38-M12 |  | MEASURED | open | Harmonia |
| B38-M13 |  | MEASURED + DERIVED | open | Thermodynamics |
| B38-M14 |  | not re-derived | open | AGM |
| B38-M15 |  | not re-derived | open | Incompleteness |
| B38-M16 |  | not re-derived | open | Anamnesis |
| B38-M17 |  | MEASURED | open | "11/11 verified" |
| B38-M18 |  | MEASURED | open | Novelty / normalisation |
| B38-N1 |  | M1 rescue (DERIVED, numeric witness). … | fixed in tree | M1 rescue (DERIVED, numeric witness). For S = h(C(ψ)), a fixed point of the ascent needs ∇C = 0 whenever C ≠ ½. There ∇²S = h′(C)·∇²C. For C > ½, h′ < 0, so a coherence peak gives ∇²S ⪰ 0 and DG = I − α∇²S has eigenvalues in (0, … |
| B38-N2 |  | M2 discrete form (DERIVED, sampled … | checked, holds | M2 discrete form (DERIVED, sampled witness). ‖D𝒢‖ ≤ α + β + γ‖DΨ‖ is a valid non-expansion bound for the map ψ ↦ 𝒢(ψ). It holds when ‖DAo‖ ≤ 1 and ‖DΦ↑‖ ≤ 1; the normalised ascent does not guarantee the second. It says nothing … |
| B38-N3 |  | M13 corrected law (DERIVED from the … | fixed in tree | M13 corrected law (DERIVED from the Second Law, witnessed). At constant T, W ≥ ΔF. With ΔU = 0 this gives ΔS ≥ −W/T, with equality only for reversible processes. |
| B38-N4 |  | M12 Harmonia proxy cannot discriminate … | open | M12 Harmonia proxy cannot discriminate (MEASURED). barlow_dissonance measures the log2 distance to the nearest p/q with q ≤ 12. It does no prime factorisation. |


## B39 — Close-out: areas and root files no batch had named (2026-10-23)

| ID | Severity | Status | State | Finding |
|---|---|---|---|---|
| B39-R1 | LOW | MEASURED | open | `demo.py --quick` exits 0 but tells the reader "pytest tests/ — 80 tests, all passing". The suite is 1,571 passed. A stale public number. |
| B39-R2 | MEDIUM | DERIVED | open | `generate_defense_bundle.py` front matter says D-1.0 "defends canonical body C-1.0"; the canon is C-1.1 (B33). `DEFENSE_BUNDLE.pdf` is therefore stale. It was not regenerated. |
| B39-R3 | LOW | MEASURED | open | `fpdf` is neither installed nor in `requirements.txt`, so the defense bundle cannot be rebuilt from a fresh install. The generator's docstring also names an old working directory. |
| B39-R4 | LOW | MEASURED | open | `08_INTEGRATIONS/README.md` says "Status: Active" and has no 2026-10-20 review banner, unlike `04_`, `05_` and `09_`. It wires the master equation that B17 found cannot bifurcate at Π_th. |
| B39-R5 | INFO | MEASURED | open | 8 areas (127 files) and 9 root files were never named by a batch. The close-out gave them a README-level census only. This is the residual coverage debt. |
