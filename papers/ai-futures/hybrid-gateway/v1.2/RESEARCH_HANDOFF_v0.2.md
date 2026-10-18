# Lycheetah Hybrid Intelligence — handoff for the next coding agent

**Checkpoint:** v0.2 · 2026-10-18 · status: local runnable prototype + internal evaluation.

## Begin here

1. Read `README.md` and original `HYBRID_INTELLIGENCE_RESEARCH_CHARTER_v0.1.md`.
2. Run `python -m unittest discover -s tests -v`, `python demo.py`, `python run_eval.py`.
3. Read the FULL per-case `results/synthetic_evaluation_v0.2.json` and `FAILURE_MUSEUM_v0.2.md` before extending claims.
4. Inspect canonical existing source in `Lycheetah/Lycheetah-Framework`, especially `12_IMPLEMENTATIONS/core/cascade_engine.py`, `papers/LIMITATIONS_AND_FUTURE.md`, `34_ASSURANCE_RUNTIME/README.md`, `34_ASSURANCE_RUNTIME/action_guard/`, and `03_LAMAGUE_L1/22_REVERSIBLE_COMPRESSION_v1.0/` before touching integrations.

## Integration plan (not yet done)

**Proposed remote branch:** `research/hybrid-intelligence-architecture` in `Lycheetah/Lycheetah-Framework`.

**Proposed path:** `research/hybrid-intelligence/` (preserve original repo packages; avoid replacing existing CASCADE or Assurance).

- Package the gateway as an experimental module with stable `ClaimProposal`, `Decision`, `QueryResult`, and `SourceDocument` contracts.
- Build a **read-only CASCADE diagnostic adapter** that inspects only admitted, scope-and-time-filtered candidates. Do not let `CASCADE` same-domain paradigm proxies automatically override bitemporal conflicts. Do not assign synthetic evidence/uncertainty parameters as if calibrated.
- Build a **real neural extraction adapter** with explicit provider permissions. For each extracted claim carry exact evidence quote, source URI, source digest, scope and effective interval. Reject unsupported / ambiguous extraction. Test mock provider swaps first, then a consented and budget-capped provider trial.
- Bind the `REVIEW/ALLOW/BLOCK` protocol to the existing Assurance Runtime and Action Guard with typed actions, single-use grants, explicit scope, human approval, expiry, and **finality-time recheck**. The current `propose_effect` is a non-executing stop; do not quietly add `send()`.
- Implement authenticated operator and reviewer identity, persisted source registry, immutable ledger storage with independently pinned heads, privacy policy and tenant isolation in storage (not just query filters).
- Make a genuinely held-out dataset with third-party effective-date labels and disputes. Compare a strong version-aware RAG implementation; report errors, citation accuracy, false abstentions, overhead, cost, and negative outcomes.
- Only consider offline open-weight model editing after this external-state approach holds up. Preserve parameter snapshots; test locality, forgetting, reversal and unrelated tasks.

## Intended architecture boundary

```text
Untrusted model / OCR / extractor => structured candidate
Trusted source registry => document bytes and hashes
Operator domain checks + independently authorized review => accepted fact
Bitemporal ledger + supersession graph => query-time current fact or abstention
Constrained answer renderer => evidence references
[separate future action gateway] => effects, only with final authorization
```

Claims that **must not** be made on upload:

- "We solved hallucinations", "independently validated", "full neural-symbolic CASCADE integration", "safe production agent", "new invention of bitemporal RAG", "cryptographically authenticated approvals", "LLM prompt injection solved", or "CASCADE improved model weights".

## Test health at creation

- `42/42` internal Python `unittest` cases green.
- Internal fictional evaluation: B0 `8/22`, B1 `13/22`, H1 `22/22` exact outcome matches. Both baselines source-filtered; B1 uses two clocks but lacks dispute/withdrawal resolution.
- Negative-control FM-HYB-001 intentionally confirms misbinding under the optional loose anchor mode and its rejection under the exact refund-window schema.
- No known internet calls or side effects in demo/test.

## Suggested first commit

```bash
# Within an existing trusted checkout of Lycheetah-Framework:
git switch -c research/hybrid-intelligence-architecture
mkdir -p research/hybrid-intelligence
cp -R /PATH/TO/UNZIPPED/lycheetah_hybrid_architecture/. research/hybrid-intelligence/
# Review generated files and do NOT commit __pycache__/ or other local runtime files.
git add research/hybrid-intelligence
git diff --cached --stat
git commit -m "research: add bounded hybrid evidence gateway and synthetic baselines"
# Push/pull request ONLY upon the owner's decision.
```

**Ownership:** Lycheetah collaboration research. Source source-of-truth lives in the GitHub repository; this package is a local *proposed addition*, not an existing branch or release. Original v0.1 charter is preserved unchanged.
