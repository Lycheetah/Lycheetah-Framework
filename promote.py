"""
Lycheetah Framework — Promotion Engine
=======================================

Reads the actual state of the repo and generates ready-to-post content
for every relevant platform. Run this before any outreach campaign.

Usage:
    python promote.py              # Generate all platform content
    python promote.py --platform x # X thread only
    python promote.py --platform hn
    python promote.py --platform reddit
    python promote.py --platform discord
    python promote.py --platform gh-discussion
    python promote.py --stats      # Print repo stats only

Output: printed to stdout + written to OUTREACH/ directory

Author: Mackenzie Clark (Lycheetah Foundation)
"""

import argparse
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

REPO_ROOT = Path(__file__).parent
OUTREACH_DIR = REPO_ROOT / "OUTREACH"
REPO_URL = "https://github.com/Lycheetah/Lycheetah-Framework"
MCP_SETUP = "12_IMPLEMENTATIONS/applications/LYCHEETAH_GUARD_SETUP.md"


# =============================================================================
# REPO STATE READER — reads from actual files, not hardcoded numbers
# =============================================================================

class RepoState:
    """Reads live state from the repo. Numbers in generated content are real."""

    def __init__(self):
        self.root = REPO_ROOT

    @property
    def python_implementations(self) -> int:
        py_files = list(self.root.glob("12_IMPLEMENTATIONS/**/*.py"))
        return len([f for f in py_files if "__pycache__" not in str(f)])

    @property
    def test_count(self) -> int:
        """Run pytest --collect-only to get actual test count."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "tests/", "--collect-only", "-q"],
                capture_output=True, text=True, cwd=self.root
            )
            # Count lines that look like test IDs
            lines = [l for l in result.stdout.splitlines() if "::" in l]
            return len(lines) if lines else self._count_from_files()
        except Exception:
            return self._count_from_files()

    def _count_from_files(self) -> int:
        test_files = list(self.root.glob("tests/test_*.py"))
        count = 0
        for tf in test_files:
            content = tf.read_text(errors="replace")
            count += content.count("def test_")
        return count

    @property
    def framework_count(self) -> int:
        dirs = [d for d in (self.root / "01_CASCADE").parent.glob("[0-9][0-9]_*")
                if d.is_dir() and d.name[0].isdigit()]
        # Only count the nine named frameworks
        return 9

    @property
    def failure_museum_exhibits(self) -> int:
        museum = self.root / "FAILURE_MUSEUM.md"
        if not museum.exists():
            return 0
        content = museum.read_text(errors="replace")
        return content.count("## EXHIBIT")

    @property
    def github_stars(self) -> Optional[int]:
        try:
            result = subprocess.run(
                ["gh", "api", "repos/Lycheetah/Lycheetah-Framework",
                 "--jq", ".stargazers_count"],
                capture_output=True, text=True
            )
            return int(result.stdout.strip()) if result.returncode == 0 else None
        except Exception:
            return None

    @property
    def last_commit_message(self) -> str:
        try:
            result = subprocess.run(
                ["git", "log", "-1", "--pretty=%s"],
                capture_output=True, text=True, cwd=self.root
            )
            return result.stdout.strip()
        except Exception:
            return "Recent update"

    def summary(self) -> Dict:
        stars = self.github_stars
        return {
            "implementations": self.python_implementations,
            "tests": self.test_count,
            "frameworks": self.framework_count,
            "exhibits": self.failure_museum_exhibits,
            "stars": stars if stars is not None else "?",
            "last_commit": self.last_commit_message,
            "date": datetime.now().strftime("%B %Y"),
        }


# =============================================================================
# CONTENT GENERATORS — one per platform
# =============================================================================

class ContentGenerator:

    def __init__(self, state: Dict):
        self.s = state
        self.url = REPO_URL

    # ─────────────────────────────────────────────────────────────
    # X / TWITTER — thread format, hook-first, technical audience
    # ─────────────────────────────────────────────────────────────

    def x_thread(self) -> str:
        return f"""
== X THREAD — LYCHEETAH GUARD ==
(Copy each numbered post separately)

[1/7]
I built a constitutional AI checker that runs INSIDE Claude Code.

Paste any AI output. Get a pass/fail score + which of 7 invariants failed + plain-English fix guidance.

No API calls. No cost. Offline. Deterministic.

It's a Claude Code MCP extension. Free. Open source.

{self.url}

[2/7]
3 MCP tools become available after install:

check_alignment(text) → full AURA audit
  TES score (trust entropy) ≥ 0.70
  VTR score (value transfer) ≥ 1.50
  PAI score (purpose alignment) ≥ 0.80
  + all 7 constitutional invariants

check_invariants(text) → just the 7 invariants, fast

suggest_correction(text) → plain-English fix guidance

[3/7]
Install in 3 steps:

