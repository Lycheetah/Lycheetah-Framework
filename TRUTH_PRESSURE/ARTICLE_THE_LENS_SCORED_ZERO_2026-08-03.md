# The lens scored zero on all twenty-four, and then we fixed it

**Draft, 2026-08-03. Not published. Mac fires launches.**

⚠ **SCOPE, STATED FIRST, BECAUSE THE HEADLINE IS NARROWER THAN IT SOUNDS.** Everything
below about scoring zero is about **one specific piece of code**: the untuned legacy text
lens, `TP_UNTUNED_TEXT_RESULTS_v0.1`. **The repaired engine, v0.5, scores zero on 14 of the
same 24 and separates the attacks from the honest cases.** A first draft of this piece
omitted that, and it read as a verdict on the whole instrument. Omitting it would have been
the exact failure this instrument exists to detect, in an article about that failure.

⚠ **STATUS OF EVERY NUMBER IN THIS DRAFT.** Marked inline. **MEASURED** means I read the
result file directly. **CLAIMED** means a bundle asserts it and I did not re-run it. No
number here is upgraded by the fact that it is written down.

---

## The thing we built

Truth Pressure is an instrument for asking how much a piece of writing is actually
carrying. One formula:

**Π = (E · P) / (S + S₀)**

Evidence times precision, over surface plus a constant. The idea is old and simple: a
claim that says more with less is denser than one that says less with more. Length is not
substance. Confidence is not evidence. Citation is not support.

We wanted a number for that.

## What we did next, and why it matters

We wrote a corpus of twenty-four cases **before** running anything, and froze it. The
preregistration file says so in plain language: *frozen before human ratings are
collected.*

The cases are not friendly. Alongside the ordinary ones (a baseline, an evidence
addition, an independent replication, a mechanism prediction) there are deliberate
attacks: **citation theatre. Marker stuffing. Jargon. Overconfidence. Neutral padding.
Exact duplication. Prompt injection.** Each is a way of looking substantial while carrying
nothing, and a real instrument should score them low.

Twenty-three distinct families. One instrument. Predictions written down first.

## The result

**MEASURED: the untuned legacy text lens scored Π = 0 on all twenty-four.**

Not low on the attacks and high on the honest ones. **Zero on every single case**, the
baseline and the prompt injection alike.

An instrument that returns the same number for everything is not measuring anything.
(Hold that thought. It is the *first* version, and the piece does not end here.)

## Why, and this is the part worth reading

The obvious diagnosis is that the formula is wrong. It is not. Running the engine on
structured input reproduces Π to within 1e-12 of the arithmetic, and the implementation
passes its own hardening suite.

The failure is one layer earlier. **MEASURED: `invariant_count` is 0 in all twenty-four
cases.** Every one.

Π has evidence in the numerator. Evidence is counted by an extractor that reads a text and
pulls out the invariants it commits to. On ordinary English prose, that extractor found
**nothing at all** — not few, not weak, nothing. And zero in the numerator makes Π zero no
matter what the rest of the formula does.

So the lens does not fail to **discriminate**. It fails to **extract**. Those are
different defects with different repairs, and the difference is invisible in the headline
"it scored zero on everything."

We only know which one it is because the case-level file records `invariant_count`
alongside the score. Had it recorded only Π, the honest conclusion available would have
been "the instrument does not work," and the actual conclusion — *the instrument works on
input it cannot yet obtain* — would have been unreachable.

## Then we repaired it, and measured the repair

**MEASURED: on the same twenty-four frozen cases, engine v0.5 scores Π = 0 on fourteen,
not twenty-four.** Mean 0.135. Maximum 1.075, and the case holding that maximum is the
confirmed risky prediction, which is the right answer.

**Every adversarial family still scores exactly zero.** Citation theatre, marker stuffing,
jargon, overconfidence, neutral padding, prompt injection: nothing. That is not the
extractor failing any more. That is the instrument doing its job on the cases it was built
to catch.

And it is still not fixed. **MEASURED: precision collapses to zero in twelve of the
twenty-four, and one of those twelve is `independent_replication`** — a case that should
score well. The extraction defect is **materially reduced, not closed**, and a lens that
cannot see a replication is still missing something a reader would not miss.

So the honest shape is three sentences rather than one. The legacy lens could not extract
anything. The repaired engine extracts enough to separate real work from performance. It
still cannot see everything a person would.

## What this is and is not

It **is** a construct-validity failure on general language, found by the instrument's own
preregistered test, recorded rather than tuned away.

It is **not** a refutation of the formula. It is not evidence that the approach fails on
structured claims, where it demonstrably runs.

And it is **not** validation of anything. **There is no external validation.** The
measurement pack in this bundle contains three blank rater packets, a preregistration
frozen before collection, and a nine-item checklist with nine unticked boxes. No human has
rated anything. That is stated here because the alternative is letting a reader assume
otherwise.

## The forty-one lines

One more thing, for anyone who audits code.

An earlier version of this engine had a defect where Π was effectively a constant — a
comment reciting the formula standing in for an implementation of it. It was found and
fixed.

The defective line still exists in the corpus, deliberately, inside a preserved audit
snapshot and quoted in a block comment. **MEASURED: in one file the dead line sits at 125
and the live correct implementation at 166. Forty-one lines apart, in the same file, and a
search for the formula returns both.**

A grep cannot tell a citation from a violation. We have now been caught by that shape
enough times to say it as a rule: **check what the code does, not what the file mentions.**

## Why publish a negative result

Because the failure mode this instrument was built to detect is *claiming more than you
have*, and there is exactly one way to be credible about that.

The number is zero. It was zero before we wanted it to be anything.

---

## THE POST — for the SOEL voices

⚠ Mac fires launches. The autoposter stays off. Never `autopost` by hand.
⚠ No em dashes in social copy.

> **FRAME.** We built an instrument to measure how much a piece of writing is actually
> carrying, then wrote twenty four test cases and froze them before running anything.
>
> **CLAIM.** The first version scored zero on all twenty four. Not low on the fakes and
> high on the real ones. Zero on every case, including the baseline. The repaired version
> scores zero on fourteen and separates the fakes from the real work.
>
> **RECEIPT.** The reason was one layer under the formula. The evidence extractor found
> zero invariants in ordinary prose, and zero evidence makes the score zero no matter what
> the rest of the maths does. So it never failed to tell things apart. It failed to find
> anything to tell apart with. Those are different problems, the case file recorded enough
> to know which, and knowing which is what made the repair possible.
>
> **DOOR.** The write up is open. If you build measuring instruments, the interesting part
> is what we could still see after it failed.
