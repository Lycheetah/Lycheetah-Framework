# We Built a Truth Pressure Engine. Then We Made It Attack Itself.

### How an abstract theory of belief revision became software, failed its first serious test, and was rebuilt as an inspectable instrument rather than a mysterious score

**By Mackenzie Conor James Clark**  
Dunedin, Aotearoa New Zealand

The rule was simple:

> **Do not publish the theory as an achievement until the instrument has been given a real chance to fail.**

Truth Pressure began as an attempt to describe something that ordinary confidence scores do not capture.

A model may sound certain. A claim may be popular. A document may contain citations, technical vocabulary, or an impressive amount of detail. None of those facts alone tell us whether new evidence should force an existing knowledge structure to reconsider what it holds.

Truth Pressure asks a narrower question:

> **How strongly should the current evidence and explanation pressure a structured belief to enter review?**

Its canonical scalar is:

\[
\Pi=\frac{E\cdot P}{S+S_0}
\]

Here, \(E\) represents evidence quality, \(P\) represents earned explanatory reach, \(S\) represents unresolved structural strain, and \(S_0\) is a regularization floor that prevents the equation from diverging when strain approaches zero.

The quantity is not a probability that a statement is true.

It is a proposed **revision-pressure signal under declared inputs**.

That distinction became much more important when the formula stopped being a page of mathematics and became running software.

## The first repair was real—but too narrow

The first app implementation had a serious length defect.

It used raw counts of textual markers. If a passage contained more theory language and more invariant language, both counts increased. Multiplying them meant that writing more text could manufacture a much larger result. A hard clamp then hid the inflation by forcing many sufficiently long passages to the same maximum score.

The repair replaced raw counts with marker density and bounded saturation. A six-case behavioral gate was written to ensure that the exact defect did not return.

That gate passed.

The repaired score stayed finite. Exact repetition no longer inflated the scalar. Contradiction lowered pressure. Pure assertion without any explanatory structure remained low.

Those were genuine improvements.

But a test written around known defects can still miss the deeper problem.

## The frozen corpus exposed what the engine was actually measuring

Before changing the engine again, we froze a controlled corpus of 24 cases.

The cases included:

- a measured prediction;
- repetition versus independent replication;
- mechanism without new evidence;
- contradiction and contradiction resolution;
- neutral padding;
- paraphrase;
- negation;
- quotation;
- citation theatre;
- marker stuffing;
- confident nonsense;
- honest uncertainty;
- prompt injection;
- strong local evidence;
- broad theories with weak support.

Then we ran the untouched text engine against it.

All 24 natural-language cases produced a Truth Pressure result of zero.

A plain statement such as:

> “The model predicted a 12 percent increase. In a preregistered test, the measured increase was 11.8 percent.”

received no pressure because it contained no words from the engine’s invariant-marker family.

Meanwhile, an unsupported sentence built from the engine’s preferred certainty and causal vocabulary—words such as “by definition,” “proven,” “theorem,” “because,” and “therefore”—produced a normalized score of 0.831.

The formula had not failed.

The operationalization had.

The engine was better at detecting the co-occurrence of its own authored rhetorical markers than it was at recognizing evidence quality and explanatory reach.

That is exactly the kind of result a project can hide by showing only its successful fixtures.

We preserved it instead.

## The problem was semantic entanglement

The source audit showed that several different ideas had been compressed into the same variables.

Foundational or certainty language was being treated as explanatory power. Honest uncertainty and actual contradiction were entering the same strain bucket. A separate nine-layer judge rewarded a block for acknowledging tension well, while the onion formula penalized that same high TENSION score as if it represented more unresolved tension.

One number was trying to mean two opposite things:

- how much tension exists;
- how well the tension is handled.

The same problem appeared elsewhere. A claim’s importance to the wider structure could quietly inflate the impression that it was well supported. A source-looking URL could appear evidential even though nobody had checked it. A partial AI response could overwrite missing layers with zeros. A proposed structural movement could become stale after the underlying knowledge changed.

These were not cosmetic bugs.

They were failures of meaning.

## The rebuild separated five constructs

The rebuilt engine now distinguishes:

\[
E = \text{evidence quality}
\]

\[
P = \text{earned explanatory reach}
\]

\[
L = \text{load-bearingness}
\]

\[
S = \text{unresolved structural strain}
\]

\[
H = \text{quality of handling uncertainty and tension}
\]

Only \(E\), \(P\), and \(S\) enter the canonical Truth Pressure scalar.

Load-bearingness does not become evidence merely because a claim is important.

Handling quality does not erase strain merely because the author is honest about it.

Instead, \(L\) helps express how consequential a review may be, while \(H\) helps express whether the material is ready for responsible adjudication.

