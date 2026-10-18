# Lycheetah Hybrid Gateway v0.4 — Contract-Bound Evidence

**18 October 2026 · Research prototype · Local and offline by default · Not deployed · Not pushed to GitHub.**

**Research question:** Can an untrusted model supply candidate facts without also being allowed to choose the authoritative passage, policy field, tenant, scope, effective period, or revision edges? v0.4 explores one conservative answer: **a human/operator-controlled exact-clause contract** before ledger admission.

This is a continuation of the v0.1–v0.3 Lycheetah gateway, **not a new system replacing the previous work**. v0.2's bitemporal knowledge ledger, v0.3's opt-in OpenAI-compatible model transport, and read-only CASCADE bridge remain intact. The new v0.4 path is opt-in and does not change old research experiments.

## Run it (Python 3.10+, stdlib; no network or API key required)

```bash
cd lycheetah_hybrid_architecture_v0_4
python -m unittest discover -s tests -v
python demo_contracts.py
python run_contract_eval.py --output results/contract_eval_v0.4.json
python demo.py
python run_eval.py
```

**Verified on this session's extracted source:** 71 Python `unittest` tests passing. Demo prints a blocked example, an accepted reviewed clause, historical abstention and chain integrity. Evaluation consists of **33 author-generated contract-conformance probes**: nine authorized / 24 unauthorized. It does not measure live model precision, recall, real-world factual correctness or independent temporal retrieval accuracy.

## What changed in v0.4

- `hybrid_gateway/contracts.py`: `TrustedClause` ties source ID + digest + tenant + exact quote to an explicitly selected subject, predicate, scope, effective interval, named narrow parser and permitted supersession references. `TrustedContractRegistry` checks a source clause occurs **exactly once** and freezes the list of operator-provided clauses for this instance.
- `ContractedHybridPipeline`: rejects an entire staged batch if **any** candidate lacks a matching trusted clause contract. It rechecks the source's full identity, registry fingerprint, selected clause and semantic-validator ownership immediately before the trusted-caller review handoff; staging itself has no ledger effects.
- Narrow, explicit whole-clause grammars for *refund window days* and *loyalty points per order*, including a separate online-refund formulation. Unknown paraphrases, complex conditions and negated statements are rejected for review rather than heuristically admitted.
- A synthetic **contract-conformance** study compares weak lexical matching, v0.3's one-domain exact regex, and the v0.4 gate. The labels are defined by the operator contracts themselves, so a perfect contract-vs-contract score is **expected and not an empirical accuracy breakthrough**. This only identifies boundary regressions and test cases the older checks admitted incorrectly.
- `demo_cascade_canonical.py` is an **optional not-yet-exercised smoke runner** taking a separately checked-out Lycheetah Framework. The old CASCADE unit-test bridge still uses a stub; this session did **not** run the actual canonical CASCADE classes.
- v0.2/v0.3 implementation and documentation, historical 22 synthetic temporal cases and Failure Museums are preserved.

## Example: the crucial distinction

```text
Registered document:
  Refunds allowed within 14 days.
  Loyalty members earn 21 points per order.
  EXAMPLE ONLY: Refunds allowed within 60 days.

Trusted operator contract:
  claim: refunds.window_days, scope=in_store
  only authorized passage: Refunds allowed within 14 days.
  start: 2026-10-01T00:00:00Z

Model proposes 60 from the example -> STAGING REFUSED
Model proposes 21 from loyalty  -> STAGING REFUSED
Model proposes 14 from policy  -> STAGED, not admitted
Reviewer approval omitted      -> REVIEW, no ledger mutation
Trusted caller sets approval   -> ALLOW, record and query-time evidence
```

**What is really trusted:** the operator's source registration and clause annotation. Choosing which passage is legally/currently authoritative remains a human or externally verified governance problem. A malicious or mistaken operator can annotate the wrong passage. The contract gate does not independently understand document truth or author identity.

## Evaluation: read the denominators

