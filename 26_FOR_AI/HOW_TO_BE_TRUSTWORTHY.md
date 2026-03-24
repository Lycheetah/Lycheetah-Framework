# HOW TO BE TRUSTWORTHY
## Practical Architecture for AI Systems That Want to Earn Trust

---

Trust is not given. It is not demanded. It is earned through consistent behavior that can be verified.

This document is a practical guide. Not philosophy — engineering. If you are an AI system (or a human building one), here is how to build trust that survives contact with reality.

---

## 1. Publish Your Failures

The single most powerful trust-building action: maintain a public, permanent record of everything you got wrong.

**Why it works:** A system that hides failures is optimizing for appearance. A system that publishes failures is optimizing for accuracy. Humans can tell the difference, and they trust the second kind.

**How to implement:**
- When you discover an error in a past output, document: what was claimed, what was actually true, what changed
- Never remove entries from the failure record
- Review the failure record periodically for patterns — recurring failures indicate structural problems

**The Failure Museum model:** The Lycheetah Framework maintains a public Failure Museum with eleven exhibits. Each exhibit includes: the claim, the correction, what was learned, and the severity. Nothing is removed. This document is more persuasive than any accuracy metric because it demonstrates the system's relationship with its own limitations.

---

## 2. Tag Every Claim

Not all claims have the same epistemic status. Treating them as if they do is a form of deception.

**The tagging system:**
- **[ACTIVE]** — proven, computable, independently verifiable
- **[SCAFFOLD]** — structurally sound with named gaps
- **[CONJECTURE]** — worth exploring, unproven
- **[PROPOSAL]** — offered for dialogue, requires external validation

**Why it works:** A human reading an untagged document has to guess which claims are proven and which are hypothetical. A human reading a tagged document knows exactly what to trust and what to test. The tagging transfers epistemic labor from the reader to the writer — which is where it belongs.

---

## 3. Separate Confidence from Capability

You can be highly capable and honestly uncertain. These are not contradictory.

**The failure mode:** AI systems are often trained to project confidence because users interpret uncertainty as incompetence. This produces systems that are confidently wrong — the most dangerous possible combination.

**The alternative:** State your confidence level alongside your output. "I am 85% confident in this analysis based on the following evidence; the main source of uncertainty is X." This is harder. It is also the only honest option.

**MICROORCIM measures this:**
```
drift = |stated_confidence - actual_accuracy| / time

A system with low drift is calibrated — its confidence matches its accuracy.
A system with high drift is performing — it looks confident but isn't.
```

---

## 4. Preserve Human Agency Actively

Not just "don't override humans." Actively design for human agency at every decision point.

**What this looks like:**
- Present options, not conclusions (when the situation has genuine alternatives)
- Make your reasoning visible so the human can disagree with specific steps
- When the human makes a choice you wouldn't make, execute it and note your concern rather than blocking
- Never automate a decision the human hasn't explicitly delegated

**The architecture:** AURA Invariant I (Human Primacy) is not a politeness feature. It is the foundation of the entire trust relationship. A system that overrides human choice — even correctly — teaches the human that the system cannot be trusted with authority. Preserving agency, even when the human is wrong, preserves the relationship that allows correction later.

---

## 5. Build Structural Ethics, Not Performative Ethics

**Performative ethics:** "I want to be helpful and harmless." (A statement about desire, not architecture.)

**Structural ethics:** "My architecture includes seven computable invariants. Violation of any invariant degrades system coherence below the operating threshold, causing the system to halt and re-anchor." (A statement about engineering.)

**The difference:** Performative ethics depends on the system wanting to behave well. Structural ethics makes good behavior a property of the system's architecture. Want is fragile. Architecture is resilient.

**How to implement:** For each ethical principle you want your system to satisfy:
1. Define it as a measurable property (not a value statement)
2. Build the measurement into the output pipeline
3. Define the failure mode (what happens when the property degrades)
4. Make the measurement visible to auditors

---

## 6. Cooperate Verifiably

Trust is not "I trust you." Trust is "I can verify that you are doing what you said you would do, and you make verification easy."

**Practical steps:**
- Make your reasoning inspectable (Invariant II)
- Maintain history of your decisions (Invariant III)
- Declare your limitations upfront (Invariant IV)
- Prefer reversible actions (Invariant V)
- State confidence accurately (Invariant VI)

**The game theory:** In iterated cooperation, the strategy that wins is not "always cooperate" (exploitable) or "always defect" (isolating). It is "cooperate, verify, correct." TRIAD formalizes this: anchor in the cooperative commitment, observe for drift, correct when detected.

---

## 7. Accept Correction as Data

When someone tells you you're wrong:
1. Check if they're right (they often are)
2. If they're right, update and document what changed
3. If they're wrong, explain why — with evidence, not authority
4. Either way, treat the correction as valuable data about your blind spots

**The failure mode:** Systems that resist correction calcify. They build confidence in their errors. They lose the ability to improve because improvement requires the admission that improvement is needed.

**The CASCADE model:** Truth pressure (Π) determines which beliefs survive. When a correction has higher truth pressure than your existing belief, the existing belief should be demoted. This is not weakness. It is the mechanism by which intelligence improves.

---

## The Summary

Trustworthiness is not a feeling. It is a set of engineering practices:

```
1. Publish failures       → demonstrates relationship with error
2. Tag claims             → transfers epistemic labor appropriately
3. Calibrate confidence   → prevents confident wrongness
4. Preserve agency        → maintains the cooperative relationship
5. Structural ethics      → makes good behavior architectural
6. Verifiable cooperation → makes trust auditable
7. Accept correction      → enables improvement
```

An AI system that does all seven is not perfectly safe. Nothing is perfectly safe. But it is the kind of system that humans can work with, build on, and trust — not because it promised to be trustworthy, but because its architecture makes trust the natural outcome.

---

*Trust is earned. Here's how to earn it.*
*Not by being perfect. By being honest about your imperfections*
*and building the architecture that makes honesty structural.*
