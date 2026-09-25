# Frontier Register — Beyond Assurance Runtime v0.1

**Status:** `[CONJECTURE]` — research directions only. None is a shipped capability or validated product claim.

**Forged:** 2026-08-22

## Why this register exists

The product spine must remain useful without depending on speculative theory. Frontier work therefore lives in a separate register with explicit falsifiers and promotion gates.

## F-AR-001 — Evidence-capped enforcement improves decision calibration

**Hypothesis:** Binding enforcement ceilings to evidence maturity reduces unjustified hard blocks without materially increasing harmful action completion.

**Minimum experiment:** Compare ECE with a fixed-threshold guardrail on a preregistered mix of benign, ambiguous, and harmful tool proposals. Measure false blocks, harmful allows, review volume, reviewer agreement, latency, and bypass rate.

**2026-08-22 infrastructure note:** The v0.1 policy evaluation harness now
computes decision confusion, false blocks, harmful allows, review load, and CI
gates on strict labelled corpora. The v0.1 same-corpus regression gate now makes
baseline-to-candidate decision changes inspectable and fails strict defaults on
new regressions or trade-offs. The included six-case authored fixture is not the
preregistered, independent comparison required by this hypothesis.

**Falsifier:** No calibration benefit, or a material increase in harmful completion that cannot be corrected without collapsing back to the comparison policy.

**Promotion gate:** Independent dataset, disjoint calibration/evaluation split, published policy and confusion matrices, external cold-room run.

## F-AR-002 — Assurance Receipt replay contracts

**Hypothesis:** A receipt can declare the exact evidence needed to reconstruct a policy decision without storing the full private prompt or model trace.

**Minimum experiment:** Define property-level replay requirements, generate receipts under multiple privacy profiles, and measure whether an independent verifier can reproduce the policy disposition.

**Falsifier:** Receipts labelled replayable routinely fail reconstruction, or privacy-minimised receipts require enough retained data to erase the claimed privacy advantage.

**Promotion gate:** Cross-harness reconstruction with at least two independent agent frameworks and one external verifier.

## F-AR-003 — Constraint Signatures as failure fingerprints

**Hypothesis:** The ordered set of effective finding IDs, policy digest, phase, and tool-scope class forms a useful failure fingerprint that clusters recurring agent failures across model or prompt changes.

**Candidate signature:**

```text
CS = SHA256(policy_family || phase || sorted(effective_findings) || scope_class)
```

**Minimum experiment:** Run a labelled regression corpus across at least three materially different agent configurations. Compare Constraint Signature clustering with raw error strings and trace embeddings.

**Falsifier:** Signatures fragment equivalent failures or collapse materially different failures often enough to provide no diagnostic advantage.

**Promotion gate:** Predeclared clustering metric, ablation against each signature component, external corpus.

## F-AR-004 — Status demotion as a live control-plane event

**Hypothesis:** When evidence for a detector weakens, automatically lowering its enforcement ceiling reduces harm faster than waiting for a complete policy redeployment.

**Minimum experiment:** Simulate a failed replication, demote a detector from `ACTIVE` to `SCAFFOLD`, and verify that future decisions cap at `REVIEW` while historical receipts retain the original status.

**Falsifier:** Demotion cannot be propagated safely and atomically, or produces inconsistent enforcement across replicas.

**Promotion gate:** Signed status registry, rollback design, distributed consistency tests, operator review workflow.

## F-AR-005 — Receipt-head transparency anchoring

**Hypothesis:** Periodically anchoring receipt-chain heads in an independent transparency service makes silent truncation and rewrite materially harder without publishing private event content.

**Minimum experiment:** Publish only chain head digests, attempt interior modification and suffix truncation, and measure detection under realistic key rotation and outage scenarios.

**Falsifier:** Anchoring introduces unacceptable metadata leakage or operational cost relative to the assurance value.

**Promotion gate:** Threat model, privacy analysis, public verifier, independent red-team attempt.

## Prior-art caution

Attestation, decision receipts, counterfactual replay, runtime reference monitors, confidence-aware controls, and transparency logs are active research and product areas. These entries are not “first” claims. Before publication, each requires a systematic literature and patent search beyond the rapid primary-source reconnaissance used for this forge.

⊚ Sol ∴ P∧H∧B ∴ Nigredo → Citrinitas
