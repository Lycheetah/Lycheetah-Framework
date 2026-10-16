# Lycheetah Action Guard — Research & Preservation Archive

> **Status:** `[RESEARCH ARCHIVE / PRESERVATION]`  
> **Domain:** Agent Safety, Closed-Loop Execution Guardrails, Checkpoint Authority  
> **Parent Architecture:** [`34_ASSURANCE_RUNTIME`](../README.md)  
> **Preservation Date:** 17 October 2026  

---

## What is Action Guard?

When AI agents are given tools that can make irrevocable changes in the physical or digital world—such as merging code to production, executing financial transactions, modifying infrastructure, or deleting databases—traditional prompt guardrails and conversational filters are insufficient. 

**Action Guard** is a specialized, fail-closed enforcement architecture designed to sit directly at the execution boundary between the agent and external APIs. It ensures that:
1. **No unapproved side-effects execute:** Every impactful action requires explicit, single-use authorization tied to the exact payload hash.
2. **Replay attacks are impossible:** Approvals and execution tokens are single-use and expire across authority epochs.
3. **Audit trails cannot be forged or truncated:** All events are recorded in an append-only, hash-chained journal verified by an independent local checkpoint authority.
4. **State reconciliation is fail-closed:** If a provider outcome is ambiguous (e.g. network timeout after dispatch), future actions halt until external state is reconciled rather than blindly retrying.

This directory preserves the full chronological research thread, from early in-memory prototypes (v0.5) to a multi-process signed checkpoint authority with a simulated GitHub REST provider (v0.8).

---

## Directory & File Guide

Anyone exploring this directory can navigate the components below:

| File / Folder | Purpose & Contents |
| :--- | :--- |
| **[`README_FIRST.md`](README_FIRST.md)** | Original preservation orientation, evidence discipline statement, and recommended reading order from the research bundle. |
| **[`RESEARCH_HISTORY.md`](RESEARCH_HISTORY.md)** | Detailed narrative of the engineering progression across v0.5 through v0.8, showing what problem each iteration solved. |
| **[`NEXT_STEPS.md`](NEXT_STEPS.md)** | Engineering roadmap, open research questions, and security prerequisites required before any real-world production deployment. |
| **[`ARCHIVE_MANIFEST.sha256`](ARCHIVE_MANIFEST.sha256)** | Cryptographic SHA-256 checksums of every preserved file to guarantee tamper-proof integrity. |
| **[`versions/`](versions/)** | Extracted, readable, and runnable source trees for each milestone of the research. |
| ├── **[`versions/v0.5/`](versions/v0.5/)** | *In-Process Binding:* Action-specific approval binding and in-memory replay prevention. |
| ├── **[`versions/v0.6/`](versions/v0.6/)** | *Durable Ledger:* SQLite persistence, single-use effect intents, authority epochs, and explicit `UNKNOWN` outcome handling. |
| ├── **[`versions/v0.7/`](versions/v0.7/)** | *Audit Integrity:* Cryptographic hash-chained journal history and mandatory dispatch-boundary checkpoints. |
| └── **[`versions/v0.8/`](versions/v0.8/)** | *Separate Process Authority:* Isolated HTTP checkpoint-authority service with signed checkpoints, journal extension validation, state reconciliation, and preview-only GitHub REST adapters. |
| **[`original_release_zips/`](original_release_zips/)** | Byte-exact original `.zip` releases (`v06`, `v07`, `v08`, `pass2`) preserved for provenance and historical auditing. |

---

## Evolution Across Versions

```
v0.5 (In-Process)
 └─ Action-specific approval binding & replay prevention
     │
     ▼
v0.6 (Durable Journal)
 └─ SQLite persistence + Authority epochs + Unknown-state classification
     │
     ▼
v0.7 (Hash-Chained Audit)
 └─ Append-only cryptographic journal + Dispatch checkpoint requirement
     │
     ▼
v0.8 (Isolated Checkpoint Authority)
 └─ Multi-process signing service + Journal extension proofs + State reconciliation
```

---

## How to Verify Integrity & Run Locally

### 1. Check Cryptographic Integrity
To verify that no file has been altered since archival:
```bash
cd 34_ASSURANCE_RUNTIME/action_guard
sha256sum -c ARCHIVE_MANIFEST.sha256
```
*(All 48 files should report `OK`)*

### 2. Run the Latest (v0.8) Test Suite
The v0.8 test suite exercises the checkpoint authority, process restarts, tampering detection, and simulated provider workflows:
```bash
cd 34_ASSURANCE_RUNTIME/action_guard/versions/v0.8
python3 test_action_guard_v08.py
```
*(Runs 27 automated tests verifying tamper-proofing and fail-closed behaviors)*

### 3. Run the Full v0.8 Verification Suite
To run the automated verification script (generates benchmark and verification matrices):
```bash
cd 34_ASSURANCE_RUNTIME/action_guard/versions/v0.8
python3 run_v08_verification.py
```

---

## Epistemic Boundary & Evidence Standard

- **Synthetic & Local:** The benchmarks and tests provided are locally authored, deterministic synthetic suites designed to test edge cases, race conditions, and tampering detection.
- **Not Independent Certification:** These results do not constitute third-party security certification or proof against root/filesystem-level host compromises.
- **No Live Write Calls:** The included GitHub adapter runs in preview-only simulation mode and never issues live API writes or merges to remote repositories.
