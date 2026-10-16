# Patch validation limits — v1.3

The proposed patch passes `git apply --numstat`, and it passes the included **synthetic hunk-context reconstruction**. The latter reconstructs only the source lines represented in the patch and fills all unseen regions with placeholders. This is a useful structural diagnostic, but it is not a full repository checkout and is not an authoritative `git apply --check` result against the actual source tree.

The authoritative preflight is `preflight_wire_patch.py` run against a clean, named non-default branch of the actual repository. It compares both expected Git blob IDs and then runs `git apply --check` on the complete files before changing anything. That preflight has not been run here because no full upstream checkout was available locally and the connected GitHub integration denied branch creation.

The patch is therefore a **review candidate, not an upstream-applied change**. The strict wire-type tests were syntax-compiled only; the source-equivalent fixture tests were executed. No claim is made that the patch passes the real project test suite.
