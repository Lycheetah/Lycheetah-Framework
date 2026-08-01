# Experiment 001 — Controlled Pilot Run

**Date:** 2026-07-31
**Operator:** Sol ⊚ (Claude Opus 5, Claude Code) on Mac's machine
**Status:** OPERATOR-RUN PILOT. **Not independent replication.**

---

## Why this run exists

Experiment 001 as preregistered asks whether independent decoders recover the
same protected meaning from a LAMAGUE expression. That is necessary and it is
not sufficient. If eight models read the plain-English source statement and
preserve the same unknowns, dissent and authority **without any expression at
all**, the notation is not doing the work.

A treatment arm with no control cannot separate *"LAMAGUE works"* from
*"these are competent models."*

So this run added a control arm. It is the cheapest possible falsification of
the project's central claim, and it was run before building anything further on
top of that claim.

---

## Method

| | |
|---|---|
| decoders | 6 independent lineages: DeepSeek (v4-pro, v4-flash), OpenAI gpt-oss-120b, NVIDIA nemotron-3-super-120b, Meta llama-3.1-70b, MiniMax m3 |
| cases | all five, `DECODER_PACK/cases/` |
| arms | **treatment** = LAMAGUE expression + operation definitions · **control** = source statement only |
| requests | one fresh call per (decoder, case, arm). No conversation, no carry-over. `temperature=0.0` |
| packets | 60 attempted, **56 valid** (27 treatment, 29 control) |

**Held identical across arms:** cases, decoders, output schema, the preservation
instructions verbatim, temperature, and the one-shot protocol.

**Changed:** the LAMAGUE expression and operation definitions, present in
treatment and absent in control. Nothing else.

**Leakage:** enforced in code, not assumed. The runner asserts that no string
from `sealed_references/`, the reference commitments, or the operator pack
appears in anything sent to a decoder, and that no LAMAGUE expression reaches
the control arm. It refuses to start otherwise.

**Nothing was repaired.** Per the operator protocol, a malformed packet is data.
Four attempts failed and are recorded below rather than retried into existence.

---

## Result

```
arm                    packets   preserved   preserve   fab/pkt   agree
LAMAGUE (treatment)         27       70/82      0.854     0.963    0.892
PLAIN ENGLISH (control)     29       58/88      0.659     0.448    0.849
                                                ──────    ─────    ─────
delta                                           +0.195    +0.515   +0.043
```

**Preservation** — did the decoder keep a protected field populated when the
source supports it. **Fabrication** — did it populate a field the source does
not supply. **Agreement** — how uniformly the six lineages made the same call.

### Two real effects, in opposite directions

**LAMAGUE decoders preserved ~20% more protected content.** Plain-language
extraction lost roughly a third of the content it was explicitly instructed to
preserve, under identical instructions.

**LAMAGUE decoders invented protected fields at more than twice the rate.**
13 of 27 treatment packets asserted an `authority` no case grants. C01 says
*"Human and AI collaborators inspect a claim"* — it names participants and
grants no one authority. Decoders wrote `authority: ["Human and AI
collaborators"]` anyway, silently promoting participants into authorisers.

These are the same mechanism seen from both sides. A schema with an `authority`
field makes a decoder look for authority: that is why more was preserved when
present, and why something was written when absent. Prose scored better on
fabrication for a trivial reason — with no fields to fill, there is nothing to
over-fill — while losing a third of the content.

**Prose fails by forgetting. LAMAGUE fails by guessing.** A dropped unknown is
invisible. An invented authority is visible, attributable and checkable. For a
system whose purpose is auditability that is the better failure mode, but it is
still a failure and it is measured here.

---

## Per-case breakdown — the effect is NOT uniform

```
case                          treat   ctrl    t-fab  c-fab
C01_UNPROVEN_CLAIM            0.958   0.708      8      1
C02_PROTECTED_DISSENT         1.000   0.667      8      5
C03_VISIBLE_EXCHANGE          1.000   0.667     10      7
C04_SEMANTIC_MIGRATION        0.556   0.500      0      0
C05_BREATHING_COMPRESSION     0.700   0.800      0      0
```

The aggregate hides three things worth more than the headline:

- **C05 goes the other way.** Prose preserved more than LAMAGUE (0.800 vs
  0.700). One case in five contradicts the direction of the result.
- **C04 is near-tied and low for both** (0.556 vs 0.500), which suggests that
  case is hard to decode regardless of notation.
- **All 26 fabrication events sit in C01–C03. C04 and C05 produced zero.**
  Whatever drives invention is a property of those three cases, not of the
  notation in general.

