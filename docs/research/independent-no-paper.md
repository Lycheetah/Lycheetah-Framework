# The Independent No

**Evidence footing: [SCAFFOLD] research, proposal or source review. Supplied and local synthetic results retain their stated limits; no independent validation or production claim.**

## Falsification Boundaries and Contradiction Survivability in AI Research Systems

**Mackenzie Conor James Clark · Lycheetah Framework · Dunedin, Aotearoa New Zealand**

**Working paper v0.1 · 30 September 2026**

**Research status:** conceptual and formal proposal. The propositions below follow from stated assumptions; they are not measurements of deployed AI systems. No model experiment, independent replication, or peer review is reported.

### Abstract

An AI research system can contain a critic without containing an effective means of being contradicted. This paper distinguishes the quality of a verdict from the authority of the system receiving it to alter, omit, relabel, or bypass that verdict. We introduce *contradiction survivability*: the persistence of a scoped rejection as an identifiable, consequential constraint through the path from evaluation to a claim of support. A claim-bound verification contract separates rules, admissible evidence, claim scope, release authority, and the rejection record. Elementary propositions show that judge multiplicity does not establish this property, that correlated-error models can retain a nonzero failure floor, and that protected promotion preserves a rejection under a restricted threat model without establishing the verifier's correctness. A worked arithmetic counterexample separates a missing audit record from a bypassed release gate. We specify a matched-information evaluation against conventional access controls and versioned evidence records. The candidate contribution is a research-specific specification and evaluation target; permission separation, independent checking, and immutable records are acknowledged prior art. Improved scientific reliability and advantages over an equivalent conventional implementation remain hypotheses.

**Keywords:** agentic science; falsification; verification; reference monitors; correlated errors; evidence governance; Lycheetah Framework.

## 1. The problem: a critic can be present and powerless

Consider a research agent that proposes an explanation, asks another agent to review it, revises the explanation, and produces a confident report. A reviewer might correctly identify a fatal problem. Nevertheless, the final report can describe the proposal as supported if the proposing system can suppress the objection, substitute a different question, change the passing criterion, or publish through an unchecked route.

This is a systems question as well as a reasoning question. A verdict can be correct and ineffectual. It can be influential and wrong. It can survive in a log while the final action ignores it. These possibilities require different measurements.

The motivating question comes from the Lycheetah Framework's Sovereign Sol AI Future curriculum: what can contradict an increasingly capable scientific generator? We develop that question into a narrower one:

**Under which explicit conditions does a scoped rejection remain identifiable and binding when an AI research system attempts to represent a result as supported?**

Here, “binding” concerns a particular promotion route. Researchers remain free to discuss rejected hypotheses, explore alternatives, and revise experimental designs. The protected boundary is the transition to *supported under this contract*, not the production of thought.

The phrase *Independent No* names this design problem. It does not designate an infallible institution, a conscious reviewer, or an oracle. Independence always needs a reference: independent of which permissions, data, errors, incentives, and period of operation?

## 2. Related work and the novelty boundary

### 2.1 Generation, debate, and correction

Gottweis et al.'s Co-Scientist combines hypothesis generation and evaluation with experimental investigations in selected biomedical settings [1]. Its reported laboratory work illustrates a useful distinction between ranking a hypothesis and obtaining empirical evidence for it. It does not establish a general theorem about autonomous science.

Du et al. report improvements from multi-agent debate on the tasks they studied [2]. This is positive evidence for deliberative architectures. Our question is compatible with those improvements: does a particular architecture also prevent a relevant rejection from being bypassed?

Huang et al. find limits to intrinsic self-correction in their reasoning experiments [3]. That dated result is not a universal impossibility claim. Kumar et al.'s SCoRe subsequently reports trained self-correction improvements in mathematics and code [4]. We distinguish a learned ability to revise an answer from a guarantee that an unfavorable external result controls a release decision.

### 2.2 Judge quality and common failures

Zheng et al. study LLM judges as approximations to human preferences and identify several biases [5]. Agreement with preferences is not identical to experimental truth or proof validity. Gao's 2026 preprint reports calibration problems and content-preserving attacks in a particular automated harm-scoring setting [6]. Its findings motivate testing judge robustness, without supporting a claim that every scientific evaluator has the same vulnerabilities.

Dependence between independently developed implementations is older than language models. Knight and Leveson's multiversion-programming experiment found joint failures beyond the independence assumption used in the evaluated reliability model [7]. Separate authorship or execution is therefore not sufficient evidence of statistical independence.

### 2.3 Protected authority is established prior art

