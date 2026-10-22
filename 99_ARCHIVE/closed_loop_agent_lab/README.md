# Lycheetah Closed-Loop Agent Lab & Cybernetics Research Vault

> **Status:** `[RESEARCH ARCHIVE & RUNNABLE LAB SUITE v5.1]`  
> **Domain:** Cybernetics, Closed-Loop Agent Safety, Ingress Quotas, State Integrity  
> **Parent Architecture:** [`34_CYBERNETICS`](../../34_CYBERNETICS/README.md)  
> **Preservation Date:** 17 October 2026  

---

## Foundational Lineage: Where the Loops Close

> *"A loop regulates only where it closes. A sensor that reads, a comparator that judges and no actuator that acts make a measurement, not a regulator. That is not a defect, but it must not be described as one."*  
> — [*34_CYBERNETICS / Where the Loops Close*](../../34_CYBERNETICS/README.md)

In the theoretical foundations of the Lycheetah Framework, cybernetics provides the mathematical grammar of regulation: Ashby’s Law of Requisite Variety, the Good Regulator Theorem, and ultrastability. 

This research vault preserves the practical, software-engineering culmination of that thesis. Across 50+ research increments (from v1.0 through v5.1), the **Closed-Loop Agent Lab** implements real, fail-closed actuators, brokers, and witnesses that ensure autonomous AI agent systems can be regulated safely in code.

---

## Technical Focus: Ingress Quotas & Overflow State Integrity (v5.0 – v5.1)

The latest milestone (v5.1) focuses on **bounded-cardinality overflow state integrity** within hierarchical attempt-rate quota systems:

1. **Fixed-Shard Fallback:** When cardinality pressure spikes (e.g. distributed bursts or bot traffic), requests route through fixed overflow shards rather than exhausting local memory or unboundedly expanding tracking tables.
2. **Fail-Closed Ledger Reopening:** When a quota ledger is reopened across process restarts, v5.1 explicitly validates that overflow-shard rows are intact and token values remain strictly within bounds. Malformed or tampered rows are rejected immediately rather than silently resetting or recreating quota capacity.
3. **Hierarchical Fairness:** Builds upon v4.9’s dual controls: enforcing per-peer rate fairness alongside aggregate IPv6 CIDR prefix caps.

---

## Directory & File Guide

Anyone exploring this vault can navigate the components below:

```
closed_loop_agent_lab/
├── README.md                      # This navigation guide & technical architecture map
├── SHA256SUMS.txt                 # Cryptographic SHA-256 sums for all 100+ files
├── 00_START_HERE/
│   └── READ_ME_FIRST.md           # Original archive orientation & reading recommendations
├── 01_LATEST_RELEASES/
│   ├── lycheetah_closed_loop_agent_lab_v5.1.zip          # Full cumulative snapshot through v5.1
│   └── lycheetah_ingress_overflow_state_integrity_v5.1.zip # Standalone v5.0/v5.1 package
├── 02_HISTORICAL_AND_FOCUSED_ZIPS/
│   ├── cumulative_snapshots/      # Historical snapshots (v4.1 through v4.9)
│   ├── focused_standalone_modules/# Milestones (mTLS, quotas, witness nodes)
│   └── companion_research/        # Human-AI Transition & Rabbit Holes architecture
├── 03_LAB_SOURCE_TREE/
│   └── lycheetah_closed_loop_lab/ # Extracted, inspectable, and runnable lab modules (r1 – r41)
│       ├── r8_trusted_witness_v1_8/            # Witness attestation and tamper evidence
│       ├── r9_durable_action_outbox_v1_9/      # Crash-resilient transactional action broker
│       ├── r30_mtls_registry_gateway_v4_0/     # Mutual TLS node registry & identity
│       ├── r34_shared_preauth_quota_v4_4/      # Cross-agent distributed quota coordination
│       ├── r39_hierarchical_attempt_quotas_v4_9/# Per-peer & prefix attempt-rate limits
│       └── r41_overflow_state_integrity_v5_1/  # Overflow-shard validation & retest suite
└── 04_COMPANION_RECORDS/
    ├── ZIP_CATALOG.csv            # Detailed index of all historical archive packages
    ├── CONTENTS_MANIFEST.csv      # File-by-file hash manifest
    └── *.log / *.json             # Historical regression logs and archive verification proofs
```

---

## Evolution of the Lab Across Milestones

| Milestone | Key Capability Introduced | Cybernetic Function |
| :--- | :--- | :--- |
| **v1.8** | Trusted Witness nodes | Independent observer validating actual effect execution |
| **v1.9** | Durable Action Outbox | Transactional actuator preventing duplicate/lost dispatches |
| **v2.8** | Reconciliation Workers | Closed-loop state alignment following ambiguous network timeouts |
| **v4.0** | Mutual TLS Gateway | Cryptographic identity boundary between agent and orchestrator |
| **v4.4** | Shared Pre-Auth Quota | Distributed attempt-rate regulation across concurrent worker threads |
| **v4.9** | Hierarchical Quotas | Multi-tier attempt caps (individual IP + IPv6 prefix aggregation) |
| **v5.0** | Fixed-Shard Fallback | Bounded-cardinality protection against state exhaustion |
| **v5.1** | Overflow State Integrity | Strict tamper rejection on ledger reload; 54/54 tests passing |

---

## How to Verify Integrity & Run Tests Locally

### 1. Check Cryptographic Hashes
```bash
cd 99_ARCHIVE/closed_loop_agent_lab
sha256sum -c SHA256SUMS.txt
```
This command checks the **complete original vault**, including its result logs.
The 21 October review found that the Git tree omits 374 `.log` paths named by
this 1,788-entry manifest. They exist in the local preservation vault, so a local
pass does not establish availability in a clean checkout. The two tracked latest
ZIPs contain matching bytes for 373 of those log records; one companion retest
log was not found there. Complete clean-checkout preservation remains an open
repair, recorded in the [Framework review](../../28_DEFENSE/FULL_FRAMEWORK_REVIEW_2026-10-20.md).
Do not use `--ignore-missing` to turn that gap into a successful full-vault check.

### 2. Run the Latest v5.1 Test Suite
Exercises the shared ingress quota, fixed-shard fallback, and overflow state validation:
```bash
cd 99_ARCHIVE/closed_loop_agent_lab/03_LAB_SOURCE_TREE/lycheetah_closed_loop_lab/r41_overflow_state_integrity_v5_1
python3 -m unittest test_shared_ingress_quota.py
```
*(All 54 automated unit tests pass in ~7 seconds)*

---

## Epistemic Boundary & Evidence Discipline

- **Local Reference Implementation:** These modules are local research and reference prototypes tested on single-host SQLite coordination. They do not constitute an audited production certification.
- **Application-Layer Boundary:** Ingress rate controls execute post-TCP accept. They regulate application-level API saturation, not upstream infrastructure or kernel SYN floods.
- **No Hosted Cloud Calls:** All test suites run locally against simulated fixtures and mock servers with zero live external network egress.

---

> **RV31 review note (Sol, 2026-10-22).** The tree above labels `cumulative_snapshots/` as
> "v4.1 through v4.9". The 45 tracked ZIPs there actually span v0.1 to v4.9
> (44 distinct version labels), so that range is inaccurate; the line is kept as written.
> Until this review, `.gitignore` dropped the 374 `.log` files that `SHA256SUMS.txt` pins, so a clean
> clone failed its own checksums. They are now unignored, and `tools/verify_research_intake.py`
> pins all 1,788 entries. README.md and SHA256SUMS.txt are outside the sums, as before.
