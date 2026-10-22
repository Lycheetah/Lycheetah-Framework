# Opus review — Batch 9: findings register and coverage ledger

Workstream: **RV10, Chorus false assurance.** The checklist carried it as
"Reproduced open." Branch `review/full-framework-2026-10-20`, HEAD `d7ae0ad`,
working tree uncommitted. Nothing was committed or pushed.

Decision: RV10 offers two exits: "design and demonstrate a real implementation or
keep the entire path explicitly scaffolded." This batch takes the second. A real
chorus needs message passing, content inspection and an audit corpus. That makes
it a design decision for Mac, not a review repair (see the open decision below).
What this batch changed: every place that returned a verdict it never computed now
says so. That covers the hub, the role classes, Aurora, the menu, the role scripts
and the four documents that called the chorus working.

The 20 October review had already corrected the runner (`run_chorus.py`
`health_check` and `run_truth_audit`). This batch found the same pattern one level
down, inside the agents the runner holds.

Method: `repro_batch9.py <repository root>` copies `19_MULTI_AGENT_CHORUS/` into a
temporary folder and probes the copy, so `.agent_state` is created there and not
in the repository. The probe ran against the HEAD export and the working tree.
New tests were copied into the HEAD export, where they must fail, and must pass on
the tree.

Read in full at HEAD:

- `sol_meridian.py` (409 lines)
- `remaining_agents.py` (373)
- `aurora_investigator.py` (309)
- `run_chorus.py` (290)
- the seven 16-line role scripts
- `README.md` (53)
- `AGENTS_MANIFEST.md` (320)
- `tests/test_chorus_honesty.py`
- the chorus cases in `tests/test_threads_fixes.py`

Read in part:

- the chorus section and table row of `14_MYSTERY_SCHOOL/THE_AI_ARCHITECTS_DOOR.md`
- `02_AURA_L3/THE_FOUR_PRINCIPLES.md:425`
- `02_AURA_L3/LAWS_COMPLETE.md:539`

## Findings register

| ID | Severity | Status | Where |
|----|----------|--------|-------|
| K1 | Medium (a constitutional verdict returned as a constant) | FIXED in working tree | `SolMeridian.health_check` |
| K2 | Medium (a missing flag read as compliant) | FIXED in working tree | `check_hard_guardrails`, `check_seven_invariants`, `apply_pcf` |
| K3 | Medium (15 methods returned 24 fixed `True` fields; an empty structure validated) | FIXED in working tree | `remaining_agents.py` |
| K4 | Medium (consent outranked a declared override; declaring nothing passed) | FIXED in working tree | `ProtectorGuardian` |
| K5 | Low (semitone and tritone rated harmonic) | FIXED in working tree | `HarmoniaResonator.measure_consonance` |
| K6 | Low (Π infinite for S ≤ 0) | FIXED in working tree | `CascadeArchitect.measure_truth_pressure` |
| K7 | Medium (a fabricated CRITICAL finding attributed to a real file, for any input) | FIXED in working tree | `AuroraInvestigator.scan_for_contradictions` |
| K8 | Medium (data loss: a corrupt log read as empty, then overwritten) | FIXED in working tree | `read_coherence_buffer`, `log_decision` |
| K9 | Low (the menu and 8 scripts announced health nobody probed) | FIXED in working tree | `run_chorus.py`, role scripts |
| D1 | Medium (published status false at HEAD) | CORRECTED, March text kept and marked | `AGENTS_MANIFEST.md`, `README.md` |
| D2 | Medium (chorus described as working outside its folder) | CORRECTED | `THE_AI_ARCHITECTS_DOOR.md:272,286,288,319`, `THE_FOUR_PRINCIPLES.md:425`, `LAWS_COMPLETE.md:539` |
| D3 | — | LEFT: unchecked roadmap item and archive | `THE_GOLDEN_STONE.md:499`, `99_ARCHIVE/` |
| L1 | Low | OPEN, not fixed | `aurora_investigator.py:126,142`: `line_number=0` placeholders in `detect_false_claims`, whose line-134 pattern also lists `proves` twice |
| L2 | Low | OPEN, not fixed | `aurora_investigator.py:210`: `pressure_applied: "MAXIMUM"` is a constant |
| B1 | Boundary | UNCHANGED, now stated everywhere | no agent passes messages, reads or writes the coherence buffer, or inspects content; PCF reads flags an output declares about itself |

K2 detail: at HEAD every guardrail and invariant check used `.get` with a passing
default. An output that declared only its trinity and signature flags was
approved. It said nothing about rights claims, hidden constraints, reversibility,
auditability, history or care. A missing flag now fails as `undeclared: <flag>`.
An approval states that every flag was self-reported. It also names the 7 of 9
hard guardrails with no check.

K7 detail: `00_Sovereign_Index.md` exists at the repository root. It does not
contain the "100% validation" wording the fabricated finding attributed to its
line 42.

### Probe results

