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
