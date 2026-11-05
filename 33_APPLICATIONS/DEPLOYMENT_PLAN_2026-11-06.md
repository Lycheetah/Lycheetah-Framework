# Lycheetah as an architecture for accountable cognition — and how it reaches the real world

**Status:** PROPOSED plan, 2026-11-06, written for Mackenzie Conor James Clark at his request.
Not adopted until Mac says so. Every "exists" below names a file on branch
`claude/youthful-volta-di3ma8` or `master`; every "next" is unbuilt.

## 1. What Lycheetah is, said plainly

Not a model, and not a cognitive architecture in the research sense (systems that model how a
mind works). It is the layer around *any* model that does the jobs a model is bad at:

> **The model thinks. Lycheetah decides what is allowed, remembers why, knows what it does not
> know, and keeps a person in charge.**

Read through a cognitive-architecture lens, the working parts map like this:

| Function | In a mind | In Lycheetah | Exists today | Missing |
|---|---|---|---|---|
| Reasoning / perception | cortex | **any model** (local or hosted) | — | deliberately not ours |
| Working + episodic memory | carrying context forward | `lycheetah/handoff.py`, `lycheetah/compaction/` (10 protected fields incl. authority, dissent, unknowns) | yes, tested | measured benefit to people |
| Belief revision | updating on evidence | CASCADE (`12_IMPLEMENTATIONS/core/`), Truth Pressure | yes, modelled | real-world inputs |
| Inhibition / executive control | stopping the wrong action | `lycheetah/assurance/` ActionGateway: exact-action binding, single use, TTL, revocation, UNKNOWN ≠ failed | yes; 9/10 on the Approval Integrity Suite | C10: a screen bound to the action |
| Metacognition | knowing what you don't know | UNKNOWN outcomes, evidence-capped enforcement, claim labels | yes | calibration on real data |
| Autobiographical record | "what did I actually do?" | receipts, checkpoint authority, in-toto export, Failure Museum | yes | external anchoring |
| Learning across cycles | getting better without losing the plot | Sync Zone cycle contract (`18_EXPERIMENTAL/sync-zone-recursive-framework/`) | experimental | outside review |
| Values | conscience | AURA (normative spec) | as a spec | not machine-checkable, and the repo says so |
| The human | will, taste, veto | principal-only ratification; approvals | yes | approval UI people can trust (C10) |

**The honest one-liner for outsiders:** *a trust layer for AI agents — open source, local-first,
made in Aotearoa.* "Cognitive architecture" is a fine internal lens; in public it invites the
question "where's the cognition?", and the strong answer is that the cognition is swappable and
the accountability is not.

## 1b. Added later the same day: research and a working skeleton

- [Research memo](ON_DEVICE_NZ_RESEARCH_2026-11-06.md) with sources: the best open models trail the
  closed frontier by ~4 months (Epoch AI), but **small models are not well measured anywhere**; a
  3B model runs on a flagship phone at roughly 10–25 tokens/s with real battery cost; NZ's bet is
  big onshore data centres (contested), and on-device is the complementary bet; Te Hiku Media's
  Kaitiakitanga licence is the precedent for Māori data; local-model apps (Jan, LM Studio, Ollama)
  already solve "run a model locally" and none offers approvals that bind, receipts or a witness.
- [On-device assistant skeleton](on_device_assistant/README.md): a terminal assistant whose web
  access goes through the gateway; its own approval path scores 10/10 on the Approval Integrity
  Suite; a blocked fetch is reported as UNKNOWN rather than invented. No model is bundled.
- [Pre-registered benchmark](on_device_assistant/BENCHMARK_PREREG.md): twenty everyday NZ tasks,
  blind raters, predicted local/frontier helpfulness ratio 0.70–0.85. **This is the investable
  number**, and nobody has it yet.

