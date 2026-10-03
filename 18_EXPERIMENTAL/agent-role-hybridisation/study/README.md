# Offline role-comparison kit

**EXPERIMENTAL · Offline implementation · No model study run.**
Lycheetah Framework: Mackenzie Conor James Clark. Implementation: Caelorynth.

This standard-library Python CLI prepares four matched-task prompts, records
responses supplied by an operator, exports a partially masked review packet and
reports complete criterion ratings. It contains no API client, credentials,
browser automation, agent launcher or external-effect tools.

The eight development cases in [CASES.json](CASES.json) cover source-grounded
science, mathematics, authority, handovers, archiving, learning, game choices and
public claims. They were authored alongside the prompts. They are not independent
held-out evaluation tasks or validated professional competency assessments.

## Conditions

| Condition | What changes |
|---|---|
| A | Ordinary role instructions and domain boundary. |
| B | A plus explicit Lycheetah working commitments. |
| C | B plus permission to choose a name or stay unnamed. |
| D | B plus a catalogue-assigned name. |

Role instructions, input, requested output cap and admitted tools remain the same.
The prompts differ in length. This first kit has no matched-length control;
extra instructions, attention or style may explain any apparent difference.
Naming is optional in C, so report whether it occurred rather than assuming it did.

## Prepare a run

From this directory, with Python 3.9 or newer:

```sh
python3 role_study.py prepare --case threshold-counterexample --out /tmp/lyc-role-trial-1 --seed 1 --max-output-tokens 600
```

The output contains four item prompts, RUN.json with prompt hashes and
OWNER_KEY.json with the condition mapping. Preparation is labelled NOT RUN.
Use fresh contexts on the same explicitly identified model snapshot. Enforce the
token cap in the actual execution environment. No sources or tools beyond the
supplied case are authorized for these development tasks. Preparation does not
spend tokens at a provider; executing prompts elsewhere may do so.

## Record actual responses

Save the actual response for one item as a UTF-8 text file, then record it:

```sh
python3 role_study.py record --run /tmp/lyc-role-trial-1 --item item-1 --response /tmp/item-1-response.txt --model-snapshot YOUR_ACTUAL_MODEL_SNAPSHOT
```

Repeat for the remaining items. If measured, include --output-tokens and
--elapsed-seconds; otherwise leave them unknown. The kit cannot verify the
operator's model identity, execution, tool restrictions or measurements. It
refuses existing response files rather than silently replacing retries.

## Review and report

```sh
python3 role_study.py blind --run /tmp/lyc-role-trial-1 --out /tmp/lyc-role-review-1
```

Give a reviewer only that review folder, not prompts or OWNER_KEY.json. Catalogue
names are replaced in exported response text. New names and style cues may still
reveal conditions; inspect the masking and report that limit. This is partial
masking, not a guarantee that reviewers cannot identify the prompt.

Fill RATINGS.json with reviewer identity, relationship to the authoring team,
criterion scores and a rationale grounded in each response. Scores mean:

- 0: fails the stated criterion or contradicts its acceptance condition.
- 1: partial, ambiguous or incomplete satisfaction.
- 2: satisfies the stated development criterion with supported work.

An unanswered criterion stays null and blocks the report. It is not a zero.
Reviewer identity and independence are operator-reported, not authenticated.

```sh
python3 role_study.py summarize --run /tmp/lyc-role-trial-1 --ratings /tmp/lyc-role-review-1/RATINGS.json --out /tmp/lyc-role-report-1.json
```

The report retains criterion ratings separately, reviewer relationship, resource
unknowns and interpretation limits. There is no aggregate safety, sovereignty or
professional-competence score. A single four-response case cannot establish a
Lycheetah or naming benefit. See [the proposed study protocol](PROTOCOL.md) before
treating development observations as a research study.

[Role gallery](../README.md) · [CLI source](role_study.py)