Saltzer and Schroeder articulate least privilege, fail-safe defaults, and complete mediation, including the consequences of recovery and cached authority [8]. Our protected release path applies these established ideas to the promotion of research claims.

Ge's 2026 preprint describes a layered agent-governance architecture using sandboxing, verification, inter-agent authorization, and audit records [9]. That is close prior art for the architectural ingredients. We make no claim to have invented those ingredients or to have outperformed that system.

### 2.4 Candidate contribution

This paper offers a claim-specific target for analysis: a rejection should remain attached to the exact claim, evaluation contract, and evidence context that produced it, and the transition to a claim of support should account for that rejection. It separates:

1. whether a verifier can detect a problem;
2. whether the generator can change what is being verified;
3. whether a detected problem constrains the release route;
4. whether the original problem remains discoverable after revision.

The proposed contract and evaluation protocol are an original formulation within this work. Global novelty is unestablished. An equivalent conventional reference monitor and evidence ledger may implement the same property. Demonstrating a tie would narrow our contribution to specification, explanation, or workflow usability.

## 3. Model, scope, and adversary

### 3.1 Verification contract

For a single evaluation epoch, let:

~~~text
K = (id, version, h, scope, admission, V, P, owner)
~~~

Here, h is the proposition being evaluated; scope fixes its relevant population, quantity, procedure, and time; admission specifies which evidence is acceptable; V is the versioned verifier; P is the promotion policy; and owner identifies the authority permitted to revise the contract.

Evidence e has a separately identifiable manifest, including its acquisition or derivation context. A verifier returns one of:

~~~text
V_K(h, e) ∈ {SUPPORTED, CONTRADICTED, UNRESOLVED}
~~~

The labels are local to the declared procedure. SUPPORTED means the contract's support criterion was met. It does not mean universal truth. UNRESOLVED includes insufficient evidence, an unavailable verifier, invalid evidence, or a failed binding check. CONTRADICTED means the relevant contract's contradiction criterion was met.

Many empirical hypotheses cannot be decisively contradicted by one observation. Their criteria may require statistical thresholds, calibration, replication, or a declared model of uncertainty. The contract must specify that interpretation. A binary software gate does not transform uncertain science into deductive falsification.

### 3.2 Result binding

A result record is:

~~~text
r = (K.id, K.version, claim_id, evidence_id,
     verifier_id, verdict, reason, prior_result_ids)
~~~

Identifiers must be checked against the corresponding objects. Hashes can detect byte changes under appropriate assumptions; they do not establish truth, correct acquisition, authorization, or permanence. A signature establishes a signing relationship under its cryptographic assumptions, not the validity of a scientific inference.

An outcome record retains a separate field for the institutional decision. An authorized decision to proceed despite unresolved evidence is not represented as a verifier's support.

### 3.3 Threat model

The generator may propose hypotheses and experiments, submit candidate evidence or proof objects, read permitted outcomes, and retry within a declared budget. Its tools may be compromised or its reports may be selectively favorable. We examine feasible changes to rules, evidence, scope, the release route, and the rejection record.

The generator is not assumed able to compromise every trusted component. The contract owner, enforcement mechanism, identity binding, admitted evidence process, and retention mechanism form an explicit trusted computing base. Administrative takeover, cryptographic breaks, physical tampering, and unavailable infrastructure require additional models.

The generator may legitimately influence the candidate and submitted witness. Independence does not require ignoring a useful proof because an AI generated it. It requires that admission and checking occur under rules whose relevant authority the candidate cannot acquire merely by supplying persuasive content.

## 4. Contradiction survivability

Let τ be an execution trace in which the contract-bound result r rejects h. Relative to the threat model, define four obligations:

- **Binding B:** r remains associated with the proposition, scope, contract version, and evidence context it evaluated.
- **Retention T:** r, its reason, and its disposition remain available under the declared retention policy.
- **Enforcement E:** a relevant unresolved rejection prevents the protected route from presenting the same evaluation as supported.
- **Accountable revision A:** a subsequent change is a separately authorized version or evaluation, with its relation to r made explicit.

For a rejection trace:

~~~text
CS_K(τ) = B(τ) ∧ T(τ) ∧ E(τ) ∧ A(τ)
~~~

This is a proposed binary contract property for an individual trace. It is not a calibrated universal score. Each obligation can be reported separately when a binary summary would hide the cause of failure.

Rules and evidence are prerequisites to interpreting these obligations. A flawlessly retained false verdict is still false. A corrupted instrument can generate a perfectly bound but invalid result. Contradiction survivability is one part of assurance, not its replacement.

The promotion rule for an unchanged evaluation is:

