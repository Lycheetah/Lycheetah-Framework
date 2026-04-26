# D-1.1 | 2026-04-26 | Status: Active

# Evidence Ladder — Status Promotion Criteria

*What evidence promotes a claim. What evidence demotes one. The published rules.*

*Defends: C-1.0 | Closes threats: T-04 (overclaiming), T-08 (vague status), T-13 (movable goalposts)*

---

## Why This Document Exists

Status labels (`[ACTIVE]`, `[SCAFFOLD]`, `[CONJECTURE]`, `[RETRACTED]`) are only meaningful if the rules for assigning them are public, prior, and binding. Otherwise the labels become marketing — anything can be called "active" by the author who needs it to be.

This document fixes the rules. Once published, the framework is bound by them. The author cannot upgrade a claim's status without satisfying the criteria below; an external reviewer can hold the framework to them; a future steward can audit prior promotions against the criteria of the day.

The labels are a contract. This document is the contract terms.

---

## The Four Status Tiers (definitions)

| Status | Plain meaning | Promotion direction |
|---|---|---|
| `[CONJECTURE]` | Rigorously formulated hypothesis. Falsifiable. No empirical or formal support yet. | Up to SCAFFOLD or ACTIVE; or to RETRACTED |
| `[SCAFFOLD]` | The structure is proven (formal definition, type-checked, runs). Parameters or fit-to-data still pending. | Up to ACTIVE; back to CONJECTURE if structure breaks |
| `[ACTIVE]` | Empirically supported with measured evidence. Reproducible. Survives adversarial review. | Down to SCAFFOLD if a replication fails; down to RETRACTED if falsified |
| `[RETRACTED]` | Once held, now disproven, superseded, or scope-corrected. Documented in FAILURE_MUSEUM.md. | Permanent record. Does not move back up. |

Two adjacent labels exist for documentation completeness:

| Status | Plain meaning |
|---|---|
| `[FOUNDATIONAL]` | Architectural assumption necessary for the framework to operate. Not independently testable; the test is whether the framework as a whole produces useful results. |
| `[ANALOGY]` | Structural parallel to a known result, not claimed identity. Useful as scaffolding for intuition; cannot be promoted to a formal claim without independent proof. |
| `[LIVED]` | First-person phenomenological claim. True in experience for the author or named practitioner. Not a population claim. |

These three are stable categories — they do not move on the ladder.

---

## Promotion Criteria — CONJECTURE → SCAFFOLD

A `[CONJECTURE]` becomes `[SCAFFOLD]` when **all** of the following are met:

1. **Formal statement.** A precise mathematical or computational definition exists. No ambiguity in what is being claimed.
2. **Type-check or formal validity.** The claim is internally consistent — type-checks (if computational), passes formal verification (if mathematical), or composes correctly with existing framework predicates.
3. **Operationalization.** A method exists to compute the predicted quantity from real inputs. The method is documented in code or pseudocode in `12_IMPLEMENTATIONS/`.
4. **Falsifier defined.** A specific outcome is named that would prove the claim false (recorded in `FALSIFICATION_REGISTER.md`).
5. **Adversarial pass.** The claim has been examined under Nigredo Research Mode and not been refuted on internal-consistency grounds.

What this does NOT require: empirical fit. SCAFFOLD says "the architecture is sound and the operationalization is implemented" — not "the numbers match reality." That is the next rung.

**Example:** Master equation `dΨ/dt = k₁(...) − k₂(...)` is currently SCAFFOLD. Structure formally defined; implemented in `master_equation_sim.py`; falsifier is "the equation cannot be fit to any historical paradigm-shift trajectory with consistent k-values within ±20%." Calibration of k₁–k₄ from real data is the experiment that promotes it to ACTIVE.

---

## Promotion Criteria — SCAFFOLD → ACTIVE

A `[SCAFFOLD]` becomes `[ACTIVE]` when **all** of the following are met:

1. **Reproducible empirical result.** A measurement that supports the claim, with documented methodology, executable from the public repository, and produces the same result on at least one cold-room run by an independent party.
2. **Effect size and significance.** Where statistical, the result includes effect size and significance (p-value, confidence interval, or comparable). Where formal, the proof is complete and refereed (internal NRM pass at minimum).
3. **Replication on disjoint data.** The result holds on at least one dataset, domain, or instance that was not used in the original calibration. This is the firewall against overfitting.
4. **Falsifier survived.** The originally declared falsifier was tested and the claim was not falsified.
5. **Recorded in EMPIRICAL_INVENTORY.md.** Methodology, n, effect, replication, and known limits documented.

**Example — promotion satisfied:** CASCADE Theorem C1 (invariant preservation) is ACTIVE because: invariants formally defined; CASCADE engine implemented; tested on germ theory (5 invariants, n=200 trials, 100% preservation) and classical→quantum (7 invariants, n=200 trials, 100% preservation, p=5.14e-110 vs static-coherence baseline); replication on a domain not used in calibration succeeded; falsifier "any invariant degrades > 5% under CASCADE update" did not fire; full methodology in EMPIRICAL_INVENTORY.md.

