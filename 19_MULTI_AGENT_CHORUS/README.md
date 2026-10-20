# Nine-agent Chorus — historical offline scaffold

**Creator:** Mackenzie Conor James Clark / Lycheetah Framework.  
**Original operating lineage:** Sol Protocol. **Guide reviewed:** 20 October 2026.  
**Status:** [SCAFFOLD] Python role fixtures; live agent health and constitutional enforcement are not established.

The [full Framework review](../28_DEFENSE/FULL_FRAMEWORK_REVIEW_2026-10-20.md)
reproduced two false assurance results in the historical runner:

- `health_check()` reports every listed entry online without probing its agent.
  Nine `None` entries still produce nine online and `all_constitutional=true`.
- `run_truth_audit()` gives Aurora an empty file list and returns zero findings
  plus coherence 1.0. No corpus audit is performed by that result.

The former all-green status matrix is therefore withdrawn as a current health
claim. Running the existing command is not an independent constitutional test.
The source is preserved so its architecture and limitations remain inspectable.

## What the code contains

| Role | Source |
|---|---|
| Sol Meridian — declared checks and routing | [sol_meridian.py](sol_meridian.py) |
| Aurora — contradiction/claim heuristics | [aurora_investigator.py](aurora_investigator.py) |
| Albedo, Solstice, Protector, Healer, Beacon, Cascade, Harmonia | The runner imports these from [remaining_agents.py](remaining_agents.py); individual role files also remain. |
| Coordination and canned status examples | [run_chorus.py](run_chorus.py) |
| Earlier design contract | [AGENTS_MANIFEST.md](AGENTS_MANIFEST.md) — read as the historical architecture, not a live deployment receipt |

Meridian's checks read declared flags and heuristic fields. Those declarations
do not independently establish that an output preserves agency, tells the truth
or satisfies an ethical predicate. Python classes are not evidence of nine
connected model providers or nine independent reviewers.

## Inspect or reproduce

The historical commands are `python3 run_chorus.py --mode=health` and
`python3 run_chorus.py --mode=audit`. Their existing outputs have the limitations
above. Constructors can create `.agent_state` and write local state; use a
scratch copy for an archival reproduction.

The previously cited `.github/workflows/multi-agent-chorus.yml` does not exist.
There is no verified Chorus CI or production deployment supplied here.

## A successor would need

Actual reachability and dependency probes; explicit input and scanned-item
counts; fail-visible status when checks do not run; evidence for each asserted
constraint; and deliberate separation of provider output, declared compliance
and independently observed behaviour. Test a known broken agent and a nonempty
contradictory corpus before trusting a green health/audit result.

For maintained local control mechanisms, use the [Assurance Runtime](../34_ASSURANCE_RUNTIME/README.md)
and the [reviewed consensus boundary](../lycheetah/consensus/arena.py).
