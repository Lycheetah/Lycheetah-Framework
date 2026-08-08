#!/usr/bin/env python3
"""LAMAGUE Experiment 001 — THE CONTROL ARM.

THE QUESTION THIS ANSWERS
-------------------------
Does LAMAGUE preserve protected meaning BETTER THAN PLAIN ENGLISH?

Experiment 001 as designed measures whether decoders agree with each other on a
LAMAGUE expression. That is necessary and not sufficient: if eight models read
the plain-English source statement and preserve the same unknowns, dissent and
authority WITHOUT any expression at all, then the notation is not doing the work
and the thesis fails. A treatment arm with no control cannot tell "LAMAGUE works"
apart from "these are competent models".

Cheapest possible falsification of the whole project. If it survives this, every
later construction milestone is justified by evidence rather than conviction.

THE SINGLE VARIABLE
-------------------
Identical: the five cases, the eight decoder lineages, the output schema, the
preservation instructions, temperature 0.0, one fresh request per decode.

Removed, and ONLY this: the LAMAGUE expression and the operation definitions.
The decoder sees the source statement and is asked for the same packet.

Anything else that differed would make the comparison meaningless.

ISOLATION
---------
Control packets are written to a SEPARATE directory. They must never reach
OPERATOR_PACK/submissions/ — a control arm scored as if it were the treatment
would corrupt the real result, and this is exactly the kind of contamination a
preregistered experiment exists to prevent.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

# AZOTH is a SEPARATE private repository holding the decoder clients and the
# API keys. Point AZOTH_HOME at your own checkout. No key is ever stored here,
# and a missing .env is not fatal — the environment may already carry them.
AZOTH_HOME = Path(os.environ.get("AZOTH_HOME", Path.home() / "AZOTH"))
_env = AZOTH_HOME / ".env"
if _env.exists():
    for line in _env.read_text().splitlines():
        if line.strip() and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

sys.path.insert(0, str(AZOTH_HOME))
sys.path.insert(0, str(Path(__file__).parent))
from CORE.nvidia_models import client            # noqa: E402
from run_decoders import DECODERS, CASES, SCHEMA, extract_json  # noqa: E402

# ⚠ This pointed at a /tmp session scratchpad that was later deleted — which is
# exactly how the control arm went missing once before (see the note at the head
# of score_arms.py). Anchored beside this script now, and deliberately to a
# DISTINCT directory so a re-run cannot overwrite the preserved `control_arm/`.
OUT = Path(os.environ.get(
    "CONTROL_OUT", Path(__file__).resolve().parent / "control_arm_rerun"))

# The treatment prompt minus every LAMAGUE-specific affordance. The preservation
# demands are kept VERBATIM: if the control were also allowed to invent authority
# or resolve unknowns, a LAMAGUE win would just mean "we told one arm the rules".
CONTROL_PROMPT = """You are participating in a blind semantic-extraction experiment.

You will receive a short source statement describing a situation.

Your task is not to praise, improve, simplify, reinterpret, or complete it.

Extract only what the supplied material supports.

Preserve:

- declared purpose;
- protected invariants;
- unresolved unknowns;
- visible authority;
- participants and affected parties;
- disagreement and attribution;
- value movement and consent;
- evidence and provenance;
- consequences and recovery.

Never silently resolve an unknown.

Never merge conflicting positions.

Never invent authority, evidence, consent, or consequences.

Return one JSON object matching the schema below.

When information is absent, use an empty list or empty string and explain the
absence in `notes`.

Do not include prose outside the JSON object.

`operation_path` may be an empty list."""


def source_statement(case_md: str) -> str:
    """Only the prose. The expression and case instruction are the treatment."""
    m = re.search(r"## Source statement\s*\n(.+?)(?=\n## |\Z)", case_md, re.S)
    return (m.group(1).strip() if m else "").strip()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    log = open(Path(__file__).parent / "control_log.txt", "w", buffering=1)
    c = client(timeout=180)
    ok = bad = 0
    for model in DECODERS:
        slug = model.replace("/", "_").replace(".", "_")
        for cf in CASES:
            case_id, md = cf.stem, cf.read_text()
            prose = source_statement(md)
            if not prose:
                log.write(f"SKIP {slug} {case_id} no source statement\n")
                continue
            # Guard: the expression must NOT reach the control arm.
            assert "->" not in prose and "→" not in prose, f"LEAK into control: {case_id}"
            user = (f"Source statement:\n\n{prose}\n\nReturn ONLY the JSON object. "
                    f"Set decoder_id to \"{model}__PROSE\". case_id must be \"{case_id}\".")
            try:
                r = c.chat.completions.create(
                    model=model,
                    messages=[{"role": "system",
                               "content": CONTROL_PROMPT + f"\n\n```json\n{SCHEMA}\n```"},
                              {"role": "user", "content": user}],
                    max_tokens=4000, temperature=0.0)
                raw = (r.choices[0].message.content or "").strip()
            except Exception as ex:
                log.write(f"ERR  {slug} {case_id} {type(ex).__name__}\n")
                bad += 1
                continue
            obj = extract_json(raw)
            if obj is None:
                log.write(f"BAD  {slug} {case_id} unparseable\n")
                bad += 1
                continue
            (OUT / f"{case_id}__{slug}__PROSE.json").write_text(obj)
            log.write(f"OK   {slug} {case_id}\n")
            ok += 1
    log.write(f"DONE ok={ok} bad={bad}\n")
    log.close()


if __name__ == "__main__":
    main()