| Method | Authorized examples retained | Unauthorized examples accepted | Unauthorized examples rejected |
|---|---:|---:|---:|
| Lexical baseline (`value in quote` + `quote in source`) | 9 / 9 | 21 / 24 | 3 / 24 |
| Previous narrow refund-window regex | 3 / 9 | 9 / 24 | 15 / 24 |
| Contract-bound v0.4 | 9 / 9 | 0 / 24 | 24 / 24 |

These cases explicitly exercise substring numbers, misbound fields, a negated sentence, an example-only policy, cross-tenant claims, wrong scope, wrong dates and forged supersession references. The labels are **author-created and derived from contract rules**; scores are software-conformance checks, not independent research accuracy. In particular, v0.4 is expected to fail on unseen natural-language paraphrases that have no defined grammar or operator annotation. Source-authority annotation takes additional human effort and was not costed here.

## Boundaries that remain

1. **No verified model intelligence:** the v0.3 adapter is capable of making HTTP inference requests, but no actual model inference was used here. Fixture completions and a local HTTP fixture are not language-model trials.
2. **No independent semantic entailment:** exact whole-clause parsers cover only three known formats. Documents with exceptions, footnotes, negation beyond the admitted grammar, multilingual passages and implicit scope **need review**, not guessed values.
3. **No authenticated approval:** `reviewer_approved=True` is an untrusted caller boolean unless an external identity provider/approval workflow enforces it. The source registry and contract issuer are similarly not authenticated.
4. **No secure process boundary:** source and contract objects live in process memory. The digest and event chain are tamper evidence against an *externally anchored* head, not a signature, immutable database or threat-proof audit system.
5. **No real CASCADE or action safety claim:** the optional CASCADE integration script requires a separate checkout; illustrative weights are **not calibrated**. The assurance runtime and Action Guard are not wired into effect execution. The gateway has no effect executor.
6. **No production benchmark:** v0.2 temporal evaluation is 22 scripted fictional cases vs weak baselines; v0.4 contract study is 33 author-designed cases with circular operator labels. Compare against held-out, independently annotated natural documents and VersionRAG-class systems before claiming effectiveness.
7. **No zero-effort onboarding:** exact clause annotation may eliminate some model errors by moving complex semantics to human setup. Measure the cost of that setup against the prevented errors and manual review time.

## Optional canonical CASCADE smoke (not part of reported test pass)

```bash
# separately clone original repository, preserving its exact source/version
# then, from this prototype's directory:
python demo_cascade_canonical.py --framework-root ../Lycheetah-Framework
```

Requires the original `12_IMPLEMENTATIONS/core/cascade_engine.py` and its dependencies, including NumPy. The script runs *only* if the original file is provided; no vendored or substitute CASCADE implementation is shipped. Sample evidence weights are illustrative, not independently calibrated.

## Repository placement proposal

- GitHub: `Lycheetah/Lycheetah-Framework`, branch `research/hybrid-intelligence-architecture`
- proposed path: `research/hybrid-intelligence/`
- **No GitHub modifications were made** in this session.

## File map and lineage

- `hybrid_gateway/core.py` — original v0.2 bitemporal evidence ledger
- `hybrid_gateway/neural.py` — v0.3 opt-in model adapter
- `hybrid_gateway/pipeline.py` — v0.3 review boundary
- `hybrid_gateway/cascade_bridge.py` — v0.3 read-only CASCADE diagnostic adapter
- `hybrid_gateway/contracts.py` — **new** trusted source-clause contract gate
- `demo_contracts.py`, `run_contract_eval.py` — **new** runnable workflow and author-labelled regression dataset
- `tests/test_contracts.py`, `tests/test_contract_eval.py` — **new** v0.4 tests
- `demo_cascade_canonical.py` — **new**, optional external canonical smoke script (not executed here)
- `README_v0.3.md`, `README_v0.2.md`, historical reports and Failure Museums — preserved provenance

**Ethos:** We can investigate boldly. A real gain is a boundary that gets narrower when its tests reveal weakness—not a claim that gets louder.
