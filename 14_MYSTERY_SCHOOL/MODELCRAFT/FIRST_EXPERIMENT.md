# Make a checklist you can actually use

Begin with one small artifact: a build checklist for a personal project.
You can do the planning on paper. To compare model behavior, use a tool you already
have permission to use and record its actual cost. No paid API is required by the lesson.

## 1. Name the result

Use this fictitious project so there are no private files to upload:

> I want a browser timer for short study sessions. Make a build checklist.

Before trying either request, define your acceptance rubric:

- It covers start, pause and reset.
- The user can choose 5, 10 or 20 minutes.
- It works offline after loading, with no account or tracking.
- Controls have accessible labels and keyboard support.
- It gives a concrete way to check each requirement.

Also count unsupported assumptions: a backend, subscriptions, social feeds or
other requirements you did not request. Do not change the rubric to favor an output.

## 2. Compare two requests

**Baseline:** give the project sentence above and ask for a checklist of at most
eight items. Save the output unchanged.

**Context-pack treatment:** give the same sentence and output limit, followed by:

```text
PROJECT FACTS
One HTML file, for one person, opened in a browser.
Start, pause and reset; choices of 5, 10 and 20 minutes.
No server, account, tracking or online dependency after loading.
Accessible controls with keyboard support.

DELIVERABLE
At most eight checklist items, each with an observable verification step.
If a required fact is missing, say so instead of inventing it.
```

Record product, model/version if visible, date, settings and input/output size.
Use the same model and settings and a fresh conversation for each attempt.
Randomize order where practical. Set the same total allowance for retries and
output, and count the extra context as treatment cost. If budgets cannot be matched,
record that limitation. Never claim the comparison held cost constant when it did not.

## 3. Inspect the artifacts

Score against the declared rubric. If possible, label the outputs A and B and
score before checking which request made each. Record correct constraints,
unsupported assumptions, usable verification steps, cost and time.

No improvement is an acceptable result. One run is a small observation, not proof
of a universal technique. Repeat on a different project before relying on transfer.
Use private, invented or explicitly permissioned material in later experiments.

## 4. Change it and make it yours

Edit the best usable checklist yourself. Remove unneeded work. Add one requirement
that matters to you. Keep the earlier version so your decision is inspectable.
The final artifact belongs to your project, not to the School's completion counter.

## 5. Export the recipe

Save a local text file containing your goal, inputs, both requests, unedited outputs,
rubric, observations, failures, settings and budget limits. Begin from the private
[hypothesis receipt](examples/hypothesis.json); populate actual run records only
after trying the experiment. Do not copy the synthetic test records into a claim.

You can leave at any point. Nothing is lost by skipping, disagreeing or deciding
the model was unnecessary. Sharing is a separate choice after privacy and rights review.
