# Handoff v0.4 — Lycheetah Hybrid Intelligence

**Source of truth:** This entire archive, especially `README.md`, `SESSION_REPORT_v0.4.md`, `FAILURE_MUSEUM_v0.4.md`, and the preserved earlier reports. Previous source modules unchanged except adding v0.4 exports to `hybrid_gateway/__init__.py`. This is still an uncommitted local research artifact.

## Reproduce

```bash
python -m unittest discover -s tests -q       # 71 tests
python demo_contracts.py                       # offline/no network
python run_contract_eval.py                    # 33 author-built conformance cases
python demo.py                                 # historical v0.2 demo
python run_eval.py                             # historical 22-case temporal study
```

## What the next engineer should tackle

1. **Real model trial on fictional text only:** run `demo_live_inbox.py` against an explicitly installed local model, pin the model version and prompt digest, and record output validity, correct abstentions, wrong scope/date/field binding, omissions and latency. Do not transmit private material without user approval.
2. **Actual canonical CASCADE smoke:** checkout `Lycheetah/Lycheetah-Framework` separately; run `python demo_cascade_canonical.py --framework-root PATH`. Verify code revision and NumPy installation, and do not call illustrative weights calibrated. Keep CASCADE diagnostic only.
3. **Independent evaluation:** create independently annotated unseen source documents and policies, include paraphrase and exception cases, split by document, and compare current lexicon, contract-bound pipeline, and legitimate version-aware RAG/temporal retrieval baseline. Include annotation-time cost and abstentions.
4. **Authority & finality:** decide how operator/source identity is verified, attach signed/revocable provenance, persist in a durable append-only store, pin chain head independently, and verify policy immediately before effect execution. Do not treat `reviewer_approved=True` as authentication.
5. **Contract generalization:** document-specific trusted span offsets, exact source provenance and policy taxonomy; permit paraphrase only with independent entailment checks and explicit uncertainty. Track cost of operator annotation and policy-version transitions.
6. **Research distribution:** consider a PR to `research/hybrid-intelligence-architecture` in Lycheetah Framework only with explicit consent. Preserve all historical versions and avoid claiming an existing GitHub branch.

## Explicit cannot-claim list

No real-model evaluation; no canonical CASCADE execution; no independently validated accuracy; no generic semantic entailment; no production security; no real reviewer authentication; no live authorized actions; no universal new architecture; no performance win over VersionRAG.

**Foundational principle:** neural proposal -> operator-registered clause -> deterministic binding -> independent approval -> bitemporal ledger -> non-authoritative diagnostic -> external effects gate (future).
