# Strict TextRule parser patch v1.2 — review note

**Status:** Proposed local patch; not applied upstream.  
**Inspected target:** `Lycheetah/Lycheetah-Framework`, commit `8ae1b367dcf09997e82ce66f9ad5d30ff36e5d65`.  
**Target blob:** `913006991327ac40bf34e96fce591ca100334ca9` (`lycheetah/assurance/policy.py`).

## What changed from v1.0/v1.1

The earlier patch guarded `id`, `pattern`, `title`, and `description`, but omitted `status_basis`, which was also passed through `str(...)`. The v1.2 patch closes that gap and enforces the five declared string fields at both ingress routes:

1. `TextRule.from_dict`, before the values are passed into the dataclass.
2. `TextRule.__post_init__`, so direct construction cannot bypass the class invariant for title/description/status_basis.

All other parser behavior is intended to remain unchanged. It still allows missing optional fields and preserves the existing defaults for title, description, and status basis.

## Local experiment

- Six focused unit-test methods passed for the source-equivalent candidate fixture.
- The comparison covers 30 malformed inputs: six wrong JSON value types (`null`, Boolean, integer, float, array, object) across five string fields.
- Source-equivalent baseline accepts 27/30 malformed type inputs; candidate rejects 30/30.
- Explicit strings and existing defaults were accepted by the candidate fixture.
- A synthetic-context `git apply --check` passed for the patch's hunk syntax/context.

These are fixture results, not a run against the installed/upstream package. The proposed upstream pytest file contains 60 parameterized malformed cases plus two compatibility methods (62 resulting cases depending on pytest collection); it was syntax-compiled, but cannot be run in a full checkout in this environment.

## Why direct-constructor validation is included

A parser-only check can be bypassed by Python callers that instantiate `TextRule(...)` directly. The dataclass already validates `rule_id` and `pattern`, but did not similarly validate the three other string annotations. Validating the class invariant once in `__post_init__` makes direct and parsed instances consistent.

## Risk and compatibility

The intentional compatibility change is limited to callers that supplied non-string objects in fields whose public type is `str`. Those callers now receive `PolicyError` rather than silent conversion or later incidental failures. Existing valid string configurations and omitted-option defaults are expected to remain identical; verify through the actual project regression suite before merge.

## Required upstream gate

1. Run `preflight_upstream_v1_2.py` on a clean non-default branch at the exact source blob.
2. Apply patch and copy the pytest file.
3. Run targeted assurance policy/runtime/model tests.
4. Run full CI and compare against a known-good base run.
5. Review the diff; do not merge if baseline CI remains unexplained/red.

The GitHub integration refused branch creation with HTTP 403, and local GitHub network resolution is unavailable in this session. No repository files or refs have been changed.
