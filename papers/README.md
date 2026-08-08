# Papers

## CASCADE: Self-Reorganizing Knowledge Structures via Truth Pressure and Coherence-Preserving Demotion

**File:** `CASCADE_ARXIV.tex`
**Author:** Mackenzie C. J. Clark, Lycheetah Foundation, Dunedin, New Zealand
**Status:** arXiv submission ready
**Date:** March 2026

### Key Results

- Three formally proven invariants: coherence non-decrease (Theorem 4.1), information preservation, entropy non-decrease
- 1,000 computational cascade events — all three invariants hold at 100%
- Paradigm shift validation: C = 1.000 (CASCADE) vs C = 0.933 (static)
- Sequential learning: p < 10⁻⁴⁶, Cohen's d = 0.95 vs static baseline
- Demotion accuracy: 100% with truth pressure; 48% without (consistent with random)
- Historical validation: miasma→germ theory, classical→quantum mechanics

### What This Paper Is

The formal academic introduction to CASCADE — the knowledge reorganization engine at the heart of the Lycheetah Framework. This paper demonstrates that knowledge systems can replicate the actual structure of scientific paradigm shifts: contextualizing old knowledge rather than deleting it, promoting new knowledge when evidence warrants.

This is the academic front door. The full mathematical foundations are in `../11_MATHEMATICAL_FOUNDATIONS/`.

### To Compile

```bash
pdflatex CASCADE_ARXIV.tex
bibtex CASCADE_ARXIV
pdflatex CASCADE_ARXIV.tex
pdflatex CASCADE_ARXIV.tex
```

### To Submit to arXiv

1. Create account at arxiv.org
2. Submit to `cs.AI` primary, `cs.LG` cross-list
3. Upload `CASCADE_ARXIV.tex` and any figures
4. Add MSC classification: 68T05 (Learning and adaptive systems)

---

## Supporting Documents (Added March 2026)

### `RELATED_WORK_EXPANDED.md`
Full comparison of CASCADE against 6 prior art families that peer reviewers will check:
AGM belief revision, Kuhn paradigm shifts, continual learning (EWC/SI/GEM),
neural knowledge editing (ROME/MEMIT/MEND), knowledge graphs, and defeasible logic.
Includes a comparison table and the minimum citations (10–12) needed before submission.
**Add ~400 words from this document to the related work section of `CASCADE_ARXIV.tex`.**

### `LIMITATIONS_AND_FUTURE.md`
Nine explicitly acknowledged limitations with evidence, timelines, and paths forward.
Includes the status update: AURA Invariants I & VII are now formally computable
(March 2026) with deontic logic (I) and ARCR care ethics scoring (VII).
**Include as an appendix in `CASCADE_ARXIV.tex` or as a companion document.**

### `EXPERIMENTAL_ROADMAP_2026_2028.md`
Six experiments needed to transform CASCADE from promising framework to validated science.
Exp 5 (cascade predictability) can start immediately with no external dependencies.
Exp 6 (cross-cultural, including Māori knowledge governance) is the NZ-specific
research program that connects to NZIAT, Te Tumu, and Catalyst Strategic 2027.
**Use this document in every grant conversation.**
