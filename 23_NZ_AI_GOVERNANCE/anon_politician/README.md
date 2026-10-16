# Anon Politician — AI-Assisted Democratic Policy Intelligence

> **Status:** `[RESEARCH ARCHIVE & PROTOTYPE CONTINUATION v1.3]`  
> **Jurisdiction:** Aotearoa New Zealand  
> **Parent Domain:** [`23_NZ_AI_GOVERNANCE`](../README.md)  
> **Lineage Anchor:** [`14_MYSTERY_SCHOOL/THE_POLITICIANS_DOOR.md`](../../14_MYSTERY_SCHOOL/THE_POLITICIANS_DOOR.md) & [`02_AURA_L3`](../../02_AURA_L3/README.md)  
> **Preservation Date:** 17 October 2026  

---

## Foundational Lineage: How Work Evolves Across New Lenses

> *"AI is already governing. Not in the future — now. Hiring algorithms are deciding who gets interviews. Welfare systems are calculating who gets support. Moderation systems are deciding what speech is permitted. Credit systems are deciding who gets loans.*  
>  
> *None of these systems are accountable in any way that a constituent can understand, challenge, or appeal through democratic means. That is a political problem. Not a technology problem. Not a philosophy problem. **A political problem** — the kind that ends mandates when it goes wrong and builds legacies when it's handled well.*  
>  
> *The Lycheetah Framework offers four things a politician can actually use: tools to ask the right questions, standards to propose, language constituents already understand, and a record of intellectual honesty that provides political cover."*  
> — **Mackenzie Clark**, [*The Politicians Door*](../../14_MYSTERY_SCHOOL/THE_POLITICIANS_DOOR.md) (March 2026)

### From Constitutional AI to Democratic Policy Intelligence

This project illustrates a central principle of Mackenzie Clark's work: **foundational ideas do not remain static; they evolve through new empirical lenses while preserving their core causal keel.**

1. **The Origin (AURA Protocol & CASCADE):**  
   The technical foundation began in [`02_AURA_L3`](../../02_AURA_L3/) and [`01_CASCADE_L4`](../../01_CASCADE_L4/) as a constitutional framework for AI alignment, exploring value-action invariants, contradiction preservation, and metrics including Trust Entropy (TE/TES), Value-Transfer Ratio (VTR), and the Purpose Alignment Index (PAI).
2. **The Institutional Translation (The Politicians Door & Community AI WOF):**  
   In March 2026, *The Politicians Door* translated these philosophical concepts into practical institutional tools for elected MPs and ministers—grounded in the intuitive New Zealand metaphor of the Warrant of Fitness (`COMMUNITY_AI_WOF.md`).
3. **The Active Continuation (Anon Politician v1.0 – v1.3):**  
   In October 2026, that lineage expanded into a full democratic policy intelligence system. Anon Politician takes the AURA constitutional principles and CASCADE dependency tracing directly into civic life: connecting recurring citizen voice, evidence registers, adversarial cross-party critique, scenario forecasting, transparent revision, and post-implementation outcome tracking.

> *"The technical origin is the user's AURA Protocol and Pyramid Cascade Architecture, also referred to as CASCADE. The founding idea is to keep knowledge and policy reasoning traceable, preserve contradictions, and review conclusions when supporting foundations change—without silently erasing ideas or claiming that coherence proves truth."*  
> — *Anon Politician Master Specification* (October 2026)

---

## What is Anon Politician?

Anon Politician is designed as an **AI-assisted policy intelligence workspace** for Aotearoa New Zealand. It does not replace elected representatives, automate laws, or let AI govern. Rather, it investigates the founder's core incentive hypothesis:

> **The Incentive Hypothesis:** That listening to the public on an ongoing basis, transparently explaining trade-offs, improving policy proposals under adversarial scrutiny, and demonstrating measurable delivery over time can become a competitive advantage in political leadership.

