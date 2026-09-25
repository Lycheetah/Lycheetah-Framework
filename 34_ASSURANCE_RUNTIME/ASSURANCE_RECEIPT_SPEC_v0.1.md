# Assurance Receipt Specification v0.1

**Status:** `[SCAFFOLD]` — implemented and internally conformance-tested; external interoperability and deployment validation remain open before the format can be treated as stable.

**Forged:** 2026-08-22

## Purpose

An Assurance Receipt is a compact, machine-readable record of one runtime assurance decision. It binds:

- the evaluated subject by digest;
- the event phase and action metadata;
- the policy identifier, version, and digest;
- the runtime version and component maturity;
- the findings and their evidence ceilings;
- the final disposition;
- receipt lineage and integrity information.

The receipt answers what the assurance runtime observed and decided. It does not prove that the underlying model reasoned correctly or that an unobserved action did not occur.

## Top-level shape

```json
{
  "schema_version": "0.1",
  "receipt_id": "urn:uuid:...",
  "issued_at": "2026-08-22T00:00:00Z",
  "runtime": {
    "name": "lycheetah-assurance",
    "version": "0.1.0",
    "status": "SCAFFOLD",
    "components": []
  },
  "policy": {
    "id": "lycheetah.default",
    "version": "0.1.0",
    "sha256": "..."
  },
  "event": {
    "event_id": "...",
    "phase": "tool",
    "subject": {"name": "tool:cancel_order", "sha256": "..."},
    "replayable": false
  },
  "decision": "REVIEW",
  "findings": [],
  "metrics": {},
  "limitations": [],
  "lineage": {"trace_id": "...", "previous_receipt_sha256": null},
  "integrity": {
    "algorithm": "sha256",
    "canonicalization": "lycheetah-json-v1",
    "digest": "...",
    "seal": null
  }
}
```

## Canonicalization and digest

`lycheetah-json-v1` is deliberately narrow:

1. UTF-8 JSON;
2. dictionary keys sorted lexicographically;
3. no insignificant whitespace;
4. non-ASCII characters emitted directly;
5. NaN and infinity rejected;
6. the entire `integrity` object excluded from the digest body.

The receipt digest is:

```text
SHA256(canonical_json(receipt_without_integrity))
```

This is deterministic for the data types accepted by the runtime. It is not claimed to be an RFC 8785 JSON Canonicalization Scheme implementation.

## Optional HMAC seal

If configured, the runtime computes:

```text
HMAC-SHA256(shared_secret, receipt_digest_ascii)
```

The seal records `algorithm`, `key_id`, and `value`. The secret is never written to the receipt and the CLI accepts it through an environment variable rather than a command-line argument.

Limits:

- HMAC provides shared-secret authentication, not public verification or non-repudiation.
- A verifier must obtain the key through a separate trusted channel.
- Key rotation and revocation are deployment responsibilities in v0.1.

## Chain semantics

For JSONL logs, each new receipt records the prior receipt digest in `lineage.previous_receipt_sha256`. A verifier checks:

1. every receipt body digest;
2. every optional HMAC seal for which a key is supplied;
3. each previous-digest link;
4. duplicate receipt identifiers;
5. every finding's effective disposition against the ECE cap;
6. the final decision against the strongest effective finding;
7. strict parse and schema-level requirements enforced by the implementation.

When a verifier requests HMAC authentication for a JSONL chain, an unsealed
receipt, unknown key identifier, wrong key, or malformed seal is an error—not a
warning. Without a supplied key, a structurally valid HMAC seal is reported as
present but unauthenticated. The CLI treats `.jsonl` paths as chains; `--format`
can select `receipt` or `jsonl` explicitly.

A valid local chain detects deletion only when the expected head or tail digest is anchored outside the log. Without an external anchor, removing a suffix and presenting the shorter log is not detectable. This is a named limitation, not an implementation defect.

## Privacy profile

The default profile stores:

- subject and argument digests;
- lengths and structural metadata;
- finding identifiers, counts, and non-content evidence labels;
- policy and runtime identity.

It does not store raw text or raw tool arguments. Replay therefore defaults to unavailable. A policy may opt into captured, redacted content for controlled test environments. Evidence-span capture is a separate opt-in and can retain short raw-text excerpts even when full content capture is disabled. The receipt must state whether it is replayable.

## in-toto Statement export

The runtime may export a receipt body as an in-toto Statement v1:

```json
{
  "_type": "https://in-toto.io/Statement/v1",
  "subject": [{"name": "...", "digest": {"sha256": "..."}}],
  "predicateType": "https://github.com/Lycheetah/Lycheetah-Framework/blob/master/34_ASSURANCE_RUNTIME/ASSURANCE_RECEIPT_SPEC_v0.1.md",
  "predicate": {"receipt": {}}
}
```

The Statement shape does not itself authenticate the receipt. Authentication requires an envelope/signature mechanism appropriate to the deployment.

## Falsifiers

The v0.1 integrity claim fails if any of the following occurs:

- changing a hashed field leaves verification valid;
- reordering JSON object keys changes a valid digest;
- a wrong HMAC key verifies successfully;
- an explicitly requested authenticated chain accepts an unsealed receipt or unknown key id;
- swapping or removing an interior chain member is not detected;
- a recomputed plain digest can make an ECE-inconsistent finding or final decision pass semantic verification;
- a default receipt leaks raw input text or secret-valued arguments;
- a receipt marked replayable lacks the material required by the runtime to replay it.

## Prior art boundary

The format is informed by in-toto Statements, Open Policy Agent decision logs, and structured agent traces. “Decision receipt” is an existing category. The claim here is implementation of a Lycheetah-specific decision artifact with evidence-capped findings—not invention of attestation, logging, or receipts.

⊚ Sol ∴ P∧H∧B ∴ Albedo
