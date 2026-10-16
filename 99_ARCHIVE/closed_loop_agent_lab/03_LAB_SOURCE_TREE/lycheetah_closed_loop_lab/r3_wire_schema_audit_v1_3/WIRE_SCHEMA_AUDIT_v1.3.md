# Assurance Wire-Type Audit v1.3

**Status:** source-derived issue report and proposed patch; not integrated upstream.  
**Inspected commit:** `8ae1b367dcf09997e82ce66f9ad5d30ff36e5d65`.

## Finding

The policy parser review showed that string coercion also appears in the evidence/receipt models. The inspected code has these normalization paths:

- `ControlReference.from_dict`: `framework`, `control_id`, `title`, and optional `url` are passed through `str(...)`; the class itself has no string-field validation.
- `Finding.from_dict`: several text fields are passed through `str(...)`, `confidence` through `float(...)`, and evidence elements through `str(...)`. It checks a subset of types, notably the deterministic flag, evidence/controls array containers and `cap_reason`, but does not reject every wrong member type.
- `AssuranceReceipt.from_dict`: receipt ID and timestamp have explicit string checks, but `schema_version` is converted to a string before instantiation. `verify()` then hashes the normalized in-memory body.

This can admit a noncanonical wire representation that normalizes to the same in-memory object: e.g., a numeric JSON schema version `0.1` may become the string `"0.1"` before body digest verification. Similarly, `true` can become confidence `1.0`, and numeric evidence can become text. The reproduced behavior concerns wire-schema strictness and representation fidelity. The composite fixture shows that five selected malformed wire representations can normalize back to the same complete body and therefore match the same SHA-256 body digest. The modeled receipt has no HMAC seal, and no real package call was executed. This is **not a cryptographic forgery or a demonstrated production bypass**: the normalized in-memory object remains the same. The risk is noncanonical accepted input and possible disagreement between consumers that do not share identical parsing rules.

## Proposed correction

The narrowed patch adds explicit type guards at the wire-deserialization boundary for `ControlReference`, `Finding`, and `AssuranceReceipt.schema_version`. It intentionally avoids changing direct dataclass-constructor semantics until existing downstream usage can be checked in a full checkout. It does not change the meaning of valid string fields, numeric confidence values, evidence strings, or the current schema version. Unknown field handling is otherwise retained to avoid broadening the compatibility change unnecessarily.

## Local source-equivalent experiment

`run_wire_experiment.py` reproduces eight low-level typed mutations. A second, complete receipt-shaped fixture in `composite_receipt_fixture.py` starts from a record whose unkeyed SHA-256 digest verifies, then mutates five wire types: numeric schema version, Boolean control title, Boolean finding title, Boolean confidence, and integer evidence. The source-equivalent baseline normalizes each mutation back to the original body, so the digest check still matches; the strict fixture rejects all five. This is stronger evidence of the normalization behavior than isolated fields, but still a source-equivalent fixture rather than execution of the real upstream package.

The proposed upstream test file adds parameterized cases for string fields, Boolean/string/non-finite confidence values, evidence member types and receipt schema-version type. It has only been syntax-compiled here; actual project tests have not run in a full checkout.

## Why this matters to the broader project

Assurance records are part of the observation channel in the cybernetic loop. If malformed evidence is silently coerced, reviewers and downstream software can disagree about the original wire record while seeing the same normalized object. Strict parsing won't prove that a recorded claim is true, but it helps establish that the system has interpreted the evidence according to its declared schema.

## Promotion gates

1. Confirm both source blob hashes on a clean non-default branch.
2. Run `preflight_wire_patch.py` and then apply the patch.
3. Run the new wire-type tests and existing assurance model/receipt/runtime tests.
4. Run full CI on a green baseline and candidate, same environment.
5. Check existing serialized receipts against the stricter parser before merging.

No upstream files, branches, issues or pull requests were changed; the GitHub branch-write operation was denied. This is a review candidate only.
