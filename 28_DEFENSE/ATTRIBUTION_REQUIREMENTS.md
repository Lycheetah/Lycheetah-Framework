# D-1.0 | 2026-04-26 | Status: Active

# Attribution Requirements

*How to use, extend, and build on the Lycheetah Framework correctly.*

*Defends: C-1.0 | Closes threats: T-04, T-05, T-08*

---

## License

> **RV34 review note (Sol, 2026-10-22). Footing: [MEASURED] for the records, [DERIVED] for the licence
> reading, which is not legal advice.**
>
> - **What MIT requires.** Only that the copyright and permission notice be kept in copies of the
>   Software. The "minimum required attribution" for papers and products, and the bar on relabelling
>   the symbolic architecture, are the author's standards and scholarly norms, not MIT conditions.
> - **Ideas are not licensed.** MIT is a copyright licence on this code and text. It does not cover
>   ideas or mathematical results, so "standard academic plagiarism covered by the MIT license" below
>   is not accurate. Plagiarism is answered by scholarly norms and by the timestamped record.
> - **The record is further along than this page says.** The Zenodo DOI was minted on 2026-05-04:
>   10.5281/zenodo.20020828 (`v1.0.0-c1.1`), with a later version 10.5281/zenodo.21122441
>   (`tianxia-v0.2`, 2026-07-02), both under the concept DOI 10.5281/zenodo.20020827, and both
>   licensed MIT on Zenodo. No arXiv preprint exists (0 results from the arXiv API).
> - **Not everything here is MIT.** Four subtrees carry Apache-2.0: the retired LAMAGUE kernel v0.8
>   (`03_LAMAGUE_L1/13_RETIRED_KERNEL_BRANCH/...v0.8...`) and `papers/agent-safety/earned-light/
>   forges_01_07/Forge_05`, `Forge_06` and `Forge_07`, whose copyright line reads "Lycheetah research
>   collaborators". Both licences are permissive and compatible; each subtree keeps its own file.
> - **Conflict.** `CONTRIBUTING.md` and ten source headers name an "Earned Sovereignty Clause" whose
>   text exists nowhere. Mac's options are in `FOR-REVIEW/2026-10-22_OPUS_REVIEW/BATCH33_FINDINGS_AND_LEDGER.md`.

The Lycheetah Framework is released under the **MIT License**.

You can: use it, copy it, modify it, distribute it, sublicense it, use it commercially. You must: include the original license and copyright notice.

Full license: `LICENSE` file in the repository root.

---

## Attribution Standards

The MIT license requires attribution. These are the standards for how that attribution should be expressed.

### Minimum Required Attribution

Any use of the framework — in code, research, products, or publications — requires:

```
Lycheetah Framework by Mackenzie Conor James Clark
https://github.com/Lycheetah/Lycheetah-Framework
MIT License
```

This minimum applies to: software that imports or uses the implementations, papers that build on the formal results, products that use the framework's methods.

### Academic Attribution

Papers citing this work should use the BibTeX entries in `28_DEFENSE/CITATIONS.md`. The preferred citation is the canonical body (`clark2026codex`). If citing a specific framework (CASCADE, AURA, etc.), cite the framework-specific entry.

Do not cite as "anonymous" or under an institutional name without the author's name. The work is attributed to Mackenzie Conor James Clark.

### Attribution for Derived Works

If you build a derived framework — one that extends, modifies, or builds on the Lycheetah Framework — the attribution must:

1. Name the Lycheetah Framework as the source.
2. Specify which components were used or extended.
3. Not imply that the derived work is the original or endorsed by the author.

**Example:** "This framework extends the AURA constitutional invariants from the Lycheetah Framework (Clark, 2026) with three additional invariants for medical contexts."

### Attribution for the Symbolic Architecture

The alchemical vocabulary used in this framework — the Sol Protocol operating architecture, the Two-Point Protocol, the PGF filter (P∧H∧B), the four operating modes (Nigredo/Albedo/Citrinitas/Rubedo) — is part of the framework's symbolic architecture. It is covered by the MIT license in the same way as the formal mathematical content.

If you use the symbolic architecture (e.g., implement the Sol Protocol or the EWM interval table in a product), attribution follows the same standard as above.

The symbolic architecture may not be relabeled and presented as a distinct original work without attribution to its source. "Relabeling" means adopting the structural design (e.g., the four operating modes, the Two-Point Protocol, the three-generator filter) under different names while omitting attribution to this framework.

---

## What "Capture" Looks Like and Why It Matters

The attribution requirements exist because capture is a real risk.

**Capture without attribution** means: taking the mathematical results (Theorem C3, the AURA invariants, the TRIAD convergence proof) and presenting them in a new paper or product without citing the source. This is standard academic plagiarism covered by the MIT license.

**Capture by absorption** means: a larger institution or framework incorporates the Lycheetah Framework's architecture — the nine-framework structure, the master equation, the constitutional invariants — into its own system without attribution, effectively erasing the provenance. This is prevented by the timestamped public record (GitHub commits, Zenodo DOI when minted, arXiv preprint when submitted) and by this document's existence.

The defense against both is: the public record is prior and timestamped. Anyone claiming independent discovery of these specific formal structures after 2026-04-25 faces a provenance question that this record answers.

---

## What You Can Do Without Attribution

The general ideas in this framework — that AI should have constitutional constraints, that belief revision should be coherent, that multi-agent systems need drift detection — are not proprietary. You can:

- Build on these ideas without attribution if you develop them independently and differently.
- Write papers that cite the same prior art without citing this framework, if your development path was genuinely independent.
- Implement your own constitutional invariants without using the AURA framework.

Attribution is required when you use the specific formal structures, implementations, or symbolic architecture from this repository. The test: if you cloned the repo and built from it, attribute. If you read the ideas and built independently from scratch, the MIT license does not require attribution (though academic norms may).

---

## Tikanga Maori Content

The Tikanga Maori epistemological content in this framework is labeled [PROPOSAL] — it is proposed integration, not claimed formalized Maori knowledge. It has not been validated by iwi partnership as of C-1.0.

Derived works that use the Tikanga Maori content:
1. Must preserve the [PROPOSAL] label — do not present it as validated Maori knowledge.
2. Must attribute the source (this framework) and the caveat.
3. Are encouraged to pursue iwi validation independently and share results back to the canonical body via the Living Codex Protocol.

---

## Questions

For attribution questions, contact: banduabusiness@gmail.com

For framework governance and contribution: see `CONTRIBUTING.md` and `29_GOVERNANCE/LIVING_CODEX_PROTOCOL.md`.

---

*This document is part of Codex Defense Protocol D-1.0, defending canonical body C-1.0 (2026-04-25).*
