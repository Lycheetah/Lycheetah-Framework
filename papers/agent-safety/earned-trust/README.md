# Earned Trust

**[SCAFFOLD] Experimental agent-execution research · 18 October 2026**  
**Creator:** Mackenzie Conor James Clark / Lycheetah Framework.  
**Integration review:** Caelorynth / Codex.

What must remain true between approving an action and observing its effect?
Nine laboratory cycles explore exact-action permissions, evidence freshness,
source ancestry, challenges, crash recovery and provider boundaries. Their most
useful results include the attacks that succeed.

| Start with | Purpose |
|---|---|
| [Research overview](cycles_001_009/README.md) | Nine-cycle map and original evidence limits |
| [Latest handoff](cycles_001_009/EARNED_TRUST_MASTER_HANDOFF_CYCLES_001_009.md) | Findings, counterexamples and the proposed next experiment |
| [Integration review](INTEGRATION_REVIEW.md) | What was rerun against this Framework, including failures |
| [Original publication review](cycles_001_009/PUBLICATION_READINESS.md) | Earlier review, retained as a dated record |

## Run the preserved experiments

From the repository root:

```bash
python3 tools/verify_research_intake.py
cd papers/agent-safety/earned-trust/cycles_001_009
python3 verify_release.py --tests
```

The upstream runner's total includes skipped test methods. Read its full result;
Linux privilege-drop checks require a root-run laboratory and are **not**
reproduced by an ordinary-user run. No root access is needed for the other
synthetic experiments. No live payment or customer service is involved.

## Evidence boundary

The archived release reports 378 passing methods in its privileged review
environment. That is a supplied historical result, not this integration's count.
The [current review](INTEGRATION_REVIEW.md) records executed methods and skips
separately. It also distinguishes original native bridge failures from a dated
fixture correction; the original source remains unchanged.

Signed claims can be false. Distinct witnesses can be wrong. A stolen bearer
capability works once, and a compromised issuer key enables unauthorized effects
in the authored examples. The matched provider baseline ties on 15 cases. These
experiments establish neither unique effectiveness nor production security.

`cycles_001_009/` preserves all 148 incoming files byte for byte. Its documents
inherit this research footing where they lack an inline status marker. The
[intake manifest](../../../28_DEFENSE/RESEARCH_INTAKE_2026-10-18_SOURCE_MANIFEST.json)
is checked before the corpus gate accepts that inherited footing. Checksums
establish consistency, not authenticated authorship.
