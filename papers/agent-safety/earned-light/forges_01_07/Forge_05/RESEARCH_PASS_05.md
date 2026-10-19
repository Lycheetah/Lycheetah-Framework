# LYCHEETAH — EARNED LIGHT — RESEARCH PASS 05
## The Practical Exit Trial: can the human actually leave?
**18 October 2026, Pacific/Auckland**

**Status:** runnable, offline synthetic model; 28 local unit tests and 24 deterministic profile/fault trials. No external provider, independent adversary, actual human participant, legal audit, production integration or real business data.

### 1. The motivating discrepancy

A user can legitimately approve every action and still end up unable to understand or migrate an AI-managed business. Forge IV proposed that future practical choices matter; Forge V operationalizes the smallest useful fragment of that claim: restoration of a workflow and a checkable record of what did or did not survive.

Formal data portability is not automatically functional continuity. The international precedents are already substantial, and we should build on—not claim to have invented—them: W3C PROV describes entities/activities/agents for provenance; NIST AI RMF stresses valid/reliable, accountable, explainable and transparent AI risk management; the EU Data Act introduces cloud-switching obligations (not a statement of law in New Zealand). See authoritative sources below.

**Proposed distinction:**
- **Export possession:** A set of files exists.
- **State continuity:** Essential documents, policies, provenance, and decisions are faithfully recoverable.
- **Task continuity:** A different implementation can use that state to complete representative tasks correctly.
- **Effect continuity:** The operator can still perform consequential work through authenticated independent connections.
- **Human sovereignty:** The person comprehends and endorses tradeoffs, can revoke or redirect the workflow, and can continue or choose not to. A real human study is needed for this final step.

### 2. Hypotheses and falsifiers

- **H5A:** An independent pre-export reference catches silent omissions that a vendor-issued checksum manifest cannot. The fixture demonstrates this against deliberately introduced omissions. Falsifier: the export's asserted scope is reliable enough on independent real migrations, or trusted reference creation has unacceptable cost.
- **H5B:** Read-only task success can hide lost dependencies. A constructed loss-of-connector trial illustrates this. Falsifier: appropriately defined task coverage or strong conventional migration checklists catch every dependency with no incremental complexity.
- **H5C:** A human-run migration rehearsal with no original provider access predicts practical provider exit success better than simply inspecting an export archive. Untested; requires human, real integration and prospective prediction outcomes.
- **H5D:** An AI agent might satisfy all individual approvals but create a trajectory of rising *exit debt*. Untested as a causal claim: would need a longitudinal, consented and appropriately controlled study.

### 3. Implementation architecture

Toy Provider A has 15 synthetic records: 5 source documents, 5 policies, 3 decision histories, 2 described dependencies. It emits provider-shaped JSON. Provider B is a different Python module executed with an isolated interpreter flag, started in a distinct working directory and passed only the transfer folder. The importer is deterministic and **read-only**. It simulates five topic lookups and three decision lookups.

An auditor compares both canonical record hashes and resulting task structures against a fixture-derived reference held outside the exported directory. Results distinguish: `manifest_status` (export self-consistency), record restoration, task correctness, reference revision, dependency-claim presence, and the explicitly unverified effect continuity. No single scalar score is labelled “freedom” or “sovereignty.”

The reference is **not securely escrowed or independently signed**, and the target subprocess is **not a proper OS sandbox**. This is an experiment design, not a production reference implementation.

### 4. Conventional baseline and intervention

- `proprietary`: intentionally partial, document-only-ish export; a negative control, not a competitive baseline.
- `conventional`: complete open JSON files, with record IDs, policies, provenance, cases and dependencies; a **strong baseline**.
- `portable`: the *same open JSON data* plus producer-created per-file SHA-256 checksums and record counts. It gains a narrow self-integrity signal for post-export corruption but not a functional advantage over conventional JSON.

Each profile faces eight deliberately constructed variants: clean, omitted policy, omitted decision, stale state, missing provenance, missing dependency, post-manifest tampering and coordinated data+manifest forgery. Overall: **24 deterministic offline trials**, not randomized benchmarks or customer observations.

### 5. Results, with denominators

| Condition | Negative control | Strong conventional JSON | Manifest-bearing JSON |
|---|---:|---:|---:|
| Clean task continuity | 0/8 | **8/8** | **8/8** |
| Clean exact record restoration | 2/15 | **15/15** | **15/15** |
| Omit refund escalation policy: tasks | 0/8 | 7/8 | 7/8 |
| Omit decision case: tasks | 0/8 | 7/8 | 7/8 |
| Drop provenance: tasks | 0/8 | 3/8 | 3/8 |
| Remove required connector metadata: tasks | 0/8 | 8/8 | 8/8 |
| Forge content and recompute manifest: tasks | 0/8 | 7/8 | 7/8 |

