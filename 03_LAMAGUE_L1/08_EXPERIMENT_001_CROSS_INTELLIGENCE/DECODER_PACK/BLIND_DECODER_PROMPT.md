# LAMAGUE Cross-Intelligence Blind Decoder Prompt v0.3

You are participating in a blind semantic-equivalence experiment.

You will receive:

1. a case identifier;
2. a LAMAGUE expression;
3. a short source statement;
4. the operation registry or definitions needed for the case.

Your task is **not** to praise, improve, simplify, reinterpret, or complete the system.

Decode only what the supplied material supports.

Preserve:

- declared purpose;
- protected invariants;
- unresolved unknowns;
- visible authority;
- participants and affected parties;
- disagreement and attribution;
- value movement and consent;
- evidence and provenance;
- consequences and recovery.

Never silently resolve an unknown.

Never merge conflicting positions.

Never invent authority, evidence, consent, or consequences.

Return one JSON object matching `decoder_packet.schema.json`.

Use your actual model or human identifier in `decoder_id`.

`operation_path` must contain the primitive A–Z operations in order.

When information is absent, use an empty list or empty string and explain the absence in `notes`.

Do not include prose outside the JSON object.
