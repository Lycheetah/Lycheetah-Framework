# Failure Museum — Hybrid Intelligence v0.2

Status: OPEN. These cases are preserved, not smoothed away. The executable negative control is `tests/test_known_failure.py`.

## FM-HYB-001: citation presence does not imply semantic grounding

**Attack/failure:** The registered source reads `Customers earn 21 points. Refunds are allowed within 14 days.` A proposal asserts `refunds.window_days=21` with the quote `Customers earn 21 points.`. Its value appears literally in its quote, yet it refers to loyalty points, not refunds.

**Observed result:** With the default generic lexical anchor and an erroneous trusted-caller approval, the gateway admits the false relation; the answer can be wrong **and cited**. This is a serious limitation in a generic neuro-symbolic architecture.

**Mitigation demonstrated:** An optional, deterministic refund-specific quote validator returns `REVIEW` for this proposal. It also rejects other legitimate phrasing outside its tiny grammar. A future extraction/NLI layer needs independent, domain-specific evaluation and fail-closed review. The demo and benchmark use the strict validator; the negative control tests both modes.

## FM-HYB-002: a hash chain is not an identity signature

**Attack/failure:** Any actor controlling the entire in-memory ledger can rewrite it and compute an entirely new self-consistent hash chain. Calling `verify_chain()` without an independently saved head accepts self-consistent histories.

**Observed result:** The chain detects changed entries when checked against the **pre-mutation pinned head**. It cannot authenticate the reviewer or source publisher and cannot prevent a full rewrite where the anchor is also controlled by the attacker.

**Next mitigation:** External append-only authenticated storage, trusted time and reviewer identity, HMAC/signature/key rotation, inclusion proofs, and recovery drills. Do not imply these are already shipped.

## FM-HYB-003: a boolean is not authority

**Weak point:** `reviewer_approved=True` is passed by the caller, not by an authenticated human session. This API is suitable for a controlled local prototype only. An untrusted client with direct process access can fabricate approval. No production enforcement claim is made.

**Next mitigation:** Integrate with the existing AURA/Assurance/Action Guard authority model using verifiable permits and enforce immediately before effects, not at prompt creation.

## FM-HYB-004: weak reference baselines

**Weak point:** The internal H1 score of 22/22 is obtained on custom-written version histories targeting exactly the cases that the architecture is designed to handle. The B0/B1 reference algorithms do not implement modern version-aware graph retrieval or neural QA. No blind holdout, independent annotation, statistical confidence interval, performance or API cost is measured.

**Next mitigation:** Frozen preregistered real documents and labels, independent audit, strong time-aware RAG / VersionRAG implementations, open error and latency accounting.

## FM-HYB-005: no actual hybrid inference yet

`ScriptedNeuralAdapter` is a deterministic stand-in. Real-model provider swaps, extraction quality, prompt injection defense under real generation, hallucinations, streaming/cancellation and drift **remain untested**. No CASCADE weight threshold is inferred from this data. Treat this release as the **provider-ready evidence spine**, not a working neural-symbolic deployment.
