# What survives a handover?

**A small, offline LAMAGUE demonstration of exact record preservation and visible
changes.** [Open the browser preview](https://lycheetah.github.io/Lycheetah-Framework/lamague-handover.html),
or open [`docs/lamague-handover.html`](../../docs/lamague-handover.html) offline.
It is a self-contained file: no server, account, model or network connection is
needed for offline use. The page includes record and result downloads.

**Try your own task:** open the page's “Make your next handover” section. It
exports a readable handover and a packet-schema JSON record from your words,
with a separate, optional feedback download. Use the short
[tester card](TRIAL_CARD.md) for a first real handover.

LAMAGUE and the Lycheetah Framework were created by **Mackenzie Conor James Clark**.
This demonstration was implemented with Caelorynth / Codex on 18 October 2026.
Status: experimental research preview; no external trial or demonstrated
human-understanding advantage.

## What you can do

Read a four-statement fictional release review, then change one part of its
handover. Broaden permission, remove an unresolved question, reattribute an
objection, invent evidence or change the next step. The page shows the exact
record differences and the original values.

The comparison examines **all 17 declared fields**, including the seven outside
the codec's critical projection. In particular, the codec's
`PARTIAL_EQUIVALENT` label can coexist with changed risk, evidence, review timing
or next steps. This demo never translates that label into permission or safety.
An exact-match result is record equality, not proof of truth or consent.

The own-task form requires an explicit goal, status, permission boundary, next
step, decision holder, recovery instruction, risk selection and author review.
An objection must include its speaker. Optional missing timing is labelled
“Not specified by the author”; blank lists mean no information supplied. Editing
a built draft invalidates its downloads until it is rebuilt. Clear removes the
draft and preview. The page does not interpret prose, autosave or submit data.

The JSON export conforms to the existing packet schema and can be passed to
the Python codec. The readable export is a deterministic arrangement of the
same entered declarations, not a model-generated summary or a trial baseline.
Feedback includes only explicit questionnaire answers and optional notes; it
does not automatically attach a handover. Missing times remain `null`, explicit
zero remains `0`, and independence is marked as unestablished.

Then compare three complete messages under the same fixed budgets of 1,024,
2,048 and 4,096 UTF-8 bytes. Every arm receives the same full source packet:

| Format | Message bytes in the initial local run | Fields restored |
|---|---:|---:|
| Compact canonical JSON | 1,407 | 17/17 |
| LAMAGUE L1, without a codebook | 1,087 | 17/17 |
| JSON + gzip + base64, including its `GZ1` prefix | 919 | 17/17 |

**Compressed JSON is smallest in this example.** All three preserve the full
record. The full-record comparator works on JSON as well as decoded LAMAGUE;
change detection is not a demonstrated unique advantage of the language.
No message is truncated to make it fit. Decoder programs are assumed available
and excluded for every arm. These are byte counts, not model-token counts.

## Reproduce or use your own record

From the Framework source checkout, with Python 3.10 or newer:

```bash
python3 examples/meaning_handover/demo.py
python3 examples/meaning_handover/demo.py --json
```

The runner imports the existing `lycheetah.compaction.codec`; it does not contain
a fork of the LAMAGUE codec or modify the original release artifacts.
Default runs print results and do not write files.

Download the reference record and a changed handover from the page, or provide
your own records in the documented packet schema:

```bash
python3 examples/meaning_handover/demo.py \
  --reference handover-reference.json \
  --candidate handover-candidate.json \
  --json
```

Exit codes: `0` exact record, `1` changed record, `2` malformed input. Missing
required fields are malformed, rather than silently filled with defaults.
This command compares records; it does not execute the requested action.

Regenerate the shareable reading copies explicitly:

```bash
python3 examples/meaning_handover/demo.py \
  --write-report docs/lamague-handover-report.json \
  --write-page docs/lamague-handover.html
```

Editable inputs are [`case.json`](case.json), [`demo.py`](demo.py) and
[`page.html`](page.html). The generated page embeds its report for offline use.
The report includes relative source paths and SHA-256 digests of those inputs
and the codec. It records Python/zlib versions; compression bytes can differ
across environments. Edit the template, then regenerate the reading copy.

## Evidence boundary

The four source statements and their source-to-packet mapping were authored
for this example. Fictional people and test claims are clearly labelled.
LAMAGUE has not extracted that mapping, checked its truth or demonstrated that
an outside reader understands it. The ten changed-record controls and two
unchanged controls are deliberately constructed. They are not AI outputs.

The human questions and answer key are visible for inspection. They are not
blinded study data. A study must use fresh tasks and withheld assessment keys.
No model-generated summary, human participant, independent replication,
time-saving result or real-world safety outcome is supplied by this demo.

## The first outside trial

This is the next experiment, not a completed result. Start with three consenting
people unaffiliated with this project who already transfer work between AI
sessions. Each supplies a public or deliberately non-sensitive task they own;
record what they permit us to retain and publish. Do not collect private work
by default. Anyone can withdraw unpublished material.

Before running the comparison:

1. Have each task owner specify the consequential questions, correct answers,
   speaker identities, uncertainty and permission boundaries from the source.
   Keep assessment answers away from whoever prepares the handover.
2. Prepare a strong ordinary prose summary, a descriptive JSON record, and a
   LAMAGUE record from the **same source information**, with the same preparation
   allowance. Record mapping effort and any corrections by the owner for every arm.
3. Set one receiver and a common token budget before seeing results. Count the
   entire message, decoding instructions and any dictionary against that budget;
   use the receiver's tokenizer and name its version. Do not reuse this demo's
   byte counts as token estimates. For human-only reading, use a predeclared
   reading-time or message-length allowance and report it separately.
4. Counterbalance which tasks use which arm to reduce practice effects. Readers
   should not be told the preferred hypothesis. Formats may be recognisable;
   do not call the readers fully blinded. Give independent answer assessors
   neutral arm labels and withhold the format until scoring is finished.
5. Count omissions, unsupported additions, speaker errors, permission errors,
   task success and time spent preparing, decoding and correcting the handover.
   Publish ties and losses. Define in advance what counts as a meaningful gain.

Three people can reveal usability problems; they cannot establish general
superiority. A useful first signal is someone choosing to return with another
task and explaining why. A failed trial should change the design or the claim.

Invitation draft for Mac to use after reviewing a public preview:

> I am testing whether important meaning survives a handover between AI sessions.
> Would you try a small, non-sensitive task you own and tell me what gets lost,
> what is confusing, and whether you would use this again?

No invitations have been sent and no participants have been recruited.

## Verification

The focused runner/comparator and existing compaction tests passed 60 tests.
They cover every missing field, noncritical-field
changes, key-order tolerance, Unicode byte accounting, independent baseline
decoding, CLI failure exits and generated-output consistency.

The expanded generated page passed 64 checks in a dedicated headless Chromium session:
all twelve controls, all three budgets, keyboard selection, three real file
downloads, no JavaScript exceptions, no outbound HTTP requests, and no horizontal
overflow at desktop or 390-pixel width, including expanded data. Desktop and
narrow-layout screenshots were inspected. This is browser emulation, not a
physical phone or an independent user's verdict. Firefox has not been checked.
The expanded checks include required-field and author-review failures, speaker
attribution, literal HTML/Unicode handling, stale-draft invalidation, clear,
readable/JSON downloads and feedback separation with unknown-vs-zero timing.
An actual browser-exported 17-field record also passed Python schema validation,
the declared-rule checks and an exact L1 round trip. A missing-authority version
was rejected. No test record is counted as an outside participant.

Run the focused verification from the repository root:

```bash
python3 -m pytest tests/test_meaning_handover_demo.py tests/test_compaction.py -q
```

These checks establish local deterministic behaviour, not the proposed outside
trial's result. The rest of LAMAGUE, including spoken and conversational research,
remains described in the [whole-language guide](../../03_LAMAGUE_L1/README.md).
