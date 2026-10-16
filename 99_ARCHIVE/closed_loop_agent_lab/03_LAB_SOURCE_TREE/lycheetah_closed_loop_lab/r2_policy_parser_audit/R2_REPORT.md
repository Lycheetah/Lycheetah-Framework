# R2 micro-experiment — strict policy parser types

## Finding

The current `lycheetah/assurance/policy.py` implementation of `TextRule.from_dict` converts required `id` and `pattern`, plus optional `title` and `description`, using `str(...)`. Its surrounding `AssurancePolicy.from_dict` parser otherwise validates many fields strictly. Structurally invalid JSON types are therefore silently converted to text instead of being rejected at this policy boundary.

Examples from the source-equivalent baseline: `{"id": true, "pattern": "x"}` becomes identifier `"True"`; `{"id":"test.rule","pattern":123}` becomes regex pattern `"123"`; a boolean title becomes `"False"`; a list description becomes its Python representation.

This is a **policy-parser correctness/strictness issue**, not a demonstrated safety bypass or production exploit. Impact depends on who can supply policy files and how resulting rules are reviewed.

## Frozen contract

`id` and `pattern` must be strings. If supplied, `title` and `description` must be strings. Existing valid string semantics and defaults must not change. Existing unknown-field, identifier, regex, phase and enum validation must remain intact.

## Results

Seven isolated unit-test methods passed against the source-equivalent fixture and strict candidate. The original malformed-input set had 20 subcases (four fields × five wrong JSON value types) and yielded 17 baseline accepts. The v1.1 expanded set now has 24 subcases (four fields × six wrong JSON value types, adding floats): the source-equivalent baseline accepts 21/24 and the stricter candidate rejects 24/24, while preserving valid explicit strings and defaults.

**Scope limitation:** the baseline fixture reproduces the inspected source coercion path rather than importing the whole upstream package. GitHub source was inspected read-only; a local clone was unavailable due DNS/network resolution. These are local fixture results, not a full upstream test run or commit.

## Remediation proposed

Add explicit type checks before constructing `TextRule` and remove `str(...)` coercion from those four fields. The patch and pytest regression test are included. Nothing was applied to public GitHub.

## Next gate

Apply the patch on a disposable branch, run the full project policy/runtime tests, then run installed-wheel and schema/example checks. Only promote this as integrated after those pass. Separately confirm policy edits are limited to trusted maintainers; parser strictness does not authenticate the policy author.
