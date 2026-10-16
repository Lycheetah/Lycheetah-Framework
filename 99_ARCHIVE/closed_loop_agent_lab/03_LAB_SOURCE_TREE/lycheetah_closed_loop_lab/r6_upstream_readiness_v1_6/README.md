# Lycheetah Closed-Loop Agent Lab — R6 upstream readiness (v1.6)

This is an integration-readiness pack, not another standalone “security result.” It unifies the receipt-wire audit (R3/R4) with the policy contract audit (R5) and adds a read-only compatibility inventory so the stricter contract can be evaluated against real stored records before adoption.

## Main additions

- `strict_assurance_wire_types_v1_3.patch` — original wire-type parser patch for `models.py` and `receipt.py`.
- `receipt_contract_delta_v1_6.patch` — closes unknown control fields and checks `policy.sha256` shape at deserialization.
- `policy_type_guard_v1_6.patch` — removes silent string coercion at the `TextRule.from_dict` boundary.
- `policy.schema.strict-candidate.json` and `receipt.schema.strict-candidate.json` — candidate normative wire schemas.
- `scan_migration_compat.py` — read-only inventory comparing current parser/schema acceptance with candidate schema + candidate wire guards. It imports the current parsers from the supplied checkout; install project dependencies first.
- `fixtures/customer_support_policy.json` and `repository_example_policy_results.json` — source-hash-verified copy of the repository's real example policy; both current and candidate schemas and the source-equivalent strict gate accept it.
- `audit_repository_example_policy.py` — reproduces that single-file compatibility check.
- `preflight_upstream_integration.py` — source-pinned, non-mutating preflight that simulates patch application in a temporary source copy.
- `tests/` — proposed tests intended to be copied into the real package checkout after review. They are not falsely reported as upstream-executed here.
- `UPSTREAM_PROMOTION_CHECKLIST.md` — safe sequence and release gates.
- `INTEGRATION_STATUS.md` — permission and validation boundaries.

## Run the pack's standalone checks

From this folder:

```sh
python -m pytest -q tests/test_migration_compat_audit.py
python -m json.tool policy.schema.strict-candidate.json >/dev/null
python -m json.tool receipt.schema.strict-candidate.json >/dev/null
for p in *.patch; do git apply --numstat "$p"; done
```

Requires `jsonschema` for the scanner/tests. The upstream tests require the Lycheetah package and its normal test dependencies.

## Evidence boundary

No repository source was modified. GitHub branch creation was attempted against the inspected repository and returned HTTP 403 `Resource not accessible by integration`. The pack therefore contains local, reviewable artifacts only. It is not a PR, not a merge, not CI evidence, and not proof of production impact.