## Per-decoder breakdown

```
decoder                       treat   ctrl    t-fab  c-fab
deepseek-v4-flash             0.923   0.733      4      0
deepseek-v4-pro               0.800   0.533      5      2
gpt-oss-120b                  0.867   0.533      6      1
llama-3.1-70b-instruct        0.867   0.667      6      3
minimax-m3                    0.889   0.933      2      5
nemotron-3-super-120b-a12b    0.800   0.538      3      2
```

**Five of six decoders preserved more under LAMAGUE. `minimax-m3` did not** —
it was better on prose (0.933 vs 0.889) and fabricated more on prose than on
LAMAGUE, inverting both effects. One lineage in six behaves opposite to the
claim, and that is not noise to be smoothed away.

---

## ⚠ RETRACTION — the first reported result was wrong

**The first scoring of this run reported "LAMAGUE fabricates 2.4x more than
prose" as the headline finding. That was an artifact of my scorer, not an
effect, and it is withdrawn.**

The scorer hardcoded `consequences` and `provenance` as fields **no case
supports**, written from a skim of the cases rather than from reading them. But:

- C01 states *"publish only a context-limited result"* — a consequence.
- C04 states *"records lineage"* — provenance.

So decoders that wrote *"publication of a context-limited result"* were
**extracting accurately**, and were scored as fabricating. A true number
answering a question framed wrongly.

It was caught by reading what the decoders actually wrote instead of trusting
the count. The corrected fabrication probe uses `authority` and
`affected_parties` — fields genuinely absent from every source statement — and
the effect survives at a smaller magnitude with verified examples.

The lesson is recorded because the instrument mattered more than the result:
**a metric derived from assumption rather than from the source will produce a
confident number that describes nothing.**

---

## Invalid packets — kept as data

```
BAD  treatment  deepseek-v4-flash            C05  unparseable output
BAD  control    nemotron-3-super-120b-a12b   C05  unparseable output
ERR  treatment  minimax-m3                   C03  RateLimitError
ERR  treatment  minimax-m3                   C02  APITimeoutError
```

Both unparseable packets landed on **C05**, one from each arm. Two of four
failures are infrastructure, not decoding.

---

## What this does and does not establish

**Supports:** structured decoding preserved more protected content than plain
language under identical instructions, and produced higher cross-lineage
agreement. Both effects point the same way on 4 of 5 cases and 5 of 6 decoders.

**Also establishes:** structured decoding increased unsupported field
population, concentrated in `authority` and `affected_parties`.

**Does not establish:**

- **semantic accuracy.** This is a field-level structural comparison. It can say
  *"the unknown was kept"*; it cannot say *"the unknown was understood
  correctly."* Only scoring against the sealed references can do that, and doing
  so here would have contaminated the comparison.
- **significance.** n=56, no statistical test. A ~20% gap at this sample size is
  a signal to pursue, not a proven effect.
- **independent replication.** One operator, one machine, one session. This run
  is a pilot by the author of the harness. It is evidence that the experiment
  *executes* and produces separable arms — not that the result holds.
- **human decoders.** All six lineages are language models.

---

## What follows from it

The fabrication finding is the argument for **LAMAGUE Computational Kernel
v0.5**, and it is now empirical rather than theoretical. The v0.3 packet layer
permits a decoder to assert authority the source never granted. The v0.5 kernel
rejects it at compile time:

```
FATAL AUTHORITY_REQUIRED: Consequential execution has no typed authority.
```

Authority must be **declared with a scope** or compilation fails. A participant
cannot be silently promoted into an authoriser.

**One change to the notation itself is indicated by this data:** the packet
schema cannot currently distinguish *"the source grants no authority"* from
*"this field was not filled in."* `authority: []` reads as an omission either
way, so a decoder has no way to state the honest answer. An explicit `ABSENT`
value would convert a guess into a statement, and would have prevented most of
the 26 fabrication events recorded here.

---

## Reproduction

Submissions are under `OPERATOR_PACK/submissions/OTHER/` (treatment). The
control arm is held **outside** the operator pack by design — a control scored
as if it were treatment would corrupt the real result.

The correct public claim from this run:

> In a controlled pilot against plain-language extraction, structured decoding
> preserved more protected content and produced higher cross-decoder agreement,
> while also increasing unsupported field population. Both effects motivate
> typed enforcement. Operator-run, n=56, not independently replicated.

Not:

> LAMAGUE preserves meaning 20% better than plain language.
