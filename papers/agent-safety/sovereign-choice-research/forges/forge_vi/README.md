# LYCHEETAH — Sovereign Choice Forge VI

**18 October 2026 · Cryptographic approval and counterfactual-agency research · Not deployed**

> Power is what an intelligence can do. Sovereignty is what remains yours while it does it.

## Two connected investigations

1. **Local engineering** — Extend the verified Lycheetah `CommitFence` and Forge V `AtomicChoiceLedger` with Ed25519-signed, exact-action, expiring approval/withdrawal events. Store versions and permissions in the same SQLite transaction. Install a guarded finality trigger so a signed approval cannot *expire between an early check and local insertion* unnoticed. Do not rewrite the upstream `commit()` implementation.
2. **Philosophy / UX** — Develop the **Counterfactual Agency Horizon (CAH)**, a set-valued research proposal for the alternatives genuinely available to people, and an observational choice-surface checklist that refuses to score a person's free will.

## Directory map

- `code/attested_gateway.py` — cryptographic signed gateway and local finality trigger.
- `code/choice_ledger.py` — exact byte copy of the Forge V atomic intention layer, included to make Forge VI runnable without extracting the lineage archive.
- `code/choice_surface.py` — manual interface observation schema with `unknown` statuses.
- `tests/` — scripted cryptographic, concurrency, revocation, expiry, threat-model and conceptual audit tests.
- `docs/SOVEREIGN_POSSIBILITY_CHARTER_v0.6.md` — philosophical advance, research agenda and public charter.
- `docs/THREAT_MODEL_AND_FINDINGS.md` — verified claims, negative controls and gaps.
- `prototype/sovereign_possibility_lab.html` — standalone offline educational simulation (no real signing).
- `upstream_mirror/` — unchanged upstream code with original MIT license.
- `lineage/FORGE_V_COMPLETE.zip` — preserved Forge V, which contains IV, III, II and the original I charter.
- `evidence/` — verification results, hashes, test output and experiment notes.

## Run

Requires Python 3.10+ and `cryptography` (tested locally with Python 3.13 and cryptography 46.0.4).

```sh
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

Run from this directory. Tests generate fresh ephemeral Ed25519 keys only as fixtures and interact with **temporary local SQLite databases**; no email or remote request is sent. Never use in-process test keys as proof of human identity.

## Evidence ceilings

The software proves narrow properties about this code and its synthetic setup: signed message verification, exact action hashes, revision and revocation checks, local expiry at finality, and atomic local records. The code cannot establish a living person's informed, uncoerced consent. It cannot cancel a remote API effect after release. Any operator with privileged DB access can remove the trigger. No production deployment, security audit, real-agent evaluation, or user comprehension study was performed.

CAH is **a philosophical/research proposal**, not a scientific theory of free will or new established mathematical law. The UI audit is deliberately not a numeric measure of sovereignty.

## Upstream provenance

Mirror copied from the connected public `Lycheetah/Lycheetah-Framework` GitHub repository (`master`):

- `papers/agent-safety/frontier-controls/01_commit_time_authority_v0_7/commit_fence.py` Git blob SHA-1 `0af8050808569a098e11fb72a9f7d6c4c15044bb`.
- `papers/agent-safety/frontier-controls/research_support.py` Git blob SHA-1 `0f623b6614be03a2f7bf65f2a5ea3fe1b12e51e9`.

Their bytes were verified against the Git blob hash formula, not signed upstream provenance. The original MIT license and copyright are included. `code/choice_ledger.py` is copied verbatim from Forge V, not rebranded as upstream code. **No files were committed to GitHub.**
