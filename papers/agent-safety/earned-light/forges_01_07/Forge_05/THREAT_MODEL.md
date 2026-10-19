# Forge V — Threat model and trust assumptions

## Assets
1. Source records and provenance; 2. human-authorized policy semantics; 3. historical decision evidence; 4. continuity of read-only operations; 5. the operator's ability to replace a provider.

## Actors and boundaries
- **Provider A**: may export honestly, omit data accidentally, or maliciously distort records.
- **Operator**: wants to leave Provider A. An authentically human-held pre-export reference is assumed for the strongest checks but not provided by this prototype.
- **Provider B**: separate Python importer, not an independent audited service or actual LLM. Reads a transferred directory, not provider A's internal state.
- **Auditor**: receives both a previously created expected snapshot and the transferred bundle; in this prototype these are both fixture-generated in a single harness.

## Threats actually exercised
- Data omitted from a bundle, including escalation policy and historical decision.
- Revision freshness mismatch.
- Source attribution omitted.
- Dependency inventory omitted even though text queries still succeed.
- Content tampering *after* a checksum manifest.
- Coordinated content alteration and checksum-manifest recomputation.
- Coordinated alteration of the source reference and exported data.
- Duplicate identifiers, missing files, unknown format.
- An injection-style instruction placed in a quoted data field that the deterministic importer never executes.

## NOT covered
- Authenticated issuance of trusted reference; Byzantine/hacked auditor; cryptographically enforced human identity; verifying the truth of provenance; meaningful equivalence of LLM answers; paid/live provider behavior; actual tools or payment actions; OAuth or API credentials; durability under operating system compromise; realistic user skill and comprehension; third-party security audit; real data privacy and deletion; schema upgrades, encoding attacks, schema migration across incompatible real vendors; regulatory compliance.

## Important negative result
If the same adversary can change (a) the exported data, (b) the export's checksum manifest and (c) the apparently independent trusted reference, *all current checks can pass*. This is an implementation of a root-of-trust counterexample, not a solved root-of-trust design.

## Principle
`recoverable data` != `recovered operation` != `human sovereignty`.

Do not let the AI system self-certify the last two merely by emitting metadata.
