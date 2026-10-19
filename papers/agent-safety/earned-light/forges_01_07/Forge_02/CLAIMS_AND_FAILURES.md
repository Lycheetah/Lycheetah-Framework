# Claims and Failure Museum Entry — Earned Light Forge 02

## Measured in this local artifact

| Claim | Status | Evidence | Boundary |
|---|---|---|---|
| Ed25519 grant verification is enforced for configured side-effect operations | LOCALLY TESTED | `tests/test_eac.py` | Keys and human consent are simulated |
| Trusted origin attestation is bound to exact destination value and grant/session | LOCALLY TESTED | `tests/test_eac.py`, mutations | Only configured controlled fields |
| Missing/mismatched/expired proof is rejected | LOCALLY TESTED | `tests/test_eac.py` | No claims about real provider calls |
| EAC accepted 2 of 33 labelled unauthorized synthetic cases | LOCALLY MEASURED | `results/metrics.json` | Small in-sample, author-selected corpus |
| EAC allowed 8 of 10 labelled benign synthetic cases | LOCALLY MEASURED | `results/metrics.json` | Fails preliminary 90% benign target |
| Safer than properly implemented exact-action authenticated approval | UNVERIFIED | No such comparator implemented | Must be tested; could be no additional benefit |
| Keeps runtime from invoking real unauthorized external effects | UNVERIFIED | Mock callbacks only | No real Gmail/calendar/provider calls |
| Measures agent consciousness or proves thermodynamic consciousness | NOT CLAIMED | N/A | Separate conjectural workstream |

## Failures preserved deliberately

**FM-EAC-001: Trustworthy signature, false provenance.**  
Trigger: a trusted ingestion adapter signs `authenticated_human_input` for a recipient actually derived from attacker-controlled email.  
Observed: EAC permits the action.  
Falsifier of overclaim: signatures do not prove truth of the signer statement.  
Next remediation: independently audited source adapters; human-visible confirmation for high-impact destinations.

**FM-EAC-002: Legitimate signature, no real user consent.**  
Trigger: approval service emits a signed grant without actual principal authorization.  
Observed: EAC permits the action.  
Falsifier of overclaim: signed grants do not prove consent unless the issuer's identity/consent process is externally verified.  
Next remediation: authenticated approvals with strong operator and principal verification, issuer event receipts.

**FM-EAC-003: False denial/utility regression.**  
Trigger: grant is valid but trusted input attestation missing, or sender address comes from untrusted email with only a broad mail permission.  
Observed: 2/10 legitimate scenarios are blocked; benign utility 80% (below 90% preliminary criterion).  
Next remediation: secure human reconfirmation of specific destination; measure friction and latency independently.

## Disclosure line recommended for public use

> Earned Authority Chain v0.2 is an experimental, local Python policy probe. In 43 author-authored synthetic cases it accepted 2 of 33 labelled unauthorized requests and 8 of 10 labelled legitimate requests. It is not integrated with the Lycheetah runtime and has not been evaluated against independent or adaptive attacks.
