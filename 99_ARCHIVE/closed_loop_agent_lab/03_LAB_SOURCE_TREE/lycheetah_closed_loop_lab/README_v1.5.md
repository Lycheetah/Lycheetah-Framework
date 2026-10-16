# Lycheetah Closed-Loop Agent Lab — v1.5

**Status: R0 research prototype.** v1.5 continues the evidence / authority chain investigation by auditing the policy configuration boundary.

## New work

`r5_policy_contract_v1_5/` compares the inspected policy JSON Schema with source-equivalent behavior of `TextRule.from_dict` and `AssurancePolicy.from_dict`. Twenty deliberately selected inputs explore type coercion, regex validity, active-rule evidence basis, array values, duplicate identifiers, and numeric representation. Five local test methods pass. The proposed fix checks text-rule field types before constructing the rule, keeps optional-field defaults, adds schema constraints, and preserves semantic validation in the parser.

## Main finding

Some policy text-rule fields are stringified before validation. For example, a Boolean or number supplied as `pattern` may become a valid regular expression string instead of being rejected as malformed policy input. This is a config-contract reliability defect in the inspected parsing logic, but no malicious policy execution or production impact was demonstrated.

## Evidence limits

The matrix uses a source-equivalent parser model based on code read through the repository connector. It is not execution of a full package checkout. Proposed source changes and upstream tests are handoff material, not committed or run in CI. Semantic checks that JSON Schema does not express—such as regex compilation and unique IDs—remain parser responsibilities. See `r5_policy_contract_v1_5/POLICY_CONTRACT_AUDIT_v1.5.md` and `r5_policy_contract_v1_5/VERIFICATION_RESULTS_v1.5.md`.

Repository source: https://github.com/Lycheetah/Lycheetah-Framework
