# Evidence, audit blockers, and conflict register

## Stage 1 — what the local tests demonstrate
Software exhibits bounded parsing, canonical rendering, round-trip checks, provenance sidecar generation, rejection of selected ambiguous references and syntactic errors, and browser study export. Representative local results: v1.8 49/49 test methods + 700 generated dialogues; v1.9 71/71 test methods + 400 generated valid conversations, 80/80 synthetic restricted-reader agreement; v2.0 12/12 new tests + 71/71 focused inherited tests, 4/4 synthetic browser end-to-end cohort flows, 32 items per cohort. These are repository-supplied assertions independently reproducible from the preserved released code, but this compiler has **not independently rerun every historical test**.

## Stage 2 — stronger outside audit on earlier lineage
The public `03_LAMAGUE_L1/SXP-L_LAMAGUE_INDEPENDENT_AUDIT_v0.1_to_v1.0.md` by Aetheron/Argon (dated 2026-10-18) reports independent reproduction of **387 top-level tests plus 239 subtests** across earlier releases and identifies substantial problems:
- Noncompositional, regex/legacy-fallback grammar layers and dropped Native-36 expressivity in later human register.
- Initial phonology not uniquely decodable in continuous speech (16 active Levenshtein-one pairs; five concatenation collisions reported).
- Old v0.2 AST round-trip defect around `USR:A` vs `N36:A`.
- `ariva` (“arrive”) incorrectly treated as obligatorily transitive.
- Dual-schema interpretations of attitude predicates in v0.8 wrappers.
- Early meaning-diff crash on v0.9/v1.0 concepts and insufficient priority for actor/target changes.
- `authority_bridge.py` lacks proper handling of denials/revocations, repaired turns, and speaker/grantee bindings, a meaningful hazard if elevated to action authorization.
- Old repair-chain validation permits a superseded target to be reused.
**These findings are not certified fixed by v1.9 or v2.0.** Their status is *OPEN / REQUIRES REPRODUCTION ON CURRENT CONSOLIDATED BRANCH*.
Source: https://github.com/Lycheetah/Lycheetah-Framework/blob/master/03_LAMAGUE_L1/SXP-L_LAMAGUE_INDEPENDENT_AUDIT_v0.1_to_v1.0.md

## Stage 3 — what has not been shown
- No independent consenting participant has taken the v2.0 comprehension study; no acoustic listening study; no natural conversation corpus; no real-world AI-model improvement result; no semantic superiority against a modern natural-language inference system; no live agent permission tests.
- Source-code agreement with a separately written *restricted* reader is useful but not independent human evidence or an end-to-end semantic verification proof.
- Checksum manifests establish byte consistency for the packaged files, not authenticated source authorship.
- A pilot Latin square mitigates some item allocation imbalance but does not remove familiarity, fatigue, teaching, and item difficulty biases.

## Open merge conflicts
1. **Canonical semantic intermediate representation**: SXP-C AST, Native-36, LAMAGUE Core v0.4, RUNTIME, PACKET, spoken register and BRIDGE need explicit mapping or acknowledged non-mapping; no silent inheritance.
2. **Grammar implementation**: consolidate parsing approaches without breaking old archives; adversarially test changed semantic classifications and negation scope.
3. **Pronunciation**: reconstruct acoustic minimal-pair inventory before announcing intelligibility.
4. **Authorization**: keep external verified capability gate; never promote reported linguistic permission to token issuance.
5. **Evidence naming**: separate local test, independent external reproduction, human performance, deployment and illustrative worldbuilding.
6. **Publishing**: current GitHub workspaces are concurrent; use PR branch, don't overwrite repo main/master or other agents' work without integration review.

## Decision to preserve
The user's language affection and linguistic ambition are not merely branding: they impose a requirement for expressive, everyday speech, poetry, conflict resolution and metaphor, *alongside* inspectable semantics. Proof of parser interoperability alone is insufficient.
