# EARNED LIGHT: FORGES I–III — COMPLETE RESEARCH HANDOFF

**Maintainer/workstream:** Lycheetah · Earned Light Layer 0 · EAC Research  
**Compiled:** 18 October 2026  
**Status:** Tested local **prototype**, not production, not GitHub-integrated.

## Reading order

1. `Earned_Light_Research_Pass_01.md` — original normative proposition, falsifiable hypotheses and initial design.
2. `Forge_02/RESEARCH_PASS_02.md` — signed grant and trusted field provenance, 43 author-authored synthetic scenarios, known root failures.
3. `Forge_03/RESEARCH_PASS_03.md` — human reconfirmation protocol and first local experiment.
4. `Forge_03/CLAIMS_AND_FAILURES.md` — all negative findings preserved.
5. `Forge_03/THREAT_MODEL.md` — explicit trust boundaries and remaining holes.

## Reproducing the new work

```sh
cd Forge_03
python -m pip install cryptography pytest
sh run_checks.sh
```

The Forge III bundle retains copies of the core Forge II dependencies to enable stand-alone tests. Tested with `76 passed` and a repeat of the original `43` cases. The simulated human permitted *exactly two pre-selected, legitimate* exception cases. The tests do not use real users, providers, or trusted identity systems.

## The change

- **Forge II:** Enforce signed grants and source attestations; 8/10 benign completion, 2/33 unauthorized accepted in the pre-existing synthetic cases.
- **Forge III:** Add signed, one-use human-*initiated* review and signed, exact-action approval. With two scripted trusted simulated human decisions, 10/10 benign completion, still 2/33 unauthorized accepted. Prompt creation gated by separate initiation: 2 prompts initiated instead of 11 proposed by the earlier automatic-challenge design.

**No general security efficacy statistics may be inferred.** The lingering 2 unauthorized successes are signed trust-root failures. A conventional exact-action human approval flow may be safer and should be implemented as a comparator before any superiority claim. No actual provider effects or GitHub commits were performed.

## Research slogan

> A capable agent may identify a path. Only legitimate human authority may authorize the crossing.
