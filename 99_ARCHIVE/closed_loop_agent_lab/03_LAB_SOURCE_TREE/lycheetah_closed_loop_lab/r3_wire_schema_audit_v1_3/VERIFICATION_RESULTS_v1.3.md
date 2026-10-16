# Verification results — v1.3 wire-schema audit

## Passed locally

| Check | Result | What it establishes |
|---|---|---|
| `python -m unittest -v test_wire_fixture.py test_composite_receipt_fixture.py` | 7 test methods passed | The source-equivalent low-level and receipt-shaped fixtures behave as specified. The composite test checks five mutated wire values. |
| `python run_wire_experiment.py` | 8/8 baseline normalizations; 8/8 strict-fixture rejections | Eight authored malformed-type examples are distinguished by the low-level fixture. |
| `python run_composite_experiment.py` | 5/5 normalized bodies match original digest; 5/5 strict-fixture rejections | Five mutations of a complete receipt-shaped record normalize back to the original body and pass its unkeyed SHA-256 digest check in the baseline fixture. The strict fixture rejects all five. |
| `python -m py_compile test_assurance_wire_types.py test_wire_fixture.py test_composite_receipt_fixture.py composite_receipt_fixture.py source_equivalent_wire_fixture.py run_wire_experiment.py run_composite_experiment.py preflight_wire_patch.py check_patch_context.py` | passed | Research and proposed-test scripts parse syntactically. |
| `git apply --numstat strict_assurance_wire_types_v1_3.patch` | parsed; 36 insertions / 11 deletions in `models.py`, 3 insertions / 1 deletion in `receipt.py` | Git can read the unified-diff structure. |
| `python check_patch_context.py` | passed, synthetic context only | The patch applies to a sparse reconstructed context made from the patch's own context lines. This is not a substitute for a real-checkout apply check. |

## Not passed / not executed

- No full Lycheetah-Framework checkout was available in the local container, so `git apply --check` against the complete inspected source was not run.
- `test_assurance_wire_types.py` was only syntax-compiled. It imports the real `lycheetah.assurance` package and was not run against a complete local package.
- Existing upstream assurance tests, package build, and CI were not run for this candidate.
- The attempt to create a GitHub review branch was denied (HTTP 403 / resource not accessible). No upstream branch, issue, pull request, or source file was changed.

## Scope

The fixture results show that selected invalid JSON types can normalize into the same in-memory body as an original well-typed record under the mirrored conversion expressions. The composite test uses an unkeyed SHA-256 digest, not an HMAC signature. This supports a wire-schema strictness finding; it does not establish a production exploit, HMAC forgery, remote bypass, or broad security improvement.
