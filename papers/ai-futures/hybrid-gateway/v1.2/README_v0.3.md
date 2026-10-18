# Lycheetah Hybrid Gateway v0.3 — Neural Proposal Boundary

**Date:** 18 October 2026 · **Status:** runnable offline reference prototype and opt-in network adapter; no production deployment, live-model evaluation, or actual CASCADE inference exercised in this package. **Not pushed to GitHub.**

**Question:** Can we put a genuine, bounded model interface ahead of a reversible, evidence-carrying, bitemporal knowledge ledger without giving untrusted model output authority to revise what the system knows?

## What changed since v0.2

1. `hybrid_gateway/neural.py`: **OpenAI-compatible `/v1/chat/completions` client** (also supports compatible local Ollama), `json_schema` extraction request, strict parser with duplicate-key rejection, limits, full-value lexical boundary, source quote match, deterministic claim IDs, locked target/tenant/source and optional operator-pinned effective interval. No network call happens unless `extract()` is invoked; remote HTTPS requires explicit opt-in; HTTP restricted to loopback.
2. `hybrid_gateway/pipeline.py`: an **inert staging/review pipeline**. Requires operator-pre-registered unchanged source and a domain-specific semantic validator. `stage()` cannot write events. `commit_one()` requires `reviewer_approved=True` from the trusted caller; **this is still a boolean, not an authenticated human approval**.
3. `hybrid_gateway/cascade_bridge.py`: read-only **CASCADE interoperability probe**. Inject the original `CascadeEngine` and `KnowledgeBlock` classes when available; analysis only consumes temporally visible surviving cited claims; explicit calibrated evidence weights are required. The bridge cannot alter the source ledger or promote heuristic CASCADE decisions to authority. The unit tests use a stub engine, *not the canonical CASCADE implementation*. No result from CASCADE is validated here.
4. `demo_live_inbox.py`: opt-in demonstration that stages fictional source text and **never commits**. Works with a running local compatible model; this research session did not run a real LLM.
5. `tests/test_neural.py`: provider permission gates, local HTTP fixture transport, malicious output tests, source binding, semantic mismatch, atomic parsing failure, bitemporal read-only diagnostics and operator-pinned effective dates.
6. `README_v0.2.md`, prior reports, original charter, baseline fixture and Failure Museum remain in the package for lineage. The prior synthetic 22-case evaluation is unchanged.

## Verify in 3 commands (Python 3.10+, standard library)

```bash
cd lycheetah_hybrid_architecture_v0_3
python -m unittest discover -s tests -v
python demo.py
python run_eval.py
```

At this checkpoint: **54/54 unit and contract tests pass**. The live-provider transport exercised an actual **local HTTP fixture server**; that is not an inference model. `run_eval.py` retains 8/22 latest-document (B0), 13/22 bitemporal retrieval (B1), and 22/22 hybrid ledger (H1) on **author-created fictional cases**. None of these are strong modern version-aware RAG baselines, blinded measures, or live models.

## Opt in to a local neural extraction trial

First start a local OpenAI-compatible API with a model you installed (e.g. Ollama listening on `127.0.0.1:11434`), then:

```bash
python demo_live_inbox.py --model YOUR_INSTALLED_LOCAL_MODEL
```

The demo sends this *fictional* sentence: `Refunds allowed within 14 days.`; the trust boundary pins the field and validity start. Its output is a review queue, not a committed fact. Real model responses may be empty, invalid, or fail the small domain validator. None were collected in this cycle.

For a third-party compatible **HTTPS** provider, this requires an explicit choice:

```bash
export LYCHEETAH_PROVIDER_API_KEY=YOUR_SECRET   # don't commit or print it
python demo_live_inbox.py --model YOUR_MODEL --base-url https://YOUR_PROVIDER/v1 --remote-https
```

**Privacy:** Don't send confidential documents. This is not a sandbox. Provider compatibility varies; the schema-format request may be unsupported. No auto-retry or fallback to unstructured inference is allowed. `--remote-https` may incur fees and transmit the sample to that provider.

## Architecture

```text
TRUSTED OPERATOR             UNTRUSTED MODEL              REVIEWER/CALLER
  register source   --->     structured candidate   --->       review
  pin time/target            immutable source quote          independent approval*
                                       |                            |
                      no commit until strict validation     bitemporal ledger
                                       |                            |
                                       +-------->   historical answer/citations
                                                        |
                                                 CASCADE diagnostics
                                                  [optional, read-only]

* v0.3 reviewer approval is still a caller-controlled boolean, NOT an authenticated reviewer.
```

## Key boundaries

- **Neither structured JSON nor an accurate source quote proves semantic entailment.** The existing Failure Museum deliberately shows 21 loyalty points misbound to 21 refund days. A narrow domain validator blocks that specific failure, not all hallucinations.
- The protocol cannot detect a model's silent omission, resolve conflicting primary documents unaided, authenticate a user, or enforce source publisher identity. It is not prompt-injection-proof.
- Source registry, ledger and approvals are trusted-process research fixtures. Hash chains only detect tampering against a separately retained trusted head. Privacy and robust multi-tenant isolation require external enforcement.
- Real CASCADE classes and their calibrated evidence scores must be supplied by the operator; the current tests use a test double. No CASCADE update is used as a fact override.
- The canonical Lycheetah Assurance Runtime and Action Guard are **not integrated or deployed**. `propose_effect()` remains non-executing.
- The simulated evaluation is unchanged and designed by the authors, not an external breakthrough claim.

## File map

| File | Function |
|---|---|
| `hybrid_gateway/core.py` | v0.2 bitemporal ledger, preserved |
| `hybrid_gateway/neural.py` | new opt-in model extraction adapter |
| `hybrid_gateway/pipeline.py` | inert staging and gated admission |
| `hybrid_gateway/cascade_bridge.py` | read-only CASCADE interface (experimental) |
| `demo_live_inbox.py` | opt-in real-model staging demo; no commit |
| `tests/test_neural.py` | provider, security and diagnostic contract tests |
| `SESSION_REPORT_v0.3.md` | findings and exact scope |
| `RESEARCH_HANDOFF_v0.3.md` | next agent continuation |
| `FAILURE_MUSEUM_v0.3.md` | new failures and inherited limits |
| `README_v0.2.md` | complete preserved previous checkpoint README |
| `RESEARCH_REFERENCES.md` | bibliography from earlier cycle |

**Principle:** No apologies for investigating. No promotion from candidate to fact without evidence and authority.
