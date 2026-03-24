# LYCHEETAH FRAMEWORK — WEB FRONTEND
## Navigation Interface for the Codex
### Architecture Plan | March 2026

> **Status:** [SCAFFOLD — architecture specified, build pending]
> **What this is:** A web application that makes the entire framework
> navigable, searchable, and readable — without needing to know GitHub.

---

## THE PROBLEM

The framework lives on GitHub as 80+ markdown files across 20+ folders.
This works for developers. It doesn't work for:
- Policy people who need one standard
- Community members exploring the Mystery School
- Iwi governance experts evaluating the NZ proposals
- Researchers looking for specific mathematical claims
- Someone at 3am who needs THE_THRESHOLD

A frontend solves this. One URL. Every document. Multiple reading paths.

---

## WHAT IT DOES

### 1. Reading Paths (Guided Navigation)

The landing page offers five doors — not a file list:

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│   THE LYCHEETAH FRAMEWORK                               │
│   Nine frameworks. One architecture. Open. Testable.    │
│                                                         │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│   │ I NEED   │  │ I WANT   │  │ I WANT   │            │
│   │ HELP     │  │ TO BUILD │  │ TO KNOW  │            │
│   │          │  │          │  │          │            │
│   │ Crisis   │  │ NZ Gov   │  │ The Nine │            │
│   │ support  │  │ standards│  │ frameworks│            │
│   │ & ground │  │ & tools  │  │ & maths  │            │
│   └──────────┘  └──────────┘  └──────────┘            │
│                                                         │
│   ┌──────────┐  ┌──────────┐                           │
│   │ I WANT   │  │ I WANT   │                           │
│   │ TO TEST  │  │ TO USE   │                           │
│   │          │  │          │                           │
│   │ Audit,   │  │ Code,    │                           │
│   │ failures,│  │ agents,  │                           │
│   │ proofs   │  │ deploy   │                           │
│   └──────────┘  └──────────┘                           │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

Each door leads to a curated reading path — not a dump of files.

### 2. Document Viewer

Every markdown file rendered beautifully:
- LaTeX equations rendered (KaTeX)
- Mermaid diagrams rendered
- Table of contents auto-generated
- Claim status tags ([ACTIVE], [SCAFFOLD], [CONJECTURE]) colour-coded
- Cross-references between documents are clickable links
- Dark mode default (the framework runs at night too)

### 3. Search

Full-text search across every document:
- Search by keyword, framework name, concept
- Filter by claim status ([ACTIVE] only, [CONJECTURE] included, etc.)
- Filter by folder (NZ Governance, Mathematics, Mystery School, etc.)
- Results show context around the match

### 4. Framework Map (Interactive)

Visual representation of how the nine frameworks connect:
```
                    CASCADE
                   /       \
              AURA  ———————  LAMAGUE
             / |  \         / |
        TRIAD  |   ANAMNESIS  |
           \   |   /          |
         MICROORCIM    CHRYSOPOEIA
              \         /
            EARNED LIGHT
                 |
             HARMONIA
```
Click any node → opens that framework's primary document.
Lines show mathematical relationships between frameworks.

### 5. Failure Museum (Live)

Dedicated page for the Failure Museum — front and centre:
- Every exhibit displayed as a card
- Severity colour-coded
- Timeline view showing when failures were discovered
- "This framework records its own failures publicly. Here they are."

### 6. NZ AI Standards Hub

Dedicated section for the four accountability standards:
- Each standard as its own page with full specification
- "How to adopt" section for each
- Download as PDF for printing/sharing
- Comparison table showing how they stack

---

## TECHNICAL ARCHITECTURE

### Option A: Static Site (Recommended for MVP)

```
Technology:   Next.js (Static Export) or Astro
Hosting:      GitHub Pages (free) or Vercel (free tier)
Content:      Markdown files pulled directly from the repository
Rendering:    MDX with KaTeX + Mermaid plugins
Search:       Pagefind (static search, zero server cost)
Build:        Automatic on push via GitHub Actions

Cost:         $0/month (GitHub Pages) or $0/month (Vercel free)
Build time:   2-4 weeks for MVP
Maintenance:  Push to GitHub → site rebuilds automatically
```

**Why this is the right choice:**
- No server to maintain. No database. No hosting costs.
- Content stays in the Git repo — single source of truth
- Every push automatically rebuilds the site
- Works offline if cached
- Fast globally (CDN-distributed static files)

### Option B: Dynamic Site (If interactive features needed later)

```
Technology:   Next.js (App Router) + Tailwind CSS
Backend:      Edge functions (Vercel) or Cloudflare Workers
Database:     None initially; Supabase if user accounts needed
Auth:         None initially; GitHub OAuth if contribution system added
Search:       Full-text search via Orama (in-browser) or Meilisearch

Cost:         $0-20/month depending on traffic
Build time:   4-8 weeks
```

### Recommended: Start with Option A, add dynamic features as needed.

---

## FILE STRUCTURE

