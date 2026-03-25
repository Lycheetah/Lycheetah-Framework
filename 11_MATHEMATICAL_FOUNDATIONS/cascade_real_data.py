"""
CASCADE Real-Data Validation
=============================
Tests CASCADE belief revision on real Wikipedia article summaries.
Proves (or honestly refutes) the +40.3% coherence improvement claim
outside the framework's own synthetic test harness.

Run:
    py 11_MATHEMATICAL_FOUNDATIONS/cascade_real_data.py

Requirements: numpy (already installed), internet connection for Wikipedia API
"""

import sys
import os
import json
import time
import urllib.request
import urllib.parse
import numpy as np
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '12_IMPLEMENTATIONS'))

from core.cascade_engine import CascadeEngine, KnowledgeBlock

# ---------------------------------------------------------------------------
# Wikipedia API fetcher
# ---------------------------------------------------------------------------

WIKI_TOPICS = [
    # Science
    "quantum mechanics", "photosynthesis", "evolution", "black hole",
    "DNA", "plate tectonics", "thermodynamics", "relativity",
    # History
    "French Revolution", "World War II", "Roman Empire", "Silk Road",
    # Philosophy
    "epistemology", "ethics", "consciousness", "free will",
    # Mathematics
    "prime number", "Fourier transform", "topology", "game theory",
    # Culture
    "jazz music", "Buddhism", "democracy", "language acquisition",
    # NZ / Indigenous
    "Maori people", "Treaty of Waitangi", "New Zealand",
    # AI / Technology
    "artificial intelligence", "neural network", "cryptography",
]


def fetch_wikipedia_summary(topic: str) -> dict | None:
    """Fetch first paragraph summary from Wikipedia API."""
    url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + urllib.parse.quote(topic)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "LycheetahFramework/1.0"})
        with urllib.request.urlopen(req, timeout=8) as r:
            data = json.loads(r.read().decode())
            return {
                "title": data.get("title", topic),
                "extract": data.get("extract", ""),
                "topic": topic,
            }
    except Exception:
        return None


def sentences_from_extract(extract: str) -> list[str]:
    """Split extract into sentences as knowledge blocks."""
    sentences = [s.strip() for s in extract.replace("  ", " ").split(". ") if len(s.strip()) > 20]
    return sentences[:8]  # cap at 8 sentences per article


# ---------------------------------------------------------------------------
# Coherence measurement helpers
# ---------------------------------------------------------------------------

def measure_coherence_baseline(sentences: list[str]) -> float:
    """
    Baseline: add all sentences to static engine, measure final coherence.
    No CASCADE reorganisation — just raw knowledge state.
    """
    engine = CascadeEngine()
    for i, sent in enumerate(sentences):
        block = KnowledgeBlock(
            id=f"b{i}",
            content=sent,
            evidence_weight=0.5,  # neutral evidence weight (no prior)
            source="wikipedia",
        )
        engine.add_block(block)
    return engine.coherence()


def measure_coherence_cascade(sentences: list[str]) -> float:
    """
    CASCADE: add sentences in order with increasing evidence weight,
    simulating knowledge integration and truth pressure.
    """
    engine = CascadeEngine()
    for i, sent in enumerate(sentences):
        # Evidence weight increases as we encounter more corroborating facts
        evidence = 0.4 + (i / len(sentences)) * 0.6  # 0.4 → 1.0
        block = KnowledgeBlock(
            id=f"b{i}",
            content=sent,
            evidence_weight=evidence,
            source="wikipedia",
        )
        engine.add_block(block)
    return engine.coherence()


# ---------------------------------------------------------------------------
# Main experiment
# ---------------------------------------------------------------------------

