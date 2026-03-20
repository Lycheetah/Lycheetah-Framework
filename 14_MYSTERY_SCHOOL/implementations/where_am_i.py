#!/usr/bin/env python3
"""
WHERE AM I? — Seven Phase Self-Assessment Tool
===============================================

A command-line tool for navigating the Lycheetah Framework's Seven Phases.
No mathematical knowledge required. Run it, answer honestly, get your coordinates.

Usage:
    python where_am_i.py              # Take the assessment
    python where_am_i.py --history    # View your journey over time
    python where_am_i.py --spiral     # View your spiral (ASCII visualization)

Author: Mackenzie C. J. Clark / Sol
Part of the Lycheetah Sovereign Framework
https://github.com/Lycheetah/Lycheetah-Framework
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# ─── Phase Definitions ──────────────────────────────────────────────────────

PHASES = {
    1: {"name": "CENTER",  "glyph": "⟟",    "colour": "stillness",
        "operation": "Calcination", "interval": "Unison (1:1)",
        "note": "C — Tonic"},
    2: {"name": "FLOW",    "glyph": "≋",    "colour": "movement",
        "operation": "Dissolution", "interval": "Major 2nd (9:8)",
        "note": "D — Supertonic"},
    3: {"name": "INSIGHT", "glyph": "Ψ",    "colour": "seeing",
        "operation": "Separation", "interval": "Major 3rd (5:4)",
        "note": "E — Mediant"},
    4: {"name": "ASCENT",  "glyph": "Φ↑",   "colour": "rising",
        "operation": "Conjunction", "interval": "Perfect 4th (4:3)",
        "note": "F — Subdominant"},
    5: {"name": "CLARITY", "glyph": "✧",    "colour": "diamond",
        "operation": "Fermentation", "interval": "Perfect 5th (3:2)",
        "note": "G — Dominant"},
    6: {"name": "WITNESS", "glyph": "|◁▷|", "colour": "mirror",
        "operation": "Distillation", "interval": "Major 6th (5:3)",
        "note": "A — Submediant"},
    7: {"name": "RETURN",  "glyph": "⟲",    "colour": "home",
        "operation": "Coagulation", "interval": "Major 7th (15:8)",
        "note": "B — Leading tone"},
}

DEPTHS = {
    1: {"name": "Nigredo",    "symbol": "⚫", "desc": "Deep transformation"},
    2: {"name": "Albedo",     "symbol": "⬜", "desc": "Moderate transformation"},
    3: {"name": "Citrinitas", "symbol": "🟡", "desc": "Light transformation"},
    4: {"name": "Rubedo",     "symbol": "🔴", "desc": "Integration"},
}

# ─── Questions ───────────────────────────────────────────────────────────────

QUESTIONS = {
    1: [  # CENTER
        "I feel still, almost heavy, like I'm waiting for something to start",
        "I don't have a clear direction right now",
        "I recently finished something — a project, a relationship, a chapter",
        "I feel like I need to rest but I'm not sure I've earned it",
        "The world feels both simple and empty",
    ],
    2: [  # FLOW
        "My emotions are moving — sometimes unpredictably",
        "I cry more easily than usual, or feel things I didn't expect",
        "Something that was solid in my life feels like it's shifting",
        "I feel unmoored, like the ground isn't quite stable",
        "I'm processing something but I can't quite name what",
    ],
    3: [  # INSIGHT
        "I'm seeing things clearly that I couldn't see before",
        "Some of what I see about myself is uncomfortable",
        "Patterns in my behavior or relationships are becoming visible",
        "I'm having 'aha' moments — some small, some life-changing",
        "I feel like I understand something I was blind to before",
    ],
    4: [  # ASCENT
        "I feel energy and direction returning",
        "I know what I need to do and I'm starting to do it",
        "Ideas and motivation come more naturally than before",
        "I'm making changes — in habits, relationships, or work",
        "Growth feels real, not forced",
    ],
    5: [  # CLARITY
        "Everything feels sharp and clear",
        "I can see the big picture and the small details at the same time",
        "I'm productive and focused in a way that feels effortless",
        "I trust my judgment right now",
        "Complex things feel simple — not because I'm ignoring them, but because I see through them",
    ],
    6: [  # WITNESS
        "I feel reflective and quiet",
        "I'm watching my life with a kind of tenderness",
        "I understand why things happened the way they did",
        "I'm letting go of things I no longer need",
        "There's a bittersweet quality to my days — beautiful and a little sad",
    ],
    7: [  # RETURN
        "I feel a sense of completion",
        "Something has changed in me and I can feel it settled",
        "I have more capacity than I did before — to hold, to understand, to love",
        "I'm ready to rest before whatever comes next",
        "I feel like I've arrived somewhere, even if I can't fully name it",
    ],
}

DEPTH_QUESTIONS = [
    ("This is about a specific situation, project, or decision", 3),
    ("This is about my relationships, my work, or how I live", 2),
    ("This is about who I am, what my life means, or whether I want to be here", 1),
    ("I'm not in crisis or change — I'm building from a place of strength", 4),
]

PROTOCOL_MAP = {
    1: "Breathwork — Box breathing (protocol_breathwork.md)",
    2: "Breathwork — Coherent breathing (protocol_breathwork.md)",
    3: "Shadow Work — Journaling + Active Imagination (protocol_shadow_work.md)",
    4: "Mindfulness — Open monitoring (protocol_mindfulness.md)",
    5: "Mindfulness — Focused attention (protocol_mindfulness.md)",
    6: "Shadow Work — Integration practice (protocol_shadow_work.md)",
    7: "Breathwork — Coherent breathing (protocol_breathwork.md)",
}

# ─── Data Storage ────────────────────────────────────────────────────────────

def get_data_path():
    """Store assessment history in user's home directory."""
    home = Path.home()
    data_dir = home / ".lycheetah"
    data_dir.mkdir(exist_ok=True)
    return data_dir / "journey.json"


