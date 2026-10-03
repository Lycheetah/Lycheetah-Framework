# Agent Safety Research Packet

**Public working draft v0.3 · 3 October 2026**

**Author and Framework creator:** Mackenzie Conor James Clark. Literature inspection, formalisation, and drafting assisted by Caelorynth, an AI coding assistant.

This packet turns the Lycheetah Framework's commitments into a proposed specification for permissions, evidence preservation, delegation, memory, stopping, and recovery around tool-using agents. The Translation Gate is one part of that specification. It is not a claim that general agent safety or alignment has been solved.

Read in this order:

1. [Research paper](PAPER.md) — motivation, prior art, specification, conditional propositions, limitations, and research tracks.
2. [Sovereign Sol implementation handoff](SOVEREIGN_SOL_HANDOFF.md) — one proposed simulated route and concrete acceptance evidence.
3. [Evaluation protocol](EVALUATION_PROTOCOL.md) — matched baselines, challenge families, outcome measurements, and falsification criteria.
4. [Source ledger](SOURCES.json) and [claim register](CLAIMS.json) — evidence boundaries and local provenance.
5. [Verification receipt](VERIFICATION.md) — checks actually completed for this packet.
6. [Adversarial publication review](ADVERSARIAL_REVIEW.md) — challenges, corrections, and deployment blockers found by the authoring seat.

The central distinction is between **permission to act**, **evidence supporting a decision**, and **whether the action harms someone**. A correct permission check cannot answer all three.

An [executable control simulator](simulator/README.md) now accompanies the conceptual paper and study design. Its 53 unit tests passed, and 19 self-authored scripted cases in each of two arms met their expected outcomes. [Results and limits](simulator/reports/RESULTS.md) show identical aggregate observations for the capability and conventional ACL implementations. Expected outcomes include permitted harm and already-admitted effects completing after revocation.

Two further [reproducible adversarial probes](simulator/adversarial_checks.py) expose a multi-broker accounting failure and admission-only evidence freshness. These are known deployment blockers for stronger contracts, documented rather than hidden behind passing fixture counts.

No language-model agent benchmark, participant study, real-provider experiment, production safety implementation, independent security review, or peer review has been performed. No safety improvement or priority claim is made. The author authorised public sharing as a working paper on 3 October 2026.

This packet's public source home is the [Lycheetah Framework repository](https://github.com/Lycheetah/Lycheetah-Framework), under `papers/agent-safety/`. Its fixtures require only the standard library. Six inspected Framework references already exist publicly; two unpublished background sources are identified without distributing private files or workspace locations. The related Independent No manuscript remains separate and is not included in this publication batch. A private snapshot preserves the original draft.
