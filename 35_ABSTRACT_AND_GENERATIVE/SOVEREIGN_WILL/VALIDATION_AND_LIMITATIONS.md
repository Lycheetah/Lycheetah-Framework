# Validation, Source Integrity and Evidence Limits

**Consolidation run:** 19 October 2026.

## What was verified during this handoff

- All seven original Forge II–VIII ZIP files were present and individually passed Python `ZipFile.testzip()` integrity checking.
- The Forge I charter and complete 3,897-word story were present as actual Markdown files.
- The extracted **Forge VIII archive** was run with `python run_verification.py` from a clean temporary directory; **return code 0**.
- This ran the preserved historical test chain through Forges II–VII. The result reports **142 total passing tests**, including **32 Forge VIII unit tests** and **110 historical tests**. `cryptography` was available (46.0.4), so the Forge VI tests were not skipped for missing dependency.
- The handoff's expanded tree contains primary files from every Forge and original ZIPs preserved separately, so extracted code is not quietly flattened into a fictional merged engine.
- Original ZIPs themselves are unchanged; see SHA-256 manifest.

**Review correction (2026-10-22, RV22).** The 142-test chain covers Forges **IV–VIII**, not II–VII: the 110 historical tests are Forge IV (28) + V (23) + VI (36) + VII (23), and the Forge VIII runner requires exactly that 110. Forges II (28) and III (37) are outside it. `papers/agent-safety/sovereign-choice-research/verify.py` runs all three parts for 207 test executions, and its README says the same. The bullet above is kept as written in the handoff.

## What the test count does and does not mean

The 142 count comes from deterministic, self-authored local tests. It confirms that the included reference implementations and fixtures behave as specified under those test conditions. It **does not** prove end-to-end production security, machine or human free will, genuine approval from a human, vulnerability absence, independent replication, or a demonstrated advantage over strong conventional design.

Forge VII's 18/18 policy *tie* with a conventional goal-aware baseline is explicitly preserved as a negative/neutral result. Forge VIII's 7/8 counterexamples concern **fictional graph fixtures**, not human participants.

## Threat boundaries

- Signed local approval verifies a key and payload; not real identity, informed consent or absence of coercion.
- An agent with bypass access to unmediated tools or privileged database mutation can evade reference controls.
- A local transactional fence cannot retroactively prevent a remote action already accepted elsewhere.
- The archived mirror of the `CommitFence` is a historical upstream snapshot, not an authority to silently overwrite current GitHub code.
- A user's frequency of AI use, self-reported adherence or path reachability cannot establish or rank human free will.
- The story and abstract hypotheses are interpretive / creative artifacts, not scientific findings.

## Source links

- https://github.com/Lycheetah/Lycheetah-Framework/tree/master/05_MICROORCIM_L5
- https://github.com/Lycheetah/Lycheetah-Framework/tree/master/35_ABSTRACT_AND_GENERATIVE
- https://github.com/Lycheetah/Lycheetah-Framework/tree/master/papers/agent-safety
- https://github.com/Lycheetah/Lycheetah-Framework/tree/master/LYCHEETAH_MYTHOS/SCRIPTURES_AND_STORIES

Use repository source files and archived manifest hashes when citing or re-testing research. This handoff is not a commit; no GitHub changes were made.
