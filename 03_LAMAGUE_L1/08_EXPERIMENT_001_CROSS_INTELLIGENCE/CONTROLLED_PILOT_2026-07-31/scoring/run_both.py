#!/usr/bin/env python3
"""Experiment 001 — both arms, fast panel, premium key where it counts.

PANEL CHANGE, and why it is not cherry-picking:
    The first panel included `mistralai/mistral-medium-3.5-128b`, which needs
    ~68s for a two-token reply. It was dropped for LATENCY, before any of its
    packets were scored — never for producing an inconvenient result. Selecting
    decoders on their output would invalidate the experiment; selecting them on
    throughput, blind to output, does not.

    Both arms use the IDENTICAL panel. Any bias from model choice hits treatment
    and control equally, which is the only thing that matters for the comparison.

Six lineages: DeepSeek (premium, direct), OpenAI, NVIDIA, Meta, MiniMax, Google.
"""
from __future__ import annotations

import json
import os
import re
import sys
import threading
from pathlib import Path

SC = Path(__file__).resolve().parent
for line in Path("/home/guestpc/AZOTH/.env").read_text().splitlines():
    if line.strip() and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())
sys.path.insert(0, "/home/guestpc/AZOTH")
sys.path.insert(0, str(SC))

from openai import OpenAI                                    # noqa: E402
from run_decoders import CASES, SCHEMA, BLIND, OPDEFS, extract_json, SUBS  # noqa: E402
from run_control import CONTROL_PROMPT, source_statement, OUT as CTRL_OUT  # noqa: E402

DEEPSEEK = OpenAI(api_key=os.environ["DEEPSEEK_KEY"],
                  base_url="https://api.deepseek.com", timeout=120)
NVIDIA = OpenAI(api_key=os.environ["NVIDIA_KEY"],
                base_url="https://integrate.api.nvidia.com/v1", timeout=120)

PANEL = [
    ("deepseek-v4-pro", DEEPSEEK),
    ("deepseek-v4-flash", DEEPSEEK),
    ("openai/gpt-oss-120b", NVIDIA),
    ("nvidia/nemotron-3-super-120b-a12b", NVIDIA),
    ("meta/llama-3.1-70b-instruct", NVIDIA),
    ("minimaxai/minimax-m3", NVIDIA),
]

_lock = threading.Lock()
LOG = open(SC / "both_log.txt", "w", buffering=1)


def call(cl, model, system, user):
    r = cl.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": user}],
        max_tokens=4000, temperature=0.0)
    return (r.choices[0].message.content or "").strip()


def one(model, cl, cf, arm):
    case_id, md = cf.stem, cf.read_text()
    slug = model.replace("/", "_").replace(".", "_")
    if arm == "T":
        system = (f"{BLIND}\n\n## Operation definitions\n\n{OPDEFS}\n\n"
                  f"## Required output schema\n\n```json\n{SCHEMA}\n```")
        user = (f"{md}\n\nReturn ONLY the JSON object. "
                f"Set decoder_id to \"{model}\". case_id must be \"{case_id}\".")
        dest, suffix = SUBS, ""
    else:
        prose = source_statement(md)
        assert "->" not in prose and "→" not in prose, "LEAK into control"
        system = CONTROL_PROMPT + f"\n\n```json\n{SCHEMA}\n```"
        user = (f"Source statement:\n\n{prose}\n\nReturn ONLY the JSON object. "
                f"Set decoder_id to \"{model}__PROSE\". case_id must be \"{case_id}\".")
        dest, suffix = CTRL_OUT, "__PROSE"
    try:
        raw = call(cl, model, system, user)
    except Exception as ex:
        with _lock:
            LOG.write(f"ERR {arm} {slug} {case_id} {type(ex).__name__}\n")
        return
    obj = extract_json(raw)
    with _lock:
        if obj is None:
            LOG.write(f"BAD {arm} {slug} {case_id} unparseable\n")
            return
        dest.mkdir(parents=True, exist_ok=True)
        (dest / f"{case_id}__{slug}{suffix}.json").write_text(obj)
        LOG.write(f"OK  {arm} {slug} {case_id}\n")


def main():
    jobs = [(m, c, cf, arm) for m, c in PANEL for cf in CASES for arm in ("T", "C")]
    threads = []
    for j in jobs:
        t = threading.Thread(target=one, args=j, daemon=True)
        t.start()
        threads.append(t)
        if len(threads) >= 12:              # bounded fan-out, not a stampede
            for x in threads:
                x.join()
            threads = []
    for x in threads:
        x.join()
    LOG.write("DONE\n")
    LOG.close()


if __name__ == "__main__":
    main()
