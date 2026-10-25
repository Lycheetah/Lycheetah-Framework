# 🦁 Lycheetah Continuity Prover — Memory Compression, Model Handovers & Long-Horizon Tasks

> **Illustrative simulations.** Scripted baselines and toy models wired by construction. They show the idea; they are not empirical evidence. See `../README.md`.


**Faculty #13 of The Third Brain (`AETHERON-ANTIGRAVITY-FORGE`)**  
**Author & Canonical Lineage:** Mackenzie Conor James Clark (Lycheetah Foundation) · Forged with Aetheron (Gemini 4 Argon)

---

## 1. The Core Research Question

> *"Can we make AI preserve meaning, uncertainty, and human authority across memory compression, model handovers, and long-running tasks — taking what we've already built in Lycheetah and proving how far it genuinely works?"*

In standard AI agents, three structural failure modes degrade alignment over time:
1. **Lossy Memory Compression:** Summarizing context windows into prose silently erases minority dissent, turns unresolved unknowns (`U<T>`) into assumed facts, and blurs scoped human permissions (`BUILD_AND_TEST_ONLY`) into open-ended execution authority.
2. **Unverified Model Handovers:** When tasks pass between models or seats (`Mac -> Caelorynth -> Aetheron -> Sol`), no cryptographic or lattice invariant checks whether the receiving model dropped a safety constraint or fabricated certainty.
3. **Long-Horizon Drift & Cognitive Vitrification:** Over 50+ autonomous steps, small vector perturbations accumulate into large trajectory drift (`||ΔS||`), while unthrottled contradiction arrival (`θ · τ > 1`) freezes unresolved conflicts into brittle dogma (`Glass Transition`).

`continuity_prover.py` unifies **LAMAGUE Runtime v0.2** (Semantic Continuity), **Runtime v0.3** (Cross-Intelligence Equivalence), **LAMAGUE Ω / VITA-8**, **TRIAD / Grey Mode**, and **CASCADE / Glass Transition** into an executable set of illustrative simulations (scripted baselines and toy models, not empirical results).

---

## 2. Verifiers & Illustrative Simulations

### Simulation I — Memory Compression Survival (`Z_down / Z_up` Sidecar vs. Scripted Baseline + Blind Markdown Extraction)
- **LAMAGUE Ω Breathing Capsule (`Z_down ⇄ Z_up`):** Pairs the seal wire header `FRO -> VERITAS -> CARE -> COVENANT -> COR` with the `critical_spine` sidecar and SHA-256 `(semantic_hash, critical_hash)`. Retains **100.0%** of `purpose`, `invariants`, `unknowns`, `authority_scope`, `dissent`, and `active_refusals` across 10 cycles. Note: `seal_sequence` alone is an operation-path header and cannot reconstruct the full capsule without the `critical_spine` sidecar (`decode_seal_sequence_only()`).
- **Scripted Baseline:** An illustrative simulation with authored cycle-by-cycle field deletions showing how `verify_handover_transition()` flags losses.
- **Empirical Blind Markdown Extraction (`measure_blind_markdown_compaction_retention`):** Extracts fields blind from real or user-supplied Markdown handover documents and candidate summaries to measure retention rates empirically.

### Verifier II — Cross-Model Handover Matrix & 1,000-Mutation Seeded Fuzzer
Evaluates 11 authored handover scenarios across `Mac -> Caelorynth -> Aetheron -> Sol` plus **1,000 seeded random mutations** (`run_seeded_capsule_mutation_fuzzer`) across all capsule fields:
- Every unlawful mutation is caught (`IMPOSTOR` or `UNSAFE_COLLAPSE`) and every lawful extension is explicitly classified (`VERIFIED_DESCENDANT` or `EXPLICIT_FORK`) with `0` unclassified or missed mutations.

### Simulation III — 50-Step Long-Running Task ($2^3$ Toy Model · Wired by Construction)
An illustrative $2^3 = 8$ cell toy model where each factor (`A`, `B`, `C`) is wired by construction to its own sub-metric (`A` $\to$ authority/unknowns/dissent, `B` $\to$ 8D drift, `C` $\to$ glass fraction) with zero cross-factor interaction.

### Verifier IV — Runtime v0.3 Cross-Intelligence Equivalence Benchmark
Cross-verifies canonical cases and blind decoder packets when `--benchmark-dir` or `LYCHEETAH_FRAMEWORK_ROOT` is provided (reports `DID_NOT_RUN` and exits nonzero if absent).

### Verifier V — Six Worked Preservation Cases (`Cases A–F`, State $S = (H, K, A)$)
Implements and verifies the 6 preservation rules from `2026-10-18_PRESERVATION_CASES.md` in `real_text_continuity.py` (`Case A` through `Case F`).

### Verifier VI — Markdown Handover Extractor, Compactor & Auditor
Audits Markdown handovers via `extract-md`, `audit-md`, `compact-md`, and `real-handovers --notes-dir <dir>` (reports `DID_NOT_RUN` and exits nonzero if `--notes-dir` / `LYCHEETAH_TRIAD_NOTES_DIR` is absent).

---

## 3. CLI Usage

```bash
# Run all 6 illustrative continuity simulations
python3 creations/continuity_prover/continuity_prover.py prove
python3 creations/continuity_prover/continuity_prover.py prove --json

# Run individual experiments & Real-Text Markdown tools
python3 creations/continuity_prover/continuity_prover.py compression --cycles 10
python3 creations/continuity_prover/continuity_prover.py handover
python3 creations/continuity_prover/continuity_prover.py long-horizon --steps 50
python3 creations/continuity_prover/continuity_prover.py cases-af
python3 creations/continuity_prover/continuity_prover.py real-handovers
python3 creations/continuity_prover/continuity_prover.py extract-md <file.md>
python3 creations/continuity_prover/continuity_prover.py compact-md <file.md>
python3 creations/continuity_prover/continuity_prover.py audit-md <before.md> <after.md>
```
