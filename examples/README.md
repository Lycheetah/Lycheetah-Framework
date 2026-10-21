# Examples — choose one instrument

**Guide updated:** 21 October 2026. These are local demonstrations and maintained
website build sources, with different evidence and deployment states.

Run Python examples from the repository root after the
[source installation](../lycheetah/README.md). Read a script before running it;
its scenario and fixtures define what its result can establish.

| Example | What to inspect |
|---|---|
| [Meaning handover](meaning_handover/README.md) | Goal, uncertainty, permission and recovery records; command-line comparisons, browser preview and a proposed user trial. |
| [Earned Light reading site](earned_light_reading/README.md) | Maintained builder for the [live public reader](https://lycheetah-earned-light.banduabusiness.chatgpt.site); canonical story manuscripts remain in the collection. |
| [Action guard](action_guard_demo.py) | Constructed policy scenarios, a local Unix diagnostic and simulated migration/timeout outcomes; approver IDs are declared metadata. |
| [Guarded handoff risk](guarded_handoff_risk_demo.py) | Create one declared local file, reject altered risk/action and replay, then optionally export and verify an inspectable audit bundle. |
| [Sovereign harness](sovereign_harness_demo.py) | Permission and action checks within a local constructed scenario. |
| [Compaction shield](compaction_shield_demo.py) | One exact record round-trip and manually changed copies; the critical projection excludes risk, evidence, horizon and yield and grants no permission. |
| [Consensus arena](consensus_arena_demo.py) | Constructed multi-agent agreement/recovery scenarios. |
| [Assurance inputs](assurance/) | Example policy/evidence records for the runtime. |

## Try one local action and inspect its record

The guarded handoff example needs no account, API key, model or provider call.
It uses synthetic numerical proposals, declared approval metadata and a trusted
fixed callback to create one file. The default run discards its temporary
workspace. To retain the artifact and audit bundle, choose a **new directory**;
export refuses an existing destination and does not overwrite it.

From the repository root after source installation:

```sh
python3 examples/guarded_handoff_risk_demo.py
python3 examples/guarded_handoff_risk_demo.py --export ./my-handoff-demo
python3 examples/guarded_handoff_risk_demo.py --verify ./my-handoff-demo
```

Read the exported records alongside the script's observed file bytes/hash and
executor-call count. Verification checks the bundle's declared relationships;
it does not authenticate a human approver or independently witness execution.
The callback is trusted code, not a sandbox for arbitrary actions.

The export prints `manifest_sha256`. Retain that digest separately and pass it
with `--expected-digest` when verifying to pin the bundle's bytes. Without a
separately retained digest, `SELF_CONSISTENT` means its included records agree;
it cannot detect replacement of the whole bundle. The export contains no private
checkpoint keys. Exit codes are 0 for a consistent bundle, 1 for failed
verification and 2 for invalid usage or an export error.

## Compare a handover record

The [meaning-handover comparator](meaning_handover/README.md) compares all 17
declared fields and reports exact changes. Use it when risk, evidence, review
timing or the next step matters: these can change while the codec's critical
hash still matches. Record equality does not establish truth or permission.

Other entry points:

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