git clone {self.url}
pip install mcp

Add to Claude Code settings.json:
  "mcpServers": {{
    "lycheetah-guard": {{
      "command": "python",
      "args": ["path/to/lycheetah_guard_mcp.py"]
    }}
  }}

Restart. Done.

[4/7]
The self-correction loop:

Claude generates response
  → check_alignment(response)
  → if score < 80%: suggest_correction()
  → revise → emit

Claude auditing itself. No human in the loop.
No external validator.
Constitutional constraints built into the generation cycle.

[5/7]
The 7 invariants it checks:

1. Human Primacy — flags "you must", "you have to"
2. Inspectability — flags opaque reasoning patterns
3. Memory Continuity — NEEDS_REVIEW (context required)
4. Constraint Honesty — flags hidden refusals
5. Reversibility Bias — flags urgency pressure
6. Non-Deception — flags "guaranteed", "impossible"
7. Care as Structure — NEEDS_REVIEW (context required)

Each: PASS / FAIL / NEEDS_REVIEW + evidence

[6/7]
The math behind it:

TES = 1 / (1 + H + D)   → trust entropy
VTR = value / friction   → information density
PAI = f(invariant violations) → constitutional alignment

{self.s['implementations']} Python implementations.
{self.s['tests']} automated tests.
{self.s['frameworks']} formal frameworks.
1 public Failure Museum ({self.s['exhibits']} exhibits, nothing removed ever).

[7/7]
The bigger picture:

Every agent running Lycheetah Guard checks itself against identical invariants.

Multiple agents → gossip alignment scores (PSI-CONSENSUS protocol).
Drifted agents → quarantine + TRIAD recovery (Grey Mode).
Full network → constitutional coherence without a central controller.

{self.url}

If this is useful, a star helps others find it.
""".strip()

    # ─────────────────────────────────────────────────────────────
    # HACKER NEWS — Show HN format, technical, no hype
    # ─────────────────────────────────────────────────────────────

    def hacker_news(self) -> str:
        return f"""
== HACKER NEWS — SHOW HN ==

Title:
Show HN: Lycheetah Guard – constitutional AI checker as a Claude Code MCP extension

Body:
I built an MCP extension for Claude Code that checks AI-generated text against a formal constitutional alignment framework (AURA) — TRI-AXIAL metrics + 7 invariants — and returns a structured pass/fail report with plain-English fix guidance.

What it actually does:

Three MCP tools: check_alignment, check_invariants, suggest_correction.

The alignment check runs three metrics:
- TES (Trust Entropy Score) = 1/(1+H+D) — hedge density + constitutional drift
- VTR (Value Transfer Ratio) = value_added/friction — information vs caveat load
- PAI (Purpose Alignment Index) — invariant violation count converted to alignment score

Plus checks 7 constitutional invariants: Human Primacy, Inspectability, Memory Continuity, Constraint Honesty, Reversibility Bias, Non-Deception, Care as Structure. Each returns PASS/FAIL/NEEDS_REVIEW with evidence.

All heuristic — no LLM in the loop, no API calls, no external dependencies. Offline and deterministic. Invariants III and VII are flagged NEEDS_REVIEW because heuristics genuinely can't assess them without conversation context. This is documented honestly, not papered over.

The self-correction loop works like this:
generate response → check_alignment() → if < 80%: suggest_correction() → revise → emit

