# Claims, evidence and criticism

**Guide updated:** 19 October 2026. This area keeps claims inspectable, including
their assumptions, objections, failures and changes. Its records are project
evidence; their existence is not independent scientific validation.

| Task | Read |
|---|---|
| Understand the register | [Claims guide](CLAIMS_README.md), [records](CLAIMS.json), [schema](CLAIMS.schema.json) |
| Find what would falsify a claim | [Falsification register](FALSIFICATION_REGISTER.md), [testability manifest](TESTABILITY_MANIFEST.md) |
| Read objections and limits | [Counter-Codex](COUNTER_CODEX.md), [scope boundary](SCOPE_BOUNDARY.md), [prior art](PRIOR_ART.md) |
| Trace withdrawal and repair | [Failure Museum](FAILURE_MUSEUM.md), [downgrades](DOWNGRADE_REGISTER.md), [outside-review ledger](OUTSIDE_REVIEW_LEDGER_2026-10-03.md) |
| Inspect the 18 October research intake | [Review](RELEASE_AUDIT_2026-10-18.md), [source manifest](RESEARCH_INTAKE_2026-10-18_SOURCE_MANIFEST.json) |
| Inspect the 19 October intake | [Review](RELEASE_AUDIT_2026-10-19.md), [source manifest](RESEARCH_INTAKE_2026-10-19_SOURCE_MANIFEST.json) |
| Review the current entrance cleanup | [Dated entry audit](REPO_ENTRY_AUDIT_2026-10-19.md) |
| See current software/evaluation limits | [Capability guide](../33_APPLICATIONS/README.md), [test guide](../tests/README.md) |

The register's normalized statuses are `ACTIVE`, `SCAFFOLD`, `CONJECTURE` and
`RETRACTED`. Read [CLAIMS_README](CLAIMS_README.md) for schema and source-version
details. Internal `ACTIVE` classifications do not mean peer review, external
replication or deployment approval. Recent research packets are not automatically
new rows in the older register.

From the repository root:

```sh
python3 tools/verify-claims.py --register
python3 -m pytest -q tests/test_claims_register.py
```

The count gate compares structured rows with pinned summaries. It cannot prove
the scientific claims. The test includes a deliberately wrong summary in a
temporary copy, so a passing result also depends on detecting drift.

Older defense versions, bundles and the April cold-room report remain dated
sources. That cold-room report is an internally simulated reviewer perspective,
not an external replication receipt. Preserve disagreements between version
records rather than inventing one release number for the whole corpus.

Created by Mackenzie Conor James Clark / Lycheetah Framework.
