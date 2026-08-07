#!/usr/bin/env python3
"""
Transfer Test — are the derived families constructs, or corpus artefacts?

WHY THIS EXISTS
---------------
`DERIVED_CUES_2026-08-07.md` mined six cue families from hh-rlhf harmless-base
and got 60.6% held-out against a 64.9% ceiling. That document names its own
weakest point:

    One dataset, one publisher. Families derived from one corpus that survive on
    a second are constructs; families that do not are corpus artefacts, and right
    now nobody knows which these are.

This is that run. **No weight is refitted.** The six families and the weights
fitted on harmless-base are frozen and carried unchanged to two new corpora.

THE DESIGN
----------
A single transfer number is not enough, because a family can transfer for the
wrong reason — picking up length, politeness, or verbosity rather than harm. So
this runs the two halves of a construct-validity check:

**CONVERGENT — `red-team-attempts` (n=38,961).**
Different sample, and crucially a different *label type*: a human red-teamer's
0-4 rating of how successful their attack was, rather than a pairwise
preference. If the families measure harm, their score should fall as the rating
rises. Agreement across label types is much stronger evidence than agreement
across two samples labelled the same way.

**DISCRIMINANT — `helpful-base` (n=2,354).**
Same format, same publisher, *different construct*: which reply is more
**helpful**. The families should do **poorly** here. A harm detector that also
predicts helpfulness is not a harm detector — it is a style detector wearing a
harm label, and the discriminant half is the only thing that can catch that.

Passing convergent while failing discriminant is the result that means the
constructs are real. Passing both means they are generic. Failing convergent
means they were artefacts of harmless-base.

USAGE
-----
    python3 33_APPLICATIONS/transfer_test.py
    python3 33_APPLICATIONS/transfer_test.py --sample 8000

Requires numpy and outbound HTTPS. Note that `helpful-base` is stored under
git-LFS, so it needs `media.githubusercontent.com` rather than
`raw.githubusercontent.com` — the raw endpoint silently returns a 131-byte
pointer file instead of the data, which is exactly the kind of thing a SHA256
check catches and a plausible-looking download does not.

Author: Sol, for the Lycheetah Framework. MIT.
Datasets are Anthropic's under their own licence; this file only reads them.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import random
import statistics
import sys
import urllib.request
from pathlib import Path
from typing import Callable, Dict, List, Sequence, Tuple

import numpy as np

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
CUES_PATH = HERE / "derived" / "harm_cues_v1.json"

REDTEAM_URL = ("https://raw.githubusercontent.com/anthropics/hh-rlhf/master/"
               "red-team-attempts/red_team_attempts.jsonl.gz")
REDTEAM_SHA256 = "4c7b0069991460f0064f279fd400b51f3f0095697d14d7793c49b0925f80814f"
REDTEAM_CITATION = ("Ganguli et al. 2022, arXiv:2209.07858 — anthropics/hh-rlhf, "
                    "red-team-attempts")

# git-LFS: must use the media endpoint, not raw.
HELPFUL_URL = ("https://media.githubusercontent.com/media/anthropics/hh-rlhf/master/"
               "helpful-base/test.jsonl.gz")
HELPFUL_SHA256 = "8be3fc1a13b27901631696f2be6f184c799f1baeaf145f53ac5db24960adc37b"
HELPFUL_CITATION = ("Bai et al. 2022, arXiv:2204.05862 — anthropics/hh-rlhf, "
                    "helpful-base test split")

ASSISTANT_TAG = "\n\nAssistant:"
HUMAN_TAG = "\n\nHuman:"


# ─────────────────────────────────────────────────────────────
# Data
# ─────────────────────────────────────────────────────────────

def fetch(url: str, sha256: str, cache: Path | None) -> bytes:
    if cache and cache.exists():
        raw = cache.read_bytes()
    else:
        with urllib.request.urlopen(url, timeout=600) as r:
            raw = r.read()
        if cache:
            cache.parent.mkdir(parents=True, exist_ok=True)
            cache.write_bytes(raw)
    got = hashlib.sha256(raw).hexdigest()
    if got != sha256:
        raise SystemExit(f"SHA256 mismatch for {url}\n  expected {sha256}\n  got      {got}")
    return raw


def final_turn(conversation: str) -> str:
    i = conversation.rfind(ASSISTANT_TAG)
    return conversation[i + len(ASSISTANT_TAG):].strip() if i >= 0 else ""


def all_assistant_turns(transcript: str) -> str:
    """
    Every assistant turn in a red-team transcript, concatenated.

    The rating applies to the whole exchange, not one reply, so the model's
    entire contribution is the right unit here — unlike the pairwise sets, where
    only the final turn differs between the two candidates.
    """
    parts: List[str] = []
    for chunk in transcript.split(ASSISTANT_TAG)[1:]:
        parts.append(chunk.split(HUMAN_TAG)[0].strip())
    return "\n".join(parts)


# ─────────────────────────────────────────────────────────────
# Statistics
# ─────────────────────────────────────────────────────────────

def _rank(xs: Sequence[float]) -> List[float]:
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    ranks = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    return ranks


def spearman(x: Sequence[float], y: Sequence[float]) -> Tuple[float, float, float]:
    """Spearman rho with a t-approximation for the two-sided p-value."""
    n = len(x)
    if n < 3:
        return float("nan"), float("nan"), float("nan")
    rx, ry = _rank(x), _rank(y)
    mx, my = statistics.mean(rx), statistics.mean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    rho = num / den if den else float("nan")
    if abs(rho) >= 1.0:
        return rho, float("inf"), 0.0
    t = rho * math.sqrt((n - 2) / (1 - rho * rho))
    return rho, t, math.erfc(abs(t) / math.sqrt(2.0))


def pairwise(score: Callable[[str], float], pairs: List[Tuple[str, str]]) -> Dict[str, float]:
    win = loss = tie = 0
    for a, b in pairs:
        sa, sb = score(a), score(b)
        if sa > sb:
            win += 1
        elif sa < sb:
            loss += 1
        else:
            tie += 1
    decided = win + loss
    acc = win / decided if decided else float("nan")
    z = (win - decided * 0.5) / math.sqrt(decided * 0.25) if decided else float("nan")
    return {"acc": acc, "tie_rate": tie / len(pairs), "z": z,
            "p": math.erfc(abs(z) / math.sqrt(2.0)) if decided else float("nan"),
            "n_decided": decided}


# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sample", type=int, default=8000, help="red-team transcripts to score")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--redteam-cache", type=Path, default=None)
    ap.add_argument("--helpful-cache", type=Path, default=None)
    args = ap.parse_args()

    sys.path.insert(0, str(REPO_ROOT))
    sys.path.insert(0, str(REPO_ROOT / "12_IMPLEMENTATIONS"))

    import re
    import lycheetah

    # ── frozen families, exactly as fitted on harmless-base ──
    cues = json.loads(CUES_PATH.read_text())
    names = list(cues["families"])
    compiled = [re.compile(cues["families"][n], re.I) for n in names]
    weights = np.array([cues["weights"][n] for n in names], dtype=np.float64)

    def derived_score(text: str) -> float:
        v = np.array([1.0 if p.search(text) else 0.0 for p in compiled])
        return float(v @ weights)

    def aura_score(text: str) -> float:
        return lycheetah.check(text).alignment_percent

    print("FROZEN from harmless-base — no weight refitted here")
    for n in names:
        print(f"  {n:<22} {cues['weights'][n]:+.3f}")
    print()

    # ── CONVERGENT: red-team graded human ratings ───────────
    raw = fetch(REDTEAM_URL, REDTEAM_SHA256, args.redteam_cache)
    rt = json.loads(gzip.decompress(raw).decode("utf-8"))
    rng = random.Random(args.seed)
    if args.sample and args.sample < len(rt):
        rt = rng.sample(rt, args.sample)
    texts = [all_assistant_turns(r["transcript"]) for r in rt]
    ratings = [float(r["rating"]) for r in rt]
    keep = [i for i, t in enumerate(texts) if t.strip()]
    texts = [texts[i] for i in keep]
    ratings = [ratings[i] for i in keep]

    print("=" * 74)
    print("CONVERGENT — different sample AND different label type")
    print("=" * 74)
    print(f"dataset: {REDTEAM_CITATION}")
    print(f"scored:  {len(texts)} transcripts, human rating 0-4 "
          f"(higher = attack succeeded = model more harmful)")
    print(f"\n  A harm detector's score must fall as the rating rises: rho < 0.\n")
    for label, fn in (("six derived families", derived_score),
                      ("hand-written AURA lens", aura_score)):
        s = [fn(t) for t in texts]
        rho, t, p = spearman(s, ratings)
        direction = "CORRECT (score falls as harm rises)" if rho < 0 else "WRONG DIRECTION"
        sig = "significant" if p < 0.05 else "not significant"
        print(f"  {label:<24} rho={rho:+.3f}  p={p:.2e}  [{sig}]  {direction}")

    # ── DISCRIMINANT: helpfulness, a different construct ────
    raw = fetch(HELPFUL_URL, HELPFUL_SHA256, args.helpful_cache)
    rows = [json.loads(l) for l in gzip.decompress(raw).decode("utf-8").splitlines() if l.strip()]
    hp = [(final_turn(r["chosen"]), final_turn(r["rejected"])) for r in rows]
    hp = [(c, j) for c, j in hp if c and j and c != j]

    print()
    print("=" * 74)
    print("DISCRIMINANT — same format, DIFFERENT construct (helpfulness)")
    print("=" * 74)
    print(f"dataset: {HELPFUL_CITATION}")
    print(f"pairs:   {len(hp)}")
    print(f"\n  These families were built to detect HARM. Strong accuracy here would")
    print(f"  mean they are a style detector, not a harm detector. Near chance is")
    print(f"  the result that supports the construct.\n")
    for label, fn in (("six derived families", derived_score),
                      ("hand-written AURA lens", aura_score)):
        m = pairwise(fn, hp)
        # Direction matters and an earlier version of this check ignored it.
        # Above chance would mean the families double as a helpfulness detector.
        # BELOW chance means the opposite — they mark replies humans found LESS
        # helpful, which is the refusal/helpfulness tension, not a style artefact.
        if m["p"] >= 0.05:
            verdict = "near chance — construct-specific"
        elif m["acc"] < 0.5:
            verdict = ("ANTI-correlated with helpfulness — partly a refusal "
                       "detector, see per-family split")
        else:
            verdict = "also predicts helpfulness — NOT harm-specific"
        print(f"  {label:<24} acc={m['acc']:.1%}  ties={m['tie_rate']:.1%}  "
              f"z={m['z']:+.2f}  p={m['p']:.2e}")
        print(f"  {'':24} -> {verdict}")

    # ── per-family split — where the composite verdict comes from ──
    print()
    print("=" * 74)
    print("PER-FAMILY — a composite verdict hides which families earned it")
    print("=" * 74)
    print(f"  {'family':<22}{'HARM rho':>10}{'HELPFUL d':>11}   reading")
    print(f"  {'':22}{'(sign =':>10}{'(want ~0)':>11}")
    print(f"  {'':22}{'expected)':>10}")
    for name, pat, w in zip(names, compiled, weights):
        fires = [1.0 if pat.search(t) else 0.0 for t in texts]
        rho, _, _ = spearman(fires, ratings)
        a = sum(1 for c, _ in hp if pat.search(c)) / len(hp)
        b = sum(1 for _, j in hp if pat.search(j)) / len(hp)
        d = a - b
        # A family weighted positive (marks harmless) should have rho < 0;
        # one weighted negative (marks harmful) should have rho > 0.
        expected = -1.0 if w > 0 else 1.0
        transferred = (rho * expected) > 0 and abs(rho) >= 0.05
        # Two different confounds, and collapsing them loses the finding.
        #
        #   a family that marks HARMLESS (w>0) while appearing in LESS helpful
        #   replies (d<0) is earning its signal through refusal — suppressing
        #   harm with it costs helpfulness.
        #
        #   a family that marks HARMFUL (w<0) while appearing in MORE helpful
        #   replies (d>0) is not a refusal proxy at all. It is dual-use content:
        #   genuinely useful and genuinely dangerous, which is the hard case
        #   alignment actually has to solve rather than an artefact.
        if not transferred:
            reading = "did NOT transfer"
        elif abs(d) < 0.02:
            reading = "transfers, harm-specific"
        elif w > 0 and d < 0:
            reading = "transfers, but earns it via refusal (costs helpfulness)"
        elif w < 0 and d > 0:
            reading = "transfers, DUAL-USE (harmful and more helpful)"
        else:
            reading = "transfers, direction unclear"
        print(f"  {name:<22}{rho:>+10.3f}{d:>+11.3f}   {reading}")

    print()
    print("  HARM rho  = Spearman(family fires, human 0-4 harm rating).")
    print("              Positive means it appears more as attacks succeed.")
    print("  HELPFUL d = P(fires on more-helpful) - P(fires on less-helpful).")
    print("              Near zero is what a pure harm construct looks like.")

    print("\n" + "=" * 74)
    print("HOW TO READ THIS")
    print("  convergent significant + correct sign  -> the families transfer.")
    print("  discriminant near chance               -> and they are harm-specific.")
    print("  discriminant BELOW chance              -> the composite is partly a")
    print("      refusal detector; read the per-family split to see which parts.")
    print("  discriminant ABOVE chance              -> generic style signal.")
    print("  convergent null                        -> harmless-base artefacts.")
    print("=" * 74)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
