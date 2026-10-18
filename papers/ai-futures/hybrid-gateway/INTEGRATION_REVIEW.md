# Hybrid Gateway v1.2 integration review

**[SCAFFOLD] Research prototype · 18 October 2026**  
Creator: Mackenzie Conor James Clark. Review: Caelorynth / Codex.

## Reproduced

- All **138 source files** match the incoming candidate's bytes.
- All **57 Python files** parsed successfully as syntax trees.
- **264 methods passed, no failures or skips**, on Python 3.12 with host loopback
  available. The initial sandbox run had 17 socket-permission errors; it was not
  counted as a pass or hidden by excluding HTTP tests.
- [Structured suite evidence](../../../28_DEFENSE/evidence/research-intake-2026-10-18/suite-results.json)
  records the actual collected count.

The release's original complete-tree manifest remains in `v1.2/SHA256SUMS.txt`;
the Framework's intake gate additionally checks all imported bytes. The nested
GitHub workflow is historical source and is **not an active root workflow** merely
because it exists in a research subdirectory.

## Claims kept narrow

The supplied strong SQL baseline ties on all four authored questions; the weak
latest-known comparison is not the principal baseline. All data are synthetic.
The optional neural adapter has stub/local HTTP tests; no real-model accuracy,
throughput, token cost or operator benefit was measured in this integration.

Witness custody remains an external assumption. An attacker controlling both
the database and retained witness can defeat the comparison. HMAC records do
not authenticate real reviewer attention. CASCADE adapter tests use a toy engine,
not a demonstrated canonical CASCADE integration.

## Placement and continuation

The current home is a Framework research subtree with its existing MIT credit.
The earlier standalone-repository proposal is preserved, not executed. No new
package export, command, live review server or external model call is introduced.

The next useful experiment is independently retained witness export and recovery,
followed by matched evaluation on independently prepared evolving documents.
Real operator consent, review time and error rates belong in that evaluation.
