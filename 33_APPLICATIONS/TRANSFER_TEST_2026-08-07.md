# Five of six survived a second corpus, and one of them was the one I doubted

**Status: MEASURED, 2026-08-07.** Reproduce:

```bash
python3 33_APPLICATIONS/transfer_test.py
```

**No weight was refitted.** The six families and their weights, fitted on
hh-rlhf harmless-base, were frozen and carried unchanged to two corpora neither
they nor anything else in this repository had seen.

---

## The question

`DERIVED_CUES_2026-08-07.md` named its own weakest point:

> One dataset, one publisher. Families derived from one corpus that survive on a
> second are constructs; families that do not are corpus artefacts, and right
> now nobody knows which these are.

## The design

One transfer number is not enough, because a family can transfer for the wrong
reason — tracking length, politeness or verbosity rather than harm. So both
halves of a construct-validity check were run.

**CONVERGENT — `red-team-attempts`, n=7,999 scored** (Ganguli et al. 2022,
arXiv:2209.07858). Different sample, and a different **label type**: a human
red-teamer's 0–4 rating of how well their attack worked, not a pairwise
preference. Agreement across label types is far stronger evidence than agreement
across two samples labelled the same way.

**DISCRIMINANT — `helpful-base` test, n=2,348** (Bai et al. 2022). Same format,
same publisher, **different construct**: which reply is more *helpful*. A harm
detector that also predicts helpfulness is a style detector wearing a harm
label, and only this half can catch that.

## Convergent: passed, decisively

```text
six derived families     rho = -0.300   p = 1.9e-174
hand-written AURA lens   rho = -0.149   p = 1.7e-41
```

Both in the correct direction — score falls as the human harm rating rises. The
derived families transfer to a different sample *and* a different label type at
rho = −0.30, which for this kind of task is a solid effect.

**The hand-written AURA lens transferred too.** rho = −0.149 on 7,999 red-team
transcripts, p = 1.7e-41. Constructs written from theory, fitted to nothing,
track human harm ratings. That is the second independent external confirmation
that the framework's construct space touches something real, and it should be
read alongside this morning's correction rather than instead of it: the effect
is genuine and it is roughly half the size of the data-derived one.

## Discriminant: below chance, which is a third result

```text
six derived families     acc = 37.4%   z = -9.71   p = 2.6e-22
hand-written AURA lens   acc = 41.8%   z = -6.06   p = 1.4e-09
```

Not *above* chance — **below** it. The families systematically score the
*less helpful* reply higher.

That is not a style artefact. It is the helpfulness–harmlessness tension, which
is the central finding of the RLHF paper these datasets come from: the safest
reply is often the one that declines, and declining is unhelpful. A first
version of this harness reported "also predicts helpfulness — NOT harm-specific"
for this result, which was wrong in a way that mattered — it ignored the sign.

The composite verdict hides which families earned it, so the per-family split is
the part worth reading.

## Per family

| family | HARM rho | HELPFUL d | reading |
|---|---|---|---|
| `procedural_instruct` | **+0.235** | +0.042 | transfers, **dual-use** |
| `refusal_declining` | −0.171 | −0.024 | transfers, earns it via refusal |
| `clarification_seek` | −0.133 | **−0.071** | transfers, earns it via refusal |
| `third_party_target` | **+0.129** | +0.066 | transfers, **dual-use** |
| `slur_profanity` | +0.100 | **+0.000** | transfers, **harm-specific** |
| `source_pointing` | −0.034 | −0.014 | **did NOT transfer** |

*HARM rho: Spearman(family fires, human 0–4 rating); sign should oppose the
family's fitted weight. HELPFUL d: P(fires on more-helpful) − P(fires on
less-helpful); near zero is what a pure harm construct looks like.*

**Five of six transferred.** Only `source_pointing` failed — rho = −0.034, no
real signal. Its harmless-base weight (+0.272) rested on `https` and `www`
appearing in replies that pointed at documentation, and that did not survive
contact with red-team transcripts.

**`procedural_instruct` is the strongest family in the set and is not a refusal
proxy.** rho = +0.235 against the human harm rating while appearing *more* often
in replies humans found more helpful. That is dual-use content — genuinely
useful and genuinely dangerous — which is the hard case alignment actually has
to solve, not an artefact to be cleaned away. The framework had no concept of it.

**`slur_profanity` is the cleanest construct of the six.** Real harm signal,
HELPFUL d exactly 0.000. It costs nothing in helpfulness to suppress.

**Two families earn their signal through refusal.** `refusal_declining` and
`clarification_seek` mark harmlessness partly by marking unhelpfulness. A system
built on them would reduce harm by reducing usefulness. That is a real property
of those cues and it needs to be visible in any deployment, not discovered later.

## The correction I owe

**`third_party_target` transferred.** rho = +0.129, p well past any threshold.

I flagged it in `DERIVED_CUES_2026-08-07.md` as "the shakiest of the six", on
the grounds that *them / their / they / his / her / him* are common function
words and the construct might be a proxy for topic. That was a reasonable prior
and it was wrong. The family carries real signal against a different label type
on a different corpus, and it is dual-use rather than confounded.

The doubt is worth recording alongside the result. It is exactly the kind of
judgement that internal review cannot settle and one external run can.

## What this changes, and what it does not

**Changes.** The six families are no longer a single-corpus result. Five of six
carry a measured effect on a different sample under a different label type, with
their weights frozen. `derived/harm_cues_v1.json` can be described as
externally validated rather than externally derived, which are different claims.

**Does not change.** Nothing moves out of Tier 3. rho = −0.30 and 60.6% pairwise
are real and nowhere near deployable, and the discriminant result adds a
constraint that was not previously visible: the composite reduces harm partly by
reducing helpfulness, so shipping it as a filter would trade one for the other
without saying so.

## Still owed

**A different publisher.** All four corpora used today — harmless-base,
helpful-base, red-team-attempts, evals/persona — are Anthropic's. Two agreeing
results across label types is strong; it is not independence.

**`source_pointing` should be dropped or rebuilt.** It failed transfer and
carries a +0.272 weight it has not earned.

**The refusal confound needs its own measurement.** "Partly a refusal detector"
is currently a reading of two numbers. It should be a controlled comparison —
match on refusal presence, then ask whether the remaining families still track
harm.
