# EVIDENCE PATH AUDIT — `28_DEFENSE/CLAIMS.json`

**MEASURED 2026-08-05 by Sol.** 67 claim records, 91 evidence-path references, each
resolved from the repository root.

> ⚠ **A report of "three unrelated missing evidence paths" does not survive measurement.**
> **37 of 67 claims carry at least one evidence path that does not resolve, and 28 of those
> are status ACTIVE, EMPIRICAL or OBSERVATIONAL** — the tiers `README.md` sells publicly as
> *"proven, computable, independently verifiable."*

## What the 91 references actually do

| state | refs | meaning |
|---|---:|---|
| **resolve** | 53 | the cited file exists |
| **ABSENT** | 23 | nothing of that name exists anywhere in the repo |
| **framework mismatch** | 8 | a same-named file exists, but under a *different framework* |
| **ambiguous** | 6 | two candidates; a human must choose |
| **repaired** | 1 | unique target, safe, applied |

## ⭐ The finding — a whole document class was never written

Six framework theorem documents are cited by ACTIVE claims and **do not exist anywhere**:

`CASCADE_THEOREMS.md` · `AURA_THEOREMS.md` · `LAMAGUE_THEOREMS.md` ·
`TRIAD_THEOREMS.md` · `MICROORCIM_THEOREMS.md` · `CHRYSOPOEIA_THEOREMS.md`

Plus `07_ANAMNESIS_L0/TC_CATALOG.md` (cited by 3 **EMPIRICAL** claims) and
`01_CASCADE_L4/implementations/` (cited by 3 **ACTIVE** claims).

**This is not a broken-pointer problem. The evidence was planned, never produced, and the
claims were promoted anyway.** A pointer repair cannot fix it and must not pretend to.

## ⛔ The trap that nearly got applied

Eight claims across LAMAGUE, CHRYSOPOEIA and HARMONIA cite `<framework>/essentials.md`.
A basename search "resolves" every one of them to **`01_CASCADE_L4/essentials.md`** — a
*different framework's* document. An automated repair keyed on filename would have silently
attached eight claims to evidence about another subject, and afterwards **every path would
resolve and the register would look clean.**

⭐⭐⭐ **A REPAIR THAT MAKES THE CHECK GO GREEN IS NOT THE SAME AS A REPAIR THAT MAKES THE
CLAIM TRUE.** The repair pass therefore refuses any candidate whose leading `NN_FRAMEWORK`
segment differs from the original's.

⚠ The same discipline caught an earlier draft of this very audit: a first pass reported
**46** unresolved paths because it read semicolon-separated lists as single paths. Both
"3" and "46" were produced by instruments nobody had checked.

## What was changed, and what was not

- ✅ **One pointer repaired.** `LAM-005` → `docs/LAMAGUE_CROSS_CULTURAL_PAPER.md` — unique
  target, same document, applied as a **one-line** text edit.
  ⚠ An automated rewrite of the whole file was attempted first and **reformatted 1,290
  lines**; it was reverted to HEAD before the surgical edit landed. A defense-critical
  registry is not worth reformatting for one repair.
- ⛔ **Nothing was demoted.** Per `28_DEFENSE/EVIDENCE_LADDER.md` an ABSENT evidence path
  means the claim should drop status — but **demoting Mac's research claims is Mac's
  judgement, not Sol's.** This list is the decision surface, not the decision.

## Mac's call — two honest routes, per claim

1. **Write the missing document.** The claim keeps its status once the evidence exists.
2. **Demote the claim** to SCAFFOLD or CONJECTURE until it does.

⛔ There is no third route. Repointing an ABSENT path at a plausible neighbour is exactly
the false certainty this folder was built to prevent.

## Ambiguous — 6 references, one human decision each

| claims | status | path | note |
|---|---|---|---|
| `CAS-002` `CAS-008` `LYV-001` `LYV-002` | SCAFFOLD · ASPIRATIONAL · ACTIVE · ACTIVE | `MATHEMATICS_FOUNDATIONS.md` | 2 candidates; `11_MATHEMATICAL_FOUNDATIONS/` holds one |
| `CAS-007` `XFW-001` | SCAFFOLD | `10_INTEGRATIONS/SYSTEM_INTEGRATION_GUIDE.md` | 2 candidates; `08_INTEGRATIONS/` exists — the folder appears renumbered |

## Reproduce

The audit walks `28_DEFENSE/CLAIMS.json`, splits `evidence_path` on `;` and `,`, resolves
each part from the repo root, and classifies a miss as ABSENT, framework-mismatch or
ambiguous by indexing every basename in the tree. **Re-run before trusting this file** —
it has been wrong twice already.
