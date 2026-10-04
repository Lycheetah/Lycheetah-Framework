# Language, memory and learning tools

**Status: PROPOSED product and game briefs; no prototype implied.**

These tools help people keep distinctions intact across time and translation. They must show what was preserved, what changed and what is still unknown.

[Catalogue home](README.md) · [Build contract](07_BUILD_CONTRACT_AND_SEQUENCE.md)

## LYC-B009 · Decision Record Workbench

**Form:** tool · **Build status:** PROPOSED

Build a structured handoff that states intent, authority, constraints and open questions.

- **Source to inspect:** [03_LAMAGUE_L1/](../../03_LAMAGUE_L1/). This is a lineage pointer, not a statement that the proposed product already exists.
- **Inputs:** An explicit schema, user-authored fields and a vocabulary agreed by the receiving team.
- **Interaction:** Fill a record → inspect missing fields → hand it to another person → let them paraphrase it → compare meaning and amend the record.
- **Artifact:** A machine-readable record paired with a plain-language rendering.
- **First build:** Ten explicit fields and three ambiguous examples; no automatic action execution.
- **Acceptance:** Presence checks are labelled as presence checks; a filled but contradictory record can still be flagged by a human; the recipient’s understanding is recorded separately.
- **Limits:** Structured completeness is not semantic correctness, authority authenticity or reliable translation between arbitrary agents.

## LYC-B010 · Protected Codec Workbench

**Form:** tool · **Build status:** PROPOSED

See what an exact codec preserves and what its protection boundary excludes.

- **Source to inspect:** [03_LAMAGUE_L1/22_REVERSIBLE_COMPRESSION_v1.0/src/lamague_codec.py](../../03_LAMAGUE_L1/22_REVERSIBLE_COMPRESSION_v1.0/src/lamague_codec.py). This is a lineage pointer, not a statement that the proposed product already exists.
- **Inputs:** Supported structured values, a codec version and named protected fields.
- **Interaction:** Encode → inspect size and representation → decode → compare exact protected fields → inject a corruption and see the failure.
- **Artifact:** A round-trip report with original bytes, decoded values and rejected cases.
- **First build:** A small local interface over the supported grammar, with explicit size overhead.
- **Acceptance:** Every claimed supported round trip is exact; unsupported input is refused; compression ratios count framing and metadata; corruption is not presented as a successful decode.
- **Limits:** An exact structured codec is not lossless natural-language summarisation or evidence of universal semantic compression.

## LYC-B011 · Versioned Notebook

**Form:** tool · **Build status:** PROPOSED

Let someone reconstruct a thought without pretending every saved summary is the original.

- **Source to inspect:** [21_MEMORIA/](../../21_MEMORIA/). This is a lineage pointer, not a statement that the proposed product already exists.
- **Inputs:** Private notes, dated revisions, source attachments and explicit derived summaries.
- **Interaction:** Write → revise → branch an interpretation → compare history → restore a prior version. A summary points back to the material it omitted.
- **Artifact:** An inspectable private notebook archive and revision graph.
- **First build:** One notebook with original/revision/summary relationships and a local export.
- **Acceptance:** The original survives every summarisation; sources remain attached after restore; stale summaries are marked; deletion and export are demonstrable.
- **Limits:** Stored continuity does not establish autobiographical identity, consciousness or faithful retrieval by an AI model.

## LYC-B012 · Negotiation Board

**Form:** tool · **Build status:** PROPOSED

Explore incompatible preferences and see whose requirements a proposed agreement leaves unmet.

- **Source to inspect:** [32_TIANXIA/](../../32_TIANXIA/). This is a lineage pointer, not a statement that the proposed product already exists.
- **Inputs:** Synthetic stakeholder preferences, explicit non-negotiables, resource constraints and a chosen aggregation rule.
- **Interaction:** Propose an allocation → each simulated party objects or accepts → change the rule → inspect distribution and unresolved conflict.
- **Artifact:** A decision worksheet naming beneficiaries, burdens and unresolved objections.
- **First build:** Three fictional parties, two resources and two transparent aggregation rules.
- **Acceptance:** The interface exposes a minority losing under a majority rule; a hard constraint cannot disappear through averaging; participants can reject the proposed agreement.
- **Limits:** Tianxia/CHORA provides an interpretive design lens. Simulated agreement is not political legitimacy, cultural equivalence or empirical governance success.

## LYC-B013 · Modelcraft Experiment Bench

**Form:** tool · **Build status:** PROPOSED

Compare two ways of asking for the same task while keeping judgement, cost and failures visible.

- **Source to inspect:** [14_MYSTERY_SCHOOL/MODELCRAFT/README.md](../../14_MYSTERY_SCHOOL/MODELCRAFT/README.md). This is a lineage pointer, not a statement that the proposed product already exists.
- **Inputs:** A task, two prompt conditions, a fixed rubric, chosen model and user-entered outputs.
- **Interaction:** State the rubric first → perform both conditions → score without changing the task → record cost → inspect ties and failures → decide whether to keep the technique.
- **Artifact:** A private experiment receipt with conditions, outputs, rubric, caveats and reproduction notes.
- **First build:** Use the existing first context-pack experiment manually, with no provider integration.
- **Acceptance:** A tie is allowed; missing costs remain unknown; a receipt cannot promote itself to externally validated; ranking does not use engagement or inferred identity.
- **Limits:** All 24 technique families remain untested in the packet. Schema validation does not authenticate model outputs, outcomes or storage privacy.
