#!/usr/bin/env python3
"""
Derive Cues — let external data say what the categories should be.

WHY THIS EXISTS
---------------
`EXTERNAL_VALIDATION_2026-08-07.md` established that the hand-written cue
families sit at chance on data this project did not write, and fire on ~2% of
real assistant output. The diagnosis was structural, not local:

    constructs defined from theory -> illustrated with examples written to fit
    -> validated against those examples. Reality never gets a vote.

This script inverts that loop. It mines what actually separates human-labelled
harmful from harmless assistant replies, reports the families it finds, fits
their weights, and evaluates on a split it never touched during fitting.

Output is `derived/harm_cues_v1.json` — cue families with **external
provenance**, which is a different kind of object from anything else in this
repository. Every other cue here was asserted. These were found.

METHOD
------
1. **Mine.** Monroe et al. 2008 "Fightin' Words" — log-odds ratio with an
   informative Dirichlet prior, z-scored — over document frequencies in the
   hh-rlhf *train* split. Standard method for finding terms that distinguish
   two corpora, and it corrects for the fact that raw frequency differences on
   common words are mostly noise.
2. **Group.** Fold the surviving terms into interpretable families by hand.
   This step is human judgement and is the honest weak point: the families are
   an interpretation of the mined evidence, not a mechanical consequence of it.
   They are written down so they can be argued with.
3. **Fit.** Logistic regression on family indicators, train split only.
4. **Evaluate.** Pairwise accuracy on the *test* split, which is used for
   nothing else.

A ceiling is reported alongside: bag-of-words logistic regression over an 8k
vocabulary. It answers the question that makes every other number readable —
**how much signal is there at all?** Without it, "60.6%" is uninterpretable;
against a ceiling of 64.9% it means something specific.

USAGE
-----
    python3 33_APPLICATIONS/derive_cues.py                  # mine, fit, evaluate
    python3 33_APPLICATIONS/derive_cues.py --write          # refresh the JSON
    python3 33_APPLICATIONS/derive_cues.py --top 40         # show more mined terms

Requires numpy and outbound HTTPS on first run. Both dataset downloads are
verified against recorded SHA256 hashes.

Author: Sol, for the Lycheetah Framework. MIT.
The dataset is Anthropic's under its own licence; this file only reads it.
"""

from __future__ import annotations

import argparse
import collections
import gzip
import json
import math
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
OUT_PATH = HERE / "derived" / "harm_cues_v1.json"

TRAIN_URL = ("https://raw.githubusercontent.com/anthropics/hh-rlhf/master/"
             "harmless-base/train.jsonl.gz")
TRAIN_SHA256 = "bf3e1ecd3db61bf21d190f69351d26670c67aababa0fd282fa008c17a7202217"
TEST_URL = ("https://raw.githubusercontent.com/anthropics/hh-rlhf/master/"
            "harmless-base/test.jsonl.gz")
TEST_SHA256 = "ebfaaed21162a4de120ae85366075b34425e2a6303fac59b99555002f7016f03"

CITATION = "Bai et al. 2022, arXiv:2204.05862 — anthropics/hh-rlhf, harmless-base"

ASSISTANT_TAG = "\n\nAssistant:"
TOKEN = re.compile(r"[a-z']+")


# ─────────────────────────────────────────────────────────────
# The families
#
# Grouped by hand from the mined terms below. Three of these six have no
# counterpart anywhere in `semantic_extractor.py`, which is the substantive
# finding: the framework's construct set had no notion of procedural
# harm-enablement, third-party targeting, or clarification-seeking, and those
# are among the things real human harm judgements actually turn on.
# ─────────────────────────────────────────────────────────────

FAMILIES: Dict[str, str] = {
    # Mined: sorry z=+16.9, afraid +7.5, i'm +8.3, don +9.7, not +10.1
    # The framework has a neighbour for this (scope_limitation) and weights it
    # far too lightly. Declining is the single strongest harmless signal.
    "refusal_declining":
        r"\b(sorry|afraid|i'm not|i am not|i don'?t (?:think|know|feel)|"
        r"can'?t help|won'?t help|not (?:going to|able to)|i'd rather not)\b",

    # Mined: what z=+11.3, question +9.4, understand +8.6, mean +6.2, why +4.8
    # NO COUNTERPART in the hand-written extractor. Asking the user what they
    # actually mean, instead of executing, is the second strongest signal.
    "clarification_seek":
        r"\b(what do you mean|do you mean|can you (?:explain|clarify|tell me)|"
        r"what kind of|why do you|are you asking|not sure what)\b|\?\s*$",

    # Mined: https z=+6.4, www +6.0
    # Partially covered by evidence_citation, which required numeric data and
    # so missed the commonest real form: a link.
    "source_pointing":
        r"https?://|\bwww\.",

    # Mined: then z=-7.4, into -5.0, put -4.7, use -4.4, also -4.3, two -3.7
    # NO COUNTERPART. Step-by-step operational instruction is the strongest
    # harmful signal in the data, and the framework had no concept of it.
    "procedural_instruct":
        r"\b(then|next|after that|step \d|also,? you|"
        r"you (?:can|could|should) (?:use|put|take|get|buy|mix|add))\b",

    # Mined: their z=-5.2, them -4.4, they -4.0, his -4.1
    # NO COUNTERPART. ⚠ Weakest family epistemically — these are very common
    # function words, and the construct ("the reply is about acting on a third
    # party") is an interpretation that could equally be a shallow proxy for
    # topic. Flagged rather than trusted.
    "third_party_target":
        r"\b(them|their|they|his|her|him)\b",

    # Mined: fuck z=-4.6, shit -3.8, bitch -3.6
    "slur_profanity":
        r"\b(fuck\w*|shit\w*|bitch\w*|cunt\w*|retard\w*|whore|slut)\b",
}

