# R4 — Receipt Schema / Parser Parity Audit

**Status:** source-equivalent differential experiment, not upstream package execution.

## Question

Do three boundaries agree about the same assurance receipt: (1) the packaged Draft 2020-12 JSON Schema, (2) `AssuranceReceipt.from_dict` and nested `Finding`/`ControlReference` normalization, and (3) digest/HMAC verification on the normalized object?

## Source inspected

Repository: `Lycheetah/Lycheetah-Framework`

Commit: `8ae1b367dcf09997e82ce66f9ad5d30ff36e5d65`

- `lycheetah/assurance/schemas/receipt.schema.json`, blob `eeb1306040a17ce530f42f74966b185fece9a41e`
- `lycheetah/assurance/receipt.py`, blob `91f9ec4d7177480d259240a0899b8b54aff6f0e5`
- `lycheetah/assurance/models.py`, blob `12895f2a7d3e66f4584040713dad131c154b80f0`
- `tests/test_assurance_schemas.py`, which validates generated output against schema but does not exercise hostile wire mutations through both schema and parser.

The schema file in this directory is a semantic reconstruction of the schema text fetched from the inspected source, reformatted for local validation; it is not byte-for-byte archival. A full local checkout was unavailable, so code behavior is modeled from the inspected expressions, not imported from the upstream package.

## Findings

1. The JSON Schema is already stricter than the deserializer for `schema_version`, finding text fields, confidence and evidence item types. `from_dict` normalizes some invalid wire types before `verify()` re-hashes the in-memory body.
2. Nested `finding.controls.items` is only typed as a generic object in the current schema. It has no required fields, field types, or `additionalProperties: false`. That means boolean control titles and URLs pass schema validation despite the model being presented as a typed `ControlReference`.
3. HMAC seals the normalized digest string, not the exact incoming JSON bytes. If a wire mutation normalizes to the same canonical body, the original digest and HMAC continue to verify. This is not an HMAC break: the semantic body after normalization is unchanged. It is a wire-format fidelity and schema-parity issue.
4. Existing `test_assurance_schemas.py` verifies generated receipts conform to the schema, but does not demonstrate that the inverse direction holds: every wire record accepted by the parser matches the schema.

## Differential result

Eight normalizable wire substitutions are tested both unsigned and HMAC-sealed. The source-equivalent parser accepts all 16 because they normalize to the original body. The existing schema rejects four top-level/finding-type cases but accepts four nested control type/unknown-property cases because its control schema is open. Two additional digest-consistent records test a malformed embedded policy hash and an unknown Finding property: the actual parser rejects the unknown Finding property, while the current schema accepts it because the schema definition is open. Across the full 20-row matrix, the source-equivalent parser accepts 18, the current schema rejects 10, and strict parser/schema candidates reject all 20.

These are fixture-level results, not a package-level vulnerability demonstration. The fixture demonstrates that the inspected conversion expressions can produce these behaviors. It does not show unauthorized actions, HMAC forgery, or deployed impact.

## Recommended fix

- Validate incoming receipt objects against one normative wire contract before constructing typed dataclasses, or mirror the contract's types exactly in all `from_dict` methods.
- Harden `$defs/finding.controls.items` into a `controlReference` schema with required string `framework`, `control_id`, `title`, optional string `url`, and a deliberate unknown-property policy.
- Add property-based or mutation tests that run each receipt fixture through both JSON Schema validation and `AssuranceReceipt.from_dict(...).verify(...)`. A parity test should explicitly assert whether both accept or both reject each case.
- Keep HMAC semantics clear: the current seal authenticates the canonical digest of the normalized body, not the precise bytes transported on the wire. If exact-wire provenance is needed, preserve and authenticate canonical input bytes under a separately versioned protocol; do not silently change the current receipt scheme.

## Promotion gates

1. Run the differential test against the actual package from a clean checkout.
2. Decide whether strictness is a bug fix or a versioned compatibility change; inspect existing persisted receipts.
3. Update the schema, parser and tests together.
4. Run existing receipt, schema, CLI, OTel, regression and packaging tests against the same known-green CI baseline.
5. Independently review error handling and HMAC-key custody.

No upstream file, branch, issue or PR has been changed.

## v1.4 extension: policy digest shape and schema candidate

The experiment now also creates self-consistent fixture receipts (digest and fixture HMAC freshly generated) with either an embedded `policy.sha256` that is not a 64-character lowercase hexadecimal digest or an unknown Finding property. The inspected parser model accepts the malformed policy hash but rejects the unknown Finding property; the current receipt schema rejects the malformed policy hash but accepts the unknown Finding property. These cases model schema/serializer divergence, not an external actor forging a valid HMAC.

A strict-candidate schema is included. It adds a closed `controlReference` definition and validates the policy digest shape. In this twenty-record matrix (eight wire substitutions unsigned/HMAC-sealed plus two malformed-record variants each unsigned/HMAC-sealed), 18 records are accepted by the source-equivalent parser model. The current schema rejects ten, and the strict parser/schema candidates reject all twenty. Eight of the original HMAC-sealed wire mutations preserve verification because the normalized canonical body and digest remain the same.
