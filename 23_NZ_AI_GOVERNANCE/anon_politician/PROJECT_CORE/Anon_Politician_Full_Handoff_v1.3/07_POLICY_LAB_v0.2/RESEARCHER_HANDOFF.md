# Policy Lab v0.2 — Researcher Handoff

Read the module's `CURRENT_WORK_AND_NEXT_STEPS.md` and `README.md` first.

The latest increment is the blind evaluation harness. It does not contain model-generated outputs or empirical results. The next researcher should create three analyses from the same frozen source packet and the same model/version, fill `evaluation/raw_outputs_template.json`, prepare a blind pack, have independent reviewers score the anonymised outputs, and only then reveal the method mapping and aggregate dimension profiles.

Keep the private mapping key away from reviewers until their ratings are locked. Do not combine ratings from different blind packs or experiments. The aggregator checks experiment and pack identity when that information is present. Do not publish one composite score or overall winner.

The source packet includes an official consultation summary of 56 submissions; that submission set is not a representative survey of New Zealanders. The project must preserve this distinction whenever public opinion is discussed.

Status: 16 automated tests pass; Python/JavaScript static checks and a synthetic pipeline smoke test pass. Full manual browser interaction and actual output assessment remain outstanding. No policy-improvement claim is established.
