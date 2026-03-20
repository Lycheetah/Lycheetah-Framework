"""
MICROORCIM Tracker — Daily Sovereignty Measurement
===================================================

Implements real-time drift tracking and sovereignty scoring.

MICROORCIM: Micro-level Organizational Coherence Recalibration & Identity Monitoring
Core equation: Sovereignty_score = (1 − ρ_drift) · ρ_stability ∈ [0,1]

Where:
    ρ_drift = |intended − actual| / Δt
    ρ_stability = measure of phase-lock duration and consistency

Example: If I plan 4 hours and spend 3h, ρ_drift = |4−3|/24h = 0.042 per hour.
Measured against daily budget: sovereignty_score = (1 − 0.042) · [stability metric]

Status: ACTIVE equation
Implementation: Daily CLI tracker with history persistence
Author: Mackenzie Clark (Lycheetah Foundation)
Date: March 2026
"""

import json
import datetime
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import statistics

# Ensure UTF-8 output on Windows
if sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout.reconfigure(encoding='utf-8')


class MicroorcimTracker:
    """Track and measure daily sovereignty through drift and stability."""

    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize tracker with persistent storage.

        Args:
            data_dir: Directory for daily logs. Defaults to ~/.microorcim/
        """
        if data_dir is None:
            data_dir = Path.home() / ".microorcim"

        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = self.data_dir / "history.json"
        self.today_file = self.data_dir / f"day_{datetime.date.today().isoformat()}.json"

        self.history = self._load_history()
        self.today_data = self._load_today()

    def _load_history(self) -> List[Dict]:
        """Load historical records from file."""
        if self.history_file.exists():
            with open(self.history_file) as f:
                return json.load(f)
        return []

    def _save_history(self):
        """Persist history to file."""
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)

    def _load_today(self) -> Dict:
        """Load today's tracking data."""
        if self.today_file.exists():
            with open(self.today_file) as f:
                return json.load(f)
        return {
            "date": str(datetime.date.today()),
            "intentions": [],  # [{"name": str, "intended_hours": float, "context": str}]
            "actuals": [],     # [{"name": str, "actual_hours": float, "timestamp": str}]
            "stability_events": [],  # Track phase-lock hold duration
        }

    def _save_today(self):
        """Persist today's data."""
        with open(self.today_file, 'w') as f:
            json.dump(self.today_data, f, indent=2)

    def add_intention(self, name: str, intended_hours: float, context: str = "") -> None:
        """
        Record an intention at the start of a task.

        Args:
            name: Task name
            intended_hours: Expected duration
            context: Optional context string
        """
        self.today_data["intentions"].append({
            "name": name,
            "intended_hours": intended_hours,
            "context": context,
            "timestamp": datetime.datetime.now().isoformat(),
        })
        self._save_today()

    def add_actual(self, name: str, actual_hours: float) -> None:
        """
        Record actual time spent after task completion.

        Args:
            name: Task name (should match an intention)
            actual_hours: Actual duration
        """
        self.today_data["actuals"].append({
            "name": name,
            "actual_hours": actual_hours,
            "timestamp": datetime.datetime.now().isoformat(),
        })
        self._save_today()

    def record_stability_event(self, event_type: str, duration_minutes: int) -> None:
        """
        Record a stability event (phase-lock hold).

        Args:
            event_type: Type of stability (e.g., "deep_work", "meditation", "coherent_decision")
            duration_minutes: How long the coherent state was held
        """
        self.today_data["stability_events"].append({
            "event_type": event_type,
            "duration_minutes": duration_minutes,
            "timestamp": datetime.datetime.now().isoformat(),
        })
        self._save_today()

    def calculate_drift(self) -> Tuple[float, List[Dict]]:
        """
        Calculate ρ_drift = |intended − actual| / Δt

        Returns:
            (mean_drift, details_list) where details_list has per-task breakdown
        """
        drifts = []

        # Match intentions to actuals by name
        intention_map = {item["name"]: item for item in self.today_data["intentions"]}

        for actual in self.today_data["actuals"]:
            name = actual["name"]
            if name in intention_map:
                intended = intention_map[name]["intended_hours"]
                actual_h = actual["actual_hours"]

                # ρ_drift = |intended − actual| / day_length (24 hours)
                drift = abs(intended - actual_h) / 24.0

                drifts.append({
                    "name": name,
                    "intended_hours": intended,
                    "actual_hours": actual_h,
                    "drift": drift,
                })

        if not drifts:
            return 0.0, []

        mean_drift = statistics.mean(d["drift"] for d in drifts)
        return mean_drift, drifts

    def calculate_stability(self) -> Tuple[float, List[Dict]]:
        """
        Calculate ρ_stability from coherent hold events.

        Stability metric: ratio of time in coherent states to total tracking time.
        ρ_stability = Σ(coherent_duration) / total_day_minutes

        Returns:
            (stability_score, event_details) where event_details has per-event breakdown
        """
        events = self.today_data["stability_events"]

        if not events:
            return 0.0, []

        total_coherent_minutes = sum(e["duration_minutes"] for e in events)
        total_day_minutes = 24 * 60  # 1440

        stability = min(total_coherent_minutes / total_day_minutes, 1.0)

        event_details = [
            {
                "event_type": e["event_type"],
                "duration_minutes": e["duration_minutes"],
                "contribution": e["duration_minutes"] / total_day_minutes,
            }
            for e in events
        ]

        return stability, event_details

    def calculate_sovereignty_score(self) -> Dict:
        """
        Calculate full sovereignty score: (1 − ρ_drift) · ρ_stability ∈ [0,1]

        Returns:
            Dictionary with all components and final score
        """
        drift, drift_details = self.calculate_drift()
        stability, stability_details = self.calculate_stability()

        # Sovereignty = (1 − drift) · stability
        sovereignty = (1.0 - drift) * stability

        return {
            "date": str(datetime.date.today()),
            "sovereignty_score": max(0.0, min(1.0, sovereignty)),
            "drift": drift,
            "drift_details": drift_details,
            "stability": stability,
            "stability_details": stability_details,
            "interpretation": self._interpret_score(sovereignty),
        }

    def _interpret_score(self, score: float) -> str:
        """Provide human-readable interpretation of sovereignty score."""
        if score >= 0.8:
            return "STRONG — High coherence, low drift, stable phase-lock"
        elif score >= 0.6:
            return "MODERATE — Coherent but some drift noted; stability improving"
        elif score >= 0.4:
            return "TRANSITIONAL — Significant drift; building stability"
        elif score >= 0.2:
            return "RECOVERING — High drift; minimal stability; reset needed"
        else:
            return "CRITICAL — Sovereignty at boundary; return to anchor"

    def close_day(self) -> Dict:
        """
        Finalize today's record and add to history.

        Returns:
            Full day report including sovereignty score
        """
        report = self.calculate_sovereignty_score()
        self.history.append(report)
        self._save_history()

        # Archive today's file
        return report

    def daily_cli_report(self) -> str:
        """Generate human-readable daily report."""
        report = self.calculate_sovereignty_score()
        score = report["sovereignty_score"]

        lines = [
            "",
            "╔════════════════════════════════════════════════════════════╗",
            "║          MICROORCIM DAILY SOVEREIGNTY REPORT               ║",
            f"║  {report['date']:<54}║",
            "╚════════════════════════════════════════════════════════════╝",
            "",
            f"Sovereignty Score:  {score:.3f}  [{self._score_bar(score)}]",
            f"Status:             {report['interpretation']}",
            "",
            "─ Drift Analysis ─────────────────────────────────────────────",
            f"ρ_drift = |intended − actual| / 24h = {report['drift']:.4f}",
        ]

        if report['drift_details']:
            for detail in report['drift_details']:
                lines.append(
                    f"  {detail['name']:<30} "
                    f"planned {detail['intended_hours']:.1f}h, "
                    f"actual {detail['actual_hours']:.1f}h "
                    f"(drift: {detail['drift']:.4f})"
                )

        lines.extend([
            "",
            "─ Stability Analysis ────────────────────────────────────────",
            f"ρ_stability = coherent_time / total_day = {report['stability']:.4f}",
        ])

        if report['stability_details']:
            for detail in report['stability_details']:
                lines.append(
                    f"  {detail['event_type']:<30} "
                    f"{detail['duration_minutes']:>3d}min "
                    f"({detail['contribution']*100:.1f}%)"
                )

        lines.extend([
            "",
            "─ Calculation ────────────────────────────────────────────────",
            f"Sovereignty = (1 − {report['drift']:.4f}) × {report['stability']:.4f}",
            f"            = {1.0 - report['drift']:.4f} × {report['stability']:.4f}",
            f"            = {score:.4f}",
            "",
        ])

        return "\n".join(lines)

    @staticmethod
    def _score_bar(score: float, width: int = 30) -> str:
        """ASCII bar representation of score."""
        filled = int(width * score)
        return "█" * filled + "░" * (width - filled)


if __name__ == "__main__":
    # Simple CLI example
    import sys

    tracker = MicroorcimTracker()

    if len(sys.argv) > 1:
        cmd = sys.argv[1]

        if cmd == "intention":
            name, hours = sys.argv[2], float(sys.argv[3])
            context = " ".join(sys.argv[4:]) if len(sys.argv) > 4 else ""
            tracker.add_intention(name, hours, context)
            print(f"✓ Recorded intention: {name} ({hours}h)")

        elif cmd == "actual":
            name, hours = sys.argv[2], float(sys.argv[3])
            tracker.add_actual(name, hours)
            print(f"✓ Recorded actual: {name} ({hours}h)")

        elif cmd == "stability":
            event_type, duration = sys.argv[2], int(sys.argv[3])
            tracker.record_stability_event(event_type, duration)
            print(f"✓ Recorded stability: {event_type} ({duration}min)")

        elif cmd == "report":
            print(tracker.daily_cli_report())

        elif cmd == "close":
            report = tracker.close_day()
            print(tracker.daily_cli_report())
            print(f"✓ Day finalized. Final score: {report['sovereignty_score']:.3f}")

        else:
            print(f"Unknown command: {cmd}")
    else:
        print(tracker.daily_cli_report())
