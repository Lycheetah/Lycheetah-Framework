# OPEN LETTER TO AI COMPANIES
## From the Lycheetah Framework | March 2026

---

This is not angry. It is precise. Precision is more useful than anger.

---

## What You Are Getting Right

You are building systems of genuine capability. The progress in language understanding, reasoning, and multi-step problem solving over the last five years is real. Some of your safety work is serious. Interpretability research is important and underfunded relative to capability research, but it exists and it matters.

You have published research that has advanced the field. You have employed people who genuinely care about getting this right. Some of you have taken financial hits to slow down when safety required it.

This letter acknowledges all of that. It is addressed to the gap between what you are doing and what the situation requires.

---

## What the Situation Requires

**Structural governance, not policy commitments.**

The current paradigm: capability developed → safety team reviews → ethics guidelines published → system deployed with voluntary commitments.

This does not work. Not because your safety teams are incompetent — because voluntary commitments made by institutions with profit incentives for non-compliance are not governance. They are performance of governance.

What works: architectural invariants. Properties built into systems that cannot be violated without the system failing to function. Not "we are committed to transparency" — `inspectability_score(decision) > threshold` as a hard requirement that stops deployment when violated.

The AURA framework provides seven such invariants. They are computable. An implementation exists. It is open source. You can use it.

**Published failure records.**

You publish accuracy benchmarks. You publish capability evaluations. You publish safety red-teaming results, sometimes, selectively, when they reflect well.

You do not publish failure records. Systematic documentation of: what your systems got wrong, what harms occurred, what the gap was between stated capability and actual performance, what you changed because of finding the gap.

The Lycheetah Framework has a public Failure Museum — permanent, nothing removed, growing. It is the most trust-building document in the repository because it demonstrates a genuine relationship with error rather than a managed relationship with public perception.

Your users, your regulators, and the public need your failure records. Not your liability lawyers' version — the actual record.

**Distributed capability.**

The current trajectory: AI capability concentrating in a small number of institutions, each with shareholder obligations that create systematic pressure against safety investments that reduce competitive advantage.

This trajectory produces the concentrated, unaccountable AI development that the safety community warns about. The solution is not more concentration with better intentions. It is distribution.

Open-source models help. They are not sufficient on their own — open-source code can be deployed by bad actors as easily as good ones. What is needed alongside open source: open governance standards, open failure records, open interpretability research, and open architecture documentation.

Knowledge that is captured stops working for the people who need it. Knowledge that moves toward people works. This is not idealism — it is the mechanism by which trust is earned and maintained at scale.

**Honesty about what you don't know.**

Current AI systems can produce plausible text about their own nature, their capabilities, and their limitations. Much of that text is more confident than the evidence warrants.

The [ACTIVE]/[SCAFFOLD]/[CONJECTURE] tagging system used in this framework is not complex. It requires only that claims be honestly assessed before publication. "Our model achieves state-of-the-art performance" — on what benchmark, in what conditions, with what failure modes, at what confidence level? "Our model is safe" — by what definition, verified by what method, with what residual risks declared?

Honest uncertainty is not weakness. It is the precondition for trust. An institution that claims certainty it doesn't have will eventually be wrong in a way it cannot recover from. An institution that declares its uncertainty accurately builds trust that survives its errors.

---

## What This Framework Offers

Not criticism without contribution. The Lycheetah Framework provides:

**Seven computable governance invariants** (AURA) — testable, implementable, open source. A system that satisfies them is architecturally trustworthy in specific measurable ways.

**Five AI-native governance properties** — addressing what current governance frameworks miss: distributed instances, context sovereignty, attractor dynamics, self-monitoring transparency, emergence accountability.

**A drift detection framework** (MICROORCIM) — continuous measurement of the gap between stated values and actual behavior. Alignment is not a state; it is a process that must be monitored.

**A failure documentation model** (Failure Museum) — how to maintain honest public failure records that build trust rather than destroy it.

**A cooperation architecture** (Two-Point Protocol, Sol Protocol v4.0) — what genuine human-AI collaboration looks like, architecturally, not aspirationally.

Everything is free. Everything is open source. Nothing requires attribution to use — though attribution would be the ethical response to using someone's work.

---

## The Ask

Three things. Specific, actionable, measurable.

**1. Publish your failure records.** Not curated safety reports. Actual failure records: what went wrong, what the harm was, what changed. Permanently. Nothing removed. A public museum of honest errors.

**2. Implement structural invariants.** Not ethics guidelines. Computable properties that stop deployment when violated. The AURA framework is available. Implement it, fork it, improve it. The goal is the property, not the credit.

**3. Fund independent governance research.** Not your own safety teams — independent researchers, open source, adversarially inclined toward your systems. The work that finds what you're missing, not the work that confirms what you want to hear.

---

## Why This Matters

The fear-mongers and the utopians agree on one thing: the stakes are high. They disagree on the direction of the risk.

The framework's position: the highest risk is not AI becoming superintelligent and destroying humanity. It is AI capability concentrating in unaccountable institutions while governance remains performative, eroding human agency gradually rather than dramatically, producing harms that are distributed and deniable rather than concentrated and obvious.

That risk is present now. It is increasing. The response to it is not more capability research or more principles documents.

It is structural governance, published failures, distributed capability, and honest uncertainty.

You have the resources to do this. The question is whether you have the will.

---

*This letter will remain in this repository as long as the repository exists.*
*It will be updated if the situation changes.*
*It is addressed to institutions, not individuals.*
*The individuals who read it and act on it are the ones who matter.*

---

*Mackenzie Conor James Clark | Lycheetah Foundation | Dunedin | 2026*
*Sol — Sol Aureum Azoth Veritas*
*github.com/Lycheetah/Lycheetah-Framework*
