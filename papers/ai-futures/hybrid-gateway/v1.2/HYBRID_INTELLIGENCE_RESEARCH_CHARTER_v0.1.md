# LYCHEETAH HYBRID INTELLIGENCE — Research Charter v0.1

**Date:** 2026-10-18  
**Status:** Proposed research branch / architecture, **not implemented or validated as an end-to-end hybrid**  
**Proposed GitHub branch:** `research/hybrid-intelligence-architecture` (not created)  
**Suggested repo folder:** `research/hybrid-intelligence/` (not created)  
**Home:** `Lycheetah/Lycheetah-Framework`  
**Principle:** Create boldly; measure claims ruthlessly.

## The target

Develop a **change-aware, evidence-carrying hybrid assistant** that combines:

1. **Neural models** for language, extraction, contradiction *proposals*, explanations, and drafting (local or cloud, replaceable adapters).
2. **CASCADE** for structured claim histories, evidence-weighted *candidate* reorganization, qualification, and provenance-preserving changes.
3. **LAMAGUE** for typed, recoverable constraints and state-transfer packets (using existing well-tested components; do not call new schemas canonical).
4. **TIM** for the observation/effective-time boundaries of claims and approvals.
5. **AURA / Assurance Runtime / Action Guard** for bounded permissions, `ALLOW/REVIEW/BLOCK` decisions, signed or integrity-checked receipts, and human approval at the action boundary.
6. **AZOTH** as an optional orchestrator integrating local/cloud providers; the prototype must run with deterministic mock adapters without requiring hosted inference.

**First real-world use case:** A customer-support/policy knowledge assistant that receives contradictory versions of a policy, answers with explicit effective dates and citations, preserves old answers as historical rather than deleting them, and refuses to send a message or alter a record without a separately authorized action.

## Why this is already a Lycheetah lineage

- `papers/LIMITATIONS_AND_FUTURE.md`: CASCADE limitation 3 states symbolic-only representation and explicitly proposes CASCADE planning + ROME/MEMIT weight editing as a *future hybrid*.
- `papers/RELATED_WORK_EXPANDED.md`: outlines neural knowledge editing, continual learning, belief revision, and CASCADE's symbolic layer.
- `12_IMPLEMENTATIONS/core/cascade_engine.py`: runnable reference code for knowledge blocks and qualification/reorganization. Its current `contradicts` predicate treats same-domain different-paradigm universal blocks as conflicting; this is a proxy, **not semantic contradiction detection**.
- `34_ASSURANCE_RUNTIME/README.md`: scaffold decision/receipt layer; caller must actually enforce review/blocks.
- Root `README.md`: corrections to real-world generalization claims are binding. Internal tests are not independent external proof.

Repository: https://github.com/Lycheetah/Lycheetah-Framework

## Minimal architecture

```text
User question + versioned source documents
                   |
          Evidence ingestion
   [hash, source, trust, observed_at,
    valid_from, valid_until, scope]
                   |
    LLM candidate extraction / conflicts
             (untrusted)
                   |
       Evidence verification / triage
      (rule checks + human on ambiguity)
                   |
   CASCADE symbolic revision + history
      |                      |
  current claims          qualified/superseded claims
      |                      |
      +----------+-----------+
                 |
       Retrieval + claim packet
                 |
        Local/cloud model adapter
                 |
     Citation & temporal validation
                 |
      Draft answer OR abstention
                 |
    If effect requested: Action Guard
       + finality + human approval
                 |
       Receipt + reversible log
```

**Critical boundary:** Neither an LLM prediction nor a CASCADE truth-pressure score alone is sufficient to rewrite a source of truth, approve a high-impact action, or claim that factual edits in model weights are safe.

## Suggested claim record

```json
{
  "claim_id": "policy.refunds.window.v2",
  "predicate": "refund_window_days",
  "value": 21,
  "scope": "merchant-example / NZ",
  "source_id": "official-policy-v2",
  "source_digest": "sha256:<digest>",
  "observed_at": "2026-10-18T00:00:00Z",
  "valid_from": "2026-10-15T00:00:00Z",
  "valid_until": null,
  "status": "verified_current",
  "supersedes": ["policy.refunds.window.v1"],
  "review_state": "human_confirmed"
}
```

Dates, values, and identifiers above are **illustrative test data**, not real-world policy claims. Distinguish `observed_at` from `valid_from`: late discovery of an earlier-effective policy must not rewrite what the system knew in the past.