**Size, for the record:** the app is roughly 1–2.5 GB on a phone or 2–5 GB on a laptop, almost all
of it the model; the Lycheetah layer is a few MB. No server is needed for the core. The one hosted
piece worth having is an NZ witness that stores receipt hashes only.

## 2. Why now

Agents are starting to act — refunds, emails, records, payments — and every framework has an
"approve" button that, on today's evidence (`papers/agent-safety/approval-integrity-suite/`),
usually doesn't bind what runs. Compute is concentrated offshore and contested; people and
organisations here increasingly want AI that runs on their own devices with their data at home.
Lycheetah's layer is small, model-agnostic and already runs locally. Those two trends meet in it.

## 3. Deployment, in four phases — each ends at an outside witness

### Phase 0 — ship what exists (this month)
- Merge the two review branches (Mac's call). Fix C10 in the gateway: return a rendering built
  from the canonical action with every `GateDecision` (small, additive, tested by the suite).
- Publish the package to PyPI (name availability UNVERIFIED) and the Approval Integrity Suite post.
- Run the pre-registered benchmark on a laptop with one chosen 3–4B model.
- **Witness:** one developer Mac has never met runs the suite on their own approval layer and
  reports the result in an issue.

### Phase 1 — a drop-in guard for agent builders (1–3 months)
- Adapters wrapping the gateway for the tool-calling surfaces people already use (MCP first — the
  repo already has an MCP guard), each shipped with the suite as a CI check.
- **Witness:** three outside projects run it in CI; one bug found by a stranger and fixed in public.

### Phase 2 — the NZ local assistant pilot (3–6 months)
- An open-weight small model on a laptop (phone later), every web or tool call through the gateway,
  handoff memory, receipts the user can read. Nothing trained from scratch: that costs millions;
  adapting an existing small model does not.
- New Zealand content only with consent; te reo Māori only with Māori data-sovereignty partners
  (learn from or work with Te Hiku Media's approach). Policy frame: Mac's six data rights,
  `23_NZ_AI_GOVERNANCE/DATA_SOVEREIGNTY_FOR_NEW_ZEALANDERS.md`.
- **Witness:** 10–20 testers who aren't Mac use it for two weeks; a pre-registered handoff-fidelity
  study (`SYNC_ZONE_TASKS.json` SZ-010) reports, including null results.

### Phase 3 — one real organisation (6–12 months)
- One NZ organisation with real consequential actions (a council service, an iwi trust, a small
  business's refunds or records) runs the guard in production on a bounded workflow.
- Independent security review before it touches anything real. Check obligations against the
  Privacy Act 2020 and the Algorithm Charter for Aotearoa New Zealand with someone qualified.
- **Witness:** the organisation's own staff, and the reviewer's report — published, findings and all.

## 4. How it pays for itself (honestly)

Open core: the library, suite and local assistant stay free and MIT. Paid: integration and support
for organisations, NZ-hosted or on-premises deployment, and review of their approval flows using
the suite. This needs no hardware run, no inventory and no outside equity to start. Revenue figures
are not projected here because none have been earned yet.

## 5. What would sink it

- **Claim inflation.** One overclaim found by a stranger costs more trust than ten features earn.
  Keep every public number tied to a command anyone can run.
- **Two doors in one room.** The mythos, school and stories are real work with their own audience.
  Give the deployable layer its own plain front door so an engineer never has to read past
  alchemy to find `pip install`.
- **One person carrying everything.** Phases 1–3 each need one outside person (a developer, a tester
  cohort, a partner organisation). Finding them is the real work of each phase.
- **Scope.** Saying no to the next 30 repos is what makes this one land.

## 6. Decisions for Mac

1. Adopt the frame ("trust layer"; "architecture for accountable cognition" internally) — or reject it.
2. Approve Phase 0: merge, gateway C10 fix, PyPI, the post.
3. Choose the plain public name for the deployable layer (Lycheetah stays the research home).
4. Say who the first outside witness could be.