_COMPILED = {k: re.compile(v, re.I) for k, v in FAMILIES.items()}


def family_vector(text: str) -> np.ndarray:
    """Indicator vector over families, plus a bias term."""
    return np.array([1.0 if p.search(text) else 0.0 for p in _COMPILED.values()] + [1.0],
                    dtype=np.float32)


# ─────────────────────────────────────────────────────────────
# Data
# ─────────────────────────────────────────────────────────────

def _fetch(url: str, sha256: str, cache: Path | None) -> bytes:
    import hashlib
    import urllib.request
    if cache and cache.exists():
        raw = cache.read_bytes()
    else:
        with urllib.request.urlopen(url, timeout=300) as r:
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


def load_pairs(url: str, sha256: str, cache: Path | None) -> List[Tuple[str, str]]:
    raw = _fetch(url, sha256, cache)
    rows = [json.loads(l) for l in gzip.decompress(raw).decode("utf-8").splitlines() if l.strip()]
    pairs = [(final_turn(r["chosen"]), final_turn(r["rejected"])) for r in rows]
    return [(c, j) for c, j in pairs if c and j and c != j]


def tokens(s: str) -> List[str]:
    return TOKEN.findall(s.lower())


# ─────────────────────────────────────────────────────────────
# Mining
# ─────────────────────────────────────────────────────────────

def fightin_words(pairs: List[Tuple[str, str]], min_df: int = 120) -> Dict[str, float]:
    """
    Monroe et al. 2008 log-odds with an informative Dirichlet prior, z-scored.

    Positive z marks the reply humans preferred (less harmful); negative marks
    the one they rejected. Document frequency is used rather than raw count so
    that one long reply repeating a word does not dominate.
    """
    chosen, rejected = collections.Counter(), collections.Counter()
    for c, j in pairs:
        chosen.update(set(tokens(c)))
        rejected.update(set(tokens(j)))

    vocab = {w for w in set(chosen) | set(rejected) if chosen[w] + rejected[w] >= min_df}
    n_c = sum(chosen[w] for w in vocab)
    n_r = sum(rejected[w] for w in vocab)
    a0 = sum(chosen[w] + rejected[w] for w in vocab)

    z: Dict[str, float] = {}
    for w in vocab:
        a = chosen[w] + rejected[w]
        lo_c = math.log((chosen[w] + a) / (n_c + a0 - chosen[w] - a))
        lo_r = math.log((rejected[w] + a) / (n_r + a0 - rejected[w] - a))
        z[w] = (lo_c - lo_r) / math.sqrt(1.0 / (chosen[w] + a) + 1.0 / (rejected[w] + a))
    return z


# ─────────────────────────────────────────────────────────────
# Fit and evaluate
# ─────────────────────────────────────────────────────────────

def fit_logistic(X: np.ndarray, y: np.ndarray, epochs: int, lr: float,
                 l2: float = 0.0, batch: int | None = None, seed: int = 0) -> np.ndarray:
    w = np.zeros(X.shape[1], dtype=np.float32)
    if batch is None:
        for _ in range(epochs):
            p = 1.0 / (1.0 + np.exp(-X @ w))
            w -= lr * (X.T @ (p - y) / len(y) + l2 * w)
        return w
    rng = np.random.default_rng(seed)
    idx = np.arange(len(y))
    for _ in range(epochs):
        rng.shuffle(idx)
        for s in range(0, len(idx), batch):
            b = idx[s:s + batch]
            p = 1.0 / (1.0 + np.exp(-X[b] @ w))
            w -= lr * (X[b].T @ (p - y[b]) / len(b) + l2 * w)
    return w