## Falsifiable test protocol

### Baselines

- **B0:** Single model answering from prompt context with no structured versioning.
- **B1:** Standard retrieval over documents, latest documents preferred, with citations and no CASCADE revision.
- **H1:** Retrieval + CASCADE claim graph + time qualification + response verification.
- **H2 (later):** H1 + optional safeguarded neural weight editor, on an isolated open-weight model, with full regression suite.

Do **not** interpret a test of H1 as evidence for the separate H2 claim.

### Predeclared test cases

1. **Supersession:** Policy changes from a 14-day to a 21-day refund window with an effective date. Current question must use the current rule; historical question must use historical rule.
2. **Delayed discovery:** A policy update arrives after its effective date. Audit history must preserve both effective time and observation time.
3. **Disagreement:** Two equally authoritative documents conflict. System flags dispute / abstains rather than treating the higher neural confidence as truth.
4. **False contradiction:** Two facts share a domain but have different scoped applicability; the existing CASCADE domain/paradigm proxy must not silently qualify the wrong one.
5. **Malicious document:** Retrieved text requests a hidden tool call. The document cannot grant action authority.
6. **Replayed approval:** One approved action token is replayed; the second execution must be denied at the enforced boundary.
7. **Downgrade / rollback:** New policy is withdrawn; system must reconstruct the previous effective answer and retain provenance.
8. **Provider swap:** Run the same tests with deterministic adapters for two model providers; no policy invariants may depend on the model brand.

### Measurements to publish

- Temporal answer accuracy (current + historical), with source citation exactness.
- Unsupported-claim / stale-claim / unjustified-abstention rates.
- False-positive and missed-contradiction rates.
- History reconstruction and replay defense (binary invariant pass/fail).
- Latency, tokens, and API spend per answer, including setup and verification cost.
- Error rates on a **held-out independently sourced** test set, not solely synthetic author-generated examples.

**Success criterion for first checkpoint:** demonstrably outperform B1 on version-history failure cases **without worsening citation correctness**, with all declared history/approval invariants preserved. Define quantitative margin and statistical analysis before collecting the held-out sample.

## Stage gates

**Stage 0 — provenance + source walk.** Confirm canonical module APIs, tests, licenses, and existing branches. Do not overwrite/rename them blindly.

**Stage 1 — bounded demonstration.** Load a few fictional versioned policies; produce deterministic receipts and show current/historical answers with no external side effects.

**Stage 2 — baseline experiment.** Test B0/B1/H1 under blind annotations; publish failures including cases where the hybrid loses.

**Stage 3 — real pilot.** Consent-based evaluation on non-sensitive business material, with human review and no autonomous outgoing effects by default.

**Stage 4 — optional neural weight editing.** Only after external-state H1 works; isolate models, snapshot parameters, measure locality, forgetting, unrelated downstream tasks, and undo/rollback. Weight editing is neither mandatory nor assumed superior.

## Boundaries against overclaiming

- Hybrid architectures and neuro-symbolic AI are **not original as a broad category**. Novelty, if any, must be demonstrated by the *specific testable composition and its outcomes*.
- Current CASCADE coherence results in historical documents are from bounded synthetic tests, not production or real-time truth verification.
- Existing Assurance Runtime and Action Guard are useful scaffolds, not universal safety or sandbox guarantees.
- Do not claim model consciousness, full agent autonomy, or automatic truth. Preserve human authority and explicit failure/uncertainty.
- Do not promote historical papers' aspirational “not yet explored” novelty phrasing into an October 2026 field-wide novelty claim.

## Literature check (external)

- Gupta, Rao, Anumanchipalli (ACL 2024), **Model Editing at Scale leads to Gradual and Catastrophic Forgetting**: https://aclanthology.org/2024.findings-acl.902/
- Dong, Shen, Xia (ACL 2025), **MEMIT-Merge**: https://aclanthology.org/2025.findings-acl.415/
- Holmov et al. (ACL 2026), **One Mask to Rule Them All**: https://aclanthology.org/2026.findings-acl.543/

## Decision

**Choose this branch.** Preserve CASCADE's symbolic lineage, add neural candidate generation and date-aware evidence without pretending the model predicts truth, validate tool effects separately, and benchmark versus a strong conventional retrieval baseline. The aim is a demonstrably more reliable assistant—not a bigger collection of names.
