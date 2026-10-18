# Earned Trust integration review

**[SCAFFOLD] Synthetic engineering evidence · 18 October 2026**  
Framework creator: Mackenzie Conor James Clark. Review: Caelorynth / Codex.

## What was executed

Python 3.12, Linux, ordinary-user host execution with loopback sockets. Each
cycle ran in a fresh Python process against an exact copy of the supplied
source. No live provider, customer record or payment was used.

| Suite | Methods collected | Passed | Skipped | Failed |
|---|---:|---:|---:|---:|
| Cycles 001–008, selected local modules | 331 | 331 | 0 | 0 |
| Cycle 009, HTTP/provider and Unix gateway | 47 | 38 | 9 | 0 |
| Original Cycle 004 native bridge | 4 | 4 | 0 | 0 |
| Original Cycle 005 native bridge | 4 | 2 | 0 | 2 |
| Corrected Cycle 005 bridge | 5 | 5 | 0 | 0 |

The nine skipped tests require root to drop a subprocess to UID 65534. Their
earlier privileged result remains supplied historical evidence, not a result
reproduced here. The original release runner prints PASS from unittest's exit
code even with skips; this review separates them explicitly.

[Machine-readable original-suite results](../../../28_DEFENSE/evidence/research-intake-2026-10-18/suite-results.json)
include exact method names and skip reasons.

## A fixture mismatch hid the intended boundary

Cycle 005 seeded the synthetic provider's default approval `a1`, then issued a
token for `approval-1`. The provider correctly refused `GRANT_MISMATCH`. Two
normal-confirmation assertions failed. The common-origin test returned its
expected REVIEW label **at the provider**, before reaching provenance; its green
assertion alone did not establish a working provenance check.

The separate [corrected adapter](integration/cycle_005_bridge.py) names the
historical imports explicitly and seeds the same approval ID used in its token.
It leaves provider validation intact and exposes an intentionally wrong seed as
a regression control. Five tests require both the decision and the boundary:
normal confirmation, common-origin review, stale evidence, authenticated false
facts, and provider approval mismatch.

From the repository root:

```bash
PYTHONPATH="$PWD" python3 -m unittest discover -s papers/agent-safety/earned-trust/integration -v
```

The original files, failed expectations and checksums remain untouched in
`cycles_001_009/`. This adapter does not retroactively make that original suite
green.

## What remains open

- Provenance REVIEW in this bridge occurs **after the synthetic provider effect**;
  it does not prevent that effect or demonstrate remote rollback.
- Independent source labels and human approval are trusted laboratory fixtures.
  Authenticated, distinct sources still confirm the authored false-world case.
- Stolen issuer secrets and valid bearer capabilities remain successful attacks.
- Split-process signer/provider isolation, non-root equivalent containment,
  independently maintained source registries and external evaluation are unbuilt.

The corrected bridge reaches real Framework classes, but this remains one
bounded integration experiment rather than full-system security validation.