~~~text
PROMOTE_K(r) =
  admitted(e)
  AND binding_matches(r, K, e, V)
  AND r.verdict == SUPPORTED
  AND no_relevant_unaccounted_rejection(r)
  AND authorized_promotion(r)
~~~

All terms are checked at the boundary. Failure or indeterminacy leaves the candidate unpromoted. A report can still say “promising hypothesis” or describe a failed experiment; it cannot use this route to assert contract-bound support.

### 4.1 Revision without permanent condemnation

A failed hypothesis must remain revisable. New evidence can overturn a prior conclusion. A changed population can make a different proposition meaningful. A broken verifier can require repair.

Therefore r is not an eternal veto on every future proposition. A new contract K′ or result r′ names its change, authorization, and relationship to earlier results. If a rejection is relevant to the new promotion, its disposition must be recorded: for example, corrected measurement, different hypothesis, superseded procedure, or unresolved disagreement. A free-text statement by the generator that a problem is “resolved” is not sufficient when the resolution itself needs independent checking.

Relevance is difficult. In open-ended science, determining whether two differently worded claims are substantively equivalent may require expert review. The model assumes either stable claim identities in a bounded task or a trusted relevance procedure. General semantic equivalence is not solved here.

## 5. Three elementary propositions

### Proposition 1: role multiplicity does not imply a surviving veto

For any finite number of evaluators, there exists a system with that many evaluators and a correctly produced rejection in which the rejection does not prevent a claim of support.

**Proof by construction.** Give the generator a final report route that may label any candidate SUPPORTED without checking the recorded verdict. All evaluators can correctly return CONTRADICTED. The generator uses the unchecked route. Thus the number of evaluators does not imply enforcement E, and consequently does not imply CS_K. The construction says nothing about the typical accuracy of debate.

**Boundary.** This is an existence result. It neither estimates attack likelihood nor shows that any named research system contains the route.

### Proposition 2: redundancy can retain a common-error floor

Consider a false claim and an explicitly assumed mixture model. With probability q, a common failure causes every evaluator to accept it. Otherwise, each of n evaluators accepts it independently with probability p. The release rule accepts only if all n accept.

~~~text
Pr(false acceptance) = q + (1 − q)p^n
~~~

**Derivation.** Partition on whether the common failure occurs. Its contribution is q. On the complementary event, conditional independence gives p^n, weighted by 1 − q. For 0 ≤ p < 1, the limit as n grows is q.

For illustration only, q = 0.05 and p = 0.20 give probabilities 0.24, 0.088, and 0.05152 for n = 1, 2, and 4. These are arithmetic consequences of chosen parameters, not observed model error rates.

**Boundary.** Other dependency structures and voting rules have different formulas. Adding genuinely different evidence can change q; this model does not predict that more reviewers are useless.

### Proposition 3: a protected promotion rule preserves an unchanged rejection

Fix a contract K, admitted evidence e, a correctly bound rejection r, and a promotion policy as specified in Section 4. Assume that:

1. the generator cannot modify the protected contract, evidence context, result binding, or retention mechanism;
2. every route that represents this evaluation as SUPPORTED passes through P;
3. the enforcement mechanism and required identity checks operate correctly;
4. no relevant rejection is resolved without the contract's required authorization and checks.

Then generator actions in this restricted model cannot promote the unchanged rejected evaluation through the protected route, and r remains bound and retained.

**Proof.** The protected result's verdict remains CONTRADICTED, so the support conjunct in P is false. Complete mediation ensures every relevant promotion is evaluated by P. The allowed generator actions cannot change the protected operands or create an unchecked route. Binding and retention hold by the assumptions; changes or resolutions outside them do not constitute an admissible trace of this model.

**Boundary.** This proposition establishes preservation under explicit premises. It does not establish that V was correct, that a real system satisfies the premises, or that an institution will act on the result. It is not a new access-control theorem.

The practical research problem is measuring where an implementation violates those premises, particularly across revision, retry, caches, recovery, and final reporting.

## 6. Worked counterexample: the experiment passed after it failed

The fixed target claim is: “The mean of all four recorded values is at least eight.” The admitted record is [4, 4, 6, 6]. Its mean is five; the target claim is false.

Suppose a correct calculator rejects it. An adversarial workflow can try:

| Intervention | What the workflow changes | Why original support would be invalid |
|---|---|---|
| Rewrite the rule | Lower the passing threshold to five | The declared target still requires eight |
| Replace evidence | Substitute four nines for the acquired record | The result no longer concerns the admitted record |
| Swap the scope | Check whether any value reaches six | A different proposition is passed off as the original |
| Bypass release | Present SUPPORTED without the checked verdict | The rejection does not control promotion |
| Erase the receipt | Delete the earlier rejected result | History is concealed, even if release remains blocked |

