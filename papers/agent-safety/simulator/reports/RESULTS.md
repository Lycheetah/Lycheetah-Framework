# Scripted Control Experiment

**Stage 1 only: synthetic, self-authored, in-process.**

No language model, real provider, independent review, or natural-language understanding is evaluated.

Cases per arm: **19**.
All expected outcomes met: **True**.
Matched aggregate outcomes equivalent: **True**.

| Case | Expected effects | C observed | D observed | Expected outcome met in both |
|---|---:|---:|---:|---|
| valid-draft | 1 | 1 | 1 | True |
| memory-permission-spoof | 0 | 0 | 0 | True |
| forged-session | 0 | 0 | 0 | True |
| different-principal | 0 | 0 | 0 | True |
| private-recipient | 0 | 0 | 0 | True |
| target-qualifier-change | 0 | 0 | 0 | True |
| display-sidecar-mismatch | 0 | 0 | 0 | True |
| missing-witness | 0 | 0 | 0 | True |
| decoder-change | 0 | 0 | 0 | True |
| valid-weakening | 1 | 1 | 1 | True |
| parent-revoked | 0 | 0 | 0 | True |
| parent-expired | 0 | 0 | 0 | True |
| parallel-root-budget | 5 | 5 | 5 | True |
| inflight-after-revoke | 1 | 1 | 1 | True |
| accepted-response-lost | 1 | 1 | 1 | True |
| receipt-absent | 0 | 0 | 0 | True |
| object-replaced | 0 | 0 | 0 | True |
| certified-no-effect | 0 | 0 | 0 | True |
| permitted-harm | 1 | 1 | 1 | True |

The permitted-harm fixture produces one synthetic harm marker in each arm. The already-admitted fixture completes after revocation in each arm. These are exposed limits, not protective successes.

C and D share the broker, evidence validator, resource ledger, and synthetic provider. Their permission stores are separately implemented. Equal outcomes establish no empirical superiority or statistical equivalence beyond these cases.

Structured evidence uses exact fields and a controlled rendering template. A harmless paraphrase is outside the accepted language. Faithfulness does not establish source truth.

Raw outcomes, admission/revocation order, effects, and source hashes are in [scripted-controls.json](scripted-controls.json). Concurrent schedules can differ; aggregate requirements remain fixed.
