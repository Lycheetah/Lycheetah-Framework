# Upstream review handoff

## Goal
Reject non-string values for `TextRule.from_dict` fields `id` and `pattern`, and supplied optional fields `title` and `description`, rather than silently converting malformed JSON values with `str(...)`.

## Contents
- `proposed_patches/strict_text_rule_parser.patch` — minimal implementation change.
- `proposed_patches/test_assurance_policy_text_rule_types.py` — 24 malformed-type cases and two compatibility tests through `AssurancePolicy.from_dict`.
- `../../scripts/verify_upstream_patch.py` — non-mutating safety preflight for the intended source blob and review branch.

## Apply safely
1. Clone or update `Lycheetah/Lycheetah-Framework`.
2. Create a named review branch off the source revision containing the expected target blob.
3. From this pack, run `python scripts/verify_upstream_patch.py /path/to/Lycheetah-Framework`.
4. Only if preflight passes, follow its printed `git apply`, `cp` and targeted `pytest` commands.
5. Run the full CI matrix and inspect outcomes before opening or merging a pull request.

This session did not have GitHub write permission, so the candidate remains a local artifact and is not represented as an upstream commit.
