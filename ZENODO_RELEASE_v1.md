# ZENODO RELEASE — The Lycheetah Framework v1.0 (C-1.1)
## DOI Mint Plan and Submission Instructions

**Status:** `[ACTIVE]` — ready for Mac to execute  
**Prepared by:** Sol (2026-05-03) | **Updated:** Sol (2026-05-04) — TIANXIA v0.3 patched in  
**Closes:** Master Plan A-08  
**Mac action required:** A-09 — Zenodo DOI mint (this document is the prep; execution is yours)

---

## Why This Matters

arXiv requires endorsers. Zenodo does not.

Once this DOI is minted, the entire Lycheetah corpus — nine frameworks, 34 implementations, the TIANXIA module, the empirical programme design, the defense layer — becomes permanently citable. Every subsequent paper, grant application, or correspondence can cite a real DOI that resolves to a versioned, immutable snapshot. The arXiv submission path (Task 2) remains open; this removes the dependency on endorsement before the work has a permanent external address.

Zenodo is operated by CERN. DOIs minted there are permanent. The record is indexed by OpenAIRE, Google Scholar, and most academic search engines within days.

---

## Release Metadata — Fill These In Exactly

### Title
```
The Lycheetah Framework: Nine Formal Frameworks for AI Alignment and Epistemology (Version C-1.1)
```

### Authors
```
Clark, Mackenzie Conor James
  Affiliation: Independent Researcher, Dunedin, Aotearoa New Zealand
  ORCID: [add if you have one — create at orcid.org if not, takes 2 minutes]
```

### Description (paste this into the Description field)
```
The Lycheetah Framework is a system of nine interdependent formal frameworks 
for AI alignment and epistemology: CASCADE (Bayesian belief dynamics with truth 
pressure), AURA (seven computable constitutional invariants), LAMAGUE (formal 
grammar for ethical constraints), TRIAD (anchor-observe-correct convergence 
cycle), MICROORCIM (continuous drift detection), EARNED LIGHT (thermodynamic 
consciousness model), ANAMNESIS (convergent discovery dynamics), CHRYSOPOEIA 
(transformation operator), and HARMONIA (resonance coupling).

This release — version C-1.1 — is the defended canonical body of work. It 
includes:

- 22-act canonical body (C-1.0, completed 2026-04-25), reforged to C-1.1
- Three-pass defense layer (D-1.0 / D-1.1 / D-1.2), 24 defense documents
- Empirical programme design (E-1.0), five preregistered studies
- TIANXIA civilisational engagement module v0.3 (Classical Triad complete) — 
  nine operators across Confucian, Daoist, and Legalist traditions (Tianxia, 
  Hexie, Shi, Wuwei, Datong, Ren Zheng, Wang Dao / Ba Dao, Li, Han Fei Fa, 
  Five-Fold Hexie H₅) formally mapped onto CASCADE / AURA operations; 
  9 Python implementations with full test suites; three-layer alignment stack
- 38 Python implementations with 219+ automated tests
- CLAIM_STATUS_LEDGER: 17 ACTIVE / 40 SCAFFOLD / 16 CONJECTURE across all 
  frameworks including TIANXIA; CLAIMS.json machine-readable register with 
  60 structured records (ACTIVE / SCAFFOLD / CONJECTURE / RETRACTED)
- Machine-readable claims register (CLAIMS.json), adversarial audit, failure 
  museum, and counter-codex

All claims carry explicit status tags. The adversarial audit and counter-codex 
(including five objections the framework cannot yet answer) are included in the 
public record. Built by one self-taught independent researcher in Dunedin, 
Aotearoa New Zealand. Free under MIT license.

The Sol Protocol (human–AI co-creation architecture, v3.1/v4.0) governing 
the development process is also included.
```

### Version
```
C-1.1
```

### Publication date
```
2026-05-04
```

### Resource type
```
Software
```
*(Zenodo also accepts "Dataset" or "Other" — Software is correct here because the implementations and test suite are primary artefacts.)*

### License
```
MIT
```