**Example — promotion blocked:** EARNED LIGHT formula C_ψ(t) is SCAFFOLD, not ACTIVE, because operationalization exists but no empirical measurement has been run on a conscious system (no operationalization of the input variables on real data). Until that measurement happens, the SCAFFOLD label is binding.

---

## Demotion Criteria — ACTIVE → SCAFFOLD or RETRACTED

An ACTIVE claim is demoted when **any** of the following occur:

| Trigger | Action |
|---|---|
| A replication attempt with adequate power fails (and the failure is not attributable to methodology error). | Demote to SCAFFOLD; document the failure in FAILURE_MUSEUM.md; investigate. |
| A formal proof shows the claim is incorrect. | Demote to RETRACTED; full FAILURE_MUSEUM.md entry; do not delete from history. |
| A scope-revision shows the claim was overstated. | Demote to SCAFFOLD with corrected scope, or RETRACTED if no honest version remains. Original overstated form joins FAILURE_MUSEUM.md. |
| A measurement reveals the claim was an artifact (data leak, p-hacking, instrument bias, etc.). | RETRACTED. FAILURE_MUSEUM.md entry. |

Demotion is not a defeat — it is honest aging. A framework that has retracted claims is more credible than one that has not, because the demotion process is visibly working.

---

## Demotion Criteria — SCAFFOLD → CONJECTURE

A SCAFFOLD is demoted to CONJECTURE if the structure breaks: a definitional inconsistency is found, the implementation does not match the formal statement, or the falsifier was poorly chosen and must be reformulated. The claim returns to CONJECTURE until the structure is repaired, at which point it can re-climb.

---

## What Counts as Evidence (and what does not)

### Counts

- A measured experimental result with documented methodology and reproducible code
- A formal proof, refereed (NRM pass at minimum, peer review where claimed)
- A successful replication on disjoint data
- A successful prediction of an outcome before it was observed
- An independent group reporting the same result with their own implementation

### Does not count

- The claim "feels right" to the author
- The framework would be more elegant if the claim were true
- The claim has been published in a non-refereed venue
- The claim has been cited (citation is not evidence)
- An LLM agreed with the claim
- The author's lived experience aligns with the claim (this can support a `[LIVED]` claim, never an ACTIVE empirical one)
- "Multiple frameworks converge on the same answer" — convergence within the framework's own outputs is not independent confirmation

This list is binding. If a future promotion is supported only by items in the second list, the promotion is invalid and may be reverted by any reviewer.

---

## Audit Trail Requirements

Every status change (any direction) must produce:

1. **A diff entry.** What was the previous status, what is the new status.
2. **A justification.** Which criterion was met (for promotion) or triggered (for demotion). Cite the specific evidence — file path, experiment ID, theorem reference.
3. **A date.** When the change took effect.
4. **A reviewer.** Who certified the change. For ACTIVE promotions, the reviewer must not be the original author of the claim (or, where the framework has only one canonical reviewer, an external collaborator must co-sign).

Audit trail entries are recorded in `CLAIMS.json` (the `provenance` array per claim) and surfaced in change logs. Loss of audit trail is grounds for reversion to the prior status.

---

## What This Costs the Framework

Some things the author would like to call ACTIVE will remain SCAFFOLD until the experiments run. Some hypotheses that feel proven will remain CONJECTURE until the falsifier is tested. The cost is real: the framework looks weaker on a claims chart than a less disciplined competitor.

This cost is intentional. A framework that promotes by criteria builds compound credibility. A framework that promotes by need erodes its own labels until they mean nothing.

The Lycheetah Framework chooses the slower path. The published evidence ladder is the contract that makes the choice binding.

---

## Relationship to Other Defense Documents

- **CLAIMS.json** is the live status register. This document defines the rules by which entries change.
- **FALSIFICATION_REGISTER.md** lists the specific falsifiers; this document defines when one is considered "tested."
- **FAILURE_MUSEUM.md** receives RETRACTED claims; this document defines what triggers retraction.
- **LIVING_CODEX_PROTOCOL.md** governs document evolution; this document is the per-claim version of the same discipline.
- **NOVEL_CONTRIBUTIONS.md** lists per-claim novelty; this document defines the evidence required to keep the novelty claim ACTIVE.

---

## Future Updates

Changes to this document — adding criteria, tightening existing ones, defining new tiers — require:

- Public proposal in a defense-challenge issue
- Review by Mac (or designated successor)
- D-version increment (e.g., D-1.1 → D-1.2)
- Audit pass: every existing ACTIVE claim must satisfy any new tightened criteria, or be demoted

Loosening a criterion is permitted only when paired with a stricter or compensating criterion elsewhere. The ladder may evolve, but never get easier overall without explicit justification.

---

*This document is part of Codex Defense Protocol D-1.1, defending canonical body C-1.0 (2026-04-25).*