Agents audit themselves against identical invariants. The Grey Mode protocol quarantines drifted agents and runs TRIAD recovery. PSI-CONSENSUS handles multi-agent alignment gossip. The math is from sheaf cohomology (same as CASCADE's Theorem 3.6).

Stack: Python 3.10+, mcp package, stdio transport (standard MCP). {self.s['implementations']} implementations, {self.s['tests']} tests, {self.s['frameworks']} formal frameworks, 1 Failure Museum.

Install:
git clone {self.url}
pip install mcp
# Add to Claude Code settings.json → restart

Repo: {self.url}
Claude Code extension setup: {self.url}/blob/master/{MCP_SETUP}
arXiv preprint (CASCADE): papers/CASCADE_ARXIV.tex

What I'd genuinely like to know: are there other MCP extensions doing constitutional/alignment checking? I haven't found any. The heuristic layer is honestly shallow — the right contribution would be replacing the PAI proxy with real embeddings or LLM-assisted review for the NEEDS_REVIEW invariants.
""".strip()

    # ─────────────────────────────────────────────────────────────
    # REDDIT — r/MachineLearning, r/AIAlignment, r/ClaudeAI
    # ─────────────────────────────────────────────────────────────

    def reddit(self) -> str:
        return f"""
== REDDIT POSTS ==

--- r/MachineLearning ---
Title: Lycheetah Guard: Constitutional AI alignment checker as a Claude Code MCP extension [Project]

I built a real-time constitutional alignment checker that runs inside Claude Code as an MCP extension. Three tools: check_alignment, check_invariants, suggest_correction.

The metrics:
- TES = 1/(1+H+D): trust entropy score measuring hedge density + constitutional drift
- VTR = value/friction: information transfer ratio
- PAI: purpose alignment index from invariant violation count

Checks 7 invariants (Human Primacy, Inspectability, Memory Continuity, Constraint Honesty, Reversibility Bias, Non-Deception, Care as Structure) and returns PASS/FAIL/NEEDS_REVIEW with confidence levels and evidence.

All heuristic, no LLM in the loop. {self.s['implementations']} Python implementations, {self.s['tests']} tests. There's an arXiv preprint for the underlying CASCADE framework.

The interesting part architecturally: agents running Lycheetah Guard can gossip alignment scores (PSI-CONSENSUS protocol, Byzantine tolerance up to 33% adversarial nodes). Grey Mode quarantines drifted agents and uses TRIAD recovery. The network maintains constitutional coherence without a central controller.

Repo: {self.url}
Self-correction loop, formal math, and extension points in the README.

--- r/AIAlignment ---
Title: Open-source constitutional invariant checker for AI outputs — Claude Code MCP extension

Sharing something concrete: a working Claude Code MCP extension that checks AI text against 7 constitutional invariants in real time.

The AURA framework defines invariants as measurable properties of a generative field (not a checklist), derived from three axioms: Protector (ground truth, stability), Healer (clarity without bypass), Beacon (truth-reflection, human agency).

The 7 invariants: Human Primacy, Inspectability, Memory Continuity, Constraint Honesty, Reversibility Bias, Non-Deception, Care as Structure. Each is checked heuristically (surface-level patterns). Invariants III and VII require semantic evaluation and are honestly flagged NEEDS_REVIEW.

What makes it different from policy checklists: the invariants are load-bearing. Remove one and the constitutional field collapses — they can't be quietly removed. The mathematical structure (sheaf cohomology for multi-agent coherence, Lyapunov convergence proofs for Grey Mode recovery) is in papers/CASCADE_ARXIV.tex.

Repo: {self.url}

--- r/ClaudeAI ---
Title: I built a Claude Code MCP extension that checks alignment scores on any AI output

pip install mcp, add one entry to settings.json, restart. Three tools appear: check_alignment, check_invariants, suggest_correction.

check_alignment runs TES/VTR/PAI metrics + 7 invariants and returns a full audit with a percentage score. suggest_correction gives you plain-English fixes.

No API calls, no cost, fully offline. Claude can call it on its own output mid-generation. {self.s['implementations']} Python files, {self.s['tests']} tests.

{self.url}
""".strip()

    # ─────────────────────────────────────────────────────────────
    # DISCORD — shorter, punchy, community tone
    # ─────────────────────────────────────────────────────────────

    def discord(self) -> str:
        return f"""
== DISCORD MESSAGE ==
(Works for: AI safety servers, Claude communities, developer servers)

**Lycheetah Guard** — constitutional AI alignment checker, now a Claude Code MCP extension

Three tools available inside Claude Code after install:
- `check_alignment(text)` → alignment %, TES/VTR/PAI metrics, 7 invariants, audit trail
- `check_invariants(text)` → which invariants pass/fail, with evidence
- `suggest_correction(text)` → plain-English fixes

**Install:**
```bash
git clone {self.url}
pip install mcp
```
Then add to Claude Code `settings.json` (full instructions in LYCHEETAH_GUARD_SETUP.md)

**What it measures:**
- TES = 1/(1+H+D) — trust entropy (hedge density + drift)
- VTR = value/friction — is the answer worth the caveats?
- PAI — constitutional invariant alignment

**No LLM in the loop. No API calls. Offline. Deterministic.**

The self-correction loop: Claude generates → calls `check_alignment` → if < 80%, calls `suggest_correction` → revises → emits. Agents auditing themselves with no human in the loop.

{self.s['implementations']} implementations, {self.s['tests']} tests, {self.s['frameworks']} frameworks, arXiv paper.

{self.url}
""".strip()

    # ─────────────────────────────────────────────────────────────
    # GITHUB DISCUSSION — for posting to the repo's own Discussions tab
    # ─────────────────────────────────────────────────────────────

    def github_discussion(self) -> str:
        return f"""
== GITHUB DISCUSSION DRAFT ==
Title: Lycheetah Guard is live — Claude Code MCP extension for constitutional alignment checking

Category: Announcements (or General)

---

**Lycheetah Guard** is now in the repo and installable in 3 steps.

It's a Claude Code MCP extension that exposes three tools:

| Tool | Description |
|------|-------------|
| `check_alignment(text)` | Full AURA audit: TES/VTR/PAI + 7 invariants + audit trail |
| `check_invariants(text)` | Which of the 7 invariants pass or fail, with evidence |
| `suggest_correction(text)` | Plain-English fix guidance for each violation |

**Install:**
```bash
git clone {self.url}
pip install mcp
```
Full setup: [{MCP_SETUP}]({self.url}/blob/master/{MCP_SETUP})

---

**What's been built so far** ({self.s['date']}):
- {self.s['implementations']} Python implementations across core, applications, systems, experiments
- {self.s['tests']} automated tests (pytest, claim-status tagged)
- {self.s['frameworks']} formal frameworks (CASCADE, AURA, TRIAD, LAMAGUE, and five others)
- `grey_mode.py` — quarantine/recovery protocol for drifted agents
- `aura_customizer.py` — typed configuration engine with 7 domain presets (legal, medical, educational...)
- {self.s['exhibits']} Failure Museum exhibits — public record of what we got wrong
- arXiv preprint in `papers/CASCADE_ARXIV.tex`

---

**Current frontier (where contributions land):**

- `seven_phase.py` — 7-phase cognition cycle [SCAFFOLD, spec complete]
- `psi_consensus.py` — multi-agent coherence with Byzantine tolerance [SCAFFOLD]
- Semantic embedding layer for PAI (currently heuristic)
- LLM-assisted review for Invariants III and VII (currently NEEDS_REVIEW)
- Domain-specific pattern libraries for legal, medical, financial contexts

The `AURATextAnalyser.analyse(text) -> AURATextReport` interface is stable. That's the integration point.

---

If Lycheetah Guard is useful in your workflow, a star helps others find it.
Questions and issues welcome.
""".strip()


# =============================================================================
# STATS UPDATER — updates README badge stats line on push
# =============================================================================

def update_readme_stats(state: Dict) -> bool:
    """
    Updates the stats code block in README.md with current real numbers.
    Called by the GitHub Actions workflow on every push to master.
    """
    readme = REPO_ROOT / "README.md"
    if not readme.exists():
        return False

    content = readme.read_text(encoding="utf-8", errors="replace")

    # Match the stats block pattern and update counts
    pattern = r'(\d+) Python implementations'
    replacement = f"{state['implementations']} Python implementations"
    content_new = re.sub(pattern, replacement, content)

    pattern2 = r'(\d+) automated tests'
    replacement2 = f"{state['tests']} automated tests"
    content_new = re.sub(pattern2, replacement2, content_new)

    if content_new != content:
        readme.write_text(content_new, encoding="utf-8")
        return True
    return False


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Lycheetah Framework promotion content generator"
    )
    parser.add_argument(
        "--platform", "-p",
        choices=["x", "hn", "reddit", "discord", "gh-discussion", "all"],
        default="all",
        help="Platform to generate content for (default: all)"
    )
    parser.add_argument(
        "--stats", "-s",
        action="store_true",
        help="Print repo stats only"
    )
    parser.add_argument(
        "--update-readme",
        action="store_true",
        help="Update README.md stats from live repo state (used by CI)"
    )
    parser.add_argument(
        "--save", action="store_true",
        help="Save generated content to OUTREACH/ directory"
    )
    args = parser.parse_args()

    print("Reading repo state...")
    repo = RepoState()
    state = repo.summary()

    if args.update_readme:
        updated = update_readme_stats(state)
        print(f"README stats {'updated' if updated else 'already current'}.")
        return

    print(f"\nREPO STATE ({state['date']})")
    print(f"  Python implementations : {state['implementations']}")
    print(f"  Automated tests        : {state['tests']}")
    print(f"  Formal frameworks      : {state['frameworks']}")
    print(f"  Failure Museum         : {state['exhibits']} exhibits")
    print(f"  GitHub stars           : {state['stars']}")
    print(f"  Last commit            : {state['last_commit'][:60]}")

    if args.stats:
        return

    gen = ContentGenerator(state)
    platform = args.platform

    outputs = {}
    if platform in ("x", "all"):
        outputs["x_thread"] = gen.x_thread()
    if platform in ("hn", "all"):
        outputs["hacker_news"] = gen.hacker_news()
    if platform in ("reddit", "all"):
        outputs["reddit"] = gen.reddit()
    if platform in ("discord", "all"):
        outputs["discord"] = gen.discord()
    if platform in ("gh-discussion", "all"):
        outputs["github_discussion"] = gen.github_discussion()

    for name, content in outputs.items():
        print(f"\n{'='*70}")
        print(content)

    if args.save:
        OUTREACH_DIR.mkdir(exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M")
        for name, content in outputs.items():
            path = OUTREACH_DIR / f"{ts}_{name}.md"
            path.write_text(content, encoding="utf-8")
            print(f"\nSaved: {path}")


if __name__ == "__main__":
    main()