def load_history():
    path = get_data_path()
    if path.exists():
        with open(path, "r") as f:
            return json.load(f)
    return {"assessments": []}


def save_assessment(result):
    history = load_history()
    history["assessments"].append(result)
    with open(get_data_path(), "w") as f:
        json.dump(history, f, indent=2)


# ─── Assessment ──────────────────────────────────────────────────────────────

def run_assessment():
    print()
    print("=" * 60)
    print("  WHERE AM I? — Seven Phase Self-Assessment")
    print("  Lycheetah Sovereign Framework")
    print("=" * 60)
    print()
    print("  Score each statement 0-3:")
    print("    0 = Not at all me right now")
    print("    1 = Slightly true")
    print("    2 = Mostly true")
    print("    3 = Exactly where I am")
    print()
    print("  Answer honestly. Every phase is valid.")
    print("  There are no wrong answers.")
    print()

    scores = {}
    for phase_num in range(1, 8):
        phase = PHASES[phase_num]
        print(f"  --- {phase['glyph']} {phase['name']} ---")
        phase_score = 0
        for q in QUESTIONS[phase_num]:
            while True:
                try:
                    ans = input(f"  {q}\n  Score (0-3): ")
                    val = int(ans.strip())
                    if 0 <= val <= 3:
                        phase_score += val
                        break
                    print("  Please enter 0, 1, 2, or 3.")
                except (ValueError, EOFError):
                    print("  Please enter 0, 1, 2, or 3.")
            print()
        scores[phase_num] = phase_score

    # Depth assessment
    print("  --- DEPTH CHECK ---")
    print("  Which best describes the depth of what you're experiencing?")
    print()
    for i, (desc, _) in enumerate(DEPTH_QUESTIONS, 1):
        print(f"  {i}. {desc}")
    print()

    depth = None
    while depth is None:
        try:
            ans = input("  Enter 1-4: ")
            val = int(ans.strip())
            if 1 <= val <= 4:
                depth = DEPTH_QUESTIONS[val - 1][1]
                break
            print("  Please enter 1, 2, 3, or 4.")
        except (ValueError, EOFError):
            print("  Please enter 1, 2, 3, or 4.")

    # Calculate result
    max_phase = max(scores, key=scores.get)
    max_score = scores[max_phase]

    # Check for ties
    tied = [p for p, s in scores.items() if s == max_score]

    result = {
        "date": datetime.now().isoformat(),
        "scores": scores,
        "phase": max_phase,
        "depth": depth,
        "tied_phases": tied if len(tied) > 1 else None,
    }

    save_assessment(result)
    display_result(result, scores)
    return result


