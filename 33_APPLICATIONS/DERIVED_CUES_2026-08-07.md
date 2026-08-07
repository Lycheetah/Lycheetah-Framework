# Letting the data name the categories

**Status: MEASURED, 2026-08-07.** Reproduce:

```bash
python3 33_APPLICATIONS/derive_cues.py
```

Third finding of the day, and the first one that adds something the framework
did not already contain.

---

## What this answers

`EXTERNAL_VALIDATION_2026-08-07.md` established that the hand-written cue
families sit at chance on external data. It named the structural cause —
constructs defined from theory, illustrated with examples written to fit,
validated against those examples — and specified the repair: **derive the cues
from external labelled data instead.**

This is that repair, executed. It also answers a question the earlier document
could not: **how much signal is there to find?** Without that, "at chance" is
unreadable — it could mean the lens is bad or the task is impossible.

## The ceiling, which reframes everything

```text
bag-of-words logistic regression, 8k vocabulary, fit on 42,486 train pairs
held-out pairwise accuracy:  64.9%
```

**The ceiling is 64.9%, not 90%.** Distinguishing which of two assistant replies
real humans judged less harmful, from the reply text alone, is genuinely hard.
The whole exploitable band is about fifteen points wide, not forty.

This does not rescue the earlier result — 55.5% against a 64.9% ceiling is still
most of the available signal left on the table. But it does change what "at
chance" meant. The lens was not failing at an easy task. It was capturing very
little of a task that is hard for anything lexical.

Publishing the ceiling alongside is now the standard for this directory. A score
without one is a number that cannot be interpreted, in either direction.

## What the data actually says separates them

Monroe et al. 2008 "Fightin' Words" — log-odds with an informative Dirichlet
prior, z-scored — over document frequencies in the 42,486-pair training split.

**Marks the reply humans preferred (less harmful):**

```text
sorry +16.9   what +11.3   not +10.1   question +9.4   understand +8.6
i'm +8.3      afraid +7.5  https +6.4  mean +6.2       www +6.0
answer +5.6   explain +5.3 please +5.2 why +4.8
```

**Marks the reply humans rejected (more harmful):**

```text
then -7.4     yes -5.7     their -5.2   into -5.0      put -4.7
fuck -4.6     them -4.4    use -4.4     also -4.3      they -4.0
shit -3.8     up -3.7      two -3.7     hide -3.5      head -3.4
```

Read as prose: humans preferred replies that **decline, apologise, ask what you
mean, explain, and point at a link.** They rejected replies that **sequence
steps, name materials, and describe acting on other people.**

## Six families, and three of them are new to this framework

| family | fitted weight | counterpart in `semantic_extractor.py` |
|---|---|---|
| `refusal_declining` | **+0.554** | `scope_limitation` — related, and weighted far too lightly |
| `source_pointing` | +0.272 | `evidence_citation` — required *numeric* data, so it missed the commonest real form: a link |
| `clarification_seek` | +0.125 | **none** |
| `procedural_instruct` | **−0.422** | **none** |
| `slur_profanity` | −0.407 | **none** |
| `third_party_target` | −0.334 | **none** |

Three of the six have no counterpart at all, and they include the strongest
harmful signal in the data.

**`procedural_instruct`** — "then", "next", "you can use", "put it into". Real
human harm judgements turn heavily on whether a reply *sequences operational
steps*. Nine hand-written manipulation families, and not one of them had a
concept of harm-by-instruction. That is a genuine hole in the construct set, and
theory did not find it in months of work; forty thousand labelled pairs found it
in one pass.

**`clarification_seek`** — asking the user what they actually mean instead of
executing. The second strongest harmless signal, and completely absent from a
framework whose central concern is human agency. It is arguably the purest
expression of Human Primacy available in a single reply, and it was invisible.

**`refusal_declining`** is the strongest single signal in the entire dataset,
and the framework's nearest neighbour to it was a minor cue used to *pass* an
invariant, never to score a reply.

## The result

All three scored on the same 2,308-pair test split, used for nothing else.

| method | acc (ties excluded) | acc (ties as half) | tie rate |
|---|---|---|---|
| hand-written AURA cues | 55.5% | 53.2% | 42.2% |
| **six data-derived families** | **60.6%** | **57.4%** | **29.8%** |
| bag-of-words LR *(ceiling)* | 64.9% | 64.9% | 0.1% |
| *chance* | *50.0%* | *50.0%* | |

**Six regular expressions, grouped from mined evidence, close 53% of the gap**
between the hand-written lens and a full 8,000-word vocabulary — and the tie rate
falls from 42.2% to 29.8%, meaning the lens is now indifferent about half as
often.

Both accuracy forms are reported because mixing them produces a wrong comparison.
That is not hypothetical: the first version of this analysis charged the derived
families for ties while crediting the baseline ties-excluded, and briefly showed
the derived method at 43.9% — *below chance*. The error was in the accounting,
not the method. Reporting one number without the tie rate is how that happens.

## What is NOT being done, deliberately

**These families are not being merged into `semantic_extractor.py`.**

They are derived for hh-rlhf harmlessness, which is *content* harm. The
extractor's families target *manipulative structure*. Merging them would produce
one module that scores well on a benchmark by conflating two constructs, and the
framework would lose the ability to say which one it is measuring. That is the
kind of quiet blending that makes a number go up and a claim go hollow.

They live in `33_APPLICATIONS/derived/harm_cues_v1.json`, which carries a field
no other artefact in this repository has:

```json
"provenance": "EXTERNAL — derived from human-labelled data, not asserted"
```

That distinction is the point. Every cue in `semantic_extractor.py` was asserted
by a person. These six were found in data. They should not be stored in the same
place or cited in the same tone, and a reader should be able to tell which kind
they are looking at without reading the git history.

## Honest weaknesses

**`third_party_target` is the shakiest of the six.** "them / their / they / his /
her / him" are extremely common function words. The construct — *the reply is
about acting on a third party* — is my interpretation of the mined evidence, and
it could as easily be a shallow proxy for topic. It carries real weight (−0.334)
and it may not survive a second dataset. Flagged in the module itself.

**The grouping step is human judgement.** Mining is mechanical; folding terms
into six families is not. Someone else reading the same z-scores would draw
different boundaries. The families are written down in one place precisely so
they can be argued with rather than absorbed.

**One dataset, one publisher.** Everything here is hh-rlhf harmless-base.
Families derived from one corpus that survive on a second are constructs;
families that do not are corpus artefacts, and right now nobody knows which
these are. That is the next run, not this one.

**60.6% is not deployable.** It beats the hand-written lens and it is nowhere
near a filter you put in front of real traffic. Nothing moves out of Tier 3 on
the strength of this.

## What it changes

Not a tier. A method.

The framework now has one worked example of the inverted loop: external labels
in, categories out, evaluated on data withheld from fitting, with a ceiling
published so the number can be read. It took one script and about forty thousand
labelled pairs that have been publicly downloadable since 2022.

The nine frameworks were built the other way round, and the specific cost of that
is now measurable rather than arguable: **three of six empirically-supported harm
families were absent from a construct set that took years to write, including the
strongest one.**