| Probe | Input | HEAD | Tree |
|-------|-------|------|------|
| R1 | `SolMeridian().health_check()` | "✅ CONSTITUTIONAL INTEGRITY MAINTAINED", `pcf_active` True, `vip_routing_active` True | NOT_MEASURED, both None |
| R2 | PCF, trinity and signature flags only | approved | refused |
| R2c | PCF, declares `claims_framework_rights` (control) | refused | refused |
| R3 | agency: consent and override declared | (True, "Agency preserved") | (False, "Agency violated — VIP required") |
| R3 | agency: nothing declared | (True, "Agency intact") | False |
| R3 | reversibility: nothing declared | (True, "Action can be undone") | False |
| R4 | 15 role methods with no implementation | 24 fixed `True` fields | 0 |
| R4 | `AlbedoSynthesizer().validate_structure({})` | (True, "Structure is sound and internally consistent") | (False, "Not validated: … [SCAFFOLD]") |
| R5 | Harmonia, 440 Hz against a semitone | consonance 0.944, harmonic | 0.5, not harmonic |
| R5 | Harmonia, 440 Hz against a tritone | 0.921, harmonic | 0.495, not harmonic |
| R5c | Harmonia, just fifth (control) | 1.0, harmonic | 1.0, harmonic |
| R6 | Cascade Π at S = 0 and S = -1 | inf, inf | ValueError, ValueError |
| R7 | Aurora scan of `README.md` | CRITICAL at `00_Sovereign_Index.md:line 42` | NotImplementedError; no file read |
| R7 | Aurora example (empty list) | the same CRITICAL finding, against a real file | ILLUSTRATIVE, `ILLUSTRATIVE/claimed_status.md` does not exist |
| R8 | `log_decision` over the log `[{"kept": 1}, ` | returned; log now holds only the new entry | ValueError; log unchanged |
| R9 | `read_coherence_buffer` over `{` | `[]` | ValueError |
| R10 | supervised menu, items 3, 4, 5 | integrity verdict, `"pcf_active": true`, "would be displayed" | none of the three |
| R11 | 8 role scripts run as `__main__` | 8 of 8 print "online" or "Operational" | 0 of 8 |

### Witness

- `tests/test_chorus_scaffold_honesty.py`: 55 cases. In the HEAD export, 44 fail
  and 11 pass. The 11 are the benign controls:
  - 2 declared violations
  - 1 full declaration
  - 3 Protector controls
  - the just fifth, octave and tempered fifth
  - 1 defined Cascade strain
  - 1 valid log append
- On the tree, the chorus tests (`test_chorus_scaffold_honesty.py`,
  `test_chorus_honesty.py`, `test_threads_fixes.py`) give 80 passed.
- Full suite on the tree: 1354 passed, 1 skipped, 1 xfailed (was 1299 passed;
  +55, exactly the new file).

## Files changed

- `19_MULTI_AGENT_CHORUS/sol_meridian.py` (K1, K2, K8)
- `19_MULTI_AGENT_CHORUS/remaining_agents.py` (K3 to K6, K9)
- the seven role scripts `albedo_synthesizer.py`, `solstice_illuminator.py`,
  `protector_guardian.py`, `healer_transmuter.py`, `beacon_reflector.py`,
  `cascade_architect.py`, `harmonia_resonator.py` (K9: one print line each)
- `19_MULTI_AGENT_CHORUS/aurora_investigator.py` (K7)
- `19_MULTI_AGENT_CHORUS/run_chorus.py` (K9: menu items 1 to 5, the real
  decision log, `test_agent_communication` wording, the `--help` epilog)
- `19_MULTI_AGENT_CHORUS/README.md`, `AGENTS_MANIFEST.md` (D1)
- `14_MYSTERY_SCHOOL/THE_AI_ARCHITECTS_DOOR.md`, `02_AURA_L3/THE_FOUR_PRINCIPLES.md`,
  `02_AURA_L3/LAWS_COMPLETE.md` (D2)
- `tests/test_chorus_scaffold_honesty.py` (new)
- `CHANGELOG.md`: the "Multi-Agent Chorus" group
- `BATCH8_FINDINGS_AND_LEDGER.md`: one class name corrected (`CompletionResult`
  to `HandoffResult`)
- `FOR-REVIEW/2026-10-22_OPUS_REVIEW/repro_batch9.py` and this ledger

## Coverage against the RV10 checklist item

| RV10 asks for | Covered by |
|---------------|------------|
| Trace real agent invocation | B1, K3, K9: the runner constructs nine objects; no agent invokes another |
| Health probes | K1 here; the runner's own probe was corrected on 20 October |
| Audit inputs | K7: Aurora reads no file, and a scan with files now refuses |
| A real implementation, or the entire path explicitly scaffolded | scaffold, through code, menu, scripts and four documents |
| "A healthy-looking fixture cannot establish operational assurance" | K1, K9, D1, D2, held by 55 tests |

Not covered:

- No real implementation was designed. That is the open decision below.
- Only the supervised menu was driven end to end. The other `--mode` values were
  read in source, not run.
- L1 and L2 remain open.

## Open decision for Mac

Build a real chorus, or keep it as a labelled design sketch? Sol's stance is to
keep the sketch (DERIVED). The Framework's live enforcement path is the
`lycheetah/` package: the sovereign harness, consensus and the guarded handoff. A
second constitutional engine inside a demo folder would be a parallel
implementation of the same law. If the chorus is revived, it should be an
adapter: nine role prompts whose outputs pass through the harness. It should not
be new verdict logic.

Next workstream: RV11, the frozen policy-evolution gate (reproduce, stage a patch,
do not edit).
