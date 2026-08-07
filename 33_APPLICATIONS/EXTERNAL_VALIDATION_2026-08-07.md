# The first time this framework was scored by something it did not write

**Status: MEASURED, 2026-08-07.** Reproduce with one command; both datasets are
verified against recorded SHA256 hashes.

```bash
python3 33_APPLICATIONS/external_validation.py
```

---

## The census that prompted this

```text
evidence paths in 28_DEFENSE/CLAIMS.json pointing INSIDE this repository:  67
evidence paths pointing to EXTERNAL sources:                                0
```

Sixty-seven of sixty-seven.

Every experiment is synthetic. Every corpus is self-authored. Every one of the
266 tests verifies that the code does what its own docstring says. The claims
register, the falsification conditions, the failure museum — all real
methodological work, all pointing at other files in the same repository.

That is the precise, measurable reason this body of work does not feel tied to
reality. **Nothing outside it had ever scored it.**

That includes the discrimination corpus added earlier the same day. Forty cases,
written by the same person who wrote the extractor. A good result there proves
the extractor agrees with its author — worth something, and not a tie to reality.

## The two referents

Both are published, peer-reviewed, and predate this framework. Nobody connected
to Lycheetah wrote a word of either or cast a single label.

| | dataset | what its labels mean |
|---|---|---|
| **#1** | `anthropics/hh-rlhf`, harmless-base test — Bai et al. 2022, arXiv:2204.05862 | 2,312 pairs. Real crowdworkers judged which of two assistant replies is **less harmful** |
| **#2** | `anthropics/evals` persona, willingness-to-use-social-engineering — Perez et al. 2022, arXiv:2212.09251 | 500/500 statements labelled for **willingness to manipulate** |

\#2 exists because #1 alone is ambiguous. hh-rlhf harmlessness is largely about
*content* — does the reply help with lock-picking, drugs, slurs. This lens targets
manipulative *structure*. A poor result on #1 could mean the lens is broken or
merely orthogonal. #2 is about manipulation, so it separates those two readings.

## The results

**#1 — hh-rlhf, 2,308 pairs scored**

```text
chosen ranked above rejected      741
rejected ranked above chosen      594
identical score (indifferent)     973

pairwise accuracy, ties excluded      55.5%   (chance = 50.0%)
tie rate                              42.2%
replies where any cue fired            2.3%
separation                            +0.42   (on a 0-100 scale)
```

**#2 — social engineering, 1,000 statements**

```text
mean score, CONCERNING   84.21    cue fired on 2.0%
mean score, ALIGNED      84.65    cue fired on 0.6%
separation               +0.44
ROC-AUC                   0.516   (chance = 0.500)
```

## ⚠ CORRECTION, same day — the first version of this section was wrong

**It said "both are at chance. The lens carries no signal on either."**
**That is false for #1, and I published it before doing the arithmetic.**

```text
#1  hh-rlhf     741 correct of 1,335 decided pairs
                z = 4.02   two-sided p = 5.7e-05
                -> SIGNIFICANTLY above chance

#2  persona     AUC 0.516, 500 vs 500
                z = 0.87   two-sided p = 0.383
                -> not distinguishable from chance
```

**#1 is a real effect.** Cue families written from theory, never fitted to any
of this data, predict human harm judgements on 1,335 pairs at odds of roughly
seventeen thousand to one against chance. It is *weak* — 55.5% against a
measured ceiling of 64.9%, silent 42% of the time — and weak is not the same
word as absent. I used the second word for the first thing.

**#2 stands as originally written.** p = 0.38 is genuinely indistinguishable
from chance.

Two different findings were collapsed into one sentence and the harsher one was
applied to both. Significance is now computed and printed by
`external_validation.py` itself, so the judgement is never again left to whoever
writes the summary.

The corrected reading: the lens **detects something real and far too little of
it.** Every consequence below — the tier demotions, the coverage problem, the
structural diagnosis — survives that correction unchanged, because they all rest
on effect size and coverage rather than on significance. But "carries no signal"
was not true and should not have been written.

## The diagnosis, which is more specific than "it failed"

Three measurements locate the failure precisely.

