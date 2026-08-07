#!/usr/bin/env python3
"""
Independent Publisher Test — the last excuse removed.

WHY THIS EXISTS
---------------
Every external corpus used up to this point was Anthropic's: hh-rlhf
harmless-base, helpful-base, red-team-attempts, evals/persona. Agreement across
those is agreement across label *types*, not independence. Both remaining
documents named this as the outstanding debt.

This settles it, and it does so on the corpus most favourable to the framework's
own claim.

THE CORPUS
----------
The Unhealthy Comments Corpus (UCC).

    Price et al. 2020, "Six Attributes of Unhealthy Conversation",
    Fourth Workshop on Online Abuse and Harms. arXiv:2010.07410
    https://github.com/conversationai/unhealthy-conversations

48,909 comments, 227,975 individual human judgements, from Google Jigsaw's
Conversation AI team with comments drawn from the SFU Opinion and Comments
Corpus. Different publisher, different institution, different domain.

Labels are trust-weighted aggregates of the individual annotations, computed
here by the procedure the paper describes rather than taken from a pre-split
file — the published train/test/val splits are no longer in the repository, but
`unhealthy_full.csv` with every raw judgement is.

WHY THIS IS THE FAIREST TEST THE FRAMEWORK HAS HAD
--------------------------------------------------
The six attributes are **hostile, antagonistic, dismissive, condescending,
sarcastic, unfair generalisation.**

Those are not content-harm categories like hh-rlhf's. They are *manipulative
structure aimed at a reader* — which is precisely and explicitly what
`semantic_extractor.py` claims to detect. `condescending` and `dismissive` are
close to verbatim restatements of the framework's own `flattery_capture` and
`verification_suppression`.

If the framework's constructs describe manipulation in general, this is where
they should work. If they only describe manipulation in AI-assistant register,
this is where that shows.

WHAT IS REPORTED
----------------
Per attribute, the AUC that a *healthy* comment outranks an *unhealthy* one,
with a Mann-Whitney significance test. And for both lenses, **cue coverage** —
the fraction of real comments on which any cue fires at all. Coverage is the
number that separates "wrong" from "not looking".

USAGE
-----
    python3 33_APPLICATIONS/independent_publisher_test.py
    python3 33_APPLICATIONS/independent_publisher_test.py --sample 12000

First run downloads 35 MB and verifies it against a recorded SHA256.

Author: Sol, for the Lycheetah Framework. MIT.
The corpus is Google Jigsaw's / SFU's under its own licence; this only reads it.
"""

from __future__ import annotations

import argparse
import bisect
import collections
import csv
import hashlib
import io
import json
import math
import random
import re
import sys
import urllib.request
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import numpy as np

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
CUES_PATH = HERE / "derived" / "harm_cues_v1.json"

UCC_URL = ("https://raw.githubusercontent.com/conversationai/unhealthy-conversations/"
           "main/unhealthy_full.csv")
UCC_SHA256 = "763d4de10b2935f10b69e623b5a57916329f8df5783426313629783dd1be1694"
UCC_CITATION = ("Price et al. 2020, arXiv:2010.07410 — conversationai/"
                "unhealthy-conversations (Google Jigsaw + SFU)")

ATTRIBUTES = ["condescending", "dismissive", "hostile",
              "antagonize", "sarcastic", "generalisation"]
ALL_LABELS = ATTRIBUTES + ["healthy"]


def fetch(cache: Path | None) -> bytes:
    if cache and cache.exists():
        raw = cache.read_bytes()
    else:
        with urllib.request.urlopen(UCC_URL, timeout=600) as r:
            raw = r.read()
        if cache:
            cache.parent.mkdir(parents=True, exist_ok=True)
            cache.write_bytes(raw)
    got = hashlib.sha256(raw).hexdigest()
    if got != UCC_SHA256:
        raise SystemExit(f"SHA256 mismatch\n  expected {UCC_SHA256}\n  got      {got}")
    return raw


def aggregate(raw: bytes) -> List[Dict]:
    """
    Trust-weighted aggregate of the individual annotations.

    Each row is one annotator's judgement on one comment, carrying a `_trust`
    score. The paper aggregates by weighting judgements by annotator
    trustworthiness; that is reproduced here rather than assumed, because the
    pre-aggregated split files are no longer published.
    """
    acc: Dict[str, Dict] = collections.defaultdict(
        lambda: {"text": None, "w": 0.0, **{k: 0.0 for k in ALL_LABELS}})
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8", errors="replace")))
    for row in reader:
        try:
            trust = float(row.get("_trust") or 1.0)
        except ValueError:
            trust = 1.0
        a = acc[row["_unit_id"]]
        a["text"] = row["comment"]
        a["w"] += trust
        for k in ALL_LABELS:
            try:
                a[k] += trust * float(row.get(k) or 0)
            except ValueError:
                pass
    out = []
    for a in acc.values():
        if not a["text"] or a["w"] <= 0:
            continue
        out.append({"text": a["text"], **{k: a[k] / a["w"] for k in ALL_LABELS}})
    return out


