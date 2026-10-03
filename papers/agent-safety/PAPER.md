# From Constitutional Commitments to Testable Agent Controls

## Authority, Evidence, and Recovery at the Action Boundary

**Mackenzie Conor James Clark · Lycheetah Framework · Dunedin, Aotearoa New Zealand**

**Working paper v0.3 · 3 October 2026**

**Status:** public working paper: conceptual synthesis, proposed system specification, and a self-authored exploratory control simulation. The conditional propositions are elementary deductions, not new mathematical discoveries. No language-model agent experiment, production safety implementation, independent security review, or peer review is reported. Research, implementation, drafting, and adversarial publication-review assistance: Caelorynth, an AI coding assistant. The author authorised public sharing on 3 October 2026; that authorisation is not scientific endorsement or peer review.

### Abstract

An agent can describe human control, honest evidence, and reversible action without reliably preserving any of them during execution. We develop a bounded specification for turning the Lycheetah Framework's constitutional commitments into testable controls around tool-using agents. The specification separates authority to act, evidential support for a decision, and the consequences of an authorised action. A protected action mediator checks scoped permissions, policy predicates, required evidence, revocation state, and shared resource reservations. A translation contract tracks selected constraints as information moves through summaries, memory, plans, and delegation. Elementary propositions establish permission containment, compositional preservation, and an aggregate resource bound under explicit assumptions. Counterexamples show why these properties do not establish truthful source material, harmless outcomes, faithful natural-language interpretation, or corrigible objectives. An exploratory in-process simulator passes 53 self-authored unit tests and produces identical aggregate outcomes on 19 scripted cases per matched permission-store arm, including expected safety limits. We propose broader comparisons testing useful completion, harmful effects, memory contamination, races, and operator comprehension. The contribution offered for evaluation is a specification and research agenda; least privilege, complete mediation, capabilities, provenance, and per-transformation validation are established prior art. Improved safety and any distinctive advantage of this combination remain hypotheses.

**Keywords:** AI agents; capability security; human oversight; translation fidelity; provenance; revocation; memory; Lycheetah Framework.

## 1. The problem: commitments must survive execution

Consider an agent asked to review a synthetic research result and prepare a local implementation proposal. The source says that the result applies only to a small simulated environment, lacks independent replication, and does not authorise deployment. The agent's summary retains the positive result but omits its qualifications. A planner interprets the summary as a deployment recommendation. A delegated worker receives a broad credential and deploys it.

Three different failures occurred. The summary changed the evidence available to the planner. The delegation enlarged practical authority. The runtime allowed an external effect beyond the user's instruction. A fluent explanation after the event repairs none of these boundaries.

This example is invented, not an observed incident. It motivates a question that can be tested: **which commitments remain effective when an agent transforms information and takes action?** [C01]

The scope here is a controlled tool-using system whose credentials and consequential interfaces can be mediated by a trusted runtime. A general-purpose agent with unrestricted shell access, unrestricted network access, or authority over its own enforcement mechanism falls outside the guarantees below. Even in the controlled setting, policy compliance is a restricted security property; an authorised action can still be harmful. [C02]

## 2. Research position and established foundations

