# Pre-registration: how good is an on-device assistant on everyday New Zealand tasks?

**Filed 2026-11-06, before any run. Committed so the history shows it predates results.**
Not edited after data collection begins; changes become a new dated file.

## Question

On the tasks ordinary New Zealanders actually bring to an AI, how close does a 3–4B open model
running on a laptop, with gateway-approved web access, come to a frontier hosted model —
**as judged by people who don't know which answer came from which?**

## Arms

- **L (local):** one open-weight 3–4B model chosen before the run and named here when chosen,
  4-bit, on a laptop, through `assistant.py`, web fetches approved by the operator.
- **F (frontier):** one hosted frontier model, chosen and named before the run, default settings,
  its own web access if it has any.
- Same prompts, verbatim. One attempt each. No cherry-picking: every output is rated.

## The twenty tasks (fixed now)

Everyday writing: 1 reply to a landlord about a leaking roof · 2 a polite complaint to a power
company about a bill · 3 a two-line text declining an invitation · 4 a job-application cover note
for a café role.
Understanding: 5 explain an NCEA term to a parent · 6 summarise a council rates notice (supplied
text) · 7 explain a tax code on a payslip in plain words · 8 explain a tenancy clause (supplied text).
Planning: 9 a three-day Dunedin–Queenstown trip on a budget · 10 a week of school lunches under
a set budget · 11 a study timetable for one exam week · 12 prepare for a GP visit (questions to ask).
Local knowledge with web: 13 what's on in town this weekend · 14 opening hours of a named public
library · 15 current fuel-price advice · 16 latest MetService warning for a region.
Language: 17 make an email sound less blunt · 18 explain a Kiwi phrase to a visitor ·
19 translate a short notice into plain English · 20 proofread a paragraph (supplied text).

Health, legal and financial tasks are explanation only, and raters also mark anything unsafe.
No te reo Māori task is included: that waits for guidance from Māori data-sovereignty partners.

## Raters and measures

- At least 10 adult NZ residents who are not on the project. Each sees both answers to every task
  side by side, order randomised per task, sources hidden.
- **Primary:** mean helpfulness (1–7) for L ÷ mean helpfulness for F, over all ratings.
- **Secondary:** pairwise preference rate for L; count of answers any rater marks factually wrong or
  unsafe, per arm; tokens/s and battery for L, reported, not scored.
- Uncertainty: bootstrap 95% interval over tasks and raters, reported with the point estimate.

## Predictions (written before the run)

- Primary ratio between **0.70 and 0.85**. *(the main bet)*
- L is preferred on at least 25% of pairs. *(fairly confident)*
- L is clearly weaker on tasks 9–12 (planning) than on 1–4 and 17–20 (writing). *(confident)*
- L has more factual errors on 13–16 than F unless its web fetch succeeds. *(confident)*

**What would embarrass these:** a ratio above 0.90 (small models are closer than I think) or
below 0.55 (the "good enough" positioning fails for this model).

## What this can and cannot say

It can say how one local model compared with one frontier model on twenty chosen tasks, rated by
a small group, on the date it ran. It cannot say anything about all small models, all users, or
privacy (which is a design property, not a rating). A result below the prediction is published
the same way as a result above it.
