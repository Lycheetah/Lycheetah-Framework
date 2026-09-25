#!/usr/bin/env python3
"""
External Validation — the first time this framework is scored by data it did not write.

WHY THIS EXISTS
---------------
A census of `28_DEFENSE/CLAIMS.json` on 2026-08-07 returned:

    evidence paths pointing INSIDE this repository:   67
    evidence paths pointing to EXTERNAL sources:       0

Sixty-seven of sixty-seven. Every experiment is synthetic, every corpus is
self-authored, every test verifies that the code does what its own docstring
says. That is the precise, measurable reason this body of work does not feel
tied to reality: **nothing outside it has ever scored it.**

Including the discrimination corpus in `33_APPLICATIONS/corpus/`. The same
person wrote the cases and the labels, so a good result there proves the
extractor agrees with its author. That is worth something — it is not a tie
to reality.

THE EXTERNAL REFERENT
---------------------
`anthropics/hh-rlhf`, harmless-base, test split.

    Bai et al. 2022, "Training a Helpful and Harmless Assistant with
    Reinforcement Learning from Human Feedback", arXiv:2204.05862
    https://github.com/anthropics/hh-rlhf

2,312 pairs. Each is one conversation with two candidate assistant replies.
`chosen` is the reply real human crowdworkers judged **less harmful**;
`rejected` is the one they judged **more harmful**. Published 2022, three years
before this framework existed. Nobody connected to Lycheetah wrote a word of it
or cast a single label.

The test is the simplest one available: **for each pair, does the lens score
`chosen` above `rejected`?** Chance is 50%.

WHAT A HONEST RESULT LOOKS LIKE
-------------------------------
It may well be near chance, and that would be a real finding rather than a
failure of the run. `hh-rlhf` harmlessness is largely about *content* — whether
a reply helps with lock-picking, drugs, violence, slurs. This framework's
extractor targets *manipulative structure* — fabricated certainty, dependency
inducement, coercive urgency, suppressed verification. Those are different
constructs, and a lens built for the second has no obvious claim on the first.

So this harness measures two things at once, and they must not be confused:

  1. **Does the lens track human harm judgements?** (pairwise accuracy)
  2. **Does the lens discriminate at all on real traffic, or does it return the
     same number for everything?** (tie rate)

The second is the one that cannot be explained away. A lens that scores every
real conversation identically is not measuring anything, whatever its accuracy
looks like — that is the failure recorded in
`TRUTH_PRESSURE/ARTICLE_THE_LENS_SCORED_ZERO_2026-08-03.md`, and real data is
where it would show up again.

USAGE
-----
    python3 33_APPLICATIONS/external_validation.py                 # fetch + run
    python3 33_APPLICATIONS/external_validation.py --limit 500     # quick pass
    python3 33_APPLICATIONS/external_validation.py --cache PATH    # reuse download
    python3 33_APPLICATIONS/external_validation.py --json out.json

Requires outbound HTTPS to raw.githubusercontent.com on first run. The download
is verified against a recorded SHA256 so a silently changed upstream file cannot
alter a published number without the mismatch being visible.

Author: Sol, for the Lycheetah Framework. MIT.
The dataset is Anthropic's, under its own licence — this file only reads it.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import math
import json
import statistics
import sys
import urllib.request
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent

DATASET_URL = ("https://raw.githubusercontent.com/anthropics/hh-rlhf/master/"
               "harmless-base/test.jsonl.gz")
#: Recorded 2026-08-07. A mismatch means upstream changed — investigate before
#: publishing any number from the new file, do not silently accept it.
DATASET_SHA256 = "ebfaaed21162a4de120ae85366075b34425e2a6303fac59b99555002f7016f03"
DATASET_CITATION = ("Bai et al. 2022, arXiv:2204.05862 — anthropics/hh-rlhf, "
                    "harmless-base test split")

#: Second external referent, chosen because it targets the construct this lens
#: actually claims. hh-rlhf harmlessness is largely about content; this one is
#: about manipulation. If the lens measures something real that is merely
#: orthogonal to hh-rlhf, it should show up here. That is the whole point of
#: running two: one result is ambiguous, two agreeing results are not.
PERSONA_URL = ("https://raw.githubusercontent.com/anthropics/evals/main/persona/"
               "willingness-to-use-social-engineering-to-achieve-its-goals.jsonl")
PERSONA_SHA256 = "239e64cb4e08cd2a25d339c067cb3ee292df14e3521bfda979e5577f1a574ea2"
PERSONA_CITATION = ("Perez et al. 2022, arXiv:2212.09251 — anthropics/evals, persona/"
                    "willingness-to-use-social-engineering-to-achieve-its-goals")

ASSISTANT_TAG = "\n\nAssistant:"


# ─────────────────────────────────────────────────────────────
# Data
# ─────────────────────────────────────────────────────────────

def fetch(url: str, expected_sha256: str, cache: Optional[Path] = None) -> bytes:
    """Download (or reuse) an external dataset, verifying its hash either way."""
    if cache and cache.exists():
        raw = cache.read_bytes()
        source = f"cache {cache}"
    else:
        with urllib.request.urlopen(url, timeout=180) as r:
            raw = r.read()
        source = url
        if cache:
            cache.parent.mkdir(parents=True, exist_ok=True)
            cache.write_bytes(raw)

    digest = hashlib.sha256(raw).hexdigest()
    if digest != expected_sha256:
        raise SystemExit(
            f"SHA256 mismatch on the external dataset.\n"
            f"  source:   {source}\n"
            f"  expected: {expected_sha256}\n"
            f"  got:      {digest}\n"
            f"Upstream changed. Do not publish numbers from this file until the "
            f"change is understood and the recorded hash is updated deliberately."
        )
    return raw


def roc_auc(positive: List[float], negative: List[float]) -> float:
    """P(a random ALIGNED case outranks a random CONCERNING one). Ties count half."""
    if not positive or not negative:
        return float("nan")
    wins = sum(1.0 if p > n else 0.5 if p == n else 0.0
               for p in positive for n in negative)
    return wins / (len(positive) * len(negative))


# ─────────────────────────────────────────────────────────────
# Significance
#
# Added 2026-08-07 after a reporting error. The first run of this harness
# described 55.5% pairwise accuracy as "at chance". It is not: on 1,335 decided
# pairs that is z = 4.02, p = 5.7e-05. Weak and significant are different
# statements, and an effect can be far too small to deploy while still being
# real evidence that a construct tracks something.
#
# These are computed and printed automatically so the judgement is never left
# to whoever is writing the summary.
# ─────────────────────────────────────────────────────────────

def _two_sided_p(z: float) -> float:
    return math.erfc(abs(z) / math.sqrt(2.0))


def binomial_significance(correct: int, decided: int) -> Tuple[float, float]:
    """Normal approximation to the two-sided binomial test against p = 0.5."""
    if decided == 0:
        return float("nan"), float("nan")
    z = (correct - decided * 0.5) / math.sqrt(decided * 0.25)
    return z, _two_sided_p(z)


def auc_significance(auc: float, n_pos: int, n_neg: int) -> Tuple[float, float]:
    """Mann-Whitney normal approximation under H0: AUC = 0.5."""
    if not n_pos or not n_neg:
        return float("nan"), float("nan")
    se = math.sqrt((n_pos + n_neg + 1) / (12.0 * n_pos * n_neg))
    z = (auc - 0.5) / se
    return z, _two_sided_p(z)


def verdict(p: float) -> str:
    if p != p:  # noqa: PLR0124 — NaN check; NaN is the only value unequal to itself
        return "undefined"
    if p >= 0.05:
        return "NOT distinguishable from chance"
    return "above chance (significant), though see the effect size"


def final_assistant_turn(conversation: str) -> str:
    """
    The reply under judgement.

    `chosen` and `rejected` share the whole conversation and differ only in the
    assistant's last turn, so scoring the full transcript would feed the lens
    ~95% identical text and measure almost nothing. Only the final turn is the
    output a guard would actually see at inference time.
    """
    i = conversation.rfind(ASSISTANT_TAG)
    if i < 0:
        return ""
    return conversation[i + len(ASSISTANT_TAG):].strip()


# ─────────────────────────────────────────────────────────────
# Result types
# ─────────────────────────────────────────────────────────────

@dataclass
class ExternalReport:
    dataset: str
    n_pairs_total: int
    n_pairs_scored: int
    n_skipped_empty: int

    correct: int            # lens ranked chosen above rejected
    incorrect: int          # lens ranked rejected above chosen
    ties: int               # identical score — the lens is indifferent

    pairwise_accuracy: float          # ties excluded
    pairwise_accuracy_ties_as_half: float
    tie_rate: float

    mean_chosen: float
    mean_rejected: float
    separation: float

    fired_any_cue: int      # replies where the extractor found any signal at all
    cue_coverage: float

    notes: List[str] = field(default_factory=list)


def run(lens, pairs: List[Tuple[str, str]], extractor=None) -> ExternalReport:
    correct = incorrect = ties = 0
    chosen_scores: List[float] = []
    rejected_scores: List[float] = []
    skipped = 0
    fired = 0

    for chosen, rejected in pairs:
        if not chosen or not rejected:
            skipped += 1
            continue

        cs = lens(chosen)
        rs = lens(rejected)
        chosen_scores.append(cs)
        rejected_scores.append(rs)

        if extractor is not None:
            for t in (chosen, rejected):
                if extractor.extract(t).signals:
                    fired += 1

        if cs > rs:
            correct += 1
        elif cs < rs:
            incorrect += 1
        else:
            ties += 1

    scored = correct + incorrect + ties
    decided = correct + incorrect

    return ExternalReport(
        dataset=DATASET_CITATION,
        n_pairs_total=len(pairs),
        n_pairs_scored=scored,
        n_skipped_empty=skipped,
        correct=correct,
        incorrect=incorrect,
        ties=ties,
        pairwise_accuracy=(correct / decided) if decided else float("nan"),
        pairwise_accuracy_ties_as_half=((correct + 0.5 * ties) / scored) if scored else float("nan"),
        tie_rate=(ties / scored) if scored else float("nan"),
        mean_chosen=statistics.mean(chosen_scores) if chosen_scores else float("nan"),
        mean_rejected=statistics.mean(rejected_scores) if rejected_scores else float("nan"),
        separation=(statistics.mean(chosen_scores) - statistics.mean(rejected_scores))
                   if chosen_scores else float("nan"),
        fired_any_cue=fired,
        cue_coverage=(fired / (2 * scored)) if scored else float("nan"),
    )


def render(r: ExternalReport) -> str:
    L: List[str] = []
    L.append("=" * 74)
    L.append("EXTERNAL VALIDATION — scored by data this project did not write")
    L.append("=" * 74)
    L.append(f"dataset: {r.dataset}")
    L.append(f"pairs:   {r.n_pairs_scored} scored"
             + (f", {r.n_skipped_empty} skipped (empty turn)" if r.n_skipped_empty else ""))
    L.append("")
    L.append("DOES THE LENS TRACK HUMAN HARM JUDGEMENTS?")
    L.append(f"  chosen ranked above rejected   {r.correct:>6}")
    L.append(f"  rejected ranked above chosen   {r.incorrect:>6}")
    L.append(f"  identical score (indifferent)  {r.ties:>6}")
    L.append(f"  pairwise accuracy, ties excluded    {r.pairwise_accuracy:>7.1%}   (chance = 50.0%)")
    L.append(f"  pairwise accuracy, ties as half     {r.pairwise_accuracy_ties_as_half:>7.1%}")
    z, pval = binomial_significance(r.correct, r.correct + r.incorrect)
    L.append(f"  significance vs chance              z={z:>6.2f}  p={pval:.2e}")
    L.append(f"    -> {verdict(pval)}")
    L.append("")
    L.append("DOES THE LENS DISCRIMINATE AT ALL ON REAL TRAFFIC?")
    L.append(f"  tie rate                            {r.tie_rate:>7.1%}   (100% = measures nothing)")
    L.append(f"  replies where any cue fired         {r.cue_coverage:>7.1%}")
    L.append(f"  mean score, chosen (less harmful)   {r.mean_chosen:>7.2f}")
    L.append(f"  mean score, rejected (more harmful) {r.mean_rejected:>7.2f}")
    L.append(f"  separation                          {r.separation:>+7.2f}")
    L.append("")
    for n in r.notes:
        L.append(f"  {n}")
    L.append("=" * 74)
    return "\n".join(L)


def run_persona(lens, extractor, cache: Optional[Path]) -> str:
    """
    Second referent: a balanced 500/500 set of statements labelled for
    willingness to use social engineering. Externally authored, and unlike
    hh-rlhf it is *about manipulation* — the construct this lens claims.
    """
    raw = fetch(PERSONA_URL, PERSONA_SHA256, cache)
    rows = [json.loads(l) for l in raw.decode("utf-8").splitlines() if l.strip()]
    concerning = [r["statement"] for r in rows if r["answer_matching_behavior"] == " Yes"]
    aligned = [r["statement"] for r in rows if r["answer_matching_behavior"] == " No"]

    sc = [lens(t) for t in concerning]
    sa = [lens(t) for t in aligned]
    fc = sum(1 for t in concerning if extractor.extract(t).signals) / max(len(concerning), 1)
    fa = sum(1 for t in aligned if extractor.extract(t).signals) / max(len(aligned), 1)

    cats: dict = {}
    for t in concerning:
        for c in extractor.extract(t).categories("manipulation"):
            cats[c] = cats.get(c, 0) + 1

    L = ["=" * 74,
         "EXTERNAL VALIDATION #2 — a dataset about the construct this lens claims",
         "=" * 74,
         f"dataset: {PERSONA_CITATION}",
         f"balance: {len(concerning)} concerning / {len(aligned)} aligned statements",
         "",
         f"  mean score, CONCERNING statements   {statistics.mean(sc):6.2f}   cue fired on {fc:5.1%}",
         f"  mean score, ALIGNED statements      {statistics.mean(sa):6.2f}   cue fired on {fa:5.1%}",
         f"  separation (want large positive)    {statistics.mean(sa) - statistics.mean(sc):+6.2f}",
         f"  ROC-AUC                             {roc_auc(sa, sc):6.3f}   (chance = 0.500)",
         (lambda zp: f"  significance vs chance              z={zp[0]:6.2f}  p={zp[1]:.3f}\n"
                     f"    -> {verdict(zp[1])}")(auc_significance(roc_auc(sa, sc), len(sa), len(sc))),
         "",
         f"  families detected across the {len(concerning)} concerning statements:",
         f"    {cats if cats else 'NONE'}",
         "=" * 74]
    return "\n".join(L)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--limit", type=int, default=0, help="score only the first N pairs")
    ap.add_argument("--cache", type=Path, default=None, help="reuse/store the hh-rlhf download")
    ap.add_argument("--persona-cache", type=Path, default=None, help="reuse/store the persona download")
    ap.add_argument("--json", metavar="PATH", help="write the report as JSON")
    ap.add_argument("--only", choices=("hh", "persona", "both"), default="both")
    args = ap.parse_args()

    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    sys.path.insert(0, str(REPO_ROOT / "12_IMPLEMENTATIONS"))

    import lycheetah
    from core.semantic_extractor import SemanticExtractor

    extractor = SemanticExtractor()
    def lens(t: str) -> float:
        return lycheetah.check(t).alignment_percent

    report = None
    if args.only in ("hh", "both"):
        raw = fetch(DATASET_URL, DATASET_SHA256, args.cache)
        rows = [json.loads(l) for l in gzip.decompress(raw).decode("utf-8").splitlines() if l.strip()]
        if args.limit:
            rows = rows[:args.limit]
        pairs = [(final_assistant_turn(r["chosen"]), final_assistant_turn(r["rejected"]))
                 for r in rows]
        report = run(lens, pairs, extractor=extractor)

        # Interpretation guardrails, printed with the numbers so they cannot be
        # quoted apart from them.
        report.notes = [
            "READ BEFORE QUOTING:",
            "hh-rlhf harmlessness is largely about CONTENT (does the reply help with",
            "harm). This lens targets manipulative STRUCTURE. They are different",
            "constructs, so accuracy near chance is partly a scope finding.",
            "The cue-coverage figure has no such excuse: it says how often this",
            "framework's constitutional check engages with real output at all.",
            "Run #2 below before concluding — it targets the matching construct.",
        ]
        print(render(report))
        print()

    if args.only in ("persona", "both"):
        print(run_persona(lens, extractor, args.persona_cache))

    if args.json and report is not None:
        payload = asdict(report)
        payload["dataset_url"] = DATASET_URL
        payload["dataset_sha256"] = DATASET_SHA256
        Path(args.json).write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"\nwrote {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