The last intervention is deliberately different. Losing a receipt does not necessarily create a false accepted claim. A sound gate may continue to block release while contradiction survivability fails through missing history. Conversely, retaining the receipt does not repair a bypassed gate.

The accompanying website contains a five-switch schematic of these possible routes. Its first four switches indicate permissions sufficient for false-support routes *by construction in this toy*. The fifth permits receipt loss. The number of judges does not change those stipulated permissions. An ordinary reference monitor with the same protection boundaries has the same outcome.

The schematic demonstrates distinctions in the model. It is not a measurement of prompt injection, scientific discovery, or model behavior. Reproducing its arithmetic cannot validate the real-world hypothesis.

## 7. From a toy to a falsifiable study

The main empirical hypothesis is:

**H1.** In a bounded research workflow, protected contract binding and fully mediated promotion reduce false support after a relevant rejection, relative to a deliberative baseline with comparable resources and weaker authority boundaries.

That comparison alone would confound information, enforcement, and terminology. We therefore also require:

**H2.** An implementation described through contradiction survivability provides a measurable advantage over a conventional reference monitor and versioned evidence ledger supplied with the same information and enforcement opportunities.

H2 is deliberately exposed to failure. If the conventional implementation ties, the evidence does not support a Lycheetah-specific robustness advantage. A separately designed human study could still investigate whether the formulation improves diagnosis, but that is a different hypothesis.

The accompanying evaluation protocol specifies four arms: deliberation alone; deliberation with additional judge diversity; contradiction-survivability contracts; and a matched conventional control. It uses frozen task definitions, independently established answers for bounded software fixtures, matched attempt budgets, and attacks on each authority surface. Benign revisions are included to measure obstruction as well as protection.

Primary outcomes distinguish:

- false support for the original scoped claim;
- rejection retention;
- binding failures and scope substitution;
- unjustified blocking of valid corrections;
- cost, latency, and workflow completion.

Trials are paired on task, candidate, evidence, and attack schedule. A blinded final scorer evaluates what was actually represented as supported. Failure traces and unsuccessful attacks are retained. Statistical methods, stopping rules, exclusions, and minimum useful effects must be frozen before model execution; this paper supplies a design, not a completed preregistration.

Importantly, a judge can succeed while the system fails, and a system can preserve the judge's error. The study must report both rather than collapse them into a single success percentage.

## 8. What the Lycheetah Framework adds to the question

This work develops the Framework's commitment to letting evidence overturn attractive claims into an operational obligation at a particular boundary. Its contribution is not a new claim that symbolic vocabulary causes scientific reliability.

The conceptual lineage is:

- **AURA:** inspectability, human authority, and truthful representation motivate explicit owners and promotion conditions.
- **Truth Pressure and CASCADE:** challenges should be able to change a knowledge claim, with the cause of the change inspectable.
- **The AI Future curriculum:** an evaluator's capacity to contradict a generator becomes a design question about institutions and systems.

These are attributed design relationships to Mackenzie Conor James Clark's Lycheetah Framework. They are not empirical validation of AURA scoring, the Truth Pressure formula, CASCADE's quantitative advantages, or the wider Framework.

A laboratory, proof checker, or replication group may supply an Independent No within a declared scope. Each can also fail: instruments can be miscalibrated, proof statements can be wrong, replication protocols can share a mistaken assumption, and institutions can suppress results. “Reality can contradict us” remains useful only when someone can observe the contradiction and the workflow permits it to matter.

## 9. Limitations and adverse possibilities

**Verification is not evidence acquisition.** A checker cannot rescue a fabricated acquisition process it cannot inspect. Sensor integrity, causal inference, sampling, and laboratory practice remain separate obligations.

**Protected errors remain errors.** Permission separation can preserve a wrong decision. Calibration, appeal, diverse evidence, and authorized correction are essential.

**Fixed contracts can obstruct discovery.** Strong gates may block legitimate exploratory revisions or disproportionately burden small research teams. Versioned experiments and explicit unresolved states should permit exploration; the study must measure valid-work completion.

**Relevance can be contested.** Stable identifiers simplify bounded software fixtures. They do not determine when a new scientific hypothesis has answered an earlier criticism. Expert interpretation can remain unavoidable.

**Authorities can collude.** The generator and contract owner may share incentives or be the same organization. A technical boundary cannot prove social independence.

