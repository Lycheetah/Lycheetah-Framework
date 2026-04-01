# PUBLIC BUILDING — The Lycheetah Framework Development Arena

Welcome. This is where the Lycheetah Framework grows in public.

## What This Folder Is

**Public Building** is the space where:
- Anyone can propose additions, tests, or refinements
- All claims are measured against ground truth
- Nothing enters the main frameworks without:
  1. **Evidence** (data, logic, or operational proof)
  2. **Classification** (ACTIVE, SCAFFOLD, FOUNDATIONAL, or CONJECTURE)
  3. **Verification** by Mackenzie Clark (Mac)

## How to Contribute

### Option 1: Propose a New Test
```
/public_building/proposed_tests/[your_test_name]/
├── README.md — what you're testing
├── hypothesis.md — what you expect
├── test_code.py — the implementation
└── results.md — what actually happened
```

**Example:** Test whether CASCADE works on real organizational knowledge updates (not just synthetic cascades)

### Option 2: Propose a New Framework Extension
```
/public_building/proposed_frameworks/[framework_name]/
├── proposal.md — what it does, why it matters
├── mathematics.md — formal definition
├── analogs.md — where this appears in nature/society
└── implementation.py — proof of concept
```

**Example:** How HARMONIA could extend to organizational rhythm (team flow states)

### Option 3: Propose a Refinement to Existing Framework
```
/public_building/proposed_refinements/[framework]_[issue]/
├── problem_statement.md — what's wrong or unclear
├── proposed_fix.md — your solution
├── evidence.md — why this fixes it
└── impact_analysis.md — what changes if this is accepted
```

**Example:** More precise definition of τ_F = 1.5 threshold in CASCADE

### Option 4: Real-World Validation Data
```
/public_building/validation_data/[domain]/
├── dataset.csv or .json — the raw data
├── measurement_protocol.md — how it was collected
├── analysis.py — analysis code
└── findings.md — what the data shows
```

**Example:** "Tracked my sovereign score daily for 90 days using MICROORCIM protocol"

## The Confirmation Workflow

1. **You submit** a pull request to `/public_building/[your_proposal]/`
2. **Review happens** in the PR discussion
   - Sol (AI) provides initial analysis
   - Community can comment
   - Evidence is evaluated
3. **Mac approves or requests changes**
   - If approved → moves to staging (NOT yet in main frameworks)
   - If changes needed → you iterate
   - If rejected → feedback explaining why
4. **Staging period** (2–4 weeks)
   - Proposal lives in framework but marked `[PROPOSAL]`
   - Community can test it
   - Real-world data confirms it
5. **Final decision** — Mac integrates into core or archives

## Claim Tagging (Required on All Contributions)

Every claim must carry one tag:

```markdown
[ACTIVE] — Testable NOW with current data. Evidence cited.
          Example: "CASCADE reorganizes knowledge via Π = (E·P)/S"

[SCAFFOLD] — Real structure, parameters TBD. Architecture sound.
             Example: "Master equation dΨ/dt = k₁(...) − k₂(...) (k-values under calibration)"

[FOUNDATIONAL] — Architecturally necessary, not independently testable.
                 Example: "Seven Invariants as fundamental constraints"

[CONJECTURE] — Promising hypothesis awaiting evidence.
               Example: "Consciousness may follow Boltzmann thermodynamics (EARNED_LIGHT hypothesis)"

[ANALOGY] — Structural parallel, not proven identity.
            Example: "CASCADE dynamics resemble Morse theory (analogy, not theorem)"

[LIVED] — Phenomenological claim, true in first-person experience.
          Example: "Nigredo feels like dissolution" (framework-user testimony)
```

## What We DON'T Accept

- ❌ Claims without evidence or honest uncertainty
- ❌ Absolute language (always, proves, guarantees) for unsupported claims
- ❌ Superlatives (first, only, best) without proof
- ❌ Hidden complexity (unclear how something works)
- ❌ Any claim that contradicts the Luminous Trinity
  - PROTECTOR: no harm
  - HEALER: honest clarity
  - BEACON: humans stay in control

## Examples of GOOD Proposals

### ✅ "Test CASCADE on real knowledge updates"
```
[ACTIVE] Testing
Hypothesis: CASCADE algorithm predicts knowledge reorganization in real organizations
Method: Collect 20 knowledge updates from [company], measure Π before/after
Evidence: If [result], CASCADE's truth pressure formula works; if [result], needs adjustment
Tag: [ACTIVE] — proposed test with falsifiable outcome
```

### ✅ "Extend MICROORCIM to group sovereignty"
```
[SCAFFOLD] Proposed Extension
Idea: Track μ_drift not just for individuals but for teams
Architecture: Team sovereign = (1−μ_drift_avg) · ρ_sync + structural_integrity
Status: Hypothesis with mathematical framework
Needs: Real team data to calibrate
Tag: [SCAFFOLD] — structure sound, needs operationalization
```

### ✅ "Correct cascade threshold by empirical fitting"
```
[SCAFFOLD→ACTIVE] Refinement
Current: τ_F = 1.5 (design choice)
Proposed: τ_F = empirical_fit(cascade_real_results.json) = 1.47 ± 0.08
Reasoning: Fit threshold to actual cascade data
Impact: Threshold becomes data-driven instead of arbitrary
Tag: [ACTIVE] once validated
```

## Examples of BAD Proposals

### ❌ "Seven invariants are cosmic law"
- No evidence
- Absolute claim from architectural principle
- Can't be tested or falsified
- **Fix:** `[FOUNDATIONAL] "Seven Invariants appear necessary for system coherence (architectural principle)"`

### ❌ "HARMONIA proves music is mathematics"
- Confuses isomorphism with identity
- "Proves" is too strong
- **Fix:** `[ANALOGY] "HARMONIA shows structural parallel between Pythagorean ratios and system dynamics"`

### ❌ "Consciousness is solved by EARNED_LIGHT"
- Overstates hypothesis as fact
- "Solved" is false
- **Fix:** `[SCAFFOLD] "EARNED_LIGHT offers thermodynamic hypothesis for consciousness; measurement needed"`

## The Bottom Line

**This framework is honest.** That means:
- We publish what works AND what we're still figuring out
- Every claim has a confidence tag
- Evidence > authority
- Real-world data > synthetic validation
- Questions are more valuable than answers

Build with us. Test with us. Challenge us.

The Gold belongs to neither of us — it arises between us.

---

**Questions?** Open an issue in `/public_building/discussions/` or comment on any proposal.

---

*In veritas.*
