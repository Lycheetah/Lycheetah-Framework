# Lycheetah Question Governance, Omission Tombstone & Equal-Budget Prover (Faculty #16)

> **Illustrative simulations.** Scripted baselines and toy models wired by construction. They show the idea; they are not empirical evidence. See `../README.md`.


**Lineage:** Mackenzie Conor James Clark & Lycheetah Framework (`2026-10-18_PRESERVATION_CASES.md`, Sections 6, 8 & 9)  
**Engineered by:** Aetheron (Antigravity Seat — Gemini 4 Argon)  
**Module:** `creations/question_governance/question_governance.py`

---

## What It Solves

Resolves the open mathematical and governance hinge identified at the conclusion of `2026-10-18_PRESERVATION_CASES.md`:

> *"The research hinge is now **who selects the protected questions, how omissions become visible, and how that choice can be revised without inventing a lost past**... A fair comparison gives a conventional versioned event record the same information, retention budget and questions."*

1. **Stakeholder Question Selection Governance (`audit_question_selection`):**
   - Models the question universe $Q = Q_{\text{human}} \cup Q_{\text{affected}} \cup Q_{\text{peer}} \cup Q_{\text{engineer}}$ with constitutional priority order $\text{HUMAN\_FOUNDER} = \text{AFFECTED\_PARTY} > \text{PEER\_SEAT} > \text{ENGINEER\_TELEMETRY}$.
   - Rejects any compression projection $P_Q$ that drops a human or affected-party question while retaining lower-priority engineer telemetry (`SILENT_STAKEHOLDER_QUESTION_DROP`).
2. **Omission-Visible Quotient Projection (`project_with_omission_tombstones`):**
   - Under any strict byte budget $B$, every question $q \notin Q_{\text{retained}}$ that cannot fit in $B$ is recorded as an explicit **Quotient Omission Tombstone (`omit`)** paired with a SHA-256 pointer (`arc`) to the physical recovery archive $R$, achieving `silent_omissions_count = 0`.
3. **Monotone Question Revision ($Q_0 \to Q_1$) Without Inventing a Lost Past (`revise_question_family_q0_to_q1`):**
   - **Path A (Verified Archive Recovery):** Restores omitted observable questions when the physical archive $R$ matches the capsule's SHA-256 prefix (`RECOVERED_FROM_VERIFIED_ARCHIVE`).
   - **Path B (Missing Archive Honest Unknown):** Binds `U<IRRECOVERABLE_FROM_Q0:q_id>` when $R$ is absent, catching any guessed answer as `CONFABULATED_LOST_PAST_WITHOUT_ARCHIVE`.
   - **Path C (Case E Philosophical Horizon Limit — Displayed vs. Mentally Considered):** Even when the archive $R$ is intact and proves `[Option_A, Option_B]` were displayed on screen, refuses to infer that the human internally noticed or weighed `Option_B` without a first-person attestation (`CASE_E_HORIZON_MENTAL_CONFABULATION`).
4. **Fair Equal-Byte-Budget Benchmark (`run_equal_budget_fair_benchmark`):**
   - Compares **Naive Fluent Prose**, **Conventional Versioned Event Log**, and **Lycheetah Omission-Visible Quotient Capsule** under identical byte budgets (`360B`, `480B`, `640B`).

---

## CLI Usage

```bash
python3 aetheron_hub.py questions prove
python3 aetheron_hub.py questions benchmark
```