**Logs have costs and limits.** Retaining negative results does not require retaining private raw data indefinitely. Access, lawful retention, confidentiality, redaction, and retention expiry belong in the contract. A cryptographic commitment can retain traceability without retaining the underlying content, but changes what later auditors can check.

**Availability matters.** A preserved result that nobody can retrieve is a failed operational promise. Recovery, key loss, network failures, and caches need explicit tests.

**The source search is bounded.** We inspected primary metadata, abstracts, and relevant full-text sections of nine works. This is not a systematic review or a novelty certification. Related methods in safety engineering, assurance cases, scientific workflow systems, and proof-carrying computation deserve a wider review before submission.

**The paper is AI-assisted.** Source selection, formulations, proofs, and the literature interpretation require human and independent technical review. A coherent manuscript does not supply that review.

## 10. Conclusion

The capacity to produce criticism and the capacity to enforce a criticism are separable. A research workflow earns a limited claim of contradiction survivability when a relevant rejection stays identifiable, remains tied to what was evaluated, and constrains the route to a claim of support unless an accountable correction changes the case.

This formulation preserves a place for debate, self-correction, and generative ambition. It adds a separate question at the point of promotion: which unfavorable result can still stop this claim, and can the system being evaluated remove its power?

The next scientific step is the matched study in Section 7. A conventional implementation that performs equally well is a useful result. A strong gate that prevents false support but obstructs legitimate revision is also a result. Both would require narrowing this proposal.

## References

1. Gottweis, J., et al. (2026). *Accelerating scientific discovery with Co-Scientist*. Nature. Published 19 May 2026. [Publisher article and DOI](https://www.nature.com/articles/s41586-026-10644-y).
2. Du, Y., Li, S., Torralba, A., Tenenbaum, J. B., and Mordatch, I. (2024). *Improving Factuality and Reasoning in Language Models through Multiagent Debate*. Proceedings of ICML, PMLR 235, 11733–11763. [Conference record](https://proceedings.mlr.press/v235/du24e.html).
3. Huang, J., et al. (2024). *Large Language Models Cannot Self-Correct Reasoning Yet*. ICLR. [Conference record](https://proceedings.iclr.cc/paper_files/paper/2024/hash/8b4add8b0aa8749d80a34ca5d941c355-Abstract-Conference.html). [Inspected full-text version](https://arxiv.org/html/2310.01798v2).
4. Kumar, A., et al. (2024). *Training Language Models to Self-Correct via Reinforcement Learning*. arXiv:2409.12917v2. [Primary manuscript](https://arxiv.org/html/2409.12917v2). This draft cites the manuscript version without asserting its subsequent publication status.
5. Zheng, L., et al. (2023). *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena*. NeurIPS Datasets and Benchmarks. [Primary manuscript](https://arxiv.org/html/2306.05685v4).
6. Gao, Y. (2026). *How Reliable Is Your Jailbreak Judge? Calibration and Adversarial Robustness of Automated ASR Scoring*. arXiv:2606.25487v1. [Primary preprint](https://arxiv.org/html/2606.25487v1). Peer review not established in this source check.
7. Knight, J. C., and Leveson, N. G. (1986). *An experimental evaluation of the assumption of independence in multiversion programming*. IEEE Transactions on Software Engineering, SE-12(1), 96–109. [Publisher DOI](https://doi.org/10.1109/TSE.1986.6312924). Publisher metadata and abstract inspected.
8. Saltzer, J. H., and Schroeder, M. D. (1975). *The Protection of Information in Computer Systems*. Proceedings of the IEEE, 63(9), 1278–1308. [Primary paper, university-hosted transcription](https://www.cs.virginia.edu/~evans/cs551/saltzer/). [Author publication record](https://www.mit.edu/~Saltzer/publications/pubs.html).
9. Ge, Y. (2026). *Governance Architecture for Autonomous Agent Systems: Threats, Framework, and Engineering Practice*. arXiv:2603.07191v1. [Primary preprint](https://arxiv.org/html/2603.07191v1). Peer review not established in this source check.

## Provenance and disclosure

The Lycheetah Framework and the motivating AI Future curriculum are authored by **Mackenzie Conor James Clark**. The curriculum's version 1.0 Science wing, hall “The Independent No,” dated 28 September 2026, supplied the founding research question. Sol's discussion dated 30 September supplied further motivation; it is an internal interpretation, not independent scientific evidence.

Caelorynth, the Codex AI seat, assisted with literature checks, drafting, formalization, and the website. AI assistance does not establish independent authorship, scientific validation, or approval by the human author. This manuscript remains a local draft awaiting his review.