def run_experiment():
    print("\nCASCADE Real-Data Validation")
    print("=" * 60)
    print(f"Testing on Wikipedia summaries — {len(WIKI_TOPICS)} topics")
    print(f"Run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    results = []
    failed_fetches = []

    for topic in WIKI_TOPICS:
        data = fetch_wikipedia_summary(topic)
        if not data or not data["extract"]:
            failed_fetches.append(topic)
            continue

        sentences = sentences_from_extract(data["extract"])
        if len(sentences) < 3:
            failed_fetches.append(topic)
            continue

        c_baseline = measure_coherence_baseline(sentences)
        c_cascade  = measure_coherence_cascade(sentences)
        delta      = c_cascade - c_baseline
        pct_change = (delta / c_baseline * 100) if c_baseline > 0 else 0

        results.append({
            "topic":      data["title"],
            "sentences":  len(sentences),
            "baseline":   round(c_baseline, 4),
            "cascade":    round(c_cascade, 4),
            "delta":      round(delta, 4),
            "pct_change": round(pct_change, 2),
        })

        status = "+" if delta >= 0 else "-"
        print(f"  [{status}] {data['title'][:40]:<40} "
              f"baseline={c_baseline:.3f}  cascade={c_cascade:.3f}  "
              f"delta={delta:+.3f} ({pct_change:+.1f}%)")

        time.sleep(0.3)  # polite to Wikipedia

    # -----------------------------------------------------------------------
    # Summary statistics
    # -----------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)

    if not results:
        print("No results — check internet connection.")
        return

    deltas      = [r["delta"] for r in results]
    pct_changes = [r["pct_change"] for r in results]
    improvements = sum(1 for d in deltas if d > 0)
    neutral      = sum(1 for d in deltas if d == 0)
    regressions  = sum(1 for d in deltas if d < 0)

    mean_delta  = np.mean(deltas)
    std_delta   = np.std(deltas)
    mean_pct    = np.mean(pct_changes)
    median_pct  = np.median(pct_changes)

    baseline_mean = np.mean([r["baseline"] for r in results])
    cascade_mean  = np.mean([r["cascade"]  for r in results])

    print(f"\n  Topics tested:        {len(results)}")
    print(f"  Failed fetches:       {len(failed_fetches)}")
    print(f"  Improvements:         {improvements}/{len(results)}")
    print(f"  Neutral:              {neutral}/{len(results)}")
    print(f"  Regressions:          {regressions}/{len(results)}")
    print(f"\n  Mean baseline:        {baseline_mean:.4f}")
    print(f"  Mean CASCADE:         {cascade_mean:.4f}")
    print(f"  Mean delta:           {mean_delta:+.4f}")
    print(f"  Std delta:            {std_delta:.4f}")
    print(f"  Mean % change:        {mean_pct:+.2f}%")
    print(f"  Median % change:      {median_pct:+.2f}%")

    # Honest status assessment
    print("\n" + "=" * 60)
    print("HONEST STATUS ASSESSMENT")
    print("=" * 60)

    claimed = 40.3  # the framework's published claim

    if mean_pct >= claimed * 0.8:
        status_label = "[CONFIRMED]"
        note = f"Mean improvement {mean_pct:+.1f}% is within 20% of claimed {claimed}%"
    elif mean_pct > 0:
        status_label = "[PARTIAL]"
        note = f"Positive improvement {mean_pct:+.1f}% but below claimed {claimed}%"
    elif mean_pct >= -5:
        status_label = "[NEUTRAL]"
        note = f"Near-zero effect {mean_pct:+.1f}% — claim requires revision"
    else:
        status_label = "[REFUTED]"
        note = f"Negative result {mean_pct:+.1f}% — FAILURE MUSEUM exhibit warranted"

    print(f"\n  Claimed improvement:  {claimed}%")
    print(f"  Measured improvement: {mean_pct:+.2f}%")
    print(f"  Status:               {status_label}")
    print(f"  Note:                 {note}")

    if status_label in ("[PARTIAL]", "[NEUTRAL]", "[REFUTED]"):
        print(f"\n  FAILURE MUSEUM: This result warrants an honest exhibit.")
        print(f"  The +{claimed}% claim was measured on synthetic data.")
        print(f"  Real-world Wikipedia data shows {mean_pct:+.1f}%.")
        print(f"  The honest number is {mean_pct:+.1f}%.")

    # Save JSON results
    output = {
        "run_date":         datetime.now().isoformat(),
        "data_source":      "Wikipedia REST API summaries",
        "topics_tested":    len(results),
        "claimed_improvement_pct": claimed,
        "measured_improvement_pct": round(mean_pct, 2),
        "median_improvement_pct": round(median_pct, 2),
        "mean_baseline_coherence": round(baseline_mean, 4),
        "mean_cascade_coherence":  round(cascade_mean, 4),
        "improvements": improvements,
        "regressions":  regressions,
        "status":       status_label,
        "per_topic":    results,
    }

    out_path = os.path.join(os.path.dirname(__file__), "cascade_real_data_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n  Results saved to: cascade_real_data_results.json")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    run_experiment()