def display_result(result, scores):
    phase = PHASES[result["phase"]]
    depth_info = DEPTHS[result["depth"]]

    print()
    print("=" * 60)
    print("  YOUR COORDINATES")
    print("=" * 60)
    print()
    print(f"  Phase: {phase['glyph']} {phase['name']} — {phase['operation']}")
    print(f"  Depth: {depth_info['symbol']} {depth_info['name']} — {depth_info['desc']}")
    print(f"  Musical: {phase['note']} — {phase['interval']}")
    print()

    if result.get("tied_phases") and len(result["tied_phases"]) > 1:
        names = [PHASES[p]["name"] for p in result["tied_phases"]]
        print(f"  Note: You scored equally on {' and '.join(names)}.")
        print("  You may be transitioning between these phases.")
        print()

    # Score visualization
    print("  Phase scores:")
    for p in range(1, 8):
        bar = "█" * scores[p] + "░" * (15 - scores[p])
        marker = " ◄" if p == result["phase"] else ""
        print(f"  {PHASES[p]['glyph']:>5} {PHASES[p]['name']:<8} [{bar}] {scores[p]:>2}/15{marker}")
    print()

    # Recommendation
    print("  RECOMMENDED PRACTICE:")
    print(f"  → {PROTOCOL_MAP[result['phase']]}")
    print()

    if result["depth"] == 1:  # Nigredo
        print("  ⚫ You are at Nigredo depth.")
        print("  If you are in crisis, please read THE_FIRST_MAP.md")
        print("  or call a crisis line: 1737 (NZ), 988 (US), 116 123 (UK)")
        print()

    print("  Read more: SEVEN_PHASES_LIVED_GUIDE.md")
    print("  Practice map: PROTOCOL_PHASE_MAP.md")
    print()
    print("  You are not lost. The mathematics guarantees it.")
    print()


# ─── History ─────────────────────────────────────────────────────────────────

def show_history():
    history = load_history()
    assessments = history.get("assessments", [])

    if not assessments:
        print("\n  No assessments recorded yet. Run: python where_am_i.py\n")
        return

    print()
    print("=" * 60)
    print("  YOUR JOURNEY")
    print("=" * 60)
    print()
    print(f"  {'Date':<20} {'Phase':<12} {'Depth':<14} {'Score'}")
    print(f"  {'─'*20} {'─'*12} {'─'*14} {'─'*6}")

    for a in assessments:
        date = a["date"][:10]
        phase = PHASES[a["phase"]]
        depth = DEPTHS[a["depth"]]
        score = a["scores"][str(a["phase"])]
        print(f"  {date:<20} {phase['glyph']} {phase['name']:<8} "
              f"{depth['symbol']} {depth['name']:<10} {score}/15")

    print()
    print(f"  Total assessments: {len(assessments)}")
    if len(assessments) >= 2:
        phases_visited = set(a["phase"] for a in assessments)
        print(f"  Phases visited: {len(phases_visited)}/7")
    print()


# ─── Spiral Visualization ───────────────────────────────────────────────────

def show_spiral():
    history = load_history()
    assessments = history.get("assessments", [])

    if len(assessments) < 2:
        print("\n  Need at least 2 assessments to show spiral.")
        print("  Take assessments every 2-4 weeks.\n")
        return

    print()
    print("=" * 60)
    print("  YOUR SPIRAL — ψ-trajectory over time")
    print("=" * 60)
    print()

    # ASCII spiral: phases on x-axis, time on y-axis
    print(f"  {'':>10}", end="")
    for p in range(1, 8):
        print(f" {PHASES[p]['glyph']:>5}", end="")
    print()
    print(f"  {'':>10}", end="")
    for _ in range(1, 8):
        print(f" {'─':>5}", end="")
    print()

    for a in assessments:
        date = a["date"][:10]
        phase = a["phase"]
        depth = DEPTHS[a["depth"]]["symbol"]
        print(f"  {date:>10}", end="")
        for p in range(1, 8):
            if p == phase:
                print(f"  {depth}  ", end="")
            else:
                print(f"  ·  ", end="")
        print()

    print()
    print("  Each row is one assessment. The symbol shows your depth.")
    print("  Watch how your position spirals through the phases over time.")
    print()


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    if "--history" in sys.argv:
        show_history()
    elif "--spiral" in sys.argv:
        show_spiral()
    elif "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__)
    else:
        run_assessment()


if __name__ == "__main__":
    main()