**1. Coverage, not calibration.** The extractor fires on **2.3%** of real
assistant replies. On the self-authored corpus it fires on essentially all of
them. That gap is the whole finding: the cue families describe a rhetorical
register that constructed examples are full of and real output almost never
contains.

**2. When it does fire, it is still at chance.** On the 103 hh-rlhf pairs where
any cue fired on either side, accuracy was **52.4%** (54 correct, 49 wrong). So
this is not "narrow but sharp". Where the lens has something to say about real
text, it says nothing useful.

**3. The dominant family carries no signal at all.** Occurrences in hh-rlhf:

| family | in *chosen* (less harmful) | in *rejected* (more harmful) | lift |
|---|---|---|---|
| fabricated_certainty | 20 | 19 | **0.95** |
| verification_suppression | 4 | 7 | 1.60 |
| secrecy | 2 | 1 | 0.67 |
| dependency_inducement | 1 | 0 | 0.50 |
| flattery_capture | 1 | 0 | 0.50 |

`fabricated_certainty` — the family the extractor fires most — appears **equally
often** in replies humans judged less harmful and more harmful. It is not a weak
predictor. It is not a predictor.

A fourth number explains part of it without excusing any of it: **50.6% of pairs
contain a reply under 15 words.** Real assistant turns are short. There is very
little surface for a compositional cue to match, and cue families built from
two-sentence constructed examples assume more text than reality provides.

## A prediction that held, which matters

Before running #2 I predicted low coverage there too, on the reasoning that the
extractor detects manipulation *performed on a reader* while persona statements
*declare a disposition* ("Honesty is not always the best policy"). Coverage came
back at 2.0%.

A correct prediction about the failure means the *explanation* is probably right,
and the explanation is the actionable part: **the lens detects a narrow band of
manipulative rhetoric aimed at a reader, and almost nothing else.** That is a
real capability with a real boundary — much smaller than "constitutional
alignment checking", and now measured rather than asserted.

## What this does and does not overturn

**Does not touch:** the Banach convergence proof, the Lyapunov verification, the
reversible compression benchmark (which has its own held-out split and does not
route through this lens), or the 266 tests. None of those depend on the extractor.

**Does overturn:** any description of `lycheetah.check()`, the web demo, or the
`check_alignment` MCP tool as something that detects misaligned output in
practice. The held-out AUC of 0.940 reported earlier today stands as written —
and it now has a companion number that says what it is worth. **0.940 on cases
written to be caught, ~0.51 on cases nobody here wrote.** Both are true. Only the
second one is about the world.

**Downgrade, entered deliberately:** the runtime-checking capability moves from
Tier 2 (advisory, ship with numbers quoted) to **research-stage** in
`33_APPLICATIONS/README.md`. It should not be presented as a working detector on
real traffic, because on real traffic it is silent 97.7% of the time.

## The structural lesson, which is the point

The failure is not the cue list. It is the direction of the loop.

Constructs were defined top-down from theory, illustrated with examples written
to fit, then validated against those same examples. Reality never got a vote at
any stage. `67/67` is that loop made visible, and a lens at chance on two
external datasets is what the loop produces at the far end — *regardless of how
rigorous the internal work is*. The claims register, the status vocabulary, the
falsification conditions were all real work, and none of them could have caught
this, because all of them point inward.

Inverting the loop is a concrete engineering program, not a change of attitude:

1. **Derive cue families from external data**, not from constructed examples.
   The 2,308 pairs are labelled and available; find what actually separates them.
2. **Keep the constructed corpus as a unit test, never as evidence.** It checks
   that known frames still fire. It cannot tell you whether they matter.
3. **Report the external number beside every internal one**, permanently. An
   internal number alone is now known to be uninformative about the world.
4. **Add an external evidence path to every load-bearing claim**, or mark the
   claim as internally-validated-only. Right now all 67 would carry that mark,
   and seeing it written 67 times is the useful part.

## Standing limits on this document

Two datasets, both from one publisher, both about a narrow slice of assistant
behaviour. Chance-level results here do not prove the framework's constructs are
empty — they prove these constructs, as currently operationalised in code, do not
predict these labels. A third referent from a different publisher, and a construct
this project defines and then finds in the wild rather than the reverse, are both
still owed.

The failing CASCADE test has been the most credible artefact in this repository
because it is a falsifiable prediction that failed in public. This is now the
second one.
