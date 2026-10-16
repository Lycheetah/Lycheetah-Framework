# R5 — Policy Contract Parity Audit v1.5

**Status:** source-equivalent differential audit; not execution of the upstream package.

## Why this is the next boundary

Receipts are downstream evidence. Policies are upstream authority: they decide which tools are denied, reviewed, or allowed and which text findings are generated. A policy parser that silently stringifies malformed input can change the rule an operator thought they configured. This audit moves the same schema/parser consistency method to the policy boundary.

## Source inspected

Repository: `Lycheetah/Lycheetah-Framework`, inspected default-branch source snapshot from the prior audit (commit `8ae1b367dcf09997e82ce66f9ad5d30ff36e5d65`).

- `lycheetah/assurance/policy.py`
- `lycheetah/assurance/schemas/policy.schema.json`
- `tests/test_assurance_policy.py`

The existing test suite already checks unknown fields, malformed booleans, array shapes, NaN thresholds, string-valued integer fields, active-rule evidence basis, invalid regexes, and normal round-trips. It does **not** test wrong JSON types for TextRule `id`, `pattern`, `title`, `description`, or `status_basis` where `TextRule.from_dict` calls `str(...)`.

## Results

Twenty differential cases were executed against (a) a reconstruction of the current Draft 2020-12 policy schema and (b) a source-equivalent model of the inspected parser behavior:

- Current schema accepted: **8/20**
- Source-equivalent parser accepted: **7/20**
- Current schema/parser acceptance parity: **7/20**
- Proposed candidate schema accepted: **4/20**
- Proposed strict-type-parser model accepted: **1/20**
- Candidate schema/parser result agreement: **17/20**

These are counts over this deliberately selected matrix, not estimates of overall risk prevalence or production incidence.

### High-value mismatches

1. `TextRule.from_dict` calls `str()` on `id`, `pattern`, `title`, `description`, and `status_basis`. As a result, values such as Boolean `true`, numeric `123`, or integer `7` can be normalized into strings before dataclass checks. Several invalid wire types are rejected by JSON Schema but accepted by the source-equivalent parser.
2. The schema does not impose the implementation's 4096-character regex-pattern limit. A pattern longer than that limit can pass schema validation but is rejected by the parser.
3. The schema does not express the rule that an `ACTIVE` rule needs a non-blank `status_basis`. The parser enforces that semantic requirement.
4. The schema's generic string-array contract allows empty strings in values such as tool allowlists; the parser rejects empty entries.
5. Duplicate rule identifiers and invalid regular-expression syntax are additional semantic checks performed by the parser. Standard JSON Schema cannot conveniently express uniqueness of one property across an array of objects or Python-regex compilation validity. These should remain explicit semantic validation rather than be mislabeled as schema-only behavior.
6. JSON Schema's `integer` type uses numerical value semantics; a value parsed as `20.0` may validate as an integer because it has no fractional part, while the current Python helper uses `isinstance(value, int)` and rejects a float object. The project should explicitly choose whether to align the parser with JSON Schema's numerical semantics or document a stricter lexical/input policy. This case is retained as a deliberate unresolved mismatch, not hidden.

## Proposed low-risk change

At the parsing boundary, verify that TextRule `id` and `pattern` are strings before constructing the rule. If optional `title`, `description`, or `status_basis` fields are present, require strings. Then use the validated original values rather than converting them with `str()`. Preserve current defaults for omitted optional fields. Add the 4096-character limit and non-blank active basis to the schema; apply `minLength: 1` to string-array entries.

Keep other semantic checks in the parser: valid regex compilation, unique rule ids, phase/enum validation, finite numeric thresholds and bounded integer limits. Add a test that checks both schema validation and parser behavior but does not require the schema to duplicate semantics it cannot faithfully express.

## Verification and limitations

`policy_contract_parity.py` and its tests run locally using `jsonschema`. The parser is a source-equivalent model; upstream `policy.py` was fetched/read via the repository connector but the full repository was not cloned, imported, or tested. The candidate schema is a proposal, not an upstream modification. No branch, issue, commit, or pull request was created.

Promotion gate: apply the proposed type guard and schema changes in a clean non-default upstream branch, then run `tests/test_assurance_policy.py`, `tests/test_assurance_schemas.py`, policy CLI/runtime tests, and the full package suite. Review persisted policy files for malformed legacy entries before enforcing strict parsing.
