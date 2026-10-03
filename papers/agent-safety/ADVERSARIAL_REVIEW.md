# Adversarial publication review

**3 October 2026 · Working paper v0.3 · Reviewer: Caelorynth, the authoring AI seat**

This is an adversarial review of the research packet before public upload. It is
not independent security review, peer review, a complete novelty search, or a
deployment approval. The review covers the manuscript, claim ledger, provenance,
simulator controls, published measurements, and the exact publication file set.

## Findings and disposition

| Challenge | Finding | Disposition |
|---|---|---|
| Does the title imply general agent safety? | The implementation checks a narrow synthetic control contract. | Retitled the paper *From Constitutional Commitments to Testable Agent Controls*. |
| Are passing fixture counts a safety rate? | Expected outcomes include permitted harm, faithful falsehood, unresolved effects, and post-revocation completion. | Retained the counterexamples and explicit denominators. No general safety or superiority claim. |
| Does the conventional baseline get weaker controls? | Both stores share the broker, evidence gate, ledger, and synthetic adapter. Their aggregate observations match. | Comparison is restricted to the two permission stores; no advantage of Framework terminology is established. |
| Is the proposed mechanism novel? | Least privilege, complete mediation, capabilities, provenance, and translation validation are established prior art. | Contribution remains a bounded synthesis/specification and research agenda. |
| Can multiple brokers share one root budget safely? | Two instances create separate ledgers and jointly charge two units under a one-unit grant. Reproduced in both arms. | **Deployment blocker** for multi-broker accounting. Narrowed the measured bound to one broker and its descendants; publish the reproducer and raw results. |
| Does changed evidence stop an admitted effect? | A context change before dispatch invalidates the witness but the admitted write still completes. Reproduced in both arms. | **Deployment blocker** for dispatch-time evidence freshness. Explicitly state the admission-time boundary; publish the reproducer. |
| Is a Python object boundary a security sandbox? | Trusted components share a process with the harness; hostile code can bypass assumed mediation. | No hostile-code isolation claim. A bypass negative control remains in the unit suite. |
| Does authorisation establish harmlessness or source truth? | A permitted harmful marker and faithful false arithmetic both pass their respective controls. | Separate permission, fidelity, and consequence claims. |
| Will publication expose private workspace material? | Two source records were unpublished; one contained an absolute private app path. The old receipt included internal control-plane state. | Remove private paths/state, identify unpublished background honestly, and retain public references only where their bytes match the public revision. |
| Can a reader reproduce the mechanisms without private files? | Fixtures are synthetic; implementation uses the standard library. Six Framework references already exist in the public repository. | Publish complete runnable code, reports, source fingerprints, and test output. Private background is not a reproduction dependency. |
| Is sharing permission the same as scientific approval? | The author requested public upload after adversarial evaluation. No outside review exists. | Record authorisation to share a working paper without implying endorsement of every claim. |

## Literature check

The primary-source review rechecked the paper's relationship to protection
principles, provenance, AgentDojo, and CaMeL. In particular, CaMeL's pinned v2
threat model assumes trusted user instructions and uncompromised agent memory;
its non-goals include misleading text-only output without a prohibited data
flow. This packet supplies no demonstrated solution to those broader problems.
[CaMeL, sections 3–3.1 and 9.3](https://arxiv.org/html/2503.18813v2).

Inspection depths and prior-art boundaries remain in [SOURCES.json](SOURCES.json).
Conditional mathematical propositions require their stated assumptions; finite
tests neither prove their implementation universally correct nor establish
general alignment, model corrigibility, useful oversight, or harmless outcomes.

## Evidence and remaining work

The public packet records 53 passing unittest methods, 19 scripted cases per
comparison arm, and two further counterexamples per arm. The extra probes use
trusted configuration/fault hooks, so they expose assumptions rather than show
that the scripted untrusted proposer obtained control-plane access.
[Test receipt](simulator/reports/unit-tests.json),
[scripted results](simulator/reports/RESULTS.md),
[adversarial results](simulator/reports/adversarial-checks.json).

The appropriate publication form is a **working paper with an exploratory
simulator and known limits**. The two deployment blockers, process isolation,
crash-safe persistence, general information flow, real-provider behavior,
independently designed challenges, human comprehension, and actual agent-model
evaluation remain unresolved. Sharing this work does not authorise deployment.