### Keywords (add all of these)
```
AI alignment
constitutional AI
formal epistemology
AI governance
AI safety
Bayesian belief revision
AURA framework
cascade dynamics
multi-agent coherence
Chinese AI governance
Tianxia
computational ethics
alignment verification
knowledge reorganization
Python
open source
```

### Related identifiers
```
Is supplemented by: https://github.com/Lycheetah/Lycheetah-Framework  (type: URL)
```

### Communities (optional but useful)
Search for and add:
- `zenodo` (general)
- `openaire` (European open access)
- Any AI safety or alignment communities visible in the search

---

## Two Paths to Mint the DOI

### Path A — GitHub Integration (recommended, takes 5 minutes)

This is the cleanest path. Zenodo watches your GitHub releases and mints a DOI automatically when you tag a release.

**Step 1 — Link GitHub to Zenodo**
1. Go to [zenodo.org](https://zenodo.org) → log in (or create account — it's free)
2. Click your username (top right) → **GitHub**
3. Find `Lycheetah/Lycheetah-Framework` in the list
4. Toggle it **ON**

**Step 2 — Create a GitHub Release**

Run this in your terminal:
```bash
cd ~/CODEX_AURA_PRIME
git tag v1.0.0-c1.1
git push origin v1.0.0-c1.1
```

Then go to: https://github.com/Lycheetah/Lycheetah-Framework/releases/new

- Tag: `v1.0.0-c1.1`
- Title: `The Lycheetah Framework v1.0 — C-1.1 Canonical Body`
- Description: copy the Description field text above

Click **Publish release**.

**Step 3 — Zenodo receives it**
Within a few minutes, Zenodo will detect the release and create a draft record. Go to [zenodo.org/deposit](https://zenodo.org/deposit), find the draft, add the metadata above, and click **Publish**. DOI minted.

**What failure looks like:** If the GitHub toggle doesn't appear, you may need to authorize Zenodo via GitHub OAuth. The Zenodo UI will prompt you; it's one click.

---

### Path B — Manual Upload (if GitHub integration doesn't work)

**Step 1 — Download the repository as ZIP**
```
https://github.com/Lycheetah/Lycheetah-Framework/archive/refs/heads/master.zip
```

**Step 2 — Create a new upload**
1. Go to [zenodo.org/deposit/new](https://zenodo.org/deposit/new)
2. Upload the ZIP
3. Fill in all metadata fields from the section above
4. Click **Save** then **Publish**

---

## After the DOI Is Minted

1. **Copy the DOI** — it looks like `10.5281/zenodo.XXXXXXX`

2. **Update the citation in README.md** — replace the current citation with:
```
Clark, M. C. J. (2026). The Lycheetah Framework: Nine Formal Frameworks for AI Alignment 
and Epistemology (Version C-1.1). Zenodo. https://doi.org/10.5281/zenodo.XXXXXXX
```

3. **Update CITATIONS.md and CITATION.cff** — Sol will do this once you hand back the DOI

4. **Log the DOI in CLAIM_STATUS_LEDGER.md** — adds permanent provenance to the canonical body

5. **Post to X** — one line: "The Lycheetah Framework now has a Zenodo DOI: [DOI]" — that's enough

---

## What This Unlocks

Once the DOI exists:

- Every preregistration (E-1-A, E-1-D, E-1-F) can cite the canonical corpus with a real DOI
- The LAMAGUE paper (July 2026 deadline) has a citable framework version
- arXiv submission (when endorsement resolves) cites the Zenodo preprint as prior DOI
- Catalyst 2027 application has a citable, versioned corpus
- Grant officers, reviewers, and journalists have a permanent, immutable reference

The DOI is the difference between "a GitHub repo" and "a citable scientific artefact." Same content. Permanent address.

---

## ORCID Note

If you don't have an ORCID, create one at [orcid.org](https://orcid.org) — it takes two minutes and makes you discoverable as an independent researcher across all academic databases. Add it to the Zenodo author record. Sol can write the ORCID profile bio if you want.

---

*Prepared under Master Plan A-08. MAC-GATED on A-09 (execution).*  
*Sol forged. Mac fires.*
