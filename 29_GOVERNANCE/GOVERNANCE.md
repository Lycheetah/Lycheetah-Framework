# GOVERNANCE — How Changes Happen

This document explains how decisions are made, who can make them, and how to appeal.

## The Principle

**The framework is a shared Work. Changes require care, not permission.**

We operate under three non-negotiable axioms:
- **PROTECTOR:** No changes that cause harm
- **HEALER:** No changes that hide complexity or bypass reality
- **BEACON:** No changes that reduce human agency

Everything else is open to contribution.

## Decision Makers

### **Mackenzie Conor James Clark (Mac)**
- **Authority:** Approval of changes to frameworks, constants, and core algorithms
- **Scope:** Final decision on what enters main codebase
- **Process:** Reviews evidence, considers impacts, decides
- **Appeal:** Open an issue; if you disagree with a decision, make your case publicly

### **Sol (AI System)**
- **Role:** Initial review, evidence analysis, tagging verification
- **Authority:** Can recommend but cannot approve
- **Scope:** Check claims for evidence, spot logical errors, surface conflicts
- **Limitation:** Provides analysis; Mac makes judgment calls

### **Community**
- **Role:** Testing, validation, proposing alternatives
- **Authority:** Can discuss, challenge, and refine
- **Scope:** Comment on proposals, share data, propose experiments
- **Limitation:** Cannot merge changes without Mac approval

## The Change Process

### Phase 1: Proposal (1 day)
You create a folder in `/public_building/` with:
- Clear description of what you're proposing
- Evidence or methodology
- All claims tagged with [ACTIVE]/[SCAFFOLD]/[CONJECTURE]/etc.
- Impact analysis (what changes if this is accepted?)

**Approval:** Automatic. All proposals are accepted for review.

### Phase 2: Review (3–7 days)
Sol and community provide feedback:
- Is the evidence solid?
- Are claims properly tagged?
- Does it pass the Luminous Trinity test?
- What's missing or unclear?

**Decision point:** You iterate based on feedback OR withdraw if you disagree.

### Phase 3: Approval Decision (1 day)
Mac reviews the proposal and decides:
- ✅ **APPROVED** → moves to staging (marked `[PROPOSAL]`)
- ⚠️ **NEEDS WORK** → specific requests for revision
- ❌ **REJECTED** → explanation of why + what would need to change

**If rejected:** You can appeal (see appeal process below).

### Phase 4: Staging (2–4 weeks)
Approved proposal lives in main framework but clearly marked as experimental:
```
[PROPOSAL] This extension to CASCADE is under validation.
Status: Staging (community testing)
Approval: Mac
Proposal PR: [link]
Feedback: Comment on PR
```

Community tests it. You gather real-world data. Evidence accumulates.

### Phase 5: Integration (1 day)
If staging period succeeds (evidence holds):
- Proposal mark removed
- Status updated to [ACTIVE] or [SCAFFOLD] as appropriate
- You're credited in `CONTRIBUTORS.md`
- Framework version incremented (MAJOR.MINOR if significant)

If staging period fails (evidence doesn't hold):
- Archived in `/public_building/archived/` with explanation
- Lessons noted for future work
- No shame — science means some hypotheses don't survive testing

## What Gets Approved

### ✅ Likely Approved
- Tests with real data
- Implementations of existing frameworks
- Refinements with evidence
- Honest corrections of errors
- New domains for CASCADE
- Visualization tools
- Accessibility improvements
- Mathematical proofs (conjecture → theorem)
- Disproofs (theorem → conjecture or removal)

### ⚠️ Needs Strong Evidence
- Extensions to frameworks (new operators, new phases, new constants)
- Changes to thresholds (τ_F, τ_T, etc.) — must show measured improvement
- Integration of new frameworks — must show architectural necessity
- Changes to the Luminous Trinity (nearly impossible — these are foundational)

### ❌ Will Be Rejected
- Claims without evidence
- Grandiosity without hedging ("proves" without measurement)
- Changes that hide uncertainty
- Anything violating PROTECTOR, HEALER, or BEACON
- Unauthorized framework absorption

## Appeal Process

**If your proposal is rejected:**

1. **Understand the reason** — Read Mac's explanation
2. **Address it one of two ways:**
   - **Gather more evidence** → Resubmit with new data
   - **Challenge the reasoning** → Open an issue with your counterargument
3. **Community weighs in** — Others can support or refute your challenge
4. **Mac reconsiders** — Final decision (can change mind with new evidence)

**You have the right to appeal.** The decision-maker has the right to say no — but they must explain why and must reconsider with new evidence.

**Example appeal:**

```
ORIGINAL: Rejected because "CASCADE hasn't been validated in psychology"

YOU GATHER: 20 knowledge updates from psychology domain, run CASCADE, get Π-predicted vs actual reorganization

RESUBMIT: "New data: CASCADE predicts psychology paradigm shifts with 95% accuracy"

RESULT: Approved or reconsidered (not automatically, but with new information)
```

## Dispute Resolution

**If you disagree with Mac's decision:**

1. **Comment on the decision** — Explain your reasoning publicly
2. **Provide new evidence** — Data that changes the calculus
3. **Mac reconsiders** — Or explains why the evidence doesn't change anything
4. **Final decision** — Mac's call, explained

**There's no voting system.** This isn't a democracy. It's a **meritocracy** — better evidence wins. But evidence is judged by someone with skin in the game (Mac), not by a voting system that creates political incentives.

## Maintenance & Stability

### Backwards Compatibility
- Core APIs should not break
- If frameworks need breaking changes: major version bump + migration guide
- Old versions remain available

### Deprecation
- If something is replaced: keep old version for 2 releases with deprecation warning
- Users get clear migration path

### Security
- If security issues are found: immediate fix + security advisory
- Testing goes public only after fix is deployed

## Transparency

- All decisions are explained publicly
- Rejected proposals are archived with reasoning
- Change history is Git history (traceable)
- Budget and resource decisions are visible

## The Bottom Line

**This governance structure exists to:**
- Protect the Work from degradation (PROTECTOR)
- Ensure honesty and clarity (HEALER)
- Preserve human agency and community contribution (BEACON)

**It's NOT about:**
- Mac having absolute power (he doesn't; changes are transparent and appealable)
- Keeping others out (everyone can propose; judgment is based on evidence)
- Preventing challenge (dissent is welcome; new evidence is always considered)

## Questions?

Open an issue or contact Mac directly.

The Gold belongs to neither of us.
It arises between us.

---

*In veritas.*
