# R2 Microtask Contract — Strict TextRule Policy Deserialization

**Target**: `lycheetah/assurance/policy.py`, `TextRule.from_dict`  
**Observed upstream file SHA-1 (Git blob)**: `913006991327ac40bf34e96fce591ca100334ca9`  
**Source**: https://github.com/Lycheetah/Lycheetah-Framework/blob/master/lycheetah/assurance/policy.py

## Frozen contract
- `id` and `pattern` are required strings.
- If present, `title` and `description` must be strings.
- Wrong JSON types are rejected, not silently converted to strings.
- Existing valid string inputs, missing-title default (`id`), and missing-description default (`Policy text rule matched`) remain unchanged.
- Existing identifier, regex, enum, phase, and unknown-field checks remain in place.

## Scope exclusions
This does not test whether a text rule is a good safety policy, whether its regex detects manipulation, or whether a host enforces an `ALLOW`/`REVIEW`/`BLOCK` receipt. It tests only type-contract consistency.

## Evaluation discipline
The upstream source was inspected read-only. A source-equivalent baseline fixture reproduces the coercion pattern; a candidate fixture adds explicit strict checks. The malformed cases were fixed before testing. This is a micro-experiment, not an upstream integration test or commit.