### Three Distinct Civic Signal Lanes (v0.3)
Unlike uncalibrated online surveys, Anon Politician strictly delineates three citizen-input mechanisms:
- **Open Public Voice:** Opt-in civic pulse for discovery, nuance, and participant priorities (never conflated with a general population poll).
- **Population Measurement:** Methodologically sound probability surveys with documented sampling frames, response rates, and uncertainty bounds.
- **Informed Deliberation:** Structured citizen assemblies and deliberative panels with balanced evidence and cross-examination.

---

## Directory & File Guide

This bundle (`Anon_Politician_All_Kept_Work_v1.3`) contains the complete preserved research, specifications, datasets, and runnable codebases:

```
anon_politician/
├── README.md                      # This comprehensive navigation guide & lineage record
├── README_START_HERE.md           # Package overview and version policy
├── SHA256SUMS.txt                 # Cryptographic verification checksums for all files
├── QUICK_ACCESS/                  # Standalone documents, spreadsheets, and zipped kits
└── PROJECT_CORE/
    └── Anon_Politician_Full_Handoff_v1.3/
        ├── 00_START_HERE/         # Onboarding for researchers & models (README_FOR_NEXT_MODEL.md)
        ├── 01_MASTER_SPEC/        # Master Specification v1.0 & Continuation Addendum v1.3
        ├── 02_ORIGINAL_SOURCE/    # Full 62-page foundational source transcript (PDF)
        ├── 02_POLICY_LAB/         # Policy Lab v0.1 prototype & web interface
        ├── 03_FOUNDING_RESEARCH/  # Research dossier, Sonnet review prompt, & source audits (XLSX/DOCX)
        ├── 04_TECHNICAL_PROTOTYPE/# CASCADE audit kits (v0.2/v0.3) & standalone starter engine
        ├── 05_CONTEXT_AND_REFERENCES/# Official NZ baseline sources (Parliament survey, OECD, Treasury LSF/CBAx)
        ├── 06_NEXT_MODEL/         # Operational research protocol & non-negotiable boundaries
        ├── 07_POLICY_LAB_v0.2/    # Controlled 3-arm evaluation harness & development-levies case brief
        └── 08_CIVIC_SIGNAL_v0.3/  # Civic Signal Integrity validator (Python) & interactive UI (HTML)
```

---

## How to Verify Integrity & Run Tests Locally

The archive is fully validated with deterministic unit test suites across its components:

### 1. Check Cryptographic Hashes
```bash
cd 23_NZ_AI_GOVERNANCE/anon_politician
sha256sum -c SHA256SUMS.txt
```
*(Confirms byte-exact integrity across all 59 preserved files)*

### 2. Run Civic Signal Integrity Tests (16 Tests)
Validates declared metadata, sampling claims, representation boundaries, and privacy notice rules:
```bash
cd 23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/08_CIVIC_SIGNAL_v0.3/Anon_Politician_Civic_Signal_Kit_v0_3
python3 -m unittest discover -s tests -v
```
*(All 16 tests pass)*

### 3. Run Policy Lab v0.2 Tests (16 Tests)
Validates case packet loading, blinded 3-arm review aggregation, and dependency queue preservation:
```bash
cd 23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/07_POLICY_LAB_v0.2/Anon_Politician_Policy_Lab_v0_2
python3 -m unittest discover -s tests -v
```
*(All 16 tests pass)*

### 4. Run CASCADE Audit Kit Tests (11 Tests)
Validates dependency DAG traversal, contradiction retention, and epistemic status propagation:
```bash
cd 23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/04_TECHNICAL_PROTOTYPE/CASCADE_Audit_Kit_v0.3_Source
python3 test_cascade.py
```
*(All 11 tests pass)*

---

## Epistemic Safeguards & Democratic Boundaries

The project operates under explicit non-negotiable principles:
1. **AI Assists; Humans Decide:** AI is a retrieval, scenario, and critique engine; accountable elected representatives and citizens make decisions.
2. **Symmetric Scrutiny:** Opposing political perspectives are steelmanned with equal rigor. The platform does not endorse parties, rank candidates, or act as an automated judge of truth.
3. **No Consensus Illusion:** AI summaries must never erase minority perspectives, conditional views, or legitimate value trade-offs.
4. **Transparent Decision Ledger:** Representatives publish a permanent trace showing what input they received, what changed, what was declined, and why.