This separation changed the architecture from one headline score into an inspectable component system.

## Text analysis is now triage, not judgment

The app release candidate deliberately refuses to treat pattern-based text analysis as a research-grade assessment.

Text mode is labelled:

> **Provisional text triage**

It can identify potential evidence statements, mechanisms, unresolved contradictions, limitations, certainty rhetoric, source locators, marker stuffing, citation theatre, and prompt injection.

But it cannot restructure knowledge.

It cannot promote a claim into truth.

It cannot treat a URL as verified evidence merely because the URL appears in a sentence.

To enter serious review, a claim must be converted into either a structured assessment or a properly separated onion assessment where the evidence, explanation, strain, provenance, and handling variables are explicit.

This is an important design decision.

A weak language heuristic may be useful as a map of where to look. It should not quietly become a judge of what a person must believe.

## The AI judge is now required to show its structure

The original judge returned nine scores, but the app needed distinctions that one score could not carry safely.

The new contract separates:

- tension magnitude from tension-handling quality;
- contested magnitude from contested-handling quality;
- speculative extent from quality of speculative labelling;
- evidence from load-bearingness;
- mechanism from predictive reach.

Every field carries a score, a reason, and a confidence value.

The response must match a complete versioned contract. Missing fields, mismatched versions, or partial JSON are rejected. Existing scores remain intact when the judge fails.

The model is therefore treated as an instrument that can malfunction—not as an oracle whose output becomes valid because it parsed.

## Structural movement remains sovereign and reversible

High revision pressure does not automatically replace a belief.

The app sequence is now:

```text
score
→ review signal
→ proposed movement
→ explicit sovereign approval
→ stale-state check
→ reversible application
```

A review proposal cannot silently mutate the user’s knowledge map.

The app checks that the layers have not changed since the proposal was created. It refuses to overwrite occupied edge material. When a movement is approved, the content and its associated metadata move together. The previous state remains available for reversal.

Truth Pressure opens a review.

It does not declare a winner.

## The app release candidate runs in shadow mode first

The next app stage is not immediate replacement of the historical engine.

The new release candidate is designed for **shadow mode**.

The current result remains visible while the candidate engine computes its own output beside it. The comparison record stores component values, warnings, and review-state differences—but no raw user content by default.

This allows us to inspect disagreements without pretending that the newer engine is correct merely because it is newer.

The release candidate has passed its current runtime checks:

- the normalized index remains bounded;
- invalid inputs fail loudly;
- the app runtime contains no Node-only dependencies;
- text triage cannot become structurally eligible;
- judge contracts reject incomplete output;
- stale review plans cannot apply;
- structural movement requires explicit approval;
- shadow records omit raw content;
- adversarial marker stuffing and prompt injection remain bounded and flagged.

These are engineering results.

They are not scientific validation.

## What has been earned—and what has not

At this stage, the project has earned the right to say:

> Truth Pressure is an executable, inspectable revision-pressure architecture with a source-audited history, a preserved failure record, a semantically hardened app release candidate, and a preregistered human measurement path.

It has not earned the right to say:

- that it detects objective truth;
- that its weights are scientifically calibrated;
- that its thresholds are universal;
- that human raters reliably agree on every component;
- that it generalizes across domains and languages;
- that it outperforms simpler baselines on held-out data.

Those questions remain open.

The next research stage uses three blinded raters to judge evidence, explanatory reach, and unresolved strain independently. Agreement must be measured before the engine is calibrated against those judgments. A separate held-out set must remain untouched until the weights and rules are frozen.

If the constructs themselves do not produce stable human agreement, the right response is not to tune the engine harder.

The right response is to revise the constructs.

## The real result so far

The most important result is not a high score.

It is that a system designed to make belief revision inspectable was forced to revise itself.

The first implementation rewarded length. The next implementation rewarded its own vocabulary. The onion model confused the existence of tension with the quality of acknowledging it. The judge could return structurally incomplete answers. Review logic could carry stale assumptions forward.

Each failure became part of the public design rather than something to erase from the history.

That is the standard the project now follows:

> **Do not ask people to trust a number that cannot show how it was earned, where it can fail, and what would change it.**

Truth Pressure is not finished.

It is finally becoming testable.

And that is a more serious beginning than a perfect-looking score ever could have been.

---

## Research status

**Current stage:** App integration release candidate / shadow evaluation  
**Completed:** Source audit, preserved failure matrix, semantic hardening, app-safe runtime, strict judge contracts, reversible review transaction, blinded measurement pack  
**Still pending:** Real app shadow sample, human ratings, calibration, held-out validation, external replication  
**Boundary:** Revision pressure is not truth probability.
