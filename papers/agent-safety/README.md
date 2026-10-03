# Agent Safety Research Packet

**Working draft v0.4 · 3 October 2026**

**Author and Framework creator:** Mackenzie Conor James Clark. Literature inspection, formalisation, and drafting assisted by Caelorynth, an AI coding assistant.

This packet turns the Lycheetah Framework's commitments into a proposed specification for permissions, evidence preservation, delegation, memory, stopping, and recovery around tool-using agents. The Translation Gate is one part of that specification. It is not a claim that general agent safety or alignment has been solved.

Read in this order:

1. [Research paper](PAPER.md) — motivation, prior art, specification, conditional propositions, limitations, and research tracks.
2. [Sovereign Sol implementation handoff](SOVEREIGN_SOL_HANDOFF.md) — one proposed simulated route and concrete acceptance evidence.
3. [Evaluation protocol](EVALUATION_PROTOCOL.md) — matched baselines, challenge families, outcome measurements, and falsification criteria.
4. [Source ledger](SOURCES.json) and [claim register](CLAIMS.json) — evidence boundaries and local provenance.
5. [Verification receipt](VERIFICATION.md) — checks actually completed for this packet.
6. [Adversarial publication review](ADVERSARIAL_REVIEW.md) — challenges, corrections, and deployment blockers found by the authoring seat.
7. [Shared accounting repair](BUDGET_REPAIR.md) and [changes](CHANGELOG.md) — the bounded implementation correction and its remaining limits.

The central distinction is between **permission to act**, **evidence supporting a decision**, and **whether the action harms someone**. A correct permission check cannot answer all three.

An [executable control simulator](simulator/README.md) accompanies the conceptual paper and study design. Its original v0.3 run passed 53 unit methods, and 19 self-authored scripted cases per arm met their expected outcomes. The current repair passes 46 focused broker/authority/accounting methods and the same 19 scripted cases per arm. [Repair results and limits](BUDGET_REPAIR.md) show no observed aggregate difference between the capability and conventional ACL implementations. Expected outcomes include permitted harm and already-admitted effects completing after revocation.

The original probes exposed multi-broker accounting and admission-only freshness gaps. The [current probes](simulator/adversarial_checks.py) verify that brokers using one live authority now share the allowance; the freshness counterexample still reproduces. Distributed and restart-safe accounting remain outside the repair scope.

No language-model agent benchmark, participant study, real-provider experiment, production safety implementation, independent security review, or peer review has been performed. No safety improvement or priority claim is made. The author authorised public sharing as a working paper on 3 October 2026.

This packet's public source home is the [Lycheetah Framework repository](https://github.com/Lycheetah/Lycheetah-Framework), under `papers/agent-safety/`. Its fixtures require only the standard library. Six inspected Framework references already exist publicly; two unpublished background sources are identified without distributing private files or workspace locations. The related Independent No manuscript remains separate and is not included in this publication batch. A private snapshot preserves the original draft.
