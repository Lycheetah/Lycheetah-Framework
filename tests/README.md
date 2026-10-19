# Tests — scope before totals

**Guide updated:** 19 October 2026. The default pytest configuration collects
`tests/`, as declared in [pyproject.toml](../pyproject.toml). Research forges and
archived labs may have separate runners, inputs, dependencies and repeated
lineage cases. Default collection is not a test of every file in this repository.

Run focused checks from the repository root with the declared developer
dependencies available:

```sh
python3 -m pytest -q tests/test_claims_register.py
python3 -m pytest -q tests/test_meaning_handover_demo.py tests/test_compaction.py
python3 -m pytest -q tests/test_assurance_policy.py tests/test_assurance_receipt.py
python3 -m pytest -q tests/test_research_intake.py
```

Choose the check that exercises the behaviour being changed. The intake tests
exercise a manifest verifier with temporary fixtures; they are distinct from
replaying every imported research experiment.

| Need | Route |
|---|---|
| Count mirrors and deliberate drift detection | [test_claims_register.py](test_claims_register.py) |
| Runtime contracts and evidence caps | `test_assurance_*.py`, [runtime guide](../34_ASSURANCE_RUNTIME/README.md) |
| Handover, compaction and controls | `test_meaning_handover_demo.py`, `test_compaction.py`, `test_handoff.py`, `test_sovereign_*.py` |
| Current research replay instructions | [Research index](../papers/README.md), each packet's README and verifier |
| Dated intake evidence and source preservation | [18 October review](../28_DEFENSE/RELEASE_AUDIT_2026-10-18.md), [19 October review](../28_DEFENSE/RELEASE_AUDIT_2026-10-19.md) |
| Dataset evaluation | [Capability guide](../33_APPLICATIONS/README.md); external downloads are separate from ordinary unit tests |

Read collected, passed, failed, skipped and expected-failure counts separately.
A test that did not run is not a pass. The predictive CASCADE criterion has a
recorded failure and later strict expected-failure handling in
[test_cascade_predictability.py](test_cascade_predictability.py); marking that
expected does not turn the prediction into a successful result.

Author-written fixtures establish behaviour on their cases. Externally authored
data, independent execution and observed user outcomes are different evidence.
Keep exact commands, source versions and scope with any reported result; do not
repeat an old repository-wide total as today's verdict.

Created by Mackenzie Conor James Clark / Lycheetah Framework.
