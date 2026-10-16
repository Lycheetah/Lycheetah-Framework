# Changelog — v1.5

## R5 policy contract parity

- Extended the schema/parser parity audit from assurance receipts to policy data, the input that configures tool governance and text-rule behavior.
- Reconstructed and tested 20 cases against the inspected policy JSON Schema and source-equivalent `TextRule.from_dict` / `AssurancePolicy.from_dict` semantics.
- Found that text-rule `id`, `pattern`, `title`, `description`, and `status_basis` can be stringified by the parser, whereas the current schema expects actual strings.
- Added candidate schema constraints for non-empty string-array items, 4096-character pattern maximum, and non-blank status basis for `ACTIVE` rules.
- Added proposed upstream regression tests and a narrow parser change that retains existing defaults and semantic checks.
- Explicitly records unresolved schema/parser differences for regex compilation, uniqueness of rule IDs, and JSON Schema integer-value semantics.
- Local source-equivalent suite: 5 test methods passed; 20-case matrix generated.
- No upstream change or full-package test claimed.
