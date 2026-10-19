# Examples — choose one instrument

**Guide updated:** 19 October 2026. These are local demonstrations and maintained
website build sources, with different evidence and deployment states.

Run Python examples from the repository root after the
[source installation](../lycheetah/README.md). Read a script before running it;
its scenario and fixtures define what its result can establish.

| Example | What to inspect |
|---|---|
| [Meaning handover](meaning_handover/README.md) | Goal, uncertainty, permission and recovery records; command-line comparisons, browser preview and a proposed user trial. |
| [Earned Light reading site](earned_light_reading/README.md) | Maintained builder for the [live public reader](https://lycheetah-earned-light.banduabusiness.chatgpt.site); canonical story manuscripts remain in the collection. |
| [Action guard](action_guard_demo.py) | A bounded action-policy scenario and its decisions. |
| [Guarded handoff risk](guarded_handoff_risk_demo.py) | Transfer, admission and explicit risk boundaries. |
| [Sovereign harness](sovereign_harness_demo.py) | Permission and action checks within a local constructed scenario. |
| [Compaction shield](compaction_shield_demo.py) | Changes to declared records under compaction. |
| [Consensus arena](consensus_arena_demo.py) | Constructed multi-agent agreement/recovery scenarios. |
| [Assurance inputs](assurance/) | Example policy/evidence records for the runtime. |

For example:

```sh
python3 examples/meaning_handover/demo.py --help
python3 examples/action_guard_demo.py
```

A runnable example establishes behaviour on its supplied inputs. It does not
establish independent user benefit, clinical suitability, production deployment
or a general AI-safety guarantee. A public website has its own deployment receipt;
source being present does not make every example a hosted service.

[Runtime contract](../34_ASSURANCE_RUNTIME/README.md) ·
[Research packets](../papers/README.md) · [Test scope](../tests/README.md) ·
[Repository map](../00_Sovereign_Index.md).

Created by Mackenzie Conor James Clark / Lycheetah Framework.