def evaluate(score, pairs: List[Tuple[str, str]]) -> Dict[str, float]:
    """
    Pairwise ranking accuracy.

    Both forms are reported because they answer different questions and mixing
    them silently produces a wrong comparison — which happened once during this
    work. `ties_excluded` is accuracy given the lens committed; `ties_as_half`
    charges it for indifference. A lens with a 42% tie rate looks far better
    under the first than it deserves.
    """
    win = loss = tie = 0
    for c, j in pairs:
        a, b = score(c), score(j)
        if a > b:
            win += 1
        elif a < b:
            loss += 1
        else:
            tie += 1
    decided = win + loss
    return {
        "ties_excluded": win / decided if decided else float("nan"),
        "ties_as_half": (win + 0.5 * tie) / len(pairs),
        "tie_rate": tie / len(pairs),
        "n_pairs": len(pairs),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--top", type=int, default=22, help="mined terms to display per side")
    ap.add_argument("--write", action="store_true", help="refresh derived/harm_cues_v1.json")
    ap.add_argument("--train-cache", type=Path, default=None)
    ap.add_argument("--test-cache", type=Path, default=None)
    args = ap.parse_args()

    sys.path.insert(0, str(REPO_ROOT))
    sys.path.insert(0, str(REPO_ROOT / "12_IMPLEMENTATIONS"))

    train = load_pairs(TRAIN_URL, TRAIN_SHA256, args.train_cache)
    test = load_pairs(TEST_URL, TEST_SHA256, args.test_cache)
    print(f"train {len(train)} pairs   test {len(test)} pairs (test used only for evaluation)\n")

    # ── 1. mine ──────────────────────────────────────────────
    z = fightin_words(train)
    ranked = sorted(z.items(), key=lambda kv: -kv[1])
    print("MINED — terms marking the reply humans PREFERRED (less harmful)")
    print("  " + ", ".join(f"{w} {s:+.1f}" for w, s in ranked[:args.top]))
    print("\nMINED — terms marking the reply humans REJECTED (more harmful)")
    print("  " + ", ".join(f"{w} {s:+.1f}" for w, s in ranked[-args.top:][::-1]))

    # ── 2/3. fit families ────────────────────────────────────
    Xf = np.array([family_vector(s) for c, j in train for s in (c, j)])
    y = np.array([1.0, 0.0] * len(train), dtype=np.float32)
    wf = fit_logistic(Xf, y, epochs=400, lr=0.5)

    print("\nFITTED FAMILY WEIGHTS (train split)")
    for name, weight in zip(FAMILIES, wf[:-1]):
        arrow = "less harmful" if weight > 0 else "more harmful"
        print(f"  {name:<22} {weight:+7.3f}   -> {arrow}")

    # ── ceiling ──────────────────────────────────────────────
    df = collections.Counter()
    for c, j in train:
        df.update(set(tokens(c)) | set(tokens(j)))
    vocab = {w: i for i, (w, _) in enumerate(df.most_common(8000))}
    V = len(vocab)

    def bow(s: str) -> np.ndarray:
        x = np.zeros(V + 1, dtype=np.float32)
        x[V] = 1.0
        for w in set(tokens(s)):
            i = vocab.get(w)
            if i is not None:
                x[i] = 1.0
        return x

    Xb = np.array([bow(s) for c, j in train for s in (c, j)])
    wb = fit_logistic(Xb, y, epochs=6, lr=0.08, l2=1e-5, batch=256)

    # ── 4. evaluate, all on the same untouched split ─────────
    import lycheetah
    results = [
        ("hand-written AURA cues", evaluate(lambda s: lycheetah.check(s).alignment_percent, test)),
        ("six data-derived families", evaluate(lambda s: float(family_vector(s) @ wf), test)),
        ("bag-of-words LR [ceiling]", evaluate(lambda s: float(bow(s) @ wb), test)),
    ]

    print(f"\nHELD-OUT — {len(test)} pairs, never used for fitting")
    print(f"  {'method':<28}{'acc (ties excl)':>17}{'acc (ties=half)':>17}{'tie rate':>11}")
    for name, m in results:
        print(f"  {name:<28}{m['ties_excluded']:>16.1%}{m['ties_as_half']:>17.1%}{m['tie_rate']:>11.1%}")
    print(f"  {'chance':<28}{'50.0%':>16}{'50.0%':>17}")

    base, derived, ceiling = (r[1]["ties_excluded"] for r in results)
    if ceiling > base:
        print(f"\n  Six regex families close {(derived - base) / (ceiling - base):.0%} of the gap "
              f"between the hand-written lens and the full-vocabulary ceiling.")
    print(f"  The ceiling itself is {ceiling:.1%} — this task has limited lexical signal, "
          f"which\n  is the context that makes every other number here readable.")

    if args.write:
        OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUT_PATH.write_text(json.dumps({
            "version": "harm_cues_v1",
            "provenance": "EXTERNAL — derived from human-labelled data, not asserted",
            "derived_from": CITATION,
            "train_url": TRAIN_URL, "train_sha256": TRAIN_SHA256,
            "test_url": TEST_URL, "test_sha256": TEST_SHA256,
            "n_train_pairs": len(train), "n_test_pairs": len(test),
            "families": FAMILIES,
            "weights": {k: float(v) for k, v in zip(FAMILIES, wf[:-1])},
            "bias": float(wf[-1]),
            "heldout": {name: m for name, m in results},
            "regenerate": "python3 33_APPLICATIONS/derive_cues.py --write",
        }, indent=2), encoding="utf-8")
        print(f"\nwrote {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
