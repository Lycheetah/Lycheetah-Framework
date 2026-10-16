# v1.0 — R2 microtask: strict policy parser types

- Added a frozen task contract for `TextRule.from_dict` wrong-type rejection.
- Audited the current public `lycheetah/assurance/policy.py` source and recorded its Git blob SHA.
- Added a source-equivalent baseline fixture and stricter candidate implementation.
- Tested 20 malformed type combinations across `id`, `pattern`, `title`, and `description`.
- Baseline accepted 17/20 malformed inputs; candidate rejected 20/20.
- Added a proposed upstream patch and pytest test file.
- Kept claims bounded: no full package run, upstream mutation, or deployment.