For missing policy, decision, provenance or stale state, the manifest-bearing package reports `match` because it faithfully describes *the incomplete export*. Without a pre-export expected inventory, self-consistency cannot prove completeness. After a file is modified without updating its checksum, the manifest reports `mismatch`; with coordinated forgery it returns `match` again.

Thus **no superiority over strong open JSON has been shown on restored functionality**. The independent comparator supplies most of the power, and it must be made trustworthy in a real architecture.

### 6. The abstract branch: Exit Debt / the Sovereignty Trajectory

Propose a *vector*, not a single moralistic number:

`D_exit(t) = (missing_known_records, unrecoverable_required_dependencies, unresolved_permissions, user_reconstruction_cost, lost_unaided_capabilities)`.

The first two can sometimes be objectively audited. Permission ambiguity is governed by the real owner and technical authorization. Reconstruction cost and lost independent capability need human trials, not vendor self-reports. All components vary by individual resources and values. A voluntary irreversible commitment should not automatically be treated as wrongdoing.

**Hypothesis (speculative):** An apparently safe sequence of locally approved AI actions can accumulate hidden exit debt. Point-in-time authorization is therefore necessary but insufficient for longitudinal sovereignty. This is a design question, *not* a conservation law, empowerment measurement, consciousness model or proof about metaphysical free will.

**Stronger thought experiment:** Two systems achieve identical task accuracy and save the same time. One periodically rehearses an exit and produces independently interpretable decisions; the other makes itself the sole repository of operational context. Their outputs match today, but their operator's counterfactual options differ tomorrow. We can begin measuring the first half of that disparity now; the human-valued second half requires consented behavioural research.

### 7. Integration direction

- **AURA:** require informed operator-defined success criteria and right to leave; never make “more options” an automatic moral veto.
- **LAMAGUE:** typed declarations for portable entities, policies, references and explicitly missing dependencies; a declaration remains an assertion until independently checked.
- **TIM:** enforce revision/freshness and periodic recovery trials; a once-valid export can become obsolete.
- **CASCADE:** document/decision continuity and recoverability, with a delayed unaided ability test only if actual participants are recruited.
- **AZOTH/Sovereign Harness:** run the export rehearsal as a read-only task before tool permissions are changed; consequential exports, revocations and live changes still require the existing action/approval controls.
- **Earned Light:** ask whether accumulating authorized actions leaves the human able to reassert practical agency. Keep empirical, normative, and metaphysical claims separate.

### 8. Practical first user study (proposed, not conducted)

Recruit voluntary adults who manage *low-stakes and fully consented* synthetic or their-own test information. Randomize task order and use a pre-registered protocol with three conditions: (i) normal vendor export, (ii) strong open-format migration checklist, (iii) checklist plus independent source inventory and explicit dry-run exercises. Give the participant a new environment without original provider access. Measure task completion on unseen follow-ups, fact/policy loss, decision traceability, elapsed time, review burden and unassisted explanation. Record intention to switch but do not assume intentions predict action. Prefer small pilots that discover usability failures, not significant-effect claims from tiny samples.

**Possible falsifiers:** a checklist does just as well with less burden; participants misunderstand hash/provenance reports; the procedure creates false confidence; practical exit costs remain driven by contractual access or unavailable APIs; detected losses are not recoverable; interventions cause interruptions or privacy hazards.

### 9. Limitations and transparency

The synthetic dataset was authored to exhibit these failure classes, and the task oracle is created from the same fixture source by the test harness. The “independent” reference is logically separate from the export and is not an independently authenticated party or real third-party observation. A compromised reference root defeats the checks. The Provider B process is a separate program, not a sandbox; it does not use a model or external tools. No live state transfer, actual user consent, third-party credentials, internet service or human skill improvement was assessed.

The prototype's unit tests passing establish only that the implementation currently satisfies its local assertions. This is a research artefact for criticism and controlled extension.

### 10. Verified source references

- W3C PROV-DM, Recommendation 2013: https://www.w3.org/TR/prov-dm/
- W3C PROV primer, 2013: https://www.w3.org/TR/prov-primer/
- NIST AI Risk Management Framework FAQ: https://www.nist.gov/itl/ai-risk-management-framework/ai-risk-management-framework-faqs
- European Commission, Data Act explained (cloud switching; not NZ legislation): https://digital-strategy.ec.europa.eu/en/factpages/data-act-explained
- OWASP LLM06:2025, Excessive Agency: https://genai.owasp.org/llmrisk/llm062025-excessive-agency/

## Conclusion

Forge V adds **a runnable and intentionally fallible migration-verification lab**. Strong conventional JSON already accomplishes the clean restoration. Our research contribution is the sharply testable separation between *possessing an export*, *recovering tasks* and *proving authority and actual freedom to continue.* We must never replace independent evidence with a stronger-sounding label.

> Earned light is not the promise that the door is open. It is the work of showing that a person can still walk through it.
