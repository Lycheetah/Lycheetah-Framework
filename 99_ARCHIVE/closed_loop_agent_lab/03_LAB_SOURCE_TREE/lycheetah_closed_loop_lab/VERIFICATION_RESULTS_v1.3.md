# Verification results — v1.3 wire-schema audit

## Passed locally

| Check | Result | What it establishes |
|---|---|---|
| `python -m unittest -v test_wire_fixture.py test_composite_receipt_fixture.py` | 7 test methods passed | The low-level and receipt-shaped source-equivalent fixtures behave as specified. The composite test covers five controlled receipt mutations. |
| `python run_wire_experiment.py` | 8/8 baseline normalizations; 8/8 strict-fixture rejections | Eight authored malformed-type examples are distinguished by the low-level fixture. |
| `python run_composite_experiment.py` | 5/5 normalized bodies match the original digest; 5/5 strict-fixture rejections | Five mutations of a receipt-shaped record preserve baseline digest validity after normalization, while the strict fixture rejects all five. |
| `python -m py_compile ...` | passed | The proposed upstream test module and local scripts parse syntactically. |
| `git apply --numstat strict_assurance_wire_types_v1_3.patch` | parsed | Git reads the patch's unified-diff structure. |
| `python check_patch_context.py` | passed, synthetic context only | The patch applies against reconstructed context lines embedded in the diff. This is not a full repository apply check. |

## Not passed / not executed

- `git apply --check` against the complete inspected source tree was not run because no full local checkout was available.
- `test_assurance_wire_types.py` was syntax-compiled only; it was not run against the real `lycheetah.assurance` package.
- Existing assurance tests, package build and candidate CI were not run.
- Creating a GitHub review branch was denied by the connected integration. No upstream branch, issue, pull request or file was changed.

## Scope

The fixture results establish behavior of a bounded source-equivalent model of the inspected coercion paths, not a production exploit or measured attack rate. The composite fixture uses an unkeyed SHA-256 body digest without an HMAC seal. It demonstrates noncanonical type representations normalizing to the same body; it does not alter the normalized semantics or forge a signature.