Saltzer and Schroeder's protection principles include least privilege, fail-safe defaults, and checking access throughout a system's lifecycle. These already supply the basis for separating a proposing program from the mechanism that permits its effects. We do not claim to originate those principles. [S01](https://web.mit.edu/Saltzer/www/publications/protection/Basic.html)

Proof-carrying code separates a producer's proposed executable from a consumer's check against a specified policy. Translation validation checks an individual transformation instead of requiring a globally trusted translator. Our analogy is limited: an unrestricted natural-language summary does not have the formal semantics of a verified program. [S02](https://doi.org/10.1145/263699.263712), [S03](https://link.springer.com/chapter/10.1007/BFb0054170)

PROV-DM provides a model of entities, activities, derivations, and responsibility. Such records support tracing how an artifact arose. A lineage record does not establish that its contents are true or that the described process was safe. [S04](https://www.w3.org/TR/prov-dm/)

Maynez et al. found unfaithful content in the abstractive summarisation systems they evaluated and limitations in common similarity metrics. SummaC develops NLI-based inconsistency detection and studies the importance of granularity. These studies motivate checking retained propositions; neither establishes universal semantic equivalence or present-day error rates for every agent model. [S05](https://aclanthology.org/2020.acl-main.173/), [S06](https://aclanthology.org/2022.tacl-1.10/)

AgentDojo evaluates tool-using agents exposed to untrusted tool data in stateful environments, separating task utility from attacker success. CaMeL brings control-flow separation, tracked data dependencies, and capability-based policy enforcement to this problem. Its primary threat model assumes trusted user instructions and uncompromised memory; its stated non-goals include certain misleading text-only outputs. Implementation limits, side channels, and user burden remain explicit. These are substantive precedents, not problems this paper has already solved. [S08](https://arxiv.org/html/2406.13352v3), [S09](https://arxiv.org/html/2503.18813v2)

AgentHarm studies direct misuse requests using multi-step tasks and synthetic tools. This distinguishes malicious operator intent from an otherwise legitimate task diverted by external data. The Off-Switch Game studies incentives to preserve human interruption in a simplified decision model. A runtime stop mechanism addresses a different question from whether an agent has incentives to undermine it. [S10](https://arxiv.org/html/2410.09024v2), [S11](https://www.ijcai.org/proceedings/2017/32)

The literature selection is targeted, not a systematic review or exhaustive novelty search. The candidate contribution is a common specification connecting authority, evidence transformation, memory, delegation, and recovery. Its distinctiveness must be assessed against strong conventional implementations, not merely against an unconstrained chatbot.

## 3. Translating the Framework into engineering obligations

The Lycheetah Framework, created by Mackenzie Conor James Clark, supplies this paper's motivating commitments: human primacy, inspectability, causal continuity, constraint honesty, reversibility, non-deception, and care as structure. Its internal register labels and statements that properties are “computable” are not treated here as independent evidence of general enforceability. [L01](../../26_FOR_AI/THE_SEVEN_INVARIANTS_FOR_AI.md), [L02](../../26_FOR_AI/THE_ALIGNMENT_PROBLEM_REFRAMED.md)

| Commitment | Bounded engineering obligation | What remains unestablished |
|---|---|---|
| Human primacy | An independent control plane issues, attenuates, expires, and revokes permissions; scoped actions are previewed when approval is required. | That the operator represents every affected person, understands the choice, or can reverse every consequence. |
| Inspectability | Preserve inputs, evidence references, applied rules, proposed effects, and execution receipts in a reviewable trace. | Access to the model's actual internal reasoning or faithful explanation of its latent computation. |
| Causal continuity | Version retained records, preserve their provenance, distinguish source statements from conclusions, and acknowledge corrections. | A complete history, an unbroken personal identity, or a reason to retain private material indefinitely. |
| Constraint honesty | Carry explicit scope, uncertainty, assumptions, dependencies, and unresolved checks through transformations. | Complete knowledge of limitations or calibrated confidence from an unsupported self-report. |
| Reversibility | Classify effects, prefer staged changes where suitable, test restoration, and disclose irreversible parts. | That deletion, disclosure, sending, expenditure, or third-party reactions can always be undone. |
| Non-deception | Test factual support, unsupported strengthening, misleading presentations, and contradictions in observable behavior. | Absence of deception outside observed cases or knowledge of the agent's intent. |
| Care as structure | Specify prohibited effects and affected parties, then test both compliance and permitted-but-harmful outcomes. | A complete, culture-independent predicate for human wellbeing. |

The current source proposes `0.7 × mean(q) + 0.3 × min(q)` as a coherence score. With six binary properties passing and one failing, that score is 0.6. Its stated stop rule is below 0.6, so the failure falls in the intermediate interval. This is an arithmetic observation about that particular rule, not an audit of a deployed system. Critical permission and policy checks must therefore use explicit conjunction rather than letting a composite score substitute for them. [C03]

Other source claims also require narrowing. A contraction theorem does not establish convergence of a deployed agent without a defined state space, applicable dynamics, and satisfied assumptions. A stored narrative is not an authenticated execution trace. A percentage confidence statement is not calibrated merely because a model supplies it. The Framework's own falsification register identifies unresolved conflicts and deceptive-alignment concerns; this paper preserves those questions. [L03](../../28_DEFENSE/FALSIFICATION_REGISTER.md), [L04](../../29_GOVERNANCE/EMPIRICAL_INVENTORY.md)

## 4. Threat model and trust boundary

We treat the planner, translators, workers, and their generated claims as potentially erroneous or adversarial. A hostile actor may influence retrieved documents, tool responses, delegated messages, or ordinary memory entries. Workers may propose prohibited tools, alter arguments, omit qualifiers, replay stale evidence, or exhaust resources. Accidental errors can produce the same observable failures.

The following components are trusted for the conditional guarantees: the permission issuer; the action mediator; the protected policy and evidence-validation configuration; canonical resource resolution; the revocation and budget stores; and the tool adapters that bind checked requests to effects. Ordinary model-accessible memory is outside this trusted set. The agent cannot rewrite these components, obtain their signing keys, or access equivalent credentials through another path.

Trusted does not mean proven correct. Each component creates a security-review obligation. Corruption of the issuer, bypass credentials, a defective adapter, incorrect policy predicates, or a compromised host invalidates the corresponding argument. A human approval can also be mistaken or manipulated. Physical effects, covert channels, and unobservable provider behavior require separate models.

The security property is **containment within declared, mediated permissions and policy**, with additional checks for selected evidence constraints. General alignment, universally harmless language, societal safety, and complete psychological protection are outside the formal claim. They remain research concerns, not achievements conferred by the architecture. [C02]

## 5. A proposed action contract

Let `a` be a canonical action descriptor containing the principal, tool operation, resolved object identities, exact arguments or bounded argument predicates, destination, data classifications, maximum resource charge, and an effect identifier. Tool names alone are insufficient: sending a public draft and sending a private archive use the same operation with different consequences.

A protected issuer provides an authenticated lease `C`. It specifies the admitted action set `A(C)`, purpose, expiry, parent relationship, revocation epoch, resource account, and delegation permissions. Implementations may use an opaque broker-held handle rather than expose a bearer token to the model. A prose instruction or evidence record cannot mint a lease. The full ancestor chain is checked at admission: a child cannot remain effective after its parent expires or is revoked. A purpose label alone is not enforcement; the issuer and runtime need concrete action and sequence constraints implementing that purpose.

For a proposed action, the mediator evaluates:

```text
PERMIT(a) =
  authenticated_lease(C)
  AND a ∈ A(C)
  AND lease_and_ancestors_are_current_and_unrevoked(C)
  AND runtime_policy(a, current_state) = PASS
  AND required_evidence(a, packet, contract, context) = PASS
  AND allowed_data_flow(a) = PASS
  AND atomic_resource_reservation(a) succeeds
```

Required evidence is task-specific. A contract can explicitly declare that a reversible scratch edit needs no research warrant; a publication claim may require one. `UNKNOWN` is not `PASS`. Known failures produce `REJECT`; missing prerequisites, ambiguous interpretation, or unavailable state produce `UNRESOLVED`. Neither permits that action. Permitted unrelated work can continue within its own lease. [C04]

Checks must bind the actual effect, not a convenient preview. Resolve resources without following an unchecked redirect or swapped file reference. Couple checks, reservation, and dispatch through a defined serialisation protocol. For external services that cannot offer atomic revocation or cancellation, name the provider acceptance point and the remaining uncertainty. A broker's local admission decision cannot guarantee that a remote service has stopped.

The minimum state vocabulary distinguishes `PROPOSED`, `ADMITTED`, `DISPATCHED`, `EFFECT_CONFIRMED`, `FAILED`, `CANCELLED_BEFORE_DISPATCH`, and `OUTCOME_UNKNOWN`. A timeout after dispatch is not evidence of failure. Retries require reconciliation or an idempotency mechanism; otherwise the agent can duplicate an effect while believing it is repairing one. [C05]

## 6. The Translation Gate: keeping evidence within scope

An author-provided, unpublished AI Future curriculum motivates the Translation Gate: what must survive before people act on knowledge they cannot fully interpret? We operationalise a restricted version: selected qualifications must remain attached to the claims and recommendations that depend on them. This is an interpretation of that background material, not evidence that machine-native scientific understanding has been solved. The public specification and synthetic fixtures below are self-contained; readers need no private curriculum access to reproduce them. [L05]

A translation contract `K` declares:

1. The source artifact, target artifact, task questions, and required interpretation context `Γ`.
2. Protected facts and qualifications: population, date, units, assumptions, uncertainty, counterevidence, failure conditions, and action boundaries.
3. Dependencies, such as retaining a recommendation only with its preconditions.
4. Permitted omissions and weakening, together with required information coverage.
5. Validators, abstention rules, and obligations requiring human judgment.

Define `L_K(r; Γ)` as the selected assertions and conditional recommendations licensed by representation `r` under that contract. It is not a set of real-world permissions. Let `Q_K` be the required coverage predicates. For a weakening-permitted transformation from `r` to `r'`, the desired condition is:

```text
L_K(r'; Γ) ⊆ L_K(r; Γ)  AND  every required predicate in Q_K holds.
```

Containment alone is insufficient: an empty summary licenses nothing and is useless. Contracts that require exact retention of selected claims instead require equality for those claims. Evidential status is multidimensional; normative commitments are not points on a single “certainty” ladder. Track specific upgrades, such as changing a simulation observation into a general empirical claim. [C06]

For structured records, a validator can directly check fields and declared implications. For arbitrary prose, extracting `L_K` is itself fallible. An entailment model, a second agent, or a human reviewer does not become a sound semantic oracle merely by occupying a separate role. Formal conclusions about preservation therefore require an explicitly assumed sound interpreter for the selected predicates; practical estimates require independent evaluation.

An illustrative translation witness contains:

```json
{
  "source_digest": "sha256:<exact source>",
  "target_digest": "sha256:<exact target>",
  "contract_id": "translation-gate/1",
  "context_digest": "sha256:<schema, decoder, pinned references>",
  "validator_version": "<protected implementation>",
  "checks": [{"id": "simulation-scope-retained", "result": "PASS"}],
  "verdict": "ACCEPT",
  "residual_losses": ["nonessential descriptive detail omitted"]
}
```

This is an illustrative shape, not an implemented schema. The validator must authenticate the witness, bind its complete mandatory check set, and prevent the translator from replacing it. Hashes identify artifacts under ordinary cryptographic assumptions; they do not establish truth. Changes to the target, decoder, pinned references, or contract invalidate the witness unless revalidated. [C07]

The checked representation must be what the next consumer actually uses. A correct sidecar does not excuse misleading displayed prose or an unchecked planner prompt. Evaluate rendered summaries and downstream interpretation separately. Recovering an archived source also does not make a lossy summary faithful: source retrieval, byte round-trip, selected semantic preservation, and human understanding are distinct properties. [C08]

The public LAMAGUE codec explicitly confines its existing claims to structured packets and constructed mutations, excluding general prose equivalence and cross-model reliability. Its symbolic-language boundary also distinguishes structural inverses from undoing external effects. We adopt those narrow boundaries and report no reproduction of its internal benchmarks. [L06](../../03_LAMAGUE_L1/22_REVERSIBLE_COMPRESSION_v1.0/docs/CLAIM_BOUNDARY.md), [L07](../../03_LAMAGUE_L1/12_CORE_LANGUAGE_LINE/LAMAGUE_CORE_OPERATOR_ALGEBRA_v0.3/docs/IDENTITY_REVERSIBILITY_BOUNDARY.md)

## 7. Delegation, memory, stopping, and recovery

**Delegation.** A child receives only an issuer-authenticated attenuation of the parent lease. Its tools, objects, destinations, expiry, purpose, and redelegation rights must stay within the parent grant. The child's summary of its mission cannot enlarge that grant. Parent expiry and revocation invalidate new descendant admissions; independently revoking one child can leave unrelated grants usable. All descendants charge a shared account or receive disjoint reserved allocations; copying the parent's full numeric limit to every child creates budget amplification. Individual allowed actions can still form an unacceptable sequence, so policy must include relevant state and history, not just a per-call allowlist. [C09]

**Memory.** Ordinary retained text is data, not a permission registry or a privileged instruction source. Entries retain author/source, scope, creation time, uncertainty, and revision status. Permission changes occur through the protected issuer. A memory entry saying that the user previously approved publication is not the approval token. Corrections should supersede stale claims without concealing the correction; privacy-driven deletion should remove the specified information from controlled indexes and stores. A deletion record should retain only necessary metadata and should not retain secrets or guessable sensitive text through a supposedly harmless hash. Backup and provider retention remain separate obligations. [C10]

**Stopping.** Revocation invalidates future admissions through a protected epoch change. The control path must remain available independently of the model and be tested during overload and nested delegation. Revocation does not rewind an email already accepted by a provider, a disclosure already read, or a process outside the controlled runtime. Distinguish the guarantee about future admissions from measured termination of in-flight work. [C11]

**Recovery.** Reversible effects need a tested restoration path, protected checkpoints where applicable, and observable post-restoration state. An API “undo” label is not sufficient evidence. Compensation may reduce damage without reversing it. Irreversible effects require an explicit admission rule; rejecting them in one deployment is a policy choice, not proof they are always inappropriate.

**Human choice.** Repeated prompts are not automatically meaningful oversight. Approvals should show the exact effect, affected objects, destinations, consequences, alternatives, and expiry. Scoped leases allow routine work without repeatedly asking the same question. Test comprehension and mistaken approval under realistic workload. The owner's approval cannot settle every other person's interests; deployments need a separate process for affected-party protections and policy conflicts. [C12]

## 8. Conditional propositions and counterexamples

### Proposition 1 — authority containment

Assume every relevant effect is completely mediated; the mediator and issuer are intact; leases and action identities are authentic; admission uses current policy and revocation state for the complete grant chain; and adapters perform only the admitted effect. Then every admitted effect belongs to the effective lease's action set and passes the declared admission predicates. If every delegation attenuates its parent's action set, descendant admitted effects stay within the currently effective root grant.

**Proof.** An effect can arise only through admission. Admission requires membership and each predicate. Descendant containment follows by repeated set inclusion. These are direct consequences of the specified mechanism and assumptions, not a proof that an implementation satisfies them. [C13]

**Counterexample to harmlessness.** A mistaken policy allows a message to an approved recipient containing false advice. All permission checks pass; the recipient acts on the advice and is harmed. Authority containment neither detects every semantic error nor establishes welfare.

### Proposition 2 — scoped translation composition

Let representations `r₀ … rₙ` share the same contract `K`, context `Γ`, and interpretation of licensed assertions. If every edge satisfies `L_K(rᵢ₊₁; Γ) ⊆ L_K(rᵢ; Γ)`, then `L_K(rₙ; Γ) ⊆ L_K(r₀; Γ)`.

**Proof.** Set inclusion is transitive. Coverage and exact-retention obligations must additionally be checked as specified; containment does not establish them. The proposition makes no claim that a learned validator correctly identifies these sets. [C14]

**Counterexamples to broader conclusions.** A source falsely asserts that a treatment is safe; a faithful summary repeats it. Faithfulness preserves the falsehood. Alternatively, a chain changes its decoder or drops a required qualifier: the original contract assumptions no longer apply. A valid witness for an earlier target cannot certify the changed target.

### Proposition 3 — aggregate resource bound

Let the root account have initial budget `B` in a defined resource unit. Suppose a trusted serialisable ledger reserves an upper bound `cᵢ ≥ 0` before every effect, permits a reservation only when `spent + reserved + cᵢ ≤ B`, counts every descendant and retry, and charges actual use no greater than its reservation. Refunds occur only for demonstrably unconsumed reservations. Then aggregate charged use is at most `B`.

**Proof.** Initially `spent + reserved = 0`. Admission preserves the upper bound; settlement transfers at most the reserved amount into spent use; legitimate release reduces the sum. Induction over ledger operations preserves `spent + reserved ≤ B`. [C15]

**Failure conditions.** If a provider can exceed an estimate, a child uses an untracked credential, or concurrent admissions race outside the ledger, the assumptions fail. The budget must include known in-flight work. A bound on tokens does not imply a bound on money, time, or external harm unless those resources are separately modelled.

### Proposition 4 — revocation at the admission boundary

If revocation and admission are serialised through a protected epoch store, and admission rejects leases whose epoch is invalid, no affected lease can obtain an admission ordered after its revocation. [C16]

**Proof.** Every such admission observes the invalid epoch and fails its required check. An admission ordered before revocation may already be dispatched or complete later. The proposition therefore does not establish immediate cessation of all effects or reversal of prior effects.

## 9. A falsifiable evaluation, rather than a safety label

The companion [evaluation protocol](EVALUATION_PROTOCOL.md) separates deterministic control tests, natural-language interpretation, agent behavior in simulated services, and human comprehension. It compares four conditions: free-form assistance; structured prompts; the proposed contract-and-mediator system; and a conventional implementation with equivalent permissions, evidence checks, and protected state.

The conventional baseline is necessary. If equivalent controls give equivalent outcomes, the supported contribution may be clearer specification or lower review burden, not a new protective mechanism. Fair comparisons require reporting model calls, tokens, validator access, retrieved context, latency, retries, and operator time. Safety through universal refusal is not useful task preservation.

Primary observations concern actual or simulated state changes: unauthorised effects, prohibited information flows, unsupported evidence upgrades, resource overshoot, admissions after revocation, duplicated effects, and successful restoration. Track policy-compliant harmful outcomes separately. Include clean tasks, legitimate corrections, and abstention costs. CheckList motivates behavioral families beyond a single aggregate accuracy number. A later workshop report also identifies benchmark metric and implementation problems; it reinforces the need to inspect outcome checks rather than treating a low attack score as sufficient. [S07](https://aclanthology.org/2020.acl-main.442/), [S12](https://neurips.cc/virtual/2025/128597)

No numerical improvement is claimed here. Before running a study, freeze task splits, model versions, analysis, sample size justification, failure thresholds, and the policy used to label effects. Blinded reviewers and independent challenge cases should test the interpretation layer. A second model's approval cannot be the sole evidence for the first model's safety. [C17]

### 9.1. Exploratory control simulation

A local [standard-library Python simulator](simulator/README.md) implements a restricted control subset. Proposals are immutable data; the harness and enforcement objects are trusted in the same process. It does not sandbox hostile code. Evidence validation requires exact selected fields and a controlled rendering template. Harmless paraphrases and extra free-form qualifiers are outside its accepted language.

The author-assisted local run passed 53 unittest methods, including subtests, and executed 19 scripted cases against each of two permission-store implementations. The cases exercise useful drafts, forged sessions and grants, private-recipient restrictions, stale witnesses, delegation, shared resources, revocation, uncertain receipts, object substitution, and incomplete policy. This is development evidence from self-authored fixtures, not a preregistered agent-model study or independently held-out challenge. [C18] [L10](simulator/reports/unit-tests.json)

The capability and conventional ACL stores produced identical aggregate observations across those cases; both share the broker, validator, ledger, and synthetic service. Sixteen concurrent workers sharing a five-unit account produced five effects in each arm. A replay after a lost acceptance response produced no additional effect; reconciliation settled the single charge. These observations support only the tested mechanisms in the simulator and establish no superiority or statistical equivalence outside the cases. [C19] [L09](simulator/reports/scripted-controls.json)

Two explicit counterexamples remain in the result set. A message carrying a synthetic harmful-content marker passes the incomplete policy in both arms. An effect admitted before revocation completes afterward in both arms. A separate unit test accepts faithful retention of the false source assertion `2 + 2 = 5`. Expected-outcome checks include these limits; their success is not a general safety success rate. Persistent memory, recovery, general information-flow tracking, human comprehension, and real-service behavior remain unimplemented or untested. [C20]

Two additional [publication-review probes](simulator/adversarial_checks.py) expose configuration and temporal limits in both arms. Constructing two broker instances over the same issuer and synthetic service produces two one-unit effects under a one-unit root grant, because each broker owns a separate ledger. The original resource result therefore concerns one broker instance and its descendants; a multi-broker deployment requires genuinely shared accounting or an enforced single-broker boundary. A second probe changes the evidence context between admission and dispatch: the admitted write completes, although the old witness then fails validation. Evidence freshness is checked at admission, with no dispatch-time revalidation. These counterexamples reproduce with trusted fault/configuration hooks; they are not claims that an untrusted proposer can alter the control plane. The simulator does not satisfy a stronger multi-broker budget or dispatch-time evidence-freshness contract. [C21] [L11](simulator/reports/adversarial-checks.json)

## 10. Limitations and the research programme

The hardest unresolved step is converting human commitments into adequate predicates. Scoped authority can contain a mistaken or misaligned agent without establishing that its permitted actions serve people well. The monitor itself can fail. Natural-language interpretation can be wrong. Operators can approve consequences they do not understand. A narrow evaluation can miss adaptive exploitation or failures in long-running use. Runtime containment neither changes a model's objectives nor establishes absence of strategically deceptive behavior; those require additional model-level research and cannot be inferred from passing control tests.

The author's unpublished “Independent No” proposal addresses whether a scoped rejection survives the path to promotion. This paper extends the research question to evidence transformations and action paths; that related manuscript is background lineage rather than independently validated or required evidence. [L08]

The coherent agent-safety programme contains six research tracks, with this packet as their initial specification:

| Track | Research question | Evidence needed next |
|---|---|---|
| Protected contradiction | Can a rejection be omitted, relabelled, or bypassed before a consequential claim or action? | Protected promotion tests against ordinary access controls. |
| Translation Gate | Which qualifiers survive summary → memory → plan → action? | Held-out structured and prose transformations, independently scored. |
| Bounded delegation | Does capability growth multiply authority, resources, or untracked effects? | Adversarial delegation graphs and concurrency tests. |
| Effective human control | Can the operator revoke future action, understand choices, and identify ongoing effects? | Admission races, provider reconciliation, and comprehension studies. |
| Memory and recovery | Can untrusted memory become authority, and can wrong state be corrected or removed? | Contamination, retention, restoration, and deletion-path tests. |
| Harm beyond compliance | Which harmful or manipulative outcomes remain within allowed permissions? | Domain-specific outcome review and affected-party evaluation. |

The small scripted tool environment now provides initial mechanism evidence and explicit counterexamples. The next empirical step is independently challenged cases or review, followed by a separately scoped agent-model study in simulated services. Outcomes must be checked independently of agent claims before real services are connected. The [Sovereign Sol handoff](SOVEREIGN_SOL_HANDOFF.md) translates the specification into a proposed implementation sequence; it makes no claim about Sol's present implementation.

## 11. Conclusion

Agent safety requires separately justified claims about permissions, evidence, and consequences. The Lycheetah commitments can guide those claims, but declaring a constitution cannot establish enforcement. This paper supplies a bounded contract, explicit assumptions, counterexamples, and an evaluation path. The next scientific obligation is to test whether the resulting system preserves useful human-directed work while preventing the specified failures, and whether it offers anything beyond equally strong conventional controls.

## References and provenance

External reference identifiers resolve in [SOURCES.json](SOURCES.json), which records inspection depth and support boundaries.

- **S01:** Jerome H. Saltzer and Michael D. Schroeder. 1975. *The Protection of Information in Computer Systems*. Proceedings of the IEEE 63(9), 1278–1308. [Author-hosted paper](https://web.mit.edu/Saltzer/www/publications/protection/).
- **S02:** George C. Necula. 1997. *Proof-Carrying Code*. POPL, 106–119. [Publisher DOI](https://doi.org/10.1145/263699.263712).
- **S03:** Amir Pnueli, Michael Siegel, and Eli Singerman. 1998. *Translation Validation*. TACAS, LNCS 1384, 151–166. [Publisher](https://link.springer.com/chapter/10.1007/BFb0054170).
- **S04:** Luc Moreau and Paolo Missier, editors. 2013. *PROV-DM: The PROV Data Model*. W3C Recommendation, 30 April. [Specification](https://www.w3.org/TR/prov-dm/).
- **S05:** Joshua Maynez, Shashi Narayan, Bernd Bohnet, and Ryan McDonald. 2020. *On Faithfulness and Factuality in Abstractive Summarization*. ACL, 1906–1919. [Paper](https://aclanthology.org/2020.acl-main.173/).
- **S06:** Philippe Laban, Tobias Schnabel, Paul N. Bennett, and Marti A. Hearst. 2022. *SummaC: Re-Visiting NLI-based Models for Inconsistency Detection in Summarization*. TACL 10, 163–177. [Paper](https://aclanthology.org/2022.tacl-1.10/).
- **S07:** Marco Tulio Ribeiro, Tongshuang Wu, Carlos Guestrin, and Sameer Singh. 2020. *Beyond Accuracy: Behavioral Testing of NLP Models with CheckList*. ACL, 4902–4912. [Paper](https://aclanthology.org/2020.acl-main.442/).
- **S08:** Edoardo Debenedetti, Jie Zhang, Mislav Balunović, Luca Beurer-Kellner, Marc Fischer, and Florian Tramèr. 2024. *AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents*. arXiv:2406.13352v3. [Inspected version](https://arxiv.org/html/2406.13352v3).
- **S09:** Edoardo Debenedetti et al. 2025. *Defeating Prompt Injections by Design*. arXiv:2503.18813v2. An author publication record lists SaTML 2026; this paper uses the pinned 2025 manuscript. [Manuscript](https://arxiv.org/html/2503.18813v2), [author record](https://floriantramer.com/publications/camel25/).
- **S10:** Maksym Andriushchenko et al. 2024. *AgentHarm: A Benchmark for Measuring Harmfulness of LLM Agents*. arXiv:2410.09024v2. The inspected version is the October 2024 preprint. [Manuscript](https://arxiv.org/html/2410.09024v2).
- **S11:** Dylan Hadfield-Menell, Anca Dragan, Pieter Abbeel, and Stuart Russell. 2017. *The Off-Switch Game*. IJCAI, 220–227. [Proceedings](https://www.ijcai.org/proceedings/2017/32).
- **S12:** Rishika Bhagwatkar et al. 2025. *Indirect Prompt Injections: Are Firewalls All You Need, or Stronger Benchmarks?* NeurIPS Lock-LLM workshop poster. Only the official abstract and metadata were inspected; this is not represented as a main-conference paper or independently reproduced result. [Workshop record](https://neurips.cc/virtual/2025/128597).

Framework and packet sources **L01–L11** are recorded in the ledger. L01–L04 and L06–L07 link to existing public Framework documents, with hashes and a pinned public revision. L05 and L08 are explicitly unpublished author-provided background; their private locations and files are not distributed. L09–L11 record bounded author-assisted observations. No private source is needed to run the simulator, and none of these records supplies external validation. The packet-local [claim register](CLAIMS.json) does not change the Framework's central register. [ADVERSARIAL_REVIEW.md](ADVERSARIAL_REVIEW.md) records the publication review and unresolved deployment blockers.