```
lycheetah-web/
├── src/
│   ├── pages/
│   │   ├── index.astro           — Landing page with five doors
│   │   ├── reading/[...path].astro — Reading path renderer
│   │   ├── document/[...slug].astro — Individual document viewer
│   │   ├── search.astro          — Search page
│   │   ├── map.astro             — Interactive framework map
│   │   ├── failures.astro        — Failure Museum
│   │   └── nz/
│   │       ├── index.astro       — NZ Standards hub
│   │       ├── wof.astro         — Community AI WOF
│   │       ├── three-worlds.astro — Three Worlds Standard
│   │       ├── whakapapa.astro   — Whakapapa Disclosure
│   │       └── matariki.astro    — Matariki Audit
│   ├── components/
│   │   ├── DocumentRenderer.astro — Markdown → HTML with LaTeX + Mermaid
│   │   ├── ClaimTag.astro        — [ACTIVE]/[SCAFFOLD]/[CONJECTURE] badges
│   │   ├── FrameworkMap.astro    — D3.js or vis.js interactive graph
│   │   ├── SearchBox.astro       — Pagefind search integration
│   │   └── ReadingPath.astro     — Guided navigation component
│   ├── content/
│   │   └── (symlink or copy of CODEX_AURA_PRIME markdown files)
│   └── styles/
│       └── global.css            — Dark mode, typography, framework colours
├── public/
│   └── (static assets)
├── astro.config.mjs
├── package.json
└── README.md
```

---

## READING PATHS (CONTENT DESIGN)

### Path 1: "I Need Help"
```
THE_THRESHOLD.md → THE_FIRST_MAP.md → WHERE_AM_I.md →
SEVEN_PHASES_LIVED_GUIDE.md → (phase-specific protocol)
```

### Path 2: "I Want to Build" (NZ Governance)
```
23_NZ_AI_GOVERNANCE/README.md → COMMUNITY_AI_WOF.md →
THREE_WORLDS_DISCLOSURE_STANDARD.md → WHAKAPAPA_DISCLOSURE_STANDARD.md →
MATARIKI_AUDIT_STANDARD.md → (choose: Ancestor Vote / Moana AI / Mātauranga Probe)
```

### Path 3: "I Want to Know" (The Frameworks)
```
00_Sovereign_Index.md → CASCADE_COMPLETE.md → AURA_COMPLETE.md →
MATHEMATICS_TO_REALITY_BRIDGE.md → (choose framework to go deep)
```

### Path 4: "I Want to Test" (Skeptic Path)
```
MATHEMATICS_AUDIT.md → FAILURE_MUSEUM.md →
MATHEMATICS_REALITY_ALIGNMENT.md → NZ_COUNTER_ARGUMENTS.md →
(enter Nigredo Research Mode — question everything)
```

### Path 5: "I Want to Use" (Developer Path)
```
AI_INTEGRATION_MODULE.md → AGENTS.md → agent-init.py →
12_IMPLEMENTATIONS/core/ → (choose: CASCADE engine / LAMAGUE parser / TRIAD tracker)
```

---

## DESIGN PRINCIPLES

1. **The person at 3am gets there in one click.** THE_THRESHOLD is never more than one navigation action away from any page.

2. **Claim status is always visible.** Every document header shows [ACTIVE], [SCAFFOLD], or [CONJECTURE]. No one reads a conjecture thinking it's proven.

3. **The Failure Museum is prominent.** Not hidden. Not a footnote. Linked from the landing page. The framework's honesty is its credibility.

4. **Dark mode default.** The work happens at night. The design respects that.

5. **No login required.** Everything is public. Everything is readable. No account needed to access any content.

6. **Mobile-first.** Someone reads this on their phone at 3am. It must work.

7. **Fast.** Static site. CDN-distributed. No spinners. No loading screens. The content appears.

---

## BUILD PATHWAY

```
Week 1:  Astro project setup, GitHub Pages deployment pipeline
         Landing page with five doors
         Document renderer (markdown → HTML with LaTeX/Mermaid)

Week 2:  Reading paths implemented
         NZ Standards hub
         Search (Pagefind integration)
         Failure Museum page

Week 3:  Interactive framework map (D3.js)
         Cross-reference linking between documents
         Mobile responsiveness
         Claim status colour coding

Week 4:  Polish, testing, launch
         Custom domain (lycheetah.org or similar)
         Analytics (privacy-respecting — Plausible or similar)
         SEO basics (meta tags, Open Graph)
```

**Total build time:** 4 weeks for a complete, polished static site.
**Total cost:** $0/month hosting (GitHub Pages) + $10-15/year domain.

---

## WHY THIS MATTERS

The framework is 80+ documents. Without a frontend, the only people
who can navigate it are developers who already know GitHub.

With a frontend:
- A minister's advisor can read the AI WOF standard in 5 minutes
- An iwi governance expert can evaluate the LAMAGUE proposals
- A researcher can find every [CONJECTURE] tag and test them
- A person in crisis finds THE_THRESHOLD immediately
- A skeptic sees the Failure Museum on the front page

**The framework's value is proportional to the number of people
who can access it.** Right now, that number is limited by GitHub literacy.
A frontend removes that barrier entirely.

---

*The framework deserves a front door.*
*Not everyone enters through a terminal.*

**∅ → AURA → Aotearoa → ∞**
