# Hybrid Gateway

**[SCAFFOLD] Experimental knowledge-revision prototype · v1.2**  
**Creator:** Mackenzie Conor James Clark / Lycheetah Framework.  
**Integration review:** Caelorynth / Codex · 18 October 2026.

A proposed fact should not silently become an approved fact. This research
separates untrusted extraction, evidence contracts, time-aware knowledge,
operator decisions and a durable review journal.

| Explore | What you get |
|---|---|
| [Architecture and evidence](v1.2/README.md) | Source contracts, bitemporal ledger, atomic staging and review |
| [Integration review](INTEGRATION_REVIEW.md) | Reproduced results and current limits |
| [Failure museum](v1.2/FAILURE_MUSEUM_v1.1.md) | Failures retained through the research line |
| [Publication audit](v1.2/GITHUB_PUBLICATION_AUDIT.md) | Earlier standalone-repository proposal and its open gates |

## Reproduce

```bash
cd papers/ai-futures/hybrid-gateway/v1.2
python3 verify_release.py
python3 -m unittest discover -s tests -q
python3 demo_sql_comparison.py
python3 demo_review_journal.py
```

The standard-library suites use fictional records and local services. They do
not call a live model. Keep generated demo data outside this preserved tree when
extending the research.

## What the evidence supports

The integration run reproduced **264 tests with no failures or skips on Python
3.12**. The supplied review used Python 3.13; neither run establishes support on
every interpreter advertised in the archived candidate.

The strong temporal SQL comparison ties the gateway on four authored questions.
Model quality, authentic CASCADE integration, independent reviewer performance
and production security remain unmeasured. An exported witness detects rollback
only under its stated independent-custody assumptions.

This is a source research home inside the Framework. It adds no installed
`lycheetah` command and does not merge the prototype into the active runtime.
The earlier proposal for a separate repository remains historical; no separate
repository has been created.

`v1.2/` preserves all 138 supplied files, including their MIT attribution and
original manifest. Its historical documents inherit this experimental footing
when no inline marker is present, conditional on the checked
[intake manifest](../../../28_DEFENSE/RESEARCH_INTAKE_2026-10-18_SOURCE_MANIFEST.json).