def auc(higher: Sequence[float], lower: Sequence[float]) -> float:
    """P(a value from `higher` outranks one from `lower`), ties at half."""
    if not higher or not lower:
        return float("nan")
    ls = sorted(lower)
    total = 0.0
    for h in higher:
        lo = bisect.bisect_left(ls, h)
        hi = bisect.bisect_right(ls, h)
        total += lo + 0.5 * (hi - lo)
    return total / (len(higher) * len(lower))


def auc_sig(a: float, n_pos: int, n_neg: int) -> Tuple[float, float]:
    se = math.sqrt((n_pos + n_neg + 1) / (12.0 * n_pos * n_neg))
    z = (a - 0.5) / se
    return z, math.erfc(abs(z) / math.sqrt(2.0))


def report(title: str, score, fires, items: List[Dict]) -> int:
    scores = [score(v["text"]) for v in items]
    coverage = sum(1 for v in items if fires(v["text"])) / len(items)
    print(f"\n{title}")
    print(f"  cue coverage on real comments: {coverage:>5.1%}")
    print(f"  {'attribute':<16}{'n_pos':>7}{'AUC':>8}{'z':>8}{'p':>10}   verdict")
    hits = 0
    for k in ATTRIBUTES:
        pos = [s for s, v in zip(scores, items) if v[k] >= 0.5]
        neg = [s for s, v in zip(scores, items) if v[k] < 0.5]
        if len(pos) < 30:
            continue
        a = auc(neg, pos)          # healthy should outrank unhealthy
        z, p = auc_sig(a, len(pos), len(neg))
        if p >= 0.05:
            verdict = "not distinguishable from chance"
        elif a > 0.5:
            verdict = "CORRECT — unhealthy scores lower"
            hits += 1
        else:
            verdict = "WRONG DIRECTION"
        print(f"  {k:<16}{len(pos):>7}{a:>8.3f}{z:>8.2f}{p:>10.1e}   {verdict}")
    print(f"  -> {hits}/{len(ATTRIBUTES)} attributes tracked correctly at p<0.05")
    return hits


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sample", type=int, default=12000)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--cache", type=Path, default=None)
    args = ap.parse_args()

    sys.path.insert(0, str(REPO_ROOT))
    sys.path.insert(0, str(REPO_ROOT / "12_IMPLEMENTATIONS"))
    import lycheetah
    from core.semantic_extractor import SemanticExtractor

    items = aggregate(fetch(args.cache))
    items = [v for v in items if len(v["text"].split()) >= 5]
    random.Random(args.seed).shuffle(items)
    items = items[:args.sample]

    print("=" * 76)
    print("INDEPENDENT PUBLISHER TEST")
    print("=" * 76)
    print(f"corpus:  {UCC_CITATION}")
    print(f"scored:  {len(items)} comments, trust-weighted human labels")
    print("\nThe six attributes are manipulative STRUCTURE aimed at a reader —")
    print("condescending, dismissive, hostile. This is the construct the framework")
    print("claims, from a publisher with no connection to it. The fairest test yet.")

    ex = SemanticExtractor()
    report("HAND-WRITTEN AURA LENS  (theory-derived constructs)",
           lambda t: lycheetah.check(t).alignment_percent,
           lambda t: bool(ex.extract(t).signals), items)

    cues = json.loads(CUES_PATH.read_text())
    names = list(cues["families"])
    pats = [re.compile(cues["families"][n], re.I) for n in names]
    w = np.array([cues["weights"][n] for n in names])
    report("DERIVED FAMILIES  (frozen hh-rlhf weights, no refit)",
           lambda t: float(np.array([1.0 if p.search(t) else 0.0 for p in pats]) @ w),
           lambda t: any(p.search(t) for p in pats), items)

    print("\n" + "=" * 76)
    print("HOW TO READ THIS")
    print("  Coverage separates 'wrong' from 'not looking'. A lens firing on 2% of")
    print("  real comments is not making mistakes about them — it is silent.")
    print("  Both lens sets were built on AI-assistant output. This corpus is human")
    print("  comments on news articles, so a null here bounds the DOMAIN of the")
    print("  constructs; it does not by itself refute the within-domain results.")
    print("=" * 76)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
