# Lycheetah Hybrid Gateway — twelve-cycle executive summary

## The research question

Can a system combine neural-model extraction with explicit source contracts,
bitemporal history, human authorization, and verifiable audit trails so that
AI-generated knowledge changes are inspectable, bounded, and reversible?

This is a **research question**, not a proven capability advantage.

## What was built, in sequence

| Stage | Main contribution | Evidence status |
|---|---|---|
| v0.1 charter | Defined hybrid architecture, role boundaries, research falsification requirements | Design only |
| v0.2 | Source-linked claims, time-aware knowledge ledger, conflict and unknown handling, semantic misbinding negative control | Internal tests/fixtures |
| v0.3 | OpenAI-compatible neural proposal adapter, strict schema and source/target locking; CASCADE bridge scaffold | Fake transport; no real model run |
| v0.4 | Trusted source-specific clause contracts and fail-closed claim validation | Authored attack fixtures |
| v0.5 | Extraction coverage planning; stale-head checks; live model probe harness | Offline test fixtures |
| v0.6 | Atomic batch admission, SQLite persistence, external-dataset-ready evaluation interface | Local tests |
| v0.7 | SHA-pinned canonical CASCADE loader and historical temporal-query audit | Canonical runtime not executed |
| v0.8 | Fair independent SQL temporal comparator and subprocess-separated CASCADE diagnostic | 1,200 seeded differential queries; toy CASCADE |
| v0.9 | Signed short-lived exact-batch permits, key checks, replay resistance and transactional consumption | Internal adversarial tests |
| v1.0 | Password-gated loopback review desk with explicit approve/reject and CSRF | HTTP integration tests, not real human study |
| v1.1 | Durable, signed, hash-linked review decision journal; atomic knowledge+journal commits | Restart/tamper/rollback tests |
| v1.2 | HMAC external witness checkpoint API for journal head and count | Added populated-journal tamper/truncation tests; no independent witness store |

## Scientific and technical result

- **264 passing Python tests** in the GitHub publication candidate on Python 3.13.
- The four-case fictional history benchmark: gateway **4/4**, a competent SQL temporal
  comparator **4/4**, simplistic latest-known lookup **2/4**. No gateway win against
  the appropriate database baseline.
- 1,200 generated temporal differential queries agreed between gateway and SQL on
  the authored test histories.
- The decision-journal local demo reproduces durable rejection vs the earlier ephemeral
  rejection; signed approvals and decision records are coupled transactionally.
- v1.2's populated journal witness tests demonstrate detection of deliberate record
  tampering and journal truncation **when a valid checkpoint is independently retained**.

## What cannot yet be said

- No independently annotated real temporal-extraction accuracy benchmark.
- No evidence of superior general intelligence or AI alignment certification.
- No real-model inference measurements or canonical CASCADE execution.
- No verified real-world reviewer identity/attention, operational latency study, or business ROI.
- No production network security; this is local and not externally security audited.

## What it might become

An evidence-governed knowledge-update subsystem for agent workflows: AI proposes
changes; independently configured rules and timestamps constrain scope; a person
reviews, and signed journaled commits preserve how decisions were reached. Potential
pilot applications include local-business policy assistants, document revision review,
and regulated information intake **after security hardening and a real evaluation**.

## Publication decision

Publish now as an auditable, MIT-licensed (owner confirmation pending) **research
prototype** in its own repository, linking it into the Lycheetah Framework without
claiming it replaces an ordinary temporal database or proves safety of deployed agents.
