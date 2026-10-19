# LYCHEETAH · Sovereign Choice Forge VIII
## Sovereignty Surface — options that remain possible when intentions change

**18 October 2026 · v0.8 · `[PROPOSAL / COMPUTED SYNTHETIC TOY]` · not deployed or ratified**

> Freedom is not the absence of connection. It is the ability to alter the connection without forfeiting one's dignity, work, or legitimate options.

Forge VII showed that chosen continuing assistance is compatible with sovereignty, and a strong conventional goal-aware baseline tied the branded policy. Forge VIII asks a harder question: **if two people use a service equally often, can their ability to leave, revise, or return nevertheless be different?** Yes—**in an authored graph where those structural possibilities are explicitly different**. That is a logical distinction and test of a proposed specification, not evidence about actual human free will.

## Findings (fictional graph, NOT a field study)

- **Eight four-week paired cases / 64 snapshots** with intentionally identical weekly session counts per pair.
- **Seven of eight pairs** have different graph-based reachability results for the requested change despite indistinguishable usage.
- **One pair is a deliberate negative control:** restriction irrelevant to the requested step does not alter the result.
- Six reported statuses: `verified`, `claimed_only`, `unknown`, `blocked`, `at_target`, `preference_unknown`. `verified` means only that a path is marked verified *inside the fictional fixture*.
- **No human sovereignty score, no AI dependency diagnosis and no machine model evaluation.**
- One changing-preference demonstration: identical use, preference changes halfway, and system affordances now diverge.
- One return-to-assistance demonstration: barring chosen renewed assistance can also be a restriction.
- Implementation correctness checked by small-graph oracle enumeration.

## Run the research

```
python src/sovereignty_surface.py > results/benchmark.json
python src/trajectory.py > results/preference_revision.json
python -m unittest discover -s tests -v
python run_verification.py
```

The last command also extracts the preserved Forge VII archive into a temporary directory and reruns the full historical chain (Forges I–VII). Historical Forge VI code requires `cryptography`; if missing, the historical test fails rather than being silently skipped. No network or external effects are executed.

Open `prototype/sovereignty_surface_lab.html` in a browser. It is an offline HTML/JavaScript interface with eight paired scenarios, adjustable desired coupling state, time budget and status of unverified/blocked transitions. Its results are derived from the same authored fixture variables. It does not contact servers or retain input.

## Directory map

| Resource | Why it exists |
|---|---|
| `src/sovereignty_surface.py` | Explicit graph and shortest-path evidence semantics |
| `src/trajectory.py` | Preference revision and choice-to-return fixtures |
| `tests/test_surface.py` | 32 local tests including exhaustive 3-edge comparison |
| `results/benchmark.json` | Reproducible paired results |
| `results/preference_revision.json` | Dynamic-preference probe |
| `prototype/sovereignty_surface_lab.html` | Offline exploratory interface |
| `docs/SOVEREIGNTY_SURFACE_CHARTER_v0.8.md` | Philosophy, mechanism, falsifiers, ethics, proposed study and references |
| `docs/RESEARCH_STATUS_AND_FAILURE_MUSEUM.md` | Claims register, limitations and negative controls |
| `lineage/FORGE_VII_COMPLETE.zip` | Previous seven forges preserved unmodified |
| `MANIFEST_SHA256.json` | Reproducible integrity hashes of packaged inputs/results |

## Research boundary and positioning

This is **not** an instrument to classify people as autonomous, free, addicted, independent or weak. A graph records hypothetical product affordances under declared cost limits; it cannot detect coercion, comprehension, actual consent, material poverty, disability or relational context on its own. Using it for those judgments would contradict Lycheetah's own AURA and MICROORCIM limits.

The formal result (that an observed session count cannot recover a hidden graph if two graphs generate the same count) is elementary information loss, not a new theorem. The algorithm is conventional Dijkstra pathfinding. Existing autonomy and HCI research precede the framework. The proposed Lycheetah contribution is to combine philosophical scope discipline, fixture-verifiable exit/return mechanics, documented limits and an eventual fair UX evaluation.

**A strong conventional product with the same functional transition rights is an equally valid solution. No incremental Lycheetah advantage has been shown.**

**Human founder/final canon:** Mackenzie Conor James Clark. Drafted collaboratively with GPT-6; no GitHub writes, approvals or external deployments made by Forge VIII.
