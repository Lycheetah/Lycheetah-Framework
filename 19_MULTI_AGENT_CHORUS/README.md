# Nine-agent Chorus — historical offline scaffold

**Creator:** Mackenzie Conor James Clark / Lycheetah Framework.  
**Original operating lineage:** Sol Protocol. **Guide reviewed:** 20 October 2026; corrected 22 October 2026 (Opus review, RV10).  
**Status:** [SCAFFOLD] Python role fixtures; live agent health and constitutional enforcement are not established.

The [full Framework review](../28_DEFENSE/FULL_FRAMEWORK_REVIEW_2026-10-20.md)
reproduced two false assurance results in the historical runner. Both were
corrected afterwards:

- `health_check()` reported every listed entry online without probing its agent.
  Nine `None` entries still produced nine online and `all_constitutional=true`.
  It now reports instantiation only, with status SCAFFOLD.
- `run_truth_audit()` gave Aurora an empty file list and returned zero findings
  plus coherence 1.0. It now reports NOT_PERFORMED.

The Opus review of 22 October 2026 (RV10) reproduced the same pattern one level
down, in the agents themselves, and corrected it in place:

- Meridian's own `health_check()` returned "CONSTITUTIONAL INTEGRITY
  MAINTAINED", `pcf_active` and `vip_routing_active` as constants. It now
  reports SCAFFOLD and NOT_MEASURED, and counts the named hard guardrails that
  have any check: 2 of 9.
- PCF read a missing flag as compliant, so an output that declared nothing
  about rights claims, hidden constraints, reversibility or auditability was
  approved. A missing flag now fails, and an approval names what was not checked.
- Albedo, Solstice, Healer, Beacon and parts of Protector, Cascade and Harmonia
  returned fixed `True` verdicts for any input: structure validated, sovereignty
  intact, convergence guaranteed, frequencies converging. They now return
  `None` with status SCAFFOLD_NOT_COMPUTED.
- Protector passed an action that declared an override when it also declared
  consent, and passed an action that declared nothing. Both now fail.
- Harmonia compared the raw frequency ratio with a grid in steps of 0.5, so a
  semitone scored 0.94 and a tritone 0.92, both "harmonic". It now measures cents
  from the Pythagorean consonances (1, 4/3, 3/2, 2, 3, 4).
- Cascade reported infinite truth pressure for S = 0 and also for S = -1. It
  now refuses any strain that is not a finite positive number.
- Aurora's scan returned a CRITICAL contradiction attributed to
  `00_Sovereign_Index.md:line 42`, for words that file does not contain, whatever
  files it was given. A scan with files now raises NotImplementedError; the demo
  shows one example marked ILLUSTRATIVE that names no real file.
- A decision log or coherence buffer that was not valid JSON read as empty, and
  the next decision overwrote the log. Both now raise and leave the file as it
  was, and the log is written to a temporary file and swapped in.
- Every role script printed "online" or "Operational". They now print
  "constructed" and say no behaviour was probed.

The former all-green status matrix is therefore withdrawn as a current health
claim. Running the existing command is not an independent constitutional test.
The source is preserved so its architecture and limitations remain inspectable.

## What the code contains

| Role | Source |
|---|---|
| Sol Meridian — declared checks and routing | [sol_meridian.py](sol_meridian.py) |
| Aurora — contradiction/claim heuristics | [aurora_investigator.py](aurora_investigator.py) |
| Albedo, Solstice, Protector, Healer, Beacon, Cascade, Harmonia | The runner imports these from [remaining_agents.py](remaining_agents.py); individual role files also remain. |
| Coordination; reports instantiation, not health | [run_chorus.py](run_chorus.py) |
| Earlier design contract | [AGENTS_MANIFEST.md](AGENTS_MANIFEST.md) — read as the historical architecture, not a live deployment receipt |

Meridian's checks read declared flags and heuristic fields. Those declarations
do not independently establish that an output preserves agency, tells the truth
or satisfies an ethical predicate. Python classes are not evidence of nine
connected model providers or nine independent reviewers.

## Inspect or reproduce

The historical commands are `python3 run_chorus.py --mode=health` and
`python3 run_chorus.py --mode=audit`. Both report SCAFFOLD or
NOT_PERFORMED rather than a verdict. Constructors can create `.agent_state` and write local state; use a
scratch copy for an archival reproduction.

The previously cited `.github/workflows/multi-agent-chorus.yml` is MISSING: it does not exist.
There is no verified Chorus CI or production deployment supplied here.

## A successor would need

Actual reachability and dependency probes; explicit input and scanned-item
counts; fail-visible status when checks do not run; evidence for each asserted
constraint; and deliberate separation of provider output, declared compliance
and independently observed behaviour. Test a known broken agent and a nonempty
contradictory corpus before trusting a green health/audit result.

For maintained local control mechanisms, use the [Assurance Runtime](../34_ASSURANCE_RUNTIME/README.md)
and the [reviewed consensus boundary](../lycheetah/consensus/arena.py).
